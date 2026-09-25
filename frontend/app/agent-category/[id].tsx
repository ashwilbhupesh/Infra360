import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, ActivityIndicator } from "react-native";
import { Image } from "expo-image";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useLocalSearchParams, useRouter, Stack } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius } from "@/src/theme";
import { api } from "@/src/api";
import { tierColor, tierBgColor } from "@/src/utils/tier";

type Agent = {
  id: string; name: string; firm?: string; area: string; rating: number; reviews: number;
  verified: boolean; years_exp: number; specialties: string[]; image: string; tier?: string;
};
type Category = { id: string; name: string; description: string };

export default function AgentCategoryPage() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [cat, setCat] = useState<Category | null>(null);
  const [loading, setLoading] = useState(true);
  const [verifiedOnly, setVerifiedOnly] = useState(false);
  const [sort, setSort] = useState<"rating" | "years">("rating");

  useEffect(() => {
    (async () => {
      try {
        const cats = await api.get<Category[]>(`/agent-categories`);
        setCat(cats.find(c => c.id === id) || null);
        const a = await api.get<Agent[]>(`/agents?category_id=${id}${verifiedOnly ? "&verified_only=true" : ""}`);
        setAgents(a);
      } finally { setLoading(false); }
    })();
  }, [id, verifiedOnly]);

  const sorted = [...agents].sort((a, b) =>
    sort === "rating" ? b.rating - a.rating : b.years_exp - a.years_exp
  );

  return (
    <View style={{ flex: 1, backgroundColor: colors.surfaceSecondary }}>
      <Stack.Screen options={{ headerShown: false }} />
      <View style={{ paddingTop: insets.top + spacing.md, paddingHorizontal: spacing.xl, paddingBottom: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border }}>
        <View style={{ flexDirection: "row", alignItems: "center", gap: spacing.sm }}>
          <Pressable testID="agent-cat-back-btn" onPress={() => router.back()} hitSlop={12}>
            <Icon name="chevron-back" size={26} color={colors.onSurface} />
          </Pressable>
          <View style={{ flex: 1 }}>
            <Text style={styles.title} numberOfLines={1}>{cat?.name ?? "Agents"}</Text>
            {cat?.description ? <Text style={styles.sub}>{cat.description}</Text> : null}
          </View>
        </View>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chipsRow}>
          <Pressable testID="sort-agent-rating" onPress={() => setSort("rating")} style={[styles.chip, sort === "rating" && styles.chipActive]}>
            <Text style={[styles.chipText, sort === "rating" && styles.chipTextActive]}>Top rated</Text>
          </Pressable>
          <Pressable testID="sort-agent-years" onPress={() => setSort("years")} style={[styles.chip, sort === "years" && styles.chipActive]}>
            <Text style={[styles.chipText, sort === "years" && styles.chipTextActive]}>Most experienced</Text>
          </Pressable>
          <Pressable testID="filter-verified-agent" onPress={() => setVerifiedOnly(v => !v)} style={[styles.chip, verifiedOnly && styles.chipActive]}>
            <Icon name="shield-checkmark-outline" size={13} color={verifiedOnly ? colors.onBrandPrimary : colors.onSurface} />
            <Text style={[styles.chipText, verifiedOnly && styles.chipTextActive]}>Verified only</Text>
          </Pressable>
        </ScrollView>
      </View>

      {loading ? (
        <ActivityIndicator color={colors.brand} style={{ marginTop: spacing.xxl }} />
      ) : (
        <ScrollView contentContainerStyle={{ padding: spacing.xl, paddingBottom: spacing.xxxl }}>
          {sorted.length === 0 && <Text style={styles.empty}>No agents match. Try removing filters.</Text>}
          {sorted.map(a => (
            <Pressable
              key={a.id}
              testID={`agent-card-${a.id}`}
              onPress={() => router.push(`/agent/${a.id}` as any)}
              style={styles.card}
            >
              <Image source={{ uri: a.image }} style={styles.img} contentFit="cover" />
              <View style={{ flex: 1 }}>
                <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
                  <Text style={styles.name} numberOfLines={1}>{a.name}</Text>
                  {a.verified && <Icon name="shield-checkmark" size={14} color={colors.success} />}
                  {a.tier && a.tier !== "Unverified" && (
                    <View style={[styles.tierBadge, { backgroundColor: tierBgColor(a.tier) }]}>
                      <Icon name="ribbon" size={10} color={tierColor(a.tier)} />
                      <Text style={[styles.tierText, { color: tierColor(a.tier) }]}>{a.tier}</Text>
                    </View>
                  )}
                </View>
                {a.firm ? <Text style={styles.firm} numberOfLines={1}>{a.firm}</Text> : null}
                <View style={styles.metaRow}>
                  <View style={styles.ratingPill}>
                    <Icon name="star" size={11} color={colors.onBrandPrimary} />
                    <Text style={styles.ratingText}>{a.rating.toFixed(1)}</Text>
                  </View>
                  <Text style={styles.meta} numberOfLines={1}>{a.reviews} · {a.years_exp} yrs · {a.area}</Text>
                </View>
                {a.specialties?.length ? (
                  <View style={styles.pillsRow}>
                    {a.specialties.slice(0, 3).map(s => (
                      <View key={s} style={styles.specPill}><Text style={styles.specText}>{s}</Text></View>
                    ))}
                  </View>
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
  img: { width: 72, height: 72, borderRadius: 36, backgroundColor: colors.surfaceSecondary },
  name: { fontSize: 15, fontWeight: "700", color: colors.onSurface, flex: 1 },
  firm: { fontSize: 12, color: colors.muted, marginTop: 2 },
  metaRow: { flexDirection: "row", alignItems: "center", gap: 8, marginTop: 8 },
  ratingPill: { flexDirection: "row", alignItems: "center", gap: 3, backgroundColor: colors.success, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 6 },
  ratingText: { color: colors.onBrandPrimary, fontSize: 11, fontWeight: "700" },
  meta: { fontSize: 11, color: colors.muted, flex: 1 },
  pillsRow: { flexDirection: "row", flexWrap: "wrap", gap: 4, marginTop: 8 },
  specPill: { backgroundColor: colors.surfaceSecondary, paddingHorizontal: 8, paddingVertical: 3, borderRadius: radius.pill },
  specText: { fontSize: 10, color: colors.onSurface, fontWeight: "600" },
  tierBadge: { flexDirection: "row", alignItems: "center", gap: 3, paddingHorizontal: 6, paddingVertical: 2, borderRadius: radius.pill },
  tierText: { fontSize: 10, fontWeight: "800", letterSpacing: 0.3 },
  empty: { textAlign: "center", color: colors.muted, marginTop: spacing.xxl, fontSize: 13 },
});
