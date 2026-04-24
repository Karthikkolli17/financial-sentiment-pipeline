import yfinance as yf
import pandas as pd
from datetime import date

STOCKS = ["AMD", "BRK-B", "CVX", "DIS", "GOOG", "GS", "INTC", "NVDA", "WMT", "XOM"]

def fetch_news():

    all_articles = []

    for symbol in STOCKS:
        ticker = yf.Ticker(symbol)
        news = ticker.news

        for article in news:
            all_articles.append({
                "date":         str(date.today()),
                "stock_symbol": symbol,
                "title":        article.get("title", ""),
                "text":         article.get("summary", ""),
                }
            )

    return pd.DataFrame(all_articles)