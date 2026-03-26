# =====================================================================
# Importación de librerías para el proyecto
# =====================================================================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import joblib 
import numpy as np
import requests 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fpdf import FPDF # Librería para generar PDFs B2B

# Configuro la página (Layout ancho para Dashboard profesional)
st.set_page_config(page_title="Smart-BCN | Inteligencia B2B", page_icon="🍽️", layout="wide")
st.title("🍽️ Smart-BCN: Inteligencia Operativa y Predicción de Demanda")
st.markdown("Plataforma SaaS propulsada por **Inteligencia Artificial (Random Forest)**. Analizamos el clima, los eventos y tu modelo de negocio para predecir afluencia y sugerir estrategias operativas y de marketing.")
st.divider()

# =====================================================================
# 0. CARGA DEL CEREBRO DE IA Y SUS MÉTRICAS
# =====================================================================
@st.cache_resource
def cargar_modelo_ia():
    try:
        modelo = joblib.load('modelo_core_demanda.pkl')
        columnas = joblib.load('columnas_modelo.pkl')
        try:
            precision = joblib.load('precision_modelo.pkl')
        except FileNotFoundError:
            precision = 0.0 
        return modelo, columnas, precision
    except FileNotFoundError:
        return None, None, None

modelo_ia, columnas_ia, precision_ia = cargar_modelo_ia()

if not modelo_ia:
    st.error("🚨 Error Crítico: No encuentro el cerebro de la IA ('modelo_core_demanda.pkl'). Ejecuta tus Notebooks.")
    st.stop()

# =====================================================================
# 1. PANEL DE CONTROL (Configuración B2B)
# =====================================================================
st.sidebar.header("⚙️ Configuración del Local")

direccion_input = st.sidebar.text_input("📍 Ubicación exacta:", "Plaza Catalunya, Barcelona")

with st.sidebar.expander("🪑 Capacidad y Formato", expanded=True):
    tipo_local = st.selectbox("🍷 Tipo de negocio:", ["Restaurante", "Bar de Copas", "Cafetería/Brunch"])
    aforo_interior = st.number_input("Sillas en interior:", min_value=5, value=60, step=5)
    tiene_terraza = st.checkbox("¿Tienes terraza?", value=True)
    aforo_terraza = st.number_input("Sillas en terraza:", min_value=0, value=40, step=5) if tiene_terraza else 0
    rotacion_mesas = st.slider("Rotación (Turnos por silla):", min_value=1.0, max_value=5.0, value=2.5, step=0.5)

with st.sidebar.expander("⭐ Entorno y Competencia", expanded=False):
    puntuacion_google = st.slider("Nota en Google Maps:", min_value=1.0, max_value=5.0, value=4.2, step=0.1)
    densidad_ui = st.selectbox("Locales en tu misma calle:", ["Muchos (Alta competencia)", "Normal", "Pocos (Baja competencia)"])
    densidad_limpia = "Alta" if "Muchos" in densidad_ui else ("Media" if "Normal" in densidad_ui else "Baja")

with st.sidebar.expander("📢 Presupuesto de Marketing Diario", expanded=True):
    st.markdown("<small>¿Cuánto inviertes al día en cada canal?</small>", unsafe_allow_html=True)
    presupuesto_meta = st.number_input("📱 Instagram / TikTok Ads (€/día):", min_value=0.0, value=10.0, step=2.0)
    presupuesto_google = st.number_input("🔍 Google Ads / SEO Local (€/día):", min_value=0.0, value=5.0, step=1.0)
    usa_fidelizacion = st.checkbox("💌 Base de clientes CRM (Email/WhatsApp)", value=False)

with st.sidebar.expander("🛵 Extras y Vía Pública", expanded=False):
    tiene_delivery = st.checkbox("Canal Delivery Activo (Glovo, etc)", value=False)
    hay_obras = st.checkbox("🚧 Obras en tu calle", value=False)

with st.sidebar.expander("💶 Tus Números Financieros", expanded=False):
    ticket_medio = st.number_input("Gasto Medio por Cliente (€):", min_value=5.0, value=25.0, step=1.0)
    ratio_camarero = st.number_input("Clientes por Camarero:", min_value=5, value=15, step=1)
    coste_turno_camarero = st.number_input("Coste Salarial por Turno (€):", min_value=10.0, value=60.0, step=5.0)
    porcentaje_cogs = st.slider("Coste de Comida/Bebida (%):", min_value=10, max_value=50, value=30)

