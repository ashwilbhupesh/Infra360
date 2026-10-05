import React, { useEffect, useMemo, useState } from "react";
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, Pressable } from "react-native";
import { Image } from "expo-image";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useLocalSearchParams, useRouter, Stack } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius } from "@/src/theme";
import { api } from "@/src/api";
import { formatINR, indianComma } from "@/src/utils/format";

type CompareProp = {
  id: string; title: string; type: string; listing_type?: string;
  price: number; area: number; area_unit: string;
  price_per_unit: number; bedrooms?: number | null; facing?: string; road_width_ft?: number;
  address: string; verified: boolean; source: string; listed_at?: string;
  images: string[]; locality_name: string;
  infravalue?: { low: number; high: number; confidence: string };
  govt_value?: number;
  lifestyle?: { overall?: number; walkability?: number; schools?: number; hospitals?: number; safety?: number; connectivity?: number };
  yoy_change_pct?: number;
};

const COL_WIDTH = 180;

type Row = {
  key: string;
  label: string;
  group: "price" | "property" | "location" | "listing";
  render: (p: CompareProp) => React.ReactNode;
  highlightBest?: "high" | "low"; // mark best col
  valueFor?: (p: CompareProp) => number | null; // for highlighting
};

const INR = (n?: number | null) => (typeof n === "number" ? `₹${indianComma(Math.round(n))}` : "—");

const ALL_ROWS: Row[] = [
  // Price
  { key: "price", label: "Price", group: "price", render: (p) => <Text style={{ fontSize: 16, color: colors.onSurface, fontWeight: "800" }}>{formatINR(p.price)}</Text>, highlightBest: "low", valueFor: (p) => p.price },
  { key: "ppu", label: "Price / unit", group: "price", render: (p) => <Text style={styles.val}>{`₹${indianComma(p.price_per_unit)}/${p.area_unit.split(" ")[0]}`}</Text>, highlightBest: "low", valueFor: (p) => p.price_per_unit },
  { key: "govt", label: "Govt DLC value", group: "price", render: (p) => <Text style={styles.val}>{INR(p.govt_value)}</Text> },
  // Property
  { key: "type", label: "Type", group: "property", render: (p) => <Text style={styles.val}>{p.type}</Text> },
  { key: "listing_type", label: "Listing kind", group: "property", render: (p) => <Text style={styles.val}>{p.listing_type || "Buy"}</Text> },
  { key: "area", label: "Area", group: "property", render: (p) => <Text style={styles.val}>{p.area} {p.area_unit}</Text>, highlightBest: "high", valueFor: (p) => p.area },
  { key: "bhk", label: "Bedrooms", group: "property", render: (p) => <Text style={styles.val}>{p.bedrooms ? `${p.bedrooms} BHK` : "—"}</Text> },
  { key: "facing", label: "Facing", group: "property", render: (p) => <Text style={styles.val}>{p.facing || "—"}</Text> },
  { key: "road", label: "Road width", group: "property", render: (p) => <Text style={styles.val}>{p.road_width_ft ? `${p.road_width_ft} ft` : "—"}</Text>, highlightBest: "high", valueFor: (p) => p.road_width_ft ?? null },
  // Location
  { key: "locality", label: "Locality", group: "location", render: (p) => <Text style={styles.val}>{p.locality_name}</Text> },
  { key: "lifestyle_overall", label: "Lifestyle (overall)", group: "location", render: (p) => <Text style={styles.val}>{p.lifestyle?.overall ? p.lifestyle.overall.toFixed(1) : "—"}</Text>, highlightBest: "high", valueFor: (p) => p.lifestyle?.overall ?? null },
  { key: "walk", label: "Walkability", group: "location", render: (p) => <Text style={styles.val}>{p.lifestyle?.walkability ? p.lifestyle.walkability.toFixed(1) : "—"}</Text>, highlightBest: "high", valueFor: (p) => p.lifestyle?.walkability ?? null },
  { key: "schools", label: "Schools score", group: "location", render: (p) => <Text style={styles.val}>{p.lifestyle?.schools ? p.lifestyle.schools.toFixed(1) : "—"}</Text>, highlightBest: "high", valueFor: (p) => p.lifestyle?.schools ?? null },
  { key: "hospitals", label: "Hospitals score", group: "location", render: (p) => <Text style={styles.val}>{p.lifestyle?.hospitals ? p.lifestyle.hospitals.toFixed(1) : "—"}</Text>, highlightBest: "high", valueFor: (p) => p.lifestyle?.hospitals ?? null },
  { key: "safety", label: "Safety score", group: "location", render: (p) => <Text style={styles.val}>{p.lifestyle?.safety ? p.lifestyle.safety.toFixed(1) : "—"}</Text>, highlightBest: "high", valueFor: (p) => p.lifestyle?.safety ?? null },
  { key: "connectivity", label: "Connectivity", group: "location", render: (p) => <Text style={styles.val}>{p.lifestyle?.connectivity ? p.lifestyle.connectivity.toFixed(1) : "—"}</Text>, highlightBest: "high", valueFor: (p) => p.lifestyle?.connectivity ?? null },
  { key: "yoy", label: "Price trend (YoY)", group: "location", render: (p) => <Text style={[styles.val, { color: (p.yoy_change_pct ?? 0) >= 0 ? colors.success : colors.error }]}>{typeof p.yoy_change_pct === "number" ? `${p.yoy_change_pct > 0 ? "+" : ""}${p.yoy_change_pct.toFixed(1)}%` : "—"}</Text>, highlightBest: "high", valueFor: (p) => p.yoy_change_pct ?? null },
  // Listing
  { key: "verified", label: "Verified", group: "listing", render: (p) => p.verified ? <Icon name="shield-checkmark" size={18} color={colors.success} /> : <Text style={styles.val}>—</Text> },
  { key: "source", label: "Listed by", group: "listing", render: (p) => <Text style={styles.val}>{p.source}</Text> },
  { key: "listed_at", label: "Listed on", group: "listing", render: (p) => <Text style={styles.val}>{p.listed_at ? new Date(p.listed_at).toLocaleDateString("en-IN", { day: "2-digit", month: "short" }) : "—"}</Text> },
];

