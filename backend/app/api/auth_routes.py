"""
Auth Routes.
Handles Google Login exchanges.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.services.auth_service import verify_google_token, get_or_create_user, create_access_token
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])

class GoogleLoginRequest(BaseModel):
    id_token: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    avatar_url: str | None
    is_new: bool = False

@router.post("/google", response_model=LoginResponse)
def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    # 1. Verify Google Token
    google_data = verify_google_token(payload.id_token)
    
    # 2. Get or Create User
    # Check if new to set is_new flag (optional UI behavior)
    existing = db.query(User).filter(User.google_id == google_data["sub"]).first()
    is_new = existing is None
    
    user = get_or_create_user(db, google_data)
    
    # 3. Issue JWT
    # We embed user_id in 'sub' claim of our JWT
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        avatar_url=user.avatar_url,
        is_new=is_new
    )
