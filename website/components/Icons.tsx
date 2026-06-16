// Nafis chiziqli ikonkalar — emoji o'rniga. Barchasi currentColor bilan ishlaydi.
import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement> & { className?: string };

function Base({ className = "h-5 w-5", children, ...rest }: IconProps & { children: React.ReactNode }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.5}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className={className}
      {...rest}
    >
      {children}
    </svg>
  );
}

export const ArrowRight = (p: IconProps) => (
  <Base {...p}>
    <path d="M5 12h14M13 6l6 6-6 6" />
  </Base>
);

export const ArrowLeft = (p: IconProps) => (
  <Base {...p}>
    <path d="M19 12H5M11 6l-6 6 6 6" />
  </Base>
);

export const ArrowUpRight = (p: IconProps) => (
  <Base {...p}>
    <path d="M7 17 17 7M8 7h9v9" />
  </Base>
);

export const Bag = (p: IconProps) => (
  <Base {...p}>
    <path d="M6 8h12l-1 12.5a1 1 0 0 1-1 .9H8a1 1 0 0 1-1-.9L6 8Z" />
    <path d="M9 8V6.5a3 3 0 0 1 6 0V8" />
  </Base>
);

export const Search = (p: IconProps) => (
  <Base {...p}>
    <circle cx="11" cy="11" r="6.5" />
    <path d="m20 20-3.6-3.6" />
  </Base>
);

export const Heart = ({ filled, ...p }: IconProps & { filled?: boolean }) => (
  <Base {...p} fill={filled ? "currentColor" : "none"}>
    <path d="M12 20.5s-7.5-4.6-9.6-9.3C1 7.9 2.7 4.8 6 4.8c2 0 3.3 1.2 4 2.4.7-1.2 2-2.4 4-2.4 3.3 0 5 3.1 3.6 6.4C19.5 15.9 12 20.5 12 20.5Z" />
  </Base>
);

export const Star = ({ filled, ...p }: IconProps & { filled?: boolean }) => (
  <Base {...p} fill={filled ? "currentColor" : "none"} strokeWidth={1.2}>
    <path d="M12 3.5l2.45 5.2 5.55.7-4.1 3.9 1.05 5.7L12 16.9 6.05 19l1.05-5.7L3 9.4l5.55-.7L12 3.5Z" />
  </Base>
);

export const Plus = (p: IconProps) => (
  <Base {...p}>
    <path d="M12 5v14M5 12h14" />
  </Base>
);

export const Minus = (p: IconProps) => (
  <Base {...p}>
    <path d="M5 12h14" />
  </Base>
);

export const Check = (p: IconProps) => (
  <Base {...p}>
    <path d="m4.5 12.5 5 5 10-11" />
  </Base>
);

export const Truck = (p: IconProps) => (
  <Base {...p}>
    <path d="M3 7h11v8H3zM14 10h4l3 3v2h-7z" />
    <circle cx="7" cy="17.5" r="1.8" />
    <circle cx="17.5" cy="17.5" r="1.8" />
  </Base>
);

export const Shield = (p: IconProps) => (
  <Base {...p}>
    <path d="M12 3 5 5.5v5c0 4.5 3 8 7 9.5 4-1.5 7-5 7-9.5v-5L12 3Z" />
    <path d="m9 12 2 2 4-4.5" />
  </Base>
);

export const Leaf = (p: IconProps) => (
  <Base {...p}>
    <path d="M5 19c0-8 5-13 14-13 0 9-5 14-13 14" />
    <path d="M5 19c2-4 5-6.5 9-8" />
  </Base>
);

export const Sparkle = (p: IconProps) => (
  <Base {...p}>
    <path d="M12 3c.4 3.8 1.7 5.1 5.5 5.5-3.8.4-5.1 1.7-5.5 5.5-.4-3.8-1.7-5.1-5.5-5.5C10.3 8.1 11.6 6.8 12 3Z" />
    <path d="M18.5 14c.2 1.7.8 2.3 2.5 2.5-1.7.2-2.3.8-2.5 2.5-.2-1.7-.8-2.3-2.5-2.5 1.7-.2 2.3-.8 2.5-2.5Z" />
  </Base>
);

export const Chat = (p: IconProps) => (
  <Base {...p}>
    <path d="M4 5h16v11H9l-5 4V5Z" />
    <path d="M8 10h8M8 13h5" />
  </Base>
);

