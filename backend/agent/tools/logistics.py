import json
import time

from agents import RunContextWrapper, function_tool
from sqlalchemy import select

from agent.context import CustomerServiceContext
from agent.logging import save_tool_log
from database import SessionLocal
from models import Logistics


@function_tool
def get_logistics(
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
        logistics = db.scalars(
            select(Logistics).where(Logistics.order_id == normalized_order_id)
        ).first()

        if logistics is None:
            status = "not_found"

            result = json.dumps(
                {
                    "success": False,
                    "message": "没有找到该订单的物流信息",
                    "order_id": normalized_order_id,
                },
                ensure_ascii=False,
            )

        else:
            logistics_data = {
                column.name: getattr(logistics, column.name)
                for column in Logistics.__table__.columns
            }

            result = json.dumps(
                {
                    "success": True,
                    "logistics": logistics_data,
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
                "message": "查询物流时发生错误",
                "error": error_message,
            },
            ensure_ascii=False,
        )

    finally:
        db.close()

        save_tool_log(
            session_id=context.context.session_id,
            tool_name="get_logistics",
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
