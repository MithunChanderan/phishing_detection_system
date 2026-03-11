"""
Model Loader — save / load scikit-learn models via joblib.
"""

import os
import joblib

DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "phishing_model.pkl"
)


def save_model(model, path: str | None = None) -> str:
    """Persist a trained model to *path* (defaults to package dir)."""
    path = path or DEFAULT_MODEL_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(model, path)
    return path


def load_model(path: str | None = None):
    """
    Load a previously saved model.
    Returns ``None`` when the file does not exist.
    """
    path = path or DEFAULT_MODEL_PATH
    if os.path.exists(path):
        return joblib.load(path)
    return None
