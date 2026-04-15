"""
Testes dos endpoints da API local (FastAPI + SQLite).

Cobre:
  - GET /users/{id}   → usuário existente, inexistente
  - PUT /users/{id}   → atualização de news, usuário inexistente
  - GET /             → health check
"""


class TestHealthCheck:
    def test_health_check_returns_ok(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestGetUser:
    def test_get_existing_user_returns_200(self, client, sample_user):
        response = client.get("/users/1")
        assert response.status_code == 200

    def test_get_existing_user_returns_correct_data(self, client, sample_user):
        data = client.get("/users/1").json()
        assert data["id"]   == 1
        assert data["name"] == "Ana Paula Ferreira"

    def test_get_existing_user_has_account(self, client, sample_user):
        data = client.get("/users/1").json()
        assert data["account"]["balance"] == 2500.0
        assert data["account"]["agency"]  == "0001"

    def test_get_existing_user_has_card(self, client, sample_user):
        data = client.get("/users/1").json()
        assert data["card"]["limit"] == 5000.0

    def test_get_existing_user_news_starts_empty(self, client, sample_user):
        data = client.get("/users/1").json()
        assert data["news"] == []

    def test_get_nonexistent_user_returns_404(self, client):
        response = client.get("/users/999")
        assert response.status_code == 404

    def test_get_nonexistent_user_returns_detail(self, client):
        response = client.get("/users/999")
        assert "não encontrado" in response.json()["detail"]


class TestUpdateUser:
    def test_put_user_adds_news(self, client, sample_user):
        payload = {"news": [{"icon": "https://example.com/icon.svg", "description": "Invista hoje!"}]}
        response = client.put("/users/1", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert len(data["news"]) == 1
        assert data["news"][0]["description"] == "Invista hoje!"

    def test_put_user_appends_multiple_news(self, client, sample_user):
        payload = {
            "news": [
                {"icon": "https://example.com/icon.svg", "description": "Mensagem 1"},
                {"icon": "https://example.com/icon.svg", "description": "Mensagem 2"},
            ]
        }
        response = client.put("/users/1", json=payload)
        assert response.status_code == 200
        assert len(response.json()["news"]) == 2

    def test_put_user_preserves_name(self, client, sample_user):
        payload = {"news": [{"icon": "https://example.com/icon.svg", "description": "Test"}]}
        data = client.put("/users/1", json=payload).json()
        assert data["name"] == "Ana Paula Ferreira"

    def test_put_user_updates_name(self, client, sample_user):
        payload = {"name": "Ana P. Ferreira"}
        data = client.put("/users/1", json=payload).json()
        assert data["name"] == "Ana P. Ferreira"

    def test_put_nonexistent_user_returns_404(self, client):
        payload = {"news": [{"icon": "https://example.com/icon.svg", "description": "Test"}]}
        response = client.put("/users/999", json=payload)
        assert response.status_code == 404

    def test_put_empty_payload_returns_200(self, client, sample_user):
        response = client.put("/users/1", json={})
        assert response.status_code == 200
