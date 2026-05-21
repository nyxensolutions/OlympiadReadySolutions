import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        // Primary: indigo — modern, academic, distinct from competitors' blue
        brand: {
          DEFAULT: "#6366f1",
          50:  "#eef2ff",
          100: "#e0e7ff",
          200: "#c7d2fe",
          400: "#818cf8",
          500: "#6366f1",
          600: "#6366f1",
          700: "#4f46e5",
          800: "#4338ca",
        },
        // Secondary: violet — used in gradients paired with brand
        accent: {
          DEFAULT: "#8b5cf6",
          50:  "#f5f3ff",
          200: "#ddd6fe",
          600: "#8b5cf6",
          700: "#7c3aed",
        },
        // CTA: warm orange — high contrast on dark backgrounds, inviting
        cta: {
          DEFAULT: "#f97316",
          50:  "#fff7ed",
          600: "#f97316",
          700: "#ea580c",
        },
        // Achiever: kept for flag/reward UI (same orange family)
        achiever: {
          DEFAULT: "#f97316",
          50:  "#fff7ed",
          600: "#f97316",
          700: "#ea580c",
        },
        success: {
          DEFAULT: "#10b981",
          50:  "#f0fdf4",
          600: "#16a34a",
          700: "#15803d",
        },
        dark: {
          bg:     "#0f172a",
          card:   "#1e293b",
          border: "#334155",
          text:   "#f1f5f9",
        },
      },
      backgroundImage: {
        // Deep indigo-to-violet — premium, eye-friendly, not heavy navy
        "gradient-hero":   "linear-gradient(135deg, #1e1b4b 0%, #3730a3 50%, #6d28d9 100%)",
        // Lighter brand gradient for page headers / cards
        "gradient-brand":  "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
        // Warm gradient for CTAs / achiever callouts
        "gradient-warm":   "linear-gradient(135deg, #f97316 0%, #f59e0b 100%)",
      },
    },
  },
  plugins: [],
};

export default config;
