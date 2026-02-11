"""
Feature Engineering Module
Extracts features from job posting data for fraud detection.
- Text features via TF-IDF
- Scam keyword flagging
- Missing field indicators
- Salary anomaly detection
- Binary and categorical features
"""

import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack, csr_matrix


# ── Scam-related keywords ──────────────────────────────────────────────
SCAM_KEYWORDS = [
    "wire transfer", "western union", "money order", "cash only",
    "guaranteed income", "unlimited earning", "earn from home",
    "no experience needed", "no experience required", "no experience necessary",
    "work from home", "make money fast", "easy money", "get rich",
    "financial freedom", "be your own boss", "millionaire",
    "investment opportunity", "bitcoin", "cryptocurrency",
    "click here", "act now", "apply immediately", "urgent",
    "congratulations", "you have been selected", "you've been chosen",
    "personal information", "social security", "bank account",
    "credit card", "ssn", "date of birth",
    "processing fee", "registration fee", "training fee", "upfront fee",
    "free laptop", "free iphone", "free equipment",
    "confidential", "secret shopper", "mystery shopper",
    "data entry", "typing job", "envelope stuffing",
    "multi-level", "mlm", "pyramid",
    "nigerian", "prince", "inheritance",
]

# Suspicious email domains
SUSPICIOUS_DOMAINS = [
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "aol.com", "mail.com", "yandex.com", "protonmail.com",
]


def clean_text(text):
    """Clean and normalize text data."""
    if pd.isna(text) or text is None:
        return ""
    text = str(text).lower()
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Remove URLs
    text = re.sub(r"http\S+|www\.\S+|#URL_\S+", " ", text)
    # Remove email placeholders
    text = re.sub(r"#EMAIL_\S+", " ", text)
    # Remove phone placeholders
    text = re.sub(r"#PHONE_\S+", " ", text)
    # Remove special characters but keep spaces
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def combine_text_fields(row):
    """Combine multiple text fields into a single text blob for TF-IDF."""
    fields = ["title", "company_profile", "description", "requirements", "benefits"]
    parts = []
    for field in fields:
        val = row.get(field, "")
        cleaned = clean_text(val)
        if cleaned:
            parts.append(cleaned)
    return " ".join(parts)


def count_scam_keywords(text):
    """Count the number of scam-related keywords found in text."""
    text_lower = text.lower() if isinstance(text, str) else ""
    count = 0
    for keyword in SCAM_KEYWORDS:
        if keyword in text_lower:
            count += 1
    return count


def extract_scam_keyword_flags(text):
    """Return a list of which scam keywords were found (for explainability)."""
    text_lower = text.lower() if isinstance(text, str) else ""
    found = []
    for keyword in SCAM_KEYWORDS:
        if keyword in text_lower:
            found.append(keyword)
    return found


def count_missing_fields(row):
    """Count how many important fields are missing/empty."""
    important_fields = [
        "company_profile", "description", "requirements",
        "benefits", "salary_range", "location", "department",
        "industry", "function", "required_experience", "required_education",
    ]
    missing = 0
    for field in important_fields:
        val = row.get(field, "")
        if pd.isna(val) or str(val).strip() == "":
            missing += 1
    return missing


def parse_salary(salary_range):
    """Parse salary range string and return (min, max, is_present)."""
    if pd.isna(salary_range) or str(salary_range).strip() == "":
        return 0, 0, 0  # No salary info

    salary_str = str(salary_range).replace(",", "").replace("$", "").strip()
    match = re.findall(r"(\d+)", salary_str)

    if len(match) >= 2:
        return int(match[0]), int(match[1]), 1
    elif len(match) == 1:
        return int(match[0]), int(match[0]), 1
    return 0, 0, 0


def detect_salary_anomaly(salary_min, salary_max):
    """
    Flag salary as anomalous if:
    - Range is unrealistically wide (max > 5x min)
    - Values are suspiciously high (> 500k) or low (< 5k for full-time)
    """
    if salary_min == 0 and salary_max == 0:
        return 0  # No salary to evaluate

    score = 0
    # Unrealistically wide range
    if salary_min > 0 and salary_max > salary_min * 5:
        score += 1
    # Suspiciously high
    if salary_max > 500000:
        score += 1
    # Suspiciously low (below minimum wage territory)
    if 0 < salary_max < 5000:
        score += 1
    return min(score, 1)  # Binary flag


