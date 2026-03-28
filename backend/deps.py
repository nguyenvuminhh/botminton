from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from config import ADMIN_USER_IDS, JWT_SECRET

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
    if telegram_id not in ADMIN_USER_IDS:
        raise HTTPException(status_code=403, detail="Not an admin")
    return telegram_id
