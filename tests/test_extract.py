"""
Testes da etapa de Extração (Extract).

Cobre:
  - Leitura do CSV
  - fetch_user com resposta 200 e 404
  - extract() orquestrando múltiplos usuários
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from etl.extract import extract, fetch_user, load_user_ids


class TestLoadUserIds:
    def test_reads_ids_from_csv(self, tmp_path):
        csv = tmp_path / "test.csv"
        csv.write_text("UserID\n1\n2\n3\n")
        ids = load_user_ids(csv)
        assert ids == [1, 2, 3]

    def test_returns_list_of_integers(self, tmp_path):
        csv = tmp_path / "test.csv"
        csv.write_text("UserID\n10\n20\n")
        ids = load_user_ids(csv)
        assert all(isinstance(i, int) for i in ids)

    def test_handles_single_id(self, tmp_path):
        csv = tmp_path / "test.csv"
        csv.write_text("UserID\n42\n")
        assert load_user_ids(csv) == [42]


class TestFetchUser:
    def test_returns_user_dict_on_200(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "name": "Ana Paula Ferreira"}

        with patch("etl.extract.requests.get", return_value=mock_response):
            result = fetch_user(1, "http://localhost:8000")

        assert result == {"id": 1, "name": "Ana Paula Ferreira"}

    def test_returns_none_on_404(self):
        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch("etl.extract.requests.get", return_value=mock_response):
            result = fetch_user(999, "http://localhost:8000")

        assert result is None

    def test_returns_none_on_connection_error(self):
        import requests as req
        with patch("etl.extract.requests.get", side_effect=req.RequestException("timeout")):
            result = fetch_user(1, "http://localhost:8000")
        assert result is None


class TestExtract:
    def _make_csv(self, tmp_path, ids):
        csv = tmp_path / "SDW2023.csv"
        content = "UserID\n" + "\n".join(str(i) for i in ids)
        csv.write_text(content)
        return csv

    def test_extract_returns_list_of_users(self, tmp_path, sample_users_list):
        csv = self._make_csv(tmp_path, [1, 2])

        def fake_get(url, **kwargs):
            mock = MagicMock()
            uid = int(url.split("/")[-1])
            match = next((u for u in sample_users_list if u["id"] == uid), None)
            mock.status_code = 200 if match else 404
            mock.json.return_value = match
            return mock

        with patch("etl.extract.requests.get", side_effect=fake_get):
            result = extract(api_url="http://localhost:8000", csv_path=csv)

        assert len(result) == 2
        assert result[0]["name"] == "Ana Paula Ferreira"

    def test_extract_sets_empty_news_field(self, tmp_path, sample_users_list):
        csv = self._make_csv(tmp_path, [1])
        user_without_news = {**sample_users_list[0]}
        user_without_news.pop("news", None)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = user_without_news

        with patch("etl.extract.requests.get", return_value=mock_response):
            result = extract(api_url="http://localhost:8000", csv_path=csv)

        assert "news" in result[0]
        assert result[0]["news"] == []

    def test_extract_skips_missing_users(self, tmp_path):
        csv = self._make_csv(tmp_path, [1, 999])

        def fake_get(url, **kwargs):
            mock = MagicMock()
            uid = int(url.split("/")[-1])
            mock.status_code = 200 if uid == 1 else 404
            mock.json.return_value = {"id": 1, "name": "Ana", "news": []}
            return mock

        with patch("etl.extract.requests.get", side_effect=fake_get):
            result = extract(api_url="http://localhost:8000", csv_path=csv)

        assert len(result) == 1
