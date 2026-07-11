import random
import time
from typing import TypedDict

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from jose import jwt
from pydantic import BaseModel

from backend.deps import require_admin
from config import ADMIN_USER_ID, BOT_TOKEN, JWT_SECRET
from services.users import get_user, list_admin_users
from utils.user import check_admin, check_super_admin

router = APIRouter()
ALGORITHM = "HS256"
TOKEN_EXPIRE_SECONDS = 12 * 3600
OTP_EXPIRE_SECONDS = 300  # 5 minutes


class OTPChallenge(TypedDict):
    otp: str
    expiry: float


# In-memory OTP store: {telegram_id: {otp, expiry}}
_otp_store: dict[str, OTPChallenge] = {}

# Rate limiting: {ip: [timestamp, ...]}
_request_log: dict[str, list[float]] = {}
_RATE_WINDOW = 60  # seconds
_MAX_REQUESTS = 5  # per window


def _check_rate_limit(ip: str) -> None:
    now = time.time()
    timestamps = [t for t in _request_log.get(ip, []) if now - t < _RATE_WINDOW]
    if len(timestamps) >= _MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Too many requests")
    timestamps.append(now)
    _request_log[ip] = timestamps


def _purge_expired() -> None:
    now = time.time()
    expired = [k for k, v in _otp_store.items() if v["expiry"] < now]
    for k in expired:
        del _otp_store[k]


def _admin_option(
    telegram_id: str,
    telegram_user_name: str | None,
    full_name: str | None,
    is_admin: bool,
) -> dict:
    return {
        "telegram_id": telegram_id,
        "telegram_user_name": telegram_user_name,
        "full_name": full_name,
        "is_admin": is_admin or check_super_admin(telegram_id),
        "is_super_admin": check_super_admin(telegram_id),
    }


def list_admin_login_options() -> list[dict]:
    options: list[dict] = []
    seen: set[str] = set()

    super_admin_id = str(ADMIN_USER_ID)
    super_admin = get_user(super_admin_id)
    if super_admin:
        options.append(
            _admin_option(
                str(super_admin.telegram_id),
                super_admin.telegram_user_name,
                super_admin.full_name,
                True,
            )
        )
    else:
        options.append(_admin_option(super_admin_id, None, "Super admin", True))
    seen.add(super_admin_id)

    for user in list_admin_users():
        telegram_id = str(user.telegram_id)
        if telegram_id in seen:
            continue
        options.append(
            _admin_option(
                telegram_id,
                user.telegram_user_name,
                user.full_name,
                bool(user.is_admin),
            )
        )
        seen.add(telegram_id)

    return options


@router.get("/admins")
def get_login_admins():
    return list_admin_login_options()


@router.get("/me")
def get_me(telegram_id: str = Depends(require_admin)):
    return {
        "telegram_id": telegram_id,
        "is_admin": True,
        "is_super_admin": check_super_admin(telegram_id),
    }


class OTPRequest(BaseModel):
    telegram_id: str


@router.post("/request-otp")
async def request_otp(body: OTPRequest, request: Request):
    _check_rate_limit(request.client.host if request.client else "unknown")
    _purge_expired()

    telegram_id = body.telegram_id.strip()
    if not check_admin(telegram_id):
        raise HTTPException(status_code=403, detail="Not an admin")

    otp = f"{random.SystemRandom().randint(0, 999999):06d}"
    _otp_store[telegram_id] = {
        "otp": otp,
        "expiry": time.time() + OTP_EXPIRE_SECONDS,
    }

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json={
            "chat_id": telegram_id,
            "text": f"Your Botminton login code: *{otp}*\n\nExpires in 5 minutes.",
            "parse_mode": "Markdown",
        })

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to send OTP via Telegram")

    return {"detail": "OTP sent"}


class OTPVerify(BaseModel):
    telegram_id: str
    otp: str


@router.post("/verify-otp")
def verify_otp(body: OTPVerify, request: Request):
    _check_rate_limit(request.client.host if request.client else "unknown")
    _purge_expired()

    telegram_id = body.telegram_id.strip()
    if not check_admin(telegram_id):
        raise HTTPException(status_code=403, detail="Not an admin")

    challenge = _otp_store.get(telegram_id)
    if challenge is None or challenge["otp"] != body.otp or time.time() > challenge["expiry"]:
        if challenge and time.time() > challenge["expiry"]:
            _otp_store.pop(telegram_id, None)
        raise HTTPException(status_code=401, detail="Invalid or expired OTP")

    _otp_store.pop(telegram_id, None)
    token = jwt.encode(
        {"sub": telegram_id, "exp": int(time.time()) + TOKEN_EXPIRE_SECONDS},
        JWT_SECRET,
        algorithm=ALGORITHM,
    )
    return {"access_token": token, "token_type": "bearer"}
