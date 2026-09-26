import React, { useState } from "react";
import { View, Text, StyleSheet, Pressable, ScrollView, TextInput, ActivityIndicator, KeyboardAvoidingView, Platform } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";
import { useAuth } from "@/src/auth-context";

const ROLES = ["Property Broker", "Land Aggregator", "JDA / Land-use Liaison", "Registry Agent", "Property Lawyer", "Home-loan Advisor", "RERA Consultant", "Developer", "Other"];

export default function BecomeAgent() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { user } = useAuth();
  const [name, setName] = useState(user?.name || "");
  const [mobile, setMobile] = useState(user?.mobile || "");
  const [firm, setFirm] = useState("");
  const [role, setRole] = useState<string | null>(null);
  const [area, setArea] = useState(user?.area || "");
  const [rera, setRera] = useState("");
  const [busy, setBusy] = useState(false);
  const [ok, setOk] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const canSubmit = name.trim().length >= 2 && mobile.trim().length >= 10 && !!role && area.trim().length >= 2;

  const submit = async () => {
    setErr(null);
    if (!canSubmit) { setErr("Please fill all required fields"); return; }
    setBusy(true);
    try {
      // We reuse the agent-enquiry endpoint to record an application (no dedicated agents-signup route yet).
      await api.post(`/agents/ag-01/enquiries`, {
        agent_id: "ag-01",
        user_id: user?.id,
        name: name.trim(),
        mobile: mobile.trim(),
        message: `Onboard request · Role: ${role}, Firm: ${firm || "N/A"}, Area: ${area}, RERA: ${rera || "not provided"}`,
      });
      setOk(true);
    } catch (e: any) {
      setErr(e.message || "Failed to submit");
    } finally { setBusy(false); }
  };

  return (
    <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : undefined} style={{ flex: 1, backgroundColor: colors.surface }}>
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="become-agent-back" onPress={() => router.back()} hitSlop={12}><Icon name="chevron-back" size={26} color={colors.onSurface} /></Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.title}>Work with InfraJagat</Text>
          <Text style={styles.sub}>Become a verified agent, developer or supplier</Text>
        </View>
      </View>

      {ok ? (
        <View style={styles.doneWrap}>
          <View style={styles.tick}><Icon name="checkmark" size={30} color="#FFFFFF" /></View>
          <Text style={styles.doneTitle}>Application received</Text>
          <Text style={styles.doneSub}>Our team will WhatsApp you within 24 hours to complete verification.</Text>
          <Pressable onPress={() => router.back()} style={styles.primaryBtn}><Text style={styles.primaryText}>Back to profile</Text></Pressable>
        </View>
      ) : (
        <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingBottom: 60 }}>
          <View style={styles.perkCard}>
            <Text style={styles.perkTitle}>Why join InfraJagat?</Text>
            <View style={{ gap: 6, marginTop: 6 }}>
              {[
                "Reach buyers actively searching in your locality",
                "Free profile with verified badge on approval",
                "WhatsApp-first buyer enquiries — no cold calls",
                "Bronze / Silver / Gold tier as you grow reviews",
              ].map(p => (
                <View key={p} style={{ flexDirection: "row", gap: 6, alignItems: "flex-start" }}>
                  <Icon name="checkmark-circle" size={14} color={colors.success} />
                  <Text style={styles.perk}>{p}</Text>
                </View>
              ))}
            </View>
          </View>

          <Field label="Full name" value={name} onChangeText={setName} placeholder="e.g. Rajesh Sharma" testID="ba-name" />
          <Field label="Mobile" value={mobile} onChangeText={setMobile} placeholder="10-digit mobile" keyboardType="phone-pad" testID="ba-mobile" />
          <Field label="Firm / Company (optional)" value={firm} onChangeText={setFirm} placeholder="e.g. Skyline Realty" testID="ba-firm" />

          <Text style={styles.label}>Role</Text>
          <View style={styles.chipsWrap}>
            {ROLES.map(r => {
              const active = role === r;
              return (
                <Pressable key={r} testID={`ba-role-${r.toLowerCase().replace(/[^a-z]/g, "-")}`} onPress={() => setRole(r)} style={[styles.chip, active && styles.chipActive]}>
                  <Text style={[styles.chipText, active && styles.chipTextActive]}>{r}</Text>
                </Pressable>
              );
            })}
          </View>

          <Field label="Primary area (locality / city)" value={area} onChangeText={setArea} placeholder="e.g. Ajmer Road, Jaipur" testID="ba-area" />
          <Field label="RERA / License number (optional)" value={rera} onChangeText={setRera} placeholder="e.g. RAJ/RERA/AGT/006" testID="ba-rera" />

          {err ? <Text style={styles.err}>{err}</Text> : null}

          <Pressable testID="ba-submit" disabled={!canSubmit || busy} onPress={submit} style={[styles.primaryBtn, { opacity: (!canSubmit || busy) ? 0.5 : 1 }]}>
            {busy ? <ActivityIndicator color={colors.onBrandPrimary} /> : <Text style={styles.primaryText}>Submit application</Text>}
          </Pressable>

          <Text style={styles.disclaimer}>By submitting you agree to InfraJagat contacting you via WhatsApp or phone to verify your details.</Text>
        </ScrollView>
      )}
    </KeyboardAvoidingView>
  );
}

