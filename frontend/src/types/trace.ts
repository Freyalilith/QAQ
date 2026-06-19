// Mirrors backend app/schemas/trace.py. Keeps the Agent / Tool / Guard
// distinction visible (AGENTS.md §5, §13).

export type TraceEntryKind =
  | "agent"
  | "tool"
  | "guard"
  | "state_event"
  | "retrieval"
  | "memory";

export interface TraceStep {
  kind: TraceEntryKind;
  name: string;
  summary?: string;
  detail?: Record<string, unknown>;
}

export interface AgentTrace {
  turn_id: string;
  mode: string;
  route: string;
  risk_level: string;
  agents: TraceStep[];
  tools: TraceStep[];
  guards: TraceStep[];
  state_event: TraceStep | null;
  memory_used: boolean;
  retrieval_used: boolean;
  safety_critic_used: boolean;
}
