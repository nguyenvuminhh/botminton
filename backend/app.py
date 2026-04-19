import logging
import os

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from telegram import Update

from backend.auth import router as auth_router
from backend.routes import (
    metadata,
    participants,
    payments,
    periods,
    public,
    sessions,
    shuttlecocks,
    users,
    venues,
)
from config import BOT_TOKEN, WEBHOOK_SECRET, WEBHOOK_URL
from schemas.metadata import Metadata
from schemas.period_shuttlecock_uses import PeriodShuttlecockUses
from schemas.shuttlecock_batches import ShuttlecockBatches
from utils.database import db_manager

logger = logging.getLogger(__name__)


def _backfill_legacy_shuttlecock_batches() -> None:
    """Migrate any ShuttlecockBatch rows that still have a `period` ref but no PeriodShuttlecockUse:
    create a use row consuming the full tube_count, then clear the legacy `period` field.
    Idempotent — safe to run on every startup.
    """
    migrated = 0
    for batch in ShuttlecockBatches.objects(period__ne=None):  # type: ignore
        existing = PeriodShuttlecockUses.objects(batch=batch).first()  # type: ignore
        if existing is None:
            tubes_used = batch.tube_count or 1  # type: ignore
            PeriodShuttlecockUses(period=batch.period, batch=batch, tubes_used=tubes_used).save()  # type: ignore
        batch.period = None  # type: ignore
        batch.save()
        migrated += 1
    if migrated:
        logger.info("Migrated %d legacy shuttlecock batch(es) to PeriodShuttlecockUses", migrated)


def create_app() -> FastAPI:
    app = FastAPI(title="Botminton Admin API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Bot application — only used in webhook mode
    _bot_app = None

    @app.on_event("startup")
    async def startup():
        nonlocal _bot_app
        db_manager.connect()
        Metadata.create()
        _backfill_legacy_shuttlecock_batches()

        if WEBHOOK_URL:
            from bot_app import build_application
            _bot_app = build_application()
            await _bot_app.initialize()
            await _bot_app.start()
            webhook_url = f"{WEBHOOK_URL.rstrip('/')}/{BOT_TOKEN}"
            await _bot_app.bot.set_webhook(url=webhook_url, secret_token=WEBHOOK_SECRET or None)
            logger.info("Webhook registered: %s", webhook_url)

    @app.on_event("shutdown")
    async def shutdown():
        if _bot_app:
            await _bot_app.stop()
            await _bot_app.shutdown()
        db_manager.disconnect()

    if WEBHOOK_URL:
        @app.post(f"/{BOT_TOKEN}", include_in_schema=False)
        async def telegram_webhook(
            request: Request,
            x_telegram_bot_api_secret_token: str | None = Header(default=None),
        ):
            if WEBHOOK_SECRET and x_telegram_bot_api_secret_token != WEBHOOK_SECRET:
                raise HTTPException(status_code=403, detail="Invalid secret token")
            if _bot_app is None:
                raise HTTPException(status_code=503, detail="Bot not ready")
            data = await request.json()
            update = Update.de_json(data, _bot_app.bot)
            await _bot_app.process_update(update)
            return {"ok": True}

    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    app.include_router(users.router, prefix="/api/users", tags=["users"])
    app.include_router(periods.router, prefix="/api/periods", tags=["periods"])
    app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
    app.include_router(participants.router, prefix="/api/participants", tags=["participants"])
    app.include_router(venues.router, prefix="/api/venues", tags=["venues"])
    app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
    app.include_router(shuttlecocks.router, prefix="/api/shuttlecocks", tags=["shuttlecocks"])
    app.include_router(metadata.router, prefix="/api/metadata", tags=["metadata"])
    app.include_router(public.router, prefix="/api/public", tags=["public"])

    # Serve React build in production
    frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
    if os.path.isdir(frontend_dist):
        from fastapi.responses import FileResponse

        app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

        @app.get("/{full_path:path}", include_in_schema=False)
        async def spa_fallback(full_path: str):
            return FileResponse(os.path.join(frontend_dist, "index.html"))

    return app
