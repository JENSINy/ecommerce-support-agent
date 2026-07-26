import { useCallback, useEffect, useState } from "react";

import {
  approveReturnRequest,
  getReturnRequests,
  rejectReturnRequest,
} from "../api/returnApi";

export function useReturnRequests(onError) {
  const [returnRequests, setReturnRequests] = useState([]);
  const [loading, setLoading] = useState(false);
  const [processingId, setProcessingId] = useState(null);

  const loadReturnRequests = useCallback(async () => {
    setLoading(true);

    try {
      const data = await getReturnRequests();
      setReturnRequests(data);
    } catch (error) {
      onError(error.message);
    } finally {
      setLoading(false);
    }
  }, [onError]);

  useEffect(() => {
    loadReturnRequests();
  }, [loadReturnRequests]);

  async function approve(returnRequest) {
    const confirmed = window.confirm(
      `确认批准退货吗？\n订单：${returnRequest.order_id}\n退货原因：${returnRequest.reason}`,
    );

    if (!confirmed) {
      return;
    }

    onError("");
    setProcessingId(returnRequest.id);

    try {
      await approveReturnRequest(returnRequest.id);
      await loadReturnRequests();
    } catch (error) {
      onError(error.message);
    } finally {
      setProcessingId(null);
    }
  }

  async function reject(returnRequest) {
    const reviewNote = window.prompt(
      `请输入拒绝退货申请 ${returnRequest.return_no} 的原因：`,
    );

    if (reviewNote === null) {
      return;
    }

    const normalizedNote = reviewNote.trim();

    if (!normalizedNote) {
      onError("拒绝退货时必须填写原因");
      return;
    }

    onError("");
    setProcessingId(returnRequest.id);

    try {
      await rejectReturnRequest(
        returnRequest.id,
        normalizedNote,
      );

      await loadReturnRequests();
    } catch (error) {
      onError(error.message);
    } finally {
      setProcessingId(null);
    }
  }

  return {
    returnRequests,
    loading,
    processingId,
    loadReturnRequests,
    approve,
    reject,
  };
}
