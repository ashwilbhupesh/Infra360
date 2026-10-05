import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, Pressable, Dimensions, TextInput } from "react-native";
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
  const [emi, setEmi] = useState<any>(null);
  const [emiCfg, setEmiCfg] = useState({ down: 20, rate: 8.75, years: 20, income: "" });
  const [aiVal, setAiVal] = useState<any>(null);
  const [aiLoading, setAiLoading] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const [p, sim] = await Promise.all([
          api.get<any>(`/properties/${id}`),
          api.get<any[]>(`/properties/${id}/similar?limit=6`).catch(() => []),
        ]);
        setProp(p);
        setSimilar(sim);
        if (id) await addHistory(String(id));
      } finally { setLoading(false); }
    })();
  }, [id]);

  // Fetch EMI quote reactively
  useEffect(() => {
    if (!prop) return;
    (async () => {
      try {
        const inc = parseFloat(emiCfg.income) || null;
        const res = await api.post<any>("/finance/emi", {
          price: prop.price,
          down_payment_pct: emiCfg.down,
          annual_rate_pct: emiCfg.rate,
          tenure_years: emiCfg.years,
          monthly_income: inc,
        });
        setEmi(res);
      } catch {}
    })();
  }, [prop, emiCfg]);

  const loadAI = async () => {
    if (!prop) return;
    setAiLoading(true);
    try {
      const res = await api.get<any>(`/properties/${prop.id}/ai-valuation`);
      setAiVal(res);
    } finally { setAiLoading(false); }
  };

  useEffect(() => { if (prop) loadAI(); /* eslint-disable-next-line */ }, [prop?.id]);

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

          {/* AI InfraValue */}
          <Section title="AI InfraValue">
            {aiLoading && !aiVal ? <ActivityIndicator color={colors.brand} /> : aiVal ? (
              <View style={styles.aiCard}>
                <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
                  <View style={styles.aiBadge}><Icon name="sparkles" size={11} color="#FFFFFF" /><Text style={styles.aiBadgeTxt}>AI</Text></View>
                  <Text style={styles.aiTitle}>Fair-value range</Text>
                  <View style={{ flex: 1 }} />
                  <View style={[styles.aiVerdict, aiVal.price_vs_fair === "under" && { backgroundColor: colors.success }, aiVal.price_vs_fair === "above" && { backgroundColor: colors.error }, aiVal.price_vs_fair === "within_range" && { backgroundColor: colors.brand }]}>
                    <Text style={styles.aiVerdictTxt}>
                      {aiVal.price_vs_fair === "under" ? "Below fair" : aiVal.price_vs_fair === "above" ? "Above fair" : "Within fair"}
                    </Text>
                  </View>
                </View>
                <Text style={styles.aiRange}>
                  {formatINR(aiVal.fair_value_low)}–{formatINR(aiVal.fair_value_high)}
                </Text>
                <Text style={styles.aiMeta}>Confidence: {aiVal.confidence} · Model: {aiVal.model}</Text>
                {!!(aiVal.key_factors?.length) && (
                  <View style={{ marginTop: spacing.md, gap: 6 }}>
                    <Text style={styles.aiHead}>Why this value</Text>
                    {aiVal.key_factors.map((f: string, i: number) => (
                      <View key={i} style={styles.aiRow}>
                        <Icon name="checkmark-circle" size={12} color={colors.success} />
                        <Text style={styles.aiTxt}>{f}</Text>
                      </View>
                    ))}
                  </View>
                )}
                {!!(aiVal.risks?.length) && (
                  <View style={{ marginTop: spacing.md, gap: 6 }}>
                    <Text style={styles.aiHead}>Risks to consider</Text>
                    {aiVal.risks.map((r: string, i: number) => (
                      <View key={i} style={styles.aiRow}>
                        <Icon name="alert-circle" size={12} color={colors.error} />
                        <Text style={styles.aiTxt}>{r}</Text>
                      </View>
                    ))}
                  </View>
                )}
              </View>
            ) : <Text style={{ color: colors.muted }}>Could not generate valuation.</Text>}
          </Section>

          {/* EMI Instant Quote */}
          <Section title="Home-loan EMI (instant quote)">
            <View style={styles.emiCard}>
              <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "flex-end" }}>
                <View>
                  <Text style={styles.emiLabel}>MONTHLY EMI</Text>
                  <Text style={styles.emiValue}>₹{indianComma(emi?.emi || 0)}</Text>
                </View>
                <View style={{ alignItems: "flex-end" }}>
                  <Text style={styles.emiLabel}>DOWN PAYMENT</Text>
                  <Text style={styles.emiSmall}>₹{indianComma(emi?.down_payment || 0)}</Text>
                </View>
              </View>
              <View style={styles.emiCfgRow}>
                <View style={styles.emiCfgCol}>
                  <Text style={styles.emiCfgLabel}>Down %</Text>
                  <View style={styles.emiPills}>
                    {[10, 20, 30, 40].map(v => (
                      <Pressable key={v} testID={`emi-down-${v}`} onPress={() => setEmiCfg(c => ({ ...c, down: v }))} style={[styles.emiPill, emiCfg.down === v && styles.emiPillActive]}>
                        <Text style={[styles.emiPillTxt, emiCfg.down === v && { color: colors.onBrandPrimary }]}>{v}%</Text>
                      </Pressable>
                    ))}
                  </View>
                </View>
              </View>
              <View style={styles.emiCfgRow}>
                <View style={styles.emiCfgCol}>
                  <Text style={styles.emiCfgLabel}>Tenure</Text>
                  <View style={styles.emiPills}>
                    {[10, 15, 20, 25].map(v => (
                      <Pressable key={v} testID={`emi-years-${v}`} onPress={() => setEmiCfg(c => ({ ...c, years: v }))} style={[styles.emiPill, emiCfg.years === v && styles.emiPillActive]}>
                        <Text style={[styles.emiPillTxt, emiCfg.years === v && { color: colors.onBrandPrimary }]}>{v}y</Text>
                      </Pressable>
                    ))}
                  </View>
                </View>
              </View>
              <View style={styles.emiInline}>
                <View style={{ flex: 1 }}>
                  <Text style={styles.emiCfgLabel}>Monthly income (optional)</Text>
                  <TextInput
                    testID="emi-income"
                    value={emiCfg.income}
                    onChangeText={v => setEmiCfg(c => ({ ...c, income: v.replace(/[^0-9]/g, "") }))}
                    placeholder="₹"
                    placeholderTextColor={colors.muted}
                    keyboardType="numeric"
                    style={styles.emiInput}
                  />
                </View>
              </View>
              {emi?.eligibility?.note ? (
                <Text style={[styles.emiNote, emi.eligibility.ok === false && { color: colors.error }, emi.eligibility.ok === true && { color: colors.success }]}>{emi.eligibility.note}</Text>
              ) : null}
              {Array.isArray(emi?.bank_offers) && emi.bank_offers.length > 0 && (
                <View style={{ marginTop: spacing.md }}>
                  <Text style={styles.emiCfgLabel}>Illustrative bank offers</Text>
                  <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 8, paddingTop: 6 }}>
                    {emi.bank_offers.map((b: any) => (
                      <View key={b.bank} style={styles.bankCard}>
                        <Text style={styles.bankName}>{b.bank}</Text>
                        <Text style={styles.bankRate}>{b.rate.toFixed(2)}% p.a.</Text>
                        <Text style={styles.bankEmi}>₹{indianComma(b.emi)} / mo</Text>
                      </View>
                    ))}
                  </ScrollView>
                </View>
              )}
            </View>
          </Section>

          {/* Owner tools: Promote / Verify */}
          {(prop.owner_user_id && prop.owner_user_id === user?.id) ? (
            <Section title="Your listing tools">
              <View style={{ flexDirection: "row", gap: 8 }}>
                <Pressable
                  testID="promote-listing-btn"
                  onPress={() => router.push(`/promote-listing?property_id=${prop.id}` as any)}
                  style={[styles.toolBtn, { backgroundColor: "#D4A72C" }]}
                >
                  <Icon name="rocket-outline" size={16} color="#FFFFFF" />
                  <Text style={[styles.toolTxt, { color: "#FFFFFF" }]}>Promote</Text>
                </Pressable>
                <Pressable
                  testID="verify-listing-btn"
                  onPress={() => router.push(`/verify-listing?property_id=${prop.id}` as any)}
                  style={[styles.toolBtn, { backgroundColor: colors.success }]}
                >
                  <Icon name="shield-checkmark-outline" size={16} color="#FFFFFF" />
                  <Text style={[styles.toolTxt, { color: "#FFFFFF" }]}>
                    {prop.verified ? "Verified" : prop.verification_status === "Pending Review" ? "Under review" : "Verify"}
                  </Text>
                </Pressable>
              </View>
            </Section>
          ) : null}


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
          onPress={async () => {
            const phone = prop.lister?.whatsapp || prop.lister?.phone;
            if (!phone) return;
            // Track lead (fire-and-forget)
            api.post(`/properties/${prop.id}/leads`, { user_id: user?.id, name: user?.name, mobile: user?.mobile, channel: "whatsapp" }).catch(() => {});
            const msg = `Hi, I saw your listing "${prop.title}" (${formatINR(prop.price)}) on InfraJagat. Is it still available?`;
            openWhatsApp(phone, msg);
          }}
          style={[styles.iconCta, { backgroundColor: "#25D366" }]}
        >
          <Icon name="logo-whatsapp" size={22} color="#FFFFFF" />
        </Pressable>
        <Pressable
          testID="contact-btn"
          onPress={() => {
            if (!prop.lister?.phone) return;
            api.post(`/properties/${prop.id}/leads`, { user_id: user?.id, name: user?.name, mobile: user?.mobile, channel: "call" }).catch(() => {});
            openTel(prop.lister.phone);
          }}
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
  // AI valuation
  aiCard: { padding: spacing.lg, borderRadius: radius.lg, borderWidth: 1, borderColor: "#C8DBF9", backgroundColor: "#F4F8FF" },
  aiBadge: { flexDirection: "row", alignItems: "center", gap: 3, paddingHorizontal: 8, paddingVertical: 3, borderRadius: radius.pill, backgroundColor: "#1E6FEB" },
  aiBadgeTxt: { color: "#FFFFFF", fontSize: 10, fontWeight: "800", letterSpacing: 0.3 },
  aiTitle: { fontSize: 13, fontWeight: "800", color: colors.onSurface },
  aiVerdict: { paddingHorizontal: 8, paddingVertical: 4, borderRadius: radius.pill },
  aiVerdictTxt: { color: "#FFFFFF", fontSize: 10, fontWeight: "800", letterSpacing: 0.3 },
  aiRange: { fontSize: 20, fontWeight: "800", color: colors.brand, marginTop: 8, letterSpacing: -0.3 },
  aiMeta: { fontSize: 11, color: colors.muted, marginTop: 4 },
  aiHead: { fontSize: 11, fontWeight: "800", color: colors.muted, letterSpacing: 0.6, textTransform: "uppercase" },
  aiRow: { flexDirection: "row", alignItems: "flex-start", gap: 6 },
  aiTxt: { flex: 1, fontSize: 12, color: colors.onSurface, lineHeight: 17 },
  // EMI card
  emiCard: { padding: spacing.lg, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surfaceSecondary, gap: 10 },
  emiLabel: { fontSize: 10, fontWeight: "800", color: colors.muted, letterSpacing: 0.6 },
  emiValue: { fontSize: 26, fontWeight: "800", color: colors.brandPrimary, marginTop: 4, letterSpacing: -0.5 },
  emiSmall: { fontSize: 16, fontWeight: "800", color: colors.onSurface, marginTop: 4 },
  emiCfgRow: { marginTop: 6 },
  emiCfgCol: {},
  emiCfgLabel: { fontSize: 11, fontWeight: "700", color: colors.muted, marginBottom: 4 },
  emiPills: { flexDirection: "row", gap: 6 },
  emiPill: { paddingHorizontal: 12, height: 32, borderRadius: radius.pill, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, alignItems: "center", justifyContent: "center" },
  emiPillActive: { backgroundColor: colors.brandPrimary, borderColor: colors.brandPrimary },
  emiPillTxt: { fontSize: 12, fontWeight: "700", color: colors.onSurface },
  emiInline: { flexDirection: "row", gap: 10 },
  emiInput: { height: 40, borderRadius: radius.md, backgroundColor: colors.surface, paddingHorizontal: spacing.md, borderWidth: 1, borderColor: colors.border, fontSize: 13, color: colors.onSurface },
  emiNote: { fontSize: 11, fontWeight: "700", marginTop: 2 },
  bankCard: { padding: 10, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, minWidth: 110 },
  bankName: { fontSize: 12, fontWeight: "800", color: colors.onSurface },
  bankRate: { fontSize: 11, color: colors.muted, marginTop: 2 },
  bankEmi: { fontSize: 13, fontWeight: "700", color: colors.brandPrimary, marginTop: 4 },
  // Tools
  toolBtn: { flex: 1, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 6, paddingVertical: 12, borderRadius: radius.md },
  toolTxt: { fontSize: 13, fontWeight: "800" },
});
