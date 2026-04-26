import os
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from sqlalchemy import create_engine


def _get_engine():
    url = os.environ.get("DATABASE_URL")
    if url:
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return create_engine(url), True
    return None, False

st.set_page_config(
    page_title="Financial Sentiment Monitor",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design tokens (Light theme) ────────────────────────────────────────────────
ACCENT    = "#2563EB"
ACCENT_LT = "#EFF6FF"
GREEN     = "#059669"
GREEN_LT  = "#ECFDF5"
RED       = "#DC2626"
RED_LT    = "#FEF2F2"
AMBER     = "#D97706"
AMBER_LT  = "#FEF3C7"
BG        = "#FAFBFC"
BG_CARD   = "#FFFFFF"
BORDER    = "#E5E7EB"
BORDER_LT = "#F1F5F9"
TEXT_1    = "#0F172A"
TEXT_2    = "#334155"
TEXT_3    = "#64748B"
TEXT_4    = "#94A3B8"

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@600&display=swap');

  :root {{
    --font-ui: 'Inter';
    --font-mono: 'JetBrains Mono';
    --fs-body: 14px;
    --fs-display: 24px;
  }}

  html, body, .stApp, [class*="css"], button, input, textarea, select {{
    font-family: var(--font-ui) !important;
    font-size: var(--fs-body) !important;
  }}

  .stApp {{ background-color: {BG} !important; color: {TEXT_1} !important; }}
  #MainMenu, footer {{
    visibility: hidden !important;
  }}
  header[data-testid="stHeader"],
  div[data-testid="stToolbar"],
  div[data-testid="stDecoration"],
  .stAppHeader {{
    display: none !important;
  }}

  .block-container {{
    padding: 1.75rem 3rem 3rem 3rem !important;
    max-width: 1180px;
  }}

  /* ── Sidebar ── */
  section[data-testid="stSidebar"] {{
    background-color: {BG_CARD} !important;
    border-right: 1px solid {BORDER};
  }}
  section[data-testid="stSidebar"] > div {{ padding: 1.5rem 1.25rem; }}

  /* Hide Streamlit sidebar checkboxes (we'll use custom pills) */
  section[data-testid="stSidebar"] .stButton > button {{
    background: {BG} !important;
    border: 1px solid {BORDER} !important;
    color: {TEXT_2} !important;
    font-size: var(--fs-body) !important;
    font-weight: 500 !important;
    padding: 0.4rem 0 !important;
    border-radius: 6px !important;
    width: 100%;
    transition: all 0.15s;
  }}
  section[data-testid="stSidebar"] .stButton > button:hover {{
    border-color: {ACCENT} !important;
    color: {ACCENT} !important;
  }}

  /* Selectbox */
  section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
    background: {BG} !important;
    border: 1px solid {BORDER} !important;
    color: {TEXT_2} !important;
    font-size: var(--fs-body) !important;
  }}

  /* ── Typography ── */
  h1, h2, h3, h4, p {{ color: {TEXT_1}; }}

  .eyebrow {{
    font-family: var(--font-mono);
    font-size: var(--fs-body);
    font-weight: 600;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    color: {ACCENT};
    margin-bottom: 0.75rem;
  }}

  .hero-title {{
    font-size: var(--fs-display);
    font-weight: 700;
    color: {TEXT_1};
    letter-spacing: 0;
    line-height: 1.1;
    margin: 0 0 1rem 0;
  }}
  .hero-lede {{
    font-size: var(--fs-body);
    color: {TEXT_2};
    line-height: 1.65;
    max-width: 720px;
    margin: 0;
    font-weight: 400;
  }}

  .sec-title {{
    font-size: var(--fs-display);
    font-weight: 600;
    color: {TEXT_1};
    letter-spacing: 0;
    margin: 0 0 0.4rem 0;
  }}
  .sec-sub {{
    font-size: var(--fs-body);
    color: {TEXT_3};
    line-height: 1.55;
    margin: 0 0 1rem 0;
    max-width: 720px;
  }}

  .sec-wrap {{ margin-top: 2rem; }}

  /* ── Pipeline ── */
  .pipeline {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 0.75rem;
    margin-top: 0.5rem;
  }}
  .pipe-step {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 1.1rem;
  }}
  .pipe-num {{
    font-family: var(--font-mono);
    font-size: var(--fs-body);
    font-weight: 600;
    color: {ACCENT};
    margin-bottom: 0.5rem;
  }}
  .pipe-name {{
    font-size: var(--fs-body);
    font-weight: 600;
    color: {TEXT_1};
    margin-bottom: 0.3rem;
  }}
  .pipe-desc {{
    font-size: var(--fs-body);
    color: {TEXT_3};
    line-height: 1.5;
  }}

  /* ── KPI ── */
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
  }}
  .kpi {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 1.1rem;
    min-height: 128px;
  }}
  .kpi-label {{
    font-size: var(--fs-body);
    font-weight: 500;
    color: {TEXT_3};
    margin-bottom: 0.75rem;
  }}
  .kpi-value {{
    font-size: var(--fs-display);
    font-weight: 700;
    color: {TEXT_1};
    letter-spacing: 0;
    line-height: 1;
    margin-bottom: 0.6rem;
  }}
  .kpi-why {{
    font-size: var(--fs-body);
    color: {TEXT_3};
    line-height: 1.5;
  }}
  .pill {{
    display: inline-block;
    font-size: var(--fs-body);
    font-weight: 500;
    padding: 0.2rem 0.55rem;
    border-radius: 4px;
    margin-right: 0.4rem;
  }}

  /* ── Chart + insight block ── */
  .insight-card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 1.1rem;
    height: 100%;
  }}
  .insight-card, .insight-card div, .insight-card span {{
    color: {TEXT_2};
  }}
  .insight-label {{
    font-family: var(--font-mono);
    font-size: var(--fs-body);
    font-weight: 600;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    color: {TEXT_4};
    margin-bottom: 0.75rem;
  }}
  .insight-head {{
    font-size: var(--fs-body);
    font-weight: 600;
    color: {TEXT_1};
    margin-bottom: 0.8rem;
    line-height: 1.35;
  }}
  .insight-body {{
    font-size: var(--fs-body);
    color: {TEXT_2};
    line-height: 1.6;
  }}
  .insight-body strong {{ color: {TEXT_1}; font-weight: 600; }}
  .insight-stat {{
    font-family: var(--font-mono);
    font-size: var(--fs-body);
    color: {ACCENT};
    background: {ACCENT_LT};
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
  }}

  /* ── Dataframe ── */
  div[data-testid="stDataFrame"] {{
    border: 1px solid {BORDER};
    border-radius: 8px;
    overflow: hidden;
  }}
  div[data-testid="stDataFrame"] * {{
    font-family: var(--font-ui) !important;
    font-size: var(--fs-body) !important;
  }}

  .drift-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    align-items: stretch;
  }}

  @media (max-width: 900px) {{
    .block-container {{ padding: 1rem !important; }}
    .pipeline, .kpi-grid, .drift-grid {{ grid-template-columns: repeat(2, 1fr); }}
  }}

  /* ── Download ── */
  .stDownloadButton {{
    margin-top: 1rem;
  }}
  .stDownloadButton button {{
    background: {BG_CARD} !important;
    border: 1px solid {BORDER} !important;
    color: {TEXT_2} !important;
    font-size: var(--fs-body) !important;
    font-weight: 500 !important;
    padding: 0.55rem 1.25rem !important;
    border-radius: 8px !important;
  }}
  .stDownloadButton button:hover {{
    border-color: {ACCENT} !important;
    color: {ACCENT} !important;
  }}

