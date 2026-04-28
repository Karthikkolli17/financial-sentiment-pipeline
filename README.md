# Financial Sentiment Analysis + Live Monitoring Pipeline

Does today's financial news sentiment predict stock price movements? I built this to find out, and then turned the findings into a live system.

Two parts that connect directly: a research notebook that analyses 48k articles, and a pipeline that scores live news using the same models and watches for drift against that same historical data.

---

## What's in here

```
├── notebooks/
│   └── Analysis.ipynb        # Research: does news sentiment predict stock returns?
├── pipeline/
│   ├── main.py               # Runs every hour via scheduler
│   ├── ingestor.py           # Pulls live headlines from Yahoo Finance RSS (10 tickers)
│   ├── scorer.py             # Scores each article: VADER + TextBlob (6 features)
│   ├── monitor.py            # Evidently AI drift detection against 48k historical baseline
│   ├── store.py              # Writes to PostgreSQL (Railway) or SQLite (local)
│   └── reference.py          # Seeds the DB with 48k historical articles on first run
├── dashboard/
│   └── app.py                # Live Streamlit dashboard — scores, charts, drift report
└── docker-compose.yml        # Runs pipeline + dashboard as isolated services
```

---

## Part 1 — The Research

### Main Dataset

**Source:** [FNSPID](https://huggingface.co/datasets/Zihan1004/FNSPID) — 29.6GB, 10M+ financial news articles.

**Why filtered it down:**
- Full dataset was computationally infeasible on local hardware.
- Pre-COVID data (pre 2020) introduces heavy downward bias, almost all stocks trending together, which adds noise rather than signal.
- Fixed on post-COVID (2020–2024) for a cleaner, more stable market period.
- Even that slice was large, so restricted to the **top 10 stocks by article coverage** across the 5-year window: AMD, BRK, CVX, DIS, GOOG, GS, INTC, NVDA, WMT, XOM

Final dataset: **48,515 articles**, large enough for statistical validity, small enough to run locally. Hosted on Hugging Face:
[karthikkolli17/financial-news-sentiment](https://huggingface.co/datasets/karthikkolli17/financial-news-sentiment)

---

**Notebook**: `notebooks/Analysis.ipynb`

I took financial news articles across 10 stocks (AMD, BRK, CVX, DIS, GOOG, GS, INTC, NVDA, WMT, XOM) from 2020–2024 and tested whether sentiment scores can predict next-day stock returns.

Three sentiment models, simple to complex:
- **VADER** — rule-based, optimised for short financial text
- **TextBlob** — general purpose lexicon
- **FinBERT** — BERT model fine-tuned specifically on financial text

Tested against next day returns to avoid look ahead bias, same-day returns are contaminated because the market reacts to news within minutes, before end-of-day prices are recorded.

**Results:**

| Model | Accuracy | ROC-AUC |
|---|---|---|
| Baseline (majority class) | 51.08% | 0.500 |
| Logistic Regression | 51.20% | 0.516 |
| Random Forest | 53.84% | 0.567 |

No meaningful signal across any of the three models. The core reason: the dataset has date level granularity only, no publish timestamps. Without knowing whether an article dropped before or after market hours, the lag between news and price reaction is too noisy to measure cleanly. By the next day's close, any reaction is already fully priced in. This is consistent with the Efficient Market Hypothesis.

<img width="800" alt="ROC curves for Logistic Regression (AUC 0.516) and Random Forest (AUC 0.567) — both barely above the random baseline" src="https://github.com/user-attachments/assets/4bc26473-18e7-4acb-91e8-7d5e1b2eb823" />

<br><br>

<img width="800" alt="Random Forest feature importance — all 10 sentiment features score roughly equally, suggesting no single model dominates" src="https://github.com/user-attachments/assets/d10c2534-2742-40fb-b343-8be98afa8102" />

<br><br>

<img width="800" alt="Correlation matrix of sentiment features vs price metrics — near-zero correlation between all sentiment scores and next-day price change" src="https://github.com/user-attachments/assets/a6f014bf-4fa0-49e6-97a0-11ffe9bbd346" />

---

## Part 2 — The Live Pipeline

Built on the same foundation as the research. Same 10 stocks, same 48k dataset used as the historical baseline for drift detection.

The live pipeline uses **VADER + TextBlob** only. FinBERT was evaluated in the notebook but dropped from the live system, the model weights alone are 600MB and the Docker image exceeded Railway's 4.8GB limit. Since FinBERT showed no meaningful accuracy improvement over VADER in the research, the tradeoff wasn't worth it.

Every hour:
1. Pulls live headlines from Yahoo Finance RSS
2. Scores each article with VADER and TextBlob
3. Saves to database (deduplicates against existing articles by title + date)
4. Runs an Evidently AI drift report, compares today's sentiment distributions against the 2020–2024 baseline
5. Dashboard updates

The drift monitoring is the direct connection to the research. The notebook defines what "normal" sentiment looks like historically. The pipeline flags when live data stops looking normal.

<img width="800" alt="Pipeline overview showing the five stages: ingest, score, store, monitor, and visualise — with live article count, average VADER score, and drift status" src="https://github.com/user-attachments/assets/c04c05e1-34a2-446b-90f6-4339814b6a0c" />

<br><br>

<img width="800" alt="Latest scored articles table and distribution drift section showing Evidently AI comparison against the 48k historical baseline" src="https://github.com/user-attachments/assets/da1293e6-d53a-44af-8417-2bdea5eaf54c" />

<br><br>

<img width="800" alt="VADER sentiment by stock — box plot showing score spread and variance across 10 tickers" src="https://github.com/user-attachments/assets/0817b938-4561-4af9-88c8-2222c4114759" />

<br><br>

<img width="800" alt="TextBlob sentiment by stock — bar chart showing average polarity per ticker" src="https://github.com/user-attachments/assets/cea34a8a-a07c-4db2-8ea9-32b8ed2a60ab" />

---

## Stack

| | |
|---|---|
| Sentiment models | VADER, TextBlob (live pipeline); FinBERT (research notebook only) |
| Drift detection | Evidently AI |
| Database | PostgreSQL (Railway) / SQLite (local) |
| Dashboard | Streamlit + Plotly |
| Containerisation | Docker Compose |
| Deployment | Railway |

---

## Run it locally

```bash
git clone https://github.com/Karthikkolli17/financial-sentiment-pipeline.git
cd financial-sentiment-pipeline
docker-compose up --build
```

Dashboard at `http://localhost:8501`
