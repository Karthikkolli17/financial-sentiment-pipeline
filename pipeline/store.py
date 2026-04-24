import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("data/pipeline.db")

def init_db():
    DB_PATH.parent.mkdir(parents = True, exist_ok = True)

    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                id                      INTEGER PRIMARY KEY AUTOINCREMENT,
                date                    TEXT,
                stock_symbol            TEXT,
                title                   TEXT,
                text                    TEXT,
                vader_compound           REAL,
                vader_positive          REAL,
                vader_neutral           REAL,
                vader_negative          REAL,
                textblob_polarity       REAL,
                textblob_subjectivity   REAL,
                is_reference            INTEGER DEFAULT 0
                )
            """)
    
    conn.commit()
    conn.close()

def save_articles(df, is_reference = False):

    df["is_reference"] = int(is_reference)

    conn = sqlite3.connect(DB_PATH)
    df.to_sql("articles", conn, if_exists = "append", index = False)
    conn.close()

def load_articles(reference_only = False):

    conn = sqlite3.connect(DB_PATH)
    
    if reference_only:
        query = """
                SELECT *
                FROM articles
                WHERE is_reference = 1
            """
    else:
        query = """
                SELECT *
                FROM articles
            """
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df