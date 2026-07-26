from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies import get_db
from services.tool_log_service import get_tool_logs

router = APIRouter(
    prefix="/tool-logs",
    tags=["tool-logs"],
)


@router.get("")
def read_tool_logs(
    session_id: str | None = None,
    db: Session = Depends(get_db),
):
    return get_tool_logs(db, session_id)
