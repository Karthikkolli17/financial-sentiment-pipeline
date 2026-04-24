# import yfinance as yf
import feedparser
import pandas as pd
from datetime import date

STOCKS = ["AMD", "BRK-B", "CVX", "DIS", "GOOG", "GS", "INTC", "NVDA", "WMT", "XOM"]

def fetch_news():

    all_articles = []

    for symbol in STOCKS:
        try: 
            url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
            feed = feedparser.parse(url)

            # ticker = yf.Ticker(symbol)
            # news = ticker.news

            for entry in feed.entries:
                all_articles.append({
                    "date":         str(date.today()),
                    "stock_symbol": symbol,
                    "title":        entry.get("title", ""),
                    "text":         entry.get("summary", ""),
                    }
                )
        except Exception as e:
            print(f"Failed to fetch news for {symbol}: {e}")

    return pd.DataFrame(all_articles)