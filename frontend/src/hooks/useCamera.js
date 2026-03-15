import { useState, useRef } from "react";

export default function useCamera() {
  const [imageFile, setImageFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const inputRef = useRef(null);

  const openCamera = () => {
    if (inputRef.current) inputRef.current.click();
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setImageFile(file);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  };

  const reset = () => {
    setImageFile(null);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  return { imageFile, previewUrl, openCamera, handleFileChange, reset, inputRef };
}