</style>
""", unsafe_allow_html=True)

# ── Data ───────────────────────────────────────────────────────────────────────
APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent

SENTIMENT_COLUMNS = [
    "vader_compound",
    "vader_positive",
    "vader_neutral",
    "vader_negative",
    "textblob_polarity",
    "textblob_subjectivity",
    "finbert_compound",
    "finbert_positive",
    "finbert_negative",
]

DISPLAY_COLUMNS = [
    "date",
    "stock_symbol",
    "title",
    "text",
    *SENTIMENT_COLUMNS,
    "is_reference",
]


def first_existing_path(candidates):
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


DB_PATH = first_existing_path([
    APP_DIR / "data" / "pipeline.db",
    PROJECT_DIR / "data" / "pipeline.db",
    PROJECT_DIR / "pipeline" / "data" / "pipeline.db",
    Path("data/pipeline.db"),
])

REPORT_PATH = first_existing_path([
    APP_DIR / "reports" / "drift_report.html",
    PROJECT_DIR / "reports" / "drift_report.html",
    Path("reports/drift_report.html"),
])


def empty_live_frame():
    return pd.DataFrame(columns=DISPLAY_COLUMNS)


@st.cache_data(ttl=300)
def load_live(db_path):
    engine, using_postgres = _get_engine()

    try:
        if using_postgres:
            df = pd.read_sql("SELECT * FROM articles WHERE is_reference = 0", engine)
        else:
            import sqlite3
            path = Path(db_path)
            if not path.exists():
                return empty_live_frame()
            with sqlite3.connect(path) as conn:
                has_articles = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'articles'"
                ).fetchone()
                if not has_articles:
                    return empty_live_frame()
                df = pd.read_sql("SELECT * FROM articles WHERE is_reference = 0", conn)
    except Exception as exc:
        st.error(f"Could not read the pipeline database: {exc}")
        return empty_live_frame()

    for column in DISPLAY_COLUMNS:
        if column not in df.columns:
            df[column] = pd.NA

    for column in SENTIMENT_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["date"] = df["date"].fillna("")
    df["stock_symbol"] = df["stock_symbol"].fillna("")
    df["title"] = df["title"].fillna("")

    return df

df_all = load_live(str(DB_PATH))

# ── Sidebar ────────────────────────────────────────────────────────────────────
if "selected_stocks" not in st.session_state:
    st.session_state.selected_stocks = None

with st.sidebar:
    st.markdown(
        f"<p style='font-family:var(--font-mono);font-size:var(--fs-body);font-weight:600;"
        f"letter-spacing:0.02em;text-transform:uppercase;color:{TEXT_4};margin-bottom:0.4rem'>Filters</p>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<p style='font-size:var(--fs-body);font-weight:600;color:{TEXT_1};margin:0 0 1.75rem 0'>"
        f"Narrow your view</p>",
        unsafe_allow_html=True
    )

    if df_all.empty:
        st.warning("No live data yet. Start the pipeline, then refresh this dashboard.")
        st.stop()

    all_stocks = sorted(df_all["stock_symbol"].unique().tolist())

    if st.session_state.selected_stocks is None:
        st.session_state.selected_stocks = set(all_stocks)

    st.markdown(
        f"<p style='font-size:var(--fs-body);font-weight:500;color:{TEXT_3};margin:0 0 0.5rem 0'>Stocks</p>",
        unsafe_allow_html=True
    )

    # Custom pill-style stock selection
    cols = st.columns(2)
    for i, stock in enumerate(all_stocks):
        with cols[i % 2]:
            is_active = stock in st.session_state.selected_stocks
            label = f"● {stock}" if is_active else f"○ {stock}"
            if st.button(label, key=f"btn_{stock}", use_container_width=True):
                if is_active:
                    st.session_state.selected_stocks.discard(stock)
                else:
                    st.session_state.selected_stocks.add(stock)
                st.rerun()

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("All", key="all_stocks", use_container_width=True):
            st.session_state.selected_stocks = set(all_stocks)
            st.rerun()
    with col_b:
        if st.button("Clear", key="clear_stocks", use_container_width=True):
            st.session_state.selected_stocks = set()
            st.rerun()

    st.markdown(
        f"<p style='font-size:var(--fs-body);font-weight:500;color:{TEXT_3};margin:1rem 0 0.4rem 0'>Date</p>",
        unsafe_allow_html=True
    )
    all_dates = sorted(df_all["date"].unique().tolist(), reverse=True)
    selected_date = st.selectbox("", ["All dates"] + all_dates, label_visibility="collapsed")

    if st.button("Refresh data", key="refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ── Filter ─────────────────────────────────────────────────────────────────────
selected_stocks = list(st.session_state.selected_stocks)
df = df_all[df_all["stock_symbol"].isin(selected_stocks)]
if selected_date != "All dates":
    df = df[df["date"] == selected_date]

if df.empty:
    st.warning("No articles match the current filters.")
    st.stop()

# ── HERO ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="eyebrow">Live ML Observability</div>
<h1 class="hero-title">Financial Sentiment Monitor</h1>
<p class="hero-lede">
  A self-monitoring pipeline that continuously scores live financial news sentiment and flags when
  the data starts behaving differently from the 48,000 historical articles it was calibrated on.
</p>
""", unsafe_allow_html=True)

