"""
Evaluate Model Script
Loads the trained model and generates detailed performance metrics,
confusion matrix visualization, and ROC curve.
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_curve,
    roc_auc_score,
    precision_recall_curve,
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from feature_engineering import build_all_features


# ── Configuration ────────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "fake_job_postings.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "saved_model")
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")
PLOTS_DIR = os.path.join(os.path.dirname(__file__), "saved_model", "plots")

RANDOM_STATE = 42
TEST_SIZE = 0.2


def load_artifacts():
    """Load the trained model and vectorizer."""
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Model not found at: {MODEL_PATH}")
        print("   Run train_model.py first!")
        sys.exit(1)

    print("📂 Loading model and vectorizer...")
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    return model, vectorizer


def plot_confusion_matrix(y_true, y_pred, save_path):
    """Generate and save confusion matrix heatmap."""
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=["Legitimate", "Fraudulent"],
        yticklabels=["Legitimate", "Fraudulent"],
    )
    plt.title("Confusion Matrix", fontsize=16, fontweight="bold")
    plt.ylabel("Actual", fontsize=12)
    plt.xlabel("Predicted", fontsize=12)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"   → Saved: {save_path}")


def plot_roc_curve(y_true, y_proba, save_path):
    """Generate and save ROC curve."""
    fpr, tpr, _ = roc_curve(y_true, y_proba)
    auc = roc_auc_score(y_true, y_proba)

    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color="#2563eb", lw=2, label=f"ROC (AUC = {auc:.4f})")
    plt.plot([0, 1], [0, 1], color="gray", lw=1, linestyle="--", label="Random")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate", fontsize=12)
    plt.ylabel("True Positive Rate", fontsize=12)
    plt.title("ROC Curve", fontsize=16, fontweight="bold")
    plt.legend(loc="lower right", fontsize=11)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"   → Saved: {save_path}")


def plot_precision_recall_curve(y_true, y_proba, save_path):
    """Generate and save Precision-Recall curve."""
    precision, recall, _ = precision_recall_curve(y_true, y_proba)

    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, color="#16a34a", lw=2)
    plt.xlabel("Recall", fontsize=12)
    plt.ylabel("Precision", fontsize=12)
    plt.title("Precision-Recall Curve", fontsize=16, fontweight="bold")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"   → Saved: {save_path}")


def plot_feature_importance(model, feature_names, save_path, top_n=20):
    """Generate and save feature importance bar chart."""
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1][:top_n]

    top_names = [feature_names[i] if i < len(feature_names) else f"f_{i}" for i in indices]
    top_importances = importances[indices]

    plt.figure(figsize=(10, 8))
    colors = plt.cm.Blues(np.linspace(0.4, 0.9, top_n))[::-1]
    plt.barh(range(top_n), top_importances[::-1], color=colors)
    plt.yticks(range(top_n), top_names[::-1], fontsize=10)
    plt.xlabel("Importance", fontsize=12)
    plt.title(f"Top {top_n} Feature Importances", fontsize=16, fontweight="bold")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"   → Saved: {save_path}")


def evaluate():
    """Run full evaluation pipeline."""
    # Load data
    print("📂 Loading dataset...")
    df = pd.read_csv(DATA_PATH)
    y = df["fraudulent"].values

    # Load model
    model, vectorizer = load_artifacts()

    # Build features using trained vectorizer
    print("🔧 Building features...")
    X, _, feature_names = build_all_features(df, tfidf_vectorizer=vectorizer)

    # Same split as training
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    # Predictions
    print("📈 Generating predictions...")
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    # ── Metrics ──────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("  MODEL EVALUATION RESULTS")
    print("=" * 60)
    print()

    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_proba)

    print(f"  Accuracy:   {accuracy:.4f}")
    print(f"  Precision:  {precision:.4f}")
    print(f"  Recall:     {recall:.4f}")
    print(f"  F1 Score:   {f1:.4f}")
    print(f"  ROC AUC:    {roc_auc:.4f}")
    print()

    print("📋 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Legitimate", "Fraudulent"]))

    # ── Generate Plots ───────────────────────────────────────────────
    os.makedirs(PLOTS_DIR, exist_ok=True)
    print("📊 Generating plots...")

    plot_confusion_matrix(y_test, y_pred, os.path.join(PLOTS_DIR, "confusion_matrix.png"))
    plot_roc_curve(y_test, y_proba, os.path.join(PLOTS_DIR, "roc_curve.png"))
    plot_precision_recall_curve(y_test, y_proba, os.path.join(PLOTS_DIR, "precision_recall.png"))
    plot_feature_importance(model, feature_names, os.path.join(PLOTS_DIR, "feature_importance.png"))

    print()
    print("✅ Evaluation complete! Plots saved to:", PLOTS_DIR)


if __name__ == "__main__":
    evaluate()
