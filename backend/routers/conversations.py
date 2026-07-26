from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies import get_db
from services.conversation_service import get_conversation_messages

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
)


@router.get("/{session_id}/messages")
def read_conversation_messages(
    session_id: str,
    db: Session = Depends(get_db),
):
    return get_conversation_messages(db, session_id)
