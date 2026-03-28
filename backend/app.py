import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.auth import router as auth_router
from backend.routes import (
    participants,
    payments,
    periods,
    sessions,
    shuttlecocks,
    users,
    venues,
)
from utils.database import db_manager


def create_app() -> FastAPI:
    app = FastAPI(title="Botminton Admin API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def startup():
        db_manager.connect()

    @app.on_event("shutdown")
    def shutdown():
        db_manager.disconnect()

    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    app.include_router(users.router, prefix="/api/users", tags=["users"])
    app.include_router(periods.router, prefix="/api/periods", tags=["periods"])
    app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
    app.include_router(participants.router, prefix="/api/participants", tags=["participants"])
    app.include_router(venues.router, prefix="/api/venues", tags=["venues"])
    app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
    app.include_router(shuttlecocks.router, prefix="/api/shuttlecocks", tags=["shuttlecocks"])

    # Serve React build in production
    frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
    if os.path.isdir(frontend_dist):
        app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")

    return app
