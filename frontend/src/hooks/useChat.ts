"use client";

import { useCallback, useState } from "react";

import { sendChat } from "@/lib/apiClient";
import { DEFAULT_USER_ID } from "@/lib/constants";
import type { ChatMessage, CompanionMode } from "@/types/chat";

function newId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `m_${Date.now()}_${Math.floor(Math.random() * 1e6)}`;
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [mode, setMode] = useState<CompanionMode>("role_first");
  const [isSending, setIsSending] = useState(false);

  const send = useCallback(
    async (rawText: string) => {
      const text = rawText.trim();
      if (!text || isSending) return;

      const userMessage: ChatMessage = { id: newId(), role: "user", text };
      setMessages((prev) => [...prev, userMessage]);
      setIsSending(true);

      try {
        const response = await sendChat({
          user_id: DEFAULT_USER_ID,
          message: text,
          mode,
        });
        setMessages((prev) => [
          ...prev,
          {
            id: response.turn_id || newId(),
            role: "companion",
            text: response.response_text,
            trace: response.agent_trace,
          },
        ]);
      } catch {
        // Friendly local fallback: keep the chat usable if the backend is down.
        setMessages((prev) => [
          ...prev,
          {
            id: newId(),
            role: "companion",
            text: "我现在好像连不上后台服务。请确认后端已启动（http://localhost:8000），我们再继续聊。",
            isError: true,
          },
        ]);
      } finally {
        setIsSending(false);
      }
    },
    [isSending, mode],
  );

  return { messages, mode, setMode, isSending, send };
}
