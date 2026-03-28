from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.deps import require_admin
from schemas.sessions import Sessions
from services.sessions import (
    create_session,
    delete_session,
    get_current_session,
    get_open_session,
    get_session,
    list_sessions_by_period,
    update_session,
)

router = APIRouter()


def serialize(s: Sessions) -> dict:
    return {
        "id": str(s.id),
        "date": s.date.isoformat() if s.date else None,
        "period_id": str(s.period.id) if s.period else None,
        "period_start_date": s.period.start_date.isoformat() if s.period and s.period.start_date else None,
        "venue_name": s.venue.name if s.venue else None,
        "slots": s.slots,
        "is_poll_open": s.is_poll_open,
        "telegram_poll_message_id": s.telegram_poll_message_id,
    }


class CreateSessionBody(BaseModel):
    date: str
    period_id: str
    venue_id: Optional[str] = None
    slots: float = 0.0


class UpdateSessionBody(BaseModel):
    venue: Optional[str] = None
    slots: Optional[float] = None
    is_poll_open: Optional[bool] = None


@router.get("")
def get_sessions(period: Optional[str] = None, _: str = Depends(require_admin)):
    if period:
        return [serialize(s) for s in list_sessions_by_period(period)]
    raise HTTPException(status_code=400, detail="Provide ?period=<start_date>")


@router.get("/current")
def get_current(_: str = Depends(require_admin)):
    s = get_current_session()
    if not s:
        raise HTTPException(status_code=404, detail="No session today")
    return serialize(s)


@router.get("/open")
def get_open(_: str = Depends(require_admin)):
    s = get_open_session()
    if not s:
        raise HTTPException(status_code=404, detail="No open session")
    return serialize(s)


@router.get("/{date}")
def get_session_by_date(date: str, _: str = Depends(require_admin)):
    s = get_session(date)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return serialize(s)


@router.post("", status_code=201)
def add_session(body: CreateSessionBody, _: str = Depends(require_admin)):
    s = create_session(body.date, body.period_id, body.venue_id, body.slots)
    if not s:
        raise HTTPException(status_code=400, detail="Could not create session")
    return serialize(s)


@router.put("/{date}")
def edit_session(date: str, body: UpdateSessionBody, _: str = Depends(require_admin)):
    kwargs = {k: v for k, v in body.model_dump().items() if v is not None}
    s = update_session(date, **kwargs)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found or update failed")
    return serialize(s)


@router.delete("/{date}", status_code=204)
def remove_session(date: str, _: str = Depends(require_admin)):
    if not delete_session(date):
        raise HTTPException(status_code=404, detail="Session not found")
