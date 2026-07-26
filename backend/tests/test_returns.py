def find_request_by_id(requests, request_id):
    return next(request for request in requests if request["id"] == request_id)


def test_approve_return_updates_request_and_creates_log(
    client,
    test_data,
):
    return_request_id = test_data["return_request_id"]

    response = client.post(
        f"/return-requests/{return_request_id}/approve",
    )

    assert response.status_code == 200
    assert response.json()["status"] == "approved"

    list_response = client.get("/return-requests")
    approved_return = find_request_by_id(
        list_response.json(),
        return_request_id,
    )

    assert approved_return["status"] == "approved"
    assert approved_return["reviewed_by"] == "admin"
    assert approved_return["reviewed_at"] is not None
    assert "可按退货指引寄回商品" in approved_return["review_note"]

    log_response = client.get("/tool-logs")

    approval_log = next(
        log
        for log in log_response.json()
        if log["tool_name"] == "approve_return_request"
    )

    assert approval_log["status"] == "success"
    assert approval_log["reason"] == "人工审核通过退货申请"


def test_return_cannot_be_approved_twice(client, test_data):
    return_request_id = test_data["return_request_id"]

    first_response = client.post(
        f"/return-requests/{return_request_id}/approve",
    )
    second_response = client.post(
        f"/return-requests/{return_request_id}/approve",
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "该退货申请已处理，不能重复批准"


def test_reject_return_requires_review_note(client, test_data):
    response = client.post(
        f"/return-requests/{test_data['return_request_id']}/reject",
        json={
            "review_note": "",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "拒绝退货时必须填写原因"


def test_reject_return_updates_request_and_creates_log(
    client,
    test_data,
):
    return_request_id = test_data["return_request_id"]

    response = client.post(
        f"/return-requests/{return_request_id}/reject",
        json={
            "review_note": "商品已经超过退货期限",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"

    list_response = client.get("/return-requests")
    rejected_return = find_request_by_id(
        list_response.json(),
        return_request_id,
    )

    assert rejected_return["status"] == "rejected"
    assert rejected_return["reviewed_by"] == "admin"
    assert rejected_return["review_note"] == "商品已经超过退货期限"

    log_response = client.get("/tool-logs")

    rejection_log = next(
        log
        for log in log_response.json()
        if log["tool_name"] == "reject_return_request"
    )

    assert rejection_log["status"] == "success"
    assert rejection_log["reason"] == "人工拒绝退货申请"
