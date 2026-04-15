"""
Testes da etapa de Carregamento (Load).

Cobre:
  - update_user com resposta 200 e falha
  - load() orquestrando múltiplos usuários
  - Contagem correta de sucessos e falhas
"""

from unittest.mock import MagicMock, patch

import pytest

from etl.load import load, update_user

ICON_URL = (
    "https://digitalinnovationone.github.io"
    "/santander-dev-week-2023-api/icons/credit.svg"
)


def _make_user(uid: int, name: str, news: list = None):
    return {
        "id":      uid,
        "name":    name,
        "account": {"balance": 1000.0},
        "news":    news or [{"icon": ICON_URL, "description": f"Invista, {name.split()[0]}!"}],
    }


class TestUpdateUser:
    def test_returns_true_on_200(self):
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("etl.load.requests.put", return_value=mock_response):
            result = update_user(_make_user(1, "Ana Paula"), "http://localhost:8000")

        assert result is True

    def test_returns_false_on_500(self):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        with patch("etl.load.requests.put", return_value=mock_response):
            result = update_user(_make_user(1, "Ana Paula"), "http://localhost:8000")

        assert result is False

    def test_returns_false_on_connection_error(self):
        import requests as req
        with patch("etl.load.requests.put", side_effect=req.RequestException("timeout")):
            result = update_user(_make_user(1, "Ana Paula"), "http://localhost:8000")
        assert result is False

    def test_payload_contains_only_news(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        captured = {}

        def fake_put(url, json, **kwargs):
            captured["payload"] = json
            return mock_response

        with patch("etl.load.requests.put", side_effect=fake_put):
            update_user(_make_user(1, "Ana Paula"), "http://localhost:8000")

        assert "news" in captured["payload"]
        assert list(captured["payload"].keys()) == ["news"]

    def test_payload_news_has_correct_fields(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        captured = {}

        def fake_put(url, json, **kwargs):
            captured["payload"] = json
            return mock_response

        user = _make_user(1, "Ana Paula")
        with patch("etl.load.requests.put", side_effect=fake_put):
            update_user(user, "http://localhost:8000")

        news_item = captured["payload"]["news"][0]
        assert "icon"        in news_item
        assert "description" in news_item


class TestLoad:
    def test_all_success_returns_correct_count(self):
        users = [_make_user(i, f"User {i}") for i in range(1, 4)]
        mock_response = MagicMock(status_code=200)

        with patch("etl.load.requests.put", return_value=mock_response):
            result = load(users, "http://localhost:8000")

        assert result["success"] == 3
        assert result["failure"] == 0

    def test_all_failure_returns_correct_count(self):
        users = [_make_user(i, f"User {i}") for i in range(1, 3)]
        mock_response = MagicMock(status_code=500, text="Error")

        with patch("etl.load.requests.put", return_value=mock_response):
            result = load(users, "http://localhost:8000")

        assert result["success"] == 0
        assert result["failure"] == 2

    def test_partial_failure_counted_correctly(self):
        users = [_make_user(1, "Ana Paula"), _make_user(2, "Carlos")]
        responses = [MagicMock(status_code=200), MagicMock(status_code=500, text="err")]

        with patch("etl.load.requests.put", side_effect=responses):
            result = load(users, "http://localhost:8000")

        assert result["success"] == 1
        assert result["failure"] == 1

    def test_empty_users_list(self):
        result = load([], "http://localhost:8000")
        assert result == {"success": 0, "failure": 0}
