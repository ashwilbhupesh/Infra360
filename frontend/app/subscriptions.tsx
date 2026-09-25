import React from "react";
import { View, Text, StyleSheet, Pressable, ScrollView } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";

const PLANS = [
  {
    id: "free",
    name: "Free",
    price: "₹0",
    period: "always",
    tag: "Current",
    perks: [
      "Browse all properties",
      "Save up to 20 properties",
      "Follow 5 localities",
      "InfraValue estimates",
    ],
  },
  {
    id: "pro",
    name: "InfraLocal Pro",
    price: "₹299",
    period: "per month",
    tag: "Most popular",
    perks: [
      "Everything in Free",
      "Unlimited saves and follows",
      "Saved-search alerts",
      "Off-market whispers from verified brokers",
      "Priority WhatsApp support",
    ],
  },
  {
    id: "biz",
    name: "Business",
    price: "₹1,499",
    period: "per month",
    tag: "For agents & developers",
    perks: [
      "Everything in Pro",
      "Publish up to 25 verified listings",
      "Featured placement in your city",
      "Enquiry inbox with WhatsApp routing",
      "Lead insights and analytics",
    ],
  },
];

export default function Subscriptions() {
  const insets = useSafeAreaInsets();
  const router = useRouter();

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="subs-back-btn" onPress={() => router.back()} hitSlop={12}><Icon name="chevron-back" size={26} color={colors.onSurface} /></Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.title}>Subscriptions</Text>
          <Text style={styles.sub}>Choose a plan that fits your journey</Text>
        </View>
      </View>

      <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingBottom: 60, gap: spacing.lg }}>
        {PLANS.map(p => (
          <View key={p.id} style={[styles.card, p.id === "pro" && styles.cardHighlight]}>
            <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
              <Text style={styles.name}>{p.name}</Text>
              <View style={[styles.pill, p.id === "pro" && styles.pillHi]}>
                <Text style={[styles.pillText, p.id === "pro" && styles.pillHiText]}>{p.tag}</Text>
              </View>
            </View>
            <View style={{ flexDirection: "row", alignItems: "baseline", gap: 6, marginTop: spacing.sm }}>
              <Text style={styles.price}>{p.price}</Text>
              <Text style={styles.period}>{p.period}</Text>
            </View>
            <View style={{ marginTop: spacing.md, gap: 8 }}>
              {p.perks.map(perk => (
                <View key={perk} style={{ flexDirection: "row", gap: 8, alignItems: "flex-start" }}>
                  <Icon name="checkmark-circle" size={16} color={colors.success} />
                  <Text style={styles.perk}>{perk}</Text>
                </View>
              ))}
            </View>
            <Pressable
              testID={`subs-choose-${p.id}`}
              onPress={() => {}}
              disabled={p.id === "free"}
              style={[styles.cta, p.id === "free" && { backgroundColor: colors.surfaceSecondary }, p.id === "pro" && styles.ctaHi]}
            >
              <Text style={[styles.ctaText, p.id === "free" && { color: colors.muted }, p.id === "pro" && { color: colors.onBrandPrimary }]}>
                {p.id === "free" ? "Current plan" : "Coming soon"}
              </Text>
            </Pressable>
          </View>
        ))}
        <Text style={styles.footer}>Payments launch soon. You will always be able to keep using the free plan.</Text>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingHorizontal: spacing.lg, paddingBottom: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  title: { fontSize: 20, fontWeight: "800", color: colors.onSurface },
  sub: { fontSize: 11, color: colors.muted, marginTop: 2 },
  card: { padding: spacing.lg, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, ...shadow.card },
  cardHighlight: { borderColor: colors.brandPrimary, borderWidth: 2 },
  name: { fontSize: 17, fontWeight: "800", color: colors.onSurface, letterSpacing: 0.2 },
  pill: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: radius.pill, backgroundColor: colors.surfaceSecondary },
  pillHi: { backgroundColor: colors.brandPrimary },
  pillText: { fontSize: 10, fontWeight: "800", color: colors.onSurface, letterSpacing: 0.4 },
  pillHiText: { color: colors.onBrandPrimary },
  price: { fontSize: 26, fontWeight: "800", color: colors.onSurface },
  period: { fontSize: 12, color: colors.muted, fontWeight: "600" },
  perk: { flex: 1, fontSize: 13, color: colors.onSurfaceSecondary, lineHeight: 18 },
  cta: { marginTop: spacing.lg, paddingVertical: 12, borderRadius: radius.md, alignItems: "center", justifyContent: "center", borderWidth: 1, borderColor: colors.border },
  ctaHi: { backgroundColor: colors.brandPrimary, borderColor: colors.brandPrimary },
  ctaText: { fontWeight: "700", color: colors.onSurface },
  footer: { textAlign: "center", color: colors.muted, fontSize: 11, marginTop: spacing.md, lineHeight: 16 },
});
