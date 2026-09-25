import React, { useEffect, useMemo, useRef, useState } from "react";
import { View, Text, StyleSheet, Pressable, ScrollView, ActivityIndicator, TextInput } from "react-native";
import MapView, { Marker, Circle, PROVIDER_DEFAULT } from "react-native-maps";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useLocalSearchParams, useRouter } from "expo-router";
import BottomSheet from "@gorhom/bottom-sheet";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";
import { useAuth } from "@/src/auth-context";
import { PropertyCard, Property } from "@/src/components/property-card";
import { LocalityCard, Locality } from "@/src/components/locality-card";
import { PinPreview } from "@/src/components/pin-preview";
import { ExploreListView } from "@/src/components/explore-list-view";
import { formatINR } from "@/src/utils/format";
import { heatColor } from "@/src/utils/heat";

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
  const router = useRouter();
  const { user } = useAuth();
  const params = useLocalSearchParams<{ type?: string; q?: string }>();
  const [items, setItems] = useState<Property[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>(params.type || "");
  const [q, setQ] = useState<string>(params.q ? String(params.q) : "");
  const [loading, setLoading] = useState(true);
  const [heat, setHeat] = useState(false);
  const [view, setView] = useState<"map" | "list">("map");
  const [heatPoints, setHeatPoints] = useState<Array<{ id: string; name: string; lat: number; lng: number; intensity: number; median_price_per_sq_yd: number }>>([]);
  const [localities, setLocalities] = useState<Locality[]>([]);
  const sheetRef = useRef<BottomSheet>(null);

  useEffect(() => {
    (async () => {
      try {
        const [h, locs] = await Promise.all([
          api.get<{ points: any[] }>("/heatmap"),
          api.get<Locality[]>("/localities"),
        ]);
        setHeatPoints(h.points || []);
        setLocalities(locs);
      } catch {}
    })();
  }, []);

  const load = async () => {
    setLoading(true);
    try {
      const qs = new URLSearchParams();
      if (filter) qs.set("type", filter);
      if (q) qs.set("q", q);
      const data = await api.get<Property[]>(`/properties?${qs.toString()}`);
      setItems(data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, [filter]);

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
            onPress={() => { setSelected(p.id); sheetRef.current?.snapToIndex(2); }}
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
        <View style={styles.headerRow}>
          <View style={styles.hiPill}>
            <Text style={styles.hi} numberOfLines={1}>Hi, {user?.name?.split(" ")[0] || "there"}</Text>
          </View>
          <Pressable testID="header-list-property-btn" onPress={() => router.push("/list-property")} style={styles.listBtn}>
            <Icon name="add" size={14} color={colors.onBrandPrimary} />
            <Text style={styles.listBtnText}>List</Text>
          </Pressable>
        </View>
        <View style={styles.searchPill}>
          <Icon name="search-outline" size={16} color={colors.muted} />
          <TextInput
            testID="explore-search-input"
            style={styles.searchTxt}
            placeholder="Search locality, project, road..."
            placeholderTextColor={colors.muted}
            value={q}
            onChangeText={setQ}
            onSubmitEditing={load}
            returnKeyType="search"
          />
          {q ? (
            <Pressable onPress={() => { setQ(""); }} hitSlop={10}><Icon name="close-circle" size={16} color={colors.muted} /></Pressable>
          ) : null}
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
        <View style={[styles.heatLegend, { top: insets.top + 195 }]}>
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
        snapPoints={["22%", "55%", "92%"]}
        backgroundStyle={styles.sheetBg}
        handleIndicatorStyle={{ backgroundColor: colors.borderStrong }}
      >
        <View style={styles.sheetHeader}>
          <Text style={styles.sheetTitle}>{items.length} properties</Text>
          <View style={styles.viewToggle}>
            <Pressable testID="view-toggle-map" onPress={() => setView("map")} style={[styles.viewToggleBtn, view === "map" && styles.viewToggleActive]}>
              <Icon name="map-outline" size={13} color={view === "map" ? colors.onBrandPrimary : colors.onSurface} />
              <Text style={[styles.viewToggleText, view === "map" && { color: colors.onBrandPrimary }]}>Map</Text>
            </Pressable>
            <Pressable testID="view-toggle-list" onPress={() => setView("list")} style={[styles.viewToggleBtn, view === "list" && styles.viewToggleActive]}>
              <Icon name="list-outline" size={13} color={view === "list" ? colors.onBrandPrimary : colors.onSurface} />
              <Text style={[styles.viewToggleText, view === "list" && { color: colors.onBrandPrimary }]}>List</Text>
            </Pressable>
          </View>
        </View>

        {view === "list" ? (
          <ExploreListView items={items} filter={filter} />
        ) : selected ? (
          <ScrollView contentContainerStyle={{ paddingBottom: spacing.xxxl }}>
            <PinPreview propertyId={selected} onClose={() => setSelected(null)} />
          </ScrollView>
        ) : (
          <>
            {localities.length > 0 && (
              <View style={{ marginBottom: spacing.sm }}>
                <Text style={styles.stripTitle}>Trending localities</Text>
                <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ paddingHorizontal: spacing.lg, gap: spacing.md }}>
                  {localities.map(l => <LocalityCard key={l.id} locality={l} />)}
                </ScrollView>
              </View>
            )}
            <ScrollView contentContainerStyle={{ paddingHorizontal: spacing.lg, paddingBottom: spacing.xxxl }}>
              <Text style={styles.stripTitle}>Listings</Text>
              {items.map(p => (
                <PropertyCard key={p.id} property={p} compact />
              ))}
            </ScrollView>
          </>
        )}
      </BottomSheet>
    </View>
  );
}

