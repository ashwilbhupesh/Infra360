import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, Pressable, Dimensions } from "react-native";
import { Image } from "expo-image";
import { useLocalSearchParams, useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";
import { useAuth } from "@/src/auth-context";
import { formatINR, indianComma, formatRange } from "@/src/utils/format";
import { openWhatsApp, openTel } from "@/src/utils/contact";
import { addHistory } from "@/src/utils/history";

const W = Dimensions.get("window").width;

export default function PropertyDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { user } = useAuth();
  const [prop, setProp] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);
  const [similar, setSimilar] = useState<any[]>([]);

  useEffect(() => {
    (async () => {
      try {
        const [p, sim] = await Promise.all([
          api.get(`/properties/${id}`),
          api.get<any[]>(`/properties/${id}/similar?limit=6`).catch(() => []),
        ]);
        setProp(p);
        setSimilar(sim);
        if (id) await addHistory(String(id));
      } finally { setLoading(false); }
    })();
  }, [id]);

  const toggleSave = async () => {
    if (!user) return;
    const res = await api.post<{ saved: boolean }>("/saved/toggle", { user_id: user.id, property_id: id });
    setSaved(res.saved);
  };

  if (loading || !prop) {
    return <View style={{ flex: 1, backgroundColor: colors.surface, alignItems: "center", justifyContent: "center" }}><ActivityIndicator color={colors.brand} /></View>;
  }

  const iv = prop.infravalue;
  const govt = prop.govt_value;

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <ScrollView contentContainerStyle={{ paddingBottom: 100 }} showsVerticalScrollIndicator={false}>
        <View>
          <Image source={{ uri: prop.images?.[0] }} style={styles.hero} contentFit="cover" />
          <Pressable testID="back-btn" onPress={() => router.back()} style={[styles.iconBtn, { top: insets.top + spacing.sm, left: spacing.lg }]}>
            <Icon name="chevron-back" size={20} color={colors.onSurface} />
          </Pressable>
          <Pressable testID="save-btn" onPress={toggleSave} style={[styles.iconBtn, { top: insets.top + spacing.sm, right: spacing.lg }]}>
            <Icon name={saved ? "heart" : "heart-outline"} size={20} color={saved ? colors.brandPrimary : colors.onSurface} />
          </Pressable>
        </View>

        <View style={styles.body}>
          <View style={styles.priceRow}>
            <Text style={styles.price}>{formatINR(prop.price)}</Text>
            {prop.verified && (
              <View style={styles.verifiedBadge}>
                <Icon name="checkmark-circle" size={12} color={colors.onSuccess} />
                <Text style={styles.verifiedText}>Verified</Text>
              </View>
            )}
          </View>
          <Text style={styles.title}>{prop.title}</Text>
          <Text style={styles.subline}>{prop.area} {prop.area_unit} · ₹{indianComma(prop.price_per_unit)}/{prop.area_unit.split(" ")[0]}</Text>
          <View style={styles.addressRow}>
            <Icon name="location-outline" size={14} color={colors.muted} />
            <Text style={styles.address}>{prop.address}</Text>
          </View>

          <Section title="InfraValue™ Estimate">
            <View style={styles.compareGrid}>
              <View style={[styles.compareCard, { backgroundColor: colors.surfaceSecondary }]}>
                <Text style={styles.cLabel}>Asking Price</Text>
                <Text style={styles.cValueSm}>{formatINR(prop.price)}</Text>
              </View>
              <View style={[styles.compareCard, { backgroundColor: colors.brandTertiary }]}>
                <Text style={[styles.cLabel, { color: colors.brand }]}>InfraValue™ Range</Text>
                <Text style={[styles.cValueSm, { color: colors.brand }]}>{iv ? formatRange(iv.low, iv.high) : "—"}</Text>
                <Text style={styles.confidence}>Confidence: {iv?.confidence || "—"}</Text>
              </View>
              <View style={[styles.compareCard, { backgroundColor: colors.surfaceSecondary }]}>
                <Text style={styles.cLabel}>Govt / DLC Value</Text>
                <Text style={styles.cValueSm}>{govt ? formatINR(govt) : "—"}</Text>
              </View>
            </View>
            <Text style={styles.disclaimer}>
              InfraValue is an estimated market range based on available listings, locality data and transaction indicators. Not a formal valuation.
            </Text>
          </Section>

          <Section title="Property Details">
            <Detail label="Type" value={prop.type} />
            <Detail label="Area" value={`${prop.area} ${prop.area_unit}`} />
            {prop.bedrooms ? <Detail label="Bedrooms" value={String(prop.bedrooms)} /> : null}
            {prop.facing ? <Detail label="Facing" value={prop.facing} /> : null}
            {prop.road_width_ft ? <Detail label="Road Width" value={`${prop.road_width_ft} ft`} /> : null}
            <Detail label="Listed By" value={prop.source} />
            <Detail label="Locality" value={prop.locality_name} />
          </Section>

          <Section title="Listed by">
            <Pressable
              testID="lister-card"
              onPress={() => prop.lister?.agent_id ? router.push(`/agent/${prop.lister.agent_id}` as any) : undefined}
              style={styles.listerCard}
            >
              <View style={styles.listerAvatar}>
                {prop.lister?.image ? (
                  <Image source={{ uri: prop.lister.image }} style={{ width: 48, height: 48, borderRadius: 24 }} contentFit="cover" />
                ) : (
                  <Icon name={prop.lister?.type === "Owner" ? "person-outline" : "briefcase-outline"} size={22} color={colors.brand} />
                )}
              </View>
              <View style={{ flex: 1 }}>
                <View style={{ flexDirection: "row", alignItems: "center", gap: 4 }}>
                  <Text style={styles.listerName}>{prop.lister?.name || prop.source}</Text>
                  {prop.lister?.verified && <Icon name="shield-checkmark" size={13} color={colors.success} />}
                </View>
                <Text style={styles.listerFirm}>
                  {prop.lister?.firm || prop.lister?.type || prop.source}
                  {prop.lister?.rera_id ? ` · RERA ${prop.lister.rera_id}` : ""}
                </Text>
                {prop.lister?.phone ? (
                  <Text style={styles.listerPhone}>{prop.lister.phone}</Text>
                ) : null}
              </View>
              {prop.lister?.agent_id ? <Icon name="chevron-forward" size={20} color={colors.muted} /> : null}
            </Pressable>
          </Section>

          <Section title="Locality">
            <Pressable
              testID="open-locality-btn"
              onPress={() => router.push(`/locality/${prop.locality_id}`)}
              style={styles.localityRow}
            >
              <View style={{ flex: 1 }}>
                <Text style={styles.locName}>{prop.locality?.name}</Text>
                <Text style={styles.locMeta}>
                  Median ₹{indianComma(prop.locality?.median_price_per_sq_yd || 0)}/sq yd · {prop.locality?.yoy_change_pct > 0 ? "+" : ""}{prop.locality?.yoy_change_pct}% YoY
                </Text>
              </View>
              <Icon name="chevron-forward" size={20} color={colors.muted} />
            </Pressable>
          </Section>

          {similar.length > 0 && (
            <Section title="Similar properties">
              <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: spacing.md, paddingRight: spacing.lg }}>
                {similar.map((sp: any) => (
                  <View key={sp.id} style={styles.simCard} testID={`similar-${sp.id}`}>
                    <Pressable onPress={() => router.push(`/property/${sp.id}` as any)}>
                      <Image source={{ uri: sp.images?.[0] }} style={styles.simImg} contentFit="cover" />
                      <View style={{ padding: spacing.md, paddingBottom: 6 }}>
                        <Text style={styles.simPrice}>{formatINR(sp.price)}</Text>
                        <Text style={styles.simTitle} numberOfLines={1}>{sp.title}</Text>
                        <Text style={styles.simAddr} numberOfLines={1}>{sp.address}</Text>
                      </View>
                    </Pressable>
                    <View style={styles.simActions}>
                      <Pressable
                        testID={`similar-show-on-map-${sp.id}`}
                        onPress={() => router.push({ pathname: "/(tabs)/explore", params: { highlight: sp.id, type: sp.type } } as any)}
                        style={styles.simMapBtn}
                      >
                        <Icon name="map-outline" size={12} color={colors.brand} />
                        <Text style={styles.simMapText}>Show on map</Text>
                      </Pressable>
                    </View>
                  </View>
                ))}
              </ScrollView>
            </Section>
          )}
        </View>
      </ScrollView>

      <View style={[styles.cta, { paddingBottom: insets.bottom + spacing.md }]}>
        <Pressable
          testID="whatsapp-btn"
          onPress={() => {
            const phone = prop.lister?.whatsapp || prop.lister?.phone;
            if (!phone) return;
            const msg = `Hi, I saw your listing "${prop.title}" (${formatINR(prop.price)}) on InfraJagat. Is it still available?`;
            openWhatsApp(phone, msg);
          }}
          style={[styles.iconCta, { backgroundColor: "#25D366" }]}
        >
          <Icon name="logo-whatsapp" size={22} color="#FFFFFF" />
        </Pressable>
        <Pressable
          testID="contact-btn"
          onPress={() => prop.lister?.phone && openTel(prop.lister.phone)}
          style={styles.ctaBtn}
        >
          <Icon name="call-outline" size={16} color={colors.onBrandPrimary} />
          <Text style={styles.ctaText}>Call {prop.lister?.name?.split(" ")[0] || prop.source}</Text>
        </Pressable>
      </View>
    </View>
  );
}

