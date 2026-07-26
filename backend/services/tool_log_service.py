from sqlalchemy import select
from sqlalchemy.orm import Session

from models import ToolLog


def get_tool_logs(
    db: Session,
    session_id: str | None = None,
) -> list[dict]:
    statement = select(ToolLog).order_by(ToolLog.id.desc())

    if session_id:
        statement = statement.where(ToolLog.session_id == session_id)

    tool_logs = db.scalars(statement).all()

    return [
        {
            "id": tool_log.id,
            "session_id": tool_log.session_id,
            "tool_name": tool_log.tool_name,
            "reason": tool_log.reason,
            "input_params": tool_log.input_params,
            "output_result": tool_log.output_result,
            "status": tool_log.status,
            "duration_ms": tool_log.duration_ms,
            "error_message": tool_log.error_message,
            "created_at": tool_log.created_at,
        }
        for tool_log in tool_logs
    ]
