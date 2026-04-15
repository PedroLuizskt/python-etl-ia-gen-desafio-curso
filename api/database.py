"""
Configuração do banco de dados SQLite com SQLAlchemy.
Substitui o banco de dados da API Java original (Railway/PostgreSQL).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./sdw2023.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency para injeção de sessão nos endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
