from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.deps import require_admin
from schemas.shuttlecock_batches import ShuttlecockBatches
from services.shuttlecock_batches import (
    create_batch,
    delete_batch,
    list_batches_by_period,
)

router = APIRouter()


def serialize(b: ShuttlecockBatches) -> dict:
    return {
        "id": str(b.id),
        "purchase_date": b.purchase_date.isoformat() if b.purchase_date else None,
        "total_price": b.total_price,
        "tube_count": b.tube_count,
        "period_start_date": b.period.start_date.isoformat() if b.period and b.period.start_date else None,
    }


class CreateBatchBody(BaseModel):
    period_start_date: str
    purchase_date: str
    total_price: float
    tube_count: Optional[int] = None


@router.get("")
def get_batches(period: Optional[str] = None, _: str = Depends(require_admin)):
    if not period:
        raise HTTPException(status_code=400, detail="Provide ?period=<start_date>")
    return [serialize(b) for b in list_batches_by_period(period)]


@router.post("", status_code=201)
def add_batch(body: CreateBatchBody, _: str = Depends(require_admin)):
    b = create_batch(body.period_start_date, body.purchase_date, body.total_price, body.tube_count)
    if not b:
        raise HTTPException(status_code=400, detail="Could not create shuttlecock batch")
    return serialize(b)


@router.delete("/{purchase_date}", status_code=204)
def remove_batch(purchase_date: str, _: str = Depends(require_admin)):
    if not delete_batch(purchase_date):
        raise HTTPException(status_code=404, detail="Shuttlecock batch not found")
