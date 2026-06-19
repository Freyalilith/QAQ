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
