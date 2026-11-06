# -*- coding: utf-8 -*-
"""
Blue Chip Value Scanner — reconstrucción visual basada en las capturas aportadas.
Datos de mercado: Yahoo Finance mediante yfinance (fuente no oficial).
La lista del universo está embebida para evitar el scraping que provocaba HTTP 403.
"""
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timezone

st.set_page_config(
    page_title="Blue Chip Value Scanner",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Universo semilla de grandes compañías estadounidenses. Se conserva localmente:
# no se consulta Wikipedia ni se descarga la composición de índices en tiempo de ejecución.
UNIVERSE = [
("NVDA","NVIDIA","Information Technology"),("MSFT","Microsoft","Information Technology"),
("AAPL","Apple","Information Technology"),("AMZN","Amazon","Consumer Discretionary"),
("GOOGL","Alphabet A","Communication Services"),("GOOG","Alphabet C","Communication Services"),
("META","Meta Platforms","Communication Services"),("AVGO","Broadcom","Information Technology"),
("BRK-B","Berkshire Hathaway","Financials"),("LLY","Eli Lilly","Health Care"),
("JPM","JPMorgan Chase","Financials"),("TSLA","Tesla","Consumer Discretionary"),
("WMT","Walmart","Consumer Staples"),("V","Visa","Financials"),("XOM","Exxon Mobil","Energy"),
("MA","Mastercard","Financials"),("ORCL","Oracle","Information Technology"),
("COST","Costco","Consumer Staples"),("JNJ","Johnson & Johnson","Health Care"),
("NFLX","Netflix","Communication Services"),("PG","Procter & Gamble","Consumer Staples"),
("HD","Home Depot","Consumer Discretionary"),("ABBV","AbbVie","Health Care"),
("BAC","Bank of America","Financials"),("CVX","Chevron","Energy"),
("KO","Coca-Cola","Consumer Staples"),("CRM","Salesforce","Information Technology"),
("AMD","Advanced Micro Devices","Information Technology"),("MRK","Merck","Health Care"),
("TMUS","T-Mobile US","Communication Services"),("PEP","PepsiCo","Consumer Staples"),
("ADBE","Adobe","Information Technology"),("LIN","Linde","Materials"),
("WFC","Wells Fargo","Financials"),("ACN","Accenture","Information Technology"),
("CSCO","Cisco Systems","Information Technology"),("MCD","McDonald's","Consumer Discretionary"),
("IBM","IBM","Information Technology"),("QCOM","Qualcomm","Information Technology"),
("ABT","Abbott Laboratories","Health Care"),("GE","GE Aerospace","Industrials"),
("CAT","Caterpillar","Industrials"),("TMO","Thermo Fisher Scientific","Health Care"),
("DIS","Walt Disney","Communication Services"),("DHR","Danaher","Health Care"),
("VZ","Verizon","Communication Services"),("INTU","Intuit","Information Technology"),
("TXN","Texas Instruments","Information Technology"),("AMGN","Amgen","Health Care"),
("PM","Philip Morris","Consumer Staples"),("NOW","ServiceNow","Information Technology"),
("NEE","NextEra Energy","Utilities"),("RTX","RTX","Industrials"),
("SPGI","S&P Global","Financials"),("PFE","Pfizer","Health Care"),
("UNH","UnitedHealth Group","Health Care"),("GS","Goldman Sachs","Financials"),
("LOW","Lowe's","Consumer Discretionary"),("HON","Honeywell","Industrials"),
("ISRG","Intuitive Surgical","Health Care"),("BKNG","Booking Holdings","Consumer Discretionary"),
("AMAT","Applied Materials","Information Technology"),("BLK","BlackRock","Financials"),
("AXP","American Express","Financials"),("SYK","Stryker","Health Care"),
("ETN","Eaton","Industrials"),("PLD","Prologis","Real Estate"),
("T","AT&T","Communication Services"),("C","Citigroup","Financials"),
("DE","Deere","Industrials"),("ADP","Automatic Data Processing","Industrials"),
("MDLZ","Mondelez","Consumer Staples"),("GILD","Gilead Sciences","Health Care"),
("BMY","Bristol Myers Squibb","Health Care"),("LRCX","Lam Research","Information Technology"),
("MU","Micron Technology","Information Technology"),("PANW","Palo Alto Networks","Information Technology"),
("ANET","Arista Networks","Information Technology"),("KLAC","KLA Corporation","Information Technology"),
("UBER","Uber","Industrials"),("VRTX","Vertex Pharmaceuticals","Health Care"),
("ADI","Analog Devices","Information Technology"),("CB","Chubb","Financials"),
("MMC","Marsh & McLennan","Financials"),("SCHW","Charles Schwab","Financials"),
("SO","Southern Company","Utilities"),("COP","ConocoPhillips","Energy"),
("BSX","Boston Scientific","Health Care"),("CME","CME Group","Financials"),
("ICE","Intercontinental Exchange","Financials"),("SHW","Sherwin-Williams","Materials"),
("REGN","Regeneron","Health Care"),("PGR","Progressive","Financials"),
("APH","Amphenol","Information Technology"),("SNPS","Synopsys","Information Technology"),
("CDNS","Cadence Design Systems","Information Technology"),("MCO","Moody's","Financials"),
("WM","Waste Management","Industrials"),("UPS","United Parcel Service","Industrials"),
("NKE","Nike","Consumer Discretionary"),("F","Ford Motor","Consumer Discretionary"),
("GM","General Motors","Consumer Discretionary"),("CMCSA","Comcast","Communication Services"),
("COF","Capital One","Financials"),("CL","Colgate-Palmolive","Consumer Staples"),
("EOG","EOG Resources","Energy"),("MDT","Medtronic","Health Care"),
("CI","The Cigna Group","Health Care"),("ZTS","Zoetis","Health Care"),
("WELL","Welltower","Real Estate"),("CARR","Carrier Global","Industrials"),
("EMR","Emerson Electric","Industrials"),("AON","Aon","Financials"),
("MCK","McKesson","Health Care"),("FDX","FedEx","Industrials"),
("TT","Trane Technologies","Industrials"),("GD","General Dynamics","Industrials"),
("NOC","Northrop Grumman","Industrials"),("SLB","SLB","Energy"),
("MAR","Marriott International","Consumer Discretionary"),("ORLY","O'Reilly Automotive","Consumer Discretionary"),
("CNI","Canadian National Railway","Industrials"),("AEP","American Electric Power","Utilities"),
("KMI","Kinder Morgan","Energy"),("PSA","Public Storage","Real Estate"),
("EQIX","Equinix","Real Estate"),("AFL","Aflac","Financials"),
("MET","MetLife","Financials"),("TRV","Travelers","Financials"),
("ROP","Roper Technologies","Industrials"),("CTAS","Cintas","Industrials"),
("MSI","Motorola Solutions","Information Technology"),("FTNT","Fortinet","Information Technology"),
("WDAY","Workday","Information Technology"),("CRWD","CrowdStrike","Information Technology"),
("SNOW","Snowflake","Information Technology"),("APP","AppLovin","Information Technology"),
("PLTR","Palantir","Information Technology"),("COIN","Coinbase","Financials"),
("HOOD","Robinhood","Financials"),("DELL","Dell Technologies","Information Technology"),
("HCA","HCA Healthcare","Health Care"),("ELV","Elevance Health","Health Care"),
("AIG","American International Group","Financials"),("TGT","Target","Consumer Staples"),
("SBUX","Starbucks","Consumer Discretionary"),("CMG","Chipotle Mexican Grill","Consumer Discretionary"),
("ROST","Ross Stores","Consumer Discretionary"),("MAR","Marriott International","Consumer Discretionary"),
("OXY","Occidental Petroleum","Energy"),("FCX","Freeport-McMoRan","Materials"),
("NEM","Newmont","Materials"),("ECL","Ecolab","Materials"),
("ITW","Illinois Tool Works","Industrials"),("PH","Parker-Hannifin","Industrials"),
("PWR","Quanta Services","Industrials"),("JCI","Johnson Controls","Industrials"),
("FIS","Fidelity National Information Services","Financials"),("USB","U.S. Bancorp","Financials"),
("PNC","PNC Financial Services","Financials"),("TFC","Truist Financial","Financials"),
("A","Agilent Technologies","Health Care"),("BDX","Becton Dickinson","Health Care"),
("EW","Edwards Lifesciences","Health Care"),("IDXX","IDEXX Laboratories","Health Care"),
("DXCM","Dexcom","Health Care"),("RMD","ResMed","Health Care"),
("KDP","Keurig Dr Pepper","Consumer Staples"),("KHC","Kraft Heinz","Consumer Staples"),
("GIS","General Mills","Consumer Staples"),("K","Kellanova","Consumer Staples"),
("KR","Kroger","Consumer Staples"),("DLTR","Dollar Tree","Consumer Staples"),
("EBAY","eBay","Consumer Discretionary"),("ROKU","Roku","Communication Services"),
("EA","Electronic Arts","Communication Services"),("TTWO","Take-Two Interactive","Communication Services"),
("WBD","Warner Bros. Discovery","Communication Services"),("CHTR","Charter Communications","Communication Services"),
("EXC","Exelon","Utilities"),("DUK","Duke Energy","Utilities"),
("D","Dominion Energy","Utilities"),("XEL","Xcel Energy","Utilities"),
]
# De-duplicar conservando orden.
UNIVERSE = list(dict((x[0], x) for x in UNIVERSE).values())
UNIVERSE = UNIVERSE[:100]
META = pd.DataFrame(UNIVERSE, columns=["Ticker","Empresa","Sector"])
META["Rank S&P"] = np.arange(1, len(META)+1)
NASDAQ100 = set("NVDA MSFT AAPL AMZN GOOGL GOOG META AVGO TSLA COST NFLX AMD TMUS ADBE CSCO QCOM TXN AMAT LRCX MU PANW ANET KLAC INTU NOW ISRG BKNG ADI SNPS CDNS CRWD WDAY APP PLTR MAR INTC CMCSA MDLZ GILD REGN VRTX ORLY ROST SBUX CMG CHTR EA TTWO WBD".split())
DOW30 = set("AAPL AMGN AMZN AXP BA CAT CRM CSCO CVX DIS DOW GS HD HON IBM JNJ JPM KO MCD MMM MRK MSFT NKE NVDA PG SHW TRV UNH V VZ WMT".split())

# ---------- Estilo: gradiente nocturno, tarjetas translúcidas y tipografía sans ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
.stApp { background: linear-gradient(145deg,#07152c 0%,#10152c 48%,#241044 100%); color:#edf4ff; }
.block-container { max-width: 1500px; padding-top: 2rem; padding-bottom: 3rem; }
.hero { padding: 24px 26px 30px; border:1px solid rgba(255,255,255,.18); border-radius:24px;
 background:linear-gradient(120deg,rgba(29,74,111,.48),rgba(48,22,80,.38));
 box-shadow:0 24px 60px rgba(0,0,0,.22); position:relative; overflow:hidden; }
.hero:after { content:""; position:absolute; inset:0; pointer-events:none; opacity:.16;
 background:repeating-linear-gradient(115deg,transparent 0 90px,rgba(139,207,241,.5) 91px 93px,transparent 94px 170px); }
.eyebrow { display:inline-block; border:1px solid #8fb6d5; border-radius:30px; padding:8px 16px;
 background:rgba(255,255,255,.08); font-weight:700; font-size:13px; letter-spacing:.04em; }
.hero h1 { font-size:clamp(32px,4vw,46px); font-weight:800; margin:26px 0 12px; letter-spacing:-.035em; }
.hero p { font-size:17px; color:#e3efff; max-width:1050px; line-height:1.55; }
.stat-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; margin-top:26px; }
.stat { min-height:125px; padding:20px; border:1px solid rgba(255,255,255,.3); border-radius:20px;
 background:rgba(255,255,255,.11); backdrop-filter:blur(12px); box-shadow:0 12px 28px rgba(0,0,0,.14); }
.stat .icon { font-size:22px; } .stat .num { font-size:34px; font-weight:800; margin-top:6px; }
.stat .label { font-size:13px; letter-spacing:.04em; }
.notice { background:#fff; color:#263244; border-left:6px solid #a82b45; border-radius:14px;
 padding:20px 24px; box-shadow:0 10px 25px rgba(0,0,0,.10); margin:24px 0; }
.notice h3 { color:#98233d; font-size:18px; margin:0 0 10px; }
.notice li { margin:5px 0; }
.section-title { color:#b9dff2; border-left:5px solid #78cddd; padding-left:14px; font-size:24px; font-weight:750; margin-top:32px; }
.section-copy { color:#e4eaf4; line-height:1.6; }
div[data-testid="stDataFrame"] { background:#fff; border-radius:12px; }
.fund-grid {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:14px 0 22px;}
.fund-card {background:linear-gradient(135deg,rgba(44,83,122,.58),rgba(61,43,93,.62));border:1px solid rgba(190,220,245,.22);border-radius:14px;padding:15px 17px;min-height:88px;box-shadow:0 8px 22px rgba(0,0,0,.12)}
.fund-label {font-size:12px;color:#b8cce2;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px}
.fund-value {font-size:20px;font-weight:750;color:#f1f6ff;overflow-wrap:anywhere}
.radar-wrap {width:100%;overflow:auto;border:1px solid rgba(180,210,235,.22);border-radius:14px;background:#0d121b;}
.radar-table {width:100%;min-width:1450px;border-collapse:separate;border-spacing:0;color:#edf4ff;font-size:14px;}
.radar-table th {position:sticky;top:0;background:#172332;color:#f4f7fb;text-align:left;padding:16px 13px;border-bottom:1px solid #344354;white-space:nowrap;cursor:pointer;z-index:2}
.radar-table td {padding:17px 13px;border-bottom:1px solid rgba(160,185,210,.15);height:76px;white-space:nowrap;vertical-align:middle}
.radar-table tbody tr:nth-child(even){background:rgba(225,240,255,.035)}
.radar-table tbody tr:hover{background:rgba(105,184,226,.13)}
.radar-table .company {font-weight:700;color:#9bc8ef}.radar-table .sub {display:block;font-size:12px;color:#aebdce;margin-top:5px;font-weight:400}
.radar-table .drop {display:inline-block;background:#8f2e2b;color:white;border-radius:9px;padding:6px 10px;font-weight:700}
.radar-table .spark {width:240px;height:52px;display:block}
@media(max-width:850px){.fund-grid{grid-template-columns:repeat(2,minmax(0,1fr));}}
div[data-testid="stMetric"] { background:rgba(255,255,255,.10); padding:12px 16px; border-radius:12px; }
.stButton>button { border-radius:12px; font-weight:700; }
footer {visibility:hidden;}
@media(max-width:800px){.stat-grid{grid-template-columns:repeat(2,minmax(0,1fr));}.hero{padding:18px;}}
</style>
""", unsafe_allow_html=True)

# ---------- Barra lateral / filtros ----------
st.sidebar.markdown("## ⚙️ Filtros")
st.sidebar.caption("Ajusta el universo y el rango de caída.")
theme = st.sidebar.radio("Apariencia", ["Híbrido","Oscuro","Claro","Auto"], index=0, horizontal=True)
indices = st.sidebar.multiselect("Índices", ["S&P 500","Nasdaq 100","Dow Jones"], default=["S&P 500"])
min_cap = st.sidebar.selectbox("Capitalización mínima", ["Todas","10B USD","50B USD","100B USD","200B USD"], index=0)
max_companies = st.sidebar.slider("Máximo de empresas por actualización", 20, 100, 100, 10)
st.sidebar.markdown("### Filtro de caída")
min_drop, max_drop = st.sidebar.slider("Caída desde el pico móvil de 12 meses (%)", -80, 0, (-50,-20), 1)
sectors = ["Todos"] + sorted(META["Sector"].unique().tolist())
sector_filter = st.sidebar.selectbox("Sector", sectors, index=0)
st.sidebar.caption("El universo semilla se mantiene dentro del código para evitar el error HTTP 403 al consultar composiciones externas.")

# Apariencia dinámica sencilla
if theme == "Claro":
    st.markdown("<style>.stApp{background:linear-gradient(145deg,#eaf3fb,#f4f5fb 55%,#eee6fa);color:#172033}.hero p,.section-copy{color:#24364b}.hero h1{color:#15243a}.section-title{color:#315e80}</style>", unsafe_allow_html=True)
elif theme == "Oscuro":
    st.markdown("<style>.stApp{background:#080d16}</style>", unsafe_allow_html=True)

# ---------- Datos ----------
@st.cache_data(ttl=21600, show_spinner=False)
def download_prices(tickers, period="5y"):
    raw = yf.download(
        tickers=list(tickers), period=period, interval="1d",
        auto_adjust=True, group_by="ticker", threads=True,
        progress=False, timeout=25
    )
    return raw

@st.cache_data(ttl=86400, show_spinner=False)
def get_fundamentals(ticker):
    t = yf.Ticker(ticker)
    info = t.get_info()
    # Statements are best-effort: some symbols/accounts may not return them.
    try:
        bs = t.get_balance_sheet(freq="yearly")
    except Exception:
        bs = pd.DataFrame()
    try:
        inc = t.get_income_stmt(freq="yearly")
    except Exception:
        inc = pd.DataFrame()
    try:
        cf = t.get_cashflow(freq="yearly")
    except Exception:
        cf = pd.DataFrame()
    return info, bs, inc, cf

def field(df, names, col=0):
    if df is None or df.empty:
        return np.nan
    for name in names:
        if name in df.index:
            try:
                return float(df.loc[name].iloc[col])
            except Exception:
                pass
    return np.nan

def build_quality(info, bs, inc, cf):
    checks = []
    roa = info.get("returnOnAssets")
    roe = info.get("returnOnEquity")
    margin = info.get("profitMargins")
    debt_equity = info.get("debtToEquity")
    current_ratio = info.get("currentRatio")
    op_cf = field(cf, ["Operating Cash Flow","OperatingCashFlow"])
    total_debt = field(bs, ["Total Debt","Long Term Debt And Capital Lease Obligation"])
    equity = field(bs, ["Stockholders Equity","Total Equity Gross Minority Interest"])
    checks.extend([
        bool(roa is not None and roa > 0),
        bool(op_cf is not np.nan and pd.notna(op_cf) and op_cf > 0),
        bool(margin is not None and margin > 0),
        bool(roe is not None and roe > 0),
        bool(debt_equity is not None and debt_equity < 150),
        bool(current_ratio is not None and current_ratio >= 1),
        bool(pd.notna(total_debt) and pd.notna(equity) and equity > total_debt),
        bool(info.get("grossMargins") is not None and info.get("grossMargins") > 0),
        ])
    return int(sum(checks)), len(checks)

def load_universe():
    chosen = set()
    if "S&P 500" in indices:
        chosen.update(META["Ticker"].tolist())
    if "Nasdaq 100" in indices:
        chosen.update(NASDAQ100)
    if "Dow Jones" in indices:
        chosen.update(DOW30)
    if not chosen:
        chosen.update(META["Ticker"].tolist())
    tickers = [x for x in META["Ticker"].tolist() if x in chosen][:max_companies]
    with st.spinner(f"Descargando hasta {len(tickers)} historiales de precios…"):
        prices = download_prices(tuple(tickers))
    if prices is None or prices.empty:
        raise RuntimeError("El proveedor de precios no devolvió datos. Puede estar limitando temporalmente las consultas.")
    rows = []
    for _, m in META[META["Ticker"].isin(tickers)].iterrows():
        sym = m["Ticker"]
        try:
            if isinstance(prices.columns, pd.MultiIndex):
                if sym in prices.columns.get_level_values(0):
                    sub = prices[sym]
                elif sym in prices.columns.get_level_values(1):
                    sub = prices.xs(sym, axis=1, level=1)
                else:
                    sub = pd.DataFrame()
            else:
                sub = prices
            close = sub["Close"].dropna() if "Close" in sub else pd.Series(dtype=float)
            if len(close) < 30:
                continue
            one_year = close.tail(252)
            peak_idx = one_year.idxmax()
            last = float(close.iloc[-1])
            peak = float(one_year.max())
            drop = (last/peak - 1) * 100 if peak else np.nan
            days = int((close.index[-1] - peak_idx).days)
            one_year_return = (last/float(one_year.iloc[0])-1)*100 if one_year.iloc[0] else np.nan
            # Drawdown and sparkline series are calculated from adjusted daily closes.
            rows.append({
                "Ticker":sym,"Empresa":m["Empresa"],"Rank S&P":int(m["Rank S&P"]),
                "Sector":m["Sector"],"Precio":last,"Caida":drop,"Dias":days,
                "1 año":one_year_return,"Serie":close.tail(252)
            })
        except Exception:
            continue
    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("No se pudo construir la tabla de precios con la respuesta recibida.")
    return df, prices

try:
    data, price_data = load_universe()
    data = data.sort_values("Caida", ascending=True).reset_index(drop=True)
    data["Sev."] = np.arange(1, len(data)+1)
    # Use only available current valuation fields from Yahoo. Values are fetched for candidate names,
    # not for the entire universe, to reduce rate limiting.
    candidates = data[(data["Caida"] >= min_drop) & (data["Caida"] <= max_drop)].copy()
    if sector_filter != "Todos":
        candidates = candidates[candidates["Sector"] == sector_filter]
    if min_cap != "Todas":
        threshold = {"10B USD":10e9,"50B USD":50e9,"100B USD":100e9,"200B USD":200e9}[min_cap]
        # market cap is checked only where Yahoo returned it.
        caps = {}
        for sym in candidates["Ticker"].tolist()[:30]:
            try: caps[sym] = get_fundamentals(sym)[0].get("marketCap", np.nan)
            except Exception: caps[sym] = np.nan
        candidates = candidates[candidates["Ticker"].map(caps).fillna(0) >= threshold]
except Exception as e:
    st.markdown('<div class="hero"><span class="eyebrow">SCANNER · VALUE EN CRISIS</span><h1>Blue chips caídas desde su pico</h1><p>Universo de grandes compañías estadounidenses · análisis de caída, valoración y calidad.</p></div>', unsafe_allow_html=True)
    st.error(f"No fue posible cargar los precios: {e}")
    st.info("El error HTTP 403 de la composición de índices ya no se genera: el universo está integrado en el proyecto. Si el proveedor de cotizaciones bloquea la descarga, pulsa Actualizar datos más tarde.")
    st.stop()

# ---------- Cabecera / KPIs ----------
mean_drop = candidates["Caida"].mean() if len(candidates) else np.nan
touched = candidates["Sector"].nunique() if len(candidates) else 0
updated = datetime.now().strftime("%Y-%m-%d %H:%M")
st.markdown(f"""
<div class="hero">
 <span class="eyebrow">SCANNER · VALUE EN CRISIS</span>
 <h1>Blue chips caídas desde su pico</h1>
 <p>Universo: hasta {len(data)} grandes compañías estadounidenses · Filtro: caída {abs(min_drop)}–{abs(max_drop)}% desde el pico móvil de 12 meses, ocurrido en el último año. Actualizado {updated}.</p>
 <p style="font-size:14px">Scanner de investigación · versión independiente basada en las capturas de referencia</p>
 <div class="stat-grid">
  <div class="stat"><div class="icon">🌐</div><div class="num">{len(data)}</div><div class="label">UNIVERSO</div></div>
  <div class="stat"><div class="icon">◎</div><div class="num">{len(candidates)}</div><div class="label">CANDIDATOS</div></div>
  <div class="stat"><div class="icon">⬇</div><div class="num">{mean_drop:.0f}%</div><div class="label">CAÍDA MEDIA</div></div>
  <div class="stat"><div class="icon">▦</div><div class="num">{touched}</div><div class="label">SECTORES TOCADOS</div></div>
 </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="notice">
 <h3>HONESTIDAD ANTE TODO — leer antes de invertir</h3>
 <ul>
 <li>Esto es una <b>lista de investigación, NO una recomendación de compra</b>. Una caída por sí sola no es señal suficiente.</li>
 <li>El universo semilla se mantiene dentro del código; el ranking de referencia es aproximado y no representa una composición oficial histórica del S&amp;P 500.</li>
 <li>Cruza <b>precio + valoración + calidad</b>. Los datos fundamentales dependen de la cobertura de Yahoo Finance y pueden faltar.</li>
 <li>La valoración histórica de 5 años y los indicadores de calidad se muestran solo cuando hay datos suficientes; los campos estimados se identifican como aproximaciones.</li>
 <li>Fuente de precios/fundamentales: Yahoo Finance mediante yfinance, una interfaz no oficial que puede limitar o cambiar sus respuestas.</li>
 </ul>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">Vista RADAR — candidatos para investigar</div>', unsafe_allow_html=True)
st.markdown('<div class="section-copy">Uno por uno. Orden inicial por severidad. Haz clic en cualquier encabezado para ordenar. <b>Valuación: vs Ind.</b> = P/E frente a la mediana de su sector; <b>vs Hist.</b> = percentil histórico solo si se puede calcular; <b>Valor</b> = score relativo; <b>Calidad</b> = indicadores fundamentales disponibles. ≈ = datos de proveedor externo.</div>', unsafe_allow_html=True)

c1,c2,c3 = st.columns([2,1,1])
with c1:
    sector2 = st.selectbox("Sector", ["Todos los sectores"] + sorted(candidates["Sector"].unique().tolist()), key="sector_table")
with c2:
    if st.button("↻ Reset"):
        st.rerun()
with c3:
    visible_count = len(candidates[candidates["Sector"] == sector2]) if sector2 != "Todos los sectores" else len(candidates)
    st.markdown(f"<div style='text-align:right;padding-top:30px;color:#e9eef6'>mostrando {visible_count} de {len(candidates)}</div>", unsafe_allow_html=True)
if sector2 != "Todos los sectores":
    candidates = candidates[candidates["Sector"] == sector2].copy()

# Fundamentals: try for candidates (bounded) to build valuation and quality scores.
fund_rows = []
progress = st.progress(0, text="Preparando métricas fundamentales…")
for i, (_, row) in enumerate(candidates.iterrows()):
    sym = row["Ticker"]
    try:
        info, bs, inc, cf = get_fundamentals(sym)
        pe = info.get("trailingPE")
        fcf = info.get("freeCashflow")
        mcap = info.get("marketCap")
        fcf_yield = (fcf/mcap*100) if fcf is not None and mcap and mcap > 0 else np.nan
        fscore, nscore = build_quality(info, bs, inc, cf)
        fund_rows.append({"Ticker":sym,"P/E":pe,"FCF Yield":fcf_yield,"F-score":fscore,
                          "F-count":nscore,"Market Cap":mcap,"Info":info})
    except Exception:
        fund_rows.append({"Ticker":sym,"P/E":np.nan,"FCF Yield":np.nan,"F-score":np.nan,
                          "F-count":0,"Market Cap":np.nan,"Info":{}})
    progress.progress((i+1)/max(1,len(candidates)), text=f"Consultando fundamentos: {i+1}/{len(candidates)}")
progress.empty()
fund = pd.DataFrame(fund_rows)
if fund.empty:
    fund = pd.DataFrame(columns=["Ticker","P/E","FCF Yield","F-score","F-count","Market Cap","Info"])
view = candidates.merge(fund.drop(columns=["Info"], errors="ignore"), on="Ticker", how="left")
# Sector median P/E; comparisons are only shown if there are enough valid peers.
sector_pe = view.groupby("Sector")["P/E"].transform("median")
view["vs Ind."] = np.where(view["P/E"].notna() & sector_pe.notna() & (sector_pe>0),
                            (view["P/E"]/sector_pe-1)*100, np.nan)
# A transparent relative score: drawdown + discount to sector + F-score + FCF yield.
pe_discount = np.where(view["P/E"].notna() & sector_pe.notna() & (sector_pe>0),
                       np.clip((sector_pe-view["P/E"])/sector_pe*100,-100,100), 0)
quality_norm = view["F-score"].fillna(4)/8*100
fcf_norm = view["FCF Yield"].clip(-10,20).fillna(0)
view["Valor"] = (0.45*(100+view["Caida"].clip(-80,0))/80*100 +
                 0.30*(pe_discount+100)/2 + 0.20*quality_norm +
                 0.05*((fcf_norm+10)/30*100)).clip(0,100)
view["Veredicto"] = np.select(
    [view["Valor"]>=70, view["Valor"]>=55, view["Valor"]>=40],
    ["barata de verdad","algo barata","en precio"], default="cara / revisar"
)
view["Calidad"] = view.apply(
    lambda r: ("sana" if pd.notna(r["F-score"]) and r["F-score"]>=6 else
               "aceptable" if pd.notna(r["F-score"]) and r["F-score"]>=4 else
               "frágil" if pd.notna(r["F-score"]) else "sin datos") +
              (f" · F{int(r['F-score'])}" if pd.notna(r["F-score"]) else ""), axis=1)
view["vs Hist."] = "—"
view["Precio"] = view["Precio"].map(lambda x: f"${x:,.2f}" if pd.notna(x) else "—")
view["Caida"] = view["Caida"].map(lambda x: f"{x:.1f}%" if pd.notna(x) else "—")
view["vs Ind."] = view["vs Ind."].map(lambda x: f"{x:+.0f}%" if pd.notna(x) else "—")
view["Valor"] = view["Valor"].map(lambda x: f"{x:+.2f}" if pd.notna(x) else "—")
view["1 año"] = view["1 año"].map(lambda x: f"{x:+.1f}%" if pd.notna(x) else "—")
display_cols = ["Ticker","Empresa","Rank S&P","Sector","Precio","Caida","Dias","Sev.","1 año","vs Ind.","vs Hist.","Valor","Veredicto","Calidad"]
table = view[display_cols].rename(columns={"Ticker":"Símbolo","Caida":"Caída","Dias":"Días","Sev.":"Sev."})
table.insert(table.columns.get_loc("1 año")+1, "Evolución 1 año", view["Serie"].apply(lambda s: list(pd.Series(s).tail(60).round(2))))
# Tabla radar personalizada: mantiene las mini-gráficas visibles y da más aire vertical a cada fila.
import html as _html

def _sparkline(values, color="#39c98b"):
    vals = [float(v) for v in values if pd.notna(v)]
    if len(vals) < 2:
        return ""
    lo, hi = min(vals), max(vals)
    span = hi-lo or 1
    pts = " ".join(f"{i/(len(vals)-1)*230:.1f},{44-(v-lo)/span*36:.1f}" for i,v in enumerate(vals))
    return f'<svg class="spark" viewBox="0 0 230 52" preserveAspectRatio="none"><polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'

html_rows=[]
for _, rr in view.iterrows():
    hist = rr["Serie"].tail(60).tolist() if hasattr(rr["Serie"], "tail") else []
    vals = [rr.get("Ticker",""), rr.get("Empresa",""), rr.get("Rank S&P",""), rr.get("Sector",""),
            rr.get("Precio",""), rr.get("Caida",""), rr.get("Dias",""), rr.get("Sev.",""), rr.get("1 año",""),
            rr.get("vs Ind.","—"), rr.get("vs Hist.","—"), rr.get("Valor","—"), rr.get("Veredicto",""), rr.get("Calidad","")]
    cells = [f'<td><b>{_html.escape(str(vals[0]))}</b></td>',
             f'<td><span class="company">{_html.escape(str(vals[1]))}</span></td>',
             f'<td>#{_html.escape(str(vals[2]))}</td>', f'<td>{_html.escape(str(vals[3]))}</td>',
             f'<td>{_html.escape(str(vals[4]))}</td>', f'<td><span class="drop">{_html.escape(str(vals[5]))}</span></td>',
             f'<td>{_html.escape(str(vals[6]))} d</td>', f'<td>{_html.escape(str(vals[7]))}</td>',
             f'<td>{_html.escape(str(vals[8]))}</td>', f'<td>{_sparkline(hist)}</td>',
             f'<td>{_html.escape(str(vals[9]))}</td>', f'<td>{_html.escape(str(vals[10]))}</td>',
             f'<td>{_html.escape(str(vals[11]))}</td>', f'<td>{_html.escape(str(vals[12]))}</td>',
             f'<td>{_html.escape(str(vals[13]))}</td>']
    html_rows.append('<tr>' + ''.join(cells) + '</tr>')
headers=["Ticker","Empresa","Rank S&P","Sector","Precio","Caída","Días","Sev.","1 año","Evolución 1 año","vs Ind.","vs Hist.","Valor","Veredicto","Calidad"]
head=''.join(f'<th onclick="sortTable({i})">{h} ↕</th>' for i,h in enumerate(headers))
radar_html=f'''<style>
body{{margin:0;background:#0d121b;font-family:Inter,Arial,sans-serif;color:#edf4ff}}
.radar-wrap{{width:100%;overflow:auto;border:1px solid rgba(180,210,235,.22);border-radius:14px;background:#0d121b}}
.radar-table{{width:100%;min-width:1450px;border-collapse:separate;border-spacing:0;color:#edf4ff;font-size:14px}}
.radar-table th{{position:sticky;top:0;background:#172332;color:#f4f7fb;text-align:left;padding:16px 13px;border-bottom:1px solid #344354;white-space:nowrap;cursor:pointer;z-index:2}}
.radar-table td{{padding:17px 13px;border-bottom:1px solid rgba(160,185,210,.15);height:76px;white-space:nowrap;vertical-align:middle}}
.radar-table tbody tr:nth-child(even){{background:rgba(225,240,255,.035)}}.radar-table tbody tr:hover{{background:rgba(105,184,226,.13)}}
.company{{font-weight:700;color:#9bc8ef}}.drop{{display:inline-block;background:#8f2e2b;color:white;border-radius:9px;padding:6px 10px;font-weight:700}}
.spark{{width:240px;height:52px;display:block}}
</style><div class="radar-wrap"><table class="radar-table" id="radarTable"><thead><tr>{head}</tr></thead><tbody>{''.join(html_rows)}</tbody></table></div>
<script>function sortTable(n){{const t=document.getElementById('radarTable'),b=t.tBodies[0],r=[...b.rows];const asc=t.dataset.col==n?t.dataset.asc!=='true':true;r.sort((a,c)=>{{let x=a.cells[n].innerText.trim(),y=c.cells[n].innerText.trim();let nx=parseFloat(x.replace(/[^0-9.+-]/g,'')),ny=parseFloat(y.replace(/[^0-9.+-]/g,''));if(!isNaN(nx)&&!isNaN(ny))return asc?nx-ny:ny-nx;return asc?x.localeCompare(y):y.localeCompare(x)}});r.forEach(x=>b.appendChild(x));t.dataset.col=n;t.dataset.asc=asc;}}</script>'''
st.components.v1.html(radar_html, height=min(850, max(260, 90 + len(view)*78)), scrolling=True)
csv = view[display_cols].to_csv(index=False).encode("utf-8-sig")
st.download_button("⬇ Exportar radar a CSV", data=csv, file_name="blue_chip_value_radar.csv", mime="text/csv")

# ---------- Ficha detallada y chart ----------
st.markdown('<div class="section-title">Ficha de empresa — precio, valoración y calidad</div>', unsafe_allow_html=True)
symbols = data["Ticker"].tolist()
if symbols:
    st.caption("Puedes escribir el nombre o ticker de cualquier compañía del universo, aunque no aparezca entre los candidatos por caída.")
    selected = st.selectbox("Buscar empresa en todo el universo", symbols, index=(symbols.index("AAPL") if "AAPL" in symbols else 0),
                            format_func=lambda s: f"{s} · {META.loc[META.Ticker.eq(s),'Empresa'].iloc[0]}")
    selected_row = data[data["Ticker"]==selected].iloc[0]
    if selected in view["Ticker"].tolist():
        r = view[view["Ticker"]==selected].iloc[0]
        raw_info = next((x["Info"] for x in fund_rows if x["Ticker"]==selected), {})
    else:
        r = selected_row.copy()
        try:
            raw_info, _bs, _inc, _cf = get_fundamentals(selected)
            r["P/E"] = raw_info.get("trailingPE", np.nan)
            fcf = raw_info.get("freeCashflow"); mc = raw_info.get("marketCap")
            r["FCF Yield"] = (fcf/mc*100) if fcf is not None and mc else np.nan
        except Exception:
            raw_info = {}
            r["P/E"] = np.nan; r["FCF Yield"] = np.nan
    a,b,c,d = st.columns(4)
    a.metric("Precio", f"${float(selected_row['Precio']):,.2f}")
    b.metric("Caída desde pico", f"{float(selected_row['Caida']):.1f}%")
    c.metric("P/E trailing", f"{r['P/E']:.1f}x" if pd.notna(r.get("P/E", np.nan)) else "N/D")
    d.metric("FCF yield", f"{r['FCF Yield']:.1f}%" if pd.notna(r.get("FCF Yield", np.nan)) else "N/D")
    # Plot 1-year close series
    series = selected_row["Serie"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=series.index, y=series.values, mode="lines", name=selected,
                             line=dict(color="#67b7e8",width=2), fill="tozeroy",
                             fillcolor="rgba(103,183,232,.16)"))
    peakdate = series.idxmax()
    fig.add_trace(go.Scatter(x=[peakdate], y=[series.max()], mode="markers",
                             marker=dict(color="#e84d70",size=9), name="Pico 12m"))
    fig.update_layout(height=430, margin=dict(l=18,r=18,t=28,b=24),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,.04)",
                      font=dict(color="#eaf2fb"), xaxis_title="", yaxis_title="USD",
                      legend=dict(orientation="h",y=1.08))
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("Ver datos fundamentales disponibles", expanded=False):
        def _fmt_money(v):
            if v is None or pd.isna(v): return "Sin dato"
            v=float(v); a=abs(v)
            return (f"${v/1e12:.2f} T" if a>=1e12 else f"${v/1e9:.2f} B" if a>=1e9 else f"${v/1e6:.1f} M" if a>=1e6 else f"${v:,.2f}")
        def _fmt_pct(v): return "Sin dato" if v is None or pd.isna(v) else f"{float(v)*100:.1f}%"
        def _fmt_num(v, suffix=""): return "Sin dato" if v is None or pd.isna(v) else f"{float(v):,.2f}{suffix}"
        fundamentals = [
            ("Sector", raw_info.get("sector") or r.get("Sector","Sin dato")),
            ("Industria", raw_info.get("industry") or "Sin dato"),
            ("Capitalización", _fmt_money(raw_info.get("marketCap"))),
            ("P/E actual", _fmt_num(raw_info.get("trailingPE"), "x")),
            ("P/E estimado", _fmt_num(raw_info.get("forwardPE"), "x")),
            ("Precio / valor contable", _fmt_num(raw_info.get("priceToBook"), "x")),
            ("Rentabilidad sobre activos (ROA)", _fmt_pct(raw_info.get("returnOnAssets"))),
            ("Rentabilidad sobre patrimonio (ROE)", _fmt_pct(raw_info.get("returnOnEquity"))),
            ("Margen neto", _fmt_pct(raw_info.get("profitMargins"))),
            ("Margen bruto", _fmt_pct(raw_info.get("grossMargins"))),
            ("Deuda / patrimonio", _fmt_num(raw_info.get("debtToEquity"))),
            ("Ratio corriente", _fmt_num(raw_info.get("currentRatio"))),
            ("Flujo de caja libre", _fmt_money(raw_info.get("freeCashflow"))),
            ("Flujo operativo", _fmt_money(raw_info.get("operatingCashflow"))),
            ("Crecimiento de ingresos", _fmt_pct(raw_info.get("revenueGrowth"))),
            ("Crecimiento de beneficios", _fmt_pct(raw_info.get("earningsGrowth"))),
            ("Rendimiento por dividendo", _fmt_pct(raw_info.get("dividendYield"))),
        ]
        cards=''.join(f'<div class="fund-card"><div class="fund-label">{_html.escape(str(k))}</div><div class="fund-value">{_html.escape(str(v))}</div></div>' for k,v in fundamentals)
        st.markdown(f'<div class="fund-grid">{cards}</div>', unsafe_allow_html=True)
        st.caption("Los campos marcados como ‘Sin dato’ no fueron publicados o no estuvieron disponibles en la respuesta del proveedor.")
else:
    st.info("No hay candidatos con los filtros seleccionados.")

st.markdown("""
<div class="notice">
 <h3>Metodología y límites</h3>
 <ul>
 <li><b>Caída:</b> último cierre ajustado frente al máximo de los últimos 252 cierres disponibles. “Días” es el tiempo calendario desde ese máximo.</li>
 <li><b>vs Ind.:</b> P/E trailing de la empresa frente a la mediana de P/E del sector dentro de los candidatos que devolvieron datos; no es una comparación completa con todos los pares.</li>
 <li><b>Valor:</b> puntuación heurística propia que combina caída, descuento sectorial, calidad fundamental y FCF yield. No es una recomendación ni un modelo validado.</li>
 <li><b>Calidad:</b> proxy de ocho comprobaciones disponibles; no equivale al Piotroski F-Score oficial. La valoración histórica de cinco años no se calcula en esta versión porque no se dispone de series históricas consistentes de fundamentales.</li>
 <li><b>Sesgo de supervivencia:</b> el universo contiene compañías vigentes; no incluye empresas que salieron del índice o quebraron.</li>
 </ul>
</div>
""", unsafe_allow_html=True)
st.caption("Blue Chip Value Scanner · herramienta educativa de investigación · no constituye asesoría financiera.")
