"""
Pipeline ETL — Santander Dev Week 2023 (Reimplementação em Python)

Fluxo completo:
  Extract   → Lê IDs do CSV e busca usuários na API local (FastAPI + SQLite)
  Transform → Gera mensagens personalizadas via IA Generativa (Groq / Llama-3)
  Load      → Persiste as mensagens de volta na API via PUT /users/{id}

Pré-requisitos:
  1. API local em execução:  make run-api
  2. Seed do banco:          make seed
  3. Variáveis de ambiente:  copie .env.example → .env e preencha GROQ_API_KEY

Execução:
    python main.py
"""

import json
import logging
import os
import sys

from dotenv import load_dotenv

from etl.extract import extract
from etl.load import load
from etl.transform import transform

# ──────────────────────────────────────────────
# Configuração de logging
# ──────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Carrega variáveis de ambiente
# ──────────────────────────────────────────────

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")


# ──────────────────────────────────────────────
# Pipeline principal
# ──────────────────────────────────────────────

def run_pipeline():
    logger.info("=" * 55)
    logger.info("  🚀  Pipeline ETL — Santander Dev Week 2023")
    logger.info("=" * 55)

    # ── Extract ──────────────────────────────
    logger.info("\n📥  [1/3] EXTRACT — Buscando usuários na API...")
    users = extract(api_url=API_URL)

    if not users:
        logger.error("Nenhum usuário extraído. Verifique se a API está no ar e o seed foi executado.")
        sys.exit(1)

    # ── Transform ────────────────────────────
    logger.info("\n🤖  [2/3] TRANSFORM — Gerando mensagens com Llama-3 (Groq)...")
    users = transform(users)

    # Exibe preview das mensagens geradas
    logger.info("\n📋  Preview das mensagens geradas:")
    for u in users:
        latest = u["news"][-1]["description"] if u["news"] else "(sem mensagem)"
        logger.info(f"    → {u['name']}: {latest}")

    # ── Load ─────────────────────────────────
    logger.info("\n📤  [3/3] LOAD — Persistindo mensagens na API...")
    results = load(users=users, api_url=API_URL)

    # ── Resultado final ───────────────────────
    logger.info("\n" + "=" * 55)
    logger.info(f"  ✅  Pipeline concluído!")
    logger.info(f"      Atualizados : {results['success']}")
    logger.info(f"      Falhas      : {results['failure']}")
    logger.info("=" * 55)

    # Salva resultado em JSON para referência
    output_path = "data/output_users.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    logger.info(f"\n💾  Resultado salvo em: {output_path}")


if __name__ == "__main__":
    run_pipeline()
