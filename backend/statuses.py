from enum import StrEnum


class OrderStatus(StrEnum):
    REFUNDED = "refunded"


class RefundStatus(StrEnum):
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


class ReturnStatus(StrEnum):
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class ToolLogStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    NOT_FOUND = "not_found"
