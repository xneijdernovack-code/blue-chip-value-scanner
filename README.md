# Blue Chip Value Scanner — MVP gratuito

Aplicación web de investigación fundamental para acciones del S&P 500, Nasdaq 100 y Dow Jones.

## Qué incluye
- Carga de componentes de índices desde tablas públicas.
- Precios e indicadores financieros mediante `yfinance`.
- Score inicial con ponderaciones: valoración 35%, calidad 35%, crecimiento 20%, riesgo 10%.
- Gráfico de precio de un año, filtros, tabla ordenable y exportación CSV.
- Caché para reducir llamadas repetidas.

## Limitaciones importantes
- `yfinance` no es una API oficial de Yahoo Finance; está orientada a investigación/uso personal y puede cambiar o limitarse.
- La carga de componentes desde Wikipedia depende de la disponibilidad y estructura de esas tablas.
- El análisis de múltiplos históricos a cinco años y los descuentos frente a la industria están explícitamente pendientes. No se inventan.
- Las métricas contables varían por sector y por criterios de reporte. La versión inicial es un prototipo, no una recomendación de inversión.
- El score es relativo al conjunto de empresas descargadas en esa ejecución, no un valor intrínseco ni una señal de compra.

## Ejecutar localmente
Requiere Python 3.10+.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Publicar gratis en Streamlit Community Cloud
1. Sube el contenido de esta carpeta a un repositorio GitHub.
2. Entra a https://share.streamlit.io/ y conecta GitHub.
3. Selecciona el repositorio y el archivo `app.py`.
4. Publica la aplicación.

No añadas claves privadas ni credenciales al repositorio. Esta versión no necesita API key.