function Field({ label, testID, ...rest }: any) {
  return (
    <View style={{ marginTop: spacing.md }}>
      <Text style={styles.label}>{label}</Text>
      <TextInput testID={testID} placeholderTextColor={colors.muted} style={styles.input} {...rest} />
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingHorizontal: spacing.lg, paddingBottom: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  title: { fontSize: 20, fontWeight: "800", color: colors.onSurface },
  sub: { fontSize: 11, color: colors.muted, marginTop: 2 },
  perkCard: { padding: spacing.md, borderRadius: radius.lg, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border, marginBottom: spacing.md },
  perkTitle: { fontSize: 13, fontWeight: "800", color: colors.onSurface },
  perk: { flex: 1, fontSize: 12, color: colors.onSurfaceSecondary, lineHeight: 17 },
  label: { fontSize: 12, fontWeight: "700", color: colors.muted, letterSpacing: 0.4, marginBottom: 6, textTransform: "uppercase" },
  input: { borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, paddingHorizontal: spacing.md, height: 46, fontSize: 14, color: colors.onSurface, backgroundColor: colors.surface },
  chipsWrap: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  chip: { paddingHorizontal: 12, paddingVertical: 8, borderRadius: radius.pill, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface },
  chipActive: { backgroundColor: colors.brandPrimary, borderColor: colors.brandPrimary },
  chipText: { fontSize: 12, fontWeight: "600", color: colors.onSurface },
  chipTextActive: { color: colors.onBrandPrimary },
  err: { color: colors.error, marginTop: spacing.md, fontSize: 12 },
  primaryBtn: { marginTop: spacing.lg, height: 50, borderRadius: radius.md, backgroundColor: colors.brandPrimary, alignItems: "center", justifyContent: "center", ...shadow.card },
  primaryText: { color: colors.onBrandPrimary, fontWeight: "800", fontSize: 15 },
  disclaimer: { fontSize: 10, color: colors.muted, marginTop: spacing.md, lineHeight: 15, textAlign: "center" },
  doneWrap: { alignItems: "center", padding: spacing.xxl, gap: spacing.md, marginTop: spacing.xxxl },
  tick: { width: 60, height: 60, borderRadius: 30, backgroundColor: colors.success, alignItems: "center", justifyContent: "center" },
  doneTitle: { fontSize: 18, fontWeight: "800", color: colors.onSurface },
  doneSub: { fontSize: 13, color: colors.muted, textAlign: "center", lineHeight: 18 },
});
