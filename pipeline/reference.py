import urllib.request
from pathlib import Path
import pandas as pd
from scorer import score_article
from store import init_db, save_articles

CSV_PATH = "/app/merged_stock_news_prices_2019_2024.csv"
HF_URL = "https://huggingface.co/datasets/karthikkolli17/financial-news-sentiment/resolve/main/merged_stock_news_prices_2019_2024.csv"

if not Path(CSV_PATH).exists():
    print("Downloading reference CSV from Hugging Face...")
    urllib.request.urlretrieve(HF_URL, CSV_PATH)
    print("Download complete.")

print("Loading historical data...")                                                        
df = pd.read_csv(CSV_PATH)                                                                 
df = df.drop(columns=["Author", "Publisher"], errors="ignore")                             
df = df.drop_duplicates()                                                                  
df = df.dropna(subset=["Textrank_summary"])

print(f"Scoring {len(df)} articles...")      
scores = df["Textrank_summary"].apply(lambda x: pd.Series(score_article(x)))
df = pd.concat([df, scores], axis=1)

df = df.rename(columns={                                                                   
      "Stock_symbol": "stock_symbol",                                                        
      "Date": "date",                                                                        
      "Article_title": "title",                                                              
      "Textrank_summary": "text",                                                            
})                                                                                         
   
print("Saving to database...")                                                             
init_db()       
save_articles(df[["date", "stock_symbol", "title", "text",
                     "vader_compound", "vader_positive", "vader_neutral",
                     "vader_negative", "textblob_polarity", "textblob_subjectivity",
                     "finbert_compound", "finbert_positive", "finbert_negative", "finbert_neutral"]],
                is_reference=True)                                                           
                                                                                             
print("Done. Reference data loaded.") 