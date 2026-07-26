import json
import time
import uuid
from datetime import datetime

from agents import RunContextWrapper, function_tool
from sqlalchemy import select

from agent.context import CustomerServiceContext
from agent.logging import save_tool_log
from database import SessionLocal
from models import Order, ReturnRequest


@function_tool
def create_return_request(
    context: RunContextWrapper[CustomerServiceContext],
    order_id: str,
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
                    "message": "没有找到该订单，无法创建退货申请",
                },
                ensure_ascii=False,
            )

        elif not normalized_reason:
            status = "failed"

            result = json.dumps(
                {
                    "success": False,
                    "message": "缺少退货原因",
                },
                ensure_ascii=False,
            )

        else:
            return_request = ReturnRequest(
                return_no=(
                    f"RET{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    f"{uuid.uuid4().hex[:4].upper()}"
                ),
                order_id=normalized_order_id,
                reason=normalized_reason,
                status="pending_review",
            )

            db.add(return_request)
            db.commit()
            db.refresh(return_request)

            result = json.dumps(
                {
                    "success": True,
                    "message": "退货申请已提交，等待人工审核",
                    "return_request": {
                        "return_no": return_request.return_no,
                        "order_id": return_request.order_id,
                        "reason": return_request.reason,
                        "status": return_request.status,
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
                "message": "创建退货申请时发生错误",
                "error": error_message,
            },
            ensure_ascii=False,
        )

    finally:
        db.close()

        save_tool_log(
            session_id=context.context.session_id,
            tool_name="create_return_request",
            reason=tool_reason,
            input_params={
                "order_id": normalized_order_id,
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
