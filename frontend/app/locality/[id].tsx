import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, Pressable, Dimensions } from "react-native";
import { Image } from "expo-image";
import { useLocalSearchParams, useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";
import { useAuth } from "@/src/auth-context";
import { formatINR, formatRange, indianComma } from "@/src/utils/format";
import { PropertyCard, Property } from "@/src/components/property-card";
import { PriceChart } from "@/src/components/price-chart";

const W = Dimensions.get("window").width;

export default function LocalityDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { user } = useAuth();
  const [loc, setLoc] = useState<any>(null);
  const [props, setProps] = useState<Property[]>([]);
  const [following, setFollowing] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [l, p] = await Promise.all([
          api.get<any>(`/localities/${id}`),
          api.get<Property[]>(`/properties?locality_id=${id}&limit=20`),
        ]);
        setLoc(l); setProps(p);
      } finally { setLoading(false); }
    })();
  }, [id]);

  const toggleFollow = async () => {
    if (!user) return;
    const res = await api.post<{ following: boolean }>("/follows/toggle", { user_id: user.id, locality_id: id });
    setFollowing(res.following);
  };

  if (loading || !loc) {
    return <View style={{ flex: 1, backgroundColor: colors.surface, alignItems: "center", justifyContent: "center" }}><ActivityIndicator color={colors.brand} /></View>;
  }

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <ScrollView contentContainerStyle={{ paddingBottom: 60 }} showsVerticalScrollIndicator={false}>
        <View>
          <Image source={{ uri: loc.image }} style={styles.hero} contentFit="cover" />
          <View style={styles.heroOverlay} />
          <Pressable testID="back-btn" onPress={() => router.back()} style={[styles.iconBtn, { top: insets.top + spacing.sm, left: spacing.lg }]}>
            <Icon name="chevron-back" size={20} color={colors.onSurface} />
          </Pressable>
          <Pressable testID="follow-btn" onPress={toggleFollow} style={[styles.followBtn, { top: insets.top + spacing.sm, right: spacing.lg }]}>
            <Icon name={following ? "checkmark" : "add"} size={14} color={colors.onBrandPrimary} />
            <Text style={styles.followBtnText}>{following ? "Following" : "Follow"}</Text>
          </Pressable>
          <View style={styles.heroText}>
            <Text style={styles.heroName}>{loc.name}</Text>
            <Text style={styles.heroLoc}>{loc.city}, {loc.state}</Text>
            <Text style={styles.heroSub}>Property & Infrastructure Intelligence</Text>
          </View>
        </View>

        <View style={styles.body}>
          {/* Metric cards */}
          <View style={styles.metricsGrid}>
            <Metric label="Median Asking" value={`₹${indianComma(loc.median_price_per_sq_yd)}`} unit="/sq yd" />
            <Metric label="Properties" value={String(loc.properties_count || loc.listings_count)} unit="listed" />
            <Metric label="YoY Change" value={`${loc.yoy_change_pct > 0 ? "+" : ""}${loc.yoy_change_pct}%`} unit="1Y" tone={loc.yoy_change_pct > 0 ? "up" : "down"} />
          </View>

          <Pressable
            testID="compare-localities-btn"
            onPress={() => router.push(`/compare-localities?ids=${id}` as any)}
            style={styles.compareLocCta}
          >
            <Icon name="git-compare-outline" size={16} color={colors.brand} />
            <Text style={styles.compareLocTxt}>Compare {loc.name} with other localities</Text>
            <Icon name="chevron-forward" size={16} color={colors.muted} />
          </Pressable>

          {/* Lifestyle score */}
          {loc.lifestyle && (
            <View style={styles.lsCard}>
              <View style={styles.lsHeader}>
                <View>
                  <Text style={styles.lsKicker}>NEIGHBOURHOOD LIFESTYLE SCORE</Text>
                  <Text style={styles.lsTitle}>How family-friendly is {loc.name}?</Text>
                </View>
                <View style={[styles.lsScorePill, { backgroundColor: scoreBg(loc.lifestyle.overall) }]}>
                  <Text style={[styles.lsScoreText, { color: scoreFg(loc.lifestyle.overall) }]}>{loc.lifestyle.overall}</Text>
                </View>
              </View>
              <View style={{ marginTop: spacing.md, gap: spacing.md }}>
                <LSBar icon="walk-outline" label="Walkability" value={loc.lifestyle.walkability} />
                <LSBar icon="school-outline" label="Schools" value={loc.lifestyle.schools} />
                <LSBar icon="medkit-outline" label="Hospitals" value={loc.lifestyle.hospitals} />
                <LSBar icon="bus-outline" label="Connectivity" value={loc.lifestyle.connectivity} />
                <LSBar icon="shield-outline" label="Safety" value={loc.lifestyle.safety} />
              </View>
              {loc.lifestyle.notes ? <Text style={styles.lsNotes}>{loc.lifestyle.notes}</Text> : null}
            </View>
          )}

          {/* Price chart */}
          <Text style={styles.sectionTitle}>Price History</Text>
          <View style={styles.chartCard}>
            <PriceChart data={loc.price_history || []} width={W - spacing.xl * 2 - 32} height={200} />
          </View>

          {/* Infrastructure timeline */}
          {(loc.infrastructure || []).length > 0 && (
            <>
              <Text style={styles.sectionTitle}>What's Being Built Here</Text>
              <View style={styles.timeline}>
                {loc.infrastructure.map((inf: any) => (
                  <View key={inf.id} style={styles.tRow}>
                    <View style={styles.tDot} />
                    <View style={{ flex: 1 }}>
                      <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start" }}>
                        <Text style={styles.tYear}>{inf.expected_completion}</Text>
                        <View style={styles.statusPill}>
                          <Text style={styles.statusText}>{inf.status}</Text>
                        </View>
                      </View>
                      <Text style={styles.tTitle}>{inf.name}</Text>
                      <Text style={styles.tSub}>{inf.type} · {inf.distance_km} km away</Text>
                      <Text style={styles.tDesc}>{inf.description}</Text>
                    </View>
                  </View>
                ))}
              </View>
            </>
          )}

          {/* News */}
          {(loc.news || []).length > 0 && (
            <>
              <Text style={styles.sectionTitle}>Locality News</Text>
              {loc.news.map((n: any) => (
                <View key={n.id} style={styles.newsCard}>
                  <View style={styles.newsTop}>
                    <View style={styles.newsBadge}><Text style={styles.newsBadgeText}>{n.category}</Text></View>
                    <Text style={styles.newsDate}>{new Date(n.date).toLocaleDateString("en-IN", { day: "2-digit", month: "short" })}</Text>
                  </View>
                  <Text style={styles.newsTitle}>{n.title}</Text>
                  <Text style={styles.newsSummary}>{n.summary}</Text>
                </View>
              ))}
            </>
          )}

          {/* Listings */}
          <Text style={styles.sectionTitle}>Properties in {loc.name}</Text>
          {props.map(p => <PropertyCard key={p.id} property={p} />)}
        </View>
      </ScrollView>
    </View>
  );
}

