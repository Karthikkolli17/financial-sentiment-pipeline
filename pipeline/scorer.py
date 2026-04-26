from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import torch
from transformers import pipeline

analyzer = SentimentIntensityAnalyzer()

# Load once at startup — model stays in memory for the lifetime of the pipeline process
_device = 0 if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else -1)
_finbert = pipeline(
    "text-classification",
    model="ProsusAI/finbert",
    tokenizer="ProsusAI/finbert",
    top_k=None,
    device=_device,
)

def score_article(text):

    text = str(text)

    vader_scores = analyzer.polarity_scores(text)
    blob = TextBlob(text)

    # Truncate to 512 chars before tokenisation; max_length=128 tokens keeps inference fast
    fb_pred = _finbert(text[:512], truncation=True, max_length=128)[0]
    fb = {p["label"]: p["score"] for p in fb_pred}

    return {
        "vader_compound":        vader_scores["compound"],
        "vader_positive":        vader_scores["pos"],
        "vader_neutral":         vader_scores["neu"],
        "vader_negative":        vader_scores["neg"],
        "textblob_polarity":     blob.sentiment.polarity,
        "textblob_subjectivity": blob.sentiment.subjectivity,
        "finbert_positive":      fb.get("positive", 0),
        "finbert_negative":      fb.get("negative", 0),
        "finbert_neutral":       fb.get("neutral", 0),
        "finbert_compound":      fb.get("positive", 0) - fb.get("negative", 0),
    }