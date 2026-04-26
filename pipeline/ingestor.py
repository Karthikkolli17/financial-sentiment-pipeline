import feedparser
import pandas as pd
from datetime import date

STOCKS = ["AMD", "BRK-B", "CVX", "DIS", "GOOG", "GS", "INTC", "NVDA", "WMT", "XOM"]


def _parse_date(entry):
    pub = entry.get("published_parsed") or entry.get("updated_parsed")
    if pub:
        try:
            return str(date(pub.tm_year, pub.tm_mon, pub.tm_mday))
        except Exception:
            pass
    return str(date.today())


def fetch_news():
    all_articles = []

    for symbol in STOCKS:
        try:
            url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
            feed = feedparser.parse(url)

            for entry in feed.entries:
                all_articles.append({
                    "date":         _parse_date(entry),
                    "stock_symbol": symbol,
                    "title":        entry.get("title", ""),
                    "text":         entry.get("summary", "") or entry.get("title", ""),
                })
        except Exception as e:
            print(f"Failed to fetch news for {symbol}: {e}")

    return pd.DataFrame(all_articles)