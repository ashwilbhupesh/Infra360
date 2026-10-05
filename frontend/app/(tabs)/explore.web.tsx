import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, Pressable, ScrollView, ActivityIndicator, TextInput } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useLocalSearchParams, useRouter } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";
import { useAuth } from "@/src/auth-context";
import { useLocationStore } from "@/src/stores/location";
import { PropertyCard, Property } from "@/src/components/property-card";
import { LocalityCard, Locality } from "@/src/components/locality-card";
import { PinPreview } from "@/src/components/pin-preview";
import { ExploreListView } from "@/src/components/explore-list-view";
import { VoiceSheet } from "@/src/components/voice-sheet";
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
  const { user } = useAuth();
  const params = useLocalSearchParams<{ type?: string; q?: string; highlight?: string }>();
  const [items, setItems] = useState<Property[]>([]);
  const [filter, setFilter] = useState(params.type || "");
  const [q, setQ] = useState(params.q ? String(params.q) : "");
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<string | null>(null);
  const [heat, setHeat] = useState(false);
  const [view, setView] = useState<"map" | "list">("map");
  const [listingType, setListingType] = useState<"Buy" | "Rent" | "Sell">("Buy");
  const [bedrooms, setBedrooms] = useState<number | null>(null);
  const [priceBucket, setPriceBucket] = useState<string | null>(null);
  const [areaBucket, setAreaBucket] = useState<string | null>(null);
  const [voiceOpen, setVoiceOpen] = useState(false);
  const [voiceSummary, setVoiceSummary] = useState<string | null>(null);
  const [heatPoints, setHeatPoints] = useState<HeatPoint[]>([]);
  const [localities, setLocalities] = useState<Locality[]>([]);
  const activeAddr = useLocationStore(s => s.getActive());

  const load = async () => {
    setLoading(true);
    try {
      const qs = new URLSearchParams();
      qs.set("listing_type", listingType);
      if (filter) qs.set("type", filter);
      if (q) qs.set("q", q);
      if (bedrooms !== null) qs.set("bedrooms", String(bedrooms));
      if (priceBucket) {
        const [lo, hi] = priceBucket.split("-");
        if (lo && Number(lo) > 0) qs.set("min_price", lo);
        if (hi && Number(hi) > 0) qs.set("max_price", hi);
      }
      const data = await api.get<Property[]>(`/properties?${qs.toString()}`);
      let filtered = data;
      if (areaBucket) {
        const [lo, hi] = areaBucket.split("-").map(Number);
        filtered = data.filter(p => {
          if (!p.area) return true;
          if (hi > 0) return p.area >= lo && p.area <= hi;
          return p.area >= lo;
        });
      }
      setItems(filtered);
    } finally { setLoading(false); }
  };
  useEffect(() => { load(); }, [filter, listingType, bedrooms, priceBucket, areaBucket]);
  useEffect(() => { setBedrooms(null); setPriceBucket(null); setAreaBucket(null); }, [filter]);

  useEffect(() => {
    const h = params.highlight ? String(params.highlight) : "";
    if (h) { setSelected(h); setView("map"); }
  }, [params.highlight]);

  useEffect(() => {
    (async () => {
      try {
        const [h, locs] = await Promise.all([
          api.get<{ points: HeatPoint[] }>("/heatmap"),
          api.get<Locality[]>("/localities"),
        ]);
        setHeatPoints(h.points || []);
        setLocalities(locs);
      } catch {}
    })();
  }, []);

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface, paddingTop: insets.top + spacing.sm }}>
      <View style={{ paddingHorizontal: spacing.lg, gap: spacing.sm }}>
        <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
          <Pressable
            testID="header-location-pill"
            onPress={() => router.push("/location-picker" as any)}
            style={styles.locPill}
            hitSlop={6}
          >
            <Icon name="location-outline" size={14} color={colors.brand} />
            <View style={{ flex: 1 }}>
              <Text style={styles.locKicker} numberOfLines={1}>Hi, {user?.name?.split(" ")[0] || "there"}</Text>
              <Text style={styles.locTitle} numberOfLines={1}>
                {activeAddr?.label || "Jaipur"} <Icon name="chevron-down" size={11} color={colors.onSurface} />
              </Text>
            </View>
          </Pressable>
          <View style={{ flexDirection: "row", gap: spacing.sm }}>
            <Pressable testID="header-profile-btn" onPress={() => router.push("/profile")} style={styles.iconBtnWeb}>
              <Icon name="settings-outline" size={18} color={colors.onSurface} />
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
        </View>
        <View style={styles.segRowWeb}>
          {(["Buy", "Rent", "Sell"] as const).map(t => {
            const active = listingType === t;
            return (
              <Pressable
                key={t}
                testID={`listing-type-${t.toLowerCase()}`}
                onPress={() => {
                  setListingType(t);
                  if (t === "Sell") router.push("/sell" as any);
                }}
                style={[styles.segBtnWeb, active && styles.segBtnActiveWeb]}
              >
                <Text style={[styles.segTextWeb, active && styles.segTextActiveWeb]}>{t}</Text>
              </Pressable>
            );
          })}
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

        {filter ? (
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.subChipsRow}>
            {["Apartment", "Villa"].includes(filter) && [1, 2, 3, 4].map(n => (
              <Pressable
                key={`bhk-${n}`}
                testID={`subfilter-bhk-${n}`}
                onPress={() => setBedrooms(bedrooms === n ? null : n)}
                style={[styles.subChip, bedrooms === n && styles.subChipActive]}
              >
                <Text style={[styles.subChipText, bedrooms === n && styles.subChipTextActive]}>{n}+ BHK</Text>
              </Pressable>
            ))}
            {["Residential Plot", "Agricultural Land", "Commercial"].includes(filter) && [
              { k: "0-100", label: "<100 sq yd" },
              { k: "100-500", label: "100–500" },
              { k: "500-2000", label: "500–2 K" },
              { k: "2000-0", label: "2 K+ sq yd" },
            ].map(b => (
              <Pressable
                key={`area-${b.k}`}
                testID={`subfilter-area-${b.k}`}
                onPress={() => setAreaBucket(areaBucket === b.k ? null : b.k)}
                style={[styles.subChip, areaBucket === b.k && styles.subChipActive]}
              >
                <Text style={[styles.subChipText, areaBucket === b.k && styles.subChipTextActive]}>{b.label}</Text>
              </Pressable>
            ))}
            {[
              { k: "0-5000000", label: "<₹50 L" },
              { k: "5000000-10000000", label: "₹50 L–1 Cr" },
              { k: "10000000-30000000", label: "₹1–3 Cr" },
              { k: "30000000-0", label: "₹3 Cr+" },
            ].map(b => (
              <Pressable
                key={`price-${b.k}`}
                testID={`subfilter-price-${b.k}`}
                onPress={() => setPriceBucket(priceBucket === b.k ? null : b.k)}
                style={[styles.subChip, priceBucket === b.k && styles.subChipActive]}
              >
                <Text style={[styles.subChipText, priceBucket === b.k && styles.subChipTextActive]}>{b.label}</Text>
              </Pressable>
            ))}
            {(bedrooms !== null || priceBucket || areaBucket) && (
              <Pressable
                testID="subfilter-clear"
                onPress={() => { setBedrooms(null); setPriceBucket(null); setAreaBucket(null); }}
                style={[styles.subChip, { backgroundColor: colors.surfaceSecondary, borderColor: colors.error }]}
              >
                <Icon name="close" size={11} color={colors.error} />
                <Text style={[styles.subChipText, { color: colors.error }]}>Clear</Text>
              </Pressable>
            )}
          </ScrollView>
        ) : null}
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
        <View style={styles.sheetHeaderRow}>
          {selected && view === "map" ? (
            <>
              <Text style={styles.sheetTitle}>Property preview</Text>
              <Text style={{ fontSize: 10, fontWeight: "800", color: colors.brandPrimary, letterSpacing: 0.8 }}>SELECTED</Text>
            </>
          ) : (
            <>
              <Text style={styles.sheetTitle}>{loading ? "Loading..." : `${items.length} properties`}</Text>
              <View style={styles.viewToggle}>
                <Pressable testID="explore-voice-mic" onPress={() => setVoiceOpen(true)} style={styles.inlineMicBtn} hitSlop={6}>
                  <Icon name="mic" size={13} color="#FFFFFF" />
                </Pressable>
                <Pressable testID="view-toggle-map" onPress={() => setView("map")} style={[styles.viewToggleBtn, view === "map" && styles.viewToggleActive]}>
                  <Icon name="map-outline" size={13} color={view === "map" ? colors.onBrandPrimary : colors.onSurface} />
                  <Text style={[styles.viewToggleText, view === "map" && { color: colors.onBrandPrimary }]}>Map</Text>
                </Pressable>
                <Pressable testID="view-toggle-list" onPress={() => setView("list")} style={[styles.viewToggleBtn, view === "list" && styles.viewToggleActive]}>
                  <Icon name="list-outline" size={13} color={view === "list" ? colors.onBrandPrimary : colors.onSurface} />
                  <Text style={[styles.viewToggleText, view === "list" && { color: colors.onBrandPrimary }]}>List</Text>
                </Pressable>
              </View>
            </>
          )}
        </View>
        {view === "list" ? (
          <ExploreListView items={items} filter={filter} />
        ) : selected ? (
          <>
            <ScrollView contentContainerStyle={{ paddingBottom: 96 }}>
              <PinPreview propertyId={selected} onClose={() => setSelected(null)} />
            </ScrollView>
            <View style={styles.backBar}>
              <Pressable
                testID="pin-preview-back"
                onPress={() => setSelected(null)}
                style={({ pressed }) => [styles.backBarBtn, pressed && { opacity: 0.75 }]}
                hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
              >
                <Icon name="chevron-back" size={18} color={colors.onBrandPrimary} />
                <Text style={styles.backBarText}>Back to listings</Text>
              </Pressable>
            </View>
          </>
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
            <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingBottom: 120 }}>
              {items.map(p => <PropertyCard key={p.id} property={p} compact />)}
            </ScrollView>
          </>
        )}
      </View>

      {voiceSummary ? (
        <View style={styles.voiceSummary}>
          <Icon name="mic" size={11} color={colors.brand} />
          <Text style={styles.voiceSummaryTxt} numberOfLines={2}>“{voiceSummary}”</Text>
          <Pressable onPress={() => setVoiceSummary(null)} hitSlop={10}>
            <Icon name="close" size={13} color={colors.muted} />
          </Pressable>
        </View>
      ) : null}

      <VoiceSheet
        visible={voiceOpen}
        endpoint="/api/explore/voice-search"
        title="Narrate your search"
        subtitle="Speak in any language — Hindi, English, Marwari, Gujarati..."
        hint='Try: "Show me a 2 BHK flat in Vaishali Nagar under 50 lakhs"'
        onClose={() => setVoiceOpen(false)}
        onResult={(res: any) => {
          const f = res?.filters || {};
          if (f.listing_type && ["Buy", "Rent"].includes(f.listing_type)) setListingType(f.listing_type);
          setFilter(f.type || "");
          setBedrooms(typeof f.bedrooms === "number" ? f.bedrooms : null);
          if (f.max_price || f.min_price) setPriceBucket(`${f.min_price || 0}-${f.max_price || 0}`);
          else setPriceBucket(null);
          setAreaBucket(null);
          if (f.q) setQ(f.q);
          if (f.locality_id) router.push(`/locality/${f.locality_id}` as any);
          setVoiceSummary(res?.summary || res?.translation || res?.transcript || null);
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  hi: { fontSize: 15, fontWeight: "800", color: colors.onSurface },
  voiceFab: { position: "absolute", right: 16, bottom: 110, width: 52, height: 52, borderRadius: 26, backgroundColor: colors.brandPrimary, alignItems: "center", justifyContent: "center", zIndex: 20 },
  inlineMicBtn: { width: 30, height: 28, borderRadius: 14, backgroundColor: colors.brandPrimary, alignItems: "center", justifyContent: "center", marginRight: 4 },
  voiceSummary: { position: "absolute", left: spacing.lg, right: 76, top: 220, flexDirection: "row", alignItems: "center", gap: 8, paddingHorizontal: 12, paddingVertical: 7, borderRadius: radius.pill, backgroundColor: "rgba(255,255,240,0.98)", borderWidth: 1, borderColor: colors.brand, zIndex: 15 },
  voiceSummaryTxt: { flex: 1, fontSize: 11, color: colors.onSurface, fontWeight: "700" },
  locPill: { flex: 1, flexDirection: "row", alignItems: "center", gap: 8, paddingHorizontal: spacing.md, paddingVertical: 6, backgroundColor: colors.surfaceSecondary, borderRadius: radius.pill, borderWidth: 1, borderColor: colors.border, marginRight: spacing.sm, maxWidth: "68%" },
  subChipsRow: { gap: 6, paddingVertical: 4 },
  subChip: { flexDirection: "row", alignItems: "center", gap: 4, paddingHorizontal: 10, height: 28, borderRadius: radius.pill, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, justifyContent: "center" },
  subChipActive: { backgroundColor: colors.brand, borderColor: colors.brand },
  subChipText: { fontSize: 11, fontWeight: "700", color: colors.onSurface },
  subChipTextActive: { color: colors.onBrand },
  locKicker: { fontSize: 10, color: colors.muted, fontWeight: "700" },
  locTitle: { fontSize: 13, color: colors.onSurface, fontWeight: "800" },
  backPill: { flexDirection: "row", alignItems: "center", gap: 4, paddingVertical: 10, paddingHorizontal: spacing.sm, minHeight: 44, borderRadius: radius.pill, backgroundColor: colors.brandTertiary },
  backPillText: { fontSize: 13, fontWeight: "800", color: colors.brand },
  backBar: { position: "absolute", left: 0, right: 0, bottom: 0, paddingHorizontal: spacing.lg, paddingTop: spacing.sm, paddingBottom: spacing.md, backgroundColor: colors.surface, borderTopWidth: 1, borderTopColor: colors.border },
  backBarBtn: { flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 6, minHeight: 48, borderRadius: radius.pill, backgroundColor: colors.brandPrimary },
  backBarText: { fontSize: 14, fontWeight: "800", color: colors.onBrandPrimary, letterSpacing: 0.3 },
  iconBtnWeb: { width: 34, height: 34, borderRadius: 17, backgroundColor: colors.surfaceSecondary, alignItems: "center", justifyContent: "center", borderWidth: 1, borderColor: colors.border },
  listBtn: { flexDirection: "row", alignItems: "center", gap: 4, paddingHorizontal: 14, height: 34, borderRadius: radius.pill, backgroundColor: colors.brandPrimary },
  listBtnText: { color: colors.onBrandPrimary, fontSize: 12, fontWeight: "700" },
  segRowWeb: { flexDirection: "row", alignSelf: "flex-start", gap: 2, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border, borderRadius: radius.pill, padding: 3 },
  segBtnWeb: { paddingHorizontal: 16, paddingVertical: 6, borderRadius: radius.pill },
  segBtnActiveWeb: { backgroundColor: colors.brandPrimary },
  segTextWeb: { fontSize: 12, fontWeight: "700", color: colors.onSurface, letterSpacing: 0.3 },
  segTextActiveWeb: { color: colors.onBrandPrimary },
  stripTitle: { fontSize: 12, fontWeight: "800", color: colors.muted, letterSpacing: 0.8, marginBottom: spacing.sm, paddingHorizontal: spacing.lg, paddingTop: spacing.md },
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
  sheetHeaderRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", paddingHorizontal: spacing.lg, paddingBottom: spacing.sm },
  sheetTitle: { fontSize: 16, fontWeight: "700", color: colors.onSurface },
  viewToggle: { flexDirection: "row", backgroundColor: colors.surfaceSecondary, borderRadius: radius.pill, padding: 3, gap: 2 },
  viewToggleBtn: { flexDirection: "row", alignItems: "center", gap: 4, paddingHorizontal: 10, paddingVertical: 5, borderRadius: radius.pill },
  viewToggleActive: { backgroundColor: colors.brand },
  viewToggleText: { fontSize: 11, fontWeight: "700", color: colors.onSurface },
});
