# 🏦 Santander Dev Week 2023 — ETL com Python & IA Generativa

> Reimplementação completa em Python do desafio original da **Santander Dev Week 2023**.  
> A API Java (Spring Boot + Railway) foi substituída por uma stack moderna em **FastAPI + SQLite**, e o modelo **GPT-4 (OpenAI)** foi trocado pelo **Llama-3 70B via Groq API** — gratuito e de alto desempenho.

---

## 📐 Arquitetura

```
SDW2023.csv
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│                    PIPELINE ETL                         │
│                                                         │
│  📥 EXTRACT      📊 TRANSFORM       📤 LOAD            │
│  Lê IDs CSV  →  Groq / Llama-3  →  PUT /users/{id}    │
│  GET /users/{id}  Gera mensagens   Persiste na API     │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────┐
│  FastAPI + SQLite   │  ← API local (substitui Spring Boot + Railway)
│  GET /users/{id}    │
│  PUT /users/{id}    │
└─────────────────────┘
```

## 🔄 Comparativo com o Projeto Original

| Componente | Original (DIO) | Esta versão |
|---|---|---|
| API Backend | Java 17 + Spring Boot 3 | **FastAPI + SQLite** |
| Deploy | Railway (descontinuado) | **Local + pronto para deploy** |
| IA Generativa | OpenAI GPT-4 (pago) | **Groq + Llama-3 70B (gratuito)** |
| Execução | Jupyter Notebook | **Pipeline modular em Python** |
| Dados | API externa (indisponível) | **Seed local + CSV** |

---

## 🗂️ Estrutura do Projeto

```
santander-dev-week-etl-python/
│
├── README.md
├── .env.example            # Template de variáveis de ambiente
├── .gitignore
├── Makefile                # Automatiza todos os comandos
├── requirements.txt
│
├── data/
│   ├── SDW2023.csv         # Fonte: lista de IDs dos usuários
│   └── seed.py             # Popula o banco com dados sintéticos
│
├── api/                    # API local (substitui a API Java)
│   ├── main.py             # Endpoints FastAPI (GET e PUT /users/{id})
│   ├── models.py           # ORM SQLAlchemy + Schemas Pydantic
│   └── database.py         # Configuração SQLite + sessão
│
├── etl/                    # Pipeline ETL modularizado
│   ├── extract.py          # Lê CSV → consulta API
│   ├── transform.py        # Integração Groq (Llama-3 70B)
│   └── load.py             # PUT de volta na API
│
├── main.py                 # Orquestrador do pipeline completo
│
└── notebooks/
    └── exploratory.ipynb   # Versão notebook (referência ao desafio original)
```

---

## 🚀 Como Executar

### 1. Clone o repositório

```bash
git clone https://github.com/PedroLuizskt/santander-dev-week-etl-python.git
cd santander-dev-week-etl-python
```

### 2. Configure as variáveis de ambiente

```bash
cp .env.example .env
# Abra o .env e preencha sua GROQ_API_KEY
# Obtenha a chave gratuita em: https://console.groq.com/keys
```

### 3. Instale as dependências

```bash
make install
```

### 4. Popule o banco de dados

```bash
make seed
```

### 5. Suba a API local

```bash
make run-api
# API disponível em http://localhost:8000
# Documentação Swagger: http://localhost:8000/docs
```

### 6. Execute o pipeline ETL

Em outro terminal:

```bash
make run-etl
```

---

## 🤖 Exemplo de Output do Pipeline

```
09:12:01  INFO     ═══════════════════════════════════════════════════
09:12:01  INFO       🚀  Pipeline ETL — Santander Dev Week 2023
09:12:01  INFO     ═══════════════════════════════════════════════════

09:12:01  INFO     📥  [1/3] EXTRACT — Buscando usuários na API...
09:12:01  INFO     [Extract] ✅ Usuário extraído: Ana Paula Ferreira (id=1)
09:12:01  INFO     [Extract] ✅ Usuário extraído: Carlos Eduardo Santos (id=2)
...

09:12:02  INFO     🤖  [2/3] TRANSFORM — Gerando mensagens com Llama-3 (Groq)...
09:12:03  INFO     [Transform] ✅ Ana Paula: "Ana, seu saldo pode render mais! Invista agora."
09:12:04  INFO     [Transform] ✅ Carlos: "Carlos, cada real investido constrói seu futuro!"
...

09:12:05  INFO     📤  [3/3] LOAD — Persistindo mensagens na API...
09:12:05  INFO     [Load] ✅ Ana Paula Ferreira atualizado com sucesso.
...

09:12:05  INFO     ═══════════════════════════════════════════════════
09:12:05  INFO       ✅  Pipeline concluído!
09:12:05  INFO           Atualizados : 5
09:12:05  INFO           Falhas      : 0
09:12:05  INFO     ═══════════════════════════════════════════════════
```

---

## 🛠️ Tecnologias

- **[FastAPI](https://fastapi.tiangolo.com/)** — API REST moderna e performática
- **[SQLAlchemy](https://www.sqlalchemy.org/)** — ORM para banco de dados
- **[SQLite](https://www.sqlite.org/)** — Banco de dados embutido (zero configuração)
- **[Groq API](https://console.groq.com/)** — Inferência de LLM ultrarrápida
- **[Llama-3 70B](https://ai.meta.com/blog/meta-llama-3/)** — Modelo de linguagem open source
- **[Pandas](https://pandas.pydata.org/)** — Manipulação de dados tabulares
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** — Gestão de variáveis de ambiente

---

## 📚 Contexto

Este projeto é uma resposta ao desafio da **[Santander Dev Week 2023](https://github.com/falvojr/santander-dev-week-2023)** da [DIO](https://www.dio.me/). Como a API Java original foi descontinuada no Railway, toda a infraestrutura foi reimplementada em Python, mantendo o mesmo domínio de dados e fluxo ETL, porém com stack mais moderna e acessível.

---

## 👤 Autor

**Pedro Luiz R. Vaz de Melo**  
Engenheiro Florestal | Cientista de Dados | Desenvolvedor GIS  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue?logo=linkedin)](https://linkedin.com/in/seu-perfil)
[![GitHub](https://img.shields.io/badge/GitHub-black?logo=github)](https://github.com/PedroLuizskt)