function Metric({ label, value, unit, tone }: { label: string; value: string; unit: string; tone?: "up" | "down" }) {
  return (
    <View style={styles.metric}>
      <Text style={styles.mLabel}>{label}</Text>
      <Text style={[styles.mValue, tone === "up" && { color: colors.success }, tone === "down" && { color: colors.error }]}>{value}</Text>
      <Text style={styles.mUnit}>{unit}</Text>
    </View>
  );
}

function LSBar({ icon, label, value }: { icon: string; label: string; value: number }) {
  return (
    <View>
      <View style={{ flexDirection: "row", alignItems: "center", gap: 6, marginBottom: 4 }}>
        <Icon name={icon as any} size={13} color={colors.onSurfaceSecondary} />
        <Text style={styles.lsLabel}>{label}</Text>
        <Text style={styles.lsValue}>{value}/100</Text>
      </View>
      <View style={styles.lsTrack}>
        <View style={[styles.lsFill, { width: `${value}%`, backgroundColor: scoreFg(value) }]} />
      </View>
    </View>
  );
}

function scoreFg(v: number): string {
  if (v >= 80) return "#2E6D4D";
  if (v >= 65) return "#C9A227";
  if (v >= 50) return "#C25934";
  return "#8B0000";
}
function scoreBg(v: number): string {
  if (v >= 80) return "rgba(46, 109, 77, 0.14)";
  if (v >= 65) return "rgba(201, 162, 39, 0.14)";
  if (v >= 50) return "rgba(194, 89, 52, 0.14)";
  return "rgba(139, 0, 0, 0.10)";
}

