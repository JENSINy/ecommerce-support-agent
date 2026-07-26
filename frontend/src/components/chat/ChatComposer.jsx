function ChatComposer({
  input,
  sending,
  onInputChange,
  onSubmit,
}) {
  return (
    <form className="chat-form" onSubmit={onSubmit}>
      <textarea
        value={input}
        onChange={(event) =>
          onInputChange(event.target.value)
        }
        placeholder="请输入问题，例如：帮我查询订单 ORD001"
        disabled={sending}
        rows="3"
      />

      <button
        type="submit"
        disabled={sending || !input.trim()}
      >
        {sending ? "处理中" : "发送"}
      </button>
    </form>
  );
}

export default ChatComposer;
