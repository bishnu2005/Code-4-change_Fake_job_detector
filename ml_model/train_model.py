"""
Train Model Script
Loads the dataset, engineers features, trains a Random Forest classifier,
and saves the trained model + vectorizer to disk.
"""

import os
import sys
import time
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    accuracy_score,
    f1_score,
)

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from feature_engineering import build_all_features, combine_text_fields


# ── Configuration ────────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "fake_job_postings.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "saved_model")
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")

RANDOM_STATE = 42
TEST_SIZE = 0.2
N_ESTIMATORS = 200
MAX_DEPTH = 30
MIN_SAMPLES_SPLIT = 5
MIN_SAMPLES_LEAF = 2


def load_data(filepath):
    """Load and perform initial cleaning of the dataset."""
    print(f"📂 Loading dataset from: {filepath}")
    df = pd.read_csv(filepath)
    print(f"   → {len(df)} rows, {len(df.columns)} columns loaded")

    # Quick dataset overview
    fraud_count = df["fraudulent"].sum()
    legit_count = len(df) - fraud_count
    print(f"   → Legitimate: {legit_count} ({legit_count/len(df)*100:.1f}%)")
    print(f"   → Fraudulent: {fraud_count} ({fraud_count/len(df)*100:.1f}%)")
    print()

    return df


def train_model():
    """Main training pipeline."""
    start_time = time.time()

    # ── Step 1: Load Data ────────────────────────────────────────────
    if not os.path.exists(DATA_PATH):
        print(f"❌ Dataset not found at: {DATA_PATH}")
        print("   Please download 'fake_job_postings.csv' from Kaggle and place it in ml_model/data/")
        sys.exit(1)

    df = load_data(DATA_PATH)

    # ── Step 2: Extract target variable ──────────────────────────────
    y = df["fraudulent"].values
    print("🔧 Engineering features...")

    # ── Step 3: Build features ───────────────────────────────────────
    X, tfidf_vectorizer, feature_names = build_all_features(df)
    print(f"   → Feature matrix shape: {X.shape}")
    print(f"   → TF-IDF features: {len([f for f in feature_names if f.startswith('tfidf_')])}")
    print(f"   → Engineered features: {len([f for f in feature_names if not f.startswith('tfidf_')])}")
    print()

    # ── Step 4: Train/Test Split ─────────────────────────────────────
    print("📊 Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    print(f"   → Training set: {X_train.shape[0]} samples")
    print(f"   → Test set:     {X_test.shape[0]} samples")
    print()

    # ── Step 5: Train Random Forest ──────────────────────────────────
    print("🌲 Training Random Forest classifier...")
    model = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        max_depth=MAX_DEPTH,
        min_samples_split=MIN_SAMPLES_SPLIT,
        min_samples_leaf=MIN_SAMPLES_LEAF,
        class_weight="balanced",  # Handle class imbalance
        random_state=RANDOM_STATE,
        n_jobs=-1,  # Use all CPU cores
    )
    model.fit(X_train, y_train)
    print("   → Training complete!")
    print()

    # ── Step 6: Evaluate ─────────────────────────────────────────────
    print("📈 Evaluating model...")
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_proba)

    print(f"   → Accuracy:  {accuracy:.4f}")
    print(f"   → F1 Score:  {f1:.4f}")
    print(f"   → ROC AUC:   {roc_auc:.4f}")
    print()

    print("📋 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Legitimate", "Fraudulent"]))

    print("🔢 Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"   TN={cm[0][0]}  FP={cm[0][1]}")
    print(f"   FN={cm[1][0]}  TP={cm[1][1]}")
    print()

    # ── Step 7: Cross-validation ─────────────────────────────────────
    print("🔄 Running 5-fold cross-validation...")
    cv_scores = cross_val_score(model, X, y, cv=5, scoring="f1", n_jobs=-1)
    print(f"   → CV F1 Scores: {cv_scores}")
    print(f"   → Mean F1:      {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    print()

    # ── Step 8: Feature Importance ───────────────────────────────────
    print("🏆 Top 20 Most Important Features:")
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1][:20]
    for rank, idx in enumerate(indices, 1):
        name = feature_names[idx] if idx < len(feature_names) else f"feature_{idx}"
        print(f"   {rank:2d}. {name}: {importances[idx]:.4f}")
    print()

    # ── Step 9: Save Model & Vectorizer ──────────────────────────────
    os.makedirs(MODEL_DIR, exist_ok=True)

    print(f"💾 Saving model to: {MODEL_PATH}")
    joblib.dump(model, MODEL_PATH)

    print(f"💾 Saving vectorizer to: {VECTORIZER_PATH}")
    joblib.dump(tfidf_vectorizer, VECTORIZER_PATH)

    elapsed = time.time() - start_time
    print()
    print(f"✅ Training pipeline complete in {elapsed:.1f}s")
    print(f"   Model saved to: {MODEL_PATH}")
    print(f"   Vectorizer saved to: {VECTORIZER_PATH}")

    return model, tfidf_vectorizer


if __name__ == "__main__":
    train_model()
