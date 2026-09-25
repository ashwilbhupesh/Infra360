import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, Pressable, ScrollView, ActivityIndicator, TextInput } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useLocalSearchParams } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";
import { PropertyCard, Property } from "@/src/components/property-card";
import { formatINR } from "@/src/utils/format";

const FILTERS = [
  { key: "", label: "All" },
  { key: "Apartment", label: "Apartments" },
  { key: "Villa", label: "Villas" },
  { key: "Residential Plot", label: "Plots" },
  { key: "Agricultural Land", label: "Agri Land" },
  { key: "Commercial", label: "Commercial" },
];

// Web fallback: schematic map with clustered price pins over a static canvas
export default function MapScreenWeb() {
  const insets = useSafeAreaInsets();
  const params = useLocalSearchParams<{ type?: string; q?: string }>();
  const [items, setItems] = useState<Property[]>([]);
  const [filter, setFilter] = useState(params.type || "");
  const [q, setQ] = useState(params.q ? String(params.q) : "");
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<string | null>(null);

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
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chipsRow}>
          {FILTERS.map(f => {
            const active = filter === f.key;
            return (
              <Pressable key={f.key || "all"} testID={`filter-${f.key || "all"}`} onPress={() => setFilter(f.key)} style={[styles.filterChip, active && styles.filterChipActive]}>
                <Text style={[styles.filterText, active && styles.filterTextActive]}>{f.label}</Text>
              </Pressable>
            );
          })}
        </ScrollView>
      </View>

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
  mapArea: { margin: spacing.lg, height: 260, borderRadius: radius.lg, backgroundColor: colors.brandTertiary, padding: spacing.lg, justifyContent: "space-between" },
  mapNote: { fontSize: 12, color: colors.brand, fontWeight: "600" },
  pinsCloud: { flexDirection: "row", flexWrap: "wrap", gap: 6 },
  pin: { paddingHorizontal: 10, paddingVertical: 5, backgroundColor: colors.surface, borderRadius: radius.pill, borderWidth: 1.5, borderColor: colors.brand },
  pinActive: { backgroundColor: colors.brandPrimary, borderColor: colors.brandPrimary },
  pinText: { color: colors.brand, fontSize: 11, fontWeight: "700" },
  pinTextActive: { color: colors.onBrandPrimary },
  sheet: { flex: 1, backgroundColor: colors.surface, borderTopLeftRadius: 20, borderTopRightRadius: 20, borderWidth: 1, borderColor: colors.border, paddingTop: spacing.md },
  sheetTitle: { fontSize: 16, fontWeight: "700", color: colors.onSurface, paddingHorizontal: spacing.lg },
});
