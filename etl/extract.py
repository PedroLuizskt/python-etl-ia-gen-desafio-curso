"""
ETL — Etapa de Extração (Extract)

Responsabilidades:
  1. Lê a lista de IDs do arquivo SDW2023.csv
  2. Para cada ID, consulta GET /users/{id} na API local
  3. Retorna a lista de objetos de usuário prontos para transformação
"""

import logging
from pathlib import Path

import pandas as pd
import requests

logger = logging.getLogger(__name__)

ICON_URL = (
    "https://digitalinnovationone.github.io"
    "/santander-dev-week-2023-api/icons/credit.svg"
)

CSV_PATH = Path(__file__).parent.parent / "data" / "SDW2023.csv"


def load_user_ids(csv_path: Path = CSV_PATH) -> list[int]:
    """Lê os IDs de usuário do arquivo CSV."""
    df = pd.read_csv(csv_path)
    ids = df["UserID"].tolist()
    logger.info(f"[Extract] {len(ids)} IDs carregados do CSV: {ids}")
    return ids


def fetch_user(user_id: int, api_url: str) -> dict | None:
    """Realiza GET /users/{id} e retorna o dicionário do usuário ou None."""
    try:
        response = requests.get(f"{api_url}/users/{user_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        logger.warning(f"[Extract] Usuário {user_id} não encontrado (status {response.status_code}).")
        return None
    except requests.RequestException as e:
        logger.error(f"[Extract] Erro ao buscar usuário {user_id}: {e}")
        return None


def extract(api_url: str, csv_path: Path = CSV_PATH) -> list[dict]:
    """
    Orquestra a etapa de extração completa.

    Returns:
        Lista de dicionários de usuários extraídos da API.
    """
    user_ids = load_user_ids(csv_path)
    users = []

    for uid in user_ids:
        user = fetch_user(uid, api_url)
        if user:
            # Garante que o campo 'news' exista para a etapa de transformação
            user.setdefault("news", [])
            users.append(user)
            logger.info(f"[Extract] ✅ Usuário extraído: {user['name']} (id={user['id']})")
        else:
            logger.warning(f"[Extract] ⚠️  Usuário id={uid} ignorado.")

    logger.info(f"[Extract] Extração concluída. {len(users)} usuário(s) obtidos.")
    return users
