"use client";

import type { RecorderState } from "@/hooks/useVoice";

// Voice input (#4): press once to start recording, press again to stop. The clip
// is uploaded to the mock ASR and the transcript is sent as a chat message. When
// the device has no microphone the button is disabled and text input still works.
export function VoiceRecorderButton({
  supported,
  state,
  disabled = false,
  onStart,
  onStop,
}: {
  supported: boolean;
  state: RecorderState;
  disabled?: boolean;
  onStart: () => void;
  onStop: () => void;
}) {
  const recording = state === "recording";
  const transcribing = state === "transcribing";
  const isDisabled = disabled || transcribing || !supported;

  const title = !supported
    ? "这台设备暂时用不了麦克风，请使用文字输入"
    : transcribing
      ? "正在识别…"
      : recording
        ? "点击停止说话"
        : "点击开始说话";

  const label = !supported
    ? "语音输入（不可用）"
    : transcribing
      ? "正在识别"
      : recording
        ? "停止说话"
        : "开始说话";

  const appearance = recording
    ? "bg-companion text-white animate-pulse"
    : "bg-companion-soft text-companion";

  return (
    <button
      type="button"
      onClick={recording ? onStop : onStart}
      disabled={isDisabled}
      aria-pressed={recording}
      title={title}
      className={`h-14 w-14 shrink-0 rounded-full text-2xl grid place-items-center disabled:opacity-60 disabled:cursor-not-allowed ${appearance}`}
    >
      <span aria-hidden>{transcribing ? "⏳" : recording ? "⏹" : "🎤"}</span>
      <span className="sr-only">{label}</span>
    </button>
  );
}
