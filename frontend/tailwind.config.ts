import type { Config } from "tailwindcss";

// Warm, calm, high-contrast palette tuned for older adults: large type, soft
// background, clear focus states. No youth-slang or playful styling.
const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#faf7f2",
        surface: "#ffffff",
        ink: "#1f2733",
        muted: "#5b6573",
        companion: {
          DEFAULT: "#2f6f6a",
          soft: "#e6f0ee",
        },
        user: {
          DEFAULT: "#3a5a9b",
          soft: "#e8eef7",
        },
        caution: {
          DEFAULT: "#8a6d1f",
          soft: "#fbf3dd",
        },
      },
      fontSize: {
        // Bump the base scale up one step for readability.
        base: ["1.125rem", { lineHeight: "1.7" }],
        lg: ["1.25rem", { lineHeight: "1.7" }],
        xl: ["1.5rem", { lineHeight: "1.6" }],
        "2xl": ["1.875rem", { lineHeight: "1.5" }],
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.5rem",
      },
    },
  },
  plugins: [],
};

export default config;
