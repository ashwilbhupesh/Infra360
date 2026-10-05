import React, { useCallback, useState } from "react";
import { View, Text, StyleSheet, Pressable, ScrollView, ActivityIndicator, Alert } from "react-native";
import { Image } from "expo-image";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useFocusEffect, useRouter, Stack } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";
import { useAuth } from "@/src/auth-context";
import { useMaterialsCart } from "@/src/stores/materials-cart";
import { indianComma } from "@/src/utils/format";

type Scan = {
  id: string; user_id?: string; source?: string;
  image_url?: string; transcript?: string; translation?: string;
  created_at: string; items_count: number; unmatched_count: number;
  total_estimated: number;
};

export default function ParchaHistory() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { user } = useAuth();
  const addToCart = useMaterialsCart(s => s.add);
  const [list, setList] = useState<Scan[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const uid = user?.id;
      const url = uid ? `/materials/parcha-scans?user_id=${encodeURIComponent(uid)}&limit=50` : `/materials/parcha-scans?limit=50`;
      const data = await api.get<Scan[]>(url);
      setList(data);
    } finally { setLoading(false); }
  }, [user?.id]);
  useFocusEffect(useCallback(() => { load(); }, [load]));

  const reorder = async (sid: string) => {
    setBusy(sid);
    try {
      const full = await api.get<any>(`/materials/parcha-scans/${sid}`);
      const items = full.items || [];
      if (!items.length) { Alert.alert("Empty", "This scan had no matched items."); return; }
      for (const l of items) {
        addToCart({
          id: l.product_id, store_id: l.store_id, store_name: l.store_name || "",
          name: l.name, brand: l.brand, image: l.image, unit: l.unit, price: l.price,
        }, l.qty);
      }
      Alert.alert("Added to cart ✅", `${items.length} item${items.length === 1 ? "" : "s"} re-ordered.`, [
        { text: "View cart", onPress: () => router.push("/materials/cart" as any) },
        { text: "OK" },
      ]);
    } catch (e: any) {
      Alert.alert("Could not reorder", e?.message || "Try again");
    } finally { setBusy(null); }
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <Stack.Screen options={{ headerShown: false }} />
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="history-back" onPress={() => router.back()} hitSlop={12}>
          <Icon name="chevron-back" size={26} color={colors.onSurface} />
        </Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.title}>Parcha history</Text>
          <Text style={styles.sub}>{list.length} scan{list.length === 1 ? "" : "s"} · re-order in one tap</Text>
        </View>
      </View>

      <ScrollView contentContainerStyle={{ padding: spacing.lg, gap: spacing.md, paddingBottom: 60 }}>
        {loading ? (
          <ActivityIndicator color={colors.brand} style={{ marginTop: spacing.xxl }} />
        ) : list.length === 0 ? (
          <View style={styles.empty}>
            <Icon name="scan-outline" size={44} color={colors.muted} />
            <Text style={styles.emptyTitle}>No scans yet</Text>
            <Text style={styles.emptySub}>Scan or narrate your first material list to see it here.</Text>
            <Pressable testID="go-scan" onPress={() => router.replace("/market/scan-parcha" as any)} style={styles.goBtn}>
              <Icon name="scan" size={14} color={colors.onBrandPrimary} />
              <Text style={styles.goTxt}>Scan a parcha</Text>
            </Pressable>
          </View>
        ) : list.map(s => (
          <View key={s.id} style={styles.card} testID={`history-row-${s.id}`}>
            {s.image_url ? (
              <Image source={{ uri: s.image_url.startsWith("http") ? s.image_url : s.image_url }} style={styles.thumb} contentFit="cover" />
            ) : (
              <View style={[styles.thumb, { alignItems: "center", justifyContent: "center" }]}>
                <Icon name={s.source === "voice" ? "mic" : "document-text"} size={24} color={colors.brand} />
              </View>
            )}
            <View style={{ flex: 1 }}>
              <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
                <View style={[styles.pill, { backgroundColor: s.source === "voice" ? "#FFF4E6" : "#E7F3EC", borderColor: s.source === "voice" ? "#F0C080" : "#A5CFB2" }]}>
                  <Icon name={s.source === "voice" ? "mic" : "camera"} size={10} color={s.source === "voice" ? "#B06000" : colors.success} />
                  <Text style={[styles.pillTxt, { color: s.source === "voice" ? "#B06000" : colors.success }]}>{s.source === "voice" ? "Voice" : "Camera"}</Text>
                </View>
                <Text style={styles.date}>{new Date(s.created_at).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })}</Text>
              </View>
              {s.translation ? <Text style={styles.quote} numberOfLines={2}>“{s.translation}”</Text> : null}
              <View style={styles.statsRow}>
                <Text style={styles.stat}>{s.items_count} matched</Text>
                {s.unmatched_count > 0 && <Text style={[styles.stat, { color: colors.error }]}>{s.unmatched_count} missed</Text>}
                <Text style={styles.total}>₹{indianComma(s.total_estimated || 0)}</Text>
              </View>
              <Pressable
                testID={`history-reorder-${s.id}`}
                onPress={() => reorder(s.id)}
                disabled={busy === s.id || s.items_count === 0}
                style={[styles.reorderBtn, (busy === s.id || s.items_count === 0) && { opacity: 0.4 }]}
              >
                {busy === s.id
                  ? <ActivityIndicator color={colors.onBrandPrimary} size="small" />
                  : <><Icon name="refresh" size={14} color={colors.onBrandPrimary} />
                      <Text style={styles.reorderTxt}>Re-order to cart</Text></>}
              </Pressable>
            </View>
          </View>
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingHorizontal: spacing.lg, paddingBottom: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  title: { fontSize: 20, fontWeight: "800", color: colors.onSurface },
  sub: { fontSize: 11, color: colors.muted, marginTop: 2 },
  empty: { padding: spacing.xxl, alignItems: "center", gap: 8 },
  emptyTitle: { fontSize: 15, fontWeight: "800", color: colors.onSurface, marginTop: spacing.md },
  emptySub: { fontSize: 12, color: colors.muted, textAlign: "center", lineHeight: 17 },
  goBtn: { flexDirection: "row", alignItems: "center", gap: 6, paddingVertical: 10, paddingHorizontal: 16, borderRadius: radius.pill, backgroundColor: colors.brandPrimary, marginTop: spacing.md },
  goTxt: { color: colors.onBrandPrimary, fontWeight: "700", fontSize: 13 },
  card: { flexDirection: "row", gap: 10, padding: spacing.md, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, ...shadow.card },
  thumb: { width: 60, height: 60, borderRadius: 8, backgroundColor: colors.surfaceSecondary },
  pill: { flexDirection: "row", alignItems: "center", gap: 3, paddingHorizontal: 6, paddingVertical: 2, borderRadius: radius.pill, borderWidth: 1 },
  pillTxt: { fontSize: 9, fontWeight: "800", letterSpacing: 0.4 },
  date: { fontSize: 11, color: colors.muted, fontWeight: "600" },
  quote: { fontSize: 12, color: colors.onSurface, marginTop: 4, lineHeight: 16, fontStyle: "italic" },
  statsRow: { flexDirection: "row", alignItems: "center", gap: 10, marginTop: 6 },
  stat: { fontSize: 11, fontWeight: "700", color: colors.muted },
  total: { marginLeft: "auto", fontSize: 13, fontWeight: "800", color: colors.brandPrimary },
  reorderBtn: { flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 6, paddingVertical: 8, borderRadius: radius.md, backgroundColor: colors.brand, marginTop: 8 },
  reorderTxt: { fontSize: 12, fontWeight: "800", color: colors.onBrand },
});
