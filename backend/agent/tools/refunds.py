import json
import time
import uuid
from datetime import datetime

from agents import RunContextWrapper, function_tool
from sqlalchemy import select

from agent.context import CustomerServiceContext
from agent.logging import save_tool_log
from database import SessionLocal
from models import Order, RefundRequest


@function_tool
def request_refund(
    context: RunContextWrapper[CustomerServiceContext],
    order_id: str,
    amount: float,
    reason: str,
    tool_reason: str,
) -> str:
    started_at = time.perf_counter()

    normalized_order_id = order_id.strip().upper()
    normalized_reason = reason.strip()

    status = "success"
    error_message = None
    result = ""

    db = SessionLocal()

    try:
        order = db.scalars(
            select(Order).where(Order.order_id == normalized_order_id)
        ).first()

        if order is None:
            status = "not_found"

            result = json.dumps(
                {
                    "success": False,
                    "message": "没有找到该订单，无法创建退款申请",
                },
                ensure_ascii=False,
            )

        elif amount <= 0:
            status = "failed"

            result = json.dumps(
                {
                    "success": False,
                    "message": "退款金额必须大于 0",
                },
                ensure_ascii=False,
            )

        elif amount > order.amount:
            status = "failed"

            result = json.dumps(
                {
                    "success": False,
                    "message": "退款金额不能超过订单实付金额",
                    "order_amount": order.amount,
                    "requested_amount": amount,
                },
                ensure_ascii=False,
            )

        elif not normalized_reason:
            status = "failed"

            result = json.dumps(
                {
                    "success": False,
                    "message": "缺少退款原因",
                },
                ensure_ascii=False,
            )

        else:
            refund_request = RefundRequest(
                refund_no=(
                    f"REF{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    f"{uuid.uuid4().hex[:4].upper()}"
                ),
                order_id=normalized_order_id,
                amount=amount,
                reason=normalized_reason,
                status="pending_approval",
            )

            db.add(refund_request)
            db.commit()
            db.refresh(refund_request)

            result = json.dumps(
                {
                    "success": True,
                    "message": (
                        "退款申请已创建，正在等待人工审批。人工批准前不会执行退款。"
                    ),
                    "refund_request": {
                        "id": refund_request.id,
                        "refund_no": refund_request.refund_no,
                        "order_id": refund_request.order_id,
                        "amount": refund_request.amount,
                        "reason": refund_request.reason,
                        "status": refund_request.status,
                    },
                },
                ensure_ascii=False,
            )

    except Exception as error:
        db.rollback()

        status = "failed"
        error_message = str(error)

        result = json.dumps(
            {
                "success": False,
                "message": "创建退款申请时发生错误",
                "error": error_message,
            },
            ensure_ascii=False,
        )

    finally:
        db.close()

        save_tool_log(
            session_id=context.context.session_id,
            tool_name="request_refund",
            reason=tool_reason,
            input_params={
                "order_id": normalized_order_id,
                "amount": amount,
                "reason": normalized_reason,
            },
            output_result=result,
            status=status,
            duration_ms=round(
                (time.perf_counter() - started_at) * 1000,
                2,
            ),
            error_message=error_message,
        )

    return result
