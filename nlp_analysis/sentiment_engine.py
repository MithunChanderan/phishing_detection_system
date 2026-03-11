from textblob import TextBlob


class SentimentEngine:
    def __init__(self, text: str):
        self.text = text

    def polarity(self) -> float:
        if not self.text:
            return 0.0
        return TextBlob(self.text).sentiment.polarity
    def subjectivity(self) -> float:
        if not self.text:
            return 0.0
        return TextBlob(self.text).sentiment.subjectivity
    def analyze_sentiment(self) -> dict:
        return {
            "polarity": self.polarity(),
            "subjectivity": self.subjectivity()
        }
    