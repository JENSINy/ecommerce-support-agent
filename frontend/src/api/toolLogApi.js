import { apiRequest } from "./client";

export function getToolLogs(sessionId) {
  return apiRequest(
    `/tool-logs?session_id=${encodeURIComponent(sessionId)}`,
  );
}
