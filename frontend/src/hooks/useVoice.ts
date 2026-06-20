"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { synthesizeSpeech, transcribeAudio } from "@/lib/apiClient";
import { base64ToBlob, isRecordingSupported } from "@/lib/audio";

export type RecorderState = "idle" | "recording" | "transcribing";

export interface VoiceControls {
  // Output (TTS)
  autoSpeak: boolean;
  setAutoSpeak: (on: boolean) => void;
  isSpeaking: boolean;
  isMockVoice: boolean;
  speak: (text: string) => void; // play / replay a reply on demand
  stopSpeaking: () => void;
  // Input (record → ASR)
  recordingSupported: boolean;
  recorderState: RecorderState;
  startRecording: () => void;
  stopRecording: () => void;
  // Gentle status, e.g. "我刚才没听清…". Null when there is nothing to say.
  hint: string | null;
  clearHint: () => void;
}

const DIDNT_CATCH = "我刚才没听清，您可以再说一次，或直接打字告诉我。";
const NO_MIC = "没能打开麦克风，请检查权限，或直接打字和我说话。";
const ASR_FAILED = "语音识别暂时没成功，您可以直接打字和我说话。";

// Orchestrates the mock voice loop (#4): press to record → ASR → feed the
// transcript into chat; auto-read or replay companion replies with TTS. Voice is
// always an enhancement — every failure path leaves the text chat fully usable.
export function useVoice({
  onTranscript,
}: {
  onTranscript: (text: string) => void;
}): VoiceControls {
  const [recordingSupported, setRecordingSupported] = useState(false);
  const [recorderState, setRecorderState] = useState<RecorderState>("idle");
  const [hint, setHint] = useState<string | null>(null);
  const [autoSpeak, setAutoSpeak] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isMockVoice, setIsMockVoice] = useState(false);

  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const lastUrlRef = useRef<string | null>(null);
  const lastTextRef = useRef<string | null>(null);

  // Keep the latest onTranscript without re-creating the recorder callbacks.
  const onTranscriptRef = useRef(onTranscript);
  useEffect(() => {
    onTranscriptRef.current = onTranscript;
  });

  useEffect(() => {
    setRecordingSupported(isRecordingSupported());
  }, []);

  const stopStream = useCallback(() => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
  }, []);

  // Release audio + mic when the chat unmounts.
  useEffect(() => {
    return () => {
      streamRef.current?.getTracks().forEach((track) => track.stop());
      audioRef.current?.pause();
      if (lastUrlRef.current) URL.revokeObjectURL(lastUrlRef.current);
    };
  }, []);

  const stopSpeaking = useCallback(() => {
    audioRef.current?.pause();
    setIsSpeaking(false);
  }, []);

  const speak = useCallback(async (text: string) => {
    const clean = text.trim();
    if (!clean) return;
    try {
      // Replay the same reply from the cached clip; otherwise synthesize.
      let url = lastUrlRef.current;
      if (!url || lastTextRef.current !== clean) {
        const result = await synthesizeSpeech(clean);
        setIsMockVoice(result.is_mock);
        const blob = base64ToBlob(result.audio_base64, result.content_type);
        if (lastUrlRef.current) URL.revokeObjectURL(lastUrlRef.current);
        url = URL.createObjectURL(blob);
        lastUrlRef.current = url;
        lastTextRef.current = clean;
      }

      let audio = audioRef.current;
      if (!audio) {
        audio = new Audio();
        audioRef.current = audio;
      }
      audio.pause();
      audio.src = url;
      audio.currentTime = 0;
      audio.onended = () => setIsSpeaking(false);
      audio.onerror = () => setIsSpeaking(false);
      setIsSpeaking(true);
      await audio.play();
    } catch {
      // Autoplay blocked / network hiccup — non-fatal, the text reply is shown.
      setIsSpeaking(false);
    }
  }, []);

  const startRecording = useCallback(async () => {
    if (!isRecordingSupported()) {
      setHint("这台设备暂时用不了麦克风，您可以直接打字和我说话。");
      return;
    }
    setHint(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };
      recorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, {
          type: recorder.mimeType || "audio/webm",
        });
        chunksRef.current = [];
        stopStream();
        setRecorderState("transcribing");
        try {
          const result = await transcribeAudio(blob);
          if (result.ok && result.transcript.trim()) {
            setHint(null);
            onTranscriptRef.current(result.transcript.trim());
          } else {
            setHint(DIDNT_CATCH);
          }
        } catch {
          setHint(ASR_FAILED);
        } finally {
          setRecorderState("idle");
        }
      };
      recorderRef.current = recorder;
      recorder.start();
      setRecorderState("recording");
    } catch {
      stopStream();
      setRecorderState("idle");
      setHint(NO_MIC);
    }
  }, [stopStream]);

  const stopRecording = useCallback(() => {
    const recorder = recorderRef.current;
    if (recorder && recorder.state !== "inactive") {
      recorder.stop();
    }
  }, []);

  const clearHint = useCallback(() => setHint(null), []);

  return {
    autoSpeak,
    setAutoSpeak,
    isSpeaking,
    isMockVoice,
    speak,
    stopSpeaking,
    recordingSupported,
    recorderState,
    startRecording,
    stopRecording,
    hint,
    clearHint,
  };
}
