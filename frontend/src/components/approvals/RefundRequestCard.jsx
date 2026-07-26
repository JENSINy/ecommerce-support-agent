import StatusBadge from "../common/StatusBadge";
import { formatTime } from "../../utils/formatters";

function RefundRequestCard({
  refundRequest,
  processing,
  onApprove,
  onReject,
}) {
  const isPending =
    refundRequest.status === "pending_approval";

  return (
    <article className="request-card">
      <div className="request-card-header">
        <strong>{refundRequest.refund_no}</strong>

        <StatusBadge status={refundRequest.status} />
      </div>

      <p>
        <b>订单号：</b>
        {refundRequest.order_id}
      </p>

      <p>
        <b>退款金额：</b>
        {refundRequest.amount} 元
      </p>

      <p>
        <b>退款原因：</b>
        {refundRequest.reason}
      </p>

      <p>
        <b>申请时间：</b>
        {formatTime(refundRequest.created_at)}
      </p>

      {refundRequest.status === "approved" && (
        <p className="approved-info">
          <b>审批人：</b>
          {refundRequest.approved_by}

          <br />

          <b>审批时间：</b>
          {formatTime(refundRequest.approved_at)}
        </p>
      )}

      {refundRequest.status === "rejected" && (
        <p className="rejected-info">
          <b>拒绝原因：</b>
          {refundRequest.reject_reason}
        </p>
      )}

      {isPending && (
        <div className="approval-actions">
          <button
            className="approve-button"
            type="button"
            onClick={() => onApprove(refundRequest)}
            disabled={processing}
          >
            {processing ? "处理中" : "批准退款"}
          </button>

          <button
            className="reject-button"
            type="button"
            onClick={() => onReject(refundRequest)}
            disabled={processing}
          >
            拒绝
          </button>
        </div>
      )}
    </article>
  );
}

export default RefundRequestCard;
