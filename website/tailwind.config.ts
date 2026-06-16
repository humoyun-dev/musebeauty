import type { Config } from "tailwindcss";

// MUSE BEAUTY — logodan olingan palitra:
// blush krem fon · rose-gold/mauve signature · soft charcoal · nozik botanika.
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        porcelain: "#F8EEE9", // blush krem — sahifa foni
        shell: "#FCF7F3", // ochiqroq krem (logo foni) — kartalar
        ink: {
          DEFAULT: "#3B3834", // yumshoq charcoal (logo "MUSE")
          soft: "#7A716B", // ikkilamchi matn
          mute: "#A99E97", // placeholder / uchlamchi
        },
        rose: {
          // rose-gold / clay-rose (logo monogrammasi + "BEAUTY")
          DEFAULT: "#C28D85",
          50: "#FBF3F0",
          100: "#F5E6E1",
          200: "#EBD2CB",
          300: "#DEB8AF",
          400: "#D0A096",
          500: "#C28D85",
          600: "#A8736B",
          700: "#8C5A53",
        },
        gold: {
          // yumshoq rose-gold aksent (sariq emas)
          DEFAULT: "#C19A8D",
          light: "#E4CFC6",
        },
        line: "#ECDED7", // yumshoq rozе hairline
      },
      fontFamily: {
        serif: ['"Fraunces"', '"Playfair Display"', "Georgia", "serif"],
        sans: ['"Hanken Grotesk"', "system-ui", "sans-serif"],
      },
      borderRadius: {
        DEFAULT: "4px",
        sm: "3px",
        md: "6px",
        lg: "10px",
        xl: "16px",
      },
      letterSpacing: {
        eyebrow: "0.28em",
        wider2: "0.18em",
      },
      boxShadow: {
        soft: "0 1px 2px rgba(59,56,52,0.04), 0 14px 40px -18px rgba(166,115,107,0.20)",
        lift: "0 2px 8px rgba(59,56,52,0.06), 0 30px 60px -24px rgba(166,115,107,0.30)",
        ring: "inset 0 0 0 1px rgba(193,154,141,0.30)",
      },
      maxWidth: {
        page: "78rem",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(22px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        float: {
          "0%,100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-14px)" },
        },
        "float-slow": {
          "0%,100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-9px)" },
        },
        sway: {
          "0%,100%": { transform: "rotate(-3deg)" },
          "50%": { transform: "rotate(3deg)" },
        },
        marquee: {
          "0%": { transform: "translateX(0)" },
          "100%": { transform: "translateX(-50%)" },
        },
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.85s cubic-bezier(0.22,1,0.36,1) both",
        "fade-in": "fade-in 1.1s ease both",
        float: "float 7s ease-in-out infinite",
        "float-slow": "float-slow 9s ease-in-out infinite",
        sway: "sway 9s ease-in-out infinite",
        marquee: "marquee 38s linear infinite",
      },
    },
  },
  plugins: [],
};

export default config;
