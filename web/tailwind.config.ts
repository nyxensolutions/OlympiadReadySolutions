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
          100: "#dbeafe",
          600: "#2563eb",
          700: "#1d4ed8"
        },
        accent: {
          DEFAULT: "#7c3aed",
          50: "#faf5ff",
          600: "#7c3aed",
          700: "#6d28d9"
        },
        achiever: {
          DEFAULT: "#f97316",
          50: "#fff7ed",
          600: "#f97316",
          700: "#ea580c"
        },
        success: {
          DEFAULT: "#10b981",
          50: "#f0fdf4",
          600: "#16a34a",
          700: "#15803d"
        },
        dark: {
          bg: "#0f172a",
          card: "#1e293b",
          border: "#334155",
          text: "#f1f5f9"
        }
      },
      backgroundImage: {
        "gradient-hero": "linear-gradient(135deg, #1d4ed8 0%, #4f46e5 100%)",
        "gradient-accent": "linear-gradient(135deg, #f97316 0%, #f59e0b 100%)"
      }
    }
  },
  plugins: []
};

export default config;
