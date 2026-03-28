from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.deps import require_admin
from schemas.users import Users
from services.users import (
    delete_user,
    get_user,
    list_all_users,
    update_user,
)

router = APIRouter()


def serialize(u: Users) -> dict:
    return {
        "id": str(u.id),
        "telegram_id": u.telegram_id,
        "telegram_user_name": u.telegram_user_name,
        "is_admin": u.is_admin,
    }


class UpdateUserBody(BaseModel):
    telegram_user_name: str | None = None
    is_admin: bool | None = None


@router.get("")
def get_users(_: str = Depends(require_admin)):
    return [serialize(u) for u in list_all_users()]


@router.get("/{telegram_id}")
def get_user_by_id(telegram_id: str, _: str = Depends(require_admin)):
    u = get_user(telegram_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return serialize(u)


@router.put("/{telegram_id}")
def edit_user(telegram_id: str, body: UpdateUserBody, _: str = Depends(require_admin)):
    kwargs = {k: v for k, v in body.model_dump().items() if v is not None}
    u = update_user(telegram_id, **kwargs)
    if not u:
        raise HTTPException(status_code=404, detail="User not found or update failed")
    return serialize(u)


@router.delete("/{telegram_id}", status_code=204)
def remove_user(telegram_id: str, _: str = Depends(require_admin)):
    if not delete_user(telegram_id):
        raise HTTPException(status_code=404, detail="User not found")
