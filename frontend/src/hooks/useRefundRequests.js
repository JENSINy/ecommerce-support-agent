import { useCallback, useEffect, useState } from "react";

import {
  approveRefundRequest,
  getRefundRequests,
  rejectRefundRequest,
} from "../api/refundApi";

export function useRefundRequests(onError) {
  const [refundRequests, setRefundRequests] = useState([]);
  const [loading, setLoading] = useState(false);
  const [processingId, setProcessingId] = useState(null);

  const loadRefundRequests = useCallback(async () => {
    setLoading(true);

    try {
      const data = await getRefundRequests();
      setRefundRequests(data);
    } catch (error) {
      onError(error.message);
    } finally {
      setLoading(false);
    }
  }, [onError]);

  useEffect(() => {
    loadRefundRequests();
  }, [loadRefundRequests]);

  async function approve(refundRequest) {
    const confirmed = window.confirm(
      `确认批准退款吗？\n订单：${refundRequest.order_id}\n金额：${refundRequest.amount} 元`,
    );

    if (!confirmed) {
      return;
    }

    onError("");
    setProcessingId(refundRequest.id);

    try {
      await approveRefundRequest(refundRequest.id);
      await loadRefundRequests();
    } catch (error) {
      onError(error.message);
    } finally {
      setProcessingId(null);
    }
  }

  async function reject(refundRequest) {
    const rejectReason = window.prompt(
      `请输入拒绝退款申请 ${refundRequest.refund_no} 的原因：`,
    );

    if (rejectReason === null) {
      return;
    }

    const normalizedReason = rejectReason.trim();

    if (!normalizedReason) {
      onError("拒绝退款时必须填写原因");
      return;
    }

    onError("");
    setProcessingId(refundRequest.id);

    try {
      await rejectRefundRequest(
        refundRequest.id,
        normalizedReason,
      );

      await loadRefundRequests();
    } catch (error) {
      onError(error.message);
    } finally {
      setProcessingId(null);
    }
  }

  return {
    refundRequests,
    loading,
    processingId,
    loadRefundRequests,
    approve,
    reject,
  };
}
