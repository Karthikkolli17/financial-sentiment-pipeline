import os
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text


def _get_engine():
    url = os.environ.get("DATABASE_URL")
    if url:
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return create_engine(url)
    Path("data").mkdir(parents=True, exist_ok=True)
    return create_engine("sqlite:///data/pipeline.db")


def init_db():
    engine = _get_engine()
    dialect = engine.dialect.name
    id_col = (
        "id SERIAL PRIMARY KEY"
        if dialect == "postgresql"
        else "id INTEGER PRIMARY KEY AUTOINCREMENT"
    )
    with engine.connect() as conn:
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS articles (
                {id_col},
                date                  TEXT,
                stock_symbol          TEXT,
                title                 TEXT,
                text                  TEXT,
                vader_compound        REAL,
                vader_positive        REAL,
                vader_neutral         REAL,
                vader_negative        REAL,
                textblob_polarity     REAL,
                textblob_subjectivity REAL,
                finbert_compound      REAL,
                finbert_positive      REAL,
                finbert_negative      REAL,
                finbert_neutral       REAL,
                is_reference          INTEGER DEFAULT 0
            )
        """))
        # Migrate existing tables that predate FinBERT columns.
        # Use savepoints on PostgreSQL so a failed ALTER (column exists) doesn't
        # abort the whole transaction — PostgreSQL marks the transaction as failed
        # on any error, unlike SQLite which handles each statement independently.
        for col in ("finbert_compound", "finbert_positive", "finbert_negative", "finbert_neutral"):
            try:
                if dialect == "postgresql":
                    conn.execute(text("SAVEPOINT add_col"))
                conn.execute(text(f"ALTER TABLE articles ADD COLUMN {col} REAL"))
                if dialect == "postgresql":
                    conn.execute(text("RELEASE SAVEPOINT add_col"))
            except Exception:
                if dialect == "postgresql":
                    conn.execute(text("ROLLBACK TO SAVEPOINT add_col"))
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS drift_reports (
                {id_col.replace('id ', 'report_id ')},
                created_at  TEXT,
                html        TEXT
            )
        """))
        conn.commit()


def save_drift_report(html_content):
    from datetime import datetime, timezone
    engine = _get_engine()
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO drift_reports (created_at, html) VALUES (:ts, :html)"),
            {"ts": datetime.now(timezone.utc).isoformat(), "html": html_content},
        )
        conn.commit()


def load_latest_drift_report():
    engine = _get_engine()
    try:
        row = pd.read_sql(
            "SELECT html, created_at FROM drift_reports ORDER BY report_id DESC LIMIT 1",
            engine,
        )
        if row.empty:
            return None, None
        return row["html"].iloc[0], row["created_at"].iloc[0]
    except Exception:
        return None, None


def save_articles(df, is_reference=False):
    df = df.copy()
    df["is_reference"] = int(is_reference)
    engine = _get_engine()
    df.to_sql("articles", engine, if_exists="append", index=False)


def load_articles(reference_only=False):
    engine = _get_engine()
    query = (
        "SELECT * FROM articles WHERE is_reference = 1"
        if reference_only
        else "SELECT * FROM articles"
    )
    return pd.read_sql(query, engine)
