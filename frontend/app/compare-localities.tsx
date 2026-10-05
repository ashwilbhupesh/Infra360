import React, { useEffect, useMemo, useState } from "react";
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, Pressable, Modal } from "react-native";
import { Image } from "expo-image";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useLocalSearchParams, useRouter, Stack } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius } from "@/src/theme";
import { api } from "@/src/api";
import { indianComma } from "@/src/utils/format";

type Locality = {
  id: string; name: string; city: string; state: string; image?: string;
  median_price_per_sq_yd: number; govt_dlc_per_sq_yd: number;
  estimated_range_low: number; estimated_range_high: number;
  confidence: string; yoy_change_pct: number; listings_count: number;
  summary?: string;
  lifestyle?: { overall: number; walkability: number; schools: number; hospitals: number; connectivity: number; safety: number };
  properties_count: number; featured_count: number; infrastructure_count: number;
};

const COL_W = 180;

type Row = {
  key: string; label: string; group: string;
  render: (l: Locality) => React.ReactNode;
  valueFor?: (l: Locality) => number | null;
  best?: "high" | "low";
};

const INR = (n?: number | null) => (typeof n === "number" ? `₹${indianComma(Math.round(n))}` : "—");

const ROWS: Row[] = [
  { key: "median", label: "Median price (sq yd)", group: "price", render: (l) => <Text style={styles.val}>{INR(l.median_price_per_sq_yd)}</Text>, valueFor: l => l.median_price_per_sq_yd, best: "low" },
  { key: "govt", label: "Govt DLC rate", group: "price", render: (l) => <Text style={styles.val}>{INR(l.govt_dlc_per_sq_yd)}</Text> },
  { key: "range", label: "InfraValue range", group: "price", render: (l) => <Text style={styles.val}>{INR(l.estimated_range_low)}–{INR(l.estimated_range_high)}</Text> },
  { key: "yoy", label: "YoY appreciation", group: "price", render: (l) => <Text style={[styles.val, { color: l.yoy_change_pct >= 0 ? colors.success : colors.error }]}>{l.yoy_change_pct > 0 ? "+" : ""}{l.yoy_change_pct.toFixed(1)}%</Text>, valueFor: l => l.yoy_change_pct, best: "high" },
  { key: "conf", label: "Data confidence", group: "price", render: (l) => <Text style={styles.val}>{l.confidence}</Text> },

  { key: "overall", label: "Lifestyle (overall)", group: "lifestyle", render: (l) => <Text style={styles.val}>{l.lifestyle?.overall ?? "—"}/100</Text>, valueFor: l => l.lifestyle?.overall ?? null, best: "high" },
  { key: "walk", label: "Walkability", group: "lifestyle", render: (l) => <Text style={styles.val}>{l.lifestyle?.walkability ?? "—"}</Text>, valueFor: l => l.lifestyle?.walkability ?? null, best: "high" },
  { key: "schools", label: "Schools", group: "lifestyle", render: (l) => <Text style={styles.val}>{l.lifestyle?.schools ?? "—"}</Text>, valueFor: l => l.lifestyle?.schools ?? null, best: "high" },
  { key: "hosp", label: "Hospitals", group: "lifestyle", render: (l) => <Text style={styles.val}>{l.lifestyle?.hospitals ?? "—"}</Text>, valueFor: l => l.lifestyle?.hospitals ?? null, best: "high" },
  { key: "conn", label: "Connectivity", group: "lifestyle", render: (l) => <Text style={styles.val}>{l.lifestyle?.connectivity ?? "—"}</Text>, valueFor: l => l.lifestyle?.connectivity ?? null, best: "high" },
  { key: "safe", label: "Safety", group: "lifestyle", render: (l) => <Text style={styles.val}>{l.lifestyle?.safety ?? "—"}</Text>, valueFor: l => l.lifestyle?.safety ?? null, best: "high" },

  { key: "listings", label: "Live listings", group: "activity", render: (l) => <Text style={styles.val}>{l.properties_count}</Text>, valueFor: l => l.properties_count, best: "high" },
  { key: "feat", label: "Featured listings", group: "activity", render: (l) => <Text style={styles.val}>{l.featured_count}</Text>, valueFor: l => l.featured_count, best: "high" },
  { key: "infra", label: "Infra projects", group: "activity", render: (l) => <Text style={styles.val}>{l.infrastructure_count}</Text>, valueFor: l => l.infrastructure_count, best: "high" },
];

