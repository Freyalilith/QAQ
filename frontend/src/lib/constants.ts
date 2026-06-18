// Neutral fallback shown until the user names the companion during onboarding
// (#21). Never hardcode an invented fixed name (AGENTS.md §4.1).
export const COMPANION_FALLBACK_NAME = "陪伴 AI / AI Companion";

// Short form used inside chat bubbles / labels.
export const COMPANION_FALLBACK_NAME_SHORT = "陪伴 AI";

export const DEFAULT_USER_ID = "demo_user";

// Base URL for the FastAPI backend. Override via NEXT_PUBLIC_API_BASE_URL.
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
