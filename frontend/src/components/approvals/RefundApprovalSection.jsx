import RefundRequestCard from "./RefundRequestCard";

function RefundApprovalSection({
  refundRequests,
  loading,
  processingId,
  onRefresh,
  onApprove,
  onReject,
}) {
  return (
    <section className="approval-section">
      <div className="approval-header">
        <div>
          <h2>退款审批中心</h2>
          <p>
            退款属于敏感操作，必须由人工批准或拒绝。
          </p>
        </div>

        <button
          className="refresh-button"
          type="button"
          onClick={onRefresh}
          disabled={loading}
        >
          {loading ? "刷新中" : "刷新列表"}
        </button>
      </div>

      {refundRequests.length === 0 && !loading && (
        <div className="approval-empty">
          暂无退款申请。用户提交退款申请后会显示在这里。
        </div>
      )}

      <div className="request-list">
        {refundRequests.map((refundRequest) => (
          <RefundRequestCard
            key={refundRequest.id}
            refundRequest={refundRequest}
            processing={
              processingId === refundRequest.id
            }
            onApprove={onApprove}
            onReject={onReject}
          />
        ))}
      </div>
    </section>
  );
}

export default RefundApprovalSection;
