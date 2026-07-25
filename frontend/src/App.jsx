import { useEffect, useState } from "react";

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");

function formatTime(value) {
  if (!value) {
    return "";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString("zh-CN");
}

function formatJson(value) {
  if (!value) {
    return "无";
  }

  try {
    return JSON.stringify(JSON.parse(value), null, 2);
  } catch {
    return value;
  }
}

function getStatusText(status) {
  const statusMap = {
    success: "成功",
    not_found: "未找到",
    failed: "失败",
    pending_approval: "待审批",
    pending_review: "待审核",
    approved: "已批准",
    rejected: "已拒绝",
  };

  return statusMap[status] || status;
}

function App() {
  const [sessionId, setSessionId] = useState(
    localStorage.getItem("ecommerce_session_id") || "",
  );
  const [messages, setMessages] = useState([]);
  const [toolLogs, setToolLogs] = useState([]);
  const [refundRequests, setRefundRequests] = useState([]);
  const [returnRequests, setReturnRequests] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [loadingApprovals, setLoadingApprovals] = useState(false);
  const [loadingReturns, setLoadingReturns] = useState(false);
  const [processingRefundId, setProcessingRefundId] = useState(null);
  const [processingReturnId, setProcessingReturnId] = useState(null);
  const [error, setError] = useState("");

  async function loadMessages(currentSessionId) {
    const response = await fetch(
      `${API_BASE_URL}/conversations/${encodeURIComponent(
        currentSessionId,
      )}/messages`,
    );

    if (response.status === 404) {
      return [];
    }

    if (!response.ok) {
      throw new Error("读取聊天记录失败");
    }

    return response.json();
  }

  async function loadToolLogs(currentSessionId) {
    const response = await fetch(
      `${API_BASE_URL}/tool-logs?session_id=${encodeURIComponent(
        currentSessionId,
      )}`,
    );

    if (!response.ok) {
      throw new Error("读取工具日志失败");
    }

    return response.json();
  }

  async function loadRefundRequests() {
    setLoadingApprovals(true);

    try {
      const response = await fetch(`${API_BASE_URL}/refund-requests`);

      if (!response.ok) {
        throw new Error("读取退款审批列表失败");
      }

      const data = await response.json();
      setRefundRequests(data);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoadingApprovals(false);
    }
  }

  async function loadReturnRequests() {
    setLoadingReturns(true);

    try {
      const response = await fetch(`${API_BASE_URL}/return-requests`);

      if (!response.ok) {
        throw new Error("读取退货审核列表失败");
      }

      const data = await response.json();
      setReturnRequests(data);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoadingReturns(false);
    }
  }

  async function restoreConversation() {
    if (!sessionId) {
      return;
    }

    try {
      const [savedMessages, savedLogs] = await Promise.all([
        loadMessages(sessionId),
        loadToolLogs(sessionId),
      ]);

      setMessages(savedMessages);
      setToolLogs(savedLogs);
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  useEffect(() => {
    restoreConversation();
  }, [sessionId]);

  useEffect(() => {
    loadRefundRequests();
    loadReturnRequests();
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();

    const message = input.trim();

    if (!message || sending) {
      return;
    }

    setInput("");
    setError("");
    setSending(true);

    const temporaryId = `temp-${Date.now()}`;

    setMessages((currentMessages) => [
      ...currentMessages,
      {
        id: temporaryId,
        role: "user",
        content: message,
        created_at: new Date().toISOString(),
      },
    ]);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message,
          session_id: sessionId || null,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "发送消息失败");
      }

      setSessionId(data.session_id);
      localStorage.setItem("ecommerce_session_id", data.session_id);

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: data.reply,
          created_at: new Date().toISOString(),
        },
      ]);

      const latestLogs = await loadToolLogs(data.session_id);

      setToolLogs(latestLogs);

      // 对话提交后刷新人工审核列表。
      await loadRefundRequests();
      await loadReturnRequests();
    } catch (requestError) {
      setError(requestError.message);

      setMessages((currentMessages) =>
        currentMessages.filter(
          (messageItem) => messageItem.id !== temporaryId,
        ),
      );

      setInput(message);
    } finally {
      setSending(false);
    }
  }

  async function handleApproveRefund(refundRequest) {
    const confirmed = window.confirm(
      `确认批准退款吗？\n订单：${refundRequest.order_id}\n金额：${refundRequest.amount} 元`,
    );

    if (!confirmed) {
      return;
    }

    setError("");
    setProcessingRefundId(refundRequest.id);

    try {
      const response = await fetch(
        `${API_BASE_URL}/refund-requests/${refundRequest.id}/approve`,
        {
          method: "POST",
        },
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "批准退款失败");
      }

      await loadRefundRequests();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setProcessingRefundId(null);
    }
  }

  async function handleRejectRefund(refundRequest) {
    const rejectReason = window.prompt(
      `请输入拒绝退款申请 ${refundRequest.refund_no} 的原因：`,
    );

    if (rejectReason === null) {
      return;
    }

    if (!rejectReason.trim()) {
      setError("拒绝退款时必须填写原因");
      return;
    }

    setError("");
    setProcessingRefundId(refundRequest.id);

    try {
      const response = await fetch(
        `${API_BASE_URL}/refund-requests/${refundRequest.id}/reject`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            reject_reason: rejectReason.trim(),
          }),
        },
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "拒绝退款失败");
      }

      await loadRefundRequests();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setProcessingRefundId(null);
    }
  }

  async function handleApproveReturn(returnRequest) {
    const confirmed = window.confirm(
      `确认批准退货吗？\n订单：${returnRequest.order_id}\n退货原因：${returnRequest.reason}`,
    );

    if (!confirmed) {
      return;
    }

    setError("");
    setProcessingReturnId(returnRequest.id);

    try {
      const response = await fetch(
        `${API_BASE_URL}/return-requests/${returnRequest.id}/approve`,
        {
          method: "POST",
        },
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "批准退货失败");
      }

      await loadReturnRequests();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setProcessingReturnId(null);
    }
  }

  async function handleRejectReturn(returnRequest) {
    const reviewNote = window.prompt(
      `请输入拒绝退货申请 ${returnRequest.return_no} 的原因：`,
    );

    if (reviewNote === null) {
      return;
    }

    if (!reviewNote.trim()) {
      setError("拒绝退货时必须填写原因");
      return;
    }

    setError("");
    setProcessingReturnId(returnRequest.id);

    try {
      const response = await fetch(
        `${API_BASE_URL}/return-requests/${returnRequest.id}/reject`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            review_note: reviewNote.trim(),
          }),
        },
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "拒绝退货失败");
      }

      await loadReturnRequests();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setProcessingReturnId(null);
    }
  }

  function handleNewConversation() {
    localStorage.removeItem("ecommerce_session_id");
    setSessionId("");
    setMessages([]);
    setToolLogs([]);
    setInput("");
    setError("");
  }

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h1>电商售后 Agent 工作台</h1>
          <p>订单查询、售后申请、工具日志与人工审批</p>
        </div>

        <button type="button" onClick={handleNewConversation}>
          新建会话
        </button>
      </header>

      {error && <div className="global-error">{error}</div>}

      <main className="workspace">
        <section className="chat-panel">
          <div className="panel-header">
            <div>
              <h2>客服对话</h2>
              <p>
                会话编号：
                {sessionId || "发送第一条消息后自动生成"}
              </p>
            </div>
          </div>

          <div className="messages">
            {messages.length === 0 && (
              <div className="empty-state">
                <h3>开始售后咨询</h3>
                <p>例如：帮我查询订单 ORD001</p>
              </div>
            )}

            {messages.map((message) => (
              <div
                className={`message-row ${
                  message.role === "user" ? "user-row" : "agent-row"
                }`}
                key={message.id}
              >
                <div className="message">
                  <strong>
                    {message.role === "user" ? "用户" : "Agent"}
                  </strong>
                  <div>{message.content}</div>
                  <small>{formatTime(message.created_at)}</small>
                </div>
              </div>
            ))}

            {sending && (
              <div className="message-row agent-row">
                <div className="message">
                  <strong>Agent</strong>
                  <div>正在分析问题并调用工具……</div>
                </div>
              </div>
            )}
          </div>

          <form className="chat-form" onSubmit={handleSubmit}>
            <textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="请输入问题，例如：帮我查询订单 ORD001"
              disabled={sending}
              rows="3"
            />

            <button type="submit" disabled={sending || !input.trim()}>
              {sending ? "处理中" : "发送"}
            </button>
          </form>
        </section>

        <section className="log-panel">
          <div className="panel-header">
            <div>
              <h2>工具调用日志</h2>
              <p>Agent 的工具选择、参数和执行结果</p>
            </div>
            <span>{toolLogs.length} 条</span>
          </div>

          <div className="logs">
            {toolLogs.length === 0 && (
              <div className="empty-state">
                <h3>暂无工具调用</h3>
                <p>查询订单、物流或 FAQ 后，日志会显示在这里。</p>
              </div>
            )}

            {toolLogs.map((log) => (
              <article className="log-card" key={log.id}>
                <div className="log-title">
                  <strong>{log.tool_name}</strong>
                  <span className={`status ${log.status}`}>
                    {getStatusText(log.status)}
                  </span>
                </div>

                <p>
                  <b>调用原因：</b>
                  {log.reason}
                </p>
                <p>
                  <b>执行耗时：</b>
                  {log.duration_ms} ms
                </p>
                <p>
                  <b>调用时间：</b>
                  {formatTime(log.created_at)}
                </p>

                <details>
                  <summary>查看工具参数</summary>
                  <pre>{formatJson(log.input_params)}</pre>
                </details>

                <details>
                  <summary>查看执行结果</summary>
                  <pre>{formatJson(log.output_result)}</pre>
                </details>

                {log.error_message && (
                  <p className="log-error">
                    <b>失败原因：</b>
                    {log.error_message}
                  </p>
                )}
              </article>
            ))}
          </div>
        </section>
      </main>

      <section className="approval-section">
        <div className="approval-header">
          <div>
            <h2>退款审批中心</h2>
            <p>退款属于敏感操作，必须由人工批准或拒绝。</p>
          </div>

          <button
            className="refresh-button"
            type="button"
            onClick={loadRefundRequests}
            disabled={loadingApprovals}
          >
            {loadingApprovals ? "刷新中" : "刷新列表"}
          </button>
        </div>

        {refundRequests.length === 0 && !loadingApprovals && (
          <div className="approval-empty">
            暂无退款申请。用户提交退款申请后会显示在这里。
          </div>
        )}

        <div className="request-list">
          {refundRequests.map((refundRequest) => {
            const isPending =
              refundRequest.status === "pending_approval";
            const isProcessing =
              processingRefundId === refundRequest.id;

            return (
              <article className="request-card" key={refundRequest.id}>
                <div className="request-card-header">
                  <strong>{refundRequest.refund_no}</strong>
                  <span className={`status ${refundRequest.status}`}>
                    {getStatusText(refundRequest.status)}
                  </span>
                </div>

                <p>
                  <b>订单号：</b>
                  {refundRequest.order_id}
                </p>
                <p>
                  <b>退款金额：</b>
                  {refundRequest.amount} 元
                </p>
                <p>
                  <b>退款原因：</b>
                  {refundRequest.reason}
                </p>
                <p>
                  <b>申请时间：</b>
                  {formatTime(refundRequest.created_at)}
                </p>

                {refundRequest.status === "approved" && (
                  <p className="approved-info">
                    <b>审批人：</b>
                    {refundRequest.approved_by}
                    <br />
                    <b>审批时间：</b>
                    {formatTime(refundRequest.approved_at)}
                  </p>
                )}

                {refundRequest.status === "rejected" && (
                  <p className="rejected-info">
                    <b>拒绝原因：</b>
                    {refundRequest.reject_reason}
                  </p>
                )}

                {isPending && (
                  <div className="approval-actions">
                    <button
                      className="approve-button"
                      type="button"
                      onClick={() =>
                        handleApproveRefund(refundRequest)
                      }
                      disabled={isProcessing}
                    >
                      {isProcessing ? "处理中" : "批准退款"}
                    </button>

                    <button
                      className="reject-button"
                      type="button"
                      onClick={() =>
                        handleRejectRefund(refundRequest)
                      }
                      disabled={isProcessing}
                    >
                      拒绝
                    </button>
                  </div>
                )}
              </article>
            );
          })}
        </div>
      </section>

      <section className="approval-section">
        <div className="approval-header">
          <div>
            <h2>退货审核中心</h2>
            <p>审核通过后允许用户寄回商品，不会自动执行退款。</p>
          </div>

          <button
            className="refresh-button"
            type="button"
            onClick={loadReturnRequests}
            disabled={loadingReturns}
          >
            {loadingReturns ? "刷新中" : "刷新列表"}
          </button>
        </div>

        {returnRequests.length === 0 && !loadingReturns && (
          <div className="approval-empty">
            暂无退货申请。用户提交退货申请后会显示在这里。
          </div>
        )}

        <div className="request-list">
          {returnRequests.map((returnRequest) => {
            const isPending =
              returnRequest.status === "pending_review";
            const isProcessing =
              processingReturnId === returnRequest.id;

            return (
              <article className="request-card" key={returnRequest.id}>
                <div className="request-card-header">
                  <strong>{returnRequest.return_no}</strong>
                  <span className={`status ${returnRequest.status}`}>
                    {getStatusText(returnRequest.status)}
                  </span>
                </div>

                <p>
                  <b>订单号：</b>
                  {returnRequest.order_id}
                </p>
                <p>
                  <b>退货原因：</b>
                  {returnRequest.reason}
                </p>
                <p>
                  <b>申请时间：</b>
                  {formatTime(returnRequest.created_at)}
                </p>

                {returnRequest.status === "approved" && (
                  <p className="approved-info">
                    <b>审核人：</b>
                    {returnRequest.reviewed_by}
                    <br />
                    <b>审核时间：</b>
                    {formatTime(returnRequest.reviewed_at)}
                    <br />
                    <b>审核备注：</b>
                    {returnRequest.review_note}
                  </p>
                )}

                {returnRequest.status === "rejected" && (
                  <p className="rejected-info">
                    <b>拒绝原因：</b>
                    {returnRequest.review_note}
                  </p>
                )}

                {isPending && (
                  <div className="approval-actions">
                    <button
                      className="approve-button"
                      type="button"
                      onClick={() =>
                        handleApproveReturn(returnRequest)
                      }
                      disabled={isProcessing}
                    >
                      {isProcessing ? "处理中" : "批准退货"}
                    </button>

                    <button
                      className="reject-button"
                      type="button"
                      onClick={() =>
                        handleRejectReturn(returnRequest)
                      }
                      disabled={isProcessing}
                    >
                      拒绝
                    </button>
                  </div>
                )}
              </article>
            );
          })}
        </div>
      </section>
    </div>
  );
}

export default App;
