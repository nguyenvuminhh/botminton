import hashlib
import hmac
import time
from typing import Optional

from fastapi import APIRouter, HTTPException
from jose import jwt
from pydantic import BaseModel

from config import ADMIN_USER_IDS, BOT_TOKEN, JWT_SECRET

router = APIRouter()
ALGORITHM = "HS256"
TOKEN_EXPIRE_SECONDS = 12 * 3600


class TelegramAuthData(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str


@router.post("/telegram")
def telegram_auth(data: TelegramAuthData):
    payload = data.model_dump(exclude={"hash"})
    check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(payload.items()) if v is not None
    )

    secret = hashlib.sha256(BOT_TOKEN.encode()).digest()
    expected_hash = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_hash, data.hash):
        raise HTTPException(status_code=401, detail="Invalid Telegram auth hash")

    if time.time() - data.auth_date > 86400:
        raise HTTPException(status_code=401, detail="Auth data expired")

    telegram_id = str(data.id)
    if telegram_id not in ADMIN_USER_IDS:
        raise HTTPException(status_code=403, detail="Not an admin")

    token = jwt.encode(
        {"sub": telegram_id, "exp": int(time.time()) + TOKEN_EXPIRE_SECONDS},
        JWT_SECRET,
        algorithm=ALGORITHM,
    )
    return {"access_token": token, "token_type": "bearer"}
