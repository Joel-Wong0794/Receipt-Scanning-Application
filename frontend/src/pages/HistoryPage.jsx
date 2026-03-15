import { useState } from "react";
import useReceipts from "../hooks/useReceipts.js";
import ReceiptCard from "../components/ReceiptCard.jsx";
import ExportButton from "../components/ExportButton.jsx";

export default function HistoryPage() {
  const [search, setSearch] = useState("");
  const { receipts, loading, error, refetch } = useReceipts();

  const filtered = receipts.filter((r) =>
    !search ||
    (r.vendor_name || "").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="page-container">
      <h1 className="page-title">My Receipts</h1>

      {/* Export to HR — prominent primary action */}
      <div className="mb-6">
        <ExportButton label="Export to HR System" />
      </div>

      {/* Search */}
      <div className="relative mb-6">
        <svg
          className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          className="form-input pl-12"
          placeholder="Search by store name..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {loading && (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card animate-pulse h-24 bg-gray-100" />
          ))}
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 mb-4">
          {error}
          <button onClick={() => refetch()} className="ml-2 underline">Retry</button>
        </div>
      )}

      {!loading && !error && filtered.length === 0 && (
        <div className="text-center py-16 text-gray-400">
          <svg className="w-20 h-20 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <p className="text-xl font-medium text-gray-500">No receipts yet</p>
          <p className="mt-1">Tap "Scan Receipt" to add your first one</p>
        </div>
      )}

      <div className="space-y-3">
        {filtered.map((r) => (
          <ReceiptCard key={r.id} receipt={r} />
        ))}
      </div>
    </div>
  );
}
