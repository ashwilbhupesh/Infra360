import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, ActivityIndicator } from "react-native";
import { Image } from "expo-image";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useLocalSearchParams, useRouter, Stack } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius } from "@/src/theme";
import { api } from "@/src/api";

type Supplier = {
  id: string; name: string; tagline: string; area: string; rating: number; reviews: number;
  verified: boolean; featured: boolean; starting_price: string; offerings: string[]; image: string;
};
type Category = { id: string; name: string; image: string };

export default function MarketCategoryPage() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [cat, setCat] = useState<Category | null>(null);
  const [loading, setLoading] = useState(true);
  const [verifiedOnly, setVerifiedOnly] = useState(false);
  const [sort, setSort] = useState<"rating" | "reviews">("rating");

  useEffect(() => {
    (async () => {
      try {
        const cats = await api.get<Category[]>(`/market/categories`);
        setCat(cats.find(c => c.id === id) || null);
        const s = await api.get<Supplier[]>(`/market/suppliers?category_id=${id}${verifiedOnly ? "&verified_only=true" : ""}`);
        setSuppliers(s);
      } finally { setLoading(false); }
    })();
  }, [id, verifiedOnly]);

  const sorted = [...suppliers].sort((a, b) => sort === "rating" ? b.rating - a.rating : b.reviews - a.reviews);

  return (
    <View style={{ flex: 1, backgroundColor: colors.surfaceSecondary }}>
      <Stack.Screen options={{ headerShown: false }} />
      <View style={{ paddingTop: insets.top + spacing.md, paddingHorizontal: spacing.xl, paddingBottom: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border }}>
        <View style={{ flexDirection: "row", alignItems: "center", gap: spacing.sm }}>
          <Pressable testID="cat-back-btn" onPress={() => router.back()} hitSlop={12}>
            <Icon name="chevron-back" size={26} color={colors.onSurface} />
          </Pressable>
          <View style={{ flex: 1 }}>
            <Text style={styles.title} numberOfLines={1}>{cat?.name ?? "Suppliers"}</Text>
            <Text style={styles.sub}>{sorted.length} listed in Jaipur</Text>
          </View>
        </View>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chipsRow}>
          <Pressable testID="sort-rating" onPress={() => setSort("rating")} style={[styles.chip, sort === "rating" && styles.chipActive]}>
            <Text style={[styles.chipText, sort === "rating" && styles.chipTextActive]}>Top rated</Text>
          </Pressable>
          <Pressable testID="sort-reviews" onPress={() => setSort("reviews")} style={[styles.chip, sort === "reviews" && styles.chipActive]}>
            <Text style={[styles.chipText, sort === "reviews" && styles.chipTextActive]}>Most reviewed</Text>
          </Pressable>
          <Pressable testID="filter-verified" onPress={() => setVerifiedOnly(v => !v)} style={[styles.chip, verifiedOnly && styles.chipActive]}>
            <Icon name="shield-checkmark-outline" size={13} color={verifiedOnly ? colors.onBrandPrimary : colors.onSurface} />
            <Text style={[styles.chipText, verifiedOnly && styles.chipTextActive]}>Verified only</Text>
          </Pressable>
        </ScrollView>
      </View>

      {loading ? (
        <ActivityIndicator color={colors.brand} style={{ marginTop: spacing.xxl }} />
      ) : (
        <ScrollView contentContainerStyle={{ padding: spacing.xl, paddingBottom: spacing.xxxl }}>
          {sorted.length === 0 && <Text style={styles.empty}>No suppliers match. Try removing filters.</Text>}
          {sorted.map(s => (
            <Pressable
              key={s.id}
              testID={`supplier-card-${s.id}`}
              onPress={() => router.push(`/supplier/${s.id}` as any)}
              style={styles.card}
            >
              <Image source={{ uri: s.image }} style={styles.img} contentFit="cover" />
              <View style={{ flex: 1 }}>
                <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
                  <Text style={styles.name} numberOfLines={1}>{s.name}</Text>
                  {s.verified && <Icon name="shield-checkmark" size={14} color={colors.success} />}
                </View>
                <Text style={styles.tag} numberOfLines={1}>{s.tagline}</Text>
                <View style={styles.metaRow}>
                  <View style={styles.ratingPill}>
                    <Icon name="star" size={11} color={colors.onBrandPrimary} />
                    <Text style={styles.ratingText}>{s.rating.toFixed(1)}</Text>
                  </View>
                  <Text style={styles.meta} numberOfLines={1}>{s.reviews} · {s.area}</Text>
                </View>
                {s.offerings?.length ? (
                  <View style={styles.offeringsRow}>
                    {s.offerings.slice(0, 3).map(o => (
                      <View key={o} style={styles.offeringPill}><Text style={styles.offeringText}>{o}</Text></View>
                    ))}
                  </View>
                ) : null}
                {s.starting_price && s.starting_price !== "—" ? (
                  <Text style={styles.price}>from {s.starting_price}</Text>
                ) : null}
              </View>
            </Pressable>
          ))}
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  title: { fontSize: 22, fontWeight: "800", color: colors.onSurface, letterSpacing: -0.2 },
  sub: { fontSize: 12, color: colors.muted, marginTop: 2 },
  chipsRow: { gap: spacing.sm, paddingVertical: spacing.md },
  chip: { flexDirection: "row", alignItems: "center", gap: 4, paddingHorizontal: 12, height: 32, borderRadius: radius.pill, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, flexShrink: 0 },
  chipActive: { backgroundColor: colors.brandPrimary, borderColor: colors.brandPrimary },
  chipText: { color: colors.onSurface, fontSize: 12, fontWeight: "600" },
  chipTextActive: { color: colors.onBrandPrimary },
  card: { flexDirection: "row", gap: spacing.md, padding: spacing.md, marginBottom: spacing.md, backgroundColor: colors.surface, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border },
  img: { width: 84, height: 100, borderRadius: radius.md, backgroundColor: colors.surfaceSecondary },
  name: { fontSize: 15, fontWeight: "700", color: colors.onSurface, flex: 1 },
  tag: { fontSize: 12, color: colors.muted, marginTop: 2 },
  metaRow: { flexDirection: "row", alignItems: "center", gap: 8, marginTop: 8 },
  ratingPill: { flexDirection: "row", alignItems: "center", gap: 3, backgroundColor: colors.success, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 6 },
  ratingText: { color: colors.onBrandPrimary, fontSize: 11, fontWeight: "700" },
  meta: { fontSize: 11, color: colors.muted, flex: 1 },
  offeringsRow: { flexDirection: "row", flexWrap: "wrap", gap: 4, marginTop: 8 },
  offeringPill: { backgroundColor: colors.surfaceSecondary, paddingHorizontal: 8, paddingVertical: 3, borderRadius: radius.pill },
  offeringText: { fontSize: 10, color: colors.onSurface, fontWeight: "600" },
  price: { fontSize: 12, color: colors.brandPrimary, fontWeight: "700", marginTop: 8 },
  empty: { textAlign: "center", color: colors.muted, marginTop: spacing.xxl, fontSize: 13 },
});
