import { apiRequest } from "./client";

export function getRefundRequests() {
  return apiRequest("/refund-requests");
}

export function approveRefundRequest(refundRequestId) {
  return apiRequest(
    `/refund-requests/${refundRequestId}/approve`,
    {
      method: "POST",
    },
  );
}

export function rejectRefundRequest(
  refundRequestId,
  rejectReason,
) {
  return apiRequest(
    `/refund-requests/${refundRequestId}/reject`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        reject_reason: rejectReason,
      }),
    },
  );
}
