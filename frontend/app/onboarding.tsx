import { useState } from "react";
import { View, Text, TextInput, Pressable, StyleSheet, ActivityIndicator, KeyboardAvoidingView, Platform, ScrollView } from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";
import { useAuth } from "@/src/auth-context";

const PROFESSIONS = ["Buyer", "Investor", "Seller", "Broker", "Developer", "Architect", "Contractor", "Loan Advisor", "Lawyer", "Other"];

export default function Onboarding() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { setUser } = useAuth();
  const [name, setName] = useState("");
  const [mobile, setMobile] = useState("");
  const [area, setArea] = useState("");
  const [profession, setProfession] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const canSubmit = name.trim().length >= 2 && mobile.trim().length >= 10 && area.trim().length >= 2 && !!profession;

  const submit = async () => {
    setErr(null);
    if (!canSubmit) {
      setErr("Please fill all fields");
      return;
    }
    setBusy(true);
    try {
      const res = await api.post<{ user: any }>("/auth/onboard", { name: name.trim(), mobile: mobile.trim(), area: area.trim(), profession });
      await setUser(res.user);
      router.replace("/(tabs)/explore");
    } catch (e: any) {
      setErr(e.message || "Failed to continue");
    } finally {
      setBusy(false);
    }
  };

  return (
    <KeyboardAvoidingView style={{ flex: 1, backgroundColor: colors.surface }} behavior={Platform.OS === "ios" ? "padding" : "height"}>
      <ScrollView contentContainerStyle={[styles.container, { paddingTop: insets.top + spacing.xxl, paddingBottom: insets.bottom + spacing.xl }]} showsVerticalScrollIndicator={false}>
        <View style={styles.logoRow}>
          <View style={styles.logoDot} />
          <Text style={styles.logoText} testID="brand-text">InfraLocal</Text>
        </View>
        <Text style={styles.tagline}>Know Before You Buy.</Text>

        <Text style={styles.h1}>Welcome to InfraLocal</Text>
        <Text style={styles.sub}>Property, price, place & infrastructure intelligence for India.</Text>

        <View style={styles.field}>
          <Text style={styles.label}>Your name</Text>
          <TextInput
            testID="onboard-name-input"
            style={styles.input}
            value={name}
            onChangeText={setName}
            placeholder="Rahul Sharma"
            placeholderTextColor={colors.muted}
          />
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>Mobile number</Text>
          <TextInput
            testID="onboard-mobile-input"
            style={styles.input}
            value={mobile}
            onChangeText={(t) => setMobile(t.replace(/[^0-9+]/g, ""))}
            placeholder="+91 98xxxxxxxx"
            placeholderTextColor={colors.muted}
            keyboardType="phone-pad"
          />
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>City, town or village</Text>
          <TextInput
            testID="onboard-location-input"
            style={styles.input}
            value={area}
            onChangeText={setArea}
            placeholder="e.g. Jaipur, Chomu, Bagru"
            placeholderTextColor={colors.muted}
            autoCapitalize="words"
          />
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>What best describes you?</Text>
          <View style={styles.chipsWrap}>
            {PROFESSIONS.map(p => {
              const active = profession === p;
              return (
                <Pressable
                  key={p}
                  testID={`profession-chip-${p.toLowerCase().replace(/\s/g, "-")}`}
                  onPress={() => setProfession(p)}
                  style={[styles.chip, active && styles.chipActive]}
                >
                  <Text style={[styles.chipText, active && styles.chipTextActive]}>{p}</Text>
                </Pressable>
              );
            })}
          </View>
        </View>

        {err && <Text style={styles.err}>{err}</Text>}

        <Pressable
          testID="onboard-continue-btn"
          onPress={submit}
          disabled={!canSubmit || busy}
          style={[styles.cta, (!canSubmit || busy) && { opacity: 0.5 }]}
        >
          {busy ? <ActivityIndicator color={colors.onBrandPrimary} /> : <Text style={styles.ctaText}>Start Exploring</Text>}
        </Pressable>

        <Text style={styles.small}>No OTP. Demo prototype. Data is stored on your device.</Text>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { paddingHorizontal: spacing.xl },
  logoRow: { flexDirection: "row", alignItems: "center", gap: spacing.sm, marginBottom: spacing.xs },
  logoDot: { width: 10, height: 10, borderRadius: 5, backgroundColor: colors.brandPrimary },
  logoText: { fontSize: 18, fontWeight: "700", color: colors.brand, letterSpacing: 0.3 },
  tagline: { color: colors.muted, marginBottom: spacing.xxl },
  h1: { fontSize: 32, fontWeight: "700", color: colors.onSurface, letterSpacing: -0.5, lineHeight: 38 },
  sub: { color: colors.muted, marginTop: spacing.sm, marginBottom: spacing.xxl, fontSize: 15, lineHeight: 22 },
  field: { marginBottom: spacing.lg },
  label: { fontSize: 12, fontWeight: "600", color: colors.onSurfaceSecondary, marginBottom: spacing.sm, letterSpacing: 0.4, textTransform: "uppercase" },
  input: {
    borderWidth: 1, borderColor: colors.border, borderRadius: radius.md,
    paddingHorizontal: spacing.lg, paddingVertical: spacing.md, fontSize: 16, color: colors.onSurface,
    backgroundColor: colors.surfaceSecondary,
  },
  chipsWrap: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm },
  chip: { paddingHorizontal: spacing.lg, paddingVertical: spacing.sm + 2, borderRadius: radius.pill, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surfaceSecondary },
  chipActive: { backgroundColor: colors.brand, borderColor: colors.brand },
  chipText: { color: colors.onSurface, fontSize: 14, fontWeight: "500" },
  chipTextActive: { color: colors.onBrand, fontWeight: "600" },
  err: { color: colors.error, marginBottom: spacing.md },
  cta: {
    backgroundColor: colors.brandPrimary, borderRadius: radius.md, paddingVertical: spacing.lg,
    alignItems: "center", marginTop: spacing.md, ...shadow.floating,
  },
  ctaText: { color: colors.onBrandPrimary, fontSize: 16, fontWeight: "700", letterSpacing: 0.3 },
  small: { textAlign: "center", color: colors.muted, marginTop: spacing.lg, fontSize: 12 },
});
