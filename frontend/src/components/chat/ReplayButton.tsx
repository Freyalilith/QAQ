// Reserved TTS replay slot. Wired up with voice output in Slice 7 (#4/#23).
export function ReplayButton() {
  return (
    <button
      type="button"
      disabled
      aria-disabled
      title="语音重播即将上线"
      className="inline-flex items-center gap-2 rounded-xl px-3 py-2 text-base text-muted opacity-60 cursor-not-allowed"
    >
      <span aria-hidden>🔊</span>
      重播
    </button>
  );
}
