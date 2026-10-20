# ✅ Tasks API

![CI](https://github.com/medreda091/fastapi-tasks-api/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192?style=flat-square&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat-square&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

A production-style **REST API for task management** built with **FastAPI**, featuring **JWT authentication**, per-user data isolation, and a full test suite. Ships with **Docker** and **PostgreSQL** via Compose, plus a **CI pipeline** running pytest on every push.

## ✨ Features

- 🔐 **JWT authentication** — register, login, bearer-token protected routes (OAuth2 password flow)
- 🧑‍💻 **Per-user isolation** — users can only see and mutate their own tasks
- 📝 **Full task CRUD** — create, list (with filters + pagination), read, update, delete
- 🗄️ **SQLAlchemy 2.0** — PostgreSQL in production, SQLite fallback for local dev/tests
- ✅ **Tested** — 25+ pytest tests with an isolated in-memory database
- 🐳 **Dockerized** — one-command stack (`docker compose up`) with PostgreSQL 16
- 📚 **Auto-generated docs** — interactive Swagger UI at `/docs`, ReDoc at `/redoc`

## 🚀 Quickstart

### With Docker (recommended)

```bash
cp .env.example .env   # then set a strong SECRET_KEY
docker compose up --build
```

The API is available at **http://localhost:8000** — open **http://localhost:8000/docs** for the interactive Swagger UI.

### Local (SQLite)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Run the tests

```bash
pytest -v
```

## 🔌 API Endpoints

| Method | Route | Description | Auth |
|---|---|---|---|
| `POST` | `/auth/register` | Register a new user | ❌ |
| `POST` | `/auth/login` | Login, receive a JWT bearer token | ❌ |
| `GET` | `/users/me` | Get the current user's profile | ✅ |
| `POST` | `/tasks/` | Create a task | ✅ |
| `GET` | `/tasks/` | List own tasks (`?done=`, `?skip=`, `?limit=`) | ✅ |
| `GET` | `/tasks/{id}` | Get a single task | ✅ |
| `PUT` | `/tasks/{id}` | Update a task (partial supported) | ✅ |
| `DELETE` | `/tasks/{id}` | Delete a task | ✅ |
| `GET` | `/health` | Health check | ❌ |

### Example

```bash
# Register & login
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"supersecret1"}'

TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -d "username=demo@example.com&password=supersecret1" | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# Create a task
curl -X POST http://localhost:8000/tasks/ \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"title":"Ship the portfolio","description":"Push to GitHub"}'
```

## 🗂️ Project Structure

```
fastapi-tasks-api/
├── app/
│   ├── main.py            # FastAPI app, lifespan, router wiring
│   ├── database.py        # SQLAlchemy engine (DATABASE_URL, SQLite fallback)
│   ├── models.py          # User & Task ORM models
│   ├── schemas.py         # Pydantic v2 request/response schemas
│   ├── auth.py            # Password hashing, JWT creation, get_current_user
│   └── routers/
│       ├── users.py       # /auth/register, /auth/login, /users/me
│       └── tasks.py       # Task CRUD, JWT-protected, per-user scoped
├── tests/
│   ├── conftest.py        # Isolated in-memory DB + TestClient fixtures
│   ├── test_auth.py       # Registration, login, auth edge cases
│   └── test_tasks.py      # CRUD, filters, per-user isolation
├── .github/workflows/ci.yml  # CI: install deps + pytest on push/PR
├── Dockerfile
├── docker-compose.yml     # api + postgres:16
├── .env.example
└── requirements.txt
```

## ⚙️ Configuration

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `dev-secret-key-change-me` | JWT signing key — **set a strong one in production** |
| `DATABASE_URL` | `sqlite:///./tasks.db` | SQLAlchemy URL (PostgreSQL in Compose) |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | `tasks` / `tasks` / `tasksdb` | Compose Postgres credentials |

## 📄 License

MIT © 2026 Reda Ait Smouguen
