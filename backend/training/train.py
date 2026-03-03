"""
Training script: end-to-end pipeline with calibration.

Usage:
    cd backend
    python -m training.train
"""
import os
import sys
import json
import logging
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, precision_recall_fscore_support

from training.data_prep import load_and_clean
from training.feature_engineering import create_tfidf_vectorizer, fit_transform

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ── Paths (relative to backend/) ────────────────────────────────
DATA_PATH = os.path.join("training", "data", "fake_job_postings.csv")
ARTIFACTS_DIR = "artifacts"
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(ARTIFACTS_DIR, "vectorizer.pkl")
CALIBRATED_MODEL_PATH = os.path.join(ARTIFACTS_DIR, "calibrated_model.pkl")
THRESHOLD_PATH = os.path.join(ARTIFACTS_DIR, "threshold.json")


def main():
    # 1. Check dataset exists
    if not os.path.exists(DATA_PATH):
        logger.error(
            f"Dataset not found at '{DATA_PATH}'. "
            f"Please place fake_job_postings.csv in training/data/"
        )
        sys.exit(1)

    # 2. Load & clean
    df = load_and_clean(DATA_PATH)

    # 3. Train-test split
    X_text = df["combined_text"]
    y = df["fraudulent"]
    X_train_text, X_test_text, y_train, y_test = train_test_split(
        X_text, y, test_size=0.2, random_state=42, stratify=y
    )

    # 4. TF-IDF vectorization (tuned)
    vectorizer = create_tfidf_vectorizer(max_features=10000)
    X_train = fit_transform(vectorizer, X_train_text)
    X_test = vectorizer.transform(X_test_text)

    # 5. Train Logistic Regression (tuned)
    logger.info("Training Logistic Regression (C=1.0, class_weight='balanced')...")
    model = LogisticRegression(
        C=1.0,
        class_weight="balanced",
        max_iter=1000,
        solver="liblinear",
        random_state=42,
    )
    model.fit(X_train, y_train)

    # 6. Calibrate with CalibratedClassifierCV
    logger.info("Calibrating model with isotonic regression...")
    calibrated_model = CalibratedClassifierCV(
        estimator=model,
        method="isotonic",
        cv=5,
    )
    calibrated_model.fit(X_train, y_train)

    # 7. Evaluate uncalibrated
    y_pred = model.predict(X_test)
    print("\n" + "=" * 50)
    print("UNCALIBRATED MODEL — CLASSIFICATION REPORT")
    print("=" * 50)
    print(classification_report(y_test, y_pred, target_names=["Real", "Fake"]))

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, y_pred, pos_label=1, average="binary"
    )
    print(f"  Fake Precision: {precision:.4f}")
    print(f"  Fake Recall:    {recall:.4f}")
    print(f"  Fake F1:        {f1:.4f}")

    # 8. Evaluate calibrated
    y_pred_cal = calibrated_model.predict(X_test)
    print("\n" + "=" * 50)
    print("CALIBRATED MODEL — CLASSIFICATION REPORT")
    print("=" * 50)
    print(classification_report(y_test, y_pred_cal, target_names=["Real", "Fake"]))

    precision_c, recall_c, f1_c, _ = precision_recall_fscore_support(
        y_test, y_pred_cal, pos_label=1, average="binary"
    )
    print(f"  Fake Precision: {precision_c:.4f}")
    print(f"  Fake Recall:    {recall_c:.4f}")
    print(f"  Fake F1:        {f1_c:.4f}")

    # 9. Calibration curve
    y_prob_cal = calibrated_model.predict_proba(X_test)[:, 1]
    fraction_pos, mean_predicted = calibration_curve(
        y_test, y_prob_cal, n_bins=10
    )
    print("\n" + "=" * 50)
    print("CALIBRATION CURVE (bin_mean_predicted → fraction_positive)")
    print("=" * 50)
    for mp, fp in zip(mean_predicted, fraction_pos):
        print(f"  {mp:.3f} → {fp:.3f}")

    # 10. Optimal threshold sweep
    print("\n" + "=" * 60)
    print("THRESHOLD SWEEP (optimizing Fake F1)")
    print("=" * 60)
    print(f"{'Threshold':>10} | {'Precision':>10} | {'Recall':>10} | {'F1':>10}")
    print("-" * 50)

    best_threshold = 0.5
    best_f1 = 0.0
    thresholds = np.arange(0.10, 0.91, 0.01)

    for t in thresholds:
        y_pred_t = (y_prob_cal >= t).astype(int)
        p, r, f, _ = precision_recall_fscore_support(
            y_test, y_pred_t, pos_label=1, average="binary", zero_division=0
        )
        # Print a subset of rows for readability
        if abs(t * 100 % 5) < 0.5 or f > best_f1:
            print(f"{t:>10.2f} | {p:>10.4f} | {r:>10.4f} | {f:>10.4f}")
        if f > best_f1:
            best_f1 = f
            best_threshold = round(t, 2)

    print("-" * 50)
    # Re-compute best metrics for clean output
    y_pred_best = (y_prob_cal >= best_threshold).astype(int)
    bp, br, bf, _ = precision_recall_fscore_support(
        y_test, y_pred_best, pos_label=1, average="binary", zero_division=0
    )
    print(f"\n✨ Best Threshold: {best_threshold}")
    print(f"   Fake Precision: {bp:.4f}")
    print(f"   Fake Recall:    {br:.4f}")
    print(f"   Fake F1:        {bf:.4f}")

    # 11. Save artifacts
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    joblib.dump(calibrated_model, CALIBRATED_MODEL_PATH)

    threshold_data = {"optimal_threshold": best_threshold}
    with open(THRESHOLD_PATH, "w") as f:
        json.dump(threshold_data, f, indent=2)

    logger.info(f"Model saved to {MODEL_PATH}")
    logger.info(f"Vectorizer saved to {VECTORIZER_PATH}")
    logger.info(f"Calibrated model saved to {CALIBRATED_MODEL_PATH}")
    logger.info(f"Threshold saved to {THRESHOLD_PATH}")
    print("\n✅ Training complete. 4 artifacts saved to artifacts/")


if __name__ == "__main__":
    main()
