def find_request_by_id(requests, request_id):
    return next(request for request in requests if request["id"] == request_id)


def test_approve_refund_updates_order_and_creates_log(
    client,
    test_data,
):
    refund_request_id = test_data["refund_request_id"]

    response = client.post(
        f"/refund-requests/{refund_request_id}/approve",
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["status"] == "approved"
    assert response_data["order_status"] == "refunded"

    refund_response = client.get("/refund-requests")
    refund_requests = refund_response.json()

    approved_refund = find_request_by_id(
        refund_requests,
        refund_request_id,
    )

    assert approved_refund["status"] == "approved"
    assert approved_refund["approved_by"] == "admin"
    assert approved_refund["approved_at"] is not None

    log_response = client.get("/tool-logs")

    assert log_response.status_code == 200

    refund_log = next(
        log for log in log_response.json() if log["tool_name"] == "issue_refund"
    )

    assert refund_log["status"] == "success"
    assert refund_log["reason"] == "人工审批通过退款申请后执行退款"


def test_refund_cannot_be_approved_twice(client, test_data):
    refund_request_id = test_data["refund_request_id"]

    first_response = client.post(
        f"/refund-requests/{refund_request_id}/approve",
    )
    second_response = client.post(
        f"/refund-requests/{refund_request_id}/approve",
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "该退款申请已处理，不能重复批准"


def test_reject_refund_requires_reason(client, test_data):
    response = client.post(
        f"/refund-requests/{test_data['refund_request_id']}/reject",
        json={
            "reject_reason": "   ",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "拒绝退款时必须填写原因"


def test_reject_refund_updates_request(client, test_data):
    refund_request_id = test_data["refund_request_id"]

    response = client.post(
        f"/refund-requests/{refund_request_id}/reject",
        json={
            "reject_reason": "商品不符合退款条件",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"

    list_response = client.get("/refund-requests")
    rejected_refund = find_request_by_id(
        list_response.json(),
        refund_request_id,
    )

    assert rejected_refund["status"] == "rejected"
    assert rejected_refund["rejected_by"] == "admin"
    assert rejected_refund["reject_reason"] == "商品不符合退款条件"
