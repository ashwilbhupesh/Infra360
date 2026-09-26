import React, { useEffect, useRef, useState } from "react";
import { View, Text, TextInput, Pressable, StyleSheet, ActivityIndicator, KeyboardAvoidingView, Platform } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";
import { useAuth } from "@/src/auth-context";

// MVP OTP verification. Any code other than 0000 is rejected client-side.
// TODO: wire to real SMS provider in Phase 2.
const MOCK_OTP = "0000";
const LEN = 4;

export default function OtpVerify() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { setUser } = useAuth();
  const params = useLocalSearchParams<{ name?: string; mobile?: string; area?: string; profession?: string }>();
  const inputs = useRef<Array<TextInput | null>>([]);
  const [digits, setDigits] = useState<string[]>(Array(LEN).fill(""));
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [resendIn, setResendIn] = useState(30);

  useEffect(() => {
    const id = setInterval(() => setResendIn(n => (n > 0 ? n - 1 : 0)), 1000);
    return () => clearInterval(id);
  }, []);

  const setAt = (idx: number, v: string) => {
    const clean = v.replace(/[^0-9]/g, "").slice(-1);
    const next = [...digits];
    next[idx] = clean;
    setDigits(next);
    if (clean && idx < LEN - 1) inputs.current[idx + 1]?.focus();
    if (!clean && idx > 0) inputs.current[idx - 1]?.focus();
    if (next.every(d => d !== "")) verify(next.join(""));
  };

  const verify = async (code: string) => {
    setErr(null);
    if (code !== MOCK_OTP) {
      setErr("Incorrect OTP. Hint for the MVP: use 0000.");
      return;
    }
    if (!params.name || !params.mobile) {
      setErr("Missing details. Please go back.");
      return;
    }
    setBusy(true);
    try {
      const res = await api.post<{ user: any }>("/auth/onboard", {
        name: String(params.name),
        mobile: String(params.mobile),
        area: params.area ? String(params.area) : undefined,
        profession: params.profession ? String(params.profession) : undefined,
      });
      await setUser({ ...res.user, verified: true });
      router.replace("/(tabs)/explore");
    } catch (e: any) {
      setErr(e.message || "Failed to verify. Please try again.");
    } finally {
      setBusy(false);
    }
  };

  const resend = () => {
    if (resendIn > 0) return;
    setResendIn(30);
    setDigits(Array(LEN).fill(""));
    inputs.current[0]?.focus();
  };

  return (
    <KeyboardAvoidingView style={{ flex: 1, backgroundColor: colors.surface }} behavior={Platform.OS === "ios" ? "padding" : "height"}>
      <View style={{ paddingTop: insets.top + spacing.md, paddingHorizontal: spacing.xl }}>
        <Pressable testID="otp-back" onPress={() => router.back()} hitSlop={12} style={{ width: 40 }}>
          <Icon name="chevron-back" size={26} color={colors.onSurface} />
        </Pressable>
      </View>

      <View style={styles.body}>
        <View style={styles.iconWrap}>
          <Icon name="phone-portrait-outline" size={32} color={colors.brand} />
        </View>
        <Text style={styles.title}>Verify your mobile</Text>
        <Text style={styles.sub}>We sent a 4-digit code to</Text>
        <Text style={styles.phone}>+91 {params.mobile}</Text>

        <View style={styles.otpRow}>
          {digits.map((d, i) => (
            <TextInput
              key={i}
              ref={r => { inputs.current[i] = r; }}
              testID={`otp-input-${i}`}
              value={d}
              onChangeText={(v) => setAt(i, v)}
              onKeyPress={(e) => {
                if (e.nativeEvent.key === "Backspace" && !d && i > 0) inputs.current[i - 1]?.focus();
              }}
              keyboardType="number-pad"
              maxLength={1}
              autoFocus={i === 0}
              style={[styles.otpBox, err && styles.otpBoxErr, d && styles.otpBoxFilled]}
            />
          ))}
        </View>

        {err ? <Text style={styles.err} testID="otp-error">{err}</Text> : null}

        <View style={styles.hintCard}>
          <Icon name="information-circle-outline" size={14} color={colors.brand} />
          <Text style={styles.hint}>MVP demo · use OTP <Text style={{ fontWeight: "800", color: colors.brand }}>0000</Text> to continue.</Text>
        </View>

        <Pressable
          testID="otp-verify-btn"
          disabled={busy || digits.some(d => !d)}
          onPress={() => verify(digits.join(""))}
          style={[styles.cta, (busy || digits.some(d => !d)) && { opacity: 0.5 }]}
        >
          {busy ? <ActivityIndicator color={colors.onBrandPrimary} /> : <Text style={styles.ctaText}>Verify & continue</Text>}
        </Pressable>

        <Pressable testID="otp-resend-btn" onPress={resend} disabled={resendIn > 0} style={{ marginTop: spacing.md }}>
          <Text style={[styles.resend, resendIn > 0 && { color: colors.muted }]}>
            {resendIn > 0 ? `Resend OTP in ${resendIn}s` : "Resend OTP"}
          </Text>
        </Pressable>

        <Pressable testID="otp-change-number" onPress={() => router.back()} style={{ marginTop: spacing.xs }}>
          <Text style={styles.change}>Change number</Text>
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  body: { flex: 1, paddingHorizontal: spacing.xl, paddingTop: spacing.xl, alignItems: "center" },
  iconWrap: { width: 68, height: 68, borderRadius: 34, backgroundColor: colors.surfaceSecondary, alignItems: "center", justifyContent: "center", borderWidth: 1, borderColor: colors.border },
  title: { fontSize: 22, fontWeight: "800", color: colors.onSurface, marginTop: spacing.lg, letterSpacing: 0.2 },
  sub: { color: colors.muted, fontSize: 13, marginTop: 4 },
  phone: { color: colors.onSurface, fontSize: 15, fontWeight: "700", marginTop: 2 },
  otpRow: { flexDirection: "row", gap: 12, marginTop: spacing.xxl },
  otpBox: { width: 58, height: 62, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, textAlign: "center", fontSize: 22, fontWeight: "800", color: colors.onSurface },
  otpBoxFilled: { borderColor: colors.brandPrimary, backgroundColor: colors.surface },
  otpBoxErr: { borderColor: colors.error },
  err: { color: colors.error, marginTop: spacing.md, fontSize: 12, textAlign: "center" },
  hintCard: { flexDirection: "row", alignItems: "center", gap: 6, marginTop: spacing.lg, paddingHorizontal: 12, paddingVertical: 8, borderRadius: radius.pill, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border },
  hint: { fontSize: 11, color: colors.onSurfaceSecondary },
  cta: { marginTop: spacing.xl, height: 50, borderRadius: radius.md, backgroundColor: colors.brandPrimary, alignItems: "center", justifyContent: "center", alignSelf: "stretch", ...shadow.card },
  ctaText: { color: colors.onBrandPrimary, fontWeight: "800", fontSize: 15, letterSpacing: 0.3 },
  resend: { color: colors.brand, fontWeight: "700", fontSize: 13, textAlign: "center" },
  change: { color: colors.muted, fontWeight: "600", fontSize: 12, textAlign: "center", textDecorationLine: "underline" },
});
