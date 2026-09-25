import React, { useEffect, useMemo, useRef, useState } from "react";
import { View, Text, StyleSheet, Pressable, ScrollView, ActivityIndicator, Dimensions } from "react-native";
import MapView, { Marker, Circle, PROVIDER_DEFAULT } from "react-native-maps";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useLocalSearchParams } from "expo-router";
import BottomSheet from "@gorhom/bottom-sheet";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";
import { PropertyCard, Property } from "@/src/components/property-card";
import { formatINR } from "@/src/utils/format";
import { heatColor, heatLabel } from "@/src/utils/heat";

const FILTERS = [
  { key: "", label: "All" },
  { key: "Apartment", label: "Apartments" },
  { key: "Villa", label: "Villas" },
  { key: "Residential Plot", label: "Plots" },
  { key: "Agricultural Land", label: "Agri Land" },
  { key: "Commercial", label: "Commercial" },
];

export default function MapScreen() {
  const insets = useSafeAreaInsets();
  const params = useLocalSearchParams<{ type?: string; q?: string }>();
  const [items, setItems] = useState<Property[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>(params.type || "");
  const [loading, setLoading] = useState(true);
  const [heat, setHeat] = useState(false);
  const [heatPoints, setHeatPoints] = useState<Array<{ id: string; name: string; lat: number; lng: number; intensity: number; median_price_per_sq_yd: number }>>([]);
  const sheetRef = useRef<BottomSheet>(null);

  useEffect(() => {
    (async () => {
      try {
        const h = await api.get<{ points: any[] }>("/heatmap");
        setHeatPoints(h.points || []);
      } catch {}
    })();
  }, []);

  const load = async () => {
    setLoading(true);
    try {
      const qs = new URLSearchParams();
      if (filter) qs.set("type", filter);
      if (params.q) qs.set("q", String(params.q));
      const data = await api.get<Property[]>(`/properties?${qs.toString()}`);
      setItems(data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, [filter, params.q]);

  const initialRegion = { latitude: 26.8891, longitude: 75.7500, latitudeDelta: 0.18, longitudeDelta: 0.18 };
  const focused = useMemo(() => selected ? items.find(i => i.id === selected) : null, [items, selected]);

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <MapView
        style={StyleSheet.absoluteFill}
        provider={PROVIDER_DEFAULT}
        initialRegion={initialRegion}
        showsCompass={false}
      >
        {heat && heatPoints.map(pt => (
          <Circle
            key={`hc-${pt.id}`}
            center={{ latitude: pt.lat, longitude: pt.lng }}
            radius={1500}
            fillColor={heatColor(pt.intensity, 0.45)}
            strokeColor={heatColor(pt.intensity, 0.9)}
            strokeWidth={1}
          />
        ))}
        {!heat && items.map((p: any) => (
          <Marker
            key={p.id}
            coordinate={{ latitude: p.lat, longitude: p.lng }}
            onPress={() => { setSelected(p.id); sheetRef.current?.snapToIndex(1); }}
            anchor={{ x: 0.5, y: 0.5 }}
          >
            <View style={[styles.pin, selected === p.id && styles.pinActive]}>
              <Text style={[styles.pinText, selected === p.id && styles.pinTextActive]}>{formatINR(p.price)}</Text>
            </View>
          </Marker>
        ))}
      </MapView>

      {/* Top chrome */}
      <View style={[styles.topChrome, { top: insets.top + spacing.sm }]}>
        <View style={styles.searchPill}>
          <Icon name="search-outline" size={16} color={colors.muted} />
          <Text style={styles.searchTxt} numberOfLines={1}>{params.q ? String(params.q) : "Search Jaipur..."}</Text>
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
          <Pressable testID="heatmap-toggle" onPress={() => setHeat(v => !v)} style={[styles.filterChip, heat && styles.heatActive]}>
            <Icon name="flame-outline" size={13} color={heat ? colors.onBrandPrimary : colors.onSurface} />
            <Text style={[styles.filterText, heat && { color: colors.onBrandPrimary }]}>  Heat</Text>
          </Pressable>
        </ScrollView>
      </View>

      {heat && (
        <View style={[styles.heatLegend, { top: insets.top + 130 }]}>
          <Text style={styles.legendTitle}>Price / sq yd</Text>
          <View style={styles.legendBar}>
            {[0, 0.25, 0.5, 0.75, 1].map(i => (
              <View key={i} style={{ flex: 1, height: 8, backgroundColor: heatColor(i, 1) }} />
            ))}
          </View>
          <View style={{ flexDirection: "row", justifyContent: "space-between" }}>
            <Text style={styles.legendText}>Value</Text>
            <Text style={styles.legendText}>Prime</Text>
          </View>
        </View>
      )}

      {loading && (
        <View style={styles.loadingChip}>
          <ActivityIndicator color={colors.brand} size="small" />
          <Text style={styles.loadingTxt}>Loading properties...</Text>
        </View>
      )}

      <BottomSheet
        ref={sheetRef}
        index={0}
        snapPoints={["18%", "50%", "88%"]}
        backgroundStyle={styles.sheetBg}
        handleIndicatorStyle={{ backgroundColor: colors.borderStrong }}
      >
        <View style={styles.sheetHeader}>
          <Text style={styles.sheetTitle}>{items.length} properties</Text>
          <Text style={styles.sheetSub}>Tap a pin to view</Text>
        </View>
        <ScrollView contentContainerStyle={{ paddingHorizontal: spacing.lg, paddingBottom: spacing.xxxl }}>
          {focused && (
            <View style={{ marginBottom: spacing.md }}>
              <Text style={styles.selectedLabel}>SELECTED</Text>
              <PropertyCard property={focused} />
            </View>
          )}
          {items.filter(p => p.id !== focused?.id).map(p => (
            <PropertyCard key={p.id} property={p} compact />
          ))}
        </ScrollView>
      </BottomSheet>
    </View>
  );
}

const styles = StyleSheet.create({
  topChrome: { position: "absolute", left: 0, right: 0, paddingHorizontal: spacing.lg, gap: spacing.sm },
  searchPill: { flexDirection: "row", alignItems: "center", gap: spacing.sm, height: 44, paddingHorizontal: spacing.lg, borderRadius: radius.pill, backgroundColor: "rgba(255,255,240,0.96)", borderWidth: 1, borderColor: colors.border, ...shadow.card },
  searchTxt: { flex: 1, color: colors.onSurface, fontSize: 14 },
  chipsRow: { gap: spacing.sm, paddingRight: spacing.md, paddingVertical: 2 },
  filterChip: { paddingHorizontal: spacing.md, height: 36, justifyContent: "center", borderRadius: radius.pill, backgroundColor: "rgba(255,255,240,0.96)", borderWidth: 1, borderColor: colors.border, flexShrink: 0, ...shadow.card },
  filterChipActive: { backgroundColor: colors.brand, borderColor: colors.brand },
  heatActive: { backgroundColor: colors.brandPrimary, borderColor: colors.brandPrimary, flexDirection: "row", alignItems: "center" },
  filterText: { color: colors.onSurface, fontSize: 12, fontWeight: "600" },
  filterTextActive: { color: colors.onBrand },
  heatLegend: { position: "absolute", left: spacing.lg, right: spacing.lg, backgroundColor: "rgba(255,255,240,0.96)", borderRadius: radius.md, padding: spacing.md, borderWidth: 1, borderColor: colors.border, ...shadow.card },
  legendTitle: { fontSize: 10, fontWeight: "800", color: colors.muted, letterSpacing: 0.6, marginBottom: 6 },
  legendBar: { flexDirection: "row", height: 8, borderRadius: 4, overflow: "hidden", marginBottom: 4 },
  legendText: { fontSize: 10, fontWeight: "700", color: colors.onSurface, letterSpacing: 0.5 },
  pin: { paddingHorizontal: 10, paddingVertical: 5, backgroundColor: colors.surface, borderRadius: radius.pill, borderWidth: 1.5, borderColor: colors.brand, ...shadow.card },
  pinActive: { backgroundColor: colors.brandPrimary, borderColor: colors.brandPrimary, transform: [{ scale: 1.1 }] },
  pinText: { color: colors.brand, fontSize: 11, fontWeight: "700" },
  pinTextActive: { color: colors.onBrandPrimary },
  loadingChip: { position: "absolute", top: 140, alignSelf: "center", flexDirection: "row", alignItems: "center", gap: spacing.sm, paddingHorizontal: spacing.lg, paddingVertical: spacing.sm, borderRadius: radius.pill, backgroundColor: colors.surface, ...shadow.card },
  loadingTxt: { fontSize: 12, color: colors.onSurface, fontWeight: "500" },
  sheetBg: { backgroundColor: colors.surface, borderTopLeftRadius: 20, borderTopRightRadius: 20 },
  sheetHeader: { paddingHorizontal: spacing.lg, paddingBottom: spacing.md, flexDirection: "row", justifyContent: "space-between", alignItems: "baseline" },
  sheetTitle: { fontSize: 16, fontWeight: "700", color: colors.onSurface },
  sheetSub: { fontSize: 11, color: colors.muted },
  selectedLabel: { fontSize: 10, fontWeight: "700", color: colors.brandPrimary, letterSpacing: 0.5, marginBottom: 6 },
});
