import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timezone

st.set_page_config(page_title="Blue Chip Value Scanner", page_icon="📊", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {background: rgba(128,128,128,.08); padding: 12px; border-radius: 10px;}
div[data-testid="stDataFrame"] {border: 1px solid rgba(128,128,128,.2); border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

st.title("📊 Blue Chip Value Scanner")
st.caption("S&P 500 · Nasdaq 100 · Dow Jones | Fundamental value & quality research")

INDEX_URLS = {
    "S&P 500": "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
    "Nasdaq 100": "https://en.wikipedia.org/wiki/Nasdaq-100",
    "Dow Jones": "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average",
}

@st.cache_data(ttl=86400, show_spinner=False)
def load_universe():
    frames = []
    errors = []
    try:
        t = pd.read_html(INDEX_URLS["S&P 500"])[0]
        frames.append(pd.DataFrame({"Ticker": t["Symbol"].astype(str).str.replace(".", "-", regex=False),
                                    "Company": t["Security"].astype(str),
                                    "Sector": t["GICS Sector"].astype(str),
                                    "Index": "S&P 500"}))
    except Exception as e:
        errors.append("S&P 500: " + str(e)[:140])
    try:
        tables = pd.read_html(INDEX_URLS["Nasdaq 100"])
        found = False
        for t in tables:
            cols = [str(c).lower() for c in t.columns]
            ticker_col = next((c for c in t.columns if "ticker" in str(c).lower() or "symbol" in str(c).lower()), None)
            name_col = next((c for c in t.columns if "company" in str(c).lower() or "security" in str(c).lower()), None)
            if ticker_col is not None and name_col is not None:
                tmp = pd.DataFrame({"Ticker": t[ticker_col].astype(str).str.replace(".", "-", regex=False),
                                    "Company": t[name_col].astype(str), "Sector": "Not classified",
                                    "Index": "Nasdaq 100"})
                frames.append(tmp); found = True; break
        if not found: errors.append("No se reconoció la tabla del Nasdaq 100.")
    except Exception as e:
        errors.append("Nasdaq 100: " + str(e)[:140])
    try:
        tables = pd.read_html(INDEX_URLS["Dow Jones"])
        found = False
        for t in tables:
            ticker_col = next((c for c in t.columns if "symbol" in str(c).lower() or "ticker" in str(c).lower()), None)
            name_col = next((c for c in t.columns if "company" in str(c).lower()), None)
            if ticker_col is not None and name_col is not None:
                frames.append(pd.DataFrame({"Ticker": t[ticker_col].astype(str).str.replace(".", "-", regex=False),
                                            "Company": t[name_col].astype(str), "Sector": "Not classified",
                                            "Index": "Dow Jones"}))
                found = True; break
        if not found: errors.append("No se reconoció la tabla del Dow Jones.")
    except Exception as e:
        errors.append("Dow Jones: " + str(e)[:140])
    if not frames:
        return pd.DataFrame(), errors
    data = pd.concat(frames, ignore_index=True)
    data["Index"] = data.groupby("Ticker")["Index"].transform(lambda x: " + ".join(sorted(set(x))))
    data = data.drop_duplicates("Ticker").sort_values("Ticker").reset_index(drop=True)
    return data, errors

def safe_num(obj, key):
    try:
        v = obj.get(key)
        return float(v) if v is not None and np.isfinite(float(v)) else np.nan
    except Exception:
        return np.nan

def get_statement_value(df, candidates, column=-1):
    if df is None or df.empty:
        return np.nan
    for name in candidates:
        if name in df.index:
            try:
                val = df.loc[name].iloc[column]
                return float(val) if pd.notna(val) else np.nan
            except Exception:
                pass
    return np.nan

@st.cache_data(ttl=21600, show_spinner=False)
def fetch_one(ticker):
    t = yf.Ticker(ticker)
    try: info = t.get_info()
    except Exception: info = {}
    try: inc = t.income_stmt
    except Exception: inc = pd.DataFrame()
    try: bs = t.balance_sheet
    except Exception: bs = pd.DataFrame()
    try: cf = t.cashflow
    except Exception: cf = pd.DataFrame()
    try: hist = t.history(period="1y", auto_adjust=True)
    except Exception: hist = pd.DataFrame()

    price = safe_num(info, "currentPrice")
    if not np.isfinite(price) and not hist.empty:
        price = float(hist["Close"].dropna().iloc[-1])
    market_cap = safe_num(info, "marketCap")
    pe = safe_num(info, "trailingPE")
    fwd_pe = safe_num(info, "forwardPE")
    ev_ebitda = safe_num(info, "enterpriseToEbitda")
    p_fcf = safe_num(info, "priceToFreeCashflow")
    roe = safe_num(info, "returnOnEquity")
    op_margin = safe_num(info, "operatingMargins")
    profit_margin = safe_num(info, "profitMargins")
    debt_equity = safe_num(info, "debtToEquity")
    sector = info.get("sector", "Not classified")
    industry = info.get("industry", "Not classified")
    name = info.get("shortName") or info.get("longName") or ticker

    rev_now = get_statement_value(inc, ["Total Revenue", "Operating Revenue"])
    rev_old = get_statement_value(inc, ["Total Revenue", "Operating Revenue"], column=3)
    rev_growth_3y = (rev_now / rev_old) ** (1/3) - 1 if rev_now > 0 and rev_old > 0 else np.nan
    ebitda = get_statement_value(inc, ["EBITDA", "Normalized EBITDA"])
    total_debt = get_statement_value(bs, ["Total Debt", "Long Term Debt And Capital Lease Obligation"])
    cash = get_statement_value(bs, ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"])
    net_debt = total_debt - cash if np.isfinite(total_debt) and np.isfinite(cash) else np.nan
    debt_ebitda = net_debt / ebitda if np.isfinite(net_debt) and np.isfinite(ebitda) and ebitda > 0 else np.nan
    fcf = get_statement_value(cf, ["Free Cash Flow"])
    if not np.isfinite(fcf):
        ocf = get_statement_value(cf, ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"])
        capex = get_statement_value(cf, ["Capital Expenditure", "Capital Expenditures"])
        fcf = ocf + capex if np.isfinite(ocf) and np.isfinite(capex) else np.nan
    fcf_yield = fcf / market_cap if np.isfinite(fcf) and market_cap > 0 else np.nan

    return {
        "Ticker": ticker, "Empresa": name, "Sector": sector, "Industria": industry,
        "Precio": price, "Market Cap": market_cap, "P/E": pe, "Forward P/E": fwd_pe,
        "EV/EBITDA": ev_ebitda, "P/FCF": p_fcf, "FCF Yield": fcf_yield,
        "ROE": roe, "Margen operativo": op_margin, "Margen neto": profit_margin,
        "Crec. ingresos 3 años": rev_growth_3y, "Deuda neta/EBITDA": debt_ebitda,
        "Deuda/Patrimonio": debt_equity, "Histórico 5 años": np.nan,
        "Histórico disponible": False, "Historial precio": hist,
    }

def pct_rank(series, higher_is_better=True):
    s = pd.to_numeric(series, errors="coerce")
    if s.notna().sum() < 2: return pd.Series(np.nan, index=series.index)
    return (s.rank(pct=True, ascending=higher_is_better) * 100)

def score_data(df):
    out = df.copy()
    # Valuation: cheaper multiples and higher free-cash-flow yield score better.
    val_parts = []
    for col, high_good in [("P/E", False), ("Forward P/E", False), ("EV/EBITDA", False),
                           ("P/FCF", False), ("FCF Yield", True)]:
        s = out[col].where(out[col] > 0) if col != "FCF Yield" else out[col]
        val_parts.append(pct_rank(s, high_good).rename(col))
    out["Puntuación valoración"] = pd.concat(val_parts, axis=1).mean(axis=1)
    # Quality: profitability and cash generation; no ROIC estimate is fabricated.
    q_parts = [pct_rank(out[c], True) for c in ["ROE", "Margen operativo", "Margen neto"]]
    q_parts.append(out["FCF Yield"].gt(0).astype(float) * 100)
    out["Puntuación calidad"] = pd.concat(q_parts, axis=1).mean(axis=1)
    out["Puntuación crecimiento"] = pct_rank(out["Crec. ingresos 3 años"], True)
    # Lower net debt/EBITDA is preferable. Negative net debt is allowed and rewarded.
    out["Puntuación riesgo"] = pct_rank(out["Deuda neta/EBITDA"], False)
    weights = {"Puntuación valoración": .35, "Puntuación calidad": .35,
               "Puntuación crecimiento": .20, "Puntuación riesgo": .10}
    out["Score"] = sum(out[k] * w for k, w in weights.items())
    def verdict(x):
        if pd.isna(x): return "Datos insuficientes"
        if x >= 85: return "Oportunidad potencial"
        if x >= 70: return "Atractiva"
        if x >= 55: return "Razonable"
        if x >= 40: return "Cara"
        return "Muy cara / revisar"
    out["Veredicto"] = out["Score"].apply(verdict)
    return out

with st.sidebar:
    st.header("Filtros")
    selected_index = st.multiselect("Índices", ["S&P 500", "Nasdaq 100", "Dow Jones"],
                                    default=["S&P 500", "Nasdaq 100", "Dow Jones"])
    min_cap = st.selectbox("Capitalización mínima", ["Todas", "US$10B", "US$50B", "US$100B"], index=0)
    max_scan = st.slider("Máximo de empresas por actualización", 10, 100, 30, 10)
    refresh = st.button("↻ Actualizar datos", use_container_width=True)
    if refresh:
        st.cache_data.clear()
        st.rerun()

universe, errors = load_universe()
if universe.empty:
    st.error("No fue posible cargar la composición de los índices. Comprueba la conexión y vuelve a intentar.")
    for e in errors: st.caption(e)
    st.stop()

chosen = universe[universe["Index"].apply(lambda x: any(i in x for i in selected_index))]
sector_options = sorted([x for x in chosen["Sector"].dropna().unique() if x != "Not classified"])
sector_filter = st.sidebar.multiselect("Sectores", sector_options)
if sector_filter:
    chosen = chosen[chosen["Sector"].isin(sector_filter)]
if chosen.empty:
    st.warning("No hay empresas para los filtros seleccionados.")
    st.stop()

st.caption(f"Universo detectado: {len(universe)} tickers únicos · Selección actual: {len(chosen)}")
if errors:
    with st.expander("Avisos de carga del universo"):
        for e in errors: st.write("• " + e)

tickers = chosen["Ticker"].head(max_scan).tolist()
st.info(f"Esta primera versión analiza hasta {len(tickers)} empresas por ejecución para respetar los límites de las fuentes gratuitas. Puedes ampliar el lote en el panel lateral.")

records = []
progress = st.progress(0, text="Consultando datos financieros…")
for i, ticker in enumerate(tickers):
    try:
        records.append(fetch_one(ticker))
    except Exception:
        pass
    progress.progress((i + 1) / len(tickers), text=f"Analizando {ticker} ({i+1}/{len(tickers)})")
progress.empty()

if not records:
    st.error("No se recibieron datos financieros. Intenta más tarde o reduce el número de empresas.")
    st.stop()

df = pd.DataFrame(records)
df = score_data(df)
if min_cap != "Todas":
    threshold = {"US$10B": 10e9, "US$50B": 50e9, "US$100B": 100e9}[min_cap]
    df = df[df["Market Cap"] >= threshold]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Empresas analizadas", len(df))
c2.metric("Con score calculable", int(df["Score"].notna().sum()))
c3.metric("Atractivas o mejores", int(df["Score"].ge(70).sum()))
c4.metric("Datos consultados", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))

st.subheader("Radar de oportunidades")
display_cols = ["Ticker", "Empresa", "Sector", "Precio", "P/E", "Forward P/E", "EV/EBITDA",
                "FCF Yield", "ROE", "Margen operativo", "Crec. ingresos 3 años",
                "Deuda neta/EBITDA", "Puntuación valoración", "Puntuación calidad",
                "Puntuación crecimiento", "Puntuación riesgo", "Score", "Veredicto"]
fmt = {c: (lambda x: f"{x:.1%}") for c in ["FCF Yield", "ROE", "Margen operativo", "Crec. ingresos 3 años"]}
fmt.update({c: (lambda x: f"{x:.1f}") for c in ["P/E", "Forward P/E", "EV/EBITDA", "Deuda neta/EBITDA",
                                                "Puntuación valoración", "Puntuación calidad",
                                                "Puntuación crecimiento", "Puntuación riesgo", "Score"]})
st.dataframe(df[display_cols].sort_values("Score", ascending=False),
             use_container_width=True, hide_index=True, column_config={
                 "Precio": st.column_config.NumberColumn(format="$%.2f"),
                 "Market Cap": st.column_config.NumberColumn(format="$%.0f"),
             })

csv = df[display_cols].to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Descargar resultados CSV", csv, "blue_chip_value_scanner.csv", "text/csv")

st.subheader("Ficha de empresa")
selected_ticker = st.selectbox("Selecciona una acción", df["Ticker"].tolist())
row = df[df["Ticker"] == selected_ticker].iloc[0]
st.markdown(f"### {row['Empresa']} ({selected_ticker})")
a, b, c, d = st.columns(4)
a.metric("Score compuesto", "N/D" if pd.isna(row["Score"]) else f"{row['Score']:.1f}/100")
b.metric("P/E", "N/D" if pd.isna(row["P/E"]) else f"{row['P/E']:.1f}x")
c.metric("FCF Yield", "N/D" if pd.isna(row["FCF Yield"]) else f"{row['FCF Yield']:.1%}")
d.metric("ROE", "N/D" if pd.isna(row["ROE"]) else f"{row['ROE']:.1%}")
hist = row["Historial precio"]
if hist is not None and not hist.empty:
    st.line_chart(hist["Close"], height=220)
st.warning("El percentil histórico de múltiplos a 5 años y el descuento frente a la industria aún no se muestran: requieren series históricas y comparables sectoriales consistentes. No se sustituyen por estimaciones inventadas.")
st.caption("Uso educativo e investigativo. Datos de terceros pueden tener retrasos, errores o restricciones de uso. Verifica cada cifra en los informes oficiales antes de invertir.")
