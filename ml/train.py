"""Train a lightweight text classifier: TF-IDF (word + char n-grams) + Logistic Regression.

Char n-grams handle Banglish spelling variations and Bangla script without any tokenizer.
Run: python -m ml.train
"""
import csv
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline

from app.core.config import DATASET_PATH, MODEL_PATH


def build_pipeline() -> Pipeline:
    features = FeatureUnion([
        ("word", TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=2, sublinear_tf=True)),
        ("char", TfidfVectorizer(lowercase=True, analyzer="char_wb", ngram_range=(2, 5), min_df=2, sublinear_tf=True)),
    ])
    return Pipeline([("features", features), ("clf", LogisticRegression(max_iter=1000, C=2.0))])


def load_dataset(path: Path = DATASET_PATH):
    with path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [r["text"] for r in rows], [int(r["label"]) for r in rows]


def train(model_path: Path = MODEL_PATH, verbose: bool = True) -> Pipeline:
    if not DATASET_PATH.exists():
        from ml.generate_dataset import main as generate
        generate()
    texts, labels = load_dataset()
    x_train, x_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42, stratify=labels)
    model = build_pipeline().fit(x_train, y_train)
    if verbose:
        print(classification_report(y_test, model.predict(x_test), target_names=["legit", "fraud"]))
    model = build_pipeline().fit(texts, labels)  # final model on all data
    model_path.parent.mkdir(exist_ok=True)
    joblib.dump(model, model_path)
    if verbose:
        print(f"Saved model -> {model_path}")
    return model


if __name__ == "__main__":
    train()