const GROUPS: { key: Row["group"]; label: string }[] = [
  { key: "price", label: "Price" },
  { key: "property", label: "Property" },
  { key: "location", label: "Location" },
  { key: "listing", label: "Listing" },
];

export default function Compare() {
  const { ids } = useLocalSearchParams<{ ids: string }>();
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [items, setItems] = useState<CompareProp[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeGroups, setActiveGroups] = useState<Set<Row["group"]>>(new Set(["price", "property", "location", "listing"]));
  const [onlyDifferences, setOnlyDifferences] = useState(false);

  useEffect(() => {
    (async () => {
      if (!ids) return;
      try {
        const data = await api.get<CompareProp[]>(`/compare?ids=${ids}`);
        setItems(data);
      } finally { setLoading(false); }
    })();
  }, [ids]);

  const rows = useMemo(() => {
    let r = ALL_ROWS.filter((row) => activeGroups.has(row.group));
    if (onlyDifferences) {
      r = r.filter((row) => {
        const values = items.map(row.render).map((n) => (typeof n === "string" ? n : JSON.stringify(n)));
        return new Set(values).size > 1;
      });
    }
    return r;
  }, [activeGroups, items, onlyDifferences]);

  const bestIdxFor = (row: Row): number | null => {
    if (!row.valueFor || !row.highlightBest) return null;
    const vals = items.map((p) => row.valueFor!(p));
    if (vals.some((v) => v === null || v === undefined)) return null;
    let bestIdx = 0;
    for (let i = 1; i < vals.length; i++) {
      const better = row.highlightBest === "low" ? (vals[i]! < vals[bestIdx]!) : (vals[i]! > vals[bestIdx]!);
      if (better) bestIdx = i;
    }
    return bestIdx;
  };

  const toggleGroup = (g: Row["group"]) => {
    const n = new Set(activeGroups);
    n.has(g) ? n.delete(g) : n.add(g);
    if (n.size === 0) n.add(g); // keep at least one on
    setActiveGroups(n);
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <Stack.Screen options={{ headerShown: false }} />
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="compare-back-btn" onPress={() => router.back()} hitSlop={12}>
          <Icon name="chevron-back" size={26} color={colors.onSurface} />
        </Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.title}>Compare</Text>
          <Text style={styles.sub}>{items.length} properties · {rows.length} criteria</Text>
        </View>
      </View>

      {/* Group filter chips */}
      <View style={{ paddingHorizontal: spacing.xl, paddingTop: spacing.sm, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border, paddingBottom: spacing.sm }}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 8 }}>
          {GROUPS.map((g) => {
            const active = activeGroups.has(g.key);
            return (
              <Pressable
                key={g.key}
                testID={`compare-group-${g.key}`}
                onPress={() => toggleGroup(g.key)}
                style={[styles.chip, active && styles.chipActive]}
              >
                <Text style={[styles.chipText, active && styles.chipTextActive]}>{g.label}</Text>
              </Pressable>
            );
          })}
          <Pressable
            testID="compare-only-diff"
            onPress={() => setOnlyDifferences((v) => !v)}
            style={[styles.chip, onlyDifferences && styles.chipActive]}
          >
            <Icon name="swap-vertical-outline" size={13} color={onlyDifferences ? colors.onBrand : colors.onSurface} />
            <Text style={[styles.chipText, onlyDifferences && styles.chipTextActive]}>Only differences</Text>
          </Pressable>
        </ScrollView>
      </View>

      {loading ? (
        <ActivityIndicator color={colors.brand} style={{ marginTop: spacing.xxl }} />
      ) : items.length === 0 ? (
        <Text style={styles.empty}>No properties to compare. Go back and select at least 2.</Text>
      ) : (
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <ScrollView showsVerticalScrollIndicator={false}>
            <View>
              {/* Property header row */}
              <View style={styles.row}>
                <View style={styles.labelCell}><Text style={styles.labelHead}>Property</Text></View>
                {items.map(p => (
                  <Pressable
                    key={p.id}
                    testID={`compare-col-${p.id}`}
                    onPress={() => router.push(`/property/${p.id}` as any)}
                    style={styles.cellCard}
                  >
                    <Image source={{ uri: p.images?.[0] }} style={styles.thumb} contentFit="cover" />
                    <Text style={styles.cardTitle} numberOfLines={2}>{p.title}</Text>
                    <Text style={styles.cardAddr} numberOfLines={1}>{p.address}</Text>
                  </Pressable>
                ))}
              </View>

              {rows.map((r, idx) => {
                const bestIdx = bestIdxFor(r);
                return (
                  <View key={r.key} style={[styles.row, idx % 2 === 1 && styles.rowAlt]}>
                    <View style={styles.labelCell}><Text style={styles.labelText}>{r.label}</Text></View>
                    {items.map((p, i) => (
                      <View key={p.id} style={[styles.valueCell, bestIdx === i && styles.bestCell]}>
                        {r.render(p)}
                        {bestIdx === i && (
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
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", gap: spacing.sm, paddingHorizontal: spacing.xl, paddingBottom: spacing.md, borderBottomWidth: 1, borderBottomColor: colors.border },
  title: { fontSize: 22, fontWeight: "800", color: colors.onSurface },
  sub: { fontSize: 12, color: colors.muted, marginTop: 2 },
  empty: { textAlign: "center", color: colors.muted, marginTop: spacing.xxl, fontSize: 13 },

  chip: { flexDirection: "row", alignItems: "center", gap: 4, paddingHorizontal: 12, height: 32, borderRadius: radius.pill, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border, flexShrink: 0 },
  chipActive: { backgroundColor: colors.brand, borderColor: colors.brand },
  chipText: { color: colors.onSurface, fontSize: 12, fontWeight: "600" },
  chipTextActive: { color: colors.onBrand },

  row: { flexDirection: "row", alignItems: "stretch" },
  rowAlt: { backgroundColor: colors.surfaceSecondary },
  labelCell: { width: 130, padding: spacing.md, justifyContent: "center", borderRightWidth: 1, borderRightColor: colors.border, backgroundColor: colors.surface },
  labelHead: { fontSize: 11, fontWeight: "800", color: colors.muted, letterSpacing: 0.8 },
  labelText: { fontSize: 12, color: colors.muted, fontWeight: "600" },
  valueCell: { width: COL_WIDTH, padding: spacing.md, justifyContent: "center", borderRightWidth: 1, borderRightColor: colors.border, position: "relative" },
  bestCell: { backgroundColor: "rgba(46, 109, 77, 0.08)" },
  bestPill: { position: "absolute", top: 6, right: 8, flexDirection: "row", alignItems: "center", gap: 2, backgroundColor: colors.success, paddingHorizontal: 6, paddingVertical: 2, borderRadius: radius.pill },
  bestText: { fontSize: 9, fontWeight: "800", color: colors.onSuccess, letterSpacing: 0.3 },

  cellCard: { width: COL_WIDTH, padding: spacing.md, borderRightWidth: 1, borderRightColor: colors.border },
  thumb: { width: "100%", height: 90, borderRadius: radius.sm, backgroundColor: colors.surfaceSecondary },
  cardTitle: { fontSize: 13, fontWeight: "700", color: colors.onSurface, marginTop: spacing.sm },
  cardAddr: { fontSize: 11, color: colors.muted, marginTop: 2 },
  val: { fontSize: 13, color: colors.onSurface, fontWeight: "600" },
});
