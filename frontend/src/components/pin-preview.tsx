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
import { useAuth } from "@/src/auth-context";
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
  const { user } = useAuth();
  const [prop, setProp] = useState<Full | null>(null);
  const [similar, setSimilar] = useState<PropertyLite[]>([]);
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);

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
        if (user) {
          const list = await api.get<Array<{ property_id: string }>>(`/saved?user_id=${user.id}`).catch(() => []);
          setSaved(list.some(x => x.property_id === propertyId));
        }
      } finally { setLoading(false); }
    })();
  }, [propertyId, user]);

  const toggleSave = async () => {
    if (!user) return;
    const prev = saved;
    setSaved(!prev);
    try {
      await api.post<{ saved: boolean }>("/saved/toggle", { user_id: user.id, property_id: propertyId });
    } catch { setSaved(prev); }
  };

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
        <View style={{ flex: 1 }} />
        <Pressable
          testID="pin-preview-like"
          onPress={toggleSave}
          disabled={!user}
          hitSlop={10}
          style={[styles.likeBtn, !user && { opacity: 0.5 }]}
          accessibilityLabel={saved ? "Remove from saved" : "Save property"}
        >
          <Icon name={saved ? "heart" : "heart-outline"} size={20} color={saved ? colors.error : colors.onSurface} />
        </Pressable>
      </View>

      <View style={styles.heroWrap}>
        <Image source={{ uri: prop.images?.[0] }} style={styles.hero} contentFit="cover" transition={200} />
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
                <Pressable testID="pin-wa-btn" onPress={() => prop.lister?.phone && openWhatsApp(prop.lister.whatsapp || prop.lister.phone, `Hi, I'm interested in "${prop.title}" (${formatINR(prop.price)}) on InfraJagat.`)} style={[styles.miniBtn, { backgroundColor: "#25D366" }]}>
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
                <View
                  key={s.id}
                  testID={`similar-${s.id}`}
                  style={styles.simCard}
                >
                  <Pressable onPress={() => router.push(`/property/${s.id}` as any)}>
                    <Image source={{ uri: s.images?.[0] }} style={styles.simImg} contentFit="cover" />
                    <View style={{ padding: spacing.sm }}>
                      <Text style={styles.simPrice}>{formatINR(s.price)}</Text>
                      <Text style={styles.simMeta} numberOfLines={1}>{s.area} {s.area_unit} · {s.type}</Text>
                      <Text style={styles.simAddr} numberOfLines={1}>{s.locality_name}</Text>
                    </View>
                  </Pressable>
                  <Pressable
                    testID={`similar-show-on-map-${s.id}`}
                    onPress={() => {
                      onClose?.();
                      router.push({ pathname: "/(tabs)/explore", params: { highlight: s.id, type: s.type } } as any);
                    }}
                    style={styles.simMapBtn}
                  >
                    <Icon name="map-outline" size={11} color={colors.brand} />
                    <Text style={styles.simMapText}>Show on map</Text>
                  </Pressable>
                </View>
              ))}
            </ScrollView>
          </View>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingHorizontal: spacing.lg, paddingBottom: 6 },
  kicker: { fontSize: 10, fontWeight: "800", color: colors.brandPrimary, letterSpacing: 0.8 },
  likeBtn: { width: 36, height: 36, borderRadius: 18, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border, alignItems: "center", justifyContent: "center" },
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
  simMapBtn: { flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 4, marginHorizontal: spacing.sm, marginBottom: spacing.sm, paddingVertical: 6, borderRadius: radius.pill, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surfaceSecondary },
  simMapText: { fontSize: 10, fontWeight: "700", color: colors.brand },
});
