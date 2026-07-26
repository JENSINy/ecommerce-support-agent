import { apiRequest } from "./client";

export function getConversationMessages(sessionId) {
  return apiRequest(
    `/conversations/${encodeURIComponent(sessionId)}/messages`,
  ).catch((error) => {
    if (error.message === "会话不存在") {
      return [];
    }

    throw error;
  });
}

export function sendChatMessage(message, sessionId) {
  return apiRequest("/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      session_id: sessionId || null,
    }),
  });
}