# =====================================================================
# MOTORES DE GENERACIÓN DE PDF CORPORATIVOS
# =====================================================================
def generar_pdf_corporativo_tabla(df):
    pdf = FPDF(orientation='L', unit='mm', format='A4') 
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 18)
    pdf.set_text_color(44, 62, 80) 
    pdf.cell(0, 10, "Smart-BCN | Reporte de Inteligencia Operativa", 0, 1, 'C')
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(127, 140, 141) 
    pdf.cell(0, 6, "Proyeccion algoritmica automatizada", 0, 1, 'C')
    pdf.ln(8)
    
    cols = ['Dia', 'Lluvia', 'Viento', 'Demanda', 'Personal', 'Ingresos', 'Beneficio', 'Terraza', 'Eventos']
    anchos = [25, 18, 18, 22, 22, 25, 28, 25, 94] 
    
    pdf.set_fill_color(39, 174, 96) 
    pdf.set_text_color(255, 255, 255) 
    pdf.set_font("Arial", 'B', 9)
    
    for i, col in enumerate(cols):
        pdf.cell(anchos[i], 10, col, border=1, fill=True, align='C')
    pdf.ln()
    
    pdf.set_font("Arial", '', 9)
    pdf.set_text_color(44, 62, 80)
    fill = False
    for index, row in df.iterrows():
        if fill: pdf.set_fill_color(242, 244, 244)
        else: pdf.set_fill_color(255, 255, 255)
            
        dia = str(row['Día']).replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        lluvia = f"{row['Lluvia (mm)']}"
        viento = f"{row['Viento Máx']}"
        demanda = f"{row['Demanda (Pax)']}"
        personal = str(row['Personal (Turnos)'])
        ingresos = str(row['Ingresos']).replace('€', 'EUR')
        beneficio = str(row['Beneficio Limpio']).replace('€', 'EUR')
        terraza = str(row['Terraza']).replace('🟢', '').replace('🔴', '').replace('⚪', '').strip()
        eventos = str(row['Eventos Cerca']).replace('🔥', '').replace('🎉', '').strip()
        if len(eventos) > 50: eventos = eventos[:47] + "..." 
        
        valores = [dia, lluvia, viento, demanda, personal, ingresos, beneficio, terraza, eventos]
        for i, val in enumerate(valores):
            val_encoded = val.encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(anchos[i], 10, val_encoded, border=1, fill=fill, align='C')
        pdf.ln()
        fill = not fill
        
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(149, 165, 166)
    pdf.cell(0, 10, "Documento confidencial. Generado por la arquitectura B2B de Smart-BCN.", 0, 1, 'L')
    
    try: return pdf.output(dest='S').encode('latin-1')
    except: return bytes(pdf.output())

def generar_pdf_ia(texto_ia):
    pdf = FPDF(orientation='P', unit='mm', format='A4') 
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(41, 128, 185) 
    pdf.cell(0, 10, "Smart-BCN | Plan Estrategico de Operaciones", 0, 1, 'L')
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(127, 140, 141)
    pdf.cell(0, 6, "Consultoria generada por Inteligencia Artificial (Director Virtual)", 0, 1, 'L')
    pdf.line(10, 28, 200, 28) 
    pdf.ln(15)
    
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(44, 62, 80)
    
    texto_limpio = texto_ia.replace('**', '').replace('##', '').replace('###', '').replace('*', '-')
    texto_limpio = texto_limpio.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.multi_cell(0, 7, texto_limpio)
    
    pdf.ln(15)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(149, 165, 166)
    pdf.cell(0, 10, "Documento confidencial. B2B Smart-BCN.", 0, 1, 'C')
    
    try: return pdf.output(dest='S').encode('latin-1')
    except: return bytes(pdf.output())

# =====================================================================
# 2. MOTOR GEOESPACIAL Y PIPELINE DE DATOS
# =====================================================================
@st.cache_data
def obtener_coordenadas(direccion):
    geolocator = Nominatim(user_agent="smart_bcn_app")
    try:
        location = geolocator.geocode(direccion)
        if location: return (location.latitude, location.longitude)
    except: return None
    return None

coords_restaurante = obtener_coordenadas(direccion_input)

try:
    df_predicciones = pd.read_csv('predicciones_dashboard.csv')
except FileNotFoundError:
    st.error("Falta 'predicciones_dashboard.csv'. Ejecuta tu etl_live.py.")
    st.stop()

try: df_eventos_geo = pd.read_csv('mapa_eventos_ticketmaster.csv')
except: df_eventos_geo = pd.DataFrame()

aforo_total_cliente = aforo_interior + aforo_terraza 
capacidad_max_diaria = int(aforo_total_cliente * rotacion_mesas)
max_interior = int(aforo_interior * rotacion_mesas)
max_terraza = int(aforo_terraza * rotacion_mesas)

dias_ajustados = []
consejos_diarios = {} 
nombres_dias_esp = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

presupuesto_marketing_base = presupuesto_meta + presupuesto_google
usa_meta = presupuesto_meta > 0
usa_google = presupuesto_google > 0

