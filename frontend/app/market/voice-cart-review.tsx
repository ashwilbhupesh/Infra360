import React from "react";
import { View, Text, StyleSheet, Pressable, ScrollView, Alert } from "react-native";
import { Image } from "expo-image";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter, Stack } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { useVoiceDraft } from "@/src/stores/voice-draft";
import { useMaterialsCart } from "@/src/stores/materials-cart";
import { indianComma } from "@/src/utils/format";

export default function VoiceCartReview() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { draft, updateQty, removeLine, setDraft } = useVoiceDraft();
  const addToCart = useMaterialsCart(s => s.add);

  if (!draft) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.surface, alignItems: "center", justifyContent: "center", padding: spacing.xxl }}>
        <Stack.Screen options={{ headerShown: false }} />
        <Icon name="mic-outline" size={44} color={colors.muted} />
        <Text style={{ fontSize: 15, fontWeight: "800", color: colors.onSurface, marginTop: spacing.md }}>No draft to review</Text>
        <Text style={{ fontSize: 12, color: colors.muted, textAlign: "center", marginTop: 4 }}>Narrate or scan a materials list first.</Text>
        <Pressable onPress={() => router.replace("/(tabs)/market" as any)} style={{ marginTop: spacing.lg, paddingVertical: 12, paddingHorizontal: 20, borderRadius: radius.md, backgroundColor: colors.brandPrimary }}>
          <Text style={{ color: colors.onBrandPrimary, fontWeight: "800" }}>Back to Market</Text>
        </Pressable>
      </View>
    );
  }

  const confirm = () => {
    if (!draft.items.length) {
      Alert.alert("Nothing to add", "Add at least one item or discard this draft.");
      return;
    }
    for (const l of draft.items) {
      addToCart({
        id: l.product_id, store_id: l.store_id, store_name: l.store_name || "",
        name: l.name, brand: l.brand, image: l.image, unit: l.unit, price: l.price,
      }, l.qty);
    }
    setDraft(null);
    Alert.alert("Added to cart ✅", `${draft.items.length} item${draft.items.length === 1 ? "" : "s"} added.`, [
      { text: "View cart", onPress: () => router.replace("/materials/cart" as any) },
      { text: "Keep shopping", onPress: () => router.replace("/(tabs)/market" as any) },
    ]);
  };

  const discard = () => {
    Alert.alert("Discard draft?", "Items will be removed from this preview.", [
      { text: "Cancel", style: "cancel" },
      { text: "Discard", style: "destructive", onPress: () => { setDraft(null); router.back(); } },
    ]);
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <Stack.Screen options={{ headerShown: false }} />
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="draft-back" onPress={() => router.back()} hitSlop={12}>
          <Icon name="chevron-back" size={26} color={colors.onSurface} />
        </Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.title}>Review your cart</Text>
          <Text style={styles.sub}>{draft.items.length} item{draft.items.length === 1 ? "" : "s"} · Tweak quantities before adding</Text>
        </View>
      </View>

      <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingBottom: 160, gap: spacing.md }}>
        {draft.translation ? (
          <View style={styles.quoteCard}>
            <Icon name={draft.source === "voice" ? "mic" : "scan"} size={14} color={colors.brand} />
            <Text style={styles.quoteTxt} numberOfLines={3}>“{draft.translation}”</Text>
          </View>
        ) : null}

        {draft.items.length === 0 ? (
          <Text style={styles.empty}>Draft is empty — discard and try again.</Text>
        ) : draft.items.map((l, i) => (
          <View key={`${l.product_id}-${i}`} style={styles.lineCard} testID={`draft-line-${i}`}>
            <Image source={{ uri: l.image }} style={styles.lineImg} contentFit="cover" />
            <View style={{ flex: 1 }}>
              <Text style={styles.lineName} numberOfLines={2}>{l.name}</Text>
              <Text style={styles.lineBrand}>{l.brand || "—"}{l.unit ? ` · per ${l.unit}` : ""}</Text>
              <Text style={styles.lineStore} numberOfLines={1}>{l.store_name}{l.store_area ? ` · ${l.store_area}` : ""}</Text>
              {l.query?.raw ? <Text style={styles.lineRaw} numberOfLines={1}>“{l.query.raw}”</Text> : null}
              <View style={styles.qtyRow}>
                <Pressable testID={`draft-dec-${i}`} onPress={() => updateQty(i, l.qty - 1)} style={styles.qtyBtn} hitSlop={8}>
                  <Icon name="remove" size={14} color={colors.onSurface} />
                </Pressable>
                <Text style={styles.qtyVal}>{l.qty}</Text>
                <Pressable testID={`draft-inc-${i}`} onPress={() => updateQty(i, l.qty + 1)} style={styles.qtyBtn} hitSlop={8}>
                  <Icon name="add" size={14} color={colors.onSurface} />
                </Pressable>
                <View style={{ flex: 1 }} />
                <Pressable testID={`draft-remove-${i}`} onPress={() => removeLine(i)} hitSlop={10}>
                  <Icon name="trash-outline" size={16} color={colors.error} />
                </Pressable>
              </View>
            </View>
            <View style={{ alignItems: "flex-end", gap: 2 }}>
              <Text style={styles.lineUnitPrice}>₹{indianComma(l.price)}</Text>
              <Text style={styles.lineSub}>Line ₹{indianComma(l.subtotal)}</Text>
            </View>
          </View>
        ))}

        {draft.unmatched?.length > 0 && (
          <View style={styles.unmatchedBlock}>
            <Text style={styles.unmatchedTitle}>{draft.unmatched.length} not matched</Text>
            {draft.unmatched.map((u, i) => (
              <Text key={i} style={styles.unmatchedLine}>• {u.query?.raw || u.query?.name || "Unknown"}</Text>
            ))}
            <Text style={styles.unmatchedHint}>Add these later from Shop by category — our catalogue is growing.</Text>
          </View>
        )}

        <View style={styles.totalCard}>
          <Text style={styles.totalLbl}>DRAFT TOTAL</Text>
          <Text style={styles.totalVal}>₹{indianComma(draft.total_estimated)}</Text>
        </View>
      </ScrollView>

      <View style={[styles.ctaBar, { paddingBottom: insets.bottom + spacing.md }]}>
        <Pressable testID="draft-discard" onPress={discard} style={styles.ghostBtn}>
          <Icon name="close" size={16} color={colors.error} />
          <Text style={[styles.ghostTxt]}>Discard</Text>
        </Pressable>
        <Pressable testID="draft-confirm" onPress={confirm} style={styles.primaryBtn}>
          <Icon name="cart" size={16} color={colors.onBrandPrimary} />
          <Text style={styles.primaryTxt}>Add {draft.items.length} to cart · ₹{indianComma(draft.total_estimated)}</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingHorizontal: spacing.lg, paddingBottom: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  title: { fontSize: 20, fontWeight: "800", color: colors.onSurface },
  sub: { fontSize: 11, color: colors.muted, marginTop: 2 },
  quoteCard: { flexDirection: "row", gap: 8, padding: spacing.md, borderRadius: radius.md, backgroundColor: colors.brandTertiary, borderWidth: 1, borderColor: colors.brand },
  quoteTxt: { flex: 1, fontSize: 12, color: colors.onSurface, fontStyle: "italic", lineHeight: 17 },
  lineCard: { flexDirection: "row", gap: 10, padding: 10, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface },
  lineImg: { width: 60, height: 60, borderRadius: 8, backgroundColor: colors.surfaceSecondary },
  lineName: { fontSize: 13, fontWeight: "800", color: colors.onSurface, lineHeight: 17 },
  lineBrand: { fontSize: 11, color: colors.muted, marginTop: 2 },
  lineStore: { fontSize: 11, color: colors.brand, marginTop: 4, fontWeight: "700" },
  lineRaw: { fontSize: 11, color: colors.muted, marginTop: 4, fontStyle: "italic" },
  qtyRow: { flexDirection: "row", alignItems: "center", gap: 8, marginTop: 8 },
  qtyBtn: { width: 28, height: 28, borderRadius: 14, borderWidth: 1, borderColor: colors.border, alignItems: "center", justifyContent: "center", backgroundColor: colors.surfaceSecondary },
  qtyVal: { fontSize: 14, fontWeight: "800", color: colors.onSurface, minWidth: 22, textAlign: "center" },
  lineUnitPrice: { fontSize: 14, fontWeight: "800", color: colors.brandPrimary },
  lineSub: { fontSize: 10, color: colors.muted },
  unmatchedBlock: { padding: spacing.md, borderRadius: radius.md, backgroundColor: "#FFF4F2", borderWidth: 1, borderColor: colors.error, gap: 2 },
  unmatchedTitle: { fontSize: 12, fontWeight: "800", color: colors.error, letterSpacing: 0.4 },
  unmatchedLine: { fontSize: 12, color: colors.onSurface, marginTop: 4 },
  unmatchedHint: { fontSize: 11, color: colors.muted, marginTop: 6, fontStyle: "italic" },
  totalCard: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", padding: spacing.md, borderRadius: radius.md, backgroundColor: "#EDF4FF", borderWidth: 1, borderColor: "#C8DBF9" },
  totalLbl: { fontSize: 11, fontWeight: "800", color: colors.muted, letterSpacing: 0.6 },
  totalVal: { fontSize: 22, fontWeight: "800", color: colors.brand },
  empty: { textAlign: "center", padding: spacing.xxl, color: colors.muted },
  ctaBar: { position: "absolute", left: 0, right: 0, bottom: 0, padding: spacing.lg, flexDirection: "row", gap: 8, backgroundColor: colors.surface, borderTopWidth: 1, borderTopColor: colors.border, ...shadow.floating },
  ghostBtn: { flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 6, paddingVertical: 14, paddingHorizontal: 16, borderRadius: radius.md, borderWidth: 1, borderColor: colors.error, backgroundColor: colors.surfaceSecondary },
  ghostTxt: { fontSize: 13, fontWeight: "800", color: colors.error },
  primaryBtn: { flex: 1, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 8, paddingVertical: 14, borderRadius: radius.md, backgroundColor: colors.brandPrimary },
  primaryTxt: { color: colors.onBrandPrimary, fontWeight: "800", fontSize: 14 },
});