def compute_text_length_features(row):
    """Compute text length features for key fields."""
    desc_len = len(str(row.get("description", ""))) if pd.notna(row.get("description", "")) else 0
    req_len = len(str(row.get("requirements", ""))) if pd.notna(row.get("requirements", "")) else 0
    profile_len = len(str(row.get("company_profile", ""))) if pd.notna(row.get("company_profile", "")) else 0
    benefits_len = len(str(row.get("benefits", ""))) if pd.notna(row.get("benefits", "")) else 0
    title_len = len(str(row.get("title", ""))) if pd.notna(row.get("title", "")) else 0

    return pd.Series({
        "desc_length": desc_len,
        "req_length": req_len,
        "profile_length": profile_len,
        "benefits_length": benefits_len,
        "title_length": title_len,
        "total_text_length": desc_len + req_len + profile_len + benefits_len,
    })


def build_engineered_features(df):
    """
    Build all engineered (non-TF-IDF) features from the dataframe.
    Returns a DataFrame of numeric features.
    """
    features = pd.DataFrame(index=df.index)

    # ── Binary features ─────────────────────────────────────────────
    features["telecommuting"] = df["telecommuting"].fillna(0).astype(int)
    features["has_company_logo"] = df["has_company_logo"].fillna(0).astype(int)
    features["has_questions"] = df["has_questions"].fillna(0).astype(int)

    # ── Missing field count ──────────────────────────────────────────
    features["missing_fields"] = df.apply(count_missing_fields, axis=1)

    # ── Combined text for keyword scanning ───────────────────────────
    combined_text = df.apply(combine_text_fields, axis=1)
    features["scam_keyword_count"] = combined_text.apply(count_scam_keywords)

    # ── Salary features ──────────────────────────────────────────────
    salary_parsed = df["salary_range"].apply(parse_salary)
    features["salary_min"] = salary_parsed.apply(lambda x: x[0])
    features["salary_max"] = salary_parsed.apply(lambda x: x[1])
    features["has_salary"] = salary_parsed.apply(lambda x: x[2])
    features["salary_anomaly"] = features.apply(
        lambda r: detect_salary_anomaly(r["salary_min"], r["salary_max"]), axis=1
    )

    # ── Text length features ─────────────────────────────────────────
    text_lengths = df.apply(compute_text_length_features, axis=1)
    features = pd.concat([features, text_lengths], axis=1)

    # ── Employment type encoding ─────────────────────────────────────
    emp_types = ["Full-time", "Part-time", "Contract", "Temporary", "Other"]
    for et in emp_types:
        col_name = f"emp_type_{et.lower().replace('-', '_')}"
        features[col_name] = (df["employment_type"] == et).astype(int)

    # ── Experience level encoding ────────────────────────────────────
    exp_levels = ["Entry level", "Mid-Senior level", "Executive", "Director",
                  "Internship", "Associate", "Not Applicable"]
    for el in exp_levels:
        col_name = f"exp_{el.lower().replace(' ', '_').replace('-', '_')}"
        features[col_name] = (df["required_experience"] == el).astype(int)

    return features


def build_tfidf_features(text_series, vectorizer=None, max_features=5000):
    """
    Build TF-IDF features from a text series.
    If vectorizer is None, fits a new one. Otherwise uses the provided one.
    Returns (tfidf_matrix, vectorizer).
    """
    if vectorizer is None:
        vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
            sublinear_tf=True,
        )
        tfidf_matrix = vectorizer.fit_transform(text_series)
    else:
        tfidf_matrix = vectorizer.transform(text_series)

    return tfidf_matrix, vectorizer


def build_all_features(df, tfidf_vectorizer=None):
    """
    Build complete feature matrix combining TF-IDF and engineered features.
    Returns (feature_matrix, tfidf_vectorizer, feature_names).
    """
    # Combined text for TF-IDF
    combined_text = df.apply(combine_text_fields, axis=1)

    # TF-IDF features
    tfidf_matrix, tfidf_vec = build_tfidf_features(combined_text, tfidf_vectorizer)

    # Engineered features
    eng_features = build_engineered_features(df)
    eng_matrix = csr_matrix(eng_features.values)

    # Combine all features
    feature_matrix = hstack([tfidf_matrix, eng_matrix])

    # Feature names
    tfidf_names = [f"tfidf_{name}" for name in tfidf_vec.get_feature_names_out()]
    all_feature_names = tfidf_names + list(eng_features.columns)

    return feature_matrix, tfidf_vec, all_feature_names
