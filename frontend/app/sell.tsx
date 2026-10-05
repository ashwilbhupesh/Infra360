import React from "react";
import { View, Text, StyleSheet, ScrollView, Pressable } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter, Stack } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius } from "@/src/theme";

const STEPS = [
  { icon: "camera-outline", title: "Add great photos", body: "4–8 well-lit photos help your listing stand out. Shoot the drawing room, bedrooms, kitchen, bathrooms, parking and the entrance." },
  { icon: "pricetag-outline", title: "Set a fair price", body: "Check locality trends on InfraJagat so you price in-market. Verified listings sell up to 2x faster." },
  { icon: "shield-checkmark-outline", title: "Verify the paperwork", body: "Keep sale deed, approved map, latest tax receipt, electricity bill and NOC ready. Verified listings carry the green badge." },
  { icon: "chatbubbles-outline", title: "Reply fast on WhatsApp", body: "Serious buyers love quick replies. Enquiries land straight on WhatsApp with the property pre-filled." },
];

const WHY = [
  { icon: "eye-outline", title: "Zero commission", body: "InfraJagat doesn't charge sellers. You keep what you earn." },
  { icon: "trending-up-outline", title: "Reach serious buyers", body: "Your listing shows on the map, in locality pages and in search." },
  { icon: "map-outline", title: "Local intelligence", body: "Buyers see InfraValue, DLC rate and locality trends — fewer price haggles." },
  { icon: "people-outline", title: "Agent escalation (optional)", body: "Choose to let verified agents pitch your property for a success fee." },
];

