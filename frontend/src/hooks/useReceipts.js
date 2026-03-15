import { useState, useEffect } from "react";
import { listReceipts } from "../api/client.js";

export default function useReceipts(params = {}) {
  const [receipts, setReceipts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [meta, setMeta] = useState({ total: 0, pages: 1 });

  const fetch = async (overrideParams = {}) => {
    setLoading(true);
    setError(null);
    try {
      const resp = await listReceipts({ ...params, ...overrideParams });
      setReceipts(resp.data.receipts);
      setMeta({ total: resp.data.total, pages: resp.data.pages });
    } catch (e) {
      setError("Could not load receipts.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetch();
  }, []);

  return { receipts, loading, error, refetch: fetch, meta };
}
