import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import LineItemRow from "../components/LineItemRow.jsx";
import { createReceipt } from "../api/client.js";

const CATEGORIES = [
  { value: "Meals & Entertainment", emoji: "🍽️" },
  { value: "Travel", emoji: "✈️" },
  { value: "Office Supplies", emoji: "🖊️" },
  { value: "Other", emoji: "📋" },
];

function calcSubtotal(items) {
  return items.reduce((sum, it) => sum + (parseFloat(it.total_price) || 0), 0);
}

export default function ReviewPage() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const extracted = state?.extracted || {};

  const [form, setForm] = useState({
    vendor_name: extracted.vendor_name || "",
    date: extracted.date || "",
    currency: extracted.currency || "USD",
    subtotal: extracted.subtotal ?? "",
    tax: extracted.tax ?? "",
    total: extracted.total ?? "",
    category: "",
    notes: "",
  });
  const [lineItems, setLineItems] = useState(
    (extracted.line_items || []).map((li, i) => ({ ...li, _key: i }))
  );
  const [showItems, setShowItems] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const autoSubtotal = calcSubtotal(lineItems).toFixed(2);
  const expectedTotal = (parseFloat(autoSubtotal) + (parseFloat(form.tax) || 0)).toFixed(2);
  const totalMismatch = form.total && Math.abs(parseFloat(form.total) - parseFloat(expectedTotal)) > 0.02;

  const handleField = (field) => (e) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  const handleItemChange = (idx, updated) =>
    setLineItems((items) => items.map((it, i) => (i === idx ? updated : it)));

  const handleItemDelete = (idx) =>
    setLineItems((items) => items.filter((_, i) => i !== idx));

  const handleAddItem = () =>
    setLineItems((items) => [
      ...items,
      { description: "", quantity: 1, unit_price: null, total_price: "", _key: Date.now() },
    ]);

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      const payload = {
        ...form,
        subtotal: form.subtotal || autoSubtotal || null,
        line_items: lineItems.map(({ _key, ...li }) => li),
        image_filename: extracted.image_filename,
        ocr_raw_text: extracted.ocr_raw_text,
      };
      await createReceipt(payload);
      navigate("/success");
    } catch (e) {
      setError("Could not save receipt. Please try again.");
      setSaving(false);
    }
  };

  const handleDiscard = () => {
    if (window.confirm("Discard this receipt? Your photo will not be saved.")) {
      navigate("/");
    }
  };

  return (
    <div className="page-container">
      <h1 className="page-title">Check the Details</h1>
      <p className="text-gray-500 text-base mb-8">Step 2 of 2 — Review and save</p>

      {extracted.error && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mb-6 text-yellow-800">
          We had trouble reading some fields. Please fill them in below.
        </div>
      )}

      <div className="space-y-5">
        {/* Store Name */}
        <div>
          <label className="form-label">Store Name</label>
          <input
            className="form-input"
            placeholder="e.g. Starbucks"
            value={form.vendor_name}
            onChange={handleField("vendor_name")}
          />
        </div>

        {/* Date */}
        <div>
          <label className="form-label">Date</label>
          <input
            className="form-input"
            type="date"
            value={form.date}
            onChange={handleField("date")}
          />
        </div>

        {/* Total Amount */}
        <div>
          <label className="form-label">Total Amount</label>
          <div className="relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 text-lg">$</span>
            <input
              className="form-input pl-8"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
              value={form.total}
              onChange={handleField("total")}
            />
          </div>
          {totalMismatch && (
            <p className="text-yellow-600 text-sm mt-1">
              Note: Total doesn't match items + tax ({expectedTotal}). That's OK — just double-check the receipt.
            </p>
          )}
        </div>

        {/* Tax */}
        <div>
          <label className="form-label">Tax Amount</label>
          <div className="relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 text-lg">$</span>
            <input
              className="form-input pl-8"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
              value={form.tax}
              onChange={handleField("tax")}
            />
          </div>
        </div>

        {/* Category */}
        <div>
          <label className="form-label">Expense Type</label>
          <div className="grid grid-cols-2 gap-3">
            {CATEGORIES.map((cat) => (
              <button
                key={cat.value}
                type="button"
                onClick={() => setForm((f) => ({ ...f, category: cat.value }))}
                className={`py-4 px-3 rounded-xl border-2 text-base font-medium flex flex-col items-center gap-1 transition-colors ${
                  form.category === cat.value
                    ? "border-blue-500 bg-blue-50 text-blue-700"
                    : "border-gray-200 bg-white text-gray-700 active:bg-gray-50"
                }`}
              >
                <span className="text-2xl">{cat.emoji}</span>
                <span>{cat.value}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Line Items (collapsible) */}
        <div>
          <button
            type="button"
            onClick={() => setShowItems(!showItems)}
            className="flex items-center gap-2 text-blue-600 text-base font-medium py-2"
          >
            <svg
              className={`w-5 h-5 transition-transform ${showItems ? "rotate-90" : ""}`}
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            {showItems ? "Hide" : "Show"} itemized list ({lineItems.length} items)
          </button>

          {showItems && (
            <div className="card mt-2">
              <div className="flex text-sm font-semibold text-gray-500 pb-2 border-b border-gray-100">
                <span className="flex-1">Item</span>
                <span className="w-20 text-right">Total</span>
                <span className="w-10" />
              </div>
              {lineItems.map((item, idx) => (
                <LineItemRow
                  key={item._key ?? idx}
                  item={item}
                  index={idx}
                  onChange={handleItemChange}
                  onDelete={handleItemDelete}
                />
              ))}
              <button
                type="button"
                onClick={handleAddItem}
                className="w-full mt-3 py-3 text-blue-600 text-base font-medium border-2 border-dashed border-blue-200 rounded-xl active:bg-blue-50"
              >
                + Add Item
              </button>
              <p className="text-sm text-gray-500 mt-2 text-right">
                Items subtotal: ${autoSubtotal}
              </p>
            </div>
          )}
        </div>

        {/* Notes */}
        <div>
          <label className="form-label">Notes (optional)</label>
          <textarea
            className="form-input"
            rows={3}
            placeholder="Any extra notes..."
            value={form.notes}
            onChange={handleField("notes")}
          />
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700">
            {error}
          </div>
        )}

        {/* Actions */}
        <div className="space-y-3 pt-2">
          <button
            onClick={handleSave}
            disabled={saving}
            className="btn-primary"
          >
            {saving ? (
              <span className="flex items-center justify-center gap-3">
                <svg className="animate-spin w-6 h-6" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Saving...
              </span>
            ) : (
              "SAVE RECEIPT"
            )}
          </button>
          <button onClick={handleDiscard} disabled={saving} className="btn-secondary">
            Discard
          </button>
        </div>
      </div>
    </div>
  );
}
