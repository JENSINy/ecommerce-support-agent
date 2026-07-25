from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, get_db
from models import (
    Base,
    Logistics,
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
def setup_test_database():
    # 每次运行测试前都重新创建独立测试数据库。
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()

    if TEST_DATABASE_PATH.exists():
        TEST_DATABASE_PATH.unlink()


@pytest.fixture()
def client():
    return TestClient(app)


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

        db.add_all([
            order,
            logistics,
            refund_request,
            return_request,
        ])

        db.commit()
        db.refresh(refund_request)
        db.refresh(return_request)

        yield {
            "order_id": order.order_id,
            "refund_request_id": refund_request.id,
            "return_request_id": return_request.id,
        }
    finally:
        db.close()

        # 每个测试结束后清空数据，避免测试互相影响。
        cleanup_db = TestSessionLocal()

        try:
            cleanup_db.query(RefundRequest).delete()
            cleanup_db.query(ReturnRequest).delete()
            cleanup_db.query(Logistics).delete()
            cleanup_db.query(Order).delete()
            cleanup_db.commit()
        finally:
            cleanup_db.close()


def test_get_existing_order(client, test_data):
    response = client.get(
        f"/orders/{test_data['order_id']}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["order_id"] == "ORDTEST001"
    assert data["product_name"] == "测试无线键盘"
    assert data["amount"] == 399
    assert data["status"] == "shipped"


def test_get_missing_order(client):
    response = client.get("/orders/NOT_FOUND")

    assert response.status_code == 404
    assert response.json()["detail"] == "订单不存在"


def test_get_logistics_records(client, test_data):
    response = client.get("/tool-logs")

    # 当前测试只确认日志接口可以正常访问。
    # 物流工具本身由 Agent 调用，因此不在这里请求 DeepSeek。
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_approve_refund_updates_order_status(client, test_data):
    response = client.post(
        "/refund-requests/"
        f"{test_data['refund_request_id']}/approve",
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["status"] == "approved"
    assert response_data["order_status"] == "refunded"

    refund_response = client.get("/refund-requests")
    refund_requests = refund_response.json()

    test_refund = next(
        request
        for request in refund_requests
        if request["id"] == test_data["refund_request_id"]
    )

    assert test_refund["status"] == "approved"
    assert test_refund["approved_by"] == "admin"


def test_approve_return_updates_return_status(client, test_data):
    response = client.post(
        "/return-requests/"
        f"{test_data['return_request_id']}/approve",
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["status"] == "approved"

    return_response = client.get("/return-requests")
    return_requests = return_response.json()

    test_return = next(
        request
        for request in return_requests
        if request["id"] == test_data["return_request_id"]
    )

    assert test_return["status"] == "approved"
    assert test_return["reviewed_by"] == "admin"
    assert "可按退货指引寄回商品" in test_return["review_note"]


def test_reject_return_requires_review_note(client, test_data):
    response = client.post(
        "/return-requests/"
        f"{test_data['return_request_id']}/reject",
        json={
            "review_note": "",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "拒绝退货时必须填写原因"
