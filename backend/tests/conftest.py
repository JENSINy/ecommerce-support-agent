import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 必须在导入 main 之前设置。
# 当前 Agent 模块加载时需要 DEEPSEEK_API_KEY。
os.environ.setdefault("DEEPSEEK_API_KEY", "test-key")

from main import app, get_db
from models import (
    Base,
    Conversation,
    Logistics,
    Message,
    Order,
    RefundRequest,
    ReturnRequest,
)

TEST_DATABASE_PATH = Path("ecommerce_test.db")

test_engine = create_engine(
    "sqlite:///./ecommerce_test.db",
    connect_args={"check_same_thread": False},
)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def override_get_db():
    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def configure_test_application():
    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()
    test_engine.dispose()

    if TEST_DATABASE_PATH.exists():
        TEST_DATABASE_PATH.unlink()


@pytest.fixture(autouse=True)
def reset_test_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    yield


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def test_data():
    db = TestSessionLocal()

    try:
        order = Order(
            order_id="ORDTEST001",
            user_id="USERTEST001",
            product_name="测试无线键盘",
            quantity=1,
            amount=399,
            status="shipped",
            created_at="2026-07-25",
        )

        logistics = Logistics(
            order_id="ORDTEST001",
            company="测试快递",
            tracking_number="TEST123456789",
            status="运输中",
            latest_location="测试包裹正在配送中心等待派送。",
            updated_at="2026-07-25 10:00:00",
        )

        refund_request = RefundRequest(
            refund_no="REFTEST001",
            order_id="ORDTEST001",
            amount=399,
            reason="测试退款申请",
            status="pending_approval",
        )

        return_request = ReturnRequest(
            return_no="RETTEST001",
            order_id="ORDTEST001",
            reason="测试退货申请",
            status="pending_review",
        )

        conversation = Conversation(
            session_id="SESSIONTEST001",
        )

        messages = [
            Message(
                session_id="SESSIONTEST001",
                role="user",
                content="查询测试订单",
            ),
            Message(
                session_id="SESSIONTEST001",
                role="assistant",
                content="这是测试回复",
            ),
        ]

        db.add_all(
            [
                order,
                logistics,
                refund_request,
                return_request,
                conversation,
                *messages,
            ]
        )

        db.commit()
        db.refresh(refund_request)
        db.refresh(return_request)

        return {
            "order_id": order.order_id,
            "refund_request_id": refund_request.id,
            "return_request_id": return_request.id,
            "session_id": conversation.session_id,
        }
    finally:
        db.close()
