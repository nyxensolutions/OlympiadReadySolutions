import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#2563eb",
          50: "#eff6ff",
          600: "#2563eb",
          700: "#1d4ed8"
        },
        achiever: {
          DEFAULT: "#f59e0b",
          50: "#fffbeb",
          600: "#f59e0b",
          700: "#b45309"
        }
      }
    }
  },
  plugins: []
};

export default config;
