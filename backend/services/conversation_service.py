from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Conversation, Message


def get_or_create_conversation(
    db: Session,
    session_id: str,
) -> Conversation:
    conversation = db.get(Conversation, session_id)

    if conversation is None:
        conversation = Conversation(session_id=session_id)
        db.add(conversation)

        try:
            db.commit()
            db.refresh(conversation)
        except Exception as error:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="创建会话失败",
            ) from error

    return conversation


def load_conversation_messages(
    db: Session,
    session_id: str,
) -> list[dict[str, str]]:
    statement = (
        select(Message).where(Message.session_id == session_id).order_by(Message.id)
    )
    messages = db.scalars(statement).all()

    return [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in messages
    ]


def save_message(
    db: Session,
    conversation: Conversation,
    *,
    session_id: str,
    role: str,
    content: str,
    failure_detail: str,
) -> Message:
    message = Message(
        session_id=session_id,
        role=role,
        content=content,
    )
    db.add(message)
    conversation.updated_at = datetime.now()

    try:
        db.commit()
        db.refresh(message)
    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=failure_detail,
        ) from error

    return message


def get_conversation_messages(
    db: Session,
    session_id: str,
) -> list[dict]:
    conversation = db.get(Conversation, session_id)

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="会话不存在",
        )

    statement = (
        select(Message).where(Message.session_id == session_id).order_by(Message.id)
    )
    messages = db.scalars(statement).all()

    return [
        {
            "id": message.id,
            "session_id": message.session_id,
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at,
        }
        for message in messages
    ]
