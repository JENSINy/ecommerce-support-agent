from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies import get_db
from schemas import RejectRefundRequest
from services.refund_service import (
    approve_refund_request,
    get_refund_requests,
    reject_refund_request,
)

router = APIRouter(
    prefix="/refund-requests",
    tags=["refunds"],
)


@router.get("")
def read_refund_requests(
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return get_refund_requests(db, status)


@router.post("/{refund_request_id}/approve")
def approve_refund(
    refund_request_id: int,
    db: Session = Depends(get_db),
):
    return approve_refund_request(db, refund_request_id)


@router.post("/{refund_request_id}/reject")
def reject_refund(
    refund_request_id: int,
    request: RejectRefundRequest,
    db: Session = Depends(get_db),
):
    return reject_refund_request(
        db,
        refund_request_id,
        request.reject_reason,
    )
