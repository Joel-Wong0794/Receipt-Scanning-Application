import { useState } from "react";
import { useNavigate } from "react-router-dom";
import useCamera from "../hooks/useCamera.js";
import { extractReceipt } from "../api/client.js";

export default function CapturePage() {
  const { imageFile, previewUrl, openCamera, handleFileChange, reset, inputRef } = useCamera();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleExtract = async () => {
    if (!imageFile) return;
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("image", imageFile);

    try {
      const resp = await extractReceipt(formData);
      navigate("/review", {
        state: { extracted: resp.data, imageFile: null },
      });
    } catch (e) {
      setError("Could not read the receipt. Please try again with a clearer photo.");
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <h1 className="page-title">Scan a Receipt</h1>

      {/* Step indicator */}
      <p className="text-gray-500 text-base mb-8">Step 1 of 2 — Take a photo</p>

      {/* Hidden file input */}
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="hidden"
        onChange={handleFileChange}
      />

      {!previewUrl ? (
        <div className="space-y-4">
          {/* Primary camera button */}
          <button
            onClick={openCamera}
            className="w-full bg-blue-600 text-white rounded-2xl py-16 flex flex-col items-center gap-4 active:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-300"
          >
            <svg className="w-20 h-20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span className="text-2xl font-bold">TAKE PHOTO</span>
          </button>

          {/* Gallery fallback */}
          <div className="text-center">
            <button
              onClick={() => {
                if (inputRef.current) {
                  inputRef.current.removeAttribute("capture");
                  inputRef.current.click();
                }
              }}
              className="text-blue-600 text-base underline"
            >
              Or choose from your photo library
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Preview */}
          <div className="relative rounded-2xl overflow-hidden bg-black">
            <img
              src={previewUrl}
              alt="Receipt preview"
              className="w-full object-contain max-h-72"
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700">
              {error}
            </div>
          )}

          <button
            onClick={handleExtract}
            disabled={loading}
            className="btn-primary"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-3">
                <svg className="animate-spin w-6 h-6" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Reading receipt...
              </span>
            ) : (
              "Read This Receipt"
            )}
          </button>

          <button onClick={reset} disabled={loading} className="btn-secondary">
            Take a Different Photo
          </button>
        </div>
      )}
    </div>
  );
}
