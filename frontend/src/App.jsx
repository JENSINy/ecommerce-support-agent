import { useCallback, useState } from "react";

import ChatPanel from "./components/chat/ChatPanel";
import ErrorBanner from "./components/common/ErrorBanner";
import RefundApprovalSection from "./components/approvals/RefundApprovalSection";
import ReturnApprovalSection from "./components/approvals/ReturnApprovalSection";
import ToolLogPanel from "./components/logs/ToolLogPanel";

import { useConversation } from "./hooks/useConversation";
import { useRefundRequests } from "./hooks/useRefundRequests";
import { useReturnRequests } from "./hooks/useReturnRequests";

function App() {
  const [error, setError] = useState("");

  const refundRequests = useRefundRequests(setError);
  const returnRequests = useReturnRequests(setError);

  const refreshApprovalLists = useCallback(async () => {
    await Promise.all([
      refundRequests.loadRefundRequests(),
      returnRequests.loadReturnRequests(),
    ]);
  }, [
    refundRequests.loadRefundRequests,
    returnRequests.loadReturnRequests,
  ]);

  const conversation = useConversation({
    onError: setError,
    onRequestCreated: refreshApprovalLists,
  });

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h1>电商售后 Agent 工作台</h1>
          <p>
            订单查询、售后申请、工具日志与人工审批
          </p>
        </div>

        <button
          type="button"
          onClick={conversation.startNewConversation}
        >
          新建会话
        </button>
      </header>

      <ErrorBanner message={error} />

      <main className="workspace">
        <ChatPanel
          sessionId={conversation.sessionId}
          messages={conversation.messages}
          input={conversation.input}
          sending={conversation.sending}
          onInputChange={conversation.setInput}
          onSubmit={conversation.handleSubmit}
        />

        <ToolLogPanel
          toolLogs={conversation.toolLogs}
        />
      </main>

      <RefundApprovalSection
        refundRequests={refundRequests.refundRequests}
        loading={refundRequests.loading}
        processingId={refundRequests.processingId}
        onRefresh={refundRequests.loadRefundRequests}
        onApprove={refundRequests.approve}
        onReject={refundRequests.reject}
      />

      <ReturnApprovalSection
        returnRequests={returnRequests.returnRequests}
        loading={returnRequests.loading}
        processingId={returnRequests.processingId}
        onRefresh={returnRequests.loadReturnRequests}
        onApprove={returnRequests.approve}
        onReject={returnRequests.reject}
      />
    </div>
  );
}

export default App;
