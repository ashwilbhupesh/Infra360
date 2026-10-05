import React, { useState } from "react";
import { View, Text, StyleSheet, Pressable, ScrollView, TextInput, Alert, Modal } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter, Stack } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { useLocationStore, SavedAddress } from "@/src/stores/location";

const TAG_OPTIONS: { value: SavedAddress["tag"]; label: string; icon: string }[] = [
  { value: "home", label: "Home", icon: "home" },
  { value: "work", label: "Work", icon: "briefcase" },
  { value: "other", label: "Other", icon: "bookmark" },
];

export default function Addresses() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { addresses, active_id, setActive, addAddress, updateAddress, removeAddress } = useLocationStore();
  const [editing, setEditing] = useState<SavedAddress | null>(null);
  const [draft, setDraft] = useState<Omit<SavedAddress, "id">>({ label: "", city: "Jaipur", area: "", tag: "home" });

  const openCreate = () => {
    setDraft({ label: "", city: "Jaipur", area: "", tag: "home" });
    setEditing({ id: "__new__", label: "", city: "Jaipur", area: "", tag: "home" });
  };
  const openEdit = (a: SavedAddress) => { setEditing(a); setDraft({ ...a }); };
  const closeEditor = () => setEditing(null);

  const save = () => {
    if (!draft.label.trim() || !draft.area.trim()) {
      Alert.alert("Fill required fields", "Label and area are required."); return;
    }
    if (editing?.id === "__new__") {
      const id = addAddress(draft);
      setActive(id);
    } else if (editing) {
      updateAddress(editing.id, draft);
    }
    closeEditor();
  };

  const confirmRemove = (a: SavedAddress) => {
    Alert.alert("Remove address?", a.label, [
      { text: "Cancel", style: "cancel" },
      { text: "Remove", style: "destructive", onPress: () => removeAddress(a.id) },
    ]);
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <Stack.Screen options={{ headerShown: false }} />
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="addr-back-btn" onPress={() => router.back()} hitSlop={12}>
          <Icon name="chevron-back" size={26} color={colors.onSurface} />
        </Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.title}>My addresses</Text>
          <Text style={styles.sub}>{addresses.length} saved · tap to activate</Text>
        </View>
        <Pressable testID="addr-add-btn" onPress={openCreate} style={styles.addBtn} hitSlop={10}>
          <Icon name="add" size={18} color={colors.onBrandPrimary} />
        </Pressable>
      </View>

      <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingBottom: 60, gap: 10 }}>
        {addresses.map(a => (
          <View key={a.id} style={[styles.card, a.id === active_id && styles.cardActive]} testID={`addr-row-${a.id}`}>
            <Pressable onPress={() => setActive(a.id)} style={{ flex: 1, flexDirection: "row", alignItems: "center", gap: 10 }}>
              <View style={[styles.icon, { backgroundColor: a.id === active_id ? colors.brandPrimary : colors.brandTertiary }]}>
                <Icon
                  name={a.tag === "home" ? "home" : a.tag === "work" ? "briefcase" : "bookmark"}
                  size={16}
                  color={a.id === active_id ? colors.onBrandPrimary : colors.brand}
                />
              </View>
              <View style={{ flex: 1 }}>
                <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
                  <Text style={styles.cardLabel} numberOfLines={1}>{a.label}</Text>
                  {a.id === active_id && (
                    <View style={styles.activePill}><Text style={styles.activePillTxt}>ACTIVE</Text></View>
                  )}
                </View>
                <Text style={styles.cardMeta} numberOfLines={1}>{a.area}, {a.city}{a.pincode ? ` · ${a.pincode}` : ""}</Text>
              </View>
            </Pressable>
            <View style={{ gap: 8 }}>
              <Pressable onPress={() => openEdit(a)} hitSlop={10} testID={`addr-edit-${a.id}`}>
                <Icon name="create-outline" size={16} color={colors.brand} />
              </Pressable>
              {a.id !== "addr-default-jaipur" && (
                <Pressable onPress={() => confirmRemove(a)} hitSlop={10} testID={`addr-del-${a.id}`}>
                  <Icon name="trash-outline" size={16} color={colors.error} />
                </Pressable>
              )}
            </View>
          </View>
        ))}

        <Pressable testID="addr-create-cta" onPress={openCreate} style={styles.createBtn}>
          <Icon name="add-circle-outline" size={18} color={colors.brand} />
          <Text style={styles.createTxt}>Add new address</Text>
        </Pressable>
      </ScrollView>

      <Modal visible={!!editing} transparent animationType="slide" onRequestClose={closeEditor}>
        <Pressable style={styles.backdrop} onPress={closeEditor}>
          <Pressable style={[styles.sheet, { paddingBottom: insets.bottom + spacing.lg }]} onPress={() => {}}>
            <View style={styles.sheetHandle} />
            <Text style={styles.sheetTitle}>{editing?.id === "__new__" ? "Add address" : "Edit address"}</Text>

            <Text style={styles.fieldLbl}>Label *</Text>
            <TextInput
              testID="addr-label-input"
              value={draft.label}
              onChangeText={v => setDraft(d => ({ ...d, label: v }))}
              placeholder="Home, Office, My plot in Sikar..."
              placeholderTextColor={colors.muted}
              style={styles.input}
            />

            <Text style={styles.fieldLbl}>Area / locality *</Text>
            <TextInput
              testID="addr-area-input"
              value={draft.area}
              onChangeText={v => setDraft(d => ({ ...d, area: v }))}
              placeholder="Vaishali Nagar, Jagatpura..."
              placeholderTextColor={colors.muted}
              style={styles.input}
            />

            <Text style={styles.fieldLbl}>City</Text>
            <TextInput
              testID="addr-city-input"
              value={draft.city}
              onChangeText={v => setDraft(d => ({ ...d, city: v }))}
              placeholder="Jaipur"
              placeholderTextColor={colors.muted}
              style={styles.input}
            />

            <Text style={styles.fieldLbl}>Pincode (optional)</Text>
            <TextInput
              testID="addr-pin-input"
              value={draft.pincode || ""}
              onChangeText={v => setDraft(d => ({ ...d, pincode: v.replace(/[^0-9]/g, "") }))}
              placeholder="302017"
              placeholderTextColor={colors.muted}
              keyboardType="numeric"
              style={styles.input}
            />

            <Text style={styles.fieldLbl}>Tag</Text>
            <View style={{ flexDirection: "row", gap: 6 }}>
              {TAG_OPTIONS.map(t => {
                const active = draft.tag === t.value;
                return (
                  <Pressable
                    key={t.value}
                    testID={`addr-tag-${t.value}`}
                    onPress={() => setDraft(d => ({ ...d, tag: t.value }))}
                    style={[styles.tagChip, active && styles.tagChipActive]}
                  >
                    <Icon name={t.icon} size={14} color={active ? colors.onBrandPrimary : colors.onSurface} />
                    <Text style={[styles.tagTxt, active && { color: colors.onBrandPrimary }]}>{t.label}</Text>
                  </Pressable>
                );
              })}
            </View>

            <View style={{ flexDirection: "row", gap: 8, marginTop: spacing.lg }}>
              <Pressable testID="addr-cancel" onPress={closeEditor} style={[styles.actionBtn, styles.actionGhost]}>
                <Text style={styles.actionTxt}>Cancel</Text>
              </Pressable>
              <Pressable testID="addr-save" onPress={save} style={[styles.actionBtn, styles.actionPrimary]}>
                <Text style={[styles.actionTxt, { color: colors.onBrandPrimary }]}>Save</Text>
              </Pressable>
            </View>
          </Pressable>
        </Pressable>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingHorizontal: spacing.lg, paddingBottom: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  title: { fontSize: 20, fontWeight: "800", color: colors.onSurface },
  sub: { fontSize: 11, color: colors.muted, marginTop: 2 },
  addBtn: { width: 36, height: 36, borderRadius: 18, backgroundColor: colors.brandPrimary, alignItems: "center", justifyContent: "center" },
  card: { flexDirection: "row", alignItems: "center", gap: 10, padding: spacing.md, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, ...shadow.card },
  cardActive: { borderColor: colors.brandPrimary, borderWidth: 2 },
  icon: { width: 40, height: 40, borderRadius: 20, alignItems: "center", justifyContent: "center" },
  cardLabel: { fontSize: 14, fontWeight: "800", color: colors.onSurface, flex: 1 },
  cardMeta: { fontSize: 11, color: colors.muted, marginTop: 2 },
  activePill: { paddingHorizontal: 6, paddingVertical: 2, borderRadius: radius.pill, backgroundColor: colors.brandPrimary },
  activePillTxt: { fontSize: 9, fontWeight: "800", color: colors.onBrandPrimary, letterSpacing: 0.5 },
  createBtn: { flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 8, paddingVertical: 14, borderRadius: radius.md, borderWidth: 2, borderStyle: "dashed", borderColor: colors.brand, backgroundColor: colors.surfaceSecondary, marginTop: 6 },
  createTxt: { fontSize: 14, fontWeight: "700", color: colors.brand },
  backdrop: { flex: 1, backgroundColor: "rgba(0,0,0,0.4)", justifyContent: "flex-end" },
  sheet: { backgroundColor: colors.surface, borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: spacing.lg },
  sheetHandle: { alignSelf: "center", width: 40, height: 4, borderRadius: 2, backgroundColor: colors.borderStrong, marginBottom: spacing.md },
  sheetTitle: { fontSize: 17, fontWeight: "800", color: colors.onSurface, marginBottom: spacing.md },
  fieldLbl: { fontSize: 11, fontWeight: "800", color: colors.muted, letterSpacing: 0.4, textTransform: "uppercase", marginTop: 10 },
  input: { borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, padding: spacing.md, color: colors.onSurface, fontSize: 14, backgroundColor: colors.surfaceSecondary, marginTop: 4 },
  tagChip: { flex: 1, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 6, paddingVertical: 10, borderRadius: radius.pill, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, marginTop: 4 },
  tagChipActive: { backgroundColor: colors.brandPrimary, borderColor: colors.brandPrimary },
  tagTxt: { fontSize: 13, fontWeight: "700", color: colors.onSurface },
  actionBtn: { flex: 1, paddingVertical: 12, borderRadius: radius.md, alignItems: "center", justifyContent: "center" },
  actionGhost: { backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border },
  actionPrimary: { backgroundColor: colors.brandPrimary },
  actionTxt: { fontSize: 14, fontWeight: "800", color: colors.onSurface },
});