export default function Sell() {
  const insets = useSafeAreaInsets();
  const router = useRouter();

  return (
    <View style={{ flex: 1, backgroundColor: colors.surfaceSecondary }}>
      <Stack.Screen options={{ headerShown: false }} />
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="sell-back" onPress={() => router.back()} hitSlop={12}>
          <Icon name="chevron-back" size={26} color={colors.onSurface} />
        </Pressable>
        <Text style={styles.title}>Sell on InfraJagat</Text>
        <View style={{ width: 26 }} />
      </View>

      <ScrollView contentContainerStyle={{ padding: spacing.xl, paddingBottom: 120 }}>
        <View style={styles.hero}>
          <View style={styles.heroIconWrap}>
            <Icon name="home-outline" size={28} color={colors.onBrandPrimary} />
          </View>
          <Text style={styles.heroTitle}>List your property in 7 quick steps</Text>
          <Text style={styles.heroSub}>
            Free. No commission. Reach thousands of buyers across Jaipur who are actively looking right now.
          </Text>
          <Pressable testID="sell-start-cta" onPress={() => router.push("/list-property" as any)} style={styles.heroCta}>
            <Text style={styles.heroCtaText}>Start listing</Text>
            <Icon name="arrow-forward" size={14} color={colors.onBrandPrimary} />
          </Pressable>
        </View>

        <Text style={styles.sectionKicker}>HOW IT WORKS</Text>
        <View style={styles.card}>
          {STEPS.map((s, i) => (
            <View key={s.title} style={[styles.stepRow, i < STEPS.length - 1 && styles.rowBorder]}>
              <View style={styles.stepNumWrap}>
                <Text style={styles.stepNum}>{i + 1}</Text>
              </View>
              <View style={{ flex: 1 }}>
                <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
                  <Icon name={s.icon as any} size={14} color={colors.brand} />
                  <Text style={styles.stepTitle}>{s.title}</Text>
                </View>
                <Text style={styles.stepBody}>{s.body}</Text>
              </View>
            </View>
          ))}
        </View>

        <Text style={styles.sectionKicker}>WHY INFRAJAGAT</Text>
        <View style={styles.card}>
          {WHY.map((w, i) => (
            <View key={w.title} style={[styles.whyRow, i < WHY.length - 1 && styles.rowBorder]}>
              <View style={styles.whyIcon}>
                <Icon name={w.icon as any} size={18} color={colors.brand} />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={styles.whyTitle}>{w.title}</Text>
                <Text style={styles.whyBody}>{w.body}</Text>
              </View>
            </View>
          ))}
        </View>

        <View style={styles.testimony}>
          <Icon name="chatbubble-ellipses-outline" size={18} color={colors.brand} />
          <Text style={styles.testimonyText}>
            "Listed my Mansarovar 3BHK on InfraJagat on a Monday. 11 buyer calls by Thursday. Sold within three weeks — zero commission."
          </Text>
          <Text style={styles.testimonyBy}>— Priya S., Mansarovar</Text>
        </View>

        <View style={styles.helpBox}>
          <Icon name="help-circle-outline" size={18} color={colors.brandPrimary} />
          <Text style={styles.helpText}>
            Need help? Our team can shoot photos, write the ad and verify the paperwork for a one-time fee.
          </Text>
          <Pressable testID="sell-contact" onPress={() => router.push("/contact-us" as any)} style={styles.helpBtn}>
            <Text style={styles.helpBtnText}>Talk to us</Text>
          </Pressable>
        </View>
      </ScrollView>

      <View style={[styles.footer, { paddingBottom: Math.max(insets.bottom, 10) + 10 }]}>
        <Pressable testID="sell-list-cta" onPress={() => router.push("/list-property" as any)} style={styles.footerBtn}>
          <Icon name="add-circle" size={16} color={colors.onBrandPrimary} />
          <Text style={styles.footerBtnText}>List my property</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", paddingHorizontal: spacing.xl, paddingBottom: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  title: { fontSize: 18, fontWeight: "800", color: colors.onSurface, letterSpacing: -0.2 },
  hero: { backgroundColor: colors.brand, borderRadius: radius.lg, padding: spacing.xl, alignItems: "center", gap: 8, marginBottom: spacing.lg },
  heroIconWrap: { width: 56, height: 56, borderRadius: 28, backgroundColor: colors.brandPrimary, alignItems: "center", justifyContent: "center", marginBottom: 4 },
  heroTitle: { fontSize: 20, fontWeight: "800", color: colors.onBrand, textAlign: "center", letterSpacing: -0.3 },
  heroSub: { fontSize: 13, color: colors.onBrand, textAlign: "center", opacity: 0.85, lineHeight: 18 },
  heroCta: { flexDirection: "row", alignItems: "center", gap: 6, backgroundColor: colors.brandPrimary, paddingHorizontal: 20, paddingVertical: 12, borderRadius: radius.pill, marginTop: 8 },
  heroCtaText: { color: colors.onBrandPrimary, fontSize: 13, fontWeight: "800" },
  sectionKicker: { fontSize: 10, fontWeight: "800", color: colors.muted, letterSpacing: 1, marginTop: spacing.lg, marginBottom: spacing.sm, paddingLeft: 4 },
  card: { backgroundColor: colors.surface, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, overflow: "hidden" },
  stepRow: { flexDirection: "row", gap: spacing.md, padding: spacing.lg },
  stepNumWrap: { width: 28, height: 28, borderRadius: 14, backgroundColor: colors.brandTertiary, alignItems: "center", justifyContent: "center" },
  stepNum: { color: colors.brand, fontWeight: "800", fontSize: 13 },
  stepTitle: { fontSize: 14, fontWeight: "800", color: colors.onSurface },
  stepBody: { fontSize: 12, color: colors.muted, marginTop: 4, lineHeight: 17 },
  whyRow: { flexDirection: "row", alignItems: "flex-start", gap: spacing.md, padding: spacing.lg },
  whyIcon: { width: 36, height: 36, borderRadius: 18, backgroundColor: colors.brandTertiary, alignItems: "center", justifyContent: "center" },
  whyTitle: { fontSize: 13, fontWeight: "800", color: colors.onSurface },
  whyBody: { fontSize: 12, color: colors.muted, marginTop: 3, lineHeight: 17 },
  rowBorder: { borderBottomWidth: 1, borderBottomColor: colors.border },
  testimony: { backgroundColor: colors.brandTertiary, borderRadius: radius.lg, padding: spacing.lg, marginTop: spacing.lg, gap: 4 },
  testimonyText: { fontSize: 13, color: colors.brand, fontStyle: "italic", lineHeight: 19, marginTop: 6 },
  testimonyBy: { fontSize: 11, color: colors.brand, fontWeight: "700", marginTop: 4 },
  helpBox: { backgroundColor: colors.surface, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, padding: spacing.lg, marginTop: spacing.lg, gap: 8 },
  helpText: { fontSize: 12, color: colors.onSurface, lineHeight: 17 },
  helpBtn: { alignSelf: "flex-start", borderWidth: 1, borderColor: colors.brandPrimary, paddingHorizontal: 14, paddingVertical: 8, borderRadius: radius.pill, marginTop: 4 },
  helpBtnText: { fontSize: 12, fontWeight: "800", color: colors.brandPrimary },
  footer: { position: "absolute", bottom: 0, left: 0, right: 0, paddingHorizontal: spacing.xl, paddingTop: 10, backgroundColor: colors.surface, borderTopWidth: 1, borderTopColor: colors.border },
  footerBtn: { flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 6, backgroundColor: colors.brandPrimary, paddingVertical: 14, borderRadius: radius.pill },
  footerBtnText: { color: colors.onBrandPrimary, fontSize: 14, fontWeight: "800" },
});
