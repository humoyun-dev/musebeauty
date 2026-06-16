"use client";

import { useState } from "react";

// Brend emblemi — logo rasmi yuklanmasa ham "MB" monogramma ko'rinadi (hech qachon bo'sh qolmaydi).
export function BrandEmblem({
  className = "h-11 w-11",
  ring = true,
}: {
  className?: string;
  ring?: boolean;
}) {
  const [failed, setFailed] = useState(false);

  return (
    <span
      className={`relative inline-flex shrink-0 items-center justify-center overflow-hidden rounded-full bg-shell ${
        ring ? "ring-1 ring-rose-200/70" : ""
      } ${className}`}
    >
      {!failed ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src="/logo.jpg"
          alt="MUSE BEAUTY logotipi"
          onError={() => setFailed(true)}
          className="h-full w-full object-cover"
        />
      ) : (
        <svg viewBox="0 0 100 100" className="h-full w-full" role="img" aria-label="MUSE BEAUTY">
          <circle cx="50" cy="50" r="47" fill="none" stroke="#DEB8AF" strokeWidth="1.5" />
          <text
            x="50"
            y="56"
            textAnchor="middle"
            dominantBaseline="middle"
            fontFamily='"Fraunces", Georgia, serif'
            fontSize="42"
            fontWeight="500"
            letterSpacing="-2"
            fill="#C28D85"
          >
            MB
          </text>
        </svg>
      )}
    </span>
  );
}
