"""
ETL — Etapa de Carregamento (Load)

Responsabilidades:
  1. Para cada usuário transformado, envia PUT /users/{id} para a API local
  2. O payload inclui as novas mensagens geradas pela IA no campo 'news'
  3. Registra o resultado de cada atualização
"""

import logging

import requests

logger = logging.getLogger(__name__)


def update_user(user: dict, api_url: str) -> bool:
    """
    Envia as novas 'news' do usuário via PUT /users/{id}.

    Returns:
        True se atualizado com sucesso, False caso contrário.
    """
    # Monta apenas o payload necessário para o endpoint PUT
    payload = {
        "news": [
            {"icon": n["icon"], "description": n["description"]}
            for n in user.get("news", [])
        ]
    }

    try:
        response = requests.put(
            f"{api_url}/users/{user['id']}",
            json=payload,
            timeout=10,
        )
        if response.status_code == 200:
            return True
        logger.warning(
            f"[Load] Falha ao atualizar {user['name']} "
            f"(status {response.status_code}): {response.text}"
        )
        return False
    except requests.RequestException as e:
        logger.error(f"[Load] Erro de conexão ao atualizar {user['name']}: {e}")
        return False


def load(users: list[dict], api_url: str) -> dict:
    """
    Orquestra a etapa de carregamento completa.

    Returns:
        Dicionário com contagem de sucessos e falhas.
    """
    logger.info(f"[Load] Iniciando carregamento de {len(users)} usuário(s)...")

    results = {"success": 0, "failure": 0}

    for user in users:
        ok = update_user(user, api_url)
        if ok:
            results["success"] += 1
            logger.info(f"[Load] ✅ {user['name']} atualizado com sucesso.")
        else:
            results["failure"] += 1
            logger.error(f"[Load] ❌ Falha ao atualizar {user['name']}.")

    logger.info(
        f"[Load] Concluído. ✅ {results['success']} sucesso(s) | "
        f"❌ {results['failure']} falha(s)."
    )
    return results
