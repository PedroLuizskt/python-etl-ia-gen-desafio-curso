"""
Script de seed: popula o banco de dados SQLite com usuários sintéticos
que espelham o domínio original da Santander Dev Week 2023.

Execução:
    python data/seed.py
"""

import sys
import os

# Garante que o módulo 'api' seja encontrado a partir da raiz do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.database import Base, SessionLocal, engine
from api.models import AccountORM, CardORM, UserORM

# ──────────────────────────────────────────────
# Dados sintéticos — clientes bancários brasileiros
# ──────────────────────────────────────────────

USERS_SEED = [
    {
        "id": 1,
        "name": "Ana Paula Ferreira",
        "account": {
            "id": 1, "number": "00001-1", "agency": "0001",
            "balance": 2_500.00, "limit": 500.00,
        },
        "card": {"id": 1, "number": "**** **** **** 4321", "limit": 5_000.00},
    },
    {
        "id": 2,
        "name": "Carlos Eduardo Santos",
        "account": {
            "id": 2, "number": "00002-2", "agency": "0001",
            "balance": 1_200.00, "limit": 500.00,
        },
        "card": {"id": 2, "number": "**** **** **** 8765", "limit": 3_000.00},
    },
    {
        "id": 3,
        "name": "Mariana Costa Silva",
        "account": {
            "id": 3, "number": "00003-3", "agency": "0002",
            "balance": 8_750.00, "limit": 1_000.00,
        },
        "card": {"id": 3, "number": "**** **** **** 1122", "limit": 10_000.00},
    },
    {
        "id": 4,
        "name": "Rafael Oliveira Lima",
        "account": {
            "id": 4, "number": "00004-4", "agency": "0002",
            "balance": 350.00, "limit": 300.00,
        },
        "card": {"id": 4, "number": "**** **** **** 3344", "limit": 1_500.00},
    },
    {
        "id": 5,
        "name": "Beatriz Almeida Souza",
        "account": {
            "id": 5, "number": "00005-5", "agency": "0003",
            "balance": 5_000.00, "limit": 800.00,
        },
        "card": {"id": 5, "number": "**** **** **** 5566", "limit": 7_000.00},
    },
]

ICON_URL = (
    "https://digitalinnovationone.github.io"
    "/santander-dev-week-2023-api/icons/credit.svg"
)


def seed():
    print("🌱 Criando tabelas...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Evita duplicatas em re-execuções
        existing = db.query(UserORM).count()
        if existing > 0:
            print(f"⚠️  Banco já possui {existing} usuário(s). Seed abortado.")
            return

        for data in USERS_SEED:
            user = UserORM(id=data["id"], name=data["name"])

            user.account = AccountORM(
                id=data["account"]["id"],
                number=data["account"]["number"],
                agency=data["account"]["agency"],
                balance=data["account"]["balance"],
                limit=data["account"]["limit"],
            )

            user.card = CardORM(
                id=data["card"]["id"],
                number=data["card"]["number"],
                limit=data["card"]["limit"],
            )

            db.add(user)
            print(f"  ✅ Usuário adicionado: {user.name}")

        db.commit()
        print(f"\n🎉 Seed concluído! {len(USERS_SEED)} usuários criados com sucesso.")

    except Exception as e:
        db.rollback()
        print(f"❌ Erro durante o seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
