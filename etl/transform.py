"""
ETL — Etapa de Transformação (Transform)

Responsabilidades:
  1. Para cada usuário extraído, chama a API Groq (Llama-3)
  2. Gera uma mensagem de marketing personalizada sobre investimentos
  3. Anexa a mensagem ao campo 'news' do usuário
"""

import logging
import os

from groq import Groq

logger = logging.getLogger(__name__)

ICON_URL = (
    "https://digitalinnovationone.github.io"
    "/santander-dev-week-2023-api/icons/credit.svg"
)

SYSTEM_PROMPT = (
    "Você é um especialista em marketing bancário do Santander Brasil. "
    "Seu tom é próximo, motivador e financeiramente educativo. "
    "Escreva sempre em português brasileiro."
)

USER_PROMPT_TEMPLATE = (
    "Crie uma mensagem curta e personalizada para {name}, cliente do Santander, "
    "destacando a importância de investir o dinheiro parado na conta "
    "(saldo atual: R$ {balance:.2f}). "
    "A mensagem deve ter no máximo 110 caracteres, ser direta e usar o primeiro nome do cliente."
)


def _build_prompt(user: dict) -> str:
    first_name = user["name"].split()[0]
    balance = user.get("account", {}).get("balance", 0.0)
    return USER_PROMPT_TEMPLATE.format(name=first_name, balance=balance)


def generate_news(user: dict, client: Groq) -> str:
    """
    Chama o modelo Llama-3 via Groq API e retorna a mensagem gerada.

    Args:
        user:   Dicionário com dados do usuário.
        client: Instância autenticada do cliente Groq.

    Returns:
        Mensagem de marketing personalizada (string).
    """
    prompt = _build_prompt(user)

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        max_tokens=80,
        temperature=0.85,
    )

    message = completion.choices[0].message.content.strip().strip('"')
    return message


def transform(users: list[dict]) -> list[dict]:
    """
    Orquestra a etapa de transformação completa.

    Para cada usuário, gera uma mensagem via LLM e adiciona ao campo 'news'.

    Returns:
        Lista de usuários com campo 'news' atualizado.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Variável de ambiente GROQ_API_KEY não encontrada. "
            "Verifique o arquivo .env na raiz do projeto."
        )

    client = Groq(api_key=api_key)
    logger.info(f"[Transform] Iniciando geração de mensagens para {len(users)} usuário(s)...")

    for user in users:
        try:
            news_text = generate_news(user, client)
            user["news"].append({
                "icon": ICON_URL,
                "description": news_text,
            })
            logger.info(f"[Transform] ✅ {user['name']}: \"{news_text}\"")
        except Exception as e:
            logger.error(f"[Transform] ❌ Erro ao gerar mensagem para {user['name']}: {e}")

    logger.info("[Transform] Transformação concluída.")
    return users
