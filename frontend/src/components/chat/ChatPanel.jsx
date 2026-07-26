import ChatComposer from "./ChatComposer";
import MessageList from "./MessageList";

function ChatPanel({
  sessionId,
  messages,
  input,
  sending,
  onInputChange,
  onSubmit,
}) {
  return (
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

      <MessageList
        messages={messages}
        sending={sending}
      />

      <ChatComposer
        input={input}
        sending={sending}
        onInputChange={onInputChange}
        onSubmit={onSubmit}
      />
    </section>
  );
}

export default ChatPanel;