export default function CompareLocalities() {
  const { ids } = useLocalSearchParams<{ ids: string }>();
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [items, setItems] = useState<Locality[]>([]);
  const [loading, setLoading] = useState(true);
  const [picking, setPicking] = useState(false);
  const [allLocs, setAllLocs] = useState<Locality[]>([]);

  useEffect(() => {
    (async () => {
      try {
        const [list, all] = await Promise.all([
          ids ? api.get<Locality[]>(`/compare/localities?ids=${ids}`) : Promise.resolve([]),
          api.get<Locality[]>("/localities"),
        ]);
        setItems(list);
        setAllLocs(all);
      } finally { setLoading(false); }
    })();
  }, [ids]);

  const addLocality = async (id: string) => {
    if (items.find(i => i.id === id)) { setPicking(false); return; }
    const next = [...items.map(x => x.id), id].slice(0, 4);
    const data = await api.get<Locality[]>(`/compare/localities?ids=${next.join(",")}`);
    setItems(data);
    setPicking(false);
  };

  const bestIdx = (r: Row): number | null => {
    if (!r.valueFor || !r.best) return null;
    const vals = items.map(r.valueFor);
    if (vals.some(v => v === null || v === undefined)) return null;
    let bi = 0;
    for (let i = 1; i < vals.length; i++) {
      const better = r.best === "low" ? (vals[i]! < vals[bi]!) : (vals[i]! > vals[bi]!);
      if (better) bi = i;
    }
    return bi;
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <Stack.Screen options={{ headerShown: false }} />
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="loc-compare-back" onPress={() => router.back()} hitSlop={12}><Icon name="chevron-back" size={26} color={colors.onSurface} /></Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.title}>Compare localities</Text>
          <Text style={styles.sub}>{items.length} localities · {ROWS.length} criteria</Text>
        </View>
        <Pressable testID="loc-compare-add" onPress={() => setPicking(true)} style={styles.addBtn} hitSlop={10}>
          <Icon name="add" size={16} color={colors.onBrandPrimary} />
        </Pressable>
      </View>

      {loading ? <ActivityIndicator color={colors.brand} style={{ marginTop: spacing.xxl }} /> : items.length === 0 ? (
        <View style={{ padding: spacing.xxl, alignItems: "center" }}>
          <Icon name="location-outline" size={40} color={colors.muted} />
          <Text style={{ color: colors.muted, marginTop: spacing.md }}>Pick at least two localities to compare.</Text>
          <Pressable testID="loc-compare-pick-first" onPress={() => setPicking(true)} style={[styles.addBtn, { marginTop: 10, width: "auto", paddingHorizontal: 14 }]}>
            <Text style={{ color: colors.onBrandPrimary, fontWeight: "700" }}>Pick localities</Text>
          </Pressable>
        </View>
      ) : (
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <ScrollView showsVerticalScrollIndicator={false}>
            <View>
              <View style={styles.row}>
                <View style={styles.labelCell}><Text style={styles.labelHead}>Locality</Text></View>
                {items.map(l => (
                  <Pressable key={l.id} testID={`loc-col-${l.id}`} onPress={() => router.push(`/locality/${l.id}` as any)} style={styles.cellCard}>
                    <Image source={{ uri: l.image }} style={styles.thumb} contentFit="cover" />
                    <Text style={styles.cardTitle}>{l.name}</Text>
                    <Text style={styles.cardMeta}>{l.city} · {l.listings_count || l.properties_count} listings</Text>
                  </Pressable>
                ))}
              </View>
              {ROWS.map((r, idx) => {
                const bi = bestIdx(r);
                return (
                  <View key={r.key} style={[styles.row, idx % 2 === 1 && styles.rowAlt]}>
                    <View style={styles.labelCell}><Text style={styles.labelText}>{r.label}</Text></View>
                    {items.map((l, i) => (
                      <View key={l.id} style={[styles.valueCell, bi === i && styles.bestCell]}>
                        {r.render(l)}
                        {bi === i && (
                          <View style={styles.bestPill}>
                            <Icon name="trophy" size={9} color={colors.onSuccess} />
                            <Text style={styles.bestText}>Best</Text>
                          </View>
                        )}
                      </View>
                    ))}
                  </View>
                );
              })}
            </View>
          </ScrollView>
        </ScrollView>
      )}

      <Modal visible={picking} transparent animationType="slide" onRequestClose={() => setPicking(false)}>
        <Pressable style={styles.sheetBackdrop} onPress={() => setPicking(false)}>
          <Pressable style={styles.sheet} onPress={() => {}}>
            <View style={styles.sheetHandle} />
            <Text style={styles.sheetTitle}>Add locality to compare</Text>
            <ScrollView style={{ maxHeight: 420 }}>
              {allLocs.map(l => {
                const already = items.find(i => i.id === l.id);
                return (
                  <Pressable
                    key={l.id}
                    testID={`loc-pick-${l.id}`}
                    disabled={!!already || items.length >= 4}
                    onPress={() => addLocality(l.id)}
                    style={[styles.pickRow, already && { opacity: 0.4 }]}
                  >
                    <Image source={{ uri: l.image }} style={styles.pickThumb} contentFit="cover" />
                    <View style={{ flex: 1 }}>
                      <Text style={styles.pickTitle}>{l.name}</Text>
                      <Text style={styles.pickMeta}>{INR(l.median_price_per_sq_yd)}/sq yd · {l.yoy_change_pct > 0 ? "+" : ""}{l.yoy_change_pct}%</Text>
                    </View>
                    {already ? <Icon name="checkmark-circle" size={18} color={colors.success} /> : <Icon name="add-circle-outline" size={20} color={colors.brand} />}
                  </Pressable>
                );
              })}
            </ScrollView>
          </Pressable>
        </Pressable>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingHorizontal: spacing.lg, paddingBottom: spacing.md, borderBottomWidth: 1, borderBottomColor: colors.border },
  title: { fontSize: 20, fontWeight: "800", color: colors.onSurface },
  sub: { fontSize: 11, color: colors.muted, marginTop: 2 },
  addBtn: { width: 36, height: 36, borderRadius: 18, backgroundColor: colors.brandPrimary, alignItems: "center", justifyContent: "center" },

  row: { flexDirection: "row", alignItems: "stretch" },
  rowAlt: { backgroundColor: colors.surfaceSecondary },
  labelCell: { width: 130, padding: spacing.md, justifyContent: "center", borderRightWidth: 1, borderRightColor: colors.border, backgroundColor: colors.surface },
  labelHead: { fontSize: 11, fontWeight: "800", color: colors.muted, letterSpacing: 0.8 },
  labelText: { fontSize: 12, color: colors.muted, fontWeight: "600" },
  valueCell: { width: COL_W, padding: spacing.md, justifyContent: "center", borderRightWidth: 1, borderRightColor: colors.border, position: "relative" },
  bestCell: { backgroundColor: "rgba(46, 109, 77, 0.1)" },
  bestPill: { position: "absolute", top: 6, right: 8, flexDirection: "row", alignItems: "center", gap: 2, backgroundColor: colors.success, paddingHorizontal: 6, paddingVertical: 2, borderRadius: radius.pill },
  bestText: { fontSize: 9, fontWeight: "800", color: colors.onSuccess, letterSpacing: 0.3 },
  cellCard: { width: COL_W, padding: spacing.md, borderRightWidth: 1, borderRightColor: colors.border },
  thumb: { width: "100%", height: 90, borderRadius: radius.sm, backgroundColor: colors.surfaceSecondary },
  cardTitle: { fontSize: 13, fontWeight: "800", color: colors.onSurface, marginTop: spacing.sm },
  cardMeta: { fontSize: 11, color: colors.muted, marginTop: 2 },
  val: { fontSize: 13, color: colors.onSurface, fontWeight: "600" },

  sheetBackdrop: { flex: 1, backgroundColor: "rgba(0,0,0,0.4)", justifyContent: "flex-end" },
  sheet: { backgroundColor: colors.surface, borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: spacing.lg, paddingBottom: spacing.xxl },
  sheetHandle: { alignSelf: "center", width: 40, height: 4, borderRadius: 2, backgroundColor: colors.borderStrong, marginBottom: spacing.md },
  sheetTitle: { fontSize: 16, fontWeight: "800", color: colors.onSurface, marginBottom: spacing.md },
  pickRow: { flexDirection: "row", alignItems: "center", gap: 10, padding: 10, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, marginBottom: 8 },
  pickThumb: { width: 48, height: 48, borderRadius: 8, backgroundColor: colors.surfaceSecondary },
  pickTitle: { fontSize: 14, fontWeight: "700", color: colors.onSurface },
  pickMeta: { fontSize: 11, color: colors.muted, marginTop: 2 },
});
