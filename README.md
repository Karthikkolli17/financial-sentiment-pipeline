# Financial Sentiment Analysis + Live Monitoring Pipeline

Does today's financial news sentiment predict stock price movements? I built this to find out — and then turned the findings into a live system.

Two parts that connect directly: a research notebook that analyses 48k articles, and a pipeline that scores live news using the same models and watches for drift against that same historical data.

---

## What's in here

```
├── notebooks/
│   └── Analysis.ipynb        # Research: does news sentiment predict stock returns?
├── pipeline/
│   ├── main.py               # Runs every hour via scheduler
│   ├── ingestor.py           # Pulls live headlines from Yahoo Finance RSS (10 tickers)
│   ├── scorer.py             # Scores each article: VADER + TextBlob + FinBERT (10 features)
│   ├── monitor.py            # Evidently AI drift detection against 48k historical baseline
│   ├── store.py              # Writes to PostgreSQL (Railway) or SQLite (local)
│   └── reference.py          # Seeds the DB with 48k historical articles on first run
├── dashboard/
│   └── app.py                # Live Streamlit dashboard — scores, charts, drift report
└── docker-compose.yml        # Runs pipeline + dashboard as isolated services
```

---

## Part 1 — The Research

`notebooks/Analysis.ipynb`

I took 48,000+ financial news articles across 10 stocks (AMD, BRK, CVX, DIS, GOOG, GS, INTC, NVDA, WMT, XOM) from 2020–2024 and tested whether sentiment scores can predict next-day stock returns.

Three sentiment models, simple to complex:
- **VADER** — rule-based, optimised for short financial text
- **TextBlob** — general purpose lexicon
- **FinBERT** — BERT model fine-tuned specifically on financial text

Tested against next-day returns to avoid look-ahead bias — same-day returns are contaminated because the market reacts to news within minutes, before end-of-day prices are recorded.

**Results:**

| Model | Accuracy | ROC-AUC |
|---|---|---|
| Baseline (majority class) | 51.08% | 0.500 |
| Logistic Regression | 51.20% | 0.516 |
| Random Forest | 53.84% | 0.567 |

No meaningful signal across any of the three models. The core reason: the dataset has date-level granularity only — no publish timestamps. Without knowing whether an article dropped before or after market hours, the lag between news and price reaction is too noisy to measure cleanly. By the next day's close, any reaction is already fully priced in. This is consistent with the Efficient Market Hypothesis.

<img width="690" height="590" alt="image" src="https://github.com/user-attachments/assets/4bc26473-18e7-4acb-91e8-7d5e1b2eb823" />

> *[Screenshot — Feature importance]*

---

## Part 2 — The Live Pipeline

Built on the same foundation as the research. Same 10 stocks, same three sentiment models, same 48k dataset used as the historical baseline for drift detection.

Every hour:
1. Pulls live headlines from Yahoo Finance RSS
2. Scores each article with VADER, TextBlob, and FinBERT
3. Saves to database
4. Runs an Evidently AI drift report — compares today's sentiment distributions against the 2020–2024 baseline
5. Dashboard updates

The drift monitoring is the direct connection to the research. The notebook defines what "normal" sentiment looks like historically. The pipeline flags when live data stops looking normal.

> *[Screenshot — Dashboard overview]*

> *[Screenshot — Per-stock sentiment charts]*

> *[Screenshot — Drift report]*

---

## Stack

| | |
|---|---|
| Sentiment models | VADER, TextBlob, ProsusAI/FinBERT |
| Drift detection | Evidently AI |
| Database | PostgreSQL (Railway) / SQLite (local) |
| Dashboard | Streamlit + Plotly |
| Containerisation | Docker Compose |
| Deployment | Railway |

---

## Dataset

48,515 articles + stock price data, hosted on Hugging Face:
[karthikkolli17/financial-news-sentiment](https://huggingface.co/datasets/karthikkolli17/financial-news-sentiment)

---

## Run it locally

```bash
git clone https://github.com/Karthikkolli17/financial-sentiment-pipeline.git
cd financial-sentiment-pipeline
docker-compose up --build
```

Dashboard at `http://localhost:8501`
