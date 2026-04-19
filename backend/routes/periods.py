import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from telegram import Bot

from backend.deps import require_admin
from config import BOT_TOKEN, COMMON_GROUP_CHAT_ID, PUBLIC_BASE_URL
from schemas.period_shuttlecock_uses import PeriodShuttlecockUses
from schemas.periods import Periods
from services.calculations import calculate_period_report
from services.period_moneys import upsert_period_money
from services.period_shuttlecock_uses import (
    create_use,
    delete_use,
    list_uses_by_period,
)
from services.periods import (
    create_period,
    delete_period,
    ensure_share_token,
    get_current_period,
    get_period,
    list_all_periods,
    update_period,
)
from services.sessions import list_sessions_by_period
from utils.messages import get_period_closed_message

logger = logging.getLogger(__name__)

router = APIRouter()


async def _post_period_closed_message(start_date: str) -> bool:
    report = calculate_period_report(start_date)
    if not report:
        return False
    sessions = list_sessions_by_period(start_date)
    session_dates = [s.date for s in sessions if getattr(s, "date", None)]  # type: ignore
    first_session_date = min(session_dates) if session_dates else None
    last_session_date = max(session_dates) if session_dates else None
    message = get_period_closed_message(report, first_session_date, last_session_date)

    if PUBLIC_BASE_URL:
        period = get_period(start_date)
        if period:
            token = ensure_share_token(period)
            message += f"\n\nSee here for details: {PUBLIC_BASE_URL}/share/{token}"

    try:
        await Bot(BOT_TOKEN).send_message(chat_id=COMMON_GROUP_CHAT_ID, text=message)
        return True
    except Exception:
        logger.exception("failed to post period-closed message for %s", start_date)
        return False


def serialize(p: Periods) -> dict:
    return {
        "id": str(p.id),
        "start_date": p.start_date.isoformat() if p.start_date else None,
        "end_date": p.end_date.isoformat() if p.end_date else None,
        "total_money": p.total_money,
    }


class CreatePeriodBody(BaseModel):
    start_date: str
    end_date: str | None = None
    total_money: int | None = None


class UpdatePeriodBody(BaseModel):
    end_date: str | None = None
    total_money: int | None = None


class FinalizePeriodBody(BaseModel):
    end_date: str
    new_period_start_date: str


@router.get("")
def get_periods(_: str = Depends(require_admin)):
    return [serialize(p) for p in list_all_periods()]


@router.get("/current")
def get_current(_: str = Depends(require_admin)):
    p = get_current_period()
    if not p:
        raise HTTPException(status_code=404, detail="No active period")
    return serialize(p)


@router.get("/{start_date}")
def get_period_by_date(start_date: str, _: str = Depends(require_admin)):
    p = get_period(start_date)
    if not p:
        raise HTTPException(status_code=404, detail="Period not found")
    return serialize(p)


@router.post("", status_code=201)
def add_period(body: CreatePeriodBody, _: str = Depends(require_admin)):
    p = create_period(body.start_date, body.end_date, body.total_money)
    if not p:
        raise HTTPException(status_code=400, detail="Could not create period")
    return serialize(p)


@router.put("/{start_date}")
def edit_period(start_date: str, body: UpdatePeriodBody, _: str = Depends(require_admin)):
    kwargs = body.model_dump()
    p = update_period(start_date, **kwargs)
    if not p:
        raise HTTPException(status_code=404, detail="Period not found or update failed")
    return serialize(p)


@router.delete("/{start_date}", status_code=204)
def remove_period(start_date: str, _: str = Depends(require_admin)):
    if not delete_period(start_date):
        raise HTTPException(status_code=404, detail="Period not found")


@router.post("/{start_date}/finalize")
async def finalize_period(start_date: str, body: FinalizePeriodBody, _: str = Depends(require_admin)):
    report = calculate_period_report(start_date)
    if not report:
        raise HTTPException(status_code=404, detail="Period not found or report unavailable")

    for entry in report.personal_period_money:
        upsert_period_money(start_date, entry.person_id, entry.period_money)

    closed = update_period(start_date, end_date=body.end_date)
    if not closed:
        raise HTTPException(status_code=404, detail="Failed to close period")

    new_period = create_period(body.new_period_start_date)
    if not new_period:
        raise HTTPException(
            status_code=400,
            detail=f"Period closed, but could not create new period starting {body.new_period_start_date} (already exists?)",
        )

    group_posted = await _post_period_closed_message(start_date)

    return {
        "closed_period": serialize(closed),
        "new_period": serialize(new_period),
        "entries_upserted": len(report.personal_period_money),
        "group_posted": group_posted,
    }


@router.post("/{start_date}/resend-summary")
async def resend_summary(start_date: str, _: str = Depends(require_admin)):
    p = get_period(start_date)
    if not p:
        raise HTTPException(status_code=404, detail="Period not found")
    posted = await _post_period_closed_message(start_date)
    if not posted:
        raise HTTPException(status_code=502, detail="Failed to send message to group")
    return {"group_posted": True}


class CreateShuttlecockUseBody(BaseModel):
    batch_id: str
    tubes_used: int


def _serialize_use(u: PeriodShuttlecockUses) -> dict:
    batch = u.batch  # type: ignore
    tube_count = (batch.tube_count or 0) if batch else 0
    total_price = (batch.total_price or 0.0) if batch else 0.0
    price_each = round(total_price / tube_count, 2) if tube_count else 0.0
    return {
        "id": str(u.id),  # type: ignore
        "batch_id": str(batch.id) if batch else None,  # type: ignore
        "purchase_date": batch.purchase_date.isoformat() if batch and batch.purchase_date else None,  # type: ignore
        "price_each": price_each,
        "tubes_used": u.tubes_used,  # type: ignore
    }


@router.get("/{start_date}/shuttlecocks")
def list_period_shuttlecocks(start_date: str, _: str = Depends(require_admin)):
    return [_serialize_use(u) for u in list_uses_by_period(start_date)]


@router.post("/{start_date}/shuttlecocks", status_code=201)
def add_period_shuttlecock(
    start_date: str,
    body: CreateShuttlecockUseBody,
    _: str = Depends(require_admin),
):
    u = create_use(start_date, body.batch_id, body.tubes_used)
    if not u:
        raise HTTPException(status_code=400, detail="Could not record shuttlecock use")
    return _serialize_use(u)


@router.delete("/{start_date}/shuttlecocks/{use_id}", status_code=204)
def remove_period_shuttlecock(start_date: str, use_id: str, _: str = Depends(require_admin)):
    if not delete_use(use_id):
        raise HTTPException(status_code=404, detail="Shuttlecock use not found")
