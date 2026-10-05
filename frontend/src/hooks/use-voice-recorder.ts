// Reusable cross-platform voice recorder.
// Native: expo-audio. Web: MediaRecorder (webm/opus).
// Returns a File-like upload payload the backend can accept at any endpoint using
// FastAPI's `UploadFile = File(...)`.

import { Platform, Alert } from "react-native";
import {
  AudioModule,
  AudioRecorder,
  RecordingPresets,
  setAudioModeAsync,
  useAudioRecorder,
  useAudioRecorderState,
} from "expo-audio";
import { useCallback, useEffect, useRef, useState } from "react";
import { backendUrl as BURL } from "@/src/api";

export type RecState = "idle" | "requesting" | "listening" | "stopping" | "uploading" | "done" | "error";

type Options = { endpoint: string; extraForm?: Record<string, string>; maxMs?: number; language?: string };

type HookReturn = {
  state: RecState;
  elapsedMs: number;
  isWeb: boolean;
  start: () => Promise<void>;
  stop: () => Promise<any>;
  cancel: () => void;
  error: string | null;
  lastResponse: any;
};

export function useVoiceRecorder({ endpoint, extraForm, maxMs = 20000 }: Options): HookReturn {
  const [state, setState] = useState<RecState>("idle");
  const [elapsedMs, setElapsedMs] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [lastResponse, setLastResponse] = useState<any>(null);

  const startedAt = useRef<number>(0);
  const timerRef = useRef<any>(null);
  const watchdogRef = useRef<any>(null);

  // Native recorder
  const nativeRecorder: AudioRecorder = useAudioRecorder({ ...RecordingPresets.HIGH_QUALITY, isMeteringEnabled: true });
  const recorderState = useAudioRecorderState(nativeRecorder, 150);

  // Web recorder
  const mediaRecRef = useRef<any>(null);
  const webChunks = useRef<Blob[]>([]);

  const isWeb = Platform.OS === "web";

  const cleanupTimers = useCallback(() => {
    if (timerRef.current) clearInterval(timerRef.current);
    if (watchdogRef.current) clearTimeout(watchdogRef.current);
  }, []);

  const upload = async (payload: FormData): Promise<any> => {
    setState("uploading");
    try {
      const res = await fetch(`${BURL}${endpoint}`, { method: "POST", body: payload });
      if (!res.ok) throw new Error(`Server responded ${res.status}`);
      const data = await res.json();
      setLastResponse(data);
      setState("done");
      return data;
    } catch (e: any) {
      setError(e?.message || "Upload failed");
      setState("error");
      throw e;
    }
  };

  const start = useCallback(async () => {
    setError(null);
    setLastResponse(null);
    setElapsedMs(0);

    if (isWeb) {
      try {
        setState("requesting");
        // @ts-ignore
        const stream = await (navigator as any).mediaDevices.getUserMedia({ audio: true });
        const mime = (window as any).MediaRecorder?.isTypeSupported?.("audio/webm;codecs=opus") ? "audio/webm;codecs=opus" : "audio/webm";
        const mr = new (window as any).MediaRecorder(stream, { mimeType: mime });
        mediaRecRef.current = mr;
        webChunks.current = [];
        mr.ondataavailable = (e: any) => { if (e.data?.size > 0) webChunks.current.push(e.data); };
        mr.onstop = () => stream.getTracks().forEach((t: any) => t.stop());
        mr.start();
        setState("listening");
        startedAt.current = Date.now();
        timerRef.current = setInterval(() => setElapsedMs(Date.now() - startedAt.current), 100);
        watchdogRef.current = setTimeout(() => { stop(); }, maxMs);
      } catch (e: any) {
        setError(e?.message || "Microphone access denied");
        setState("error");
      }
      return;
    }

    // Native path
    try {
      setState("requesting");
      const perm = await AudioModule.requestRecordingPermissionsAsync();
      if (!perm.granted) {
        Alert.alert("Mic access needed", "Please allow microphone access to use voice features.");
        setState("error");
        setError("mic_denied");
        return;
      }
      await setAudioModeAsync({ playsInSilentMode: true, allowsRecording: true });
      await nativeRecorder.prepareToRecordAsync();
      nativeRecorder.record();
      setState("listening");
      startedAt.current = Date.now();
      timerRef.current = setInterval(() => setElapsedMs(Date.now() - startedAt.current), 100);
      watchdogRef.current = setTimeout(() => { stop(); }, maxMs);
    } catch (e: any) {
      setError(e?.message || "Could not start recording");
      setState("error");
    }
  }, [isWeb, maxMs, nativeRecorder]);

  const stop = useCallback(async (): Promise<any> => {
    cleanupTimers();
    try {
      if (isWeb) {
        const mr = mediaRecRef.current;
        if (!mr) return null;
        setState("stopping");
        await new Promise<void>((resolve) => {
          mr.addEventListener("stop", () => resolve(), { once: true });
          mr.stop();
        });
        const blob = new Blob(webChunks.current, { type: "audio/webm" });
        const form = new FormData();
        form.append("file", blob, "recording.webm");
        if (extraForm) for (const k of Object.keys(extraForm)) form.append(k, extraForm[k]);
        return await upload(form);
      }
      // Native
      setState("stopping");
      if (recorderState.isRecording) await nativeRecorder.stop();
      const uri = nativeRecorder.uri;
      if (!uri) throw new Error("No recording captured");
      // RN FormData — expo-audio writes an m4a
      const form = new FormData();
      // @ts-ignore
      form.append("file", { uri, name: "recording.m4a", type: "audio/m4a" });
      if (extraForm) for (const k of Object.keys(extraForm)) form.append(k, extraForm[k]);
      return await upload(form);
    } catch (e: any) {
      setError(e?.message || "Failed to stop recording");
      setState("error");
      return null;
    }
  }, [cleanupTimers, isWeb, nativeRecorder, recorderState.isRecording, extraForm]);

  const cancel = useCallback(() => {
    cleanupTimers();
    try {
      if (isWeb) mediaRecRef.current?.stop?.();
      else if (recorderState.isRecording) nativeRecorder.stop().catch(() => {});
    } catch {}
    webChunks.current = [];
    setState("idle"); setElapsedMs(0);
  }, [cleanupTimers, isWeb, nativeRecorder, recorderState.isRecording]);

  // Cleanup on unmount
  useEffect(() => () => { cancel(); }, [cancel]);

  return { state, elapsedMs, isWeb, start, stop, cancel, error, lastResponse };
}
