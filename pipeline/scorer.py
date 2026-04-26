from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

analyzer = SentimentIntensityAnalyzer()


def score_article(text):
    text = str(text)
    vader_scores = analyzer.polarity_scores(text)
    blob = TextBlob(text)

    return {
        "vader_compound":        vader_scores["compound"],
        "vader_positive":        vader_scores["pos"],
        "vader_neutral":         vader_scores["neu"],
        "vader_negative":        vader_scores["neg"],
        "textblob_polarity":     blob.sentiment.polarity,
        "textblob_subjectivity": blob.sentiment.subjectivity,
    }
