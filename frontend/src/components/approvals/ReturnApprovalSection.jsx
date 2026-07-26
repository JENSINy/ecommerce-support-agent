import ReturnRequestCard from "./ReturnRequestCard";

function ReturnApprovalSection({
  returnRequests,
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
          <h2>退货审核中心</h2>
          <p>
            审核通过后允许用户寄回商品，不会自动执行退款。
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

      {returnRequests.length === 0 && !loading && (
        <div className="approval-empty">
          暂无退货申请。用户提交退货申请后会显示在这里。
        </div>
      )}

      <div className="request-list">
        {returnRequests.map((returnRequest) => (
          <ReturnRequestCard
            key={returnRequest.id}
            returnRequest={returnRequest}
            processing={
              processingId === returnRequest.id
            }
            onApprove={onApprove}
            onReject={onReject}
          />
        ))}
      </div>
    </section>
  );
}

export default ReturnApprovalSection;
