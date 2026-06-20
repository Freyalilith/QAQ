"use client";

import { useEffect, useRef } from "react";

import { useChat } from "@/hooks/useChat";
import { useVoice } from "@/hooks/useVoice";
import type { AgentTrace } from "@/types/trace";
import { AgentTracePanel } from "@/components/traces/AgentTracePanel";
import { useProfile } from "@/components/profile/ProfileProvider";
import { DEFAULT_USER_ID } from "@/lib/constants";
import { ChatWindow } from "./ChatWindow";
import { SafetyBanner } from "./SafetyBanner";

// Composes the chat surface: safety banner slot, chat window, and the live Agent
// Trace panel. The companion name comes from the user profile (#21); the neutral
// fallback shows until the user names it. Voice (#4) records into chat and reads
// replies aloud; it is an enhancement layered over the text chat.
export function ChatExperience() {
  const { companionDisplayName } = useProfile();
  const { messages, mode, setMode, isSending, send } = useChat();
  const voice = useVoice({ onTranscript: send });

  // Read each newly-arrived companion reply aloud when auto-read is on. Keyed by
  // message id so toggling the switch never re-reads an older reply.
  const voiceRef = useRef(voice);
  voiceRef.current = voice;
  const spokenIdRef = useRef<string | null>(null);
  useEffect(() => {
    const latest = [...messages]
      .reverse()
      .find((message) => message.role === "companion" && !message.isError);
    if (!latest || spokenIdRef.current === latest.id) return;
    spokenIdRef.current = latest.id;
    if (voiceRef.current.autoSpeak) voiceRef.current.speak(latest.text);
  }, [messages]);

  const latestTrace: AgentTrace | undefined = [...messages]
    .reverse()
    .find((message) => message.trace)?.trace;

  return (
    <div className="space-y-5">
      <SafetyBanner />
      <div className="grid gap-5 lg:grid-cols-[1fr_22rem]">
        <ChatWindow
          messages={messages}
          isSending={isSending}
          mode={mode}
          onChangeMode={setMode}
          onSend={send}
          companionDisplayName={companionDisplayName}
          voice={voice}
        />
        <AgentTracePanel
          latestTrace={latestTrace}
          userId={DEFAULT_USER_ID}
          refreshKey={messages.length}
        />
      </div>
    </div>
  );
}
