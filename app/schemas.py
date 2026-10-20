"""Pydantic v2 schemas for request/response validation."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------- Users ----------


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr


# ---------- Auth ----------


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Tasks ----------


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    done: Optional[bool] = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    done: bool
    owner_id: int
