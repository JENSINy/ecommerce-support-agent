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


def test_order_id_is_normalized(client, test_data):
    response = client.get("/orders/ordtest001")

    assert response.status_code == 200
    assert response.json()["order_id"] == test_data["order_id"]


def test_get_missing_order(client):
    response = client.get("/orders/NOT_FOUND")

    assert response.status_code == 404
    assert response.json()["detail"] == "订单不存在"
