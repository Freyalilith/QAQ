// Reserved voice slot. Voice I/O (record → ASR → TTS) lands in Slice 7 (#4/#23).
// Disabled here so the layout is final and text chat is the Slice-1 fallback.
export function VoiceRecorderButton() {
  return (
    <button
      type="button"
      disabled
      aria-disabled
      title="语音功能即将上线，目前请使用文字输入"
      className="h-14 w-14 shrink-0 rounded-full bg-companion-soft text-companion text-2xl grid place-items-center opacity-60 cursor-not-allowed"
    >
      <span aria-hidden>🎤</span>
      <span className="sr-only">语音输入（即将上线）</span>
    </button>
  );
}
