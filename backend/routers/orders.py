from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies import get_db
from services.order_service import get_order

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


@router.get("/{order_id}")
def read_order(
    order_id: str,
    db: Session = Depends(get_db),
):
    return get_order(db, order_id)