# ── PIPELINE ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="sec-wrap">
  <h2 class="sec-title">How it works</h2>
  <p class="sec-sub">Five stages, each an isolated Python module, orchestrated by Docker Compose. Runs automatically every hour.</p>
  <div class="pipeline">
    <div class="pipe-step">
      <div class="pipe-num">01</div>
      <div class="pipe-name">Ingest</div>
      <div class="pipe-desc">Yahoo Finance RSS · 10 tickers</div>
    </div>
    <div class="pipe-step">
      <div class="pipe-num">02</div>
      <div class="pipe-name">Score</div>
      <div class="pipe-desc">VADER + TextBlob + FinBERT · 10 features</div>
    </div>
    <div class="pipe-step">
      <div class="pipe-num">03</div>
      <div class="pipe-name">Store</div>
      <div class="pipe-desc">SQLite · historical + live</div>
    </div>
    <div class="pipe-step">
      <div class="pipe-num">04</div>
      <div class="pipe-name">Monitor</div>
      <div class="pipe-desc">Evidently AI · drift detection</div>
    </div>
    <div class="pipe-step">
      <div class="pipe-num">05</div>
      <div class="pipe-name">Visualize</div>
      <div class="pipe-desc">Streamlit · this dashboard</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI ────────────────────────────────────────────────────────────────────────
