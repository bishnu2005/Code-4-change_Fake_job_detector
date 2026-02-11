"""
Data preparation: load CSV, drop nulls, merge text columns.
"""
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def load_and_clean(csv_path: str) -> pd.DataFrame:
    """
    Load the fake job postings CSV and prepare it for training.

    Steps:
    1. Load CSV
    2. Drop rows where 'fraudulent' label is missing
    3. Fill NaN text columns with empty strings
    4. Merge relevant text columns into a single 'combined_text' column
    """
    logger.info(f"Loading dataset from {csv_path}")
    df = pd.read_csv(csv_path)

    # Drop rows without a label
    df = df.dropna(subset=["fraudulent"])

    # Text columns to merge
    text_columns = [
        "title",
        "location",
        "department",
        "company_profile",
        "description",
        "requirements",
        "benefits",
        "employment_type",
        "required_experience",
        "required_education",
        "industry",
        "function",
    ]

    # Fill NaN with empty string for text columns
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].fillna("")

    # Merge all text columns into one
    df["combined_text"] = df[text_columns].apply(
        lambda row: " ".join(row.values.astype(str)), axis=1
    )

    # Basic text cleaning
    df["combined_text"] = (
        df["combined_text"]
        .str.lower()
        .str.replace(r"<[^>]+>", " ", regex=True)
        .str.replace(r"[^a-zA-Z0-9\s]", " ", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # Ensure label is integer
    df["fraudulent"] = df["fraudulent"].astype(int)

    logger.info(f"Dataset loaded: {len(df)} rows, fraud rate: {df['fraudulent'].mean():.2%}")
    return df[["combined_text", "fraudulent"]]
