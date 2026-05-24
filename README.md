# TaskFlow Telegram Bot

A Telegram bot client for the TaskFlow task manager. Acts as the user-facing UI for the [FastAPI-todo-API](https://github.com/vintikzq/FastAPI-todo-API) backend.

This repository also contains the `docker-compose.yml` that brings up the full stack (bot + API + PostgreSQL + Redis) in a single command.

## Features

- **Task management:** create, view, edit, and delete personal tasks via inline keyboards.
- **FSM-based forms:** multi-step task creation with name, description, priority, and a calendar-picker deadline.
- **Pagination:** paginated task list with separate "active" and "archive" views.
- **Single-message UI:** task list and details are rendered by editing the same message instead of spamming the chat.
- **Transparent auth:** the bot authenticates with the backend on behalf of the Telegram user via an internal secret. JWT tokens are cached in Redis with a TTL.
- **Centralized error handling:** API errors (404, 422, 5xx, connection issues) are mapped to user-friendly messages by a global aiogram error router.

## Tech Stack

- **Language:** Python 3.12+
- **Framework:** [aiogram 3.x](https://github.com/aiogram/aiogram) (FSM, middlewares, routers)
- **HTTP client:** [HTTPX](https://www.python-httpx.org/) (async)
- **Cache:** Redis 7 (via `redis.asyncio`) — JWT token storage
- **Validation:** Pydantic v2, Pydantic Settings v2
- **Testing:** Pytest, pytest-asyncio, pytest-cov (~90% coverage)
- **Containerization:** Docker & Docker Compose

## Project Structure

- **src/core/** — settings and custom exceptions.
- **src/storage/** — Redis-based token storage.
- **src/states/** — aiogram FSM state declarations.
- **src/schemas/** — Pydantic models, callback data, and enums.
- **src/services/** — API client classes (`TaskService`, `AuthService`) built on a shared `BaseClient`.
- **src/middlewares/** — aiogram middlewares for auth and callback message extraction.
- **src/keyboards/** — inline keyboard builders.
- **src/handlers/** — message and callback handlers (commands, task CRUD flows, error handler).
- **src/main.py** — entry point and dependency wiring.
- **tests/** — unit tests with mocked HTTP session and Redis.

## Quick Start (Full Stack)

This repository's `docker-compose.yml` runs the bot, the API, PostgreSQL, and Redis together.

### 1. Clone both repositories

Both repositories must live next to each other:

```text
├── FastAPI-todo-API/
└── FastAPI-todo-Telegram-Bot/
```

```bash
git clone https://github.com/vintikzq/FastAPI-todo-API.git
git clone https://github.com/vintikzq/FastAPI-todo-Telegram-Bot.git
cd FastAPI-todo-Telegram-Bot
```

In the root directory of this bot repository, duplicate the environment layout file:

```bash
cp .env.example .env
```

### 2. Configuration Settings

Fill out the required `.env` keys. Example setup:

```ini
# PostgreSQL
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=tasks

# Bot
BOT_TOKEN=1234567890:ABCdefGhIJK...     # from @BotFather
INTERNAL_BOT_SECRET=shared_secret       # must match the API
TOKEN_TTL_SEC=3600
```

### 3. Run

```bash
docker compose up -d --build
```

Startup order: `db` → `redis` → `api` (runs Alembic migrations) → `bot` (starts long-polling).

---

## Testing

Run the test suite:

```bash
pytest
```

With coverage report:

```bash
pytest --cov=src --cov-report=term-missing
```

Developed by [vintikzq](https://github.com/vintikzq)
