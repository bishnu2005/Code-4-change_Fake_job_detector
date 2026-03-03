# Model Artifacts

This directory stores trained ML artifacts:

- `model.pkl` — Trained Logistic Regression model
- `vectorizer.pkl` — Fitted TF-IDF vectorizer

## How to Generate

```bash
cd backend
python -m training.train
```

> These files are **not** committed to git. Run the training script to regenerate.
