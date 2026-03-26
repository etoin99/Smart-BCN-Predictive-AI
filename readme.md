# 🍽️ Smart-BCN: Inteligencia Operativa Predictiva para Hostelería

![Estado](https://img.shields.io/badge/Estado-Producción_MVP-brightgreen)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![Machine Learning](https://img.shields.io/badge/Modelo-Random_Forest-orange)

## 📌 Sobre el Proyecto

**Smart-BCN** es una plataforma SaaS B2B diseñada para revolucionar la toma de decisiones en el sector HORECA (Hostelería). El objetivo principal es pasar de la intuición a la optimización basada en datos. 

Este proyecto "End-to-End" combina predicción matemática con el pulso en vivo de la ciudad de Barcelona, analizando el clima (Open-Meteo) y la agenda de eventos (Ticketmaster) para anticipar la afluencia de clientes y sugerir estrategias operativas diarias mediante Inteligencia Artificial.

> 🔒 **Aviso de Propiedad Intelectual (IP):** Este repositorio público está enfocado en la **capa de despliegue y producción** del Producto Mínimo Viable (MVP). Por motivos de privacidad y protección algorítmica, los Jupyter Notebooks de ingeniería de datos y el archivo de pesos del modelo de Machine Learning (`.pkl`) se mantienen en un entorno local privado. 

## 📁 Estructura de este Repositorio

Los archivos disponibles en este repositorio demuestran la interfaz, la lógica de negocio final y la documentación ejecutiva del proyecto:

* `app.py`: Código fuente de la aplicación web (Dashboard interactivo construido con Streamlit). Contiene la lógica del motor de reglas y la inyección de prompts a Hugging Face.
* `predicciones_dashboard.csv` & `mapa_eventos_ticketmaster.csv`: Datasets resultantes del pipeline ETL listos para ser consumidos por el dashboard.
* `requirements.txt`: Dependencias del entorno de producción.
* `Informe - SMART BCN.docx`: Documento técnico y de negocio detallando la metodología, el descubrimiento del "Efecto Refugio" y el R² Score (81.3%).
* `PRESENTACION Smart-BCN_Predictive_AI.pptx`: Material de apoyo visual para la defensa del proyecto.
* `Vídeo_Explicación_Smart-BCN__De_los_datos_al_futuro.mp4`: Spot promocional B2B resumiendo el problema, la tecnología y la solución de la plataforma.

## 📊 Arquitectura del Sistema (Visión Global)

Aunque el repositorio muestra la fase final, el proyecto completo consta de:
1. **Generación de Datos:** Universo sintético de 5.000 días simulando 3 tipos de locales.
2. **Modelado Predictivo:** `RandomForestRegressor` optimizado para detectar interacciones cruzadas (clima vs. eventos).
3. **Restricciones Físicas:** Código híbrido que somete la predicción matemática al aforo real del local.
4. **Director Virtual (IA Generativa):** Integración con LLMs Open Source (vía API) para traducir la telemetría en consejos operativos para el gerente del local.

## 💻 Notas de Ejecución

Dado que los pesos del modelo (`modelo_core_demanda.pkl`) no están incluidos en este repositorio público por las razones de IP mencionadas, la ejecución local de `app.py` lanzará la alerta de seguridad nativa del sistema (`🚨 Error Crítico: No encuentro el cerebro de la IA`). 

Para visualizar el funcionamiento completo de la plataforma, por favor consulte el vídeo de demostración adjunto o la presentación ejecutiva.

## 🧑‍💻 Autor

Desarrollado como Proyecto Final de Especialización Data & Analytics.
* **Emilio Tornos** - Arquitecto de Datos / Analista Predictivo.
