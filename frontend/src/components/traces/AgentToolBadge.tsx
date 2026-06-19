import type { TraceEntryKind } from "@/types/trace";

// Color + label per kind so the UI never calls a tool an "agent" (AGENTS.md §5).
const KIND_STYLES: Record<TraceEntryKind, { label: string; className: string }> =
  {
    agent: { label: "Agent", className: "bg-companion-soft text-companion" },
    tool: { label: "Tool", className: "bg-user-soft text-user" },
    guard: { label: "Guard", className: "bg-caution-soft text-caution" },
    state_event: { label: "StateEvent", className: "bg-black/5 text-muted" },
    retrieval: { label: "Retrieval", className: "bg-user-soft text-user" },
    memory: { label: "Memory", className: "bg-black/5 text-muted" },
  };

export function AgentToolBadge({ kind }: { kind: TraceEntryKind }) {
  const style = KIND_STYLES[kind] ?? KIND_STYLES.tool;
  return (
    <span
      className={`inline-block rounded-md px-2 py-0.5 text-sm font-medium ${style.className}`}
    >
      {style.label}
    </span>
  );
}
