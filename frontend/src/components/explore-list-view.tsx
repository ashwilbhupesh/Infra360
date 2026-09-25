import React, { useEffect, useMemo, useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, ActivityIndicator } from "react-native";
import { Image } from "expo-image";
import { useRouter } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius } from "@/src/theme";
import { api } from "@/src/api";
import { PropertyCard, Property } from "@/src/components/property-card";
import { formatINR, indianComma } from "@/src/utils/format";
import { heatColor } from "@/src/utils/heat";

type Locality = {
  id: string; name: string; city: string; image: string; median_price_per_sq_yd: number;
  govt_dlc_per_sq_yd: number; yoy_change_pct: number; listings_count: number; confidence: string;
  lifestyle?: { overall: number };
};

export function ExploreListView({ items, filter }: { items: Property[]; filter: string }) {
  const router = useRouter();
  const [localities, setLocalities] = useState<Locality[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const l = await api.get<Locality[]>("/localities");
        setLocalities(l);
      } finally { setLoading(false); }
    })();
  }, []);

  const bestDeals = useMemo(() =>
    items.filter(p => (p as any).price_per_unit && (p as any).price_per_unit < 12000).slice(0, 6),
    [items]
  );
  const verified = useMemo(() => items.filter(p => p.verified).slice(0, 6), [items]);
  const under50 = useMemo(() => items.filter(p => p.price <= 5000000).slice(0, 6), [items]);
  const plotsUnder80 = useMemo(() => items.filter(p => p.type === "Residential Plot" && p.price <= 8000000).slice(0, 6), [items]);
  const readyToMove = useMemo(() =>
    items.filter(p => (p.type === "Apartment" || p.type === "Villa") && p.verified).slice(0, 6),
    [items]
  );

  const trending = useMemo(() =>
    [...localities].sort((a, b) => (b.yoy_change_pct ?? 0) - (a.yoy_change_pct ?? 0)).slice(0, 5),
    [localities]
  );

  if (loading) {
    return <ActivityIndicator color={colors.brand} style={{ marginTop: spacing.xxl }} />;
  }

  return (
    <ScrollView contentContainerStyle={{ paddingBottom: 140, paddingTop: spacing.md }} showsVerticalScrollIndicator={false}>
      {/* Trending areas — with quick analysis */}
      <Section
        title="Trending areas in Jaipur"
        subtitle="Sorted by 1-year asking price movement"
      >
        {trending.map(l => (
          <Pressable
            key={l.id}
            testID={`list-trending-${l.id}`}
            onPress={() => router.push(`/locality/${l.id}` as any)}
            style={styles.trendCard}
          >
            <Image source={{ uri: l.image }} style={styles.trendImg} contentFit="cover" />
            <View style={{ flex: 1 }}>
              <Text style={styles.trendName}>{l.name}</Text>
              <Text style={styles.trendMeta}>Median ₹{indianComma(l.median_price_per_sq_yd)}/sq yd · DLC ₹{indianComma(l.govt_dlc_per_sq_yd)}</Text>
              <View style={styles.trendRow}>
                <View style={[styles.yoyPill, { backgroundColor: l.yoy_change_pct >= 0 ? "rgba(46,109,77,0.14)" : "rgba(139,0,0,0.10)" }]}>
                  <Icon name={l.yoy_change_pct >= 0 ? "trending-up" : "trending-down"} size={11} color={l.yoy_change_pct >= 0 ? colors.success : colors.error} />
                  <Text style={[styles.yoyText, { color: l.yoy_change_pct >= 0 ? colors.success : colors.error }]}>{l.yoy_change_pct > 0 ? "+" : ""}{l.yoy_change_pct}% YoY</Text>
                </View>
                {l.lifestyle?.overall != null && (
                  <View style={styles.lifestylePill}>
                    <Icon name="leaf-outline" size={10} color={colors.brand} />
                    <Text style={styles.lifestyleText}>Lifestyle {l.lifestyle.overall}</Text>
                  </View>
                )}
                <View style={styles.confPill}><Text style={styles.confText}>{l.confidence}</Text></View>
              </View>
            </View>
            <Icon name="chevron-forward" size={18} color={colors.muted} />
          </Pressable>
        ))}
      </Section>

      {/* Best deals below InfraValue */}
      {bestDeals.length > 0 && (
        <Section title="Best deals" subtitle="Under ₹12,000/sq yd or priced below the InfraValue midpoint" carousel>
          {bestDeals.map(p => <SmallCard key={p.id} property={p} />)}
        </Section>
      )}

      {/* Verified spotlight */}
      {verified.length > 0 && (
        <Section title="Verified spotlight" subtitle="Listings screened by InfraLocal" carousel>
          {verified.map(p => <SmallCard key={p.id} property={p} />)}
        </Section>
      )}

      {/* Under 50L */}
      {under50.length > 0 && (
        <Section title="Under ₹50 L" subtitle="Great starter homes and plots" carousel>
          {under50.map(p => <SmallCard key={p.id} property={p} />)}
        </Section>
      )}

      {/* Plots under 80L */}
      {plotsUnder80.length > 0 && (
        <Section title="Plots under ₹80 L" subtitle="Handpicked residential and agri plots" carousel>
          {plotsUnder80.map(p => <SmallCard key={p.id} property={p} />)}
        </Section>
      )}

      {/* Ready to move */}
      {readyToMove.length > 0 && (
        <Section title="Ready to move" subtitle="Apartments and villas ready for possession" carousel>
          {readyToMove.map(p => <SmallCard key={p.id} property={p} />)}
        </Section>
      )}

      {/* All listings */}
      <Section title={filter ? `All ${filter}s` : "All properties"} subtitle={`${items.length} listings`}>
        {items.slice(0, 20).map(p => <PropertyCard key={p.id} property={p} />)}
      </Section>
    </ScrollView>
  );
}

