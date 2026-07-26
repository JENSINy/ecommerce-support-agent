import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  getConversationMessages,
  sendChatMessage,
} from "../api/chatApi";
import { getToolLogs } from "../api/toolLogApi";

const SESSION_STORAGE_KEY = "ecommerce_session_id";

export function useConversation({
  onError,
  onRequestCreated,
}) {
  const [sessionId, setSessionId] = useState(
    localStorage.getItem(SESSION_STORAGE_KEY) || "",
  );

  const [messages, setMessages] = useState([]);
  const [toolLogs, setToolLogs] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  const restoreConversation = useCallback(async () => {
    if (!sessionId) {
      return;
    }

    try {
      const [savedMessages, savedLogs] =
        await Promise.all([
          getConversationMessages(sessionId),
          getToolLogs(sessionId),
        ]);

      setMessages(savedMessages);
      setToolLogs(savedLogs);
    } catch (error) {
      onError(error.message);
    }
  }, [onError, sessionId]);

  useEffect(() => {
    restoreConversation();
  }, [restoreConversation]);

  async function handleSubmit(event) {
    event.preventDefault();

    const message = input.trim();

    if (!message || sending) {
      return;
    }

    setInput("");
    onError("");
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
      const data = await sendChatMessage(
        message,
        sessionId,
      );

      setSessionId(data.session_id);

      localStorage.setItem(
        SESSION_STORAGE_KEY,
        data.session_id,
      );

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: data.reply,
          created_at: new Date().toISOString(),
        },
      ]);

      const latestLogs = await getToolLogs(
        data.session_id,
      );

      setToolLogs(latestLogs);

      await onRequestCreated();
    } catch (error) {
      onError(error.message);

      setMessages((currentMessages) =>
        currentMessages.filter(
          (messageItem) =>
            messageItem.id !== temporaryId,
        ),
      );

      setInput(message);
    } finally {
      setSending(false);
    }
  }

  function startNewConversation() {
    localStorage.removeItem(SESSION_STORAGE_KEY);

    setSessionId("");
    setMessages([]);
    setToolLogs([]);
    setInput("");
    onError("");
  }

  return {
    sessionId,
    messages,
    toolLogs,
    input,
    sending,
    setInput,
    handleSubmit,
    startNewConversation,
  };
}
