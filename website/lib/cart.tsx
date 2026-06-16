"use client";

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

// Savat localStorage'da: { [productId]: qty }
type Items = Record<number, number>;

interface CartCtx {
  items: Items;
  count: number;
  add: (productId: number, qty?: number) => void;
  setQty: (productId: number, qty: number) => void;
  remove: (productId: number) => void;
  clear: () => void;
  ready: boolean;
}

const STORAGE_KEY = "muse_cart";
const Ctx = createContext<CartCtx | null>(null);

export function CartProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<Items>({});
  const [ready, setReady] = useState(false);

  // Yuklash
  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) setItems(JSON.parse(raw));
    } catch {
      /* ignore */
    }
    setReady(true);
  }, []);

  // Saqlash
  useEffect(() => {
    if (ready) localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  }, [items, ready]);

  const value = useMemo<CartCtx>(() => {
    const count = Object.values(items).reduce((a, b) => a + b, 0);
    return {
      items,
      count,
      ready,
      add: (id, qty = 1) =>
        setItems((p) => {
          const next = (p[id] ?? 0) + qty;
          if (next <= 0) {
            const { [id]: _, ...rest } = p;
            return rest;
          }
          return { ...p, [id]: next };
        }),
      setQty: (id, qty) =>
        setItems((p) => {
          if (qty <= 0) {
            const { [id]: _, ...rest } = p;
            return rest;
          }
          return { ...p, [id]: qty };
        }),
      remove: (id) =>
        setItems((p) => {
          const { [id]: _, ...rest } = p;
          return rest;
        }),
      clear: () => setItems({}),
    };
  }, [items, ready]);

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useCart(): CartCtx {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useCart CartProvider ichida ishlatilishi kerak");
  return ctx;
}
