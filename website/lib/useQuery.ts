"use client";

import { useEffect, useState } from "react";

// Statik eksportда useSearchParams Suspense talab qiladi — buni o'rniga
// window.location'dan o'qiymiz (client-only). Birinchi render'da null.
export function useQueryParam(key: string): string | null {
  const [value, setValue] = useState<string | null>(null);
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setValue(params.get(key));
  }, [key]);
  return value;
}
