import schedule
import time
import pandas as pd
from ingestor import fetch_news
from scorer import score_article
from store import init_db, save_articles

def run_pipeline():

    print('News being fetched: ')
    df = fetch_news()

    print(f"Scoring {len(df)} articles: ")
    # df["vader_compound"] = df["text"].apply(lambda x: score_article(x)["vader_compound"])
    # df["vader_positive"] = df["text"].apply(lambda x: score_article(x)["vader_positive"])
    # df["vader_neutral"] = df["text"].apply(lambda x: score_article(x)["vader_neutral"])
    # df["vader_negative"] = df["text"].apply(lambda x: score_article(x)["vader_negative"])
    # df["textblob_polarity"] = df["text"].apply(lambda x: score_article(x)["textblob_polarity"])
    # df["textblob_subjectivity"] = df["text"].apply(lambda x: score_article(x)["textblob_subjectivity"])

    scores = df["text"].apply(lambda x: pd.Series(score_article(x)))
    df = pd.concat([df, scores], axis=1)

    print("Saving to database: ")
    save_articles(df)

    print("Pipeline run complete.")


init_db()
run_pipeline()

schedule.every(1).hours.do(run_pipeline)

while True:
    schedule.run_pending()
    time.sleep(60)
