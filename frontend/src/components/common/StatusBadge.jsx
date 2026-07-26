import { getStatusText } from "../../utils/status";

function StatusBadge({ status }) {
  return (
    <span className={`status ${status}`}>
      {getStatusText(status)}
    </span>
  );
}

export default StatusBadge;
