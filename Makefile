# ══════════════════════════════════════════════════════════════
#  Santander Dev Week 2023 — ETL com Python & IA Generativa
#  Makefile — Automatiza instalação, seed, API e pipeline
# ══════════════════════════════════════════════════════════════

.PHONY: help install seed run-api run-etl run-all reset test

# Exibe os comandos disponíveis (padrão ao rodar apenas 'make')
help:
	@echo ""
	@echo "  ╔══════════════════════════════════════════════════╗"
	@echo "  ║   Santander Dev Week 2023 — ETL Python           ║"
	@echo "  ╚══════════════════════════════════════════════════╝"
	@echo ""
	@echo "  Comandos disponíveis:"
	@echo ""
	@echo "    make test       Executa todos os testes (pytest)"
	@echo "    make install    Instala as dependências do projeto"
	@echo "    make seed       Popula o banco de dados com usuários sintéticos"
	@echo "    make run-api    Sobe a API local (FastAPI) na porta 8000"
	@echo "    make run-etl    Executa o pipeline ETL completo"
	@echo "    make run-all    Seed + API em background + ETL (tudo de uma vez)"
	@echo "    make reset      Remove o banco de dados (útil para re-seed)"
	@echo ""
	@echo "  Pré-requisito: copie .env.example para .env e preencha GROQ_API_KEY"
	@echo ""

# Instala dependências via pip
install:
	@echo "📦 Instalando dependências..."
	pip install -r requirements.txt
	@echo "✅ Dependências instaladas."

# Popula o banco SQLite com os usuários sintéticos
seed:
	@echo "🌱 Executando seed do banco de dados..."
	python data/seed.py

# Sobe a API FastAPI em modo desenvolvimento (hot-reload)
run-api:
	@echo "🚀 Subindo API local em http://localhost:8000 ..."
	@echo "   Documentação: http://localhost:8000/docs"
	uvicorn api.main:app --reload --port 8000

# Executa o pipeline ETL completo
run-etl:
	@echo "⚙️  Executando pipeline ETL..."
	python main.py

# Sobe a API em background e roda o ETL em sequência
run-all:
	@echo "🔄 Iniciando seed + API + ETL..."
	python data/seed.py
	uvicorn api.main:app --port 8000 &
	@sleep 2
	python main.py

# Executa todos os testes com pytest
test:
	@echo "🧪 Executando testes..."
	python -m pytest tests/ -v
	@echo "✅ Testes concluídos."

# Remove o banco de dados para permitir re-seed limpo
reset:
	@echo "🗑️  Removendo banco de dados..."
	rm -f sdw2023.db
	@echo "✅ Banco removido. Execute 'make seed' para recriar."
