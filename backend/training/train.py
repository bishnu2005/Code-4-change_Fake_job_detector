"""
Training script: end-to-end pipeline.

Usage:
    cd backend
    python -m training.train
"""
import os
import sys
import logging
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from training.data_prep import load_and_clean
from training.feature_engineering import create_tfidf_vectorizer, fit_transform

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ── Paths (relative to backend/) ────────────────────────────────
DATA_PATH = os.path.join("training", "data", "fake_job_postings.csv")
ARTIFACTS_DIR = "artifacts"
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(ARTIFACTS_DIR, "vectorizer.pkl")


def main():
    # 1. Check dataset exists
    if not os.path.exists(DATA_PATH):
        logger.error(f"Dataset not found at '{DATA_PATH}'. "
                      f"Please place fake_job_postings.csv in training/data/")
        sys.exit(1)

    # 2. Load & clean
    df = load_and_clean(DATA_PATH)

    # 3. Train-test split
    X_text = df["combined_text"]
    y = df["fraudulent"]
    X_train_text, X_test_text, y_train, y_test = train_test_split(
        X_text, y, test_size=0.2, random_state=42, stratify=y
    )

    # 4. TF-IDF vectorization
    vectorizer = create_tfidf_vectorizer(max_features=5000)
    X_train = fit_transform(vectorizer, X_train_text)
    X_test = vectorizer.transform(X_test_text)

    # 5. Train Logistic Regression with balanced class weights
    logger.info("Training Logistic Regression (class_weight='balanced')...")
    model = LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
        solver="liblinear",
        random_state=42,
    )
    model.fit(X_train, y_train)

    # 6. Evaluate
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, target_names=["Real", "Fake"])
    print("\n" + "=" * 50)
    print("CLASSIFICATION REPORT")
    print("=" * 50)
    print(report)

    # 7. Save artifacts
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    logger.info(f"Model saved to {MODEL_PATH}")
    logger.info(f"Vectorizer saved to {VECTORIZER_PATH}")
    print("\n✅ Training complete. Artifacts saved to artifacts/")


if __name__ == "__main__":
    main()
