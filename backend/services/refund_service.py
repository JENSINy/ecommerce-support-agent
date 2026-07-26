import json
import time
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Order, RefundRequest, ToolLog


def get_refund_requests(
    db: Session,
    status: str | None = None,
) -> list[dict]:
    statement = select(RefundRequest).order_by(RefundRequest.id.desc())

    if status:
        statement = statement.where(RefundRequest.status == status)

    refund_requests = db.scalars(statement).all()

    return [
        {
            "id": refund_request.id,
            "refund_no": refund_request.refund_no,
            "order_id": refund_request.order_id,
            "amount": refund_request.amount,
            "reason": refund_request.reason,
            "status": refund_request.status,
            "approved_by": refund_request.approved_by,
            "approved_at": refund_request.approved_at,
            "rejected_by": refund_request.rejected_by,
            "rejected_at": refund_request.rejected_at,
            "reject_reason": refund_request.reject_reason,
            "created_at": refund_request.created_at,
        }
        for refund_request in refund_requests
    ]


def approve_refund_request(
    db: Session,
    refund_request_id: int,
) -> dict:
    refund_request = db.get(
        RefundRequest,
        refund_request_id,
    )

    if refund_request is None:
        raise HTTPException(
            status_code=404,
            detail="退款申请不存在",
        )

    if refund_request.status != "pending_approval":
        raise HTTPException(
            status_code=400,
            detail="该退款申请已处理，不能重复批准",
        )

    order_statement = select(Order).where(Order.order_id == refund_request.order_id)
    order = db.scalars(order_statement).first()

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="关联订单不存在，无法执行退款",
        )

    started_at = time.perf_counter()

    try:
        order.status = "refunded"
        refund_request.status = "approved"
        refund_request.approved_by = "admin"
        refund_request.approved_at = datetime.now()

        duration_ms = round(
            (time.perf_counter() - started_at) * 1000,
            2,
        )

        db.add(
            ToolLog(
                session_id=None,
                tool_name="issue_refund",
                reason="人工审批通过退款申请后执行退款",
                input_params=json.dumps(
                    {
                        "refund_request_id": refund_request.id,
                        "refund_no": refund_request.refund_no,
                        "order_id": refund_request.order_id,
                        "amount": refund_request.amount,
                    },
                    ensure_ascii=False,
                ),
                output_result=json.dumps(
                    {
                        "success": True,
                        "message": "退款执行成功",
                        "order_status": order.status,
                    },
                    ensure_ascii=False,
                ),
                status="success",
                duration_ms=duration_ms,
                error_message=None,
            )
        )

        db.commit()
        db.refresh(refund_request)

        return {
            "message": "退款申请已批准，退款已执行",
            "refund_request_id": refund_request.id,
            "refund_no": refund_request.refund_no,
            "status": refund_request.status,
            "order_status": order.status,
        }
    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"执行退款失败：{error}",
        ) from error


def reject_refund_request(
    db: Session,
    refund_request_id: int,
    reject_reason: str,
) -> dict:
    refund_request = db.get(
        RefundRequest,
        refund_request_id,
    )

    if refund_request is None:
        raise HTTPException(
            status_code=404,
            detail="退款申请不存在",
        )

    if refund_request.status != "pending_approval":
        raise HTTPException(
            status_code=400,
            detail="该退款申请已处理，不能重复拒绝",
        )

    normalized_reason = reject_reason.strip()

    if not normalized_reason:
        raise HTTPException(
            status_code=400,
            detail="拒绝退款时必须填写原因",
        )

    try:
        refund_request.status = "rejected"
        refund_request.rejected_by = "admin"
        refund_request.rejected_at = datetime.now()
        refund_request.reject_reason = normalized_reason

        db.commit()
        db.refresh(refund_request)

        return {
            "message": "退款申请已拒绝",
            "refund_request_id": refund_request.id,
            "refund_no": refund_request.refund_no,
            "status": refund_request.status,
        }
    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"拒绝退款申请失败：{error}",
        ) from error
