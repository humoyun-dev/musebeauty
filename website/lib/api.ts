// Backend api/public bilan ishlash. Prod'da bir xil origin (/api/public),
// dev'да NEXT_PUBLIC_API_URL (masalan http://localhost:8000/api/public).
export const API_URL = (
  process.env.NEXT_PUBLIC_API_URL ?? "/api/public"
).replace(/\/$/, "");

export interface Category {
  id: number;
  name: string;
  slug: string;
  is_active: boolean;
}

export interface Product {
  id: number;
  category_id: number | null;
  name: string;
  description: string | null;
  image_url: string | null;
  price: string;
  stock_qty: number;
  is_active: boolean;
}

export interface District {
  id: number;
  name: string;
  delivery_fee: string;
}

export interface QuoteLine {
  product_id: number;
  name: string;
  qty: number;
  unit_price: string;
  line_total: string;
}

export interface Quote {
  lines: QuoteLine[];
  subtotal: string;
  discount_amount: string;
  delivery_fee: string;
  free_delivery: boolean;
  total: string;
  promo_error: string | null;
}

export interface WebOrderResult {
  order_id: number;
  total: string;
  status: string;
  payment_card_number: string;
  payment_card_holder: string;
  payme_url: string | null;
}

export interface PublicDiscount {
  id: number;
  name: string;
  type: string; // percent | fixed
  value: string;
  scope: string;
  target_id: number | null;
  valid_until: string | null;
}

export interface PublicPromo {
  code: string;
  type: string; // percent | fixed | free_delivery
  value: string;
  min_order_amount: string;
  max_discount: string | null;
  first_order_only: boolean;
  valid_until: string | null;
}

export interface Promotions {
  discounts: PublicDiscount[];
  promo_codes: PublicPromo[];
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    cache: "no-store",
  });
  if (!res.ok) {
    let detail = `Xatolik (${res.status})`;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return res.json();
}

export const api = {
  categories: () => req<Category[]>("/catalog/categories"),
  products: (params: { category_id?: number; q?: string; in_stock?: boolean } = {}) => {
    const qs = new URLSearchParams();
    if (params.category_id) qs.set("category_id", String(params.category_id));
    if (params.q) qs.set("q", params.q);
    if (params.in_stock) qs.set("in_stock", "true");
    const s = qs.toString();
    return req<Product[]>(`/catalog/products${s ? `?${s}` : ""}`);
  },
  product: (id: number) => req<Product>(`/catalog/products/${id}`),
  promotions: () => req<Promotions>("/promotions"),
  districts: () => req<District[]>("/orders/districts"),
  quote: (body: unknown) =>
    req<Quote>("/orders/quote", { method: "POST", body: JSON.stringify(body) }),
  createWebOrder: (body: unknown) =>
    req<WebOrderResult>("/orders/web", { method: "POST", body: JSON.stringify(body) }),
};
