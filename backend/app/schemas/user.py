"""Pydantic schemas for user endpoints."""
from pydantic import BaseModel, Field
from datetime import datetime


class CreateUserRequest(BaseModel):
    """POST /users — create a user."""
    username: str = Field(..., min_length=2, max_length=100)


class UserResponse(BaseModel):
    """GET /users/{id} response."""
    id: int
    username: str
    reputation_score: float
    report_count: int
    created_at: datetime

    class Config:
        from_attributes = True