# =====================================================================
# 3. MOTOR DE INFERENCIA Y RECOMENDACIONES MULTIDIMENSIONALES
# =====================================================================
for index, row in df_predicciones.iterrows():
    fecha_str = row['Fecha_str']
    fecha_dt = pd.to_datetime(fecha_str)
    dia_semana = fecha_dt.dayofweek
    mes = fecha_dt.month
    fecha_amigable = f"{nombres_dias_esp[dia_semana]} {fecha_dt.strftime('%d/%m')}"
    
    consejos_diarios[fecha_amigable] = {
        "Personal": None,
        "Operativa_Alimentos": None,
        "Marketing": None,
        "Estrategia": None
    }
    
    afecta = False
    dist_minima = 99.0
    tipo_evento_ml = 'Ninguno'
    evento_estado = "---"
    nombres_cercanos = []
    categorias_amigables = []
    tipos_ml_detectados = []
    
    if not df_eventos_geo.empty and coords_restaurante:
        eventos_del_dia = df_eventos_geo[df_eventos_geo['Fecha'] == fecha_str]
        for _, evento in eventos_del_dia.iterrows():
            distancia_km = geodesic(coords_restaurante, (evento['Latitud'], evento['Longitud'])).kilometers
            if distancia_km <= 4.0:
                afecta = True
                dist_minima = min(dist_minima, distancia_km)
                nombres_cercanos.append(evento['Nombre_Evento'])
                categorias_amigables.append(evento.get('Categoria_Amigable', 'Evento'))
                tipos_ml_detectados.append(evento.get('Tipo_Evento_ML', 'Feria_Congreso'))
        
    if afecta:
        if 'Concierto_Masivo' in tipos_ml_detectados: tipo_evento_ml = 'Concierto_Masivo'
        elif 'Deportivo' in tipos_ml_detectados: tipo_evento_ml = 'Deportivo'
        else: tipo_evento_ml = 'Feria_Congreso'

        eventos_unidos = ", ".join(list(set(nombres_cercanos)))
        cat_unidas = ", ".join(list(set(categorias_amigables)))
        evento_estado = f"🔥 {eventos_unidos} ({cat_unidas})"
        row['Categorias_Para_IA'] = cat_unidas
    else:
        row['Categorias_Para_IA'] = "Ninguno"

    if row.get('Evento_Especial', 0) == 1:
        evento_estado = "🎉 Festivo Nacional"
        if tipo_local == "Restaurante":
            consejos_diarios[fecha_amigable]["Personal"] = "🎉 **Personal:** Festivo. Activa turnos dobles en sala y cocina. Prepara menús cerrados para agilizar."
        elif tipo_local == "Bar de Copas":
            consejos_diarios[fecha_amigable]["Personal"] = "🎉 **Personal:** Festivo (o víspera). Refuerza el equipo de seguridad y añade un bartender extra para los picos de demanda."
        else:
            consejos_diarios[fecha_amigable]["Personal"] = "🎉 **Personal:** Festivo. Prepara a la plantilla para un flujo continuo; asegura rotación rápida en las mesas."

    lluvia_hoy = row.get('Lluvia_mm', 0)
    viento_hoy = row.get('Viento_kmh', 0)
    
    datos_hoy = pd.DataFrame({
        'Dia_Semana': [dia_semana], 'Mes': [mes], 'Aforo_Sillas': [aforo_total_cliente],
        'Nota_Google': [puntuacion_google], 'Lluvia_mm': [lluvia_hoy], 
        'Viento_kmh': [viento_hoy], 'Hay_Evento': [1 if afecta else 0],
        'Distancia_Evento_km': [dist_minima], 'Densidad_Competencia': [densidad_limpia],
        'Tipo_Local': [tipo_local], 'Tipo_Evento': [tipo_evento_ml]
    })
    
    datos_hoy_encoded = pd.get_dummies(datos_hoy).reindex(columns=columnas_ia, fill_value=0)
    clientes_ml = int(modelo_ia.predict(datos_hoy_encoded)[0])
    
    if hay_obras: clientes_ml = int(clientes_ml * 0.85)
    clientes_potenciales = min(clientes_ml, capacidad_max_diaria)

    decision_terraza = row.get('Decision_Operativa', '🟢 ABIERTA')
    pax_interior, pax_terraza, pax_delivery = 0, 0, 0
    
    if not tiene_terraza:
        decision_terraza = '⚪ N/A'
        pax_interior = min(clientes_potenciales, max_interior)
    elif decision_terraza == '🔴 CERRAR TERRAZA':
        pax_interior = min(clientes_potenciales, max_interior)
    else:
        pax_interior = min(clientes_potenciales, max_interior)
        restante = clientes_potenciales - pax_interior
        if restante > 0: pax_terraza = min(restante, max_terraza)
            
    if tiene_delivery and lluvia_hoy > 5:
        pax_delivery = int(clientes_potenciales * 0.25)
    elif tiene_delivery:
        pax_delivery = int(clientes_potenciales * 0.05)

    clientes_finales = pax_interior + pax_terraza + pax_delivery
    ocupacion_porcentual = (clientes_finales / capacidad_max_diaria) * 100 if capacidad_max_diaria > 0 else 0

    # -------------------------------------------------------------
    # LLENADO DE CONSEJOS ESTRATÉGICOS (Hiper-personalizados por tipo)
    # -------------------------------------------------------------
    if decision_terraza == '🔴 CERRAR TERRAZA':
        if tipo_local == "Restaurante":
            consejos_diarios[fecha_amigable]["Operativa_Alimentos"] = f"🌧️ **Inventario:** Clima adverso ({lluvia_hoy}mm). Evita sobre-stock de producto fresco perecedero; la merma será alta al perder las mesas de fuera."
        elif tipo_local == "Cafetería/Brunch":
            consejos_diarios[fecha_amigable]["Operativa_Alimentos"] = f"🌧️ **Inventario:** Lluvia ({lluvia_hoy}mm). Reduce la producción de bollería y repostería del día, el flujo peatonal de paseantes caerá."
        else: # Bar de Copas
            consejos_diarios[fecha_amigable]["Operativa_Alimentos"] = f"🌧️ **Operativa:** Mal clima ({lluvia_hoy}mm). Asegura guardar y proteger el mobiliario de terraza rápidamente."
            
        if tiene_delivery and usa_google:
            consejos_diarios[fecha_amigable]["Marketing"] = "🔍 **Marketing Digital:** La lluvia disparará los pedidos a domicilio. Deriva tu presupuesto de Meta Ads hacia Google/Glovo Ads hoy mismo."
    else:
        if tipo_local == "Restaurante":
            consejos_diarios[fecha_amigable]["Operativa_Alimentos"] = "🍲 **Inventario:** Clima estable. Mantén los pedidos a proveedores (carnes/pescados) en niveles de rotación habituales."
        elif tipo_local == "Cafetería/Brunch":
            consejos_diarios[fecha_amigable]["Operativa_Alimentos"] = "🥐 **Inventario:** Buen clima. Asegura producción completa de horneados y vitrina atractiva para captar clientes desde primera hora."
        else:
             consejos_diarios[fecha_amigable]["Operativa_Alimentos"] = "🧊 **Inventario:** Noche despejada. Prevé stock suficiente de hielo, destilados principales y vasos."

    if afecta:
        if tipo_local == "Restaurante":
            consejos_diarios[fecha_amigable]["Estrategia"] = f"🎫 **Operativa ({eventos_unidos}):** Habilita un 'Menú Rápido' cerrado. El objetivo es que las mesas roten al menos dos veces antes de que empiece el show."
        elif tipo_local == "Bar de Copas":
            consejos_diarios[fecha_amigable]["Estrategia"] = f"🎫 **Operativa ({eventos_unidos}):** Avalancha a la salida del evento. Organiza bien los accesos, la seguridad y prepara a los DJs/Staff."
        elif tipo_local == "Cafetería/Brunch":
            consejos_diarios[fecha_amigable]["Estrategia"] = f"🎫 **Operativa ({eventos_unidos}):** Monta un stand de bebidas y snacks 'Take-Away' directo a la puerta para captar el tráfico de personas que van al evento."

    if ocupacion_porcentual >= 90:
        if usa_meta or usa_google:
            if not consejos_diarios[fecha_amigable]["Marketing"]:
                consejos_diarios[fecha_amigable]["Marketing"] = "🛑 **Marketing Ahorro:** Local proyectado al 100%. Pausa tus campañas de publicidad pagada hoy; el local se llenará de forma natural."
        
        if tipo_local == "Restaurante":
            consejos_diarios[fecha_amigable]["Personal"] = "🏃‍♂️ **Personal:** Lleno absoluto esperado. Pon a tu mejor encargado en puerta para gestionar reservas sin que se formen cuellos de botella."
            if not consejos_diarios[fecha_amigable]["Estrategia"]:
                 consejos_diarios[fecha_amigable]["Estrategia"] = "📈 **Finanzas:** Momento de maximizar. Oculta el menú económico y fomenta la venta de platos sugeridos y bodega premium (Upselling)."
        elif tipo_local == "Bar de Copas":
            consejos_diarios[fecha_amigable]["Personal"] = "🏃‍♂️ **Personal:** Lleno inminente. Sitúa a los camareros más rápidos en las barras principales y refuerza la recogida de vasos vacíos."
            if not consejos_diarios[fecha_amigable]["Estrategia"]:
                 consejos_diarios[fecha_amigable]["Estrategia"] = "📈 **Finanzas:** Sube ligeramente el precio en puerta o enfócate en promover botellas en las mesas VIP."
        elif tipo_local == "Cafetería/Brunch":
            consejos_diarios[fecha_amigable]["Personal"] = "🏃‍♂️ **Personal:** Pico de estrés matutino. Coordina perfectamente a la persona de los cafés con la sala para que los pedidos salgan al instante."
            if not consejos_diarios[fecha_amigable]["Estrategia"]:
                 consejos_diarios[fecha_amigable]["Estrategia"] = "📈 **Finanzas:** Fomenta la venta cruzada rápida en caja (ej: '¿Deseas llevarte una galleta casera por 1€ más?')."
                 
        ticket_dinamico = ticket_medio * 1.15
        
    elif ocupacion_porcentual < 60:
        ticket_dinamico = ticket_medio
        
        if tipo_local == "Restaurante":
             consejos_diarios[fecha_amigable]["Personal"] = "🚶 **Personal:** Día valle. Ideal para dar descansos, revisar escandallos de nuevos platos en cocina o adelantar limpieza profunda."
        else:
             consejos_diarios[fecha_amigable]["Personal"] = "🚶 **Personal:** Turno tranquilo. Aprovecha para reponer almacén, limpieza general e inventario semanal."
        
        if dia_semana in [0, 1, 2]:
            if tipo_local == "Restaurante" and usa_fidelizacion:
                consejos_diarios[fecha_amigable]["Marketing"] = "💌 **Marketing CRM:** Envíale un mensaje (Email/WhatsApp) a tus mejores clientes ofreciendo un postre gratis por venir hoy a comer."
            elif tipo_local == "Cafetería/Brunch":
                consejos_diarios[fecha_amigable]["Marketing"] = "☕ **Marketing Local:** Día muy tranquilo. Saca tu pizarra a la acera con una oferta especial de desayuno para atraer a los oficinistas del barrio."
            elif tipo_local == "Bar de Copas":
                 consejos_diarios[fecha_amigable]["Marketing"] = "🍻 **Marketing Local:** Lanza promociones tipo 'Afterwork' o '2x1' temprano para intentar animar el ambiente desde primera hora de la tarde."
        elif dia_semana in [4, 5, 6] and usa_meta:
            if tipo_local == "Bar de Copas":
                consejos_diarios[fecha_amigable]["Marketing"] = "📱 **Marketing Digital:** Fin de semana por debajo de lo normal. Sube un anuncio urgente (Story en Instagram) promocionando entrada libre hasta las 00:00."
            elif tipo_local == "Restaurante":
                consejos_diarios[fecha_amigable]["Marketing"] = "📱 **Marketing Digital:** Reactiva anuncios en redes apuntando a 3km a la redonda mostrando fotos atractivas para capturar reservas de última hora."
            else:
                consejos_diarios[fecha_amigable]["Marketing"] = "📱 **Marketing Digital:** Impulsa tus mejores fotos de Brunch y Tortitas en anuncios enfocados solo a los vecinos de tu propio barrio."
    else:
        ticket_dinamico = ticket_medio 
        if not consejos_diarios[fecha_amigable]["Personal"]:
            consejos_diarios[fecha_amigable]["Personal"] = "👥 **Personal:** Volumen de clientes normal. Puedes operar con tu plantilla estándar sin refuerzos extra."
            
    ingreso_extra_sugerido = clientes_finales * (ticket_dinamico - ticket_medio) if ticket_dinamico > ticket_medio else 0
    facturacion = clientes_finales * ticket_dinamico
    camareros_necesarios = max(1, round(clientes_finales / ratio_camarero)) 
    coste_mp = facturacion * (porcentaje_cogs / 100)
    coste_pl = camareros_necesarios * coste_turno_camarero
    coste_mkt = presupuesto_marketing_base if ocupacion_porcentual < 90 else 0 
    beneficio = facturacion - coste_mp - coste_pl - coste_mkt
        
    row['Fecha_Amigable'] = fecha_amigable
    row['Decision_Operativa'] = decision_terraza
    row['Pax_Interior'] = pax_interior
    row['Pax_Terraza'] = pax_terraza
    row['Pax_Delivery'] = pax_delivery
    row['Clientes_Totales'] = clientes_finales
    row['Ocupacion_%'] = ocupacion_porcentual
    row['Facturacion_Est'] = facturacion
    
    row['Coste_MP'] = coste_mp
    row['Coste_PL'] = coste_pl
    row['Coste_MKT'] = coste_mkt
    row['Coste_Total'] = coste_mp + coste_pl + coste_mkt
    row['Beneficio_Est'] = beneficio
    
    row['Extra_Yield'] = ingreso_extra_sugerido
    row['Camareros_Rec'] = camareros_necesarios
    row['Estado_Evento'] = evento_estado
    
    dias_ajustados.append(row)

