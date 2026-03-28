from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.deps import require_admin
from schemas.venues import Venues
from services.venues import (
    create_venue,
    delete_venue,
    get_venue_by_name,
    list_all_venues,
    update_venue,
)

router = APIRouter()


def serialize(v: Venues) -> dict:
    return {
        "id": str(v.id),
        "name": v.name,
        "location": v.location,
        "price_per_slot": v.price_per_slot,
    }


class CreateVenueBody(BaseModel):
    name: str
    location: str
    price_per_slot: float


class UpdateVenueBody(BaseModel):
    location: str | None = None
    price_per_slot: float | None = None


@router.get("")
def get_venues(_: str = Depends(require_admin)):
    return [serialize(v) for v in list_all_venues()]


@router.get("/{name}")
def get_venue(name: str, _: str = Depends(require_admin)):
    v = get_venue_by_name(name)
    if not v:
        raise HTTPException(status_code=404, detail="Venue not found")
    return serialize(v)


@router.post("", status_code=201)
def add_venue(body: CreateVenueBody, _: str = Depends(require_admin)):
    v = create_venue(body.name, body.location, body.price_per_slot)
    if not v:
        raise HTTPException(status_code=400, detail="Could not create venue")
    return serialize(v)


@router.put("/{name}")
def edit_venue(name: str, body: UpdateVenueBody, _: str = Depends(require_admin)):
    kwargs = {k: v for k, v in body.model_dump().items() if v is not None}
    v = update_venue(name, **kwargs)
    if not v:
        raise HTTPException(status_code=404, detail="Venue not found or update failed")
    return serialize(v)


@router.delete("/{name}", status_code=204)
def remove_venue(name: str, _: str = Depends(require_admin)):
    if not delete_venue(name):
        raise HTTPException(status_code=404, detail="Venue not found")
