from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.deps import require_admin
from schemas.sessions import Sessions
from services.session_participants import list_session_participants
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
    date_iso = s.date.isoformat() if s.date else None  # type: ignore
    people_count = 0
    if date_iso:
        participants = list_session_participants(date_iso)
        people_count = sum(1 + (p.additional_participants or 0) for p in participants)  # type: ignore

    price_per_slot = s.venue.price_per_slot if s.venue else 0.0  # type: ignore
    slots = s.slots or 0.0  # type: ignore
    total_money = round(price_per_slot * slots, 2) if price_per_slot and slots else 0.0

    return {
        "id": str(s.id),  # type: ignore
        "date": date_iso,
        "period_id": str(s.period.id) if s.period else None,  # type: ignore
        "period_start_date": s.period.start_date.isoformat() if s.period and s.period.start_date else None,  # type: ignore
        "venue_name": s.venue.name if s.venue else None,  # type: ignore
        "slots": slots,
        "is_poll_open": s.is_poll_open,  # type: ignore
        "telegram_poll_message_id": s.telegram_poll_message_id,  # type: ignore
        "people_count": people_count,
        "total_money": total_money,
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
