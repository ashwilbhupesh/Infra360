import React, { useEffect } from "react";
import { View, Text, StyleSheet, Pressable, Modal, ActivityIndicator } from "react-native";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius } from "@/src/theme";
import { useVoiceRecorder } from "@/src/hooks/use-voice-recorder";

type Props = {
  visible: boolean;
  endpoint: string;
  title: string;
  subtitle: string;
  hint?: string;
  extraForm?: Record<string, string>;
  onClose: () => void;
  onResult: (data: any) => void;
};

export function VoiceSheet({ visible, endpoint, title, subtitle, hint, extraForm, onClose, onResult }: Props) {
  const rec = useVoiceRecorder({ endpoint, extraForm, maxMs: 25000 });

  // Auto-start when opened
  useEffect(() => {
    if (visible && rec.state === "idle") {
      rec.start();
    }
    if (!visible && rec.state === "listening") {
      rec.cancel();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [visible]);

  // When done, fire result then close
  useEffect(() => {
    if (rec.state === "done" && rec.lastResponse) {
      onResult(rec.lastResponse);
      // auto-close after a beat
      setTimeout(() => { onClose(); }, 500);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [rec.state]);

  const label = rec.state === "listening" ? "Listening..."
    : rec.state === "stopping" ? "Processing audio..."
    : rec.state === "uploading" ? "Thinking..."
    : rec.state === "requesting" ? "Starting mic..."
    : rec.state === "error" ? "Something went wrong"
    : rec.state === "done" ? "Done ✓" : "Tap to speak";

  const sec = (rec.elapsedMs / 1000).toFixed(1);

  const handleTap = async () => {
    if (rec.state === "listening") await rec.stop();
    else if (rec.state === "idle" || rec.state === "error") await rec.start();
  };

  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={() => { rec.cancel(); onClose(); }}>
      <Pressable style={styles.backdrop} onPress={() => { rec.cancel(); onClose(); }}>
        <Pressable style={styles.sheet} onPress={() => {}}>
          <View style={styles.handle} />
          <Text style={styles.title}>{title}</Text>
          <Text style={styles.subtitle}>{subtitle}</Text>
          {hint ? <Text style={styles.hint}>{hint}</Text> : null}

          <Pressable testID="voice-mic-btn" onPress={handleTap} style={[styles.mic, rec.state === "listening" && styles.micListening]}>
            {["requesting", "stopping", "uploading"].includes(rec.state) ? (
              <ActivityIndicator color="#FFFFFF" size="large" />
            ) : (
              <Icon name={rec.state === "listening" ? "stop" : "mic"} size={34} color="#FFFFFF" />
            )}
            {rec.state === "listening" && (
              <>
                <View style={[styles.pulse, styles.pulse1]} />
                <View style={[styles.pulse, styles.pulse2]} />
              </>
            )}
          </Pressable>
          <Text style={styles.state}>{label}</Text>
          {rec.state === "listening" && <Text style={styles.timer}>{sec}s</Text>}
          {rec.error && <Text style={styles.err}>{rec.error}</Text>}

          <Pressable testID="voice-cancel" onPress={() => { rec.cancel(); onClose(); }} style={styles.cancelBtn}>
            <Text style={styles.cancelTxt}>Cancel</Text>
          </Pressable>
        </Pressable>
      </Pressable>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: { flex: 1, backgroundColor: "rgba(0,0,0,0.55)", justifyContent: "flex-end" },
  sheet: { backgroundColor: colors.surface, borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: spacing.xl, paddingBottom: spacing.xxl, alignItems: "center" },
  handle: { width: 40, height: 4, borderRadius: 2, backgroundColor: colors.borderStrong, marginBottom: spacing.md },
  title: { fontSize: 18, fontWeight: "800", color: colors.onSurface },
  subtitle: { fontSize: 13, color: colors.muted, marginTop: 4, textAlign: "center", paddingHorizontal: spacing.lg },
  hint: { fontSize: 11, color: colors.muted, marginTop: spacing.sm, textAlign: "center", fontStyle: "italic" },
  mic: { width: 110, height: 110, borderRadius: 55, backgroundColor: colors.brandPrimary, alignItems: "center", justifyContent: "center", marginTop: spacing.xl, marginBottom: spacing.md },
  micListening: { backgroundColor: colors.error },
  pulse: { position: "absolute", width: 110, height: 110, borderRadius: 55, borderWidth: 3, borderColor: colors.error },
  pulse1: { transform: [{ scale: 1.25 }], opacity: 0.4 },
  pulse2: { transform: [{ scale: 1.5 }], opacity: 0.2 },
  state: { fontSize: 14, fontWeight: "700", color: colors.onSurface, marginTop: 4 },
  timer: { fontSize: 12, color: colors.muted, marginTop: 4 },
  err: { fontSize: 12, color: colors.error, marginTop: 6 },
  cancelBtn: { marginTop: spacing.lg, paddingVertical: 10, paddingHorizontal: 20 },
  cancelTxt: { fontSize: 13, fontWeight: "700", color: colors.muted },
});
