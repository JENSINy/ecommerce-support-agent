import StatusBadge from "../common/StatusBadge";
import { formatTime } from "../../utils/formatters";

function ReturnRequestCard({
  returnRequest,
  processing,
  onApprove,
  onReject,
}) {
  const isPending =
    returnRequest.status === "pending_review";

  return (
    <article className="request-card">
      <div className="request-card-header">
        <strong>{returnRequest.return_no}</strong>

        <StatusBadge status={returnRequest.status} />
      </div>

      <p>
        <b>订单号：</b>
        {returnRequest.order_id}
      </p>

      <p>
        <b>退货原因：</b>
        {returnRequest.reason}
      </p>

      <p>
        <b>申请时间：</b>
        {formatTime(returnRequest.created_at)}
      </p>

      {returnRequest.status === "approved" && (
        <p className="approved-info">
          <b>审核人：</b>
          {returnRequest.reviewed_by}

          <br />

          <b>审核时间：</b>
          {formatTime(returnRequest.reviewed_at)}

          <br />

          <b>审核备注：</b>
          {returnRequest.review_note}
        </p>
      )}

      {returnRequest.status === "rejected" && (
        <p className="rejected-info">
          <b>拒绝原因：</b>
          {returnRequest.review_note}
        </p>
      )}

      {isPending && (
        <div className="approval-actions">
          <button
            className="approve-button"
            type="button"
            onClick={() => onApprove(returnRequest)}
            disabled={processing}
          >
            {processing ? "处理中" : "批准退货"}
          </button>

          <button
            className="reject-button"
            type="button"
            onClick={() => onReject(returnRequest)}
            disabled={processing}
          >
            拒绝
          </button>
        </div>
      )}
    </article>
  );
}

export default ReturnRequestCard;
