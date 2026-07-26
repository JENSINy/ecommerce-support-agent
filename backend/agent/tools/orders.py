import json
import time

from agents import RunContextWrapper, function_tool
from sqlalchemy import select

from agent.context import CustomerServiceContext
from agent.logging import save_tool_log
from database import SessionLocal
from models import Order


@function_tool
def get_order(
    context: RunContextWrapper[CustomerServiceContext],
    order_id: str,
    reason: str,
) -> str:
    started_at = time.perf_counter()

    normalized_order_id = order_id.strip().upper()

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
                    "message": "没有找到该订单",
                    "order_id": normalized_order_id,
                },
                ensure_ascii=False,
            )

        else:
            order_data = {
                column.name: getattr(order, column.name)
                for column in Order.__table__.columns
            }

            result = json.dumps(
                {
                    "success": True,
                    "order": order_data,
                },
                ensure_ascii=False,
                default=str,
            )

    except Exception as error:
        status = "failed"
        error_message = str(error)

        result = json.dumps(
            {
                "success": False,
                "message": "查询订单时发生错误",
                "error": error_message,
            },
            ensure_ascii=False,
        )

    finally:
        db.close()

        save_tool_log(
            session_id=context.context.session_id,
            tool_name="get_order",
            reason=reason,
            input_params={
                "order_id": normalized_order_id,
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