export const MapPin = (p: IconProps) => (
  <Base {...p}>
    <path d="M12 21s7-5.5 7-11a7 7 0 1 0-14 0c0 5.5 7 11 7 11Z" />
    <circle cx="12" cy="10" r="2.5" />
  </Base>
);

export const Tag = (p: IconProps) => (
  <Base {...p}>
    <path d="M3 12.5 11.5 4H20v8.5L11.5 21 3 12.5Z" />
    <circle cx="15.5" cy="8.5" r="1.3" />
  </Base>
);

export const Copy = (p: IconProps) => (
  <Base {...p}>
    <rect x="8" y="8" width="12" height="12" rx="2" />
    <path d="M4 16V5a1 1 0 0 1 1-1h11" />
  </Base>
);

export const Menu = (p: IconProps) => (
  <Base {...p}>
    <path d="M4 7h16M4 12h16M4 17h16" />
  </Base>
);

export const Close = (p: IconProps) => (
  <Base {...p}>
    <path d="M6 6l12 12M18 6 6 18" />
  </Base>
);

export const Telegram = (p: IconProps) => (
  <Base {...p}>
    <path d="M21 4 3 11l5 2 2 6 3-4 5 4 3-15Z" />
    <path d="m8 13 9-6-6 8" />
  </Base>
);

export const Instagram = (p: IconProps) => (
  <Base {...p}>
    <rect x="4" y="4" width="16" height="16" rx="5" />
    <circle cx="12" cy="12" r="3.5" />
    <circle cx="17" cy="7" r="0.6" fill="currentColor" />
  </Base>
);

export const Quote = (p: IconProps) => (
  <Base {...p} fill="currentColor" stroke="none">
    <path d="M9.5 6C6.5 7 5 9.4 5 13v5h5v-5H7.7c0-2 .8-3.4 2.5-4.2L9.5 6Zm9 0c-3 1-4.5 3.4-4.5 7v5h5v-5h-2.3c0-2 .8-3.4 2.5-4.2L18.5 6Z" />
  </Base>
);

// Mahsulot rasmi bo'lmaganda — nafis shisha-flakon siluети.
export const BottleGlyph = ({ className = "h-12 w-12" }: IconProps) => (
  <svg viewBox="0 0 48 64" fill="none" aria-hidden="true" className={className}>
    <path
      d="M19 6h10v6.5c0 1 .4 2 1.2 2.7l2.6 2.5c1.4 1.3 2.2 3.1 2.2 5V52a6 6 0 0 1-6 6H19a6 6 0 0 1-6-6V22.7c0-1.9.8-3.7 2.2-5l2.6-2.5c.8-.7 1.2-1.7 1.2-2.7V6Z"
      stroke="currentColor"
      strokeWidth={1.4}
    />
    <path d="M16 3h16M19.5 24h9" stroke="currentColor" strokeWidth={1.4} strokeLinecap="round" />
    <circle cx="24" cy="40" r="6" stroke="currentColor" strokeWidth={1.2} opacity={0.6} />
  </svg>
);

// Logodagi nozik bargli novda — brendning asosiy botanik motivi.
export const Sprig = ({ className = "h-12 w-12" }: IconProps) => (
  <svg
    viewBox="0 0 48 100"
    fill="none"
    stroke="currentColor"
    strokeWidth={1.2}
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    className={className}
  >
    <path d="M24 98 C 23 80 25 70 24 50 C 23 34 25 20 24 6" />
    <path d="M24 74 Q 10 76 4 56 Q 18 54 24 74 Z" />
    <path d="M24 63 Q 38 65 44 45 Q 30 43 24 63 Z" />
    <path d="M24 50 Q 12 52 7 33 Q 19 31 24 50 Z" />
    <path d="M24 39 Q 36 41 41 23 Q 28 21 24 39 Z" />
    <path d="M24 22 Q 18 13 24 3 Q 30 13 24 22 Z" />
  </svg>
);

// Logodagi 4-uchli yulduzcha (spark).
export const Spark = ({ className = "h-4 w-4" }: IconProps) => (
  <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" className={className}>
    <path d="M12 2 L13.6 10.4 22 12 13.6 13.6 12 22 10.4 13.6 2 12 10.4 10.4 Z" />
  </svg>
);
