"""
Fixtures compartilhadas entre todos os testes.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.database import Base, get_db
from api.main import app
from api.models import AccountORM, CardORM, UserORM

# ──────────────────────────────────────────────
# Banco de dados em memória exclusivo para testes
# StaticPool garante que todas as sessões compartilhem
# a mesma conexão — obrigatório para SQLite :memory:
# ──────────────────────────────────────────────

TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_database():
    """Cria e destrói o schema a cada teste — banco sempre limpo."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    """Sessão direta ao banco de testes (útil em testes de integração)."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """Cliente HTTP da API com banco de testes injetado via DI."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user(db_session):
    """Usuário completo persistido no banco de testes."""
    user = UserORM(id=1, name="Ana Paula Ferreira")
    user.account = AccountORM(
        id=1, number="00001-1", agency="0001", balance=2500.0, limit=500.0
    )
    user.card = CardORM(id=1, number="**** **** **** 4321", limit=5000.0)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_users_list():
    """Lista de dicionários de usuários (formato da API) para testes ETL."""
    return [
        {
            "id": 1,
            "name": "Ana Paula Ferreira",
            "account": {"id": 1, "number": "00001-1", "agency": "0001", "balance": 2500.0, "limit": 500.0},
            "card":    {"id": 1, "number": "**** **** **** 4321", "limit": 5000.0},
            "features": [],
            "news": [],
        },
        {
            "id": 2,
            "name": "Carlos Eduardo Santos",
            "account": {"id": 2, "number": "00002-2", "agency": "0001", "balance": 1200.0, "limit": 500.0},
            "card":    {"id": 2, "number": "**** **** **** 8765", "limit": 3000.0},
            "features": [],
            "news": [],
        },
    ]
