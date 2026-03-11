import re

URGENCY_KEYWORDS = {
    "urgent", "immediately", "asap", "act now",
    "verify now", "limited time", "within 24 hours"
}

FEAR_KEYWORDS = {
    "suspended", "compromised", "security alert",
    "unauthorized", "blocked", "breach"
}

AUTHORITY_KEYWORDS = {
    "bank", "paypal", "microsoft", "admin",
    "support team", "it department"
}


class ToneAnalyzer:
    def __init__(self, text: str):
        self.text = text.lower() if text else ""

    def urgency_score(self) -> int:
        return sum(1 for word in URGENCY_KEYWORDS if word in self.text)

    def fear_score(self) -> int:
        return sum(1 for word in FEAR_KEYWORDS if word in self.text)

    def authority_score(self) -> int:
        return sum(1 for word in AUTHORITY_KEYWORDS if word in self.text)

    def imperative_language(self) -> bool:
        patterns = [
            r"click here",
            r"verify your account",
            r"update your information",
            r"confirm your identity"
        ]
        return any(re.search(p, self.text) for p in patterns)
    def analyze_tone(self) -> dict:
        return {
            "urgency_score": self.urgency_score(),
            "fear_score": self.fear_score(),
            "authority_score": self.authority_score(),
            "imperative_language": self.imperative_language()
        }   
        