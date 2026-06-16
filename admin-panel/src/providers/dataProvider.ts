import type { BaseRecord, DataProvider } from "@refinedev/core";

import { API_URL, apiFetch } from "./apiClient";

// Refine method'lari generic <TData> qaytaradi; bizning REST javoblarimiz BaseRecord.
// `as any` bilan cast qilamiz — yagona maqsadi generic constraint'ni qondirish.

// Backendning api/admin'iga moslangan yengil REST provider.
// Ro'yxat endpointlari oddiy massiv qaytaradi (X-Total-Count yo'q) — shuning uchun
// total = massiv uzunligi. Kichik admin ma'lumotlari uchun yetarli.
export const dataProvider: DataProvider = {
  getApiUrl: () => API_URL,

  getList: async ({ resource, pagination, filters }) => {
    const params: Record<string, unknown> = {};
    if (pagination) {
      const { current = 1, pageSize = 50 } = pagination;
      params.limit = pageSize;
      params.offset = (current - 1) * pageSize;
    }
    // Oddiy "field eq value" filtrlarni query'ga o'tkazamiz (status, category_id, pending)
    (filters ?? []).forEach((f) => {
      if ("field" in f && f.value !== undefined && f.value !== "") {
        params[f.field] = f.value;
      }
    });

    const data = await apiFetch<BaseRecord[]>(`/${resource}`, { params });
    return { data, total: Array.isArray(data) ? data.length : 0 } as any;
  },

  getOne: async ({ resource, id }) => {
    const data = await apiFetch<BaseRecord>(`/${resource}/${id}`);
    return { data } as any;
  },

  create: async ({ resource, variables }) => {
    const data = await apiFetch<BaseRecord>(`/${resource}`, {
      method: "POST",
      body: variables,
    });
    return { data } as any;
  },

  update: async ({ resource, id, variables }) => {
    const data = await apiFetch<BaseRecord>(`/${resource}/${id}`, {
      method: "PATCH",
      body: variables,
    });
    return { data } as any;
  },

  deleteOne: async ({ resource, id }) => {
    await apiFetch(`/${resource}/${id}`, { method: "DELETE" });
    return { data: { id } } as any;
  },

  getMany: async ({ resource, ids }) => {
    const all = await apiFetch<BaseRecord[]>(`/${resource}`, {
      params: { limit: 500 },
    });
    const set = new Set(ids.map(String));
    return { data: all.filter((r) => set.has(String(r.id))) } as any;
  },

  // Maxsus chaqiruvlar uchun (to'lov tasdiq, buyurtma holati)
  custom: async ({ url, method, payload }) => {
    const path = url.startsWith("http") ? url.replace(API_URL, "") : url;
    const data = await apiFetch<BaseRecord>(path, {
      method: (method?.toUpperCase() as string) ?? "POST",
      body: payload,
    });
    return { data } as any;
  },
};
