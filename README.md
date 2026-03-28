# Botminton

A Telegram bot for managing badminton sessions — tracking weekly polls, participants, court costs, shuttlecock batches, and billing periods.

## Features

- Weekly YES/NO poll sent to a Telegram group; votes auto-tracked as session participants
- Weighted cost splitting: players with plus-ones pay proportionally more
- Shuttlecock cost split across the billing period by attendance weight
- Admin web dashboard (React + FastAPI) with Telegram OTP login
- Telegram-based logging for warnings and errors

## Stack

- **Bot**: Python, [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- **DB**: MongoDB via MongoEngine ORM
- **API**: FastAPI + Pydantic
- **Frontend**: React 19 + TypeScript + Vite
- **Deployment**: Docker / Heroku Procfile / supervisord

## Setup

```bash
cp example.env .env
# Fill in .env (see below)

pip install -r requirements.txt
python -m botminton
```

### Required environment variables

| Variable | Description |
|---|---|
| `BOT_TOKEN` | Telegram bot token from @BotFather |
| `MONGODB_URI` | MongoDB connection string |
| `DATABASE_NAME` | MongoDB database name |
| `COMMON_GROUP_CHAT_ID` | Telegram group chat ID (polls and summaries posted here) |
| `ADMIN_USER_ID` | Telegram user ID of the admin |
| `JWT_SECRET` | Secret for signing JWTs (`openssl rand -hex 32`) |

Optional: `WEBHOOK_URL`, `WEBHOOK_SECRET`, `WEBHOOK_PORT`, `LOG_GROUP_CHAT_ID`, `API_PORT`, `VITE_BOT_USERNAME`.

See `example.env` for the full list.

## Running tests

```bash
python tests/run_all_tests.py
```

Tests are integration tests — they hit a real MongoDB database (configured via `.env`).

## Admin dashboard

```bash
# Backend
python backend_main.py

# Frontend
cd frontend && npm install && npm run dev
```

## Documentation

- [`markdown/COMMANDS.md`](markdown/COMMANDS.md) — all bot commands
- [`markdown/ADMIN_MANUAL.md`](markdown/ADMIN_MANUAL.md) — admin workflow
- [`markdown/SETUP.md`](markdown/SETUP.md) — deployment guide

## License

MIT
