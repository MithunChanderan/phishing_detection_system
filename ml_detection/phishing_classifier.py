"""
Phishing Classifier — RandomForest-based ML model that outputs a
phishing probability score (0.0–1.0).

On first run the model is trained on synthetically generated samples that
capture known phishing patterns, then persisted to disk.
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier

from ml_detection.model_loader import load_model, save_model, DEFAULT_MODEL_PATH


# --------------------------------------------------------------------------- #
#  Synthetic training-data generator
# --------------------------------------------------------------------------- #

def _generate_training_data(n_samples: int = 2000, seed: int = 42):
    """
    Produce synthetic labelled data that mirrors real-world phishing
    characteristics so the classifier can learn meaningful patterns
    without requiring an external dataset.
    """
    rng = np.random.RandomState(seed)
    X, y = [], []

    for _ in range(n_samples):
        is_phish = rng.rand() < 0.5
        if is_phish:
            spf_fail = float(rng.rand() < 0.7)
            spf_softfail = float(rng.rand() < 0.3) if not spf_fail else 0.0
            spf_none = float(rng.rand() < 0.2) if not (spf_fail or spf_softfail) else 0.0
            dkim = float(rng.rand() < 0.3)
            mismatch = float(rng.rand() < 0.65)
            spoofing = float(rng.rand() < 0.55)
            shortened = float(rng.rand() < 0.5)
            sus_tld = float(rng.rand() < 0.5)
            heur_new = float(rng.rand() < 0.45)
            url_count = float(rng.randint(1, 8))
            urgency = float(rng.randint(1, 5))
            fear = float(rng.randint(1, 5))
            authority = float(rng.randint(0, 4))
            imperative = float(rng.rand() < 0.7)
            polarity = round(rng.uniform(-0.9, 0.1), 2)
        else:
            spf_fail = float(rng.rand() < 0.05)
            spf_softfail = float(rng.rand() < 0.1)
            spf_none = float(rng.rand() < 0.15) if not (spf_fail or spf_softfail) else 0.0
            dkim = float(rng.rand() < 0.9)
            mismatch = float(rng.rand() < 0.08)
            spoofing = float(rng.rand() < 0.05)
            shortened = float(rng.rand() < 0.1)
            sus_tld = float(rng.rand() < 0.05)
            heur_new = float(rng.rand() < 0.1)
            url_count = float(rng.randint(0, 3))
            urgency = float(rng.randint(0, 1))
            fear = float(rng.randint(0, 1))
            authority = float(rng.randint(0, 1))
            imperative = float(rng.rand() < 0.1)
            polarity = round(rng.uniform(-0.2, 0.8), 2)

        X.append([
            spf_fail, spf_softfail, spf_none, dkim, mismatch, spoofing,
            shortened, sus_tld, heur_new, url_count,
            urgency, fear, authority, imperative, polarity,
        ])
        y.append(1 if is_phish else 0)

    return np.array(X), np.array(y)


# --------------------------------------------------------------------------- #
#  Classifier wrapper
# --------------------------------------------------------------------------- #

class PhishingClassifier:
    """
    Wraps a scikit-learn RandomForestClassifier.
    Automatically trains + persists the model on first use.
    """

    def __init__(self, model_path: str | None = None):
        self.model_path = model_path or DEFAULT_MODEL_PATH
        self.model: RandomForestClassifier | None = None
        self._load_or_train()

    # ------------------------------------------------------------------ #
    #  Private helpers
    # ------------------------------------------------------------------ #

    def _load_or_train(self):
        """Load an existing model or train a new one."""
        self.model = load_model(self.model_path)
        if self.model is None:
            self._train_and_save()

    def _train_and_save(self):
        """Train on synthetic data and persist to disk."""
        X, y = _generate_training_data()
        self.model = RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            random_state=42,
            class_weight="balanced",
        )
        self.model.fit(X, y)
        save_model(self.model, self.model_path)

    # ------------------------------------------------------------------ #
    #  Public API
    # ------------------------------------------------------------------ #

    def predict_proba(self, features: np.ndarray) -> float:
        """
        Return the phishing probability (0.0–1.0) for a single sample.

        Parameters
        ----------
        features : np.ndarray
            1-D feature vector as produced by FeatureExtractor.extract().
        """
        if self.model is None:
            return 0.5  # fallback
        proba = self.model.predict_proba(features.reshape(1, -1))
        # Column 1 = probability of class 1 (phishing)
        return float(proba[0][1])

    def predict(self, features: np.ndarray) -> dict:
        """
        Return a dict with the phishing probability and predicted label.
        """
        prob = self.predict_proba(features)
        return {
            "phishing_probability": round(prob, 4),
            "prediction": "phishing" if prob >= 0.5 else "legitimate",
        }
