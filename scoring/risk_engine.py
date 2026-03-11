class RiskEngine:
    def __init__(self):
        self.score = 0
        self.reasons = []

    def evaluate_headers(self, signals: dict):
        if signals.get("spf") == "fail":
            self.score += 30
            self.reasons.append("SPF authentication failed")
        elif signals.get("spf") == "softfail":
            self.score += 15
            self.reasons.append("SPF softfail detected")

        if not signals.get("dkim_present", True):
            self.score += 15
            self.reasons.append("DKIM signature missing")

        if signals.get("from_return_path_mismatch"):
            self.score += 20
            self.reasons.append("From and Return-Path domain mismatch")

        if signals.get("display_name_spoofing"):
            self.score += 10
            self.reasons.append("Possible display-name spoofing")

    def evaluate_urls(self, signals: dict):
        if signals.get("shortened"):
            self.score += 20
            self.reasons.append("Shortened URL detected")

        if signals.get("suspicious_tld"):
            self.score += 15
            self.reasons.append("Suspicious top-level domain")

        if signals.get("heuristic_new_domain"):
            self.score += 10
            self.reasons.append("Domain appears newly registered")

    def evaluate_nlp(self, signals: dict):
        self.score += signals.get("urgency_score", 0) * 5
        self.score += signals.get("fear_score", 0) * 5
        self.score += signals.get("authority_score", 0) * 5

        if signals.get("imperative_language"):
            self.score += 10
            self.reasons.append("Imperative social-engineering language")

        polarity = signals.get("sentiment_polarity", 0)
        if polarity < -0.5:
            self.score += 10
            self.reasons.append("Strong negative sentiment detected")

    def verdict(self) -> str:
        if self.score > 60:
            return "HIGH RISK"
        elif self.score > 30:
            return "MEDIUM RISK"
        return "LOW RISK"

    def result(self) -> dict:
        return {
            "risk_score": self.score,
            "verdict": self.verdict(),
            "reasons": self.reasons
        }
