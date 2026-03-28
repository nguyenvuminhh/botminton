from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.deps import require_admin
from schemas.periods import Periods
from services.periods import (
    create_period,
    delete_period,
    get_current_period,
    get_period,
    list_all_periods,
    update_period,
)

router = APIRouter()


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
