/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        void: "#05090a",
        panel: "#10201e",
        line: "rgba(232, 243, 239, 0.14)",
        dust: "#b7a2ff",
        signal: "#53e0b0",
        warn: "#e8b86a",
        danger: "#ff7b87",
      },
      fontFamily: {
        display: ["\"IBM Plex Sans\"", "Segoe UI", "sans-serif"],
        mono: ["\"IBM Plex Mono\"", "ui-monospace", "monospace"],
      },
      boxShadow: {
        signal: "0 16px 44px rgba(83, 224, 176, 0.14)",
        violet: "0 16px 44px rgba(183, 162, 255, 0.14)",
      },
    },
  },
  plugins: [],
};
