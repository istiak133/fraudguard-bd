"""Loads the local ML model once and returns fraud probability for a text."""
import logging
from typing import Optional

import joblib

from app.core.config import MODEL_PATH

log = logging.getLogger(__name__)
_model = None


def load_model(path=MODEL_PATH):
    """Load the trained model; trains one on the fly if the file is missing."""
    global _model
    if path.exists():
        try:
            _model = joblib.load(path)
            return _model
        except Exception as exc:  # e.g. pickle from a different Python/sklearn version
            log.warning("Could not load model (%s), retraining...", exc)
    else:
        log.warning("Model not found at %s, training a new one...", path)
    from ml.train import train
    _model = train(path, verbose=False)
    return _model


def fraud_probability(text: str, model: Optional[object] = None) -> float:
    m = model or _model or load_model()
    return float(m.predict_proba([text])[0][1])
