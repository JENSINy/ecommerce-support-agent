import uuid
from datetime import datetime
from typing import Optional

import time
import json

from agents import Runner
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_service import (
    CustomerServiceContext,
    customer_service_agent,
)

from database import SessionLocal
from models import Conversation, Message, Order, ToolLog, RefundRequest, ReturnRequest



app = FastAPI(
    title="电商售后 Agent API",
    description="支持订单查询和多轮对话的电商售后接口",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_or_create_conversation(
    db: Session,
    session_id: str,
) -> Conversation:
    conversation = db.get(Conversation, session_id)

    if conversation is None:
        conversation = Conversation(session_id=session_id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    return conversation


def load_conversation_messages(
    db: Session,
    session_id: str,
) -> list[dict[str, str]]:
    statement = (
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.id)
    )

    messages = db.scalars(statement).all()

    return [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in messages
    ]


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str


@app.get("/")
def read_root():
    return {
        "message": "电商售后 Agent API 已启动",
    }


@app.get("/orders/{order_id}")
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
):
    normalized_order_id = order_id.strip().upper()

    statement = select(Order).where(
        Order.order_id == normalized_order_id
    )
    order = db.scalars(statement).first()

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="订单不存在",
        )

    return {
        column.name: getattr(order, column.name)
        for column in Order.__table__.columns
    }


@app.post("/chat", response_model=ChatResponse)
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

    user_message = Message(
        session_id=session_id,
        role="user",
        content=message,
    )

    db.add(user_message)

    conversation_record.updated_at = datetime.now()

    try:
        db.commit()
    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="保存用户消息失败",
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

    assistant_message = Message(
        session_id=session_id,
        role="assistant",
        content=reply,
    )

    db.add(assistant_message)

    conversation_record.updated_at = datetime.now()

    try:
        db.commit()
    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="保存 Agent 回复失败",
        )

    return ChatResponse(
        session_id=session_id,
        reply=reply,
    )


@app.get("/tool-logs")
def get_tool_logs(
    session_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    statement = select(ToolLog).order_by(ToolLog.id.desc())

    if session_id:
        statement = statement.where(
            ToolLog.session_id == session_id
        )

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


@app.get("/conversations/{session_id}/messages")
def get_conversation_messages(
    session_id: str,
    db: Session = Depends(get_db),
):
    conversation = db.get(Conversation, session_id)

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="会话不存在",
        )

    statement = (
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.id)
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


class RejectRefundRequest(BaseModel):
    reject_reason: str


@app.get("/refund-requests")
def get_refund_requests(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    statement = select(RefundRequest).order_by(
        RefundRequest.id.desc()
    )

    if status:
        statement = statement.where(
            RefundRequest.status == status
        )

    refund_requests = db.scalars(statement).all()

    return [
        {
            "id": refund_request.id,
            "refund_no": refund_request.refund_no,
            "order_id": refund_request.order_id,
            "amount": refund_request.amount,
            "reason": refund_request.reason,
            "status": refund_request.status,
            "approved_by": refund_request.approved_by,
            "approved_at": refund_request.approved_at,
            "rejected_by": refund_request.rejected_by,
            "rejected_at": refund_request.rejected_at,
            "reject_reason": refund_request.reject_reason,
            "created_at": refund_request.created_at,
        }
        for refund_request in refund_requests
    ]


@app.post("/refund-requests/{refund_request_id}/approve")
def approve_refund_request(
    refund_request_id: int,
    db: Session = Depends(get_db),
):
    refund_request = db.get(RefundRequest, refund_request_id)

    if refund_request is None:
        raise HTTPException(
            status_code=404,
            detail="退款申请不存在",
        )

    if refund_request.status != "pending_approval":
        raise HTTPException(
            status_code=400,
            detail="该退款申请已处理，不能重复批准",
        )

    order_statement = select(Order).where(
        Order.order_id == refund_request.order_id
    )
    order = db.scalars(order_statement).first()

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="关联订单不存在，无法执行退款",
        )

    started_at = time.perf_counter()

    try:
        # 模拟 issue_refund：真实项目中此处会调用支付平台退款接口。
        order.status = "refunded"

        refund_request.status = "approved"
        refund_request.approved_by = "admin"
        refund_request.approved_at = datetime.now()

        db.commit()
        db.refresh(refund_request)

        duration_ms = round(
            (time.perf_counter() - started_at) * 1000,
            2,
        )

        tool_log = ToolLog(
            session_id=None,
            tool_name="issue_refund",
            reason="人工审批通过退款申请后执行退款",
            input_params=json.dumps(
                {
                    "refund_request_id": refund_request.id,
                    "refund_no": refund_request.refund_no,
                    "order_id": refund_request.order_id,
                    "amount": refund_request.amount,
                },
                ensure_ascii=False,
            ),
            output_result=json.dumps(
                {
                    "success": True,
                    "message": "退款执行成功",
                    "order_status": order.status,
                },
                ensure_ascii=False,
            ),
            status="success",
            duration_ms=duration_ms,
            error_message=None,
        )

        db.add(tool_log)
        db.commit()

        return {
            "message": "退款申请已批准，退款已执行",
            "refund_request_id": refund_request.id,
            "refund_no": refund_request.refund_no,
            "status": refund_request.status,
            "order_status": order.status,
        }
    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"执行退款失败：{error}",
        ) from error


