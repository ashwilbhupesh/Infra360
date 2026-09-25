// Airbnb-style pin preview card - shown when a map pin is tapped.
// Displays hero image, price, quick details, InfraValue vs Govt DLC,
// listed-by mini card, similar properties strip, and a "View full details" CTA.
import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, Pressable, ScrollView, ActivityIndicator } from "react-native";
import { Image } from "expo-image";
import { useRouter } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";
import { formatINR, indianComma } from "@/src/utils/format";
import { openWhatsApp, openTel } from "@/src/utils/contact";

export type PropertyLite = {
  id: string; title: string; type: string; price: number; area: number; area_unit: string;
  price_per_unit: number; bedrooms?: number | null; address: string; locality_name: string;
  images: string[]; verified?: boolean; source: string;
};

type Full = PropertyLite & {
  infravalue?: { low: number; high: number; confidence: string };
  govt_value?: number;
  lister?: { name?: string; firm?: string; phone?: string; whatsapp?: string; image?: string; agent_id?: string | null; rera_id?: string | null; verified?: boolean };
  locality_id?: string;
};

export function PinPreview({ propertyId, onClose }: { propertyId: string; onClose?: () => void }) {
  const router = useRouter();
  const [prop, setProp] = useState<Full | null>(null);
  const [similar, setSimilar] = useState<PropertyLite[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    (async () => {
      try {
        const [p, sim] = await Promise.all([
          api.get<Full>(`/properties/${propertyId}`),
          api.get<PropertyLite[]>(`/properties/${propertyId}/similar?limit=6`).catch(() => [] as PropertyLite[]),
        ]);
        setProp(p);
        setSimilar(sim);
      } finally { setLoading(false); }
    })();
  }, [propertyId]);

  if (loading || !prop) {
    return (
      <View style={{ padding: spacing.xl, alignItems: "center" }}>
        <ActivityIndicator color={colors.brand} />
      </View>
    );
  }

  const iv = prop.infravalue;
  const mid = iv ? (iv.low + iv.high) / 2 : null;
  const isDeal = mid !== null && prop.price < mid * 0.97;

  return (
    <View style={{ paddingBottom: spacing.md }}>
      <View style={styles.header}>
        <Text style={styles.kicker}>SELECTED PROPERTY</Text>
        {onClose && (
          <Pressable testID="pin-preview-close" onPress={onClose} hitSlop={10}>
            <Icon name="close" size={20} color={colors.muted} />
          </Pressable>
        )}
      </View>

      <View style={styles.heroWrap}>
        <Image source={{ uri: prop.images?.[0] }} style={styles.hero} contentFit="cover" transition={200} />
        {isDeal && (
          <View style={styles.dealRibbon}>
            <Icon name="flash" size={11} color={colors.onBrandPrimary} />
            <Text style={styles.dealText}>Below InfraValue</Text>
          </View>
        )}
        {prop.verified && (
          <View style={styles.verifiedPill}>
            <Icon name="shield-checkmark" size={11} color={colors.onBrandPrimary} />
            <Text style={styles.verifiedText}>Verified</Text>
          </View>
        )}
      </View>

      <View style={styles.body}>
        <Text style={styles.price}>{formatINR(prop.price)}</Text>
        <Text style={styles.title} numberOfLines={1}>{prop.title}</Text>
        <Text style={styles.meta}>
          {prop.area} {prop.area_unit} · {`₹${indianComma(prop.price_per_unit)}/${prop.area_unit.split(" ")[0]}`}
          {prop.bedrooms ? ` · ${prop.bedrooms} BHK` : ""}
        </Text>
        <View style={styles.addressRow}>
          <Icon name="location-outline" size={13} color={colors.muted} />
          <Text style={styles.address} numberOfLines={1}>{prop.address}</Text>
        </View>

        <View style={styles.compareRow}>
          <View style={styles.compareCell}>
            <Text style={styles.cLabel}>ASKING</Text>
            <Text style={styles.cVal}>{formatINR(prop.price)}</Text>
          </View>
          <View style={styles.compareCell}>
            <Text style={[styles.cLabel, { color: colors.brandPrimary }]}>INFRAVALUE™</Text>
            <Text style={[styles.cVal, { color: colors.brandPrimary }]}>{iv ? `${formatINR(iv.low)}–${formatINR(iv.high)}` : "—"}</Text>
          </View>
          <View style={styles.compareCell}>
            <Text style={styles.cLabel}>GOVT / DLC</Text>
            <Text style={styles.cVal}>{prop.govt_value ? formatINR(prop.govt_value) : "—"}</Text>
          </View>
        </View>

        {prop.lister ? (
          <View style={styles.listerRow}>
            <View style={styles.listerAvatar}>
              {prop.lister.image ? (
                <Image source={{ uri: prop.lister.image }} style={{ width: 34, height: 34, borderRadius: 17 }} />
              ) : (
                <Icon name={prop.lister.name?.startsWith("Owner") ? "person-outline" : "briefcase-outline"} size={16} color={colors.brand} />
              )}
            </View>
            <View style={{ flex: 1 }}>
              <View style={{ flexDirection: "row", alignItems: "center", gap: 4 }}>
                <Text style={styles.listerName} numberOfLines={1}>{prop.lister.name || prop.source}</Text>
                {prop.lister.verified && <Icon name="shield-checkmark" size={11} color={colors.success} />}
              </View>
              <Text style={styles.listerSub} numberOfLines={1}>
                {prop.lister.firm || "Direct listing"}{prop.lister.rera_id ? ` · RERA ${prop.lister.rera_id}` : ""}
              </Text>
            </View>
            {prop.lister.phone ? (
              <View style={{ flexDirection: "row", gap: 6 }}>
                <Pressable testID="pin-wa-btn" onPress={() => prop.lister?.phone && openWhatsApp(prop.lister.whatsapp || prop.lister.phone, `Hi, I'm interested in "${prop.title}" (${formatINR(prop.price)}) on InfraLocal.`)} style={[styles.miniBtn, { backgroundColor: "#25D366" }]}>
                  <Icon name="logo-whatsapp" size={14} color="#FFFFFF" />
                </Pressable>
                <Pressable testID="pin-call-btn" onPress={() => prop.lister?.phone && openTel(prop.lister.phone)} style={[styles.miniBtn, { backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border }]}>
                  <Icon name="call-outline" size={14} color={colors.onSurface} />
                </Pressable>
              </View>
            ) : null}
          </View>
        ) : null}

        <Pressable
          testID="pin-view-full-btn"
          onPress={() => router.push(`/property/${prop.id}` as any)}
          style={styles.fullBtn}
        >
          <Text style={styles.fullBtnText}>View full details</Text>
          <Icon name="arrow-forward" size={16} color={colors.onBrandPrimary} />
        </Pressable>

        {similar.length > 0 && (
          <View style={{ marginTop: spacing.lg }}>
            <Text style={styles.simTitle}>Similar properties</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: spacing.md, paddingVertical: spacing.sm }}>
              {similar.map(s => (
                <Pressable
                  key={s.id}
                  testID={`similar-${s.id}`}
                  onPress={() => router.push(`/property/${s.id}` as any)}
                  style={styles.simCard}
                >
                  <Image source={{ uri: s.images?.[0] }} style={styles.simImg} contentFit="cover" />
                  <View style={{ padding: spacing.sm }}>
                    <Text style={styles.simPrice}>{formatINR(s.price)}</Text>
                    <Text style={styles.simMeta} numberOfLines={1}>{s.area} {s.area_unit} · {s.type}</Text>
                    <Text style={styles.simAddr} numberOfLines={1}>{s.locality_name}</Text>
                  </View>
                </Pressable>
              ))}
            </ScrollView>
          </View>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingHorizontal: spacing.lg, marginBottom: spacing.sm },
  kicker: { fontSize: 10, fontWeight: "800", color: colors.brandPrimary, letterSpacing: 0.8 },
  heroWrap: { marginHorizontal: spacing.lg, borderRadius: radius.md, overflow: "hidden", backgroundColor: colors.surfaceSecondary },
  hero: { width: "100%", height: 160 },
  dealRibbon: { position: "absolute", left: 10, top: 10, flexDirection: "row", alignItems: "center", gap: 3, backgroundColor: colors.brandPrimary, paddingHorizontal: 8, paddingVertical: 4, borderRadius: radius.pill },
  dealText: { color: colors.onBrandPrimary, fontSize: 10, fontWeight: "800", letterSpacing: 0.3 },
  verifiedPill: { position: "absolute", right: 10, top: 10, flexDirection: "row", alignItems: "center", gap: 3, backgroundColor: colors.success, paddingHorizontal: 8, paddingVertical: 4, borderRadius: radius.pill },
  verifiedText: { color: colors.onBrandPrimary, fontSize: 10, fontWeight: "700", letterSpacing: 0.3 },
  body: { paddingHorizontal: spacing.lg, paddingTop: spacing.md },
  price: { fontSize: 24, fontWeight: "800", color: colors.brand, letterSpacing: -0.3 },
  title: { fontSize: 15, fontWeight: "700", color: colors.onSurface, marginTop: 2 },
  meta: { fontSize: 12, color: colors.onSurfaceSecondary, marginTop: 4 },
  addressRow: { flexDirection: "row", alignItems: "center", gap: 4, marginTop: 4 },
  address: { fontSize: 12, color: colors.muted, flex: 1 },
  compareRow: { flexDirection: "row", marginTop: spacing.md, backgroundColor: colors.surfaceSecondary, borderRadius: radius.md, padding: spacing.sm },
  compareCell: { flex: 1, paddingHorizontal: 6 },
  cLabel: { fontSize: 9, fontWeight: "800", color: colors.muted, letterSpacing: 0.5 },
  cVal: { fontSize: 12, fontWeight: "800", color: colors.onSurface, marginTop: 3 },
  listerRow: { flexDirection: "row", alignItems: "center", gap: spacing.sm, marginTop: spacing.md, padding: spacing.sm, backgroundColor: colors.surfaceSecondary, borderRadius: radius.md },
  listerAvatar: { width: 34, height: 34, borderRadius: 17, backgroundColor: colors.surface, alignItems: "center", justifyContent: "center", overflow: "hidden" },
  listerName: { fontSize: 13, fontWeight: "700", color: colors.onSurface },
  listerSub: { fontSize: 11, color: colors.muted, marginTop: 2 },
  miniBtn: { width: 32, height: 32, borderRadius: 16, alignItems: "center", justifyContent: "center" },
  fullBtn: { flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 6, marginTop: spacing.md, height: 44, borderRadius: radius.md, backgroundColor: colors.brandPrimary, ...shadow.card },
  fullBtnText: { color: colors.onBrandPrimary, fontWeight: "700", fontSize: 14 },
  simTitle: { fontSize: 13, fontWeight: "800", color: colors.muted, letterSpacing: 0.8 },
  simCard: { width: 200, borderRadius: radius.md, backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, overflow: "hidden" },
  simImg: { width: "100%", height: 100 },
  simPrice: { fontSize: 14, fontWeight: "800", color: colors.onSurface },
  simMeta: { fontSize: 11, color: colors.muted, marginTop: 2 },
  simAddr: { fontSize: 10, color: colors.muted, marginTop: 2 },
});