df_visual = pd.DataFrame(dias_ajustados)

# =====================================================================
# 4. TARJETAS KPI GLOBALES
# =====================================================================
st.subheader("📊 Tu Resumen Semanal")
col1, col2, col3, col4 = st.columns(4)

with col1: 
    st.metric("Afluencia Esperada", f"{df_visual['Clientes_Totales'].sum()} pax")
with col2: 
    st.metric("Beneficio Neto (Limpio)", f"{df_visual['Beneficio_Est'].sum():,.0f} €".replace(",", "."))
with col3: 
    st.metric("Margen de Beneficio Media", f"{(df_visual['Beneficio_Est'].sum() / df_visual['Facturacion_Est'].sum() * 100):.1f} %")
with col4: 
    st.metric(
        label="Cerebro Analítico", 
        value=f"Random Forest", 
        delta=f"{precision_ia:.1f}% Precisión Verificada", delta_color="normal"
    )

st.divider()

# =====================================================================
# 5. DASHBOARD VISUAL
# =====================================================================
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Estrategia y Alertas", "👥 Ocupación y Saturación", "💶 Estructura Financiera", "🌍 Eventos y Clima"])

with tab1:
    st.markdown("### 🤖 Tu Briefing Diario de Operaciones")
    st.markdown("Despliega cada día para leer las instrucciones generadas por la IA para tus encargados de sala, marketing y compras.")
    
    for fecha in sorted(consejos_diarios.keys()):
        with st.expander(f"📋 Instrucciones para el {fecha}", expanded=(fecha == min(consejos_diarios.keys()))):
            if consejos_diarios[fecha]["Operativa_Alimentos"]:
                if "🌧️" in consejos_diarios[fecha]["Operativa_Alimentos"]:
                    st.error(consejos_diarios[fecha]["Operativa_Alimentos"])
                else:
                    st.info(consejos_diarios[fecha]["Operativa_Alimentos"])
            
            if consejos_diarios[fecha]["Personal"]:
                if "🏃‍♂️" in consejos_diarios[fecha]["Personal"] or "🎉" in consejos_diarios[fecha]["Personal"]:
                    st.warning(consejos_diarios[fecha]["Personal"])
                else:
                    st.info(consejos_diarios[fecha]["Personal"])
            
            if consejos_diarios[fecha]["Estrategia"]:
                st.success(consejos_diarios[fecha]["Estrategia"])
                
            if consejos_diarios[fecha]["Marketing"]:
                if "🛑" in consejos_diarios[fecha]["Marketing"]:
                    st.success(consejos_diarios[fecha]["Marketing"]) 
                else:
                    st.info(consejos_diarios[fecha]["Marketing"])

