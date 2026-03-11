from nlp_analysis.tone_analyzer import ToneAnalyzer
from nlp_analysis.sentiment_engine import SentimentEngine

sample_text = """
URGENT: Your PayPal account has been suspended due to suspicious activity.
Verify immediately to avoid permanent closure.
"""

tone = ToneAnalyzer(sample_text)
sentiment = SentimentEngine(sample_text)

results = {
    "urgency_score": tone.urgency_score(),
    "fear_score": tone.fear_score(),
    "authority_score": tone.authority_score(),
    "imperative_language": tone.imperative_language(),
    "sentiment_polarity": sentiment.polarity()
}

print(results)
