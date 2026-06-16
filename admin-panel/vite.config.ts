import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Past RAM da build OOM bo'lmasligi uchun sourcemap o'chiq (README ogohlantirishi).
export default defineConfig({
  plugins: [react()],
  build: {
    sourcemap: false,
    chunkSizeWarningLimit: 1500,
  },
  server: {
    port: 5173,
    // Dev'da yuklangan rasmlar (/media) backenddan ko'rinishi uchun
    proxy: {
      "/media": "http://localhost:8000",
    },
  },
});
