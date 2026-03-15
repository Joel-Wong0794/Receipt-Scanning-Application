import { useNavigate } from "react-router-dom";

function formatDate(dateStr) {
  if (!dateStr) return "No date";
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

export default function ReceiptCard({ receipt }) {
  const navigate = useNavigate();

  return (
    <button
      className="card w-full text-left active:bg-gray-50 transition-colors"
      onClick={() => navigate(`/receipts/${receipt.id}`)}
    >
      <div className="flex justify-between items-start gap-3">
        <div className="flex-1 min-w-0">
          <p className="text-lg font-semibold text-gray-900 truncate">
            {receipt.vendor_name || "Unknown Store"}
          </p>
          <p className="text-gray-500 text-base mt-0.5">{formatDate(receipt.date)}</p>
          {receipt.category && (
            <span className="inline-block mt-1 px-2 py-0.5 bg-blue-50 text-blue-700 text-sm rounded-full">
              {receipt.category}
            </span>
          )}
        </div>
        <div className="text-right shrink-0">
          <p className="text-xl font-bold text-gray-900">
            {receipt.total ? `$${Number(receipt.total).toFixed(2)}` : "—"}
          </p>
          {receipt.sheets_synced && (
            <span className="text-green-500 text-sm flex items-center gap-1 justify-end mt-1">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Synced
            </span>
          )}
        </div>
      </div>
    </button>
  );
}
