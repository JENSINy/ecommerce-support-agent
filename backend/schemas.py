from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="用户消息")
    session_id: str | None = Field(
        default=None,
        description="会话 ID；为空时创建新会话",
    )


class ChatResponse(BaseModel):
    session_id: str
    reply: str


class RejectRefundRequest(BaseModel):
    reject_reason: str = Field(..., description="拒绝退款原因")


class RejectReturnRequest(BaseModel):
    review_note: str = Field(..., description="退货审核备注")
