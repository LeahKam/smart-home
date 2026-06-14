# Smart Home Agent

A FastAPI service that answers questions about smart home devices using natural language. It translates user queries into SQL, runs them against the database, and returns AI-generated answers in Hebrew.

## Quick Start

```bash
cp .env.example .env
uv run uvicorn main:app --reload --port 8050
```

## API

- `GET /` – health check
- `POST /api/chat` – ask a question about your smart home

## Stack

FastAPI, OpenAI, SQLite
