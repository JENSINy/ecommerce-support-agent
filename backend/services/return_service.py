import json
import time
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import ReturnRequest, ToolLog
from statuses import ReturnStatus, ToolLogStatus


def get_return_requests(
    db: Session,
    status: str | None = None,
) -> list[dict]:
    statement = select(ReturnRequest).order_by(ReturnRequest.id.desc())

    if status:
        statement = statement.where(ReturnRequest.status == status)

    return_requests = db.scalars(statement).all()

    return [
        {
            "id": return_request.id,
            "return_no": return_request.return_no,
            "order_id": return_request.order_id,
            "reason": return_request.reason,
            "status": return_request.status,
            "reviewed_by": return_request.reviewed_by,
            "reviewed_at": return_request.reviewed_at,
            "review_note": return_request.review_note,
            "created_at": return_request.created_at,
            "updated_at": return_request.updated_at,
        }
        for return_request in return_requests
    ]


def approve_return_request(
    db: Session,
    return_request_id: int,
) -> dict:
    return_request = db.get(
        ReturnRequest,
        return_request_id,
    )

    if return_request is None:
        raise HTTPException(
            status_code=404,
            detail="退货申请不存在",
        )

    if return_request.status != ReturnStatus.PENDING_REVIEW:
        raise HTTPException(
            status_code=400,
            detail="该退货申请已处理，不能重复批准",
        )

    started_at = time.perf_counter()

    try:
        return_request.status = ReturnStatus.APPROVED
        return_request.reviewed_by = "admin"
        return_request.reviewed_at = datetime.now()
        return_request.review_note = "人工审核通过，可按退货指引寄回商品。"

        duration_ms = round(
            (time.perf_counter() - started_at) * 1000,
            2,
        )

        db.add(
            ToolLog(
                session_id=None,
                tool_name="approve_return_request",
                reason="人工审核通过退货申请",
                input_params=json.dumps(
                    {
                        "return_request_id": return_request.id,
                        "return_no": return_request.return_no,
                        "order_id": return_request.order_id,
                    },
                    ensure_ascii=False,
                ),
                output_result=json.dumps(
                    {
                        "success": True,
                        "message": "退货申请已审核通过",
                        "status": return_request.status,
                    },
                    ensure_ascii=False,
                ),
                status=ToolLogStatus.SUCCESS,
                duration_ms=duration_ms,
                error_message=None,
            )
        )

        # 审批状态和日志一起提交。
        db.commit()
        db.refresh(return_request)

        return {
            "message": "退货申请已审核通过",
            "return_request_id": return_request.id,
            "return_no": return_request.return_no,
            "status": return_request.status,
        }

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"批准退货申请失败：{error}",
        ) from error


def reject_return_request(
    db: Session,
    return_request_id: int,
    review_note: str,
) -> dict:
    return_request = db.get(
        ReturnRequest,
        return_request_id,
    )

    if return_request is None:
        raise HTTPException(
            status_code=404,
            detail="退货申请不存在",
        )

    if return_request.status != ReturnStatus.PENDING_REVIEW:
        raise HTTPException(
            status_code=400,
            detail="该退货申请已处理，不能重复拒绝",
        )

    normalized_note = review_note.strip()

    if not normalized_note:
        raise HTTPException(
            status_code=400,
            detail="拒绝退货时必须填写原因",
        )

    started_at = time.perf_counter()

    try:
        return_request.status = ReturnStatus.REJECTED
        return_request.reviewed_by = "admin"
        return_request.reviewed_at = datetime.now()
        return_request.review_note = normalized_note

        duration_ms = round(
            (time.perf_counter() - started_at) * 1000,
            2,
        )

        db.add(
            ToolLog(
                session_id=None,
                tool_name="reject_return_request",
                reason="人工拒绝退货申请",
                input_params=json.dumps(
                    {
                        "return_request_id": return_request.id,
                        "return_no": return_request.return_no,
                        "review_note": normalized_note,
                    },
                    ensure_ascii=False,
                ),
                output_result=json.dumps(
                    {
                        "success": True,
                        "message": "退货申请已拒绝",
                        "status": return_request.status,
                    },
                    ensure_ascii=False,
                ),
                status=ToolLogStatus.SUCCESS,
                duration_ms=duration_ms,
                error_message=None,
            )
        )

        # 拒绝状态和日志一起提交。
        db.commit()
        db.refresh(return_request)

        return {
            "message": "退货申请已拒绝",
            "return_request_id": return_request.id,
            "return_no": return_request.return_no,
            "status": return_request.status,
        }

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"拒绝退货申请失败：{error}",
        ) from error
