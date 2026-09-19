from fastapi import APIRouter, HTTPException

from app.repositories.flat_fares import DuplicateFlatFare
from app.schemas.quote import FlatFareRequest
from app.services.metro_service import MetroService

router = APIRouter(tags=["flat-fares"])


@router.get("/flat-fares")
def list_flat_fares():
    with MetroService() as s:
        return {"items": s.flat_fares()}


@router.post("/flat-fares", status_code=201)
def create_flat_fare(body: FlatFareRequest):
    with MetroService() as s:
        try:
            flat_id = s.add_flat_fare(body.start, body.end, body.price)
        except DuplicateFlatFare:
            raise HTTPException(409, "该起终点对已登记一口价")
        return {"id": flat_id, "start": body.start, "end": body.end, "price": body.price}


@router.delete("/flat-fares/{flat_id}")
def delete_flat_fare(flat_id: int):
    with MetroService() as s:
        if not s.delete_flat_fare(flat_id):
            raise HTTPException(404)
        return {"ok": True}
