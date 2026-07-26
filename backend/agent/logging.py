import json

from database import SessionLocal
from models import ToolLog


def save_tool_log(
    *,
    session_id: str,
    tool_name: str,
    reason: str,
    input_params: dict,
    output_result: str,
    status: str,
    duration_ms: float,
    error_message: str | None = None,
) -> None:
    db = SessionLocal()

    try:
        tool_log = ToolLog(
            session_id=session_id,
            tool_name=tool_name,
            reason=reason,
            input_params=json.dumps(
                input_params,
                ensure_ascii=False,
            ),
            output_result=output_result,
            status=status,
            duration_ms=duration_ms,
            error_message=error_message,
        )

        db.add(tool_log)
        db.commit()

    except Exception as error:
        db.rollback()
        print(f"保存工具日志失败：{error}")

    finally:
        db.close()
