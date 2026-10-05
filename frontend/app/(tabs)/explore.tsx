import React, { useEffect, useMemo, useRef, useState } from "react";
import { View, Text, StyleSheet, Pressable, ScrollView, ActivityIndicator, TextInput, Platform, Alert } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useLocalSearchParams, useRouter } from "expo-router";
import BottomSheet, { BottomSheetScrollView, BottomSheetView } from "@gorhom/bottom-sheet";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";
import { useAuth } from "@/src/auth-context";
import { PropertyCard, Property } from "@/src/components/property-card";
import { LocalityCard, Locality } from "@/src/components/locality-card";
import { PinPreview } from "@/src/components/pin-preview";
import { ExploreListView } from "@/src/components/explore-list-view";
import { WebMap, WebMapMarker, WebMapHeatPoint } from "@/src/components/web-map";
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
  const params = useLocalSearchParams<{ type?: string; q?: string; highlight?: string }>();
  const [items, setItems] = useState<Property[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>(params.type || "");
  const [q, setQ] = useState<string>(params.q ? String(params.q) : "");
  const [loading, setLoading] = useState(true);
  const [heat, setHeat] = useState(false);
  const [view, setView] = useState<"map" | "list">("map");
  const [listingType, setListingType] = useState<"Buy" | "Rent" | "Sell">("Buy");
  const [heatPoints, setHeatPoints] = useState<WebMapHeatPoint[]>([]);
  const [localities, setLocalities] = useState<Locality[]>([]);
  const sheetRef = useRef<BottomSheet>(null);

  useEffect(() => {
    (async () => {
      try {
        const [h, locs] = await Promise.all([
          api.get<{ points: any[] }>("/heatmap"),
          api.get<Locality[]>("/localities"),
        ]);
        const pts: WebMapHeatPoint[] = (h.points || []).map((p: any) => ({
          id: p.id, lat: p.lat, lng: p.lng, intensity: p.intensity, label: p.name,
        }));
        setHeatPoints(pts);
        setLocalities(locs);
      } catch {}
    })();
  }, []);

  const load = async () => {
    if (listingType === "Sell") { setLoading(false); return; }
    setLoading(true);
    try {
      const qs = new URLSearchParams();
      qs.set("listing_type", listingType);
      if (filter) qs.set("type", filter);
      if (q) qs.set("q", q);
      const data = await api.get<Property[]>(`/properties?${qs.toString()}`);
      setItems(data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, [filter, listingType]);

  // Deep link highlight ?highlight=p-01 — pan the map to it, DO NOT open the popup
  useEffect(() => {
    const h = params.highlight ? String(params.highlight) : "";
    if (h) {
      setSelected(h);        // highlights the pin visually
      setView("map");        // ensure map is visible
      // Note: we no longer snap the sheet open to show PinPreview;
      // user taps the pin to open details.
    }
  }, [params.highlight]);

  useEffect(() => {
    if (params.type !== undefined) setFilter(String(params.type || ""));
  }, [params.type]);

  const markers: WebMapMarker[] = useMemo(
    () => items.map((p: any) => ({
      id: p.id, lat: p.lat, lng: p.lng,
      label: formatINR(p.price),
      active: selected === p.id,
    })),
    [items, selected]
  );

  const initialRegion = { lat: 26.8891, lng: 75.7500 };

  const handleMarkerPress = (id: string) => {
    setSelected(id);
    sheetRef.current?.snapToIndex(2);
  };

  const openSell = () => router.push("/sell" as any);

  const saveSearch = async () => {
    if (!user) {
      Alert.alert("Login required", "Please sign in to save alerts.");
      return;
    }
    const name = [
      filter || "All",
      listingType,
      q ? `"${q}"` : null,
    ].filter(Boolean).join(" · ");
    try {
      await api.post("/saved-searches", {
        user_id: user.id,
        name,
        params: { type: filter || undefined, listing_type: listingType, q: q || undefined },
        notify: true,
      });
      Alert.alert("Alert saved 🔔", `We'll ping you when new ${filter || "properties"} match "${name}".`, [
        { text: "View my alerts", onPress: () => router.push("/saved-searches" as any) },
        { text: "OK" },
      ]);
    } catch (e: any) {
      Alert.alert("Could not save", e?.message || "Try again");
    }
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      {view === "map" ? (
        <View style={StyleSheet.absoluteFill}>
          <WebMap
            center={initialRegion}
            zoom={12}
            markers={markers}
            heatPoints={heatPoints}
            heat={heat}
            highlightedId={selected}
            onMarkerPress={handleMarkerPress}
          />
        </View>
      ) : (
        <View style={[StyleSheet.absoluteFill, { backgroundColor: colors.surfaceSecondary }]} />
      )}

      {/* Top chrome */}
      <View style={[styles.topChrome, { top: insets.top + spacing.sm }]}>
        <View style={styles.headerRow}>
          <View style={styles.hiPill}>
            <Text style={styles.hi} numberOfLines={1}>Hi, {user?.name?.split(" ")[0] || "there"}</Text>
          </View>
          <View style={{ flexDirection: "row", gap: spacing.sm }}>
            <Pressable testID="header-profile-btn" onPress={() => router.push("/profile")} style={styles.iconBtn}>
              <Icon name="menu-outline" size={20} color={colors.onSurface} />
            </Pressable>
            <Pressable testID="header-list-property-btn" onPress={() => router.push("/list-property")} style={styles.listBtn}>
              <Icon name="add" size={14} color={colors.onBrandPrimary} />
              <Text style={styles.listBtnText}>List</Text>
            </Pressable>
          </View>
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
        <View style={styles.segRow}>
          {(["Buy", "Rent", "Sell"] as const).map(t => {
            const active = listingType === t;
            return (
              <Pressable
                key={t}
                testID={`listing-type-${t.toLowerCase()}`}
                onPress={() => { setListingType(t); if (t === "Sell") openSell(); }}
                style={[styles.segBtn, active && styles.segBtnActive]}
              >
                <Text style={[styles.segText, active && styles.segTextActive]}>{t}</Text>
              </Pressable>
            );
          })}
          {/* View toggle lives alongside the segment control so it's always pinned */}
          <View style={styles.viewTogglePinned}>
            <Pressable testID="view-toggle-map" onPress={() => setView("map")} style={[styles.viewToggleBtn, view === "map" && styles.viewToggleActive]}>
              <Icon name="map-outline" size={13} color={view === "map" ? colors.onBrandPrimary : colors.onSurface} />
            </Pressable>
            <Pressable testID="view-toggle-list" onPress={() => setView("list")} style={[styles.viewToggleBtn, view === "list" && styles.viewToggleActive]}>
              <Icon name="list-outline" size={13} color={view === "list" ? colors.onBrandPrimary : colors.onSurface} />
            </Pressable>
          </View>
        </View>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chipsRow}>
          <Pressable testID="save-search-btn" onPress={saveSearch} style={[styles.filterChip, { flexDirection: "row", alignItems: "center", backgroundColor: colors.brandPrimary, borderColor: colors.brandPrimary }]}>
            <Icon name="notifications-outline" size={13} color={colors.onBrandPrimary} />
            <Text style={[styles.filterText, { color: colors.onBrandPrimary }]}>  Save & alert me</Text>
          </Pressable>
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

      {heat && view === "map" && (
        <View style={[styles.heatLegend, { top: insets.top + 275 }]}>
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

      {loading && view === "map" && (
        <View style={styles.loadingChip}>
          <ActivityIndicator color={colors.brand} size="small" />
          <Text style={styles.loadingTxt}>Loading properties...</Text>
        </View>
      )}

      {/* List view: full-screen content ABOVE the map container */}
      {view === "list" ? (
        <View style={[styles.listOverlay, { paddingTop: insets.top + 240 }]}>
          <ExploreListView items={items} filter={filter} />
        </View>
      ) : (
        <BottomSheet
          ref={sheetRef}
          index={0}
          snapPoints={["22%", "55%", "92%"]}
          enableDynamicSizing={false}
          backgroundStyle={styles.sheetBg}
          handleIndicatorStyle={{ backgroundColor: colors.borderStrong }}
        >
          <BottomSheetView style={styles.sheetHeader}>
            {selected ? (
              <>
                <Pressable
                  testID="pin-preview-back"
                  onPress={() => setSelected(null)}
                  style={styles.backChip}
                  hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
                  android_ripple={{ color: colors.border, borderless: true }}
                >
                  <Icon name="chevron-back" size={20} color={colors.onSurface} />
                  <Text style={styles.backChipText}>Back to listings</Text>
                </Pressable>
                <Text style={styles.selectedKicker}>SELECTED</Text>
              </>
            ) : (
              <Text style={styles.sheetTitle}>{items.length} properties</Text>
            )}
          </BottomSheetView>

          {selected ? (
            <BottomSheetScrollView contentContainerStyle={{ paddingBottom: spacing.xxxl }}>
              <PinPreview propertyId={selected} onClose={() => setSelected(null)} />
            </BottomSheetScrollView>
          ) : (
            <BottomSheetScrollView
              contentContainerStyle={{ paddingBottom: spacing.xxxl, paddingTop: spacing.sm }}
            >
              {localities.length > 0 && !filter && (
                <View style={{ marginBottom: spacing.lg }}>
                  <Text style={styles.stripTitle}>Trending localities</Text>
                  <ScrollView
                    horizontal
                    showsHorizontalScrollIndicator={false}
                    contentContainerStyle={{ paddingHorizontal: spacing.lg, gap: spacing.md }}
                    nestedScrollEnabled
                    directionalLockEnabled
                    {...(Platform.OS === "android"
                      ? {
                          // Lock the horizontal gesture so the parent BottomSheet doesn't eat it
                          overScrollMode: "never" as const,
                        }
                      : {})}
                  >
                    {localities.map(l => <LocalityCard key={l.id} locality={l} />)}
                  </ScrollView>
                </View>
              )}
              <View style={{ paddingHorizontal: spacing.lg }}>
                <Text style={styles.stripTitle}>{filter ? `${filter} listings` : "Listings"} ({items.length})</Text>
                {items.map(p => (
                  <PropertyCard key={p.id} property={p} compact />
                ))}
              </View>
            </BottomSheetScrollView>
          )}
        </BottomSheet>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  topChrome: { position: "absolute", left: 0, right: 0, paddingHorizontal: spacing.lg, gap: spacing.sm, zIndex: 20 },
  headerRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between" },
  hiPill: { paddingHorizontal: spacing.md, height: 40, borderRadius: radius.pill, backgroundColor: "rgba(255,255,240,0.96)", borderWidth: 1, borderColor: colors.border, justifyContent: "center", ...shadow.card },
  hi: { fontSize: 13, fontWeight: "700", color: colors.onSurface, maxWidth: 200 },
  iconBtn: { width: 40, height: 40, borderRadius: 20, backgroundColor: "rgba(255,255,240,0.96)", borderWidth: 1, borderColor: colors.border, alignItems: "center", justifyContent: "center", ...shadow.card },
  listBtn: { flexDirection: "row", alignItems: "center", gap: 4, paddingHorizontal: 14, height: 40, borderRadius: radius.pill, backgroundColor: colors.brandPrimary, ...shadow.card },
  listBtnText: { color: colors.onBrandPrimary, fontSize: 13, fontWeight: "700" },
  segRow: {
    flexDirection: "row", alignItems: "center",
    backgroundColor: "rgba(255,255,240,0.96)", borderWidth: 1, borderColor: colors.border,
    borderRadius: radius.pill, padding: 3, gap: 2, alignSelf: "flex-start", ...shadow.card,
  },
  segBtn: { paddingHorizontal: 14, paddingVertical: 6, borderRadius: radius.pill },
  segBtnActive: { backgroundColor: colors.brandPrimary },
  segText: { fontSize: 12, fontWeight: "700", color: colors.onSurface, letterSpacing: 0.3 },
  segTextActive: { color: colors.onBrandPrimary },
  viewTogglePinned: {
    flexDirection: "row", gap: 2, marginLeft: spacing.sm, borderLeftWidth: 1, borderLeftColor: colors.border, paddingLeft: 6,
  },
  viewToggleBtn: { paddingHorizontal: 10, paddingVertical: 6, borderRadius: radius.pill, alignItems: "center", justifyContent: "center" },
  viewToggleActive: { backgroundColor: colors.brand },
  searchPill: { flexDirection: "row", alignItems: "center", gap: spacing.sm, height: 44, paddingHorizontal: spacing.lg, borderRadius: radius.pill, backgroundColor: "rgba(255,255,240,0.96)", borderWidth: 1, borderColor: colors.border, ...shadow.card },
  searchTxt: { flex: 1, color: colors.onSurface, fontSize: 14 },
  chipsRow: { gap: spacing.sm, paddingRight: spacing.md, paddingVertical: 2 },
  filterChip: { paddingHorizontal: spacing.md, height: 36, justifyContent: "center", borderRadius: radius.pill, backgroundColor: "rgba(255,255,240,0.96)", borderWidth: 1, borderColor: colors.border, flexShrink: 0, ...shadow.card },
  filterChipActive: { backgroundColor: colors.brand, borderColor: colors.brand },
  heatActive: { backgroundColor: colors.brandPrimary, borderColor: colors.brandPrimary, flexDirection: "row", alignItems: "center" },
  filterText: { color: colors.onSurface, fontSize: 12, fontWeight: "600" },
  filterTextActive: { color: colors.onBrand },
  heatLegend: { position: "absolute", left: spacing.lg, right: spacing.lg, backgroundColor: "rgba(255,255,240,0.96)", borderRadius: radius.md, padding: spacing.md, borderWidth: 1, borderColor: colors.border, ...shadow.card, zIndex: 15 },
  legendTitle: { fontSize: 10, fontWeight: "800", color: colors.muted, letterSpacing: 0.6, marginBottom: 6 },
  legendBar: { flexDirection: "row", height: 8, borderRadius: 4, overflow: "hidden", marginBottom: 4 },
  legendText: { fontSize: 10, fontWeight: "700", color: colors.onSurface, letterSpacing: 0.5 },
  loadingChip: { position: "absolute", top: 240, alignSelf: "center", flexDirection: "row", alignItems: "center", gap: spacing.sm, paddingHorizontal: spacing.lg, paddingVertical: spacing.sm, borderRadius: radius.pill, backgroundColor: colors.surface, ...shadow.card, zIndex: 10 },
  loadingTxt: { fontSize: 12, color: colors.onSurface, fontWeight: "500" },
  listOverlay: { position: "absolute", top: 0, left: 0, right: 0, bottom: 0, backgroundColor: colors.surface, zIndex: 5 },
  sheetBg: { backgroundColor: colors.surface, borderTopLeftRadius: 20, borderTopRightRadius: 20 },
  sheetHeader: { paddingHorizontal: spacing.lg, paddingTop: spacing.sm, paddingBottom: spacing.md, flexDirection: "row", justifyContent: "space-between", alignItems: "center", minHeight: 48 },
  sheetTitle: { fontSize: 16, fontWeight: "700", color: colors.onSurface },
  backChip: {
    flexDirection: "row", alignItems: "center", gap: 2,
    paddingVertical: 8, paddingRight: spacing.md, minHeight: 44,
  },
  backChipText: { fontSize: 13, fontWeight: "700", color: colors.onSurface },
  selectedKicker: { fontSize: 10, fontWeight: "800", color: colors.brandPrimary, letterSpacing: 0.8 },
  stripTitle: { fontSize: 12, fontWeight: "800", color: colors.muted, letterSpacing: 0.8, marginBottom: spacing.sm, paddingHorizontal: spacing.lg },
});
