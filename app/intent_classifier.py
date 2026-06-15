"""
intent_classifier.py – TF-IDF based intent classification
Trained on voyago_dataset.csv at startup (no external model download needed)
"""

import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import pickle
import os
from app.config import settings


class IntentClassifier:
    """
    Lightweight TF-IDF + Logistic Regression classifier.
    Trains in < 1 second on the 5000-row dataset.
    Supports Arabic + English mixed text.
    """

    def __init__(self):
        self.model: Pipeline | None = None
        self.label_map: dict = {}
        self._load_or_train()

    # ── Text normalisation ────────────────────────────────────────────────
    @staticmethod
    def normalize(text: str) -> str:
        text = text.lower().strip()
        # Remove Arabic diacritics (tashkeel)
        text = re.sub(r"[\u064B-\u065F\u0670]", "", text)
        # Normalize alef variants
        text = re.sub(r"[أإآ]", "ا", text)
        # Normalize teh marbuta
        text = re.sub(r"ة", "ه", text)
        # Remove punctuation
        text = re.sub(r"[^\w\s]", " ", text)
        return text

    # ── Training ──────────────────────────────────────────────────────────
    def _train(self, df: pd.DataFrame):
        X = df["User_Query_Normalized"].fillna("").apply(self.normalize)
        y = df["Intent"]

        self.model = Pipeline([
            ("tfidf", TfidfVectorizer(
                analyzer="char_wb",
                ngram_range=(2, 5),
                max_features=20_000,
                sublinear_tf=True,
            )),
            ("clf", LogisticRegression(
                max_iter=1000,
                C=5.0,
                class_weight="balanced",
                solver="lbfgs",
            )),
        ])
        self.model.fit(X, y)

    def _load_or_train(self):
        cache = "data/intent_model.pkl"
        if os.path.exists(cache):
            with open(cache, "rb") as f:
                self.model = pickle.load(f)
            print("[IntentClassifier] Loaded cached model.")
        else:
            print("[IntentClassifier] Training model …")
            df = pd.read_csv(settings.DATASET_PATH)
            self._train(df)
            os.makedirs("data", exist_ok=True)
            with open(cache, "wb") as f:
                pickle.dump(self.model, f)
            print("[IntentClassifier] Model trained and cached.")

    # ── Prediction ────────────────────────────────────────────────────────
    def predict(self, text: str) -> tuple[str, float]:
        """
        Returns (intent_label, confidence_score 0-1).
        """
        if self.model is None:
            return "unknown", 0.0

        normalized = self.normalize(text)
        proba = self.model.predict_proba([normalized])[0]
        best_idx = proba.argmax()
        intent = self.model.classes_[best_idx]
        confidence = float(proba[best_idx])
        return intent, confidence