@app.post("/refund-requests/{refund_request_id}/reject")
def reject_refund_request(
    refund_request_id: int,
    request: RejectRefundRequest,
    db: Session = Depends(get_db),
):
    refund_request = db.get(RefundRequest, refund_request_id)

    if refund_request is None:
        raise HTTPException(
            status_code=404,
            detail="退款申请不存在",
        )

    if refund_request.status != "pending_approval":
        raise HTTPException(
            status_code=400,
            detail="该退款申请已处理，不能重复拒绝",
        )

    reject_reason = request.reject_reason.strip()

    if not reject_reason:
        raise HTTPException(
            status_code=400,
            detail="拒绝退款时必须填写原因",
        )

    try:
        refund_request.status = "rejected"
        refund_request.rejected_by = "admin"
        refund_request.rejected_at = datetime.now()
        refund_request.reject_reason = reject_reason

        db.commit()
        db.refresh(refund_request)

        return {
            "message": "退款申请已拒绝",
            "refund_request_id": refund_request.id,
            "refund_no": refund_request.refund_no,
            "status": refund_request.status,
        }
    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"拒绝退款申请失败：{error}",
        ) from error


class RejectReturnRequest(BaseModel):
    review_note: str


@app.get("/return-requests")
def get_return_requests(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    statement = select(ReturnRequest).order_by(
        ReturnRequest.id.desc()
    )

    if status:
        statement = statement.where(
            ReturnRequest.status == status
        )

    return_requests = db.scalars(statement).all()

    return [
        {
            "id": return_request.id,
            "return_no": return_request.return_no,
            "order_id": return_request.order_id,
            "reason": return_request.reason,
            "status": return_request.status,
            "reviewed_by": return_request.reviewed_by,
            "reviewed_at": return_request.reviewed_at,
            "review_note": return_request.review_note,
            "created_at": return_request.created_at,
            "updated_at": return_request.updated_at,
        }
        for return_request in return_requests
    ]


@app.post("/return-requests/{return_request_id}/approve")
def approve_return_request(
    return_request_id: int,
    db: Session = Depends(get_db),
):
    return_request = db.get(ReturnRequest, return_request_id)

    if return_request is None:
        raise HTTPException(
            status_code=404,
            detail="退货申请不存在",
        )

    if return_request.status != "pending_review":
        raise HTTPException(
            status_code=400,
            detail="该退货申请已处理，不能重复批准",
        )

    started_at = time.perf_counter()

    try:
        return_request.status = "approved"
        return_request.reviewed_by = "admin"
        return_request.reviewed_at = datetime.now()
        return_request.review_note = "人工审核通过，可按退货指引寄回商品。"

        db.commit()
        db.refresh(return_request)

        duration_ms = round(
            (time.perf_counter() - started_at) * 1000,
            2,
        )

        db.add(
            ToolLog(
                session_id=None,
                tool_name="approve_return_request",
                reason="人工审核通过退货申请",
                input_params=json.dumps(
                    {
                        "return_request_id": return_request.id,
                        "return_no": return_request.return_no,
                        "order_id": return_request.order_id,
                    },
                    ensure_ascii=False,
                ),
                output_result=json.dumps(
                    {
                        "success": True,
                        "message": "退货申请已审核通过",
                        "status": return_request.status,
                    },
                    ensure_ascii=False,
                ),
                status="success",
                duration_ms=duration_ms,
                error_message=None,
            )
        )

        db.commit()

        return {
            "message": "退货申请已审核通过",
            "return_request_id": return_request.id,
            "return_no": return_request.return_no,
            "status": return_request.status,
        }
    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"批准退货申请失败：{error}",
        ) from error


@app.post("/return-requests/{return_request_id}/reject")
def reject_return_request(
    return_request_id: int,
    request: RejectReturnRequest,
    db: Session = Depends(get_db),
):
    return_request = db.get(ReturnRequest, return_request_id)

    if return_request is None:
        raise HTTPException(
            status_code=404,
            detail="退货申请不存在",
        )

    if return_request.status != "pending_review":
        raise HTTPException(
            status_code=400,
            detail="该退货申请已处理，不能重复拒绝",
        )

    review_note = request.review_note.strip()

    if not review_note:
        raise HTTPException(
            status_code=400,
            detail="拒绝退货时必须填写原因",
        )

    started_at = time.perf_counter()

    try:
        return_request.status = "rejected"
        return_request.reviewed_by = "admin"
        return_request.reviewed_at = datetime.now()
        return_request.review_note = review_note

        db.commit()
        db.refresh(return_request)

        duration_ms = round(
            (time.perf_counter() - started_at) * 1000,
            2,
        )

        db.add(
            ToolLog(
                session_id=None,
                tool_name="reject_return_request",
                reason="人工拒绝退货申请",
                input_params=json.dumps(
                    {
                        "return_request_id": return_request.id,
                        "return_no": return_request.return_no,
                        "review_note": review_note,
                    },
                    ensure_ascii=False,
                ),
                output_result=json.dumps(
                    {
                        "success": True,
                        "message": "退货申请已拒绝",
                        "status": return_request.status,
                    },
                    ensure_ascii=False,
                ),
                status="success",
                duration_ms=duration_ms,
                error_message=None,
            )
        )

        db.commit()

        return {
            "message": "退货申请已拒绝",
            "return_request_id": return_request.id,
            "return_no": return_request.return_no,
            "status": return_request.status,
        }
    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"拒绝退货申请失败：{error}",
        ) from error
