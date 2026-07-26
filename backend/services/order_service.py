from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Order


def get_order(db: Session, order_id: str) -> dict:
    normalized_order_id = order_id.strip().upper()

    statement = select(Order).where(Order.order_id == normalized_order_id)
    order = db.scalars(statement).first()

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="订单不存在",
        )

    return {
        column.name: getattr(order, column.name) for column in Order.__table__.columns
    }
