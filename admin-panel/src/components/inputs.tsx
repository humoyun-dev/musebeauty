import { InputNumber } from "antd";
import type { InputNumberProps } from "antd";

// Raqamli inputlar — faqat raqam qabul qiladi (harf/belgi rad etiladi) va
// minglik guruhlarga ajratib ko'rsatadi: 1200000 → "1 200 000".
// money() (ru-RU, bo'sh joy ajratgich) bilan bir xil ko'rinish.

const groupDigits = (v?: string | number): string => {
  if (v === undefined || v === null || v === "") return "";
  const digits = `${v}`.replace(/\D/g, "");
  return digits.replace(/\B(?=(\d{3})+(?!\d))/g, " ");
};

const onlyDigits = (v?: string): string => (v ? v.replace(/\D/g, "") : "");

// Butun son inputi (qoldiq, limit, ID, foiz, miqdor) — guruhlash + harfsiz.
export const NumberInput = (props: InputNumberProps) => (
  <InputNumber
    min={0}
    precision={0}
    controls={false}
    style={{ width: "100%" }}
    inputMode="numeric"
    formatter={groupDigits}
    parser={onlyDigits as InputNumberProps["parser"]}
    {...props}
  />
);

// Pul inputi (narx, tannarx, summa) — NumberInput + "so'm" qo'shimchasi.
export const MoneyInput = (props: InputNumberProps) => (
  <NumberInput addonAfter="so'm" {...props} />
);
