"""
API local em FastAPI que substitui a API Java original (Santander Dev Week 2023).
Expõe os endpoints GET /users/{id} e PUT /users/{id} consumidos pelo pipeline ETL.

Execução:
    uvicorn api.main:app --reload --port 8000
"""

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from api.database import Base, engine, get_db
from api.models import NewsORM, UserORM, UserSchema, UserUpdateSchema

# Cria todas as tabelas no SQLite (se ainda não existirem)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Santander Dev Week 2023 — API Local",
    description=(
        "Reimplementação local em FastAPI + SQLite da API Java original, "
        "utilizada como backend para o pipeline ETL com IA Generativa (Llama-3)."
    ),
    version="1.0.0",
)


# ──────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────

@app.get("/users/{user_id}", response_model=UserSchema, tags=["Users"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Retorna os dados completos de um usuário pelo ID."""
    user = db.query(UserORM).filter(UserORM.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Usuário {user_id} não encontrado.")
    return user


@app.put("/users/{user_id}", response_model=UserSchema, tags=["Users"])
def update_user(user_id: int, payload: UserUpdateSchema, db: Session = Depends(get_db)):
    """
    Atualiza os dados de um usuário.
    Aceita campo 'news' com lista de novas mensagens geradas pela IA.
    """
    user = db.query(UserORM).filter(UserORM.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Usuário {user_id} não encontrado.")

    if payload.name:
        user.name = payload.name

    if payload.news is not None:
        for news_item in payload.news:
            new_news = NewsORM(
                user_id=user_id,
                icon=news_item.icon,
                description=news_item.description,
            )
            db.add(new_news)

    db.commit()
    db.refresh(user)
    return user


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Santander Dev Week 2023 API (local) está no ar."}
