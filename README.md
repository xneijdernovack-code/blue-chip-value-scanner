# Blue Chip Value Scanner

Recreación independiente de la interfaz mostrada en las capturas del usuario. Está construida en Streamlit y mantiene el universo localmente para evitar el scraping de componentes de índices que provocaba HTTP 403.

## Despliegue
1. Sube `app.py`, `requirements.txt` y la carpeta `.streamlit/config.toml` a un repositorio GitHub.
2. En Streamlit Community Cloud, crea una app desde ese repositorio, rama `main`, archivo `app.py`.
3. La primera carga puede tardar mientras instala las dependencias.

## Datos y limitaciones
- Precios y algunos fundamentales: Yahoo Finance a través de `yfinance`, interfaz no oficial y susceptible a bloqueos o cambios.
- El universo de tickers está embebido en `app.py`, por lo que no se consulta Wikipedia para recuperar listas y se elimina ese origen del HTTP 403.
- El universo semilla y el ranking son aproximados; no son una composición oficial del S&P 500 ni un ranking histórico de capitalización.
- La puntuación de calidad es un proxy, no el Piotroski F-Score oficial.
- La valoración histórica de cinco años no se incluye porque una serie fiable de fundamentales históricos requiere otra fuente de datos.
- Herramienta de investigación educativa, no asesoría financiera.