function Section({ title, children }: any) {
  return (
    <View style={{ marginTop: spacing.xl }}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {children}
    </View>
  );
}
function Detail({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.detailRow}>
      <Text style={styles.detailLabel}>{label}</Text>
      <Text style={styles.detailValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  hero: { width: W, height: 300, backgroundColor: colors.surfaceTertiary },
  iconBtn: { position: "absolute", width: 40, height: 40, borderRadius: 20, backgroundColor: "rgba(255,255,240,0.95)", alignItems: "center", justifyContent: "center", ...shadow.floating },
  body: { padding: spacing.xl },
  priceRow: { flexDirection: "row", alignItems: "center", gap: spacing.md },
  price: { fontSize: 32, fontWeight: "700", color: colors.brand, letterSpacing: -0.5 },
  verifiedBadge: { flexDirection: "row", alignItems: "center", gap: 4, backgroundColor: colors.success, paddingHorizontal: spacing.sm, paddingVertical: 3, borderRadius: radius.pill },
  verifiedText: { color: colors.onSuccess, fontSize: 10, fontWeight: "700" },
  title: { fontSize: 18, fontWeight: "600", color: colors.onSurface, marginTop: spacing.sm },
  subline: { color: colors.onSurfaceSecondary, marginTop: 4, fontSize: 14 },
  addressRow: { flexDirection: "row", alignItems: "center", gap: 4, marginTop: spacing.sm },
  address: { color: colors.muted, fontSize: 13 },
  sectionTitle: { fontSize: 16, fontWeight: "700", color: colors.onSurface, marginBottom: spacing.md, letterSpacing: -0.2 },
  compareGrid: { gap: spacing.sm },
  compareCard: { padding: spacing.lg, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border },
  cLabel: { fontSize: 11, fontWeight: "700", color: colors.muted, letterSpacing: 0.5, textTransform: "uppercase" },
  cValueSm: { fontSize: 20, fontWeight: "700", color: colors.onSurface, marginTop: 4, letterSpacing: -0.3 },
  confidence: { fontSize: 11, color: colors.brandPrimary, marginTop: 2, fontWeight: "600" },
  disclaimer: { fontSize: 11, color: colors.muted, marginTop: spacing.md, lineHeight: 16 },
  simCard: { width: 220, backgroundColor: colors.surface, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, overflow: "hidden" },
  simImg: { width: "100%", height: 120, backgroundColor: colors.surfaceSecondary },
  simPrice: { fontSize: 15, fontWeight: "800", color: colors.onSurface },
  simTitle: { fontSize: 12, fontWeight: "600", color: colors.onSurface, marginTop: 2 },
  simAddr: { fontSize: 10, color: colors.muted, marginTop: 2 },
  simActions: { paddingHorizontal: spacing.md, paddingBottom: spacing.md },
  simMapBtn: { flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 4, paddingVertical: 6, borderRadius: radius.pill, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surfaceSecondary },
  simMapText: { fontSize: 11, fontWeight: "700", color: colors.brand },
  detailRow: { flexDirection: "row", justifyContent: "space-between", paddingVertical: spacing.sm + 2, borderBottomWidth: 1, borderBottomColor: colors.divider },
  detailLabel: { color: colors.muted, fontSize: 13 },
  detailValue: { color: colors.onSurface, fontSize: 13, fontWeight: "600" },
  localityRow: { flexDirection: "row", alignItems: "center", padding: spacing.lg, backgroundColor: colors.surfaceSecondary, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border },
  locName: { fontSize: 15, fontWeight: "700", color: colors.onSurface },
  locMeta: { fontSize: 12, color: colors.muted, marginTop: 2 },
  cta: { position: "absolute", left: 0, right: 0, bottom: 0, padding: spacing.lg, backgroundColor: colors.surface, borderTopWidth: 1, borderTopColor: colors.border, flexDirection: "row", gap: spacing.sm },
  ctaBtn: { flex: 1, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: spacing.sm, backgroundColor: colors.brandPrimary, paddingVertical: spacing.md + 2, borderRadius: radius.md, ...shadow.card },
  ctaText: { color: colors.onBrandPrimary, fontWeight: "700", fontSize: 15 },
  iconCta: { width: 52, borderRadius: radius.md, alignItems: "center", justifyContent: "center" },
  listerCard: { flexDirection: "row", alignItems: "center", gap: spacing.md, padding: spacing.md, backgroundColor: colors.surfaceSecondary, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border },
  listerAvatar: { width: 48, height: 48, borderRadius: 24, backgroundColor: colors.surface, alignItems: "center", justifyContent: "center", overflow: "hidden" },
  listerName: { fontSize: 14, fontWeight: "700", color: colors.onSurface },
  listerFirm: { fontSize: 12, color: colors.muted, marginTop: 2 },
  listerPhone: { fontSize: 12, color: colors.brandPrimary, marginTop: 4, fontWeight: "700" },
});
