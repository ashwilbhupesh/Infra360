import React, { useMemo, useState } from "react";
import { View, Text, StyleSheet, ScrollView, TextInput, Pressable, ActivityIndicator, KeyboardAvoidingView, Platform, Alert } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";
import { useLocationStore } from "@/src/stores/location";

type RoleOption = { id: string; label: string; icon: string };

const EXPERT_ROLES: RoleOption[] = [
  { id: "Broker",       label: "Property Broker",     icon: "home-outline" },
  { id: "Loan Advisor", label: "Loan / Finance",      icon: "cash-outline" },
  { id: "Lawyer",       label: "Property Lawyer",     icon: "briefcase-outline" },
  { id: "JDA Liaison",  label: "JDA / Govt. Liaison", icon: "document-text-outline" },
  { id: "Marketing",    label: "Marketing / Sales",   icon: "megaphone-outline" },
  { id: "Architect",    label: "Architect",           icon: "construct-outline" },
];

const BUSINESS_ROLES: RoleOption[] = [
  { id: "Cement & Steel",      label: "Cement / Steel",       icon: "cube-outline" },
  { id: "Tiles & Marble",      label: "Tiles / Marble",       icon: "grid-outline" },
  { id: "Electrical",          label: "Electrical / Lights",  icon: "bulb-outline" },
  { id: "Plumbing & Sanitary", label: "Plumbing / Sanitary",  icon: "water-outline" },
  { id: "Paint & Hardware",    label: "Paint / Hardware",     icon: "color-palette-outline" },
  { id: "Interior Studio",     label: "Interior Studio",      icon: "color-wand-outline" },
  { id: "Packers & Movers",    label: "Packers & Movers",     icon: "car-outline" },
  { id: "Modular Kitchen",     label: "Modular Kitchen",      icon: "restaurant-outline" },
  { id: "Other",               label: "Something else",       icon: "ellipsis-horizontal" },
];

export default function RegisterScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const params = useLocalSearchParams<{ type?: string }>();
  const rawType = (params.type || "expert").toString().toLowerCase();
  const type: "expert" | "business" = rawType === "business" ? "business" : "expert";

  const active = useLocationStore(s => s.getActive());
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("");
  const [city, setCity] = useState(active?.city || "Jaipur");
  const [area, setArea] = useState(active?.area || "");
  const [services, setServices] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [done, setDone] = useState<string | null>(null);

  const roles = useMemo(() => (type === "expert" ? EXPERT_ROLES : BUSINESS_ROLES), [type]);
  const header = type === "expert" ? "Register as an Expert" : "List your business";
  const sub = type === "expert"
    ? "Join 1,200+ brokers, lawyers and loan advisors already on InfraJagat."
    : "Get discovered by thousands of buyers, builders and interior designers.";
  const servicesPh = type === "expert"
    ? "e.g. Plot sales in Jagatpura, loan tie-ups with HDFC"
    : "e.g. Birla A1 cement, TMT bars, delivery across Jaipur";

  const canSubmit = name.trim().length >= 2 && phone.replace(/\D/g, "").length >= 10 && !!role;

  const submit = async () => {
    setErr(null);
    setBusy(true);
    try {
      const res = await api.post<{ ok: boolean; id: string; message: string }>("/registrations", {
        type, name: name.trim(), phone: phone.trim(), role,
        city: city.trim(), area: area.trim(), services: services.trim(),
        email: email.trim() || undefined,
      });
      setDone(res?.message || "Thanks! We'll call you shortly.");
    } catch (e: any) {
      setErr(e?.message || "Could not submit. Please try again.");
    } finally {
      setBusy(false);
    }
  };

  if (done) {
    return (
      <View style={[styles.doneWrap, { paddingTop: insets.top + spacing.xl }]}>
        <View style={styles.doneIcon}>
          <Icon name="checkmark" size={40} color={colors.onBrandPrimary} />
        </View>
        <Text style={styles.doneTitle}>You{"\u2019"}re on the list!</Text>
        <Text style={styles.doneMsg}>{done}</Text>
        <Pressable testID="done-back-btn" onPress={() => router.back()} style={styles.primaryBtn}>
          <Text style={styles.primaryText}>Back</Text>
        </Pressable>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1, backgroundColor: colors.surface }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <View style={[styles.header, { paddingTop: insets.top + spacing.sm }]}>
        <Pressable testID="close-btn" onPress={() => router.back()} style={styles.closeBtn}>
          <Icon name="close" size={20} color={colors.onSurface} />
        </Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.kicker}>{type === "expert" ? "EXPERTS" : "MARKET"}</Text>
          <Text style={styles.title}>{header}</Text>
        </View>
      </View>

      <ScrollView contentContainerStyle={styles.body} keyboardShouldPersistTaps="handled">
        <Text style={styles.sub}>{sub}</Text>

        <Text style={styles.label}>Full Name</Text>
        <TextInput
          testID="reg-name-input"
          style={styles.input}
          placeholder="Rahul Sharma"
          placeholderTextColor={colors.muted}
          value={name}
          onChangeText={setName}
          autoCapitalize="words"
        />

        <Text style={styles.label}>Mobile Number</Text>
        <TextInput
          testID="reg-phone-input"
          style={styles.input}
          placeholder="98xxxxxxxx"
          placeholderTextColor={colors.muted}
          keyboardType="phone-pad"
          value={phone}
          onChangeText={setPhone}
          maxLength={13}
        />

        <Text style={styles.label}>Email (optional)</Text>
        <TextInput
          testID="reg-email-input"
          style={styles.input}
          placeholder="you@example.com"
          placeholderTextColor={colors.muted}
          keyboardType="email-address"
          autoCapitalize="none"
          value={email}
          onChangeText={setEmail}
        />

        <Text style={styles.label}>{type === "expert" ? "I am a" : "Business category"}</Text>
        <View style={styles.chipsWrap}>
          {roles.map(r => (
            <Pressable
              key={r.id}
              testID={`reg-role-${r.id.replace(/\s/g, "-").toLowerCase()}`}
              onPress={() => setRole(r.id)}
              style={[styles.roleChip, role === r.id && styles.roleChipActive]}
            >
              <Icon name={r.icon as any} size={14} color={role === r.id ? colors.onBrand : colors.onSurface} />
              <Text style={[styles.roleChipText, role === r.id && styles.roleChipTextActive]}>{r.label}</Text>
            </Pressable>
          ))}
        </View>

        <View style={styles.row2}>
          <View style={{ flex: 1 }}>
            <Text style={styles.label}>City</Text>
            <TextInput
              testID="reg-city-input"
              style={styles.input}
              placeholder="Jaipur"
              placeholderTextColor={colors.muted}
              value={city}
              onChangeText={setCity}
            />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.label}>Area</Text>
            <TextInput
              testID="reg-area-input"
              style={styles.input}
              placeholder="Jagatpura"
              placeholderTextColor={colors.muted}
              value={area}
              onChangeText={setArea}
            />
          </View>
        </View>

        <Text style={styles.label}>{type === "expert" ? "What do you specialise in?" : "What do you sell / offer?"}</Text>
        <TextInput
          testID="reg-services-input"
          style={[styles.input, { height: 96, textAlignVertical: "top" }]}
          placeholder={servicesPh}
          placeholderTextColor={colors.muted}
          multiline
          value={services}
          onChangeText={setServices}
        />

        <Text style={styles.privacy}>
          By continuing, you agree our team may contact you on this number for verification.
        </Text>
        {err ? <Text style={styles.err}>{err}</Text> : null}
      </ScrollView>

      <View style={[styles.footer, { paddingBottom: insets.bottom + spacing.md }]}>
        <Pressable
          testID="reg-submit-btn"
          disabled={!canSubmit || busy}
          onPress={() => {
            if (!canSubmit) {
              Alert.alert("Fill required fields", "Name, mobile and category are required.");
              return;
            }
            submit();
          }}
          style={[styles.primaryBtn, (!canSubmit || busy) && { opacity: 0.5 }]}
        >
          {busy ? <ActivityIndicator color={colors.onBrandPrimary} /> : <Text style={styles.primaryText}>Submit</Text>}
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingHorizontal: spacing.lg, paddingBottom: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  closeBtn: { width: 36, height: 36, borderRadius: 18, backgroundColor: colors.surfaceSecondary, alignItems: "center", justifyContent: "center" },
  kicker: { fontSize: 10, fontWeight: "800", color: colors.muted, letterSpacing: 1 },
  title: { fontSize: 20, fontWeight: "800", color: colors.onSurface, marginTop: 2, letterSpacing: -0.3 },
  body: { padding: spacing.xl, paddingBottom: 140 },
  sub: { fontSize: 13, color: colors.muted, marginBottom: spacing.lg, lineHeight: 19 },
  label: { fontSize: 11, fontWeight: "800", color: colors.muted, letterSpacing: 0.5, textTransform: "uppercase", marginBottom: spacing.sm, marginTop: spacing.sm },
  input: { borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, padding: spacing.md, fontSize: 15, color: colors.onSurface, backgroundColor: colors.surfaceSecondary },
  chipsWrap: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm, marginBottom: spacing.md },
  roleChip: { flexDirection: "row", alignItems: "center", gap: 6, paddingHorizontal: spacing.md, paddingVertical: spacing.sm + 2, borderRadius: radius.pill, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border },
  roleChipActive: { backgroundColor: colors.brand, borderColor: colors.brand },
  roleChipText: { color: colors.onSurface, fontSize: 13, fontWeight: "600" },
  roleChipTextActive: { color: colors.onBrand, fontWeight: "700" },
  row2: { flexDirection: "row", gap: spacing.sm },
  privacy: { fontSize: 11, color: colors.muted, marginTop: spacing.lg, lineHeight: 16 },
  err: { color: colors.error, marginTop: spacing.md, fontSize: 13 },
  footer: { position: "absolute", left: 0, right: 0, bottom: 0, padding: spacing.lg, backgroundColor: colors.surface, borderTopWidth: 1, borderTopColor: colors.border },
  primaryBtn: { backgroundColor: colors.brandPrimary, alignItems: "center", justifyContent: "center", paddingVertical: spacing.md + 2, borderRadius: radius.md, ...shadow.card },
  primaryText: { color: colors.onBrandPrimary, fontWeight: "800", fontSize: 15 },
  doneWrap: { flex: 1, backgroundColor: colors.surface, alignItems: "center", paddingHorizontal: spacing.xl, gap: spacing.md },
  doneIcon: { width: 80, height: 80, borderRadius: 40, backgroundColor: colors.brandPrimary, alignItems: "center", justifyContent: "center", marginTop: spacing.xl },
  doneTitle: { fontSize: 22, fontWeight: "800", color: colors.onSurface, marginTop: spacing.sm },
  doneMsg: { fontSize: 14, color: colors.muted, textAlign: "center", marginBottom: spacing.lg, lineHeight: 20 },
});
