import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, ActivityIndicator, TextInput, KeyboardAvoidingView, Platform } from "react-native";
import { Image } from "expo-image";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useLocalSearchParams, useRouter, Stack } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";
import { useAuth } from "@/src/auth-context";
import { openWhatsApp, openTel } from "@/src/utils/contact";
import { formatINR } from "@/src/utils/format";
import { tierColor, tierBgColor } from "@/src/utils/tier";

type Agent = {
  id: string; category_id: string; name: string; firm?: string; city: string; area: string;
  rating: number; reviews: number; verified: boolean; featured: boolean;
  years_exp: number; languages: string[]; specialties: string[]; coverage: string[];
  rera_id?: string | null; phone: string; whatsapp?: string; image: string; about: string;
  tier?: string;
  category?: { name: string };
  recent_listings?: Array<{ id: string; title: string; price: number; area: number; area_unit: string; images: string[]; type: string }>;
};

export default function AgentDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { user } = useAuth();
  const [a, setA] = useState<Agent | null>(null);
  const [analytics, setAnalytics] = useState<any>(null);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [loading, setLoading] = useState(true);
  const [showEnquiry, setShowEnquiry] = useState(false);
  const [name, setName] = useState(user?.name ?? "");
  const [mobile, setMobile] = useState(user?.mobile ?? "");
  const [msg, setMsg] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const data = await api.get<Agent>(`/agents/${id}`);
        setA(data);
        // Prefetch analytics (tier-gated)
        api.get<any>(`/agents/${id}/analytics`).then(setAnalytics).catch(() => {});
      } finally { setLoading(false); }
    })();
  }, [id]);

  const submit = async () => {
    if (!name.trim() || mobile.trim().length < 10) return;
    setSubmitting(true);
    try {
      await api.post(`/agents/${id}/enquiries`, { agent_id: id, user_id: user?.id, name: name.trim(), mobile: mobile.trim(), message: msg.trim() || undefined });
      setSubmitted(true);
    } finally { setSubmitting(false); }
  };

  if (loading || !a) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.surface, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator color={colors.brand} />
      </View>
    );
  }

  const waMsg = `Hi ${a.name}, I found you on InfraJagat and would like to talk about a property.`;

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <Stack.Screen options={{ headerShown: false }} />
      <ScrollView contentContainerStyle={{ paddingBottom: 120 }}>
        <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
          <Pressable testID="agent-back-btn" onPress={() => router.back()} hitSlop={12}>
            <Icon name="chevron-back" size={26} color={colors.onSurface} />
          </Pressable>
        </View>

        <View style={styles.heroBlock}>
          <Image source={{ uri: a.image }} style={styles.avatar} contentFit="cover" transition={200} />
          <View style={{ flexDirection: "row", alignItems: "center", gap: 6, marginTop: spacing.md }}>
            <Text style={styles.name}>{a.name}</Text>
            {a.verified && <Icon name="shield-checkmark" size={18} color={colors.success} />}
          </View>
          {a.firm ? <Text style={styles.firm}>{a.firm}</Text> : null}
          {a.category?.name ? (
            <View style={styles.catBadge}><Text style={styles.catBadgeText}>{a.category.name}</Text></View>
          ) : null}
          {a.tier && a.tier !== "Unverified" && (
            <View style={[styles.tierBadgeBig, { backgroundColor: tierBgColor(a.tier), borderColor: tierColor(a.tier) }]}>
              <Icon name="ribbon" size={14} color={tierColor(a.tier)} />
              <Text style={[styles.tierBadgeText, { color: tierColor(a.tier) }]}>{a.tier} verified agent</Text>
            </View>
          )}

          <View style={styles.statsRow}>
            <View style={styles.statCol}>
              <Text style={styles.statValue}>{a.rating.toFixed(1)}</Text>
              <Text style={styles.statLabel}>rating</Text>
            </View>
            <View style={styles.statDivider} />
            <View style={styles.statCol}>
              <Text style={styles.statValue}>{a.reviews}</Text>
              <Text style={styles.statLabel}>reviews</Text>
            </View>
            <View style={styles.statDivider} />
            <View style={styles.statCol}>
              <Text style={styles.statValue}>{a.years_exp}</Text>
              <Text style={styles.statLabel}>years</Text>
            </View>
          </View>

          {a.rera_id ? (
            <View style={styles.reraRow}>
              <Icon name="ribbon-outline" size={14} color={colors.brandPrimary} />
              <Text style={styles.reraText}>RERA · {a.rera_id}</Text>
            </View>
          ) : null}
        </View>

        <View style={{ padding: spacing.xl, paddingTop: 0 }}>
          <Text style={styles.sectionTitle}>About</Text>
          <Text style={styles.about}>{a.about}</Text>

          <Text style={styles.sectionTitle}>Specialties</Text>
          <View style={styles.pillsRow}>
            {a.specialties.map(s => (
              <View key={s} style={styles.pill}><Text style={styles.pillText}>{s}</Text></View>
            ))}
          </View>

          <Text style={styles.sectionTitle}>Coverage</Text>
          <View style={styles.pillsRow}>
            {a.coverage.map(s => (
              <View key={s} style={[styles.pill, { backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border }]}>
                <Icon name="location-outline" size={11} color={colors.muted} />
                <Text style={styles.pillText}>{s}</Text>
              </View>
            ))}
          </View>

          {a.languages?.length ? (
            <>
              <Text style={styles.sectionTitle}>Languages</Text>
              <Text style={styles.about}>{a.languages.join(" · ")}</Text>
            </>
          ) : null}

          {analytics && (
            <>
              <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginTop: spacing.xxl }}>
                <Text style={[styles.sectionTitle, { marginTop: 0 }]}>Live performance</Text>
                <Pressable testID="analytics-toggle" onPress={() => setShowAnalytics(v => !v)} hitSlop={10}>
                  <Icon name={showAnalytics ? "chevron-up" : "chevron-down"} size={18} color={colors.muted} />
                </Pressable>
              </View>
              <View style={styles.analyticsSummary}>
                <View style={styles.anaStat}><Text style={styles.anaValue}>{analytics.metrics?.views_30d ?? 0}</Text><Text style={styles.anaLabel}>Views · 30d</Text></View>
                <View style={styles.anaStat}><Text style={styles.anaValue}>{analytics.metrics?.leads_30d ?? 0}</Text><Text style={styles.anaLabel}>Leads · 30d</Text></View>
                <View style={styles.anaStat}><Text style={styles.anaValue}>{analytics.metrics?.conversion_pct ?? 0}%</Text><Text style={styles.anaLabel}>Conversion</Text></View>
                <View style={styles.anaStat}><Text style={styles.anaValue}>#{analytics.metrics?.profile_rank_city ?? "–"}</Text><Text style={styles.anaLabel}>City rank</Text></View>
              </View>
              {showAnalytics && (
                <View style={styles.chartCard}>
                  <Text style={styles.anaTitle}>Last 14 days · views & leads</Text>
                  <View style={styles.chartRow}>
                    {(analytics.trend_14d || []).map((d: any, i: number) => {
                      const max = Math.max(1, ...analytics.trend_14d.map((x: any) => x.views));
                      const h = Math.max(4, Math.round((d.views / max) * 72));
                      return (
                        <View key={i} style={styles.chartCol}>
                          <View style={{ flex: 1, justifyContent: "flex-end" }}>
                            <View style={[styles.chartBar, { height: h }]} />
                          </View>
                        </View>
                      );
                    })}
                  </View>
                  <View style={{ flexDirection: "row", justifyContent: "space-between", marginTop: 6 }}>
                    <Text style={styles.chartLabel}>{new Date(analytics.trend_14d?.[0]?.date).toLocaleDateString("en-IN", { day: "2-digit", month: "short" })}</Text>
                    <Text style={styles.chartLabel}>Today</Text>
                  </View>
                  <Text style={styles.anaCaption}>Perks: {analytics.perks?.perks?.slice(0, 2).join(" · ") || "—"}</Text>
                  <Pressable testID="upgrade-tier-btn" onPress={() => router.push("/subscriptions" as any)} style={styles.upgradeBtn}>
                    <Icon name="rocket-outline" size={14} color={colors.onBrandPrimary} />
                    <Text style={styles.upgradeTxt}>Upgrade tier</Text>
                  </Pressable>
                </View>
              )}
            </>
          )}

          {a.recent_listings && a.recent_listings.length > 0 && (
            <>
              <Text style={styles.sectionTitle}>Recent listings by this agent</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: spacing.md, paddingVertical: spacing.sm }}>
                {a.recent_listings.map(p => (
                  <Pressable
                    key={p.id}
                    testID={`agent-listing-${p.id}`}
                    onPress={() => router.push(`/property/${p.id}` as any)}
                    style={styles.listingCard}
                  >
                    <Image source={{ uri: p.images?.[0] }} style={styles.listingImg} contentFit="cover" />
                    <View style={{ padding: spacing.sm }}>
                      <Text style={styles.listingPrice}>{formatINR(p.price)}</Text>
                      <Text style={styles.listingMeta} numberOfLines={1}>{p.area} {p.area_unit} · {p.type}</Text>
                    </View>
                  </Pressable>
                ))}
              </ScrollView>
            </>
          )}

          <Text style={styles.disclaimer}>
            InfraJagat lists agents for discovery only. Verify credentials, RERA registration and paperwork before making any payment.
          </Text>
        </View>
      </ScrollView>

      <View style={[styles.bottomBar, { paddingBottom: insets.bottom + spacing.sm }]}>
        <Pressable testID="agent-whatsapp-btn" onPress={() => openWhatsApp(a.whatsapp || a.phone, waMsg)} style={[styles.iconBtn, { backgroundColor: "#25D366" }]}>
          <Icon name="logo-whatsapp" size={22} color="#FFFFFF" />
        </Pressable>
        <Pressable testID="agent-call-btn" onPress={() => openTel(a.phone)} style={styles.secondaryBtn}>
          <Icon name="call-outline" size={18} color={colors.onSurface} />
          <Text style={styles.secondaryText}>Call</Text>
        </Pressable>
        <Pressable testID="agent-enquiry-btn" onPress={() => setShowEnquiry(true)} style={styles.primaryBtn}>
          <Text style={styles.primaryText}>Send enquiry</Text>
        </Pressable>
      </View>

      {showEnquiry && (
        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : undefined} style={styles.sheetOverlay}>
          <Pressable style={styles.sheetBackdrop} onPress={() => setShowEnquiry(false)} />
          <View style={[styles.sheet, { paddingBottom: insets.bottom + spacing.lg }]}>
            {submitted ? (
              <View style={{ padding: spacing.xl, alignItems: "center" }}>
                <View style={styles.successIcon}><Icon name="checkmark" size={28} color={colors.onBrandPrimary} /></View>
                <Text style={styles.sheetTitle}>Enquiry sent</Text>
                <Text style={styles.sheetSub}>{a.name} will reach out on {mobile}.</Text>
                <Pressable testID="enquiry-done-btn" onPress={() => { setShowEnquiry(false); setSubmitted(false); }} style={[styles.primaryBtn, { marginTop: spacing.xl }]}>
                  <Text style={styles.primaryText}>Done</Text>
                </Pressable>
              </View>
            ) : (
              <View style={{ padding: spacing.xl }}>
                <View style={styles.sheetHandle} />
                <Text style={styles.sheetTitle}>Send enquiry to {a.name}</Text>
                <Text style={styles.sheetSub}>They will get your contact and reach out shortly.</Text>
                <TextInput testID="enq-name" placeholder="Your name" placeholderTextColor={colors.muted} value={name} onChangeText={setName} style={styles.input} />
                <TextInput testID="enq-mobile" placeholder="Mobile" placeholderTextColor={colors.muted} value={mobile} onChangeText={setMobile} keyboardType="phone-pad" maxLength={13} style={styles.input} />
                <TextInput testID="enq-message" placeholder="What are you looking for? (optional)" placeholderTextColor={colors.muted} value={msg} onChangeText={setMsg} multiline numberOfLines={3} style={[styles.input, { minHeight: 80, textAlignVertical: "top" }]} />
                <Pressable
                  testID="enq-submit"
                  onPress={submit}
                  disabled={submitting || !name.trim() || mobile.trim().length < 10}
                  style={[styles.primaryBtn, { marginTop: spacing.lg, opacity: (submitting || !name.trim() || mobile.trim().length < 10) ? 0.5 : 1 }]}
                >
                  {submitting ? <ActivityIndicator color={colors.onBrandPrimary} /> : <Text style={styles.primaryText}>Send</Text>}
                </Pressable>
              </View>
            )}
          </View>
        </KeyboardAvoidingView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  header: { paddingHorizontal: spacing.xl, paddingBottom: spacing.sm },
  heroBlock: { alignItems: "center", padding: spacing.xl },
  avatar: { width: 120, height: 120, borderRadius: 60, backgroundColor: colors.surfaceSecondary },
  name: { fontSize: 22, fontWeight: "800", color: colors.onSurface, letterSpacing: -0.2 },
  firm: { fontSize: 13, color: colors.muted, marginTop: 4 },
  catBadge: { marginTop: spacing.md, backgroundColor: colors.surfaceSecondary, paddingHorizontal: 10, paddingVertical: 5, borderRadius: radius.pill },
  catBadgeText: { fontSize: 11, fontWeight: "700", color: colors.onSurface, letterSpacing: 0.4 },
  tierBadgeBig: { flexDirection: "row", alignItems: "center", gap: 6, marginTop: spacing.sm, paddingHorizontal: 12, paddingVertical: 6, borderRadius: radius.pill, borderWidth: 1 },
  tierBadgeText: { fontSize: 12, fontWeight: "800", letterSpacing: 0.3 },
  statsRow: { flexDirection: "row", alignItems: "center", marginTop: spacing.xl, backgroundColor: colors.surfaceSecondary, borderRadius: radius.lg, padding: spacing.md, alignSelf: "stretch" },
  statCol: { flex: 1, alignItems: "center" },
  statDivider: { width: 1, height: 30, backgroundColor: colors.border },
  statValue: { fontSize: 18, fontWeight: "800", color: colors.onSurface },
  statLabel: { fontSize: 11, color: colors.muted, marginTop: 2, fontWeight: "600" },
  reraRow: { flexDirection: "row", alignItems: "center", gap: 6, marginTop: spacing.md, backgroundColor: colors.surfaceSecondary, paddingHorizontal: 12, paddingVertical: 6, borderRadius: radius.pill },
  reraText: { fontSize: 11, fontWeight: "700", color: colors.onSurface, letterSpacing: 0.3 },
  sectionTitle: { fontSize: 15, fontWeight: "700", color: colors.onSurface, marginTop: spacing.xl },
  about: { fontSize: 13, color: colors.onSurfaceSecondary, lineHeight: 20, marginTop: spacing.sm },
  pillsRow: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm, marginTop: spacing.sm },
  pill: { flexDirection: "row", alignItems: "center", gap: 4, backgroundColor: colors.surfaceSecondary, paddingHorizontal: 10, paddingVertical: 6, borderRadius: radius.pill },
  pillText: { fontSize: 12, color: colors.onSurface, fontWeight: "600" },
  listingCard: { width: 180, borderRadius: radius.md, backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, overflow: "hidden" },
  listingImg: { width: "100%", height: 100 },
  listingPrice: { fontSize: 14, fontWeight: "800", color: colors.onSurface },
  listingMeta: { fontSize: 11, color: colors.muted, marginTop: 2 },
  disclaimer: { fontSize: 11, color: colors.muted, marginTop: spacing.xl, lineHeight: 16 },
  bottomBar: { flexDirection: "row", gap: spacing.sm, paddingHorizontal: spacing.xl, paddingTop: spacing.md, backgroundColor: colors.surface, borderTopWidth: 1, borderTopColor: colors.border, position: "absolute", left: 0, right: 0, bottom: 0 },
  iconBtn: { width: 52, height: 52, borderRadius: radius.md, alignItems: "center", justifyContent: "center" },
  secondaryBtn: { flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 6, paddingHorizontal: 16, height: 52, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface },
  secondaryText: { color: colors.onSurface, fontWeight: "700", fontSize: 14 },
  primaryBtn: { flex: 1, height: 52, borderRadius: radius.md, backgroundColor: colors.brandPrimary, alignItems: "center", justifyContent: "center", flexDirection: "row" },
  primaryText: { color: colors.onBrandPrimary, fontWeight: "700", fontSize: 15 },
  sheetOverlay: { position: "absolute", top: 0, left: 0, right: 0, bottom: 0, justifyContent: "flex-end" },
  sheetBackdrop: { position: "absolute", top: 0, left: 0, right: 0, bottom: 0, backgroundColor: "rgba(10, 25, 47, 0.4)" },
  sheet: { backgroundColor: colors.surface, borderTopLeftRadius: 24, borderTopRightRadius: 24 },
  sheetHandle: { alignSelf: "center", width: 40, height: 4, borderRadius: 2, backgroundColor: colors.border, marginBottom: spacing.md },
  sheetTitle: { fontSize: 18, fontWeight: "800", color: colors.onSurface, textAlign: "center" },
  sheetSub: { fontSize: 13, color: colors.muted, marginTop: 6, marginBottom: spacing.lg, textAlign: "center" },
  input: { borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, borderRadius: radius.md, paddingHorizontal: spacing.md, height: 48, color: colors.onSurface, fontSize: 14, marginTop: spacing.sm },
  successIcon: { width: 56, height: 56, borderRadius: 28, backgroundColor: colors.success, alignItems: "center", justifyContent: "center", marginBottom: spacing.md },
  // Analytics
  analyticsSummary: { flexDirection: "row", gap: 6, marginTop: spacing.sm },
  anaStat: { flex: 1, padding: 10, borderRadius: radius.md, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border, alignItems: "center" },
  anaValue: { fontSize: 16, fontWeight: "800", color: colors.onSurface },
  anaLabel: { fontSize: 10, color: colors.muted, fontWeight: "700", marginTop: 2, textAlign: "center" },
  chartCard: { marginTop: spacing.md, padding: spacing.md, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface },
  anaTitle: { fontSize: 11, fontWeight: "800", color: colors.muted, letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 10 },
  chartRow: { flexDirection: "row", alignItems: "flex-end", gap: 4, height: 80 },
  chartCol: { flex: 1 },
  chartBar: { backgroundColor: colors.brandPrimary, borderRadius: 2 },
  chartLabel: { fontSize: 10, color: colors.muted, fontWeight: "700" },
  anaCaption: { fontSize: 11, color: colors.muted, marginTop: 10, lineHeight: 15 },
  upgradeBtn: { marginTop: 10, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 6, paddingVertical: 10, borderRadius: radius.md, backgroundColor: colors.brand },
  upgradeTxt: { color: colors.onBrand, fontWeight: "800", fontSize: 13 },
});