const styles = StyleSheet.create({
  topChrome: { position: "absolute", left: 0, right: 0, paddingHorizontal: spacing.lg, gap: spacing.sm },
  headerRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between" },
  hiPill: { paddingHorizontal: spacing.md, height: 40, borderRadius: radius.pill, backgroundColor: "rgba(255,255,240,0.96)", borderWidth: 1, borderColor: colors.border, justifyContent: "center", ...shadow.card },
  hi: { fontSize: 13, fontWeight: "700", color: colors.onSurface, maxWidth: 200 },
  listBtn: { flexDirection: "row", alignItems: "center", gap: 4, paddingHorizontal: 14, height: 40, borderRadius: radius.pill, backgroundColor: colors.brandPrimary, ...shadow.card },
  listBtnText: { color: colors.onBrandPrimary, fontSize: 13, fontWeight: "700" },
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
  loadingChip: { position: "absolute", top: 180, alignSelf: "center", flexDirection: "row", alignItems: "center", gap: spacing.sm, paddingHorizontal: spacing.lg, paddingVertical: spacing.sm, borderRadius: radius.pill, backgroundColor: colors.surface, ...shadow.card },
  loadingTxt: { fontSize: 12, color: colors.onSurface, fontWeight: "500" },
  sheetBg: { backgroundColor: colors.surface, borderTopLeftRadius: 20, borderTopRightRadius: 20 },
  sheetHeader: { paddingHorizontal: spacing.lg, paddingBottom: spacing.sm, flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  sheetTitle: { fontSize: 16, fontWeight: "700", color: colors.onSurface },
  sheetSub: { fontSize: 11, color: colors.muted },
  viewToggle: { flexDirection: "row", backgroundColor: colors.surfaceSecondary, borderRadius: radius.pill, padding: 3, gap: 2 },
  viewToggleBtn: { flexDirection: "row", alignItems: "center", gap: 4, paddingHorizontal: 10, paddingVertical: 5, borderRadius: radius.pill },
  viewToggleActive: { backgroundColor: colors.brand },
  viewToggleText: { fontSize: 11, fontWeight: "700", color: colors.onSurface },
  stripTitle: { fontSize: 12, fontWeight: "800", color: colors.muted, letterSpacing: 0.8, marginBottom: spacing.sm, paddingHorizontal: spacing.lg },
  selectedLabel: { fontSize: 10, fontWeight: "700", color: colors.brandPrimary, letterSpacing: 0.5, marginBottom: 6 },
});
