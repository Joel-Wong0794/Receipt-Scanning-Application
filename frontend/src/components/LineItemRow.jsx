export default function LineItemRow({ item, index, onChange, onDelete }) {
  const handle = (field) => (e) =>
    onChange(index, { ...item, [field]: e.target.value });

  return (
    <div className="flex gap-2 items-start border-b border-gray-100 py-3">
      <div className="flex-1">
        <input
          className="form-input text-sm"
          placeholder="Description"
          value={item.description || ""}
          onChange={handle("description")}
        />
      </div>
      <div className="w-20">
        <input
          className="form-input text-sm text-right"
          placeholder="0.00"
          type="number"
          step="0.01"
          min="0"
          value={item.total_price || ""}
          onChange={handle("total_price")}
        />
      </div>
      <button
        type="button"
        onClick={() => onDelete(index)}
        className="text-red-400 p-2 rounded-lg active:bg-red-50 mt-1"
        aria-label="Remove item"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}
