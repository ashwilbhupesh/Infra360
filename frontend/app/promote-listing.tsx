import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, ActivityIndicator, Alert } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useLocalSearchParams, useRouter } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";
import { useAuth } from "@/src/auth-context";
import { formatINR } from "@/src/utils/format";

type Plan = { id: string; name: string; days: number; price: number; perks: string[] };

export default function PromoteListing() {
  const { property_id } = useLocalSearchParams<{ property_id: string }>();
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { user } = useAuth();
  const [plans, setPlans] = useState<Plan[]>([]);
  const [prop, setProp] = useState<any>(null);
  const [picked, setPicked] = useState<string>("plan-14");
  const [method, setMethod] = useState<"upi" | "card">("upi");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const [pl, p] = await Promise.all([
          api.get<{ plans: Plan[] }>("/promote/plans"),
          property_id ? api.get(`/properties/${property_id}`) : Promise.resolve(null),
        ]);
        setPlans(pl.plans);
        setProp(p);
      } finally { setLoading(false); }
    })();
  }, [property_id]);

  const selected = plans.find(p => p.id === picked);

  const pay = async () => {
    if (!property_id || !selected) return;
    setSubmitting(true);
    try {
      const res = await api.post<any>(`/properties/${property_id}/promote`, {
        user_id: user?.id,
        plan_id: picked,
        payment_method: method,
        payment_ref: `mock-${Math.random().toString(36).slice(2, 10)}`,
      });
      Alert.alert(
        "Your listing is live on top ⚡",
        `Boost active until ${new Date(res.featured_until).toLocaleDateString("en-IN", { day: "2-digit", month: "short" })}.`,
        [{ text: "Done", onPress: () => router.back() }],
      );
    } catch (e: any) {
      Alert.alert("Payment failed", e?.message || "Please try again.");
    } finally { setSubmitting(false); }
  };

  if (loading) return <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}><ActivityIndicator color={colors.brand} /></View>;

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="promote-back-btn" onPress={() => router.back()} hitSlop={12}><Icon name="chevron-back" size={26} color={colors.onSurface} /></Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.title}>Promote listing</Text>
          <Text style={styles.sub}>Reach more serious buyers · Lead-based plans</Text>
        </View>
      </View>

      <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingBottom: 120, gap: spacing.lg }}>
        {prop ? (
          <View style={styles.listingPreview}>
            <Icon name="pricetag" size={16} color="#D4A72C" />
            <View style={{ flex: 1 }}>
              <Text style={styles.lpTitle} numberOfLines={1}>{prop.title}</Text>
              <Text style={styles.lpMeta}>{formatINR(prop.price)} · {prop.locality_name}</Text>
            </View>
            {prop.featured ? <Text style={styles.liveTag}>LIVE</Text> : null}
          </View>
        ) : null}

        <Text style={styles.sectionTitle}>Pick a plan</Text>
        {plans.map(p => {
          const active = picked === p.id;
          return (
            <Pressable key={p.id} testID={`promote-plan-${p.id}`} onPress={() => setPicked(p.id)} style={[styles.card, active && styles.cardActive]}>
              <View style={styles.cardHead}>
                <View style={{ flex: 1 }}>
                  <Text style={styles.cardName}>{p.name}</Text>
                  <Text style={styles.cardDays}>{p.days} days · WhatsApp lead routing</Text>
                </View>
                <View style={{ alignItems: "flex-end" }}>
                  <Text style={styles.cardPrice}>₹{p.price}</Text>
                  <Text style={styles.cardPer}>one-time</Text>
                </View>
              </View>
              {p.perks.map(perk => (
                <View key={perk} style={styles.perkRow}>
                  <Icon name="checkmark-circle" size={14} color="#D4A72C" />
                  <Text style={styles.perkTxt}>{perk}</Text>
                </View>
              ))}
              {active && (
                <View style={styles.selectedRibbon}>
                  <Icon name="checkmark" size={11} color="#FFFFFF" />
                  <Text style={styles.selectedTxt}>Selected</Text>
                </View>
              )}
            </Pressable>
          );
        })}

        <Text style={styles.sectionTitle}>Pay via</Text>
        <View style={{ flexDirection: "row", gap: 8 }}>
          {(["upi", "card"] as const).map(m => (
            <Pressable key={m} testID={`promote-pay-${m}`} onPress={() => setMethod(m)} style={[styles.payBtn, method === m && styles.payBtnActive]}>
              <Icon name={m === "upi" ? "wallet-outline" : "card-outline"} size={16} color={method === m ? colors.onBrandPrimary : colors.onSurface} />
              <Text style={[styles.payTxt, method === m && { color: colors.onBrandPrimary }]}>{m === "upi" ? "UPI" : "Card"}</Text>
            </Pressable>
          ))}
        </View>
        <Text style={styles.footerNote}>Payments are mock-only in this demo. Your listing will go live for the selected days.</Text>
      </ScrollView>

      <View style={[styles.cta, { paddingBottom: insets.bottom + spacing.md }]}>
        <Pressable
          testID="promote-pay-btn"
          onPress={pay}
          disabled={submitting}
          style={[styles.ctaBtn, submitting && { opacity: 0.5 }]}
        >
          {submitting
            ? <ActivityIndicator color={colors.onBrandPrimary} />
            : <Text style={styles.ctaText}>Pay ₹{selected?.price || 0} & go live</Text>}
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingHorizontal: spacing.lg, paddingBottom: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  title: { fontSize: 20, fontWeight: "800", color: colors.onSurface },
  sub: { fontSize: 11, color: colors.muted, marginTop: 2 },
  sectionTitle: { fontSize: 11, fontWeight: "800", color: colors.muted, letterSpacing: 0.8, textTransform: "uppercase" },
  listingPreview: { flexDirection: "row", gap: 10, alignItems: "center", padding: spacing.md, borderRadius: radius.md, backgroundColor: "#FFF8E1", borderWidth: 1, borderColor: "#F5D77A" },
  lpTitle: { fontSize: 13, fontWeight: "700", color: colors.onSurface },
  lpMeta: { fontSize: 11, color: colors.muted, marginTop: 2 },
  liveTag: { fontSize: 10, fontWeight: "800", color: "#B07020", backgroundColor: "#F5D77A", paddingHorizontal: 6, paddingVertical: 2, borderRadius: radius.pill },
  card: { padding: spacing.lg, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, gap: 8, position: "relative", ...shadow.card },
  cardActive: { borderColor: "#D4A72C", borderWidth: 2 },
  cardHead: { flexDirection: "row", alignItems: "flex-start", gap: spacing.md },
  cardName: { fontSize: 16, fontWeight: "800", color: colors.onSurface },
  cardDays: { fontSize: 11, color: colors.muted, marginTop: 2 },
  cardPrice: { fontSize: 22, fontWeight: "800", color: colors.brand },
  cardPer: { fontSize: 10, color: colors.muted, fontWeight: "700" },
  perkRow: { flexDirection: "row", gap: 8, alignItems: "flex-start" },
  perkTxt: { flex: 1, color: colors.onSurfaceSecondary, fontSize: 12, lineHeight: 17 },
  selectedRibbon: { position: "absolute", top: 10, right: 10, flexDirection: "row", alignItems: "center", gap: 3, paddingHorizontal: 8, paddingVertical: 3, borderRadius: radius.pill, backgroundColor: "#D4A72C" },
  selectedTxt: { color: "#FFFFFF", fontSize: 10, fontWeight: "800", letterSpacing: 0.3 },
  payBtn: { flex: 1, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 6, paddingVertical: 12, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface },
  payBtnActive: { backgroundColor: colors.brandPrimary, borderColor: colors.brandPrimary },
  payTxt: { fontSize: 13, fontWeight: "700", color: colors.onSurface },
  footerNote: { fontSize: 11, color: colors.muted, textAlign: "center" },
  cta: { position: "absolute", left: 0, right: 0, bottom: 0, padding: spacing.lg, backgroundColor: colors.surface, borderTopWidth: 1, borderTopColor: colors.border },
  ctaBtn: { height: 52, borderRadius: radius.md, backgroundColor: "#D4A72C", alignItems: "center", justifyContent: "center" },
  ctaText: { color: "#FFFFFF", fontWeight: "800", fontSize: 15 },
});
