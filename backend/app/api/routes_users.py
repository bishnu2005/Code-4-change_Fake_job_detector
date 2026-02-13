"""User API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import CreateUserRequest, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserResponse, status_code=201)
def create_user(
    body: CreateUserRequest,
    db: Session = Depends(get_db),
):
    """Create a new user (simple username-based identity)."""
    existing = db.query(User).filter(User.username == body.username).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username already taken")

    user = User(username=body.username)
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    """Get user profile."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)


@router.post("/login", response_model=UserResponse)
def login_or_create(
    body: CreateUserRequest,
    db: Session = Depends(get_db),
):
    """Login by username — creates account if not exists."""
    user = db.query(User).filter(User.username == body.username).first()
    if not user:
        user = User(username=body.username)
        db.add(user)
        db.commit()
        db.refresh(user)
    return UserResponse.model_validate(user)
