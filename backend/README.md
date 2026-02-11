# Fake Job Posting Detector — Backend

FastAPI-based backend with ML fraud detection for job postings.

## Setup

```bash
cd backend
pip install -r requirements.txt
```

## Train the Model

1. Place `fake_job_postings.csv` in `training/data/`
2. Run:
```bash
python -m training.train
```
This saves `model.pkl` and `vectorizer.pkl` into `artifacts/`.

## Run the Server

```bash
uvicorn app.main:app --reload
```

API docs at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Endpoints

| Method | Path             | Description                          |
|--------|------------------|--------------------------------------|
| GET    | `/health`        | Health check                         |
| POST   | `/analyze_text`  | Analyze job posting from text fields |
| POST   | `/analyze_image` | Analyze job posting from image (OCR) |

## Deploy on Render (Free Tier)

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- No Docker required.
