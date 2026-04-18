from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.deps import require_admin
from schemas.metadata import Metadata
from services.metadata import get_metadata, update_metadata

router = APIRouter()


def serialize(m: Metadata) -> dict:
    return {
        "default_venue_id": m.default_venue_id,
        "default_location": m.default_location,
        "default_start_time": m.default_start_time,
        "default_end_time": m.default_end_time,
        "default_day_of_the_week_index": m.default_day_of_the_week_index,
    }


class UpdateMetadataBody(BaseModel):
    default_venue_id: Optional[str] = None
    default_location: Optional[str] = None
    default_start_time: Optional[str] = None
    default_end_time: Optional[str] = None
    default_day_of_the_week_index: Optional[int] = None


@router.get("")
def read_metadata(_: str = Depends(require_admin)):
    m = get_metadata()
    if not m:
        raise HTTPException(status_code=404, detail="Metadata not initialized")
    return serialize(m)


@router.put("")
def edit_metadata(body: UpdateMetadataBody, _: str = Depends(require_admin)):
    kwargs = {k: v for k, v in body.model_dump().items() if v is not None}
    m = update_metadata(**kwargs)
    if not m:
        raise HTTPException(status_code=404, detail="Metadata not found or update failed")
    return serialize(m)
