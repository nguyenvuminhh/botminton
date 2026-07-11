from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from config import JWT_SECRET
from utils.user import check_admin, check_super_admin

bearer = HTTPBearer()
ALGORITHM = "HS256"


def require_admin(
    creds: HTTPAuthorizationCredentials = Security(bearer),
) -> str:
    try:
        payload = jwt.decode(creds.credentials, JWT_SECRET, algorithms=[ALGORITHM])
        telegram_id: str = payload["sub"]
    except (JWTError, KeyError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if not check_admin(telegram_id):
        raise HTTPException(status_code=403, detail="Not an admin")
    return telegram_id


def require_super_admin(
    creds: HTTPAuthorizationCredentials = Security(bearer),
) -> str:
    telegram_id = require_admin(creds)
    if not check_super_admin(telegram_id):
        raise HTTPException(status_code=403, detail="Not a super admin")
    return telegram_id
