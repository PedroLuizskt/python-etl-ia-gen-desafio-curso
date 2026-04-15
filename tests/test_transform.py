"""
Testes da etapa de Transformação (Transform).

Cobre:
  - Construção do prompt personalizado
  - Geração de mensagem via Groq (mockado)
  - transform() orquestrando múltiplos usuários
  - Erro quando GROQ_API_KEY está ausente
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from etl.transform import _build_prompt, generate_news, transform


class TestBuildPrompt:
    def test_prompt_contains_first_name(self, sample_users_list):
        prompt = _build_prompt(sample_users_list[0])
        assert "Ana" in prompt

    def test_prompt_contains_balance(self, sample_users_list):
        prompt = _build_prompt(sample_users_list[0])
        assert "2500" in prompt

    def test_prompt_uses_only_first_name(self, sample_users_list):
        prompt = _build_prompt(sample_users_list[0])
        assert "Ferreira" not in prompt

    def test_prompt_handles_zero_balance(self):
        user = {"name": "Carlos Silva", "account": {"balance": 0.0}}
        prompt = _build_prompt(user)
        assert "0.00" in prompt

    def test_prompt_handles_missing_account(self):
        user = {"name": "Maria Souza"}
        prompt = _build_prompt(user)
        assert "Maria" in prompt


class TestGenerateNews:
    def _make_groq_mock(self, text: str):
        mock_client   = MagicMock()
        mock_choice   = MagicMock()
        mock_message  = MagicMock()
        mock_message.content = f'"{text}"'
        mock_choice.message  = mock_message
        mock_client.chat.completions.create.return_value.choices = [mock_choice]
        return mock_client

    def test_returns_string(self, sample_users_list):
        client = self._make_groq_mock("Ana, invista hoje!")
        result = generate_news(sample_users_list[0], client)
        assert isinstance(result, str)

    def test_strips_surrounding_quotes(self, sample_users_list):
        client = self._make_groq_mock("Ana, invista hoje!")
        result = generate_news(sample_users_list[0], client)
        assert not result.startswith('"')
        assert not result.endswith('"')

    def test_returns_expected_message(self, sample_users_list):
        client = self._make_groq_mock("Ana, invista hoje!")
        result = generate_news(sample_users_list[0], client)
        assert result == "Ana, invista hoje!"

    def test_calls_groq_api_once(self, sample_users_list):
        client = self._make_groq_mock("Mensagem teste")
        generate_news(sample_users_list[0], client)
        client.chat.completions.create.assert_called_once()


class TestTransform:
    def _mock_transform_env(self, message: str):
        """Retorna patches para Groq e GROQ_API_KEY."""
        mock_client  = MagicMock()
        mock_choice  = MagicMock()
        mock_message = MagicMock()
        mock_message.content = message
        mock_choice.message  = mock_message
        mock_client.chat.completions.create.return_value.choices = [mock_choice]
        return mock_client

    def test_transform_adds_news_to_each_user(self, sample_users_list):
        mock_client = self._mock_transform_env("Invista agora!")

        with patch.dict(os.environ, {"GROQ_API_KEY": "fake-key"}):
            with patch("etl.transform.Groq", return_value=mock_client):
                result = transform(sample_users_list)

        for user in result:
            assert len(user["news"]) == 1

    def test_transform_news_has_icon_and_description(self, sample_users_list):
        mock_client = self._mock_transform_env("Invista agora!")

        with patch.dict(os.environ, {"GROQ_API_KEY": "fake-key"}):
            with patch("etl.transform.Groq", return_value=mock_client):
                result = transform(sample_users_list)

        news = result[0]["news"][0]
        assert "icon"        in news
        assert "description" in news
        assert isinstance(news["description"], str)

    def test_transform_raises_without_api_key(self, sample_users_list):
        env = {k: v for k, v in os.environ.items() if k != "GROQ_API_KEY"}
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(EnvironmentError, match="GROQ_API_KEY"):
                transform(sample_users_list)

    def test_transform_continues_on_single_user_error(self, sample_users_list):
        """Se um usuário falhar na geração, os demais devem ser processados."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = [
            Exception("API error"),
            MagicMock(choices=[MagicMock(message=MagicMock(content="Carlos, invista!"))]),
        ]

        with patch.dict(os.environ, {"GROQ_API_KEY": "fake-key"}):
            with patch("etl.transform.Groq", return_value=mock_client):
                result = transform(sample_users_list)

        # Ana falhou (news vazio), Carlos teve sucesso
        assert result[0]["news"] == []
        assert len(result[1]["news"]) == 1
