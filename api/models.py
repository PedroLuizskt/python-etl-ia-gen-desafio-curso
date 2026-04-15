"""
Modelos ORM (SQLAlchemy) e Schemas de validação (Pydantic).
Espelha o domínio da API Java original da Santander Dev Week 2023.
"""

from __future__ import annotations
from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from api.database import Base


# ──────────────────────────────────────────────
# ORM — Tabelas SQLite
# ──────────────────────────────────────────────

class AccountORM(Base):
    __tablename__ = "accounts"

    id       = Column(Integer, primary_key=True, index=True)
    user_id  = Column(Integer, ForeignKey("users.id"), unique=True)
    number   = Column(String, nullable=False)
    agency   = Column(String, nullable=False)
    balance  = Column(Float, default=0.0)
    limit    = Column(Float, default=500.0)

    owner = relationship("UserORM", back_populates="account")


class CardORM(Base):
    __tablename__ = "cards"

    id      = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    number  = Column(String, nullable=False)
    limit   = Column(Float, default=1000.0)

    owner = relationship("UserORM", back_populates="card")


class NewsORM(Base):
    __tablename__ = "news"

    id          = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id     = Column(Integer, ForeignKey("users.id"))
    icon        = Column(String, nullable=False)
    description = Column(String, nullable=False)

    owner = relationship("UserORM", back_populates="news")


class UserORM(Base):
    __tablename__ = "users"

    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    account  = relationship("AccountORM", back_populates="owner", uselist=False, cascade="all, delete-orphan")
    card     = relationship("CardORM",    back_populates="owner", uselist=False, cascade="all, delete-orphan")
    news     = relationship("NewsORM",    back_populates="owner", cascade="all, delete-orphan")


# ──────────────────────────────────────────────
# Pydantic — Schemas de Request / Response
# ──────────────────────────────────────────────

class AccountSchema(BaseModel):
    id:      int
    number:  str
    agency:  str
    balance: float
    limit:   float

    model_config = {"from_attributes": True}


class CardSchema(BaseModel):
    id:     int
    number: str
    limit:  float

    model_config = {"from_attributes": True}


class NewsSchema(BaseModel):
    id:          int
    icon:        str
    description: str

    model_config = {"from_attributes": True}


class NewsCreateSchema(BaseModel):
    icon:        str
    description: str


class UserSchema(BaseModel):
    id:       int
    name:     str
    account:  Optional[AccountSchema] = None
    card:     Optional[CardSchema]    = None
    features: List                    = []
    news:     List[NewsSchema]        = []

    model_config = {"from_attributes": True}


class UserUpdateSchema(BaseModel):
    """Payload aceito pelo endpoint PUT /users/{id}."""
    name:     Optional[str]              = None
    news:     Optional[List[NewsCreateSchema]] = None
