export function money(value: number | string | null | undefined): string {
  if (value === null || value === undefined || value === "") return "—";
  const n = Math.round(Number(value));
  if (Number.isNaN(n)) return String(value);
  return `${n.toLocaleString("ru-RU").replace(/,/g, " ")} so'm`;
}
