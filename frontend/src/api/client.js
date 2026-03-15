import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
});

export const extractReceipt = (formData) =>
  api.post("/api/ocr/extract", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    timeout: 60000, // OCR can take up to 30s
  });

export const createReceipt = (data) => api.post("/api/receipts", data);
export const listReceipts = (params) => api.get("/api/receipts", { params });
export const getReceipt = (id) => api.get(`/api/receipts/${id}`);
export const updateReceipt = (id, data) => api.put(`/api/receipts/${id}`, data);
export const deleteReceipt = (id) => api.delete(`/api/receipts/${id}`);
export const syncSheets = (id) => api.post(`/api/receipts/${id}/sync-sheets`);

export const exportUrl = (format, id = null) => {
  const base = id ? `/api/receipts/${id}/export` : "/api/receipts/export";
  return `${BASE_URL}${base}?format=${format}`;
};

export default api;
