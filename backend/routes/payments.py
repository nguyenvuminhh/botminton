from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.deps import require_admin
from schemas.period_moneys import PeriodMoneys
from services.calculations import calculate_period_report
from services.period_moneys import (
    list_period_moneys_by_period,
    mark_as_paid_by_telegram_id,
    mark_as_unpaid_by_telegram_id,
    upsert_period_money,
)

router = APIRouter()


def serialize(pm: PeriodMoneys) -> dict:
    return {
        "id": str(pm.id),
        "period_start_date": pm.period.start_date.isoformat() if pm.period and pm.period.start_date else None,
        "user_telegram_id": pm.user.telegram_id if pm.user else None,
        "user_name": pm.user.telegram_user_name if pm.user else None,
        "amount": pm.amount,
        "has_paid": pm.has_paid,
    }


class UpsertPaymentBody(BaseModel):
    period_start_date: str
    user_telegram_id: str
    amount: float


class MarkPaidBody(BaseModel):
    period_start_date: str
    user_telegram_id: str


@router.get("")
def get_payments(period: Optional[str] = None, _: str = Depends(require_admin)):
    if not period:
        raise HTTPException(status_code=400, detail="Provide ?period=<start_date>")
    return [serialize(pm) for pm in list_period_moneys_by_period(period)]


@router.post("", status_code=201)
def upsert_payment(body: UpsertPaymentBody, _: str = Depends(require_admin)):
    pm = upsert_period_money(body.period_start_date, body.user_telegram_id, body.amount)
    if not pm:
        raise HTTPException(status_code=400, detail="Could not upsert payment record")
    return serialize(pm)


@router.post("/mark-paid")
def mark_paid(body: MarkPaidBody, _: str = Depends(require_admin)):
    pm = mark_as_paid_by_telegram_id(body.period_start_date, body.user_telegram_id)
    if not pm:
        raise HTTPException(status_code=404, detail="Payment record not found")
    return serialize(pm)


@router.post("/mark-unpaid")
def mark_unpaid(body: MarkPaidBody, _: str = Depends(require_admin)):
    pm = mark_as_unpaid_by_telegram_id(body.period_start_date, body.user_telegram_id)
    if not pm:
        raise HTTPException(status_code=404, detail="Payment record not found")
    return serialize(pm)


@router.get("/report/{period_start_date}")
def get_report(period_start_date: str, _: str = Depends(require_admin)):
    report = calculate_period_report(period_start_date)
    if not report:
        raise HTTPException(status_code=404, detail="Could not calculate report for this period")
    return report.model_dump()
