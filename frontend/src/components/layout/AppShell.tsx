import type { ReactNode } from "react";

import { COMPANION_FALLBACK_NAME } from "@/lib/constants";

// Header shows the companion's display name. Until onboarding (#21) stores a
// user-chosen `companion_display_name`, it shows the neutral fallback.
export function AppShell({
  children,
  companionDisplayName,
}: {
  children: ReactNode;
  companionDisplayName?: string | null;
}) {
  const title =
    companionDisplayName && companionDisplayName.trim()
      ? companionDisplayName.trim()
      : COMPANION_FALLBACK_NAME;

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-surface border-b border-black/5">
        <div className="mx-auto max-w-5xl px-5 py-4 flex items-center gap-3">
          <span
            aria-hidden
            className="h-11 w-11 shrink-0 rounded-full bg-companion-soft text-companion grid place-items-center text-xl"
          >
            🌿
          </span>
          <div className="min-w-0">
            <h1 className="text-xl font-semibold text-ink truncate">{title}</h1>
            <p className="text-muted text-base">陪伴优先 · 放心使用</p>
          </div>
        </div>
      </header>

      <main className="flex-1">
        <div className="mx-auto max-w-5xl px-5 py-6">{children}</div>
      </main>
    </div>
  );
}
