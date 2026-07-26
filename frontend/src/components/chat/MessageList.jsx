import MessageItem from "./MessageItem";

function MessageList({ messages, sending }) {
  return (
    <div className="messages">
      {messages.length === 0 && (
        <div className="empty-state">
          <h3>开始售后咨询</h3>
          <p>例如：帮我查询订单 ORD001</p>
        </div>
      )}

      {messages.map((message) => (
        <MessageItem
          key={message.id}
          message={message}
        />
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
  );
}

export default MessageList;
