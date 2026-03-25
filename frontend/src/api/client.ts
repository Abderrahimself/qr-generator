import type { QRCodeRequest, QRCodeResponse } from "../types";

const API_BASE = "/api";
const REQUEST_TIMEOUT_MS = 15_000;

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const headers: HeadersInit = options?.body
    ? { "Content-Type": "application/json" }
    : {};

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: { ...headers, ...options?.headers },
      signal: controller.signal,
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new Error("Request timed out");
    }
    throw err;
  } finally {
    clearTimeout(timeout);
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `Request failed: ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

export function generateQR(data: QRCodeRequest): Promise<QRCodeResponse> {
  return request<QRCodeResponse>("/generate", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function fetchHistory(limit = 50, offset = 0): Promise<QRCodeResponse[]> {
  return request<QRCodeResponse[]>(`/history?limit=${limit}&offset=${offset}`);
}

export function fetchQR(id: string): Promise<QRCodeResponse> {
  return request<QRCodeResponse>(`/qr/${id}`);
}

export function deleteQR(id: string): Promise<void> {
  return request<void>(`/qr/${id}`, { method: "DELETE" });
}