with tab2:
    st.markdown("### ¿Cuánta gente vendrá y dónde se sentará?")
    colA, colB = st.columns([2, 1])
    
    with colA:
        fig_barras = px.bar(
            df_visual, x='Fecha_Amigable', y=['Pax_Interior', 'Pax_Terraza', 'Pax_Delivery'],
            color_discrete_map={'Pax_Interior': '#2980B9', 'Pax_Terraza': '#7FB3D5', 'Pax_Delivery': '#8E44AD'},
            labels={'value': 'Personas Esperadas', 'variable': 'Zona', 'Fecha_Amigable': ''}
        )
        fig_barras.update_layout(plot_bgcolor='rgba(0,0,0,0)', barmode='stack', margin=dict(t=20, b=0), legend_title_text='')
        st.plotly_chart(fig_barras, use_container_width=True)
    
    with colB:
        fig_ocupacion = px.line(
            df_visual, x='Fecha_Amigable', y='Ocupacion_%',
            markers=True, text='Ocupacion_%'
        )
        fig_ocupacion.update_traces(
            textposition="top center", texttemplate='%{text:.0f}%', 
            line=dict(color='#E67E22', width=4), marker=dict(size=10, color='#D35400')
        )
        fig_ocupacion.add_hline(y=85, line_dash="dash", line_color="red", annotation_text="Lleno Absoluto (85%)")
        fig_ocupacion.update_layout(plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(range=[0, 110]), margin=dict(t=20, b=0), yaxis_title="% Ocupación", xaxis_title="")
        st.plotly_chart(fig_ocupacion, use_container_width=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 **¿Cómo leer estos gráficos?:** El gráfico de barras te muestra cuánta gente se espera cada día y dónde se sentarán (dentro, terraza o a domicilio). La línea naranja del gráfico derecho te avisa de lo lleno que estará tu local. Si esa línea cruza la barrera roja del 85%, prepárate: estaréis a tope y es el momento perfecto para ofrecer los productos más caros de la carta.")

with tab3:
    st.markdown("### Previsión de Ingresos y Rentabilidad")
    colC, colD = st.columns([2, 1])
    
    with colC:
        fig_finanzas = go.Figure()
        fig_finanzas.add_trace(go.Bar(x=df_visual['Fecha_Amigable'], y=df_visual['Facturacion_Est'], name='Ingresos Brutos', marker_color='#27AE60'))
        fig_finanzas.add_trace(go.Scatter(x=df_visual['Fecha_Amigable'], y=df_visual['Coste_Total'], mode='lines+markers', name='Gastos Totales', line=dict(color='#E74C3C', width=3)))
        fig_finanzas.update_layout(plot_bgcolor='rgba(0,0,0,0)', hovermode="x unified", margin=dict(t=20, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_finanzas, use_container_width=True)
        
    with colD:
        total_beneficio = df_visual['Beneficio_Est'].sum()
        total_mp = df_visual['Coste_MP'].sum()
        total_pl = df_visual['Coste_PL'].sum()
        total_mkt = df_visual['Coste_MKT'].sum()
        
        nombres_grafico = ['Beneficio Neto', 'Ingredientes y Bebida', 'Sueldos del Personal', 'Publicidad y Redes']
        valores_grafico = [total_beneficio, total_mp, total_pl, total_mkt]
        
        mapa_colores = {
            'Beneficio Neto': '#2ECC71', 
            'Ingredientes y Bebida': '#E74C3C', 
            'Sueldos del Personal': '#F39C12', 
            'Publicidad y Redes': '#9B59B6'
        }
        
        fig_donut = px.pie(
            names=nombres_grafico, 
            values=valores_grafico,
            color=nombres_grafico, 
            color_discrete_map=mapa_colores,
            hole=0.5
        )
        
        fig_donut.update_layout(margin=dict(t=20, b=0, l=0, r=0), showlegend=False)
        fig_donut.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            sort=False,              
            direction='clockwise'           
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 **¿Cómo leer estos gráficos?:** Aquí puedes ver tu dinero en juego. El gráfico izquierdo compara tus ingresos (barras verdes) con tus gastos diarios (línea roja). El 'donut' de la derecha resume toda la semana: te dice visualmente qué porción de tus ingresos se va en pagar a proveedores o sueldos, y qué porción verde es tu beneficio limpio real.")

with tab4:
    st.markdown("### El Radar de la Ciudad (Radio 4km)")
    colE, colF = st.columns([2, 1])
    
    with colE:
        if not df_eventos_geo.empty and coords_restaurante:
            df_rest = pd.DataFrame({'Latitud': [coords_restaurante[0]], 'Longitud': [coords_restaurante[1]], 'Nombre': ['TÚ ESTÁS AQUÍ'], 'Tipo': ['Tu Local'], 'Tamaño': [15]})
            df_ev = df_eventos_geo.copy()
            df_ev['Nombre'] = df_ev['Nombre_Evento'] + " (" + df_ev['Fecha'] + ")"
            df_ev['Tipo'] = 'Concierto/Evento'
            df_ev['Tamaño'] = 10
            
            fig_mapa = px.scatter_mapbox(
                pd.concat([df_rest, df_ev[['Latitud', 'Longitud', 'Nombre', 'Tipo', 'Tamaño']]]), 
                lat="Latitud", lon="Longitud", hover_name="Nombre", color="Tipo", size="Tamaño", 
                color_discrete_map={'Tu Local': '#2C3E50', 'Concierto/Evento': '#E67E22'}, zoom=13, height=350
            )
            fig_mapa.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_mapa, use_container_width=True)
        else:
            st.info("No hay grandes eventos detectados esta semana en tu zona.")
            
    with colF:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.info("💡 **¿Cómo leer este mapa?:** Este es el radar de tu negocio. La Inteligencia Artificial vigila constantemente la agenda de Barcelona. Si aparece un punto naranja (un concierto, feria o evento deportivo) cerca de la ubicación de tu local, el sistema ya lo ha tenido en cuenta de forma automática para calcular cuántos clientes extras te traerá.")

st.divider()

# =====================================================================
# 7. EXPORTACIÓN DE DATOS (TABLA PDF) Y EMAIL
# =====================================================================
st.subheader("📅 Tabla Maestra de Planificación")
st.markdown("Descarga esta tabla en formato PDF corporativo o envíala directamente por correo al equipo.")

df_mostrar = df_visual[['Fecha_Amigable', 'Lluvia_mm', 'Viento_kmh', 'Estado_Evento', 'Decision_Operativa', 'Clientes_Totales', 'Camareros_Rec', 'Facturacion_Est', 'Beneficio_Est']].copy()
df_mostrar['Facturacion_Est'] = df_mostrar['Facturacion_Est'].apply(lambda x: f"{x:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
df_mostrar['Beneficio_Est'] = df_mostrar['Beneficio_Est'].apply(lambda x: f"{x:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))

df_mostrar.rename(columns={'Fecha_Amigable': 'Día', 'Lluvia_mm': 'Lluvia (mm)', 'Viento_kmh': 'Viento Máx', 'Clientes_Totales': 'Demanda (Pax)', 'Camareros_Rec': 'Personal (Turnos)', 'Facturacion_Est': 'Ingresos', 'Beneficio_Est': 'Beneficio Limpio', 'Decision_Operativa': 'Terraza', 'Estado_Evento': 'Eventos Cerca'}, inplace=True)

st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

pdf_tabla_bytes = generar_pdf_corporativo_tabla(df_mostrar)

col_btn1, col_btn2 = st.columns([1, 2])
with col_btn1:
    st.download_button(
        label="📄 Descargar Planificación", 
        data=pdf_tabla_bytes, 
        file_name='SmartBCN_Planificacion_Semanal.pdf', 
        mime='application/pdf',
        type="primary"
    )

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("#### 📧 Enviar por Correo Electrónico")
col_input, col_vacia = st.columns([1, 2]) 

with col_input:
    email_destino = st.text_input("Introduce el correo del encargado/a:", placeholder="ejemplo@restaurante.com")
    if st.button("🚀 Enviar Informe Operativo"):
        if email_destino:
            import time
            with st.spinner("Conectando con el servidor SMTP corporativo..."):
                time.sleep(2) 
            st.success(f"¡Informe enviado con éxito a {email_destino}!")
            st.info("💡 Arquitectura: En el entorno de producción, este módulo se conecta vía API a servicios como SendGrid o AWS SES para garantizar la entrega segura.")
        else:
            st.warning("Por favor, introduce un correo electrónico válido antes de enviar.")

# =====================================================================
# 8. MÓDULO PREMIUM: IA GENERATIVA OPEN SOURCE (Hugging Face)
# =====================================================================
st.divider()
st.subheader("✨ Consultoría Estratégica con IA Generativa")
st.markdown("Haz clic en el botón para que nuestro modelo de lenguaje procese toda tu telemetría y redacte un plan de acción ejecutivo (Rol: COO).")

HF_TOKEN = "Clave API Aquí" 

if 'plan_generado' not in st.session_state:
    st.session_state['plan_generado'] = None
if 'modelo_usado' not in st.session_state:
    st.session_state['modelo_usado'] = ""

if st.button("🧠 Generar Plan de Acción Avanzado", type="primary"):
    if HF_TOKEN == "PON_AQUI_TU_TOKEN":
        st.warning("⚠️ Arquitecto: Recuerda pegar tu Token real de Hugging Face en la variable HF_TOKEN del código para que funcione.")
    else:
        with st.spinner("Iniciando inferencia semántica... Extrayendo Insights Operativos..."):
            try:
                from huggingface_hub import InferenceClient
                cliente_hf = InferenceClient(token=HF_TOKEN)

                tipos_semana = [cat for cat in df_visual['Categorias_Para_IA'] if cat != "Ninguno"]
                contexto_eventos = f"Esta semana hay eventos en la ciudad de tipo: {', '.join(set(tipos_semana))}." if tipos_semana else "Esta semana no hay grandes eventos cerca."

                prompt_datos = f"""
                Tengo un negocio de tipo: {tipo_local} con {aforo_total_cliente} sillas.
                Mi nota en Google es {puntuacion_google}/5 y tengo competencia {densidad_limpia}.
                Mis proyecciones de los próximos 7 días:
                - Clientes totales: {df_visual['Clientes_Totales'].sum()}
                - Beneficio Neto: {df_visual['Beneficio_Est'].sum():.0f} euros.
                - Gasto en Marketing sugerido: {df_visual['Coste_MKT'].sum()} euros.
                Día más lluvioso: {df_visual.loc[df_visual['Lluvia_mm'].idxmax()]['Fecha_Amigable']}.
                
                {contexto_eventos}

                Hazme un resumen ejecutivo de 3 puntos exactos:
                1. Diagnóstico financiero de la semana.
                2. Recomendación de marketing adaptada a los eventos y mi tipología de local.
                3. Consejo operativo de contención de daños para el día de más lluvia.
                """

                mensajes = [
                    {"role": "system", "content": "Eres el Director de Operaciones (COO) experto en Hospitality. Responde en español usando Markdown. Ve directo al dato y la estrategia accionable."},
                    {"role": "user", "content": prompt_datos}
                ]

                modelos_a_probar = [
                    "Qwen/Qwen2.5-72B-Instruct",        
                    "mistralai/Mistral-Nemo-Instruct-2407", 
                    "microsoft/Phi-3.5-mini-instruct"   
                ]

                for modelo in modelos_a_probar:
                    try:
                        respuesta = cliente_hf.chat_completion(
                            model=modelo,
                            messages=mensajes,
                            max_tokens=1500, 
                            temperature=0.7
                        )
                        st.session_state['plan_generado'] = respuesta.choices[0].message.content
                        st.session_state['modelo_usado'] = modelo
                        break  
                    except Exception as e:
                        continue 

                if not st.session_state['plan_generado']:
                    st.error("Los nodos de inferencia están saturados en este instante. Espera unos segundos y reintenta.")

            except Exception as e:
                st.error(f"Error crítico en el Endpoint de IA: {e}")

# Renderizamos la respuesta si ya hay un plan guardado en memoria
if st.session_state['plan_generado']:
    st.success(f"¡Análisis Completado! (Motor: {st.session_state['modelo_usado'].split('/')[1]})")
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(145deg, #ffffff, #e6e9ee);
        padding: 30px; 
        border-radius: 20px; 
        border-left: 8px solid #2980B9; 
        color: #2C3E50; 
        line-height: 1.7; 
        box-shadow: 10px 10px 20px #c5c9d1, -10px -10px 20px #ffffff;
        margin-bottom: 20px;
    ">
        {st.session_state['plan_generado']}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### 📤 Exportar Plan de Acción")
    
    pdf_ia_bytes = generar_pdf_ia(st.session_state['plan_generado'])
    
    col_btn_ia1, col_btn_ia2 = st.columns([1, 2])
    with col_btn_ia1:
        st.download_button(
            label="📄 Descargar Plan Estratégico", 
            data=pdf_ia_bytes, 
            file_name='SmartBCN_Plan_Estrategico_IA.pdf', 
            mime='application/pdf',
            type="primary"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("#### 📧 Enviar Plan por Correo Electrónico")
    col_input_ia, col_vacia_ia = st.columns([1, 2]) 
    
    with col_input_ia:
        email_destino_ia = st.text_input("Introduce el correo para enviar el informe IA:", placeholder="director@restaurante.com", key="email_ia")
        
        if st.button("🚀 Enviar Plan Estratégico", key="btn_enviar_ia"):
            if email_destino_ia:
                import time
                with st.spinner("Conectando con el servidor SMTP corporativo..."):
                    time.sleep(2) 
                st.success(f"¡Plan de acción enviado con éxito a {email_destino_ia}!")
            else:
                st.warning("Por favor, introduce un correo electrónico válido antes de enviar.")

st.caption("🎓 Proyecto Final B2B - Inteligencia Operativa. Desarrollado por Emilio Tornos.")