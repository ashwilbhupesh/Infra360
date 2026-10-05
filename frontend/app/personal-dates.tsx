import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, Pressable, ScrollView, ActivityIndicator, Platform, Alert } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter, Stack } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import DateTimePicker from "@react-native-community/datetimepicker";
import { colors, spacing, radius } from "@/src/theme";
import { api } from "@/src/api";
import { useAuth } from "@/src/auth-context";

type DateField = "dob" | "spouse_dob" | "anniversary";

const META: Record<DateField, { label: string; icon: any; hint: string }> = {
  dob: { label: "Your birthday", icon: "calendar-outline", hint: "We'll remember to wish you." },
  spouse_dob: { label: "Spouse's birthday", icon: "heart-outline", hint: "A gentle reminder each year." },
  anniversary: { label: "Wedding anniversary", icon: "ribbon-outline", hint: "Marked for a yearly nudge." },
};

function toISO(d: Date) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function formatDisplay(iso?: string | null) {
  if (!iso) return "Add date";
  const [y, m, d] = iso.split("-").map(Number);
  if (!y || !m || !d) return "Add date";
  const date = new Date(y, m - 1, d);
  return date.toLocaleDateString("en-IN", { day: "2-digit", month: "long", year: "numeric" });
}

function daysUntilNext(iso?: string | null) {
  if (!iso) return null;
  const [y, m, d] = iso.split("-").map(Number);
  if (!y || !m || !d) return null;
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  const thisYear = new Date(now.getFullYear(), m - 1, d);
  let target = thisYear;
  if (thisYear < now) target = new Date(now.getFullYear() + 1, m - 1, d);
  const diff = Math.round((target.getTime() - now.getTime()) / (24 * 60 * 60 * 1000));
  return diff;
}

export default function PersonalDates() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { user, setUser } = useAuth();
  const [dob, setDob] = useState<string | null>(null);
  const [spouseDob, setSpouseDob] = useState<string | null>(null);
  const [anniversary, setAnniversary] = useState<string | null>(null);
  const [picker, setPicker] = useState<DateField | null>(null);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      if (!user) { setLoading(false); return; }
      try {
        const u = await api.get<any>(`/auth/me?user_id=${user.id}`);
        setDob(u.dob ?? null);
        setSpouseDob(u.spouse_dob ?? null);
        setAnniversary(u.anniversary ?? null);
      } finally { setLoading(false); }
    })();
  }, [user]);

  const valueFor = (field: DateField) =>
    field === "dob" ? dob : field === "spouse_dob" ? spouseDob : anniversary;

  const setFor = (field: DateField, iso: string | null) => {
    if (field === "dob") setDob(iso);
    else if (field === "spouse_dob") setSpouseDob(iso);
    else setAnniversary(iso);
  };

  const onPickerChange = (_: any, selected?: Date) => {
    if (Platform.OS === "android") setPicker(null);
    if (!selected || !picker) return;
    setFor(picker, toISO(selected));
  };

  const save = async () => {
    if (!user) return;
    setSaving(true);
    try {
      const u = await api.put<any>(`/users/${user.id}/dates`, {
        dob: dob ?? "",
        spouse_dob: spouseDob ?? "",
        anniversary: anniversary ?? "",
      });
      setUser({ ...user, ...u } as any);
      Alert.alert("Saved", "We'll remind you on these dates.");
    } catch (e: any) {
      Alert.alert("Couldn't save", e?.message || "Please try again.");
    } finally { setSaving(false); }
  };

  const clearField = (field: DateField) => {
    Alert.alert("Clear date?", `Remove your ${META[field].label.toLowerCase()}?`, [
      { text: "Cancel", style: "cancel" },
      { text: "Clear", style: "destructive", onPress: () => setFor(field, null) },
    ]);
  };

  const renderRow = (field: DateField) => {
    const iso = valueFor(field);
    const days = daysUntilNext(iso);
    return (
      <Pressable
        key={field}
        testID={`date-row-${field}`}
        onPress={() => setPicker(field)}
        style={styles.row}
      >
        <View style={styles.rowIcon}>
          <Icon name={META[field].icon} size={20} color={colors.brand} />
        </View>
        <View style={{ flex: 1 }}>
          <Text style={styles.rowLabel}>{META[field].label}</Text>
          <Text style={[styles.rowValue, !iso && styles.rowValueEmpty]} numberOfLines={1}>
            {formatDisplay(iso)}
          </Text>
          <Text style={styles.rowHint}>
            {iso && days !== null
              ? days === 0
                ? "🎉 Today!"
                : `In ${days} day${days > 1 ? "s" : ""}`
              : META[field].hint}
          </Text>
        </View>
        {iso ? (
          <Pressable testID={`date-clear-${field}`} onPress={() => clearField(field)} hitSlop={12}>
            <Icon name="close-circle" size={20} color={colors.muted} />
          </Pressable>
        ) : (
          <Icon name="chevron-forward" size={20} color={colors.muted} />
        )}
      </Pressable>
    );
  };

  const pickerValue = picker ? (valueFor(picker) ? new Date(valueFor(picker)!) : new Date(1990, 0, 1)) : new Date();

  return (
    <View style={{ flex: 1, backgroundColor: colors.surfaceSecondary }}>
      <Stack.Screen options={{ headerShown: false }} />
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="dates-back" onPress={() => router.back()} hitSlop={12}>
          <Icon name="chevron-back" size={26} color={colors.onSurface} />
        </Pressable>
        <Text style={styles.title}>Important dates</Text>
        <View style={{ width: 26 }} />
      </View>

      {loading ? (
        <ActivityIndicator color={colors.brand} style={{ marginTop: spacing.xxl }} />
      ) : (
        <ScrollView contentContainerStyle={{ padding: spacing.xl, paddingBottom: 120 }}>
          <View style={styles.hero}>
            <Icon name="gift" size={28} color={colors.brand} />
            <Text style={styles.heroTitle}>Never miss a special day</Text>
            <Text style={styles.heroSub}>
              Add your birthday, your spouse's birthday and your anniversary. We'll gently remind you —
              and brokers who send you offers can tailor them to your family moments.
            </Text>
          </View>

          <View style={styles.card}>
            {renderRow("dob")}
            <View style={styles.divider} />
            {renderRow("spouse_dob")}
            <View style={styles.divider} />
            {renderRow("anniversary")}
          </View>

          <Text style={styles.note}>
            Dates are stored on your profile only. You can clear any field anytime.
          </Text>
        </ScrollView>
      )}

      {picker && Platform.OS === "ios" ? (
        <View style={styles.iosPickerSheet}>
          <View style={styles.iosPickerBar}>
            <Pressable testID="date-cancel" onPress={() => setPicker(null)}><Text style={styles.iosPickerBtn}>Cancel</Text></Pressable>
            <Text style={styles.iosPickerTitle}>{META[picker].label}</Text>
            <Pressable testID="date-done" onPress={() => setPicker(null)}><Text style={[styles.iosPickerBtn, { color: colors.brandPrimary, fontWeight: "800" }]}>Done</Text></Pressable>
          </View>
          <DateTimePicker
            testID="date-picker"
            value={pickerValue}
            mode="date"
            display="spinner"
            maximumDate={new Date()}
            minimumDate={new Date(1900, 0, 1)}
            onChange={onPickerChange}
          />
        </View>
      ) : null}
      {picker && Platform.OS !== "ios" ? (
        <DateTimePicker
          testID="date-picker"
          value={pickerValue}
          mode="date"
          display="default"
          maximumDate={new Date()}
          minimumDate={new Date(1900, 0, 1)}
          onChange={onPickerChange}
        />
      ) : null}

      <View style={[styles.footer, { paddingBottom: Math.max(insets.bottom, 10) + 10 }]}>
        <Pressable
          testID="dates-save"
          onPress={save}
          disabled={saving}
          style={[styles.saveBtn, saving && { opacity: 0.6 }]}
        >
          <Text style={styles.saveText}>{saving ? "Saving…" : "Save dates"}</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  header: {
    flexDirection: "row", alignItems: "center", justifyContent: "space-between",
    paddingHorizontal: spacing.xl, paddingBottom: spacing.md,
    backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border,
  },
  title: { fontSize: 18, fontWeight: "800", color: colors.onSurface, letterSpacing: -0.2 },
  hero: { backgroundColor: colors.brandTertiary, borderRadius: radius.lg, padding: spacing.lg, marginBottom: spacing.lg, gap: 8 },
  heroTitle: { fontSize: 16, fontWeight: "800", color: colors.brand },
  heroSub: { fontSize: 12, color: colors.brand, lineHeight: 17, opacity: 0.9 },
  card: { backgroundColor: colors.surface, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, overflow: "hidden" },
  row: { flexDirection: "row", alignItems: "center", gap: spacing.md, padding: spacing.lg },
  rowIcon: { width: 42, height: 42, borderRadius: 21, backgroundColor: colors.surfaceSecondary, alignItems: "center", justifyContent: "center" },
  rowLabel: { fontSize: 11, fontWeight: "800", color: colors.muted, letterSpacing: 0.5, textTransform: "uppercase" },
  rowValue: { fontSize: 15, fontWeight: "700", color: colors.onSurface, marginTop: 2 },
  rowValueEmpty: { color: colors.muted, fontWeight: "500" },
  rowHint: { fontSize: 11, color: colors.muted, marginTop: 3 },
  divider: { height: 1, backgroundColor: colors.border, marginLeft: spacing.xxl + spacing.md },
  note: { fontSize: 11, color: colors.muted, textAlign: "center", marginTop: spacing.lg, lineHeight: 16 },
  footer: {
    position: "absolute", bottom: 0, left: 0, right: 0,
    paddingHorizontal: spacing.xl, paddingTop: 10,
    backgroundColor: colors.surface, borderTopWidth: 1, borderTopColor: colors.border,
  },
  saveBtn: { backgroundColor: colors.brandPrimary, paddingVertical: 14, borderRadius: radius.pill, alignItems: "center" },
  saveText: { color: colors.onBrandPrimary, fontSize: 14, fontWeight: "800" },
  iosPickerSheet: { position: "absolute", left: 0, right: 0, bottom: 0, backgroundColor: colors.surface, borderTopWidth: 1, borderTopColor: colors.border },
  iosPickerBar: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", padding: 12, borderBottomWidth: 1, borderBottomColor: colors.border },
  iosPickerBtn: { fontSize: 14, color: colors.onSurface },
  iosPickerTitle: { fontSize: 13, fontWeight: "700", color: colors.onSurface },
});
