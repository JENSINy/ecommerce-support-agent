import { apiRequest } from "./client";

export function getReturnRequests() {
  return apiRequest("/return-requests");
}

export function approveReturnRequest(returnRequestId) {
  return apiRequest(
    `/return-requests/${returnRequestId}/approve`,
    {
      method: "POST",
    },
  );
}

export function rejectReturnRequest(
  returnRequestId,
  reviewNote,
) {
  return apiRequest(
    `/return-requests/${returnRequestId}/reject`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        review_note: reviewNote,
      }),
    },
  );
}
