from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies import get_db
from schemas import RejectReturnRequest
from services.return_service import (
    approve_return_request,
    get_return_requests,
    reject_return_request,
)

router = APIRouter(
    prefix="/return-requests",
    tags=["returns"],
)


@router.get("")
def read_return_requests(
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return get_return_requests(db, status)


@router.post("/{return_request_id}/approve")
def approve_return(
    return_request_id: int,
    db: Session = Depends(get_db),
):
    return approve_return_request(db, return_request_id)


@router.post("/{return_request_id}/reject")
def reject_return(
    return_request_id: int,
    request: RejectReturnRequest,
    db: Session = Depends(get_db),
):
    return reject_return_request(
        db,
        return_request_id,
        request.review_note,
    )
