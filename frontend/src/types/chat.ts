import type { AgentTrace } from "./trace";

export type CompanionMode = "role_first" | "neutral_assistant";

export interface ChatRequest {
  user_id: string;
  message: string;
  mode: CompanionMode;
  voice_enabled?: boolean;
  sensor_preset_id?: string | null;
  companion_display_name?: string | null;
}

export interface ChatResponse {
  turn_id: string;
  response_text: string;
  audio_url: string | null;
  agent_trace: AgentTrace;
}

// --- Voice I/O (#4) ---------------------------------------------------------

export interface ASRResponse {
  transcript: string;
  confidence: number;
  // False when nothing was recognized — UI shows a gentle retry prompt.
  ok: boolean;
  provider: string;
  is_mock: boolean;
}

export interface TTSResponse {
  audio_base64: string;
  content_type: string;
  provider: string;
  voice: string;
  cached: boolean;
  is_mock: boolean;
}

export type MessageRole = "user" | "companion";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  text: string;
  // Present on companion replies; drives the Agent Trace Panel.
  trace?: AgentTrace;
  // True for a friendly local fallback message (e.g. backend unreachable).
  isError?: boolean;
}
