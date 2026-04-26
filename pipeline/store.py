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
        # Migrate existing tables that predate FinBERT columns
        for col in ("finbert_compound", "finbert_positive", "finbert_negative", "finbert_neutral"):
            try:
                conn.execute(text(f"ALTER TABLE articles ADD COLUMN {col} REAL"))
            except Exception:
                pass  # column already exists
        conn.commit()


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
