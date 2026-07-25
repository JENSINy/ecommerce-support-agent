from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    order_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    product_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    created_at: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<Order("
            f"order_id={self.order_id}, "
            f"user_id={self.user_id}, "
            f"amount={self.amount}"
            f")>"
        )


class Conversation(Base):
    __tablename__ = "conversations"

    session_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    session_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )


class ToolLog(Base):
    __tablename__ = "tool_logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    session_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )
    tool_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    input_params: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    output_result: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    duration_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )


class Logistics(Base):
    __tablename__ = "logistics"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    order_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    company: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    tracking_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    latest_location: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )
    updated_at: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )


class Faq(Base):
    __tablename__ = "faqs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    question: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )
    answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    keywords: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


class ReturnRequest(Base):
    __tablename__ = "return_requests"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    return_no: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    order_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending_review",
        index=True,
    )
    reviewed_by: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    review_note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class RefundRequest(Base):
    __tablename__ = "refund_requests"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    refund_no: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    order_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending_approval",
        index=True,
    )
    approved_by: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    rejected_by: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    rejected_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    reject_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
