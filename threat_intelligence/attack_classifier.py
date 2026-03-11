"""
Attack Classifier — categorises a phishing email into a specific
attack type based on heuristic keyword / pattern matching.
"""

import re


# --------------------------------------------------------------------------- #
#  Attack-type signatures
# --------------------------------------------------------------------------- #

_ATTACK_SIGNATURES: dict[str, dict] = {
    "Credential Harvesting": {
        "url_keywords": [
            "login", "signin", "verify", "account", "password",
            "secure", "update", "confirm", "webscr", "authenticate",
        ],
        "body_keywords": [
            "verify your account", "confirm your identity",
            "update your password", "enter your credentials",
            "sign in", "log in", "reset password",
            "confirm your account",
        ],
    },
    "Malware Delivery": {
        "url_keywords": [
            ".exe", ".zip", ".rar", ".scr", ".bat", ".js",
            "download", "attachment",
        ],
        "body_keywords": [
            "open the attached", "download the file",
            "enable macros", "enable content",
            "see attached", "review the document",
        ],
    },
    "Business Email Compromise": {
        "body_keywords": [
            "wire transfer", "bank transfer", "payment",
            "invoice attached", "change of bank",
            "new account details", "ceo", "cfo", "urgent request",
            "confidential", "do not share",
        ],
        "url_keywords": [],
    },
    "Invoice Scam": {
        "body_keywords": [
            "invoice", "overdue payment", "outstanding balance",
            "payment due", "remittance", "purchase order",
            "billing statement", "pay now",
        ],
        "url_keywords": ["invoice", "payment", "pay"],
    },
}


# --------------------------------------------------------------------------- #
#  Classifier
# --------------------------------------------------------------------------- #

class AttackClassifier:
    """
    Rule-based classifier that matches email content against known
    phishing-attack signatures.
    """

    def classify(
        self,
        body_text: str,
        urls: list[str] | None = None,
        subject: str = "",
    ) -> dict:
        """
        Return ``{"attack_type": str, "confidence": str, "matched_indicators": list}``.
        """
        text = f"{subject} {body_text}".lower()
        url_blob = " ".join(urls or []).lower()

        scores: dict[str, list[str]] = {}

        for attack_type, sigs in _ATTACK_SIGNATURES.items():
            matches: list[str] = []

            for kw in sigs.get("body_keywords", []):
                if kw in text:
                    matches.append(f"body: '{kw}'")

            for kw in sigs.get("url_keywords", []):
                if kw in url_blob:
                    matches.append(f"url: '{kw}'")

            if matches:
                scores[attack_type] = matches

        if not scores:
            return {
                "attack_type": "Generic Phishing",
                "confidence": "Low",
                "matched_indicators": [],
            }

        # Pick the attack type with the most matched indicators
        best = max(scores, key=lambda k: len(scores[k]))
        n_matches = len(scores[best])
        confidence = "High" if n_matches >= 3 else ("Medium" if n_matches >= 2 else "Low")

        return {
            "attack_type": best,
            "confidence": confidence,
            "matched_indicators": scores[best],
        }