avg_vader    = df["vader_compound"].mean()
report_path  = REPORT_PATH
tone_color   = GREEN if avg_vader > 0.05 else RED if avg_vader < -0.05 else AMBER
tone_bg      = GREEN_LT if avg_vader > 0.05 else RED_LT if avg_vader < -0.05 else AMBER_LT
tone_label   = "Positive" if avg_vader > 0.05 else "Negative" if avg_vader < -0.05 else "Neutral"
drift_label  = "Available" if report_path.exists() else "Pending"

st.markdown(f"""
<div class="sec-wrap">
  <h2 class="sec-title">Pipeline state</h2>
  <p class="sec-sub">Four headline indicators summarising what the system is seeing right now.</p>
  <div class="kpi-grid">
    <div class="kpi">
      <div class="kpi-label">Articles scored</div>
      <div class="kpi-value">{len(df):,}</div>
      <div class="kpi-why">Headlines processed in the selected window.</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Stocks tracked</div>
      <div class="kpi-value">{df["stock_symbol"].nunique()}</div>
      <div class="kpi-why">Tickers with active coverage · up to 10.</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Avg VADER score</div>
      <div class="kpi-value">{avg_vader:+.3f}</div>
      <div class="kpi-why"><span class="pill" style="color:{tone_color};background:{tone_bg}">{tone_label}</span>Range −1 to +1.</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Drift status</div>
      <div class="kpi-value" style="padding-top:0.5rem">{drift_label}</div>
      <div class="kpi-why">Is today's news statistically different from 2019–2024?</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── CHART 1 : VADER box ────────────────────────────────────────────────────────
CHART = dict(
    plot_bgcolor  = "rgba(0,0,0,0)",
    paper_bgcolor = "rgba(0,0,0,0)",
    font          = dict(family="Inter", size=14, color=TEXT_1),
    margin        = dict(t=12, b=82, l=76, r=18),
    xaxis         = dict(
        showgrid=False,
        color=TEXT_1,
        automargin=True,
        showline=True,
        linecolor=BORDER,
        tickfont=dict(family="Inter", size=14, color=TEXT_1),
        title_font=dict(family="Inter", size=14, color=TEXT_1),
        title_standoff=18,
    ),
    yaxis         = dict(
        gridcolor=BORDER_LT,
        zeroline=True,
        zerolinecolor=BORDER,
        color=TEXT_1,
        automargin=True,
        showline=True,
        linecolor=BORDER,
        tickfont=dict(family="Inter", size=14, color=TEXT_1),
        title_font=dict(family="Inter", size=14, color=TEXT_1),
        title_standoff=18,
    ),
)

# Compute insights
vader_by_stock = df.groupby("stock_symbol")["vader_compound"].mean().sort_values()
most_neg_stock = vader_by_stock.index[0]
most_pos_stock = vader_by_stock.index[-1]
most_neg_val   = vader_by_stock.iloc[0]
most_pos_val   = vader_by_stock.iloc[-1]

tb_by_stock = df.groupby("stock_symbol")["textblob_polarity"].mean().sort_values()
tb_pos_count = (tb_by_stock > 0).sum()
tb_neg_count = (tb_by_stock < 0).sum()

st.markdown(f"""
<div class="sec-wrap">
  <h2 class="sec-title">How each stock is being covered</h2>
  <p class="sec-sub">
    Three models, three perspectives. VADER tracks emotional intensity; TextBlob measures general tone polarity;
    FinBERT applies a transformer trained specifically on financial text. All range from −1 (negative) to +1 (positive).
  </p>
</div>
""", unsafe_allow_html=True)

c1, c2 = st.columns([3, 2], gap="large")

with c1:
    fig1 = px.box(
        df, x="stock_symbol", y="vader_compound",
        color_discrete_sequence=[ACCENT],
        labels={
            "stock_symbol": "Stock",
            "vader_compound": "VADER compound",
        },
    )
    fig1.update_traces(marker_color=ACCENT, line_color=ACCENT, fillcolor="rgba(37,99,235,0.12)")
    fig1.update_layout(**CHART, showlegend=False, height=360)
    fig1.update_xaxes(title_text="Stock")
    fig1.update_yaxes(title_text="VADER compound")
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.markdown(f"""
    <div class="insight-card">
      <div class="insight-label">Reading the chart</div>
      <div class="insight-head">VADER compound score by stock</div>
      <div class="insight-body">
        Each box shows the spread of sentiment scores for a stock's news coverage.
        A <strong>taller box</strong> means more variance in how the stock is written about.
        A box sitting <strong>higher</strong> means more consistently positive coverage.
        <br><br>
        <strong>Most positive:</strong> <span class="insight-stat">{most_pos_stock} · {most_pos_val:+.3f}</span><br><br>
        <strong>Most negative:</strong> <span class="insight-stat">{most_neg_stock} · {most_neg_val:+.3f}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

c3, c4 = st.columns([3, 2], gap="large")

with c3:
    avg_by_stock = (
        df.groupby("stock_symbol")["textblob_polarity"]
        .mean().reset_index().sort_values("textblob_polarity")
    )
    avg_by_stock["color"] = avg_by_stock["textblob_polarity"].apply(lambda x: GREEN if x >= 0 else RED)
    fig2 = px.bar(
        avg_by_stock, x="stock_symbol", y="textblob_polarity",
        color="color", color_discrete_map="identity",
        labels={
            "stock_symbol": "Stock",
            "textblob_polarity": "TextBlob polarity",
        },
    )
    fig2.update_layout(**CHART, showlegend=False, height=360)
    fig2.update_xaxes(title_text="Stock")
    fig2.update_yaxes(title_text="TextBlob polarity")
    st.plotly_chart(fig2, use_container_width=True)

with c4:
    st.markdown(f"""
    <div class="insight-card">
      <div class="insight-label">Reading the chart</div>
      <div class="insight-head">Average TextBlob polarity by stock</div>
      <div class="insight-body">
        One bar per stock showing average tone. <strong style="color:{GREEN}">Green</strong> bars mean
        coverage skews positive; <strong style="color:{RED}">red</strong> bars mean negative.
        <br><br>
        <strong>Positive coverage:</strong> <span class="insight-stat">{tb_pos_count} of {len(tb_by_stock)} stocks</span><br><br>
        <strong>Negative coverage:</strong> <span class="insight-stat">{tb_neg_count} of {len(tb_by_stock)} stocks</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── CHART 3 : FinBERT ─────────────────────────────────────────────────────────
fb_by_stock = df.groupby("stock_symbol")["finbert_compound"].mean().sort_values()
fb_pos_count = (fb_by_stock > 0.05).sum()
fb_neg_count = (fb_by_stock < -0.05).sum()

st.markdown(f"""
<div class="sec-wrap">
  <h2 class="sec-title">FinBERT sentiment by stock</h2>
  <p class="sec-sub">
    FinBERT is a BERT model fine-tuned on financial text. Unlike VADER and TextBlob, it understands
    financial jargon and context. Compound = positive probability − negative probability.
  </p>
</div>
""", unsafe_allow_html=True)

c5, c6 = st.columns([3, 2], gap="large")

with c5:
    avg_fb_stock = (
        df.groupby("stock_symbol")["finbert_compound"]
        .mean().reset_index().sort_values("finbert_compound")
    )
    avg_fb_stock["color"] = avg_fb_stock["finbert_compound"].apply(lambda x: GREEN if x >= 0 else RED)
    fig3 = px.bar(
        avg_fb_stock, x="stock_symbol", y="finbert_compound",
        color="color", color_discrete_map="identity",
        labels={
            "stock_symbol": "Stock",
            "finbert_compound": "FinBERT compound",
        },
    )
    fig3.update_layout(**CHART, showlegend=False, height=360)
    fig3.update_xaxes(title_text="Stock")
    fig3.update_yaxes(title_text="FinBERT compound")
    st.plotly_chart(fig3, use_container_width=True)

with c6:
    fb_most_pos = fb_by_stock.index[-1]
    fb_most_neg = fb_by_stock.index[0]
    st.markdown(f"""
    <div class="insight-card">
      <div class="insight-label">Reading the chart</div>
      <div class="insight-head">Average FinBERT compound by stock</div>
      <div class="insight-body">
        FinBERT assigns each article a positive, negative, and neutral probability.
        Compound = positive − negative, ranging from −1 to +1.
        Because it was trained specifically on financial text, it is more sensitive to
        domain-specific language than VADER or TextBlob.
        <br><br>
        <strong>Most positive:</strong> <span class="insight-stat">{fb_most_pos} · {fb_by_stock[fb_most_pos]:+.3f}</span><br><br>
        <strong>Most negative:</strong> <span class="insight-stat">{fb_most_neg} · {fb_by_stock[fb_most_neg]:+.3f}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── TABLE ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="sec-wrap">
  <h2 class="sec-title">Latest articles</h2>
  <p class="sec-sub">50 most recent headlines with their assigned sentiment scores. A sanity check: do the numbers line up with what you'd intuitively say about each title?</p>
</div>
""", unsafe_allow_html=True)

display_df = (
    df[["date", "stock_symbol", "title", "vader_compound", "textblob_polarity", "finbert_compound"]]
    .copy().sort_values("date", ascending=False).head(50).reset_index(drop=True)
)
display_df.columns = ["Date", "Stock", "Title", "VADER", "TextBlob", "FinBERT"]

st.dataframe(
    display_df, use_container_width=True, hide_index=True, height=380,
    column_config={
        "VADER":   st.column_config.NumberColumn(format="%.3f"),
        "TextBlob": st.column_config.NumberColumn(format="%.3f"),
        "FinBERT": st.column_config.NumberColumn(format="%.3f"),
    }
)

# ── DRIFT ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="sec-wrap">
  <h2 class="sec-title">Distribution drift</h2>
  <p class="sec-sub">
    The core observability signal. Evidently AI tests whether the distribution of each sentiment
    feature in today's data is statistically different from the 2019–2024 baseline. If it is, the
    model's assumptions may no longer hold — which matters if anything downstream trusts those scores.
  </p>
</div>
""", unsafe_allow_html=True)

if report_path.exists():
    st.markdown(f"""
    <div class="drift-grid">
      <div class="kpi">
        <div class="kpi-label">Columns monitored</div>
        <div class="kpi-value">{len(SENTIMENT_COLUMNS)}</div>
        <div class="kpi-why">All sentiment features.</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Report status</div>
        <div class="kpi-value" style="color:{AMBER}">Ready</div>
        <div class="kpi-why">Generated by Evidently.</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Current rows</div>
        <div class="kpi-value" style="color:{AMBER}">{len(df):,}</div>
        <div class="kpi-why">Rows in this dashboard view.</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Baseline</div>
        <div class="kpi-value">6 yrs</div>
        <div class="kpi-why">2019-2024 reference window.</div>
      </div>
    </div>
    <div class="insight-card" style="margin-top:1rem;height:auto">
      <div class="insight-label">What this means</div>
      <div class="insight-head">Compare live news with the historical baseline</div>
      <div class="insight-body">
        The Evidently report compares the current live rows with the historical baseline across all
        sentiment features. Use the full report for the actual drift decisions, test details, and
        per-column distributions.
      </div>
    </div>
    """, unsafe_allow_html=True)
    with open(report_path, "rb") as f:
        st.download_button(
            "Download full Evidently report",
            data=f,
            file_name="drift_report.html",
            mime="text/html",
        )
else:
    st.info("No drift report yet. It will be generated automatically on the next pipeline run.")
