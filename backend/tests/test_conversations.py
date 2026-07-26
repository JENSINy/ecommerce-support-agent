def test_get_conversation_messages(client, test_data):
    response = client.get(
        f"/conversations/{test_data['session_id']}/messages",
    )

    assert response.status_code == 200

    messages = response.json()

    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "查询测试订单"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "这是测试回复"


def test_get_missing_conversation(client):
    response = client.get(
        "/conversations/SESSION_NOT_FOUND/messages",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "会话不存在"


def test_chat_rejects_empty_message(client):
    response = client.post(
        "/chat",
        json={
            "message": "   ",
            "session_id": None,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "消息不能为空"
