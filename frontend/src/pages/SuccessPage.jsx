import { useNavigate } from "react-router-dom";

export default function SuccessPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-green-50 flex flex-col items-center justify-center px-6 text-center">
      {/* Big green checkmark */}
      <div className="w-32 h-32 bg-green-500 rounded-full flex items-center justify-center mb-8 shadow-lg">
        <svg className="w-20 h-20 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
        </svg>
      </div>

      <h1 className="text-4xl font-bold text-green-800 mb-3">Receipt Saved!</h1>
      <p className="text-xl text-green-700 mb-2">
        It's been added to your expense log.
      </p>
      <p className="text-base text-green-600 mb-12">
        You can view and export it from "My Receipts".
      </p>

      <div className="w-full max-w-sm space-y-3">
        <button
          onClick={() => navigate("/")}
          className="btn-primary bg-green-600 hover:bg-green-700 active:bg-green-700"
        >
          Done
        </button>
        <button
          onClick={() => navigate("/history")}
          className="btn-secondary"
        >
          View My Receipts
        </button>
      </div>
    </div>
  );
}
