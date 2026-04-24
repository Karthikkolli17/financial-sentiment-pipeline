import schedule
import time
import pandas as pd
from ingestor import fetch_news
from scorer import score_article
from monitor import run_drift_report
from store import init_db, save_articles, load_articles

def run_pipeline():

    print('News being fetched: ')
    df = fetch_news()

    if df.empty:
        print("No articles fetched. Skipping the run.")
        return

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

    reference_df = load_articles(reference_only = True)
    current_df = load_articles(reference_only = False)
    current_df = current_df[current_df["is_reference"] == 0]

    report_path = "reports/drift_report.html"
    if reference_df.empty:
        print("No reference data yet. Skipping drift report.")
    else:
        run_drift_report(reference_df, current_df, report_path)
        print ("Drift report saved.")

    print("Pipeline run complete.")


init_db()
run_pipeline()

schedule.every(1).hours.do(run_pipeline)

while True:
    schedule.run_pending()
    time.sleep(60)


