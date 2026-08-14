
import os
from sqlmodel import SQLModel, Field, create_engine
from sqlalchemy import Column, JSON
from typing import Optional
from datetime import datetime

# Use DATABASE_URL if provided (for Postgres in production), otherwise fallback to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")

# For SQLite we need check_same_thread, for other DBs leave connect_args empty
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


class WebhookEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    webhook_id: str = Field(index=True)
    payload: dict = Field(sa_column=Column(JSON), default={})
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CareerProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_name: Optional[str] = Field(default=None)
    area: Optional[str] = Field(default=None)
    experience: Optional[str] = Field(default=None)
    work_mode: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    soft_skills: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    career_goal: Optional[str] = Field(default=None)
    skills: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    target_roles: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
