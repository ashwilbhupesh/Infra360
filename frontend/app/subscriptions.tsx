import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, Pressable, ScrollView, ActivityIndicator } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";
import { indianComma } from "@/src/utils/format";

type Tier = {
  name: string; monthly_price: number; annual_price: number;
  perks: string[]; listings_cap: number | null; lead_cap: number | null; badge_color: string;
};

const BUYER_PLANS = [
  {
    id: "free", name: "Free", price: 0, period: "always", tag: "For buyers",
    perks: ["Browse all properties", "Save up to 20", "Follow 5 localities", "InfraValue estimates"],
  },
  {
    id: "pro", name: "InfraJagat Pro", price: 299, period: "/month", tag: "Most popular",
    perks: ["Everything in Free", "Unlimited saves & follows", "Saved-search alerts", "Off-market whispers", "Priority WhatsApp support"],
  },
];

export default function Subscriptions() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [tab, setTab] = useState<"buyers" | "agents">("buyers");
  const [tiers, setTiers] = useState<Tier[]>([]);
  const [cycle, setCycle] = useState<"monthly" | "annual">("monthly");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const data = await api.get<{ tiers: Tier[] }>("/agent-subscription-tiers");
        // Order: Bronze, Silver, Gold (Unverified excluded from selectable plans)
        const order = ["Bronze", "Silver", "Gold"];
        setTiers(data.tiers.filter(t => order.includes(t.name)).sort((a, b) => order.indexOf(a.name) - order.indexOf(b.name)));
      } finally { setLoading(false); }
    })();
  }, []);

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="subs-back-btn" onPress={() => router.back()} hitSlop={12}><Icon name="chevron-back" size={26} color={colors.onSurface} /></Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.title}>Subscriptions</Text>
          <Text style={styles.sub}>Choose a plan that fits your journey</Text>
        </View>
      </View>

      <View style={styles.tabsWrap}>
        <Pressable testID="subs-tab-buyers" onPress={() => setTab("buyers")} style={[styles.tab, tab === "buyers" && styles.tabActive]}>
          <Icon name="person-outline" size={14} color={tab === "buyers" ? colors.onBrand : colors.onSurface} />
          <Text style={[styles.tabTxt, tab === "buyers" && styles.tabTxtActive]}>Buyers</Text>
        </Pressable>
        <Pressable testID="subs-tab-agents" onPress={() => setTab("agents")} style={[styles.tab, tab === "agents" && styles.tabActive]}>
          <Icon name="briefcase-outline" size={14} color={tab === "agents" ? colors.onBrand : colors.onSurface} />
          <Text style={[styles.tabTxt, tab === "agents" && styles.tabTxtActive]}>Agents & Developers</Text>
        </Pressable>
      </View>

      <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingBottom: 80, gap: spacing.lg }}>
        {tab === "buyers" ? (
          BUYER_PLANS.map(p => (
            <View key={p.id} style={[styles.card, p.id === "pro" && { borderColor: colors.brandPrimary, borderWidth: 2 }]}>
              <View style={styles.cardHead}>
                <Text style={styles.cardName}>{p.name}</Text>
                <View style={[styles.pill, p.id === "pro" && { backgroundColor: colors.brandPrimary }]}>
                  <Text style={[styles.pillText, p.id === "pro" && { color: colors.onBrandPrimary }]}>{p.tag}</Text>
                </View>
              </View>
              <View style={{ flexDirection: "row", alignItems: "baseline", gap: 4, marginTop: 4 }}>
                <Text style={styles.cardPrice}>₹{p.price}</Text>
                <Text style={styles.cardPeriod}>{p.period}</Text>
              </View>
              <View style={{ marginTop: spacing.md, gap: 6 }}>
                {p.perks.map(k => (
                  <View key={k} style={styles.perkRow}>
                    <Icon name="checkmark-circle" size={14} color={colors.success} />
                    <Text style={styles.perk}>{k}</Text>
                  </View>
                ))}
              </View>
              <Pressable
                testID={`subs-choose-${p.id}`}
                disabled={p.id === "free"}
                style={[styles.cta, p.id === "pro" ? styles.ctaHi : { backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border }]}
              >
                <Text style={[styles.ctaTxt, p.id === "pro" && { color: colors.onBrandPrimary }, p.id === "free" && { color: colors.muted }]}>
                  {p.id === "free" ? "Current plan" : "Coming soon"}
                </Text>
              </Pressable>
            </View>
          ))
        ) : (
          <>
            <View style={styles.toggleRow}>
              <Pressable testID="subs-cycle-monthly" onPress={() => setCycle("monthly")} style={[styles.toggleBtn, cycle === "monthly" && styles.toggleActive]}>
                <Text style={[styles.toggleTxt, cycle === "monthly" && styles.toggleTxtActive]}>Monthly</Text>
              </Pressable>
              <Pressable testID="subs-cycle-annual" onPress={() => setCycle("annual")} style={[styles.toggleBtn, cycle === "annual" && styles.toggleActive]}>
                <Text style={[styles.toggleTxt, cycle === "annual" && styles.toggleTxtActive]}>Annual · save 17%</Text>
              </Pressable>
            </View>

            {loading ? <ActivityIndicator color={colors.brand} /> : tiers.map(t => {
              const price = cycle === "monthly" ? t.monthly_price : t.annual_price;
              const sub = cycle === "monthly" ? "/mo" : "/yr";
              const highlighted = t.name === "Silver";
              return (
                <View key={t.name} style={[styles.card, highlighted && { borderColor: t.badge_color, borderWidth: 2 }]}>
                  <View style={styles.cardHead}>
                    <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
                      <View style={[styles.tierDot, { backgroundColor: t.badge_color }]} />
                      <Text style={styles.cardName}>{t.name}</Text>
                    </View>
                    {highlighted && (
                      <View style={[styles.pill, { backgroundColor: t.badge_color }]}><Text style={[styles.pillText, { color: "#FFFFFF" }]}>Most Popular</Text></View>
                    )}
                  </View>
                  <View style={{ flexDirection: "row", alignItems: "baseline", gap: 4, marginTop: 4 }}>
                    <Text style={styles.cardPrice}>₹{indianComma(price)}</Text>
                    <Text style={styles.cardPeriod}>{sub}</Text>
                  </View>
                  <View style={styles.capRow}>
                    <Text style={styles.capTxt}>Listings: {t.listings_cap ?? "Unlimited"}</Text>
                    <Text style={styles.capTxt}>Leads/mo: {t.lead_cap ?? "Unlimited"}</Text>
                  </View>
                  <View style={{ marginTop: spacing.md, gap: 6 }}>
                    {t.perks.map(k => (
                      <View key={k} style={styles.perkRow}>
                        <Icon name="checkmark-circle" size={14} color={t.badge_color} />
                        <Text style={styles.perk}>{k}</Text>
                      </View>
                    ))}
                  </View>
                  <Pressable
                    testID={`subs-choose-${t.name.toLowerCase()}`}
                    style={[styles.cta, { backgroundColor: t.badge_color }]}
                  >
                    <Text style={[styles.ctaTxt, { color: "#FFFFFF" }]}>Start {t.name}</Text>
                  </Pressable>
                </View>
              );
            })}

            <View style={styles.analyticsCard}>
              <Icon name="stats-chart" size={16} color={colors.brand} />
              <Text style={styles.analyticsTxt}>
                Already an agent? <Text style={{ fontWeight: "800" }}>Pull up live analytics</Text> on your agent profile — views, leads, and conversion.
              </Text>
            </View>
          </>
        )}
        <Text style={styles.footer}>Payments launch soon. Your free access remains.</Text>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingHorizontal: spacing.lg, paddingBottom: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  title: { fontSize: 20, fontWeight: "800", color: colors.onSurface },
  sub: { fontSize: 11, color: colors.muted, marginTop: 2 },
  tabsWrap: { flexDirection: "row", gap: 6, padding: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  tab: { flexDirection: "row", alignItems: "center", gap: 6, flex: 1, paddingVertical: 10, borderRadius: radius.pill, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, justifyContent: "center" },
  tabActive: { backgroundColor: colors.brand, borderColor: colors.brand },
  tabTxt: { fontSize: 12, fontWeight: "700", color: colors.onSurface },
  tabTxtActive: { color: colors.onBrand },
  toggleRow: { flexDirection: "row", gap: 4, padding: 4, borderRadius: radius.pill, backgroundColor: colors.surfaceSecondary, alignSelf: "center", borderWidth: 1, borderColor: colors.border },
  toggleBtn: { paddingHorizontal: 14, paddingVertical: 7, borderRadius: radius.pill },
  toggleActive: { backgroundColor: colors.brand },
  toggleTxt: { fontSize: 12, fontWeight: "700", color: colors.onSurface },
  toggleTxtActive: { color: colors.onBrand },
  card: { padding: spacing.lg, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, ...shadow.card },
  cardHead: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  tierDot: { width: 10, height: 10, borderRadius: 5 },
  cardName: { fontSize: 17, fontWeight: "800", color: colors.onSurface, letterSpacing: 0.2 },
  cardPrice: { fontSize: 26, fontWeight: "800", color: colors.onSurface },
  cardPeriod: { fontSize: 12, color: colors.muted, fontWeight: "600" },
  capRow: { flexDirection: "row", justifyContent: "space-between", marginTop: 8, paddingTop: 8, borderTopWidth: 1, borderTopColor: colors.border },
  capTxt: { fontSize: 11, fontWeight: "700", color: colors.muted, letterSpacing: 0.3 },
  pill: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: radius.pill, backgroundColor: colors.surfaceSecondary },
  pillText: { fontSize: 10, fontWeight: "800", color: colors.onSurface, letterSpacing: 0.4 },
  perkRow: { flexDirection: "row", alignItems: "flex-start", gap: 8 },
  perk: { flex: 1, fontSize: 13, color: colors.onSurfaceSecondary, lineHeight: 18 },
  cta: { marginTop: spacing.lg, paddingVertical: 12, borderRadius: radius.md, alignItems: "center", justifyContent: "center" },
  ctaHi: { backgroundColor: colors.brandPrimary },
  ctaTxt: { fontWeight: "800", color: colors.onSurface, fontSize: 14 },
  analyticsCard: { flexDirection: "row", gap: 10, alignItems: "flex-start", padding: spacing.md, borderRadius: radius.md, backgroundColor: "#EDF4FF", borderWidth: 1, borderColor: "#C8DBF9" },
  analyticsTxt: { flex: 1, fontSize: 12, color: colors.onSurface, lineHeight: 17 },
  footer: { textAlign: "center", color: colors.muted, fontSize: 11, marginTop: spacing.md, lineHeight: 16 },
});
