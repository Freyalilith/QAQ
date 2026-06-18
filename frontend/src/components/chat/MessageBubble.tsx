import { COMPANION_FALLBACK_NAME_SHORT } from "@/lib/constants";
import type { ChatMessage } from "@/types/chat";

export function MessageBubble({
  message,
  companionDisplayName,
}: {
  message: ChatMessage;
  companionDisplayName?: string | null;
}) {
  const isUser = message.role === "user";
  const companionLabel =
    companionDisplayName && companionDisplayName.trim()
      ? companionDisplayName.trim()
      : COMPANION_FALLBACK_NAME_SHORT;

  return (
    <div className={isUser ? "flex justify-end" : "flex justify-start"}>
      <div className="max-w-[85%]">
        <div
          className={`mb-1 text-base ${isUser ? "text-right text-muted" : "text-companion"}`}
        >
          {isUser ? "您" : companionLabel}
        </div>
        <div
          className={[
            "rounded-2xl px-5 py-3 text-lg leading-relaxed whitespace-pre-wrap break-words",
            isUser
              ? "bg-user-soft text-ink rounded-tr-sm"
              : message.isError
                ? "bg-caution-soft text-caution rounded-tl-sm"
                : "bg-companion-soft text-ink rounded-tl-sm",
          ].join(" ")}
        >
          {message.text}
        </div>
      </div>
    </div>
  );
}
