from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.deps import require_admin
from schemas.session_participants import SessionParticipants
from services.session_participants import (
    create_participant,
    delete_participant,
    list_session_participants,
    update_participant,
)

router = APIRouter()


def serialize(p: SessionParticipants) -> dict:
    return {
        "id": str(p.id),
        "user_telegram_id": p.user.telegram_id if p.user else None,
        "user_name": p.user.telegram_user_name if p.user else None,
        "session_date": p.session.date.isoformat() if p.session and p.session.date else None,
        "additional_participants": p.additional_participants,
    }


class CreateParticipantBody(BaseModel):
    user_telegram_id: str
    session_date: str
    additional_participants: int = 0


class UpdateParticipantBody(BaseModel):
    additional_participants: Optional[int] = None


@router.get("")
def get_participants(session_date: Optional[str] = None, _: str = Depends(require_admin)):
    if not session_date:
        raise HTTPException(status_code=400, detail="Provide ?session_date=<date>")
    return [serialize(p) for p in list_session_participants(session_date)]


@router.post("", status_code=201)
def add_participant(body: CreateParticipantBody, _: str = Depends(require_admin)):
    p = create_participant(body.user_telegram_id, body.session_date, body.additional_participants)
    if not p:
        raise HTTPException(status_code=400, detail="Could not create participant")
    return serialize(p)


@router.put("/{participant_id}")
def edit_participant(
    participant_id: str, body: UpdateParticipantBody, _: str = Depends(require_admin)
):
    kwargs = {k: v for k, v in body.model_dump().items() if v is not None}
    p = update_participant(participant_id, **kwargs)
    if not p:
        raise HTTPException(status_code=404, detail="Participant not found or update failed")
    return serialize(p)


@router.delete("/{participant_id}", status_code=204)
def remove_participant(participant_id: str, _: str = Depends(require_admin)):
    if not delete_participant(participant_id):
        raise HTTPException(status_code=404, detail="Participant not found")
