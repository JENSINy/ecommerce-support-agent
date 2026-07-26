const STATUS_TEXT = {
  success: "成功",
  not_found: "未找到",
  failed: "失败",
  pending_approval: "待审批",
  pending_review: "待审核",
  approved: "已批准",
  rejected: "已拒绝",
};

export function getStatusText(status) {
  return STATUS_TEXT[status] || status;
}