const styles = StyleSheet.create({
  hero: { width: W, height: 260, backgroundColor: colors.surfaceTertiary },
  heroOverlay: { position: "absolute", top: 0, left: 0, right: 0, bottom: 0, backgroundColor: "rgba(10,25,47,0.5)", width: W, height: 260 },
  iconBtn: { position: "absolute", width: 40, height: 40, borderRadius: 20, backgroundColor: "rgba(255,255,240,0.95)", alignItems: "center", justifyContent: "center", ...shadow.floating },
  followBtn: { position: "absolute", flexDirection: "row", alignItems: "center", gap: 4, paddingHorizontal: spacing.md, paddingVertical: 8, borderRadius: radius.pill, backgroundColor: colors.brandPrimary, ...shadow.floating },
  followBtnText: { color: colors.onBrandPrimary, fontWeight: "700", fontSize: 12 },
  heroText: { position: "absolute", left: spacing.xl, bottom: spacing.xl, right: spacing.xl },
  heroName: { color: "#FFFFF0", fontSize: 32, fontWeight: "700", letterSpacing: -0.5 },
  heroLoc: { color: "#F8F8F2", fontSize: 14, marginTop: 2 },
  heroSub: { color: colors.brandPrimary, fontSize: 11, marginTop: spacing.sm, fontWeight: "700", letterSpacing: 0.5, textTransform: "uppercase" },
  body: { padding: spacing.xl },
  metricsGrid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm },
  metric: { width: "48%", padding: spacing.md, backgroundColor: colors.surfaceSecondary, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border },
  mLabel: { fontSize: 10, fontWeight: "700", color: colors.muted, letterSpacing: 0.5, textTransform: "uppercase" },
  mValue: { fontSize: 20, fontWeight: "700", color: colors.onSurface, marginTop: 4, letterSpacing: -0.3 },
  mUnit: { fontSize: 11, color: colors.muted, fontWeight: "500" },
  ivCard: { marginTop: spacing.lg, padding: spacing.lg, backgroundColor: colors.brand, borderRadius: radius.lg },
  ivLabel: { color: colors.brandPrimary, fontSize: 11, fontWeight: "700", letterSpacing: 0.5, textTransform: "uppercase" },
  ivValue: { color: colors.onBrand, fontSize: 22, fontWeight: "700", marginTop: 4, letterSpacing: -0.3 },
  ivUnit: { color: "#B3BAC5", fontSize: 12, marginTop: 4, fontWeight: "500" },
  ivMeta: { color: "#B3BAC5", fontSize: 11, marginTop: spacing.md, lineHeight: 15 },
  sectionTitle: { fontSize: 16, fontWeight: "700", color: colors.onSurface, marginTop: spacing.xxl, marginBottom: spacing.md, letterSpacing: -0.2 },
  chartCard: { padding: spacing.md, backgroundColor: colors.surfaceSecondary, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border },
  gvCard: { padding: spacing.lg, backgroundColor: colors.surfaceSecondary, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border },
  gvRow: { flexDirection: "row", justifyContent: "space-between", paddingVertical: spacing.sm + 2, borderBottomWidth: 1, borderBottomColor: colors.divider },
  gvLabel: { color: colors.muted, fontSize: 13 },
  gvVal: { color: colors.onSurface, fontSize: 14, fontWeight: "700" },
  gvTip: { color: colors.muted, fontSize: 11, marginTop: spacing.md, lineHeight: 15 },
  timeline: { paddingLeft: spacing.sm },
  tRow: { flexDirection: "row", gap: spacing.md, marginBottom: spacing.lg },
  tDot: { width: 10, height: 10, borderRadius: 5, backgroundColor: colors.brandPrimary, marginTop: 6 },
  tYear: { fontSize: 11, fontWeight: "700", color: colors.brandPrimary, letterSpacing: 0.5 },
  statusPill: { backgroundColor: colors.brandTertiary, paddingHorizontal: 8, paddingVertical: 2, borderRadius: radius.pill },
  statusText: { fontSize: 10, fontWeight: "700", color: colors.brand },
  tTitle: { fontSize: 15, fontWeight: "700", color: colors.onSurface, marginTop: 2 },
  tSub: { fontSize: 12, color: colors.muted, marginTop: 2 },
  tDesc: { fontSize: 12, color: colors.onSurfaceSecondary, marginTop: 4, lineHeight: 17 },
  newsCard: { padding: spacing.md, backgroundColor: colors.surfaceSecondary, borderRadius: radius.md, marginBottom: spacing.sm, borderWidth: 1, borderColor: colors.border },
  newsTop: { flexDirection: "row", justifyContent: "space-between", marginBottom: 6 },
  newsBadge: { backgroundColor: colors.brandTertiary, paddingHorizontal: spacing.sm, paddingVertical: 2, borderRadius: radius.pill },
  newsBadgeText: { fontSize: 9, fontWeight: "700", color: colors.brand },
  newsDate: { fontSize: 11, color: colors.muted, fontWeight: "600" },
  newsTitle: { fontSize: 14, fontWeight: "700", color: colors.onSurface },
  newsSummary: { fontSize: 12, color: colors.onSurfaceSecondary, marginTop: 4, lineHeight: 17 },
  lsCard: { marginTop: spacing.md, backgroundColor: colors.surface, borderRadius: radius.lg, padding: spacing.lg, borderWidth: 1, borderColor: colors.border },
  lsHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  lsKicker: { fontSize: 10, fontWeight: "800", color: colors.muted, letterSpacing: 0.8 },
  lsTitle: { fontSize: 15, fontWeight: "700", color: colors.onSurface, marginTop: 4 },
  lsScorePill: { width: 56, height: 56, borderRadius: 28, alignItems: "center", justifyContent: "center" },
  lsScoreText: { fontSize: 22, fontWeight: "800" },
  lsLabel: { fontSize: 12, fontWeight: "700", color: colors.onSurface, flex: 1 },
  lsValue: { fontSize: 11, fontWeight: "800", color: colors.muted },
  lsTrack: { height: 6, borderRadius: 3, backgroundColor: colors.surfaceSecondary, overflow: "hidden" },
  lsFill: { height: 6, borderRadius: 3 },
  lsNotes: { fontSize: 11, color: colors.muted, marginTop: spacing.md, lineHeight: 16 },
  compareLocCta: { marginTop: spacing.md, flexDirection: "row", alignItems: "center", gap: 8, paddingHorizontal: spacing.md, paddingVertical: 12, borderRadius: radius.md, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border },
  compareLocTxt: { flex: 1, fontSize: 13, fontWeight: "700", color: colors.onSurface },
});
