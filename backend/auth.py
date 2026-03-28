import random
import time

import httpx
from fastapi import APIRouter, HTTPException
from jose import jwt
from pydantic import BaseModel

from config import ADMIN_USER_ID, BOT_TOKEN, JWT_SECRET

router = APIRouter()
ALGORITHM = "HS256"
TOKEN_EXPIRE_SECONDS = 12 * 3600
OTP_EXPIRE_SECONDS = 300  # 5 minutes

# In-memory OTP store: {otp: expiry_timestamp}
_otp_store: dict[str, float] = {}


def _purge_expired() -> None:
    now = time.time()
    expired = [k for k, v in _otp_store.items() if v < now]
    for k in expired:
        del _otp_store[k]


@router.post("/request-otp")
async def request_otp():
    _purge_expired()

    otp = f"{random.SystemRandom().randint(0, 999999):06d}"
    _otp_store[otp] = time.time() + OTP_EXPIRE_SECONDS

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json={
            "chat_id": ADMIN_USER_ID,
            "text": f"Your Botminton login code: *{otp}*\n\nExpires in 5 minutes.",
            "parse_mode": "Markdown",
        })

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to send OTP via Telegram")

    return {"detail": "OTP sent"}


class OTPVerify(BaseModel):
    otp: str


@router.post("/verify-otp")
def verify_otp(body: OTPVerify):
    _purge_expired()

    expiry = _otp_store.pop(body.otp, None)
    if expiry is None or time.time() > expiry:
        raise HTTPException(status_code=401, detail="Invalid or expired OTP")

    token = jwt.encode(
        {"sub": ADMIN_USER_ID, "exp": int(time.time()) + TOKEN_EXPIRE_SECONDS},
        JWT_SECRET,
        algorithm=ALGORITHM,
    )
    return {"access_token": token, "token_type": "bearer"}
