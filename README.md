# FastAPI-todo-Telegram-Bot

An asynchronous, production-ready Telegram client for personal goal and task management, built strictly on **Clean Architecture** principles. This repository serves as the presentation and UI layer for the entire TaskFlow ecosystem, interacting with the **FastAPI-todo-API** backend via a custom fault-tolerant REST client and a secure Silent S2S (Service-to-Server) protocol.

> 💡 **Ecosystem Architecture Note:** While this repository operates as an autonomous UI client, its root `docker-compose.yml` acts as the primary orchestrator for the entire ecosystem. It is configured to automatically pull and build the neighboring backend repository (`FastAPI-todo-API`) for seamless full-stack deployment.

## 🛠️ Tech Stack & Metrics

- **Presentation Runtime:** Python 3.12+ (Type Hinting on Core Layers, OOP)
- **Telegram Framework:** [aiogram 3.28+](https://github.com/aiogram/aiogram) (FSM, Custom Middlewares, Routers, Error Events)
- **Network & Data Integrity:** HTTPX (Async Client), Pydantic v2, Pydantic Settings v2
- **Caching Layer:** Redis 7 (Asynchronous JWT token session storage via `aioredis`)
- **Quality Assurance:** Pytest, pytest-asyncio, pytest-cov (**Total Test Coverage: 90%**)
- **Orchestration:** Docker & Docker Compose (Multi-container setup with healthcheck propagation)

---

## 🏗️ Architectural Design Patterns

### 1. Clean Architecture (Separation of Concerns)

The codebase strictly decouples business logic from external delivery frameworks:

- **Domain Layer (`src/schemas`, `src/states`):** Pure Pydantic validation models and FSM schemas. All UI presentation logic (HTML card rendering, status-to-emoji mapping, localized date formatting) is encapsulated directly inside the domain DTOs (`TaskResponse`, `TaskStatsResponse`), keeping handlers thin.
- **Service Layer (`src/services`):** Dedicated boundary for business use cases. Inherits from an abstract `BaseClient` gateway which encapsulates cross-cutting HTTP concerns, global network error mapping (e.g., 404 -> `ResourceNotFoundError`), and automated API session handling.
- **Presentation Layer (`src/handlers`):** Thin controller-routers. Handlers remain completely decoupled from underlying network implementations, executing actions via injected services.

### 2. UI Paradigm: Hybrid Single Message UI

To eliminate excessive chat pollution while maintaining transactional readability, the system uses a **Hybrid "Canvas"** concept.

- Core interactive flows (list paginations, details viewing, field updates) happen inside a single volatile canvas message via inline markup updates (`edit_text` / `edit_message_reply_markup`).
- Text entry states instantly purge raw user keystrokes via `message.delete()`.
- System milestones (such as creation initializations or cancellation triggers) append explicit fallback notifications to the chat feed to preserve context history.

### 3. Silent S2S Auth Pattern

A secure, transparent cross-service authorization flow is embedded directly into the network pipeline:

- A custom `AuthMiddleware` intercepts incoming updates, isolates the Telegram user context, and passes it to the `AuthService`.
- If a valid JWT token is missing from the Redis cache or its TTL (`TOKEN_TTL_SEC`) has expired, the service silently resolves authorization by dispatching an internal request to the `/login/telegram` backend route, validated via an `X-Internal-Secret` header.
- The fresh token is cached back into Redis and injected into the handler data context transparently.

### 4. Centralized Global Exception Handling

System-wide networking and business logic failures are managed at the core router level utilizing `errors_router.errors()` middleware:

- Differentiates exceptions and dynamically maps them to clear, localized UI error indicators.
- Provides structured logging of error frames along with active session context parameters (`chat_id`, `user_id`, stack traces).
- Mitigates memory locks by automatically wiping active FSM states on fatal errors (e.g., `NotAuthorizedError`).

---

## 📂 Project Structure

- **src/core/** — Settings parsing and centralized application exceptions.
- **src/storage/** — Redis-backed low-level auth caching engine (`TokenStorage`).
- **src/states/** — Declarative FSM tracking structures.
- **src/schemas/** — Pydantic DTO validation matrices, callback data schemas, and HTML text binders.
- **src/services/** — Network-isolated gateway API interfaces (`TaskService`, `AuthService`).
- **src/middlewares/** — Pipeline lifecycle interceptors (`AuthMiddleware`, `CallBackMessageMiddleware`).
- **src/keyboards/** — Factory components for inline canvas building.
- **src/handlers/** — Abstract message routers and conversational flows.
- **src/main.py** — Application bootstrapping entry point, lifecycle management, and DI registration.
- **tests/** — High-fidelity suite isolating network targets and state trackers.

---

## 🚀 Quick Start (Full-Stack Orchestration)

This repository serves as the orchestration hub for the full ecosystem, deploying the bot, the backend API, a PostgreSQL container, and a Redis cache.

### 1. Repository Workspace Setup

Ensure that both the backend repository (`FastAPI-todo-API`) and this client repository (`FastAPI-todo-Telegram-Bot`) are cloned into the same parent folder level:

```text
├── FastAPI-todo-API/           # Backend microservice
└── FastAPI-todo-Telegram-Bot/  # This repository (Telegram client UI)
```

In the root directory of this bot repository, duplicate the environment layout file:

```bash
cp .env.example .env
```

### 2. Configuration Settings

Fill out the required `.env` keys. Example setup:

```ini
# PostgreSQL Setup
DB_USER=postgres
DB_PASSWORD=your_secure_postgres_pass
DB_NAME=taskflow_db

# Client Ecosystem & S2S Authorization
BOT_TOKEN=1234567890:ABCdefGhIJK...
INTERNAL_BOT_SECRET=your_super_secret_s2s_validation_key
TOKEN_TTL_SEC=3600
```

### 3. Multi-Container Orchestration

Spin up all services in their strict dependency order using a single execution flag from the `FastAPI-todo-Telegram-Bot` directory:

```bash
docker compose up -d --build
```

_Deployment sequence:_ `db` (starts healthcheck validation) -> `redis` (checks connection health) -> `api` (applies Alembic head migrations and mounts server) -> `bot` (starts processing long-polling updates).

---

## 🧪 QA Testing Framework

Run the service and base client isolation metrics:

```bash
pytest
```

Verify the coverage percentage logs:

```bash
pytest --cov=src --cov-report=term-missing
```

Developed by [vintikzq](https://github.com/vintikzq)
