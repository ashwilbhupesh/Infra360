import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, ActivityIndicator, TextInput, KeyboardAvoidingView, Platform, Linking } from "react-native";
import { Image } from "expo-image";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useLocalSearchParams, useRouter, Stack } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";
import { useAuth } from "@/src/auth-context";

type Supplier = {
  id: string; category_id: string; name: string; tagline: string; city: string; area: string;
  rating: number; reviews: number; verified: boolean; featured: boolean;
  starting_price: string; min_project: string; offerings: string[]; phone: string; image: string;
  about: string; category?: { name: string };
};

export default function SupplierDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { user } = useAuth();
  const [s, setS] = useState<Supplier | null>(null);
  const [loading, setLoading] = useState(true);
  const [showQuote, setShowQuote] = useState(false);
  const [qName, setQName] = useState(user?.name ?? "");
  const [qMobile, setQMobile] = useState(user?.mobile ?? "");
  const [qMsg, setQMsg] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const data = await api.get<Supplier>(`/market/suppliers/${id}`);
        setS(data);
      } finally { setLoading(false); }
    })();
  }, [id]);

  const submitQuote = async () => {
    if (!qName.trim() || qMobile.trim().length < 10) return;
    setSubmitting(true);
    try {
      await api.post("/market/quote-requests", { supplier_id: id, user_id: user?.id, name: qName.trim(), mobile: qMobile.trim(), message: qMsg.trim() || undefined });
      setSubmitted(true);
    } finally { setSubmitting(false); }
  };

  const callSupplier = () => {
    if (s?.phone) Linking.openURL(`tel:${s.phone.replace(/\s/g, "")}`).catch(() => {});
  };

  if (loading || !s) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.surface, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator color={colors.brand} />
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <Stack.Screen options={{ headerShown: false }} />
      <ScrollView contentContainerStyle={{ paddingBottom: 120 }}>
        <View style={styles.heroWrap}>
          <Image source={{ uri: s.image }} style={styles.hero} contentFit="cover" transition={200} />
          <Pressable testID="supplier-back-btn" onPress={() => router.back()} style={[styles.backBtn, { top: insets.top + spacing.md }]}>
            <Icon name="chevron-back" size={22} color={colors.onSurface} />
          </Pressable>
        </View>

        <View style={{ padding: spacing.xl }}>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
            <Text style={styles.name}>{s.name}</Text>
            {s.verified && <Icon name="shield-checkmark" size={18} color={colors.success} />}
          </View>
          <Text style={styles.tag}>{s.tagline}</Text>

          <View style={styles.metaRow}>
            <View style={styles.ratingPill}>
              <Icon name="star" size={12} color={colors.onBrandPrimary} />
              <Text style={styles.ratingText}>{s.rating.toFixed(1)}</Text>
            </View>
            <Text style={styles.meta}>{s.reviews} reviews</Text>
            <Text style={styles.dot}>·</Text>
            <Icon name="location-outline" size={13} color={colors.muted} />
            <Text style={styles.meta}>{s.area}, {s.city}</Text>
          </View>

          {s.category?.name ? (
            <View style={styles.catBadge}><Text style={styles.catBadgeText}>{s.category.name}</Text></View>
          ) : null}

          <View style={styles.priceRow}>
            <View style={styles.priceCol}>
              <Text style={styles.priceLabel}>STARTING PRICE</Text>
              <Text style={styles.priceValue}>{s.starting_price || "On enquiry"}</Text>
            </View>
            <View style={styles.priceDivider} />
            <View style={styles.priceCol}>
              <Text style={styles.priceLabel}>MIN. PROJECT</Text>
              <Text style={styles.priceValue}>{s.min_project || "—"}</Text>
            </View>
          </View>

          <Text style={styles.sectionTitle}>About</Text>
          <Text style={styles.about}>{s.about}</Text>

          <Text style={styles.sectionTitle}>What they offer</Text>
          <View style={styles.offerRow}>
            {s.offerings.map(o => (
              <View key={o} style={styles.offerPill}>
                <Icon name="checkmark" size={12} color={colors.brand} />
                <Text style={styles.offerText}>{o}</Text>
              </View>
            ))}
          </View>

          <Text style={styles.disclaimer}>
            Listings on the InfraLocal Market are demo entries. Verify credentials with the supplier directly before making any payment.
          </Text>
        </View>
      </ScrollView>

      {/* Bottom action bar */}
      <View style={[styles.bottomBar, { paddingBottom: insets.bottom + spacing.sm }]}>
        <Pressable testID="call-supplier-btn" onPress={callSupplier} style={styles.secondaryBtn}>
          <Icon name="call-outline" size={18} color={colors.onSurface} />
          <Text style={styles.secondaryText}>Call</Text>
        </Pressable>
        <Pressable testID="quote-btn" onPress={() => setShowQuote(true)} style={styles.primaryBtn}>
          <Text style={styles.primaryText}>Request Quote</Text>
        </Pressable>
      </View>

      {/* Quote sheet */}
      {showQuote && (
        <KeyboardAvoidingView
          behavior={Platform.OS === "ios" ? "padding" : undefined}
          style={styles.sheetOverlay}
        >
          <Pressable style={styles.sheetBackdrop} onPress={() => setShowQuote(false)} />
          <View style={[styles.sheet, { paddingBottom: insets.bottom + spacing.lg }]}>
            {submitted ? (
              <View style={{ padding: spacing.xl, alignItems: "center" }}>
                <View style={styles.successIcon}>
                  <Icon name="checkmark" size={28} color={colors.onBrandPrimary} />
                </View>
                <Text style={styles.sheetTitle}>Quote request sent</Text>
                <Text style={styles.sheetSub}>{s.name} will reach out on {qMobile}. In the meantime you can also give them a call.</Text>
                <Pressable testID="quote-done-btn" onPress={() => { setShowQuote(false); setSubmitted(false); }} style={[styles.primaryBtn, { marginTop: spacing.xl }]}>
                  <Text style={styles.primaryText}>Done</Text>
                </Pressable>
              </View>
            ) : (
              <View style={{ padding: spacing.xl }}>
                <View style={styles.sheetHandle} />
                <Text style={styles.sheetTitle}>Request a quote from {s.name}</Text>
                <Text style={styles.sheetSub}>They will get your details and reach out shortly.</Text>
                <TextInput
                  testID="quote-name-input"
                  placeholder="Your name"
                  placeholderTextColor={colors.muted}
                  value={qName}
                  onChangeText={setQName}
                  style={styles.input}
                />
                <TextInput
                  testID="quote-mobile-input"
                  placeholder="Mobile"
                  placeholderTextColor={colors.muted}
                  value={qMobile}
                  onChangeText={setQMobile}
                  keyboardType="phone-pad"
                  maxLength={13}
                  style={styles.input}
                />
                <TextInput
                  testID="quote-message-input"
                  placeholder="What do you need? (optional)"
                  placeholderTextColor={colors.muted}
                  value={qMsg}
                  onChangeText={setQMsg}
                  multiline
                  numberOfLines={3}
                  style={[styles.input, { minHeight: 80, textAlignVertical: "top" }]}
                />
                <Pressable
                  testID="quote-submit-btn"
                  onPress={submitQuote}
                  disabled={submitting || !qName.trim() || qMobile.trim().length < 10}
                  style={[styles.primaryBtn, { marginTop: spacing.lg, opacity: (submitting || !qName.trim() || qMobile.trim().length < 10) ? 0.5 : 1 }]}
                >
                  {submitting ? <ActivityIndicator color={colors.onBrandPrimary} /> : <Text style={styles.primaryText}>Send request</Text>}
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
  heroWrap: { height: 240, backgroundColor: colors.surfaceSecondary },
  hero: { width: "100%", height: "100%" },
  backBtn: { position: "absolute", left: spacing.lg, width: 36, height: 36, borderRadius: 18, backgroundColor: colors.surface, alignItems: "center", justifyContent: "center", ...shadow.card },
  name: { fontSize: 24, fontWeight: "800", color: colors.onSurface, letterSpacing: -0.3 },
  tag: { fontSize: 14, color: colors.muted, marginTop: 4 },
  metaRow: { flexDirection: "row", alignItems: "center", gap: 6, marginTop: spacing.md, flexWrap: "wrap" },
  ratingPill: { flexDirection: "row", alignItems: "center", gap: 3, backgroundColor: colors.success, paddingHorizontal: 7, paddingVertical: 3, borderRadius: 6 },
  ratingText: { color: colors.onBrandPrimary, fontSize: 12, fontWeight: "700" },
  meta: { fontSize: 12, color: colors.muted },
  dot: { color: colors.muted },
  catBadge: { alignSelf: "flex-start", marginTop: spacing.md, backgroundColor: colors.surfaceSecondary, paddingHorizontal: 10, paddingVertical: 5, borderRadius: radius.pill },
  catBadgeText: { fontSize: 11, fontWeight: "700", color: colors.onSurface, letterSpacing: 0.4 },
  priceRow: { flexDirection: "row", alignItems: "center", marginTop: spacing.xl, backgroundColor: colors.surfaceSecondary, borderRadius: radius.lg, padding: spacing.md },
  priceCol: { flex: 1 },
  priceDivider: { width: 1, height: 36, backgroundColor: colors.border },
  priceLabel: { fontSize: 10, fontWeight: "700", color: colors.muted, letterSpacing: 0.5 },
  priceValue: { fontSize: 15, fontWeight: "700", color: colors.onSurface, marginTop: 4 },
  sectionTitle: { fontSize: 15, fontWeight: "700", color: colors.onSurface, marginTop: spacing.xl },
  about: { fontSize: 13, color: colors.onSurfaceSecondary, lineHeight: 20, marginTop: spacing.sm },
  offerRow: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm, marginTop: spacing.md },
  offerPill: { flexDirection: "row", alignItems: "center", gap: 4, backgroundColor: colors.surfaceSecondary, paddingHorizontal: 10, paddingVertical: 6, borderRadius: radius.pill, borderWidth: 1, borderColor: colors.border },
  offerText: { fontSize: 12, color: colors.onSurface, fontWeight: "600" },
  disclaimer: { fontSize: 11, color: colors.muted, marginTop: spacing.xl, lineHeight: 16 },
  bottomBar: { flexDirection: "row", gap: spacing.md, paddingHorizontal: spacing.xl, paddingTop: spacing.md, backgroundColor: colors.surface, borderTopWidth: 1, borderTopColor: colors.border, position: "absolute", left: 0, right: 0, bottom: 0 },
  secondaryBtn: { flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 6, paddingHorizontal: 20, height: 52, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface },
  secondaryText: { color: colors.onSurface, fontWeight: "700", fontSize: 14 },
  primaryBtn: { flex: 1, height: 52, borderRadius: radius.md, backgroundColor: colors.brandPrimary, alignItems: "center", justifyContent: "center", ...shadow.card },
  primaryText: { color: colors.onBrandPrimary, fontWeight: "700", fontSize: 15 },
  sheetOverlay: { position: "absolute", top: 0, left: 0, right: 0, bottom: 0, justifyContent: "flex-end" },
  sheetBackdrop: { position: "absolute", top: 0, left: 0, right: 0, bottom: 0, backgroundColor: "rgba(10, 25, 47, 0.4)" },
  sheet: { backgroundColor: colors.surface, borderTopLeftRadius: 24, borderTopRightRadius: 24 },
  sheetHandle: { alignSelf: "center", width: 40, height: 4, borderRadius: 2, backgroundColor: colors.border, marginBottom: spacing.md },
  sheetTitle: { fontSize: 18, fontWeight: "800", color: colors.onSurface, textAlign: "center" },
  sheetSub: { fontSize: 13, color: colors.muted, marginTop: 6, marginBottom: spacing.lg, textAlign: "center" },
  input: { borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, borderRadius: radius.md, paddingHorizontal: spacing.md, height: 48, color: colors.onSurface, fontSize: 14, marginTop: spacing.sm },
  successIcon: { width: 56, height: 56, borderRadius: 28, backgroundColor: colors.success, alignItems: "center", justifyContent: "center", marginBottom: spacing.md },
});
