import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title = "Dashboard: Financial Sentiment", layout = "wide")

st.title("Financial Sentiment Dashboard")

DB_PATH = Path("data/pipeline.db")

def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("""
                        SELECT *
                        FROM articles
                        WHERE is_reference = 0
                    """, conn)
    conn.close()
    return df

df = load_data()

if df.empty:
    st.warning("No live data yet. Pipeline didn't start or is starting up.")
    st.stop()

st.subheader("Latest Articles")
st.dataframe(df[["date", "stock_symbol", "title", "vader_compound", "textblob_polarity"]].tail(50))

st.subheader("VADER Compound Score by Stock")
fig = px.box(df, x = "stock_symbol", y = "vader_compound", color = "stock_symbol")
st.plotly_chart(fig, use_container_width = True)

st.subheader("Drift Report")
report_path = Path("reports/drift_report.html")

if report_path.exists():
    with open(report_path, "r") as f:
        st.components.v1.html(f.read(), height = 800, scrolling = True)
else:
    st.info("No drift report yet. Waiting for pipeline to run.")