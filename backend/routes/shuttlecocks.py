from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.deps import require_admin
from schemas.shuttlecock_batches import ShuttlecockBatches
from services.period_shuttlecock_uses import get_consumed_for_batch
from services.shuttlecock_batches import (
    create_inventory_batch,
    delete_batch,
    list_all_batches,
)

router = APIRouter()


def serialize(b: ShuttlecockBatches) -> dict:
    consumed = get_consumed_for_batch(str(b.id))  # type: ignore
    tube_count = b.tube_count or 0  # type: ignore
    total_price = b.total_price or 0.0  # type: ignore
    price_each = round(total_price / tube_count, 2) if tube_count else 0.0
    remaining = tube_count - consumed
    return {
        "id": str(b.id),  # type: ignore
        "purchase_date": b.purchase_date.isoformat() if b.purchase_date else None,  # type: ignore
        "total_price": total_price,
        "tube_count": tube_count,
        "price_each": price_each,
        "consumed": consumed,
        "remaining": remaining,
    }


class CreateBatchBody(BaseModel):
    purchase_date: str
    total_price: float
    tube_count: int


@router.get("")
def get_batches(_: str = Depends(require_admin)):
    return [serialize(b) for b in list_all_batches()]


@router.post("", status_code=201)
def add_batch(body: CreateBatchBody, _: str = Depends(require_admin)):
    b = create_inventory_batch(body.purchase_date, body.total_price, body.tube_count)
    if not b:
        raise HTTPException(status_code=400, detail="Could not create shuttlecock batch")
    return serialize(b)


@router.delete("/{purchase_date}", status_code=204)
def remove_batch(purchase_date: str, _: str = Depends(require_admin)):
    if not delete_batch(purchase_date):
        raise HTTPException(status_code=404, detail="Shuttlecock batch not found")
