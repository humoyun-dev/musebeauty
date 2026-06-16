// Yagona fetch o'rami — JWT tokenni qo'shadi, JSON qaytaradi, xatoni tashlaydi.
// Bazaviy URL: prod'da nginx bir xil origin'dan /api/admin ga proxy qiladi;
// dev'da VITE_API_URL (masalan http://localhost:8000/api/admin).
export const API_URL =
  import.meta.env.VITE_API_URL?.replace(/\/$/, "") ?? "/api/admin";

export const TOKEN_KEY = "muse_admin_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export class HttpError extends Error {
  statusCode: number;
  constructor(message: string, statusCode: number) {
    super(message);
    this.statusCode = statusCode;
  }
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  params?: Record<string, unknown>;
}

export async function apiFetch<T = unknown>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { method = "GET", body, params } = options;

  let url = `${API_URL}${path}`;
  if (params) {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") qs.append(k, String(v));
    });
    const s = qs.toString();
    if (s) url += `?${s}`;
  }

  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(url, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (res.status === 204) return undefined as T;

  let data: unknown = null;
  const text = await res.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!res.ok) {
    const detail =
      (data as { detail?: string } | null)?.detail ?? `Xatolik (${res.status})`;
    throw new HttpError(
      typeof detail === "string" ? detail : "Xatolik",
      res.status,
    );
  }

  return data as T;
}

// Rasm yuklash (multipart). Content-Type qo'yilmaydi — brauzer boundary qo'shadi.
export async function uploadImage(file: File): Promise<{ url: string }> {
  const form = new FormData();
  form.append("file", file);
  const headers: Record<string, string> = {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_URL}/upload`, {
    method: "POST",
    headers,
    body: form,
  });
  if (!res.ok) {
    const t = await res.text();
    let msg = `Yuklab bo'lmadi (${res.status})`;
    try {
      msg = JSON.parse(t).detail ?? msg;
    } catch {
      /* ignore */
    }
    throw new HttpError(msg, res.status);
  }
  return res.json();
}
