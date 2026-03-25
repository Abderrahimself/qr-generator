import { useState, useEffect, useCallback } from "react";
import type { QRCodeResponse } from "../types";
import { generateQR, fetchHistory, deleteQR } from "../api/client";

interface UseQRGeneratorReturn {
  currentQR: QRCodeResponse | null;
  history: QRCodeResponse[];
  isGenerating: boolean;
  isLoadingHistory: boolean;
  error: string | null;
  generate: (url: string, format?: string) => Promise<void>;
  remove: (id: string) => Promise<void>;
  refreshHistory: () => Promise<void>;
}

export function useQRGenerator(): UseQRGeneratorReturn {
  const [currentQR, setCurrentQR] = useState<QRCodeResponse | null>(null);
  const [history, setHistory] = useState<QRCodeResponse[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshHistory = useCallback(async () => {
    setIsLoadingHistory(true);
    try {
      const data = await fetchHistory();
      setHistory(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load history");
    } finally {
      setIsLoadingHistory(false);
    }
  }, []);

  const generate = useCallback(async (url: string, format = "png") => {
    setIsGenerating(true);
    setError(null);
    try {
      const result = await generateQR({ url, format });
      setCurrentQR(result);
      await refreshHistory();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate QR code");
    } finally {
      setIsGenerating(false);
    }
  }, [refreshHistory]);

  const remove = useCallback(async (id: string) => {
    setError(null);
    try {
      await deleteQR(id);
      setCurrentQR((prev) => (prev?.id === id ? null : prev));
      await refreshHistory();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete QR code");
    }
  }, [refreshHistory]);

  useEffect(() => {
    refreshHistory();
  }, [refreshHistory]);

  return {
    currentQR,
    history,
    isGenerating,
    isLoadingHistory,
    error,
    generate,
    remove,
    refreshHistory,
  };
}
