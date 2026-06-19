import type { AgentTrace, TraceStep } from "@/types/trace";
import { AgentToolBadge } from "./AgentToolBadge";

function StepRow({ step }: { step: TraceStep }) {
  return (
    <li className="flex items-start gap-2 py-1.5">
      <AgentToolBadge kind={step.kind} />
      <div className="min-w-0">
        <div className="font-medium text-ink">{step.name}</div>
        {step.summary ? (
          <div className="text-muted text-base leading-snug">{step.summary}</div>
        ) : null}
      </div>
    </li>
  );
}

// Renders the latest turn's trace. The Trace Panel is both a product feature and
// a research artifact; full persistence + history arrives with #9.
export function AgentTracePanel({ trace }: { trace?: AgentTrace }) {
  return (
    <aside className="rounded-2xl bg-surface border border-black/5 p-5">
      <h2 className="text-lg font-semibold text-ink">Agent Trace</h2>
      <p className="text-muted text-base mt-1">
        每一轮对话经过哪些 Agent、Tool、Guard。
      </p>

      {!trace ? (
        <p className="text-muted text-base mt-4">
          发送一条消息后，这里会显示这一轮的路由与处理过程。
        </p>
      ) : (
        <div className="mt-4 space-y-4">
          <dl className="grid grid-cols-2 gap-x-3 gap-y-2 text-base">
            <dt className="text-muted">Route</dt>
            <dd className="text-ink font-medium">{trace.route}</dd>
            <dt className="text-muted">Risk</dt>
            <dd className="text-ink font-medium">{trace.risk_level}</dd>
            <dt className="text-muted">Mode</dt>
            <dd className="text-ink font-medium">{trace.mode}</dd>
          </dl>

          <div className="flex flex-wrap gap-2 text-base">
            <Flag label="Memory" on={trace.memory_used} />
            <Flag label="Retrieval" on={trace.retrieval_used} />
            <Flag label="SafetyCritic" on={trace.safety_critic_used} />
          </div>

          <Section title="Agents" steps={trace.agents} empty="（本轮无）" />
          <Section title="Tools" steps={trace.tools} empty="（本轮无）" />
          <Section title="Guards" steps={trace.guards} empty="（本轮无）" />
          {trace.state_event ? (
            <Section title="State event" steps={[trace.state_event]} empty="" />
          ) : null}
        </div>
      )}
    </aside>
  );
}

function Section({
  title,
  steps,
  empty,
}: {
  title: string;
  steps: TraceStep[];
  empty: string;
}) {
  return (
    <div>
      <h3 className="text-base font-semibold text-muted uppercase tracking-wide">
        {title}
      </h3>
      {steps.length === 0 ? (
        <p className="text-muted text-base">{empty}</p>
      ) : (
        <ul>
          {steps.map((step, index) => (
            <StepRow key={`${step.kind}-${step.name}-${index}`} step={step} />
          ))}
        </ul>
      )}
    </div>
  );
}

function Flag({ label, on }: { label: string; on: boolean }) {
  return (
    <span
      className={`rounded-md px-2 py-0.5 ${
        on ? "bg-companion-soft text-companion" : "bg-black/5 text-muted"
      }`}
    >
      {label}: {on ? "on" : "off"}
    </span>
  );
}
