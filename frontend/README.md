# Botminton Admin Dashboard

A React + TypeScript frontend for the Botminton admin panel — for managing badminton sessions, participants, venues, shuttlecock batches, and billing periods.

## Stack

- React 19 + TypeScript
- Vite
- Telegram OTP-based authentication (no password)

## Setup

```bash
npm install
npm run dev
```

Set `VITE_BOT_USERNAME` in your `.env` (copy from `../example.env`).

## Auth

Login is via Telegram: enter your Telegram username, receive a one-time code from the bot, submit it. JWT is stored in localStorage.
