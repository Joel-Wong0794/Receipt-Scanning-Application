import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getReceipt, deleteReceipt, syncSheets } from "../api/client.js";
import ExportButton from "../components/ExportButton.jsx";

function formatDate(dateStr) {
  if (!dateStr) return "—";
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" });
}

export default function DetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [receipt, setReceipt] = useState(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [syncMsg, setSyncMsg] = useState(null);

  useEffect(() => {
    getReceipt(id)
      .then((r) => setReceipt(r.data))
      .catch(() => navigate("/history"))
      .finally(() => setLoading(false));
  }, [id]);

  const handleDelete = async () => {
    if (!window.confirm("Delete this receipt? This cannot be undone.")) return;
    await deleteReceipt(id);
    navigate("/history");
  };

  const handleSync = async () => {
    setSyncing(true);
    setSyncMsg(null);
    try {
      await syncSheets(id);
      setReceipt((r) => ({ ...r, sheets_synced: true }));
      setSyncMsg("Synced to Google Sheets!");
    } catch {
      setSyncMsg("Sync failed. Check your Google Sheets settings.");
    } finally {
      setSyncing(false);
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="space-y-4">
          {[1, 2, 3].map((i) => <div key={i} className="card animate-pulse h-16 bg-gray-100" />)}
        </div>
      </div>
    );
  }

  if (!receipt) return null;

  return (
    <div className="page-container">
      {/* Back button */}
      <button
        onClick={() => navigate("/history")}
        className="flex items-center gap-2 text-blue-600 text-base font-medium mb-6 -ml-1"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        My Receipts
      </button>

      <h1 className="text-2xl font-bold text-gray-900 mb-1">
        {receipt.vendor_name || "Unknown Store"}
      </h1>
      <p className="text-gray-500 text-base mb-6">{formatDate(receipt.date)}</p>

      {/* Summary card */}
      <div className="card mb-6">
        {receipt.category && (
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-600">Expense Type</span>
            <span className="font-medium">{receipt.category}</span>
          </div>
        )}
        {receipt.subtotal && (
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-600">Subtotal</span>
            <span className="font-medium">${Number(receipt.subtotal).toFixed(2)}</span>
          </div>
        )}
        {receipt.tax && (
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-600">Tax</span>
            <span className="font-medium">${Number(receipt.tax).toFixed(2)}</span>
          </div>
        )}
        <div className="flex justify-between py-2">
          <span className="text-lg font-bold text-gray-900">Total</span>
          <span className="text-lg font-bold text-gray-900">
            {receipt.total ? `$${Number(receipt.total).toFixed(2)}` : "—"} {receipt.currency}
          </span>
        </div>
      </div>

      {/* Line items */}
      {receipt.line_items?.length > 0 && (
        <div className="card mb-6">
          <h2 className="font-semibold text-gray-700 mb-3">Items</h2>
          {receipt.line_items.map((li, i) => (
            <div key={i} className="flex justify-between py-2 border-b border-gray-100 last:border-0">
              <span className="text-gray-700 flex-1 pr-4">{li.description}</span>
              <span className="text-gray-900 font-medium shrink-0">
                {li.total_price ? `$${Number(li.total_price).toFixed(2)}` : "—"}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Notes */}
      {receipt.notes && (
        <div className="card mb-6">
          <h2 className="font-semibold text-gray-700 mb-1">Notes</h2>
          <p className="text-gray-600">{receipt.notes}</p>
        </div>
      )}

      {/* Sheets sync status */}
      <div className="mb-6">
        {receipt.sheets_synced ? (
          <div className="flex items-center gap-2 text-green-600 bg-green-50 rounded-xl p-4">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            Synced to Google Sheets
          </div>
        ) : (
          <button
            onClick={handleSync}
            disabled={syncing}
            className="btn-secondary"
          >
            {syncing ? "Syncing..." : "Sync to Google Sheets"}
          </button>
        )}
        {syncMsg && <p className="text-sm mt-2 text-gray-600">{syncMsg}</p>}
      </div>

      {/* Actions */}
      <div className="space-y-3">
        <ExportButton receiptId={receipt.id} label="Export This Receipt" />
        <button
          onClick={() => navigate("/review", { state: { extracted: receipt } })}
          className="btn-secondary"
        >
          Edit Receipt
        </button>
        <button onClick={handleDelete} className="btn-danger">
          Delete Receipt
        </button>
      </div>
    </div>
  );
}