function Section({ title, subtitle, children, carousel }: { title: string; subtitle?: string; children: React.ReactNode; carousel?: boolean }) {
  return (
    <View style={{ marginBottom: spacing.xl }}>
      <View style={{ paddingHorizontal: spacing.lg, marginBottom: spacing.sm }}>
        <Text style={styles.secTitle}>{title}</Text>
        {subtitle ? <Text style={styles.secSub}>{subtitle}</Text> : null}
      </View>
      {carousel ? (
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: spacing.md, paddingHorizontal: spacing.lg }}>
          {children}
        </ScrollView>
      ) : (
        <View style={{ paddingHorizontal: spacing.lg }}>{children}</View>
      )}
    </View>
  );
}

function SmallCard({ property }: { property: Property }) {
  const router = useRouter();
  return (
    <Pressable
      testID={`small-card-${property.id}`}
      onPress={() => router.push(`/property/${property.id}` as any)}
      style={styles.smallCard}
    >
      <Image source={{ uri: property.images?.[0] }} style={styles.smallImg} contentFit="cover" />
      {property.verified ? (
        <View style={styles.smallVerified}>
          <Icon name="shield-checkmark" size={10} color={colors.onBrandPrimary} />
          <Text style={styles.smallVerifiedText}>Verified</Text>
        </View>
      ) : null}
      <View style={{ padding: spacing.sm }}>
        <Text style={styles.smallPrice}>{formatINR(property.price)}</Text>
        <Text style={styles.smallTitle} numberOfLines={1}>{property.title}</Text>
        <Text style={styles.smallMeta} numberOfLines={1}>{property.area} {property.area_unit} · {property.locality_name}</Text>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  secTitle: { fontSize: 18, fontWeight: "800", color: colors.onSurface, letterSpacing: -0.2 },
  secSub: { fontSize: 12, color: colors.muted, marginTop: 2 },
  trendCard: { flexDirection: "row", alignItems: "center", gap: spacing.md, padding: spacing.sm, marginBottom: spacing.sm, backgroundColor: colors.surface, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border },
  trendImg: { width: 60, height: 60, borderRadius: radius.md, backgroundColor: colors.surfaceSecondary },
  trendName: { fontSize: 14, fontWeight: "700", color: colors.onSurface },
  trendMeta: { fontSize: 11, color: colors.muted, marginTop: 2 },
  trendRow: { flexDirection: "row", gap: 6, marginTop: 6, flexWrap: "wrap" },
  yoyPill: { flexDirection: "row", alignItems: "center", gap: 3, paddingHorizontal: 6, paddingVertical: 2, borderRadius: radius.pill },
  yoyText: { fontSize: 10, fontWeight: "800", letterSpacing: 0.3 },
  lifestylePill: { flexDirection: "row", alignItems: "center", gap: 3, paddingHorizontal: 6, paddingVertical: 2, borderRadius: radius.pill, backgroundColor: colors.brandTertiary },
  lifestyleText: { fontSize: 10, fontWeight: "800", color: colors.brand, letterSpacing: 0.3 },
  confPill: { paddingHorizontal: 6, paddingVertical: 2, borderRadius: radius.pill, backgroundColor: colors.surfaceSecondary },
  confText: { fontSize: 10, fontWeight: "800", color: colors.muted, letterSpacing: 0.5 },
  smallCard: { width: 200, borderRadius: radius.md, backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, overflow: "hidden" },
  smallImg: { width: "100%", height: 110, backgroundColor: colors.surfaceSecondary },
  smallVerified: { position: "absolute", left: 8, top: 8, flexDirection: "row", alignItems: "center", gap: 3, backgroundColor: colors.success, paddingHorizontal: 6, paddingVertical: 2, borderRadius: radius.pill },
  smallVerifiedText: { color: colors.onBrandPrimary, fontSize: 9, fontWeight: "800", letterSpacing: 0.3 },
  smallPrice: { fontSize: 15, fontWeight: "800", color: colors.onSurface, letterSpacing: -0.2 },
  smallTitle: { fontSize: 12, fontWeight: "700", color: colors.onSurface, marginTop: 2 },
  smallMeta: { fontSize: 10, color: colors.muted, marginTop: 2 },
});
