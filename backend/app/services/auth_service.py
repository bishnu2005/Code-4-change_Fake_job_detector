"""
Authentication Service.
Verifies Google ID Tokens and issues internal JWT Access Tokens.
"""
import os
import time
from datetime import datetime, timedelta
from jose import jwt, JWTError
from google.oauth2 import id_token
from google.auth.transport import requests
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_change_in_prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")  # Add to .env

# Google Request Adapter
_request = requests.Request()

def verify_google_token(token: str) -> dict:
    """
    Verifies Google ID token.
    Returns decoded token dict (payload).
    Throws HTTPException if invalid.
    """
    try:
        # If no client ID configured yet, we can fetch it from token audience (in dev)
        # But optimally strictly check audience.
        id_info = id_token.verify_oauth2_token(token, _request, GOOGLE_CLIENT_ID if GOOGLE_CLIENT_ID else None)
        return id_info
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_or_create_user(db: Session, google_data: dict) -> User:
    """
    Finds usage by google_id or creates one.
    """
    sub = google_data.get("sub")
    email = google_data.get("email")
    name = google_data.get("name", "Unknown User")
    picture = google_data.get("picture")

    if not sub:
        raise HTTPException(status_code=400, detail="Token missing 'sub' claim.")

    user = db.query(User).filter(User.google_id == sub).first()
    
    if user:
        # Update mutable fields on login
        if user.avatar_url != picture:
            user.avatar_url = picture
        if user.username != name:
            user.username = name
        db.commit()
        db.refresh(user)
        return user
    
    # Create new
    new_user = User(
        google_id=sub,
        email=email,
        username=name,
        avatar_url=picture
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def create_access_token(data: dict):
    """Issues internal JWT."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
