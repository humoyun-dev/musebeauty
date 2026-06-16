// Pul: "320000" → "320 000 so'm"
export function money(value: number | string | undefined | null): string {
  if (value === undefined || value === null || value === "") return "—";
  const n = Math.round(Number(value));
  if (Number.isNaN(n)) return String(value);
  return `${n.toLocaleString("ru-RU").replace(/,/g, " ")} so'm`;
}

// Sana + vaqt: "17.06.2026, 01:42"
export function dateTime(value: string | null | undefined): string {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return String(value);
  return d.toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// Faqat sana: "17.06.2026"
export function dateShort(value: string | null | undefined): string {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return String(value);
  return d.toLocaleDateString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

// Chegirma/promokod qamrovi → o'qishga qulay yorliq
export const SCOPE_LABELS: Record<string, string> = {
  all: "Hammasiga",
  category: "Kategoriya",
  product: "Mahsulot",
};

// Buyurtma holati → o'qishga qulay yorliq + rang (antd Tag uchun)
export const ORDER_STATUS: Record<string, { label: string; color: string }> = {
  yangi: { label: "Yangi", color: "blue" },
  tolandi: { label: "To'landi", color: "green" },
  tayyorlandi: { label: "Tayyorlandi", color: "cyan" },
  jonatildi: { label: "Jo'natildi", color: "geekblue" },
  yetkazildi: { label: "Yetkazildi", color: "success" },
  bekor_qilindi: { label: "Bekor qilindi", color: "red" },
  qaytarildi: { label: "Qaytarildi", color: "volcano" },
};

// Holat zanjiri — keyingi ruxsat etilgan holatlar (admin tugmalari uchun)
export const NEXT_STATUSES: Record<string, string[]> = {
  yangi: ["tolandi", "bekor_qilindi"],
  tolandi: ["tayyorlandi", "bekor_qilindi"],
  tayyorlandi: ["jonatildi", "bekor_qilindi"],
  jonatildi: ["yetkazildi", "qaytarildi"],
  yetkazildi: ["qaytarildi"],
};

export const PAYMENT_STATUS: Record<string, { label: string; color: string }> = {
  tolanmagan: { label: "To'lanmagan", color: "orange" },
  tolandi: { label: "To'landi", color: "green" },
  qaytarildi: { label: "Qaytarildi", color: "volcano" },
};
