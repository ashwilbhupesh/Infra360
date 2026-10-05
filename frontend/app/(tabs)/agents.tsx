import React, { useEffect, useMemo, useState } from "react";
import { View, Text, StyleSheet, ScrollView, TextInput, Pressable, ActivityIndicator, FlatList } from "react-native";
import { Image } from "expo-image";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";
import { tierColor, tierBgColor } from "@/src/utils/tier";
import { HeaderLocationPill } from "@/src/components/header-location-pill";

type AgentCategory = { id: string; name: string; icon: string; description: string; agents_count: number };
type Agent = {
  id: string; category_id: string; name: string; firm?: string; city: string; area: string;
  rating: number; reviews: number; verified: boolean; featured: boolean;
  years_exp: number; languages: string[]; specialties: string[]; coverage: string[];
  rera_id?: string | null; phone: string; whatsapp?: string; image: string; about: string;
  tier?: string;
};

export default function Agents() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [cats, setCats] = useState<AgentCategory[]>([]);
  const [featured, setFeatured] = useState<Agent[]>([]);
  const [q, setQ] = useState("");
  const [searchResults, setSearchResults] = useState<Agent[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [c, f] = await Promise.all([
          api.get<AgentCategory[]>("/agent-categories"),
          api.get<Agent[]>("/agents?featured_only=true"),
        ]);
        setCats(c);
        setFeatured(f);
      } finally { setLoading(false); }
    })();
  }, []);

  useEffect(() => {
    const t = setTimeout(async () => {
      if (!q.trim()) { setSearchResults(null); return; }
      try {
        const r = await api.get<Agent[]>(`/agents?q=${encodeURIComponent(q.trim())}`);
        setSearchResults(r);
      } catch { setSearchResults([]); }
    }, 350);
    return () => clearTimeout(t);
  }, [q]);

  const renderRow = (a: Agent) => (
    <Pressable
      key={a.id}
      testID={`agent-card-${a.id}`}
      onPress={() => router.push(`/agent/${a.id}` as any)}
      style={styles.card}
    >
      <Image source={{ uri: a.image }} style={styles.img} contentFit="cover" transition={200} />
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
            {a.specialties.slice(0, 2).map(s => (
              <View key={s} style={styles.specPill}><Text style={styles.specText}>{s}</Text></View>
            ))}
          </View>
        ) : null}
      </View>
    </Pressable>
  );

  return (
    <View style={{ flex: 1, backgroundColor: colors.surfaceSecondary }}>
      <View style={{ paddingTop: insets.top + spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border }}>
        <View style={{ paddingHorizontal: spacing.xl }}>
          <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between", gap: spacing.sm, marginBottom: spacing.sm }}>
            <HeaderLocationPill testID="experts-location-pill" compact />
            <View style={{ flexDirection: "row", gap: 6 }}>
              <Pressable
                testID="experts-register-btn"
                onPress={() => router.push({ pathname: "/register", params: { type: "expert" } } as any)}
                style={styles.registerBtn}
                hitSlop={6}
              >
                <Icon name="add" size={14} color={colors.onBrandPrimary} />
                <Text style={styles.registerBtnText}>Register</Text>
              </Pressable>
              <Pressable
                testID="agents-menu-btn"
                onPress={() => router.push("/profile" as any)}
                style={styles.menuBtn}
                hitSlop={10}
              >
                <Icon name="settings-outline" size={20} color={colors.onSurface} />
              </Pressable>
            </View>
          </View>
          <View style={{ flexDirection: "row", alignItems: "flex-start", justifyContent: "space-between" }}>
            <View style={{ flex: 1 }}>
              <Text style={styles.title}>Experts</Text>
              <Text style={styles.sub}>Brokers, JDA liaison, lawyers & loan advisors — verified.</Text>
            </View>
          </View>
          <View style={styles.searchWrap}>
            <Icon name="search" size={18} color={colors.muted} />
            <TextInput
              testID="agent-search-input"
              placeholder="Broker, JDA, lawyer, loan, plot..."
              placeholderTextColor={colors.muted}
              value={q}
              onChangeText={setQ}
              style={styles.searchInput}
              returnKeyType="search"
            />
            {q ? (
              <Pressable onPress={() => setQ("")} hitSlop={10}><Icon name="close-circle" size={18} color={colors.muted} /></Pressable>
            ) : null}
          </View>
        </View>
      </View>

      {loading ? (
        <ActivityIndicator color={colors.brand} style={{ marginTop: spacing.xxl }} />
      ) : q ? (
        <FlatList
          data={searchResults ?? []}
          keyExtractor={(a) => a.id}
          renderItem={({ item }) => renderRow(item)}
          contentContainerStyle={{ padding: spacing.xl, paddingBottom: spacing.xxxl }}
          ListEmptyComponent={<Text style={styles.empty}>{searchResults === null ? "Searching…" : "No agents matched."}</Text>}
        />
      ) : (
        <ScrollView contentContainerStyle={{ paddingBottom: spacing.xxxl }}>
          <Text style={styles.sectionKicker}>BROWSE BY ROLE</Text>
          <View style={styles.catGrid}>
            {cats.map(c => (
              <Pressable
                key={c.id}
                testID={`agent-cat-${c.id}`}
                onPress={() => router.push(`/agent-category/${c.id}` as any)}
                style={styles.catTile}
              >
                <View style={styles.catIconWrap}>
                  <Icon name={c.icon as any} size={24} color={colors.brandPrimary} />
                </View>
                <Text style={styles.catName} numberOfLines={2}>{c.name}</Text>
                <Text style={styles.catCount}>{c.agents_count} listed</Text>
              </Pressable>
            ))}
          </View>

          {featured.length > 0 && (
            <View style={{ marginTop: spacing.xl }}>
              <View style={styles.sectionHeader}>
                <Text style={styles.sectionTitle}>Top agents in Jaipur</Text>
              </View>
              <View style={{ paddingHorizontal: spacing.xl }}>
                {featured.map(renderRow)}
              </View>
            </View>
          )}

          <View style={styles.infoBox}>
            <Icon name="shield-checkmark-outline" size={18} color={colors.brandPrimary} />
            <Text style={styles.infoText}>
              Verified agents share their RERA number and firm details. Always confirm identity and paperwork before making any payment.
            </Text>
          </View>
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  title: { fontSize: 26, fontWeight: "800", color: colors.onSurface, letterSpacing: -0.3 },
  sub: { fontSize: 13, color: colors.muted, marginTop: 4 },
  menuBtn: {
    width: 36, height: 36, borderRadius: 18,
    backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border,
    alignItems: "center", justifyContent: "center",
  },
  registerBtn: {
    flexDirection: "row", alignItems: "center", gap: 4,
    paddingHorizontal: spacing.sm + 2, height: 36, borderRadius: radius.pill,
    backgroundColor: colors.brandPrimary,
  },
  registerBtnText: { color: colors.onBrandPrimary, fontSize: 12, fontWeight: "800" },
  searchWrap: {
    flexDirection: "row", alignItems: "center", gap: 10,
    backgroundColor: colors.surfaceSecondary, borderRadius: radius.lg,
    paddingHorizontal: spacing.md, height: 46, marginTop: spacing.md, marginBottom: spacing.md,
    borderWidth: 1, borderColor: colors.border,
  },
  searchInput: { flex: 1, color: colors.onSurface, fontSize: 14 },
  sectionKicker: { fontSize: 10, fontWeight: "800", color: colors.muted, letterSpacing: 1, marginTop: spacing.xl, marginBottom: spacing.md, paddingHorizontal: spacing.xl },
  catGrid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.md, paddingHorizontal: spacing.xl },
  catTile: {
    width: "48%",
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  catIconWrap: { width: 40, height: 40, borderRadius: 20, backgroundColor: colors.surfaceSecondary, alignItems: "center", justifyContent: "center", marginBottom: spacing.sm },
  catName: { fontSize: 14, fontWeight: "700", color: colors.onSurface },
  catCount: { fontSize: 11, color: colors.muted, marginTop: 2 },
  sectionHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingHorizontal: spacing.xl, marginBottom: spacing.md },
  sectionTitle: { fontSize: 18, fontWeight: "700", color: colors.onSurface },
  card: { flexDirection: "row", gap: spacing.md, padding: spacing.md, marginBottom: spacing.md, backgroundColor: colors.surface, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border },
  img: { width: 68, height: 68, borderRadius: 34, backgroundColor: colors.surfaceSecondary },
  name: { fontSize: 15, fontWeight: "700", color: colors.onSurface, flex: 1 },
  firm: { fontSize: 12, color: colors.muted, marginTop: 2 },
  metaRow: { flexDirection: "row", alignItems: "center", gap: 8, marginTop: 8 },
  ratingPill: { flexDirection: "row", alignItems: "center", gap: 3, backgroundColor: colors.success, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 6 },
  ratingText: { color: colors.onBrandPrimary, fontSize: 11, fontWeight: "700" },
  meta: { fontSize: 11, color: colors.muted, flex: 1 },
  pillsRow: { flexDirection: "row", gap: 4, marginTop: 8 },
  specPill: { backgroundColor: colors.surfaceSecondary, paddingHorizontal: 8, paddingVertical: 3, borderRadius: radius.pill },
  specText: { fontSize: 10, color: colors.onSurface, fontWeight: "600" },
  tierBadge: { flexDirection: "row", alignItems: "center", gap: 3, paddingHorizontal: 6, paddingVertical: 2, borderRadius: radius.pill },
  tierText: { fontSize: 10, fontWeight: "800", letterSpacing: 0.3 },
  empty: { textAlign: "center", color: colors.muted, marginTop: spacing.xxl, fontSize: 13 },
  infoBox: { flexDirection: "row", gap: spacing.sm, marginHorizontal: spacing.xl, marginTop: spacing.xxl, padding: spacing.md, borderRadius: radius.md, backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border },
  infoText: { flex: 1, fontSize: 12, color: colors.onSurfaceSecondary, lineHeight: 17 },
});
