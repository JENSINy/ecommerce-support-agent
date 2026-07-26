import uuid

from agents import Runner
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from agent_service import (
    CustomerServiceContext,
    customer_service_agent,
)
from dependencies import get_db
from schemas import ChatRequest, ChatResponse
from services.conversation_service import (
    get_or_create_conversation,
    load_conversation_messages,
    save_message,
)

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="消息不能为空",
        )

    session_id = request.session_id or str(uuid.uuid4())
    conversation_record = get_or_create_conversation(
        db,
        session_id,
    )
    conversation = load_conversation_messages(
        db,
        session_id,
    )

    save_message(
        db,
        conversation_record,
        session_id=session_id,
        role="user",
        content=message,
        failure_detail="保存用户消息失败",
    )

    conversation.append(
        {
            "role": "user",
            "content": message,
        }
    )

    try:
        result = await Runner.run(
            customer_service_agent,
            conversation,
            context=CustomerServiceContext(
                session_id=session_id,
            ),
        )
    except Exception as error:
        print(f"Agent 运行失败：{error}")
        raise HTTPException(
            status_code=500,
            detail="Agent 运行失败，请稍后重试",
        ) from error

    reply = str(result.final_output)

    save_message(
        db,
        conversation_record,
        session_id=session_id,
        role="assistant",
        content=reply,
        failure_detail="保存 Agent 回复失败",
    )

    return ChatResponse(
        session_id=session_id,
        reply=reply,
    )
