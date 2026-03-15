import { useState } from "react";
import { exportUrl } from "../api/client.js";

const FORMATS = [
  { value: "csv", label: "Standard CSV" },
  { value: "workday_csv", label: "Workday / HR Portal (CSV)" },
  { value: "json", label: "JSON (for developers)" },
];

export default function ExportButton({ receiptId = null, label = "Export to HR System" }) {
  const [open, setOpen] = useState(false);

  const handleExport = (format) => {
    const url = exportUrl(format, receiptId);
    window.location.href = url;
    setOpen(false);
  };

  return (
    <div className="relative">
      <button
        className="btn-primary"
        onClick={() => setOpen(!open)}
      >
        {label}
      </button>
      {open && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setOpen(false)}
          />
          <div className="absolute bottom-full mb-2 left-0 right-0 bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden z-20">
            {FORMATS.map((f) => (
              <button
                key={f.value}
                className="w-full text-left px-5 py-4 text-base font-medium text-gray-800 active:bg-blue-50 border-b border-gray-100 last:border-0"
                onClick={() => handleExport(f.value)}
              >
                {f.label}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
