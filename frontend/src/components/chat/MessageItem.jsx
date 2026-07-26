import { formatTime } from "../../utils/formatters";

function MessageItem({ message }) {
  const isUser = message.role === "user";

  return (
    <div
      className={`message-row ${
        isUser ? "user-row" : "agent-row"
      }`}
    >
      <div className="message">
        <strong>{isUser ? "用户" : "Agent"}</strong>

        <div>{message.content}</div>

        <small>{formatTime(message.created_at)}</small>
      </div>
    </div>
  );
}

export default MessageItem;
