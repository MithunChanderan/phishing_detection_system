"""
Feature Extractor — converts analysis signals into a numeric feature vector
for the ML phishing classifier.
"""

import numpy as np


class FeatureExtractor:
    """
    Transforms the dictionaries produced by the existing detection modules
    (header_signals, url_signals, nlp_signals) into a flat NumPy feature
    vector suitable for scikit-learn models.
    """

    # Ordered feature names (must stay consistent between training & inference)
    FEATURE_NAMES = [
        "spf_fail",
        "spf_softfail",
        "spf_none",
        "dkim_present",
        "from_return_path_mismatch",
        "display_name_spoofing",
        "shortened_url",
        "suspicious_tld",
        "heuristic_new_domain",
        "url_count",
        "urgency_score",
        "fear_score",
        "authority_score",
        "imperative_language",
        "sentiment_polarity",
    ]

    # ------------------------------------------------------------------ #
    #  Public API
    # ------------------------------------------------------------------ #

    def extract(
        self,
        header_signals: dict,
        url_signals: dict,
        nlp_signals: dict,
        url_count: int = 0,
    ) -> np.ndarray:
        """Return a 1-D NumPy array of numeric features."""

        spf = header_signals.get("spf", "none")

        features = [
            # Header features
            1.0 if spf == "fail" else 0.0,
            1.0 if spf == "softfail" else 0.0,
            1.0 if spf == "none" else 0.0,
            1.0 if header_signals.get("dkim_present", True) else 0.0,
            1.0 if header_signals.get("from_return_path_mismatch", False) else 0.0,
            1.0 if header_signals.get("display_name_spoofing", False) else 0.0,
            # URL features
            1.0 if url_signals.get("shortened", False) else 0.0,
            1.0 if url_signals.get("suspicious_tld", False) else 0.0,
            1.0 if url_signals.get("heuristic_new_domain", False) else 0.0,
            float(url_count),
            # NLP features
            float(nlp_signals.get("urgency_score", 0)),
            float(nlp_signals.get("fear_score", 0)),
            float(nlp_signals.get("authority_score", 0)),
            1.0 if nlp_signals.get("imperative_language", False) else 0.0,
            float(nlp_signals.get("sentiment_polarity", 0.0)),
        ]

        return np.array(features, dtype=np.float64)

    @classmethod
    def feature_names(cls) -> list:
        """Return the ordered list of feature names."""
        return list(cls.FEATURE_NAMES)
