from fastapi import APIRouter, HTTPException

from services.period_matrix import build_period_matrix
from services.periods import get_period_by_share_token

router = APIRouter()


@router.get("/periods/{token}/matrix")
def get_period_matrix(token: str):
    period = get_period_by_share_token(token)
    if not period:
        raise HTTPException(status_code=404, detail="Not found")

    if not period.share_snapshot:  # type: ignore
        period.share_snapshot = build_period_matrix(period)  # type: ignore
        period.save()

    return period.share_snapshot  # type: ignore
