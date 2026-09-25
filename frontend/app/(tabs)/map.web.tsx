import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, Pressable, ScrollView, ActivityIndicator, TextInput } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useLocalSearchParams, useRouter } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";
import { PropertyCard, Property } from "@/src/components/property-card";
import { formatINR, indianComma } from "@/src/utils/format";
import { heatColor, heatLabel } from "@/src/utils/heat";

const FILTERS = [
  { key: "", label: "All" },
  { key: "Apartment", label: "Apartments" },
  { key: "Villa", label: "Villas" },
  { key: "Residential Plot", label: "Plots" },
  { key: "Agricultural Land", label: "Agri Land" },
  { key: "Commercial", label: "Commercial" },
];

type HeatPoint = { id: string; name: string; lat: number; lng: number; median_price_per_sq_yd: number; govt_dlc_per_sq_yd: number; intensity: number };

export default function MapScreenWeb() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const params = useLocalSearchParams<{ type?: string; q?: string }>();
  const [items, setItems] = useState<Property[]>([]);
  const [filter, setFilter] = useState(params.type || "");
  const [q, setQ] = useState(params.q ? String(params.q) : "");
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<string | null>(null);
  const [heat, setHeat] = useState(false);
  const [heatPoints, setHeatPoints] = useState<HeatPoint[]>([]);

  const load = async () => {
    setLoading(true);
    try {
      const qs = new URLSearchParams();
      if (filter) qs.set("type", filter);
      if (q) qs.set("q", q);
      const data = await api.get<Property[]>(`/properties?${qs.toString()}`);
      setItems(data);
    } finally { setLoading(false); }
  };
  useEffect(() => { load(); }, [filter]);

  useEffect(() => {
    (async () => {
      try {
        const h = await api.get<{ points: HeatPoint[] }>("/heatmap");
        setHeatPoints(h.points || []);
      } catch {}
    })();
  }, []);

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface, paddingTop: insets.top + spacing.sm }}>
      <View style={{ paddingHorizontal: spacing.lg, gap: spacing.sm }}>
        <View style={styles.searchPill}>
          <Icon name="search-outline" size={16} color={colors.muted} />
          <TextInput
            testID="map-search-input"
            style={styles.searchTxt}
            placeholder="Search locality, project, road..."
            placeholderTextColor={colors.muted}
            value={q}
            onChangeText={setQ}
            onSubmitEditing={load}
            returnKeyType="search"
          />
        </View>
        <View style={{ flexDirection: "row", alignItems: "center", gap: spacing.sm }}>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chipsRow} style={{ flex: 1 }}>
            {FILTERS.map(f => {
              const active = filter === f.key;
              return (
                <Pressable key={f.key || "all"} testID={`filter-${f.key || "all"}`} onPress={() => setFilter(f.key)} style={[styles.filterChip, active && styles.filterChipActive]}>
                  <Text style={[styles.filterText, active && styles.filterTextActive]}>{f.label}</Text>
                </Pressable>
              );
            })}
          </ScrollView>
          <Pressable testID="heatmap-toggle" onPress={() => setHeat(v => !v)} style={[styles.heatToggle, heat && styles.heatToggleActive]}>
            <Icon name="flame-outline" size={14} color={heat ? colors.onBrandPrimary : colors.onSurface} />
            <Text style={[styles.heatToggleText, heat && { color: colors.onBrandPrimary }]}>Heat</Text>
          </Pressable>
        </View>
      </View>

      {heat ? (
        <View style={styles.heatArea}>
          <Text style={styles.heatKicker}>PRICE HEATMAP · MEDIAN ₹ / SQ YD</Text>
          <View style={styles.heatGrid}>
            {heatPoints.map(pt => (
              <Pressable
                key={pt.id}
                testID={`heat-cell-${pt.id}`}
                onPress={() => router.push(`/locality/${pt.id}` as any)}
                style={[styles.heatCell, { backgroundColor: heatColor(pt.intensity, 0.85) }]}
              >
                <Text style={styles.heatCellName} numberOfLines={1}>{pt.name}</Text>
                <Text style={styles.heatCellPrice}>₹{indianComma(pt.median_price_per_sq_yd)}</Text>
                <Text style={styles.heatCellTag}>{heatLabel(pt.intensity)}</Text>
              </Pressable>
            ))}
          </View>
          <View style={styles.legend}>
            <Text style={styles.legendText}>Value</Text>
            <View style={styles.legendBar}>
              {[0, 0.25, 0.5, 0.75, 1].map(i => (
                <View key={i} style={{ flex: 1, height: 8, backgroundColor: heatColor(i, 1) }} />
              ))}
            </View>
            <Text style={styles.legendText}>Prime</Text>
          </View>
        </View>
      ) : (
        <View style={styles.mapArea}>
          <Text style={styles.mapNote}>Interactive map available on device. Web preview shows list.</Text>
          <View style={styles.pinsCloud}>
            {items.slice(0, 12).map(p => (
              <Pressable key={p.id} onPress={() => setSelected(p.id)} style={[styles.pin, selected === p.id && styles.pinActive]}>
                <Text style={[styles.pinText, selected === p.id && styles.pinTextActive]}>{formatINR(p.price)}</Text>
              </Pressable>
            ))}
          </View>
        </View>
      )}

      <View style={styles.sheet}>
        <Text style={styles.sheetTitle}>{loading ? "Loading..." : `${items.length} properties`}</Text>
        <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingBottom: 120 }}>
          {items.map(p => <PropertyCard key={p.id} property={p} compact />)}
        </ScrollView>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  searchPill: { flexDirection: "row", alignItems: "center", gap: spacing.sm, height: 44, paddingHorizontal: spacing.lg, borderRadius: radius.pill, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border },
  searchTxt: { flex: 1, color: colors.onSurface, fontSize: 14 },
  chipsRow: { gap: spacing.sm, paddingRight: spacing.md, paddingVertical: 2 },
  filterChip: { paddingHorizontal: spacing.md, height: 36, justifyContent: "center", borderRadius: radius.pill, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border, flexShrink: 0 },
  filterChipActive: { backgroundColor: colors.brand, borderColor: colors.brand },
  filterText: { color: colors.onSurface, fontSize: 12, fontWeight: "600" },
  filterTextActive: { color: colors.onBrand },
  heatToggle: { flexDirection: "row", alignItems: "center", gap: 4, paddingHorizontal: 10, height: 36, borderRadius: radius.pill, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, flexShrink: 0 },
  heatToggleActive: { backgroundColor: colors.brandPrimary, borderColor: colors.brandPrimary },
  heatToggleText: { color: colors.onSurface, fontSize: 12, fontWeight: "700" },
  mapArea: { margin: spacing.lg, height: 260, borderRadius: radius.lg, backgroundColor: colors.brandTertiary, padding: spacing.lg, justifyContent: "space-between" },
  mapNote: { fontSize: 12, color: colors.brand, fontWeight: "600" },
  pinsCloud: { flexDirection: "row", flexWrap: "wrap", gap: 6 },
  pin: { paddingHorizontal: 10, paddingVertical: 5, backgroundColor: colors.surface, borderRadius: radius.pill, borderWidth: 1.5, borderColor: colors.brand },
  pinActive: { backgroundColor: colors.brandPrimary, borderColor: colors.brandPrimary },
  pinText: { color: colors.brand, fontSize: 11, fontWeight: "700" },
  pinTextActive: { color: colors.onBrandPrimary },
  heatArea: { margin: spacing.lg, borderRadius: radius.lg, backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, padding: spacing.md },
  heatKicker: { fontSize: 10, fontWeight: "800", color: colors.muted, letterSpacing: 1, marginBottom: spacing.sm },
  heatGrid: { flexDirection: "row", flexWrap: "wrap", gap: 6 },
  heatCell: { flexBasis: "31%", flexGrow: 1, borderRadius: radius.md, padding: spacing.sm, minHeight: 80 },
  heatCellName: { fontSize: 12, fontWeight: "800", color: "#FFFFFF", textShadowColor: "rgba(0,0,0,0.35)", textShadowOffset: { width: 0, height: 1 }, textShadowRadius: 2 },
  heatCellPrice: { fontSize: 14, fontWeight: "800", color: "#FFFFFF", marginTop: 4 },
  heatCellTag: { fontSize: 9, fontWeight: "700", color: "#FFFFFF", marginTop: 4, letterSpacing: 0.6 },
  legend: { flexDirection: "row", alignItems: "center", gap: 8, marginTop: spacing.md },
  legendBar: { flex: 1, flexDirection: "row", height: 8, borderRadius: 4, overflow: "hidden" },
  legendText: { fontSize: 10, fontWeight: "700", color: colors.muted, letterSpacing: 0.5 },
  sheet: { flex: 1, backgroundColor: colors.surface, borderTopLeftRadius: 20, borderTopRightRadius: 20, borderWidth: 1, borderColor: colors.border, paddingTop: spacing.md },
  sheetTitle: { fontSize: 16, fontWeight: "700", color: colors.onSurface, paddingHorizontal: spacing.lg },
});
