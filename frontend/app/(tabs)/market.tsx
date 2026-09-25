import React, { useEffect, useMemo, useState } from "react";
import { View, Text, StyleSheet, ScrollView, TextInput, Pressable, ActivityIndicator, FlatList } from "react-native";
import { Image } from "expo-image";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";

type Category = { id: string; group_id: string; name: string; image: string; suppliers_count?: number };
type Group = { id: string; name: string; subtitle: string; icon: string; categories: Category[] };
type Supplier = {
  id: string; category_id: string; name: string; tagline: string; city: string; area: string;
  rating: number; reviews: number; verified: boolean; featured: boolean;
  starting_price: string; min_project: string; offerings: string[]; phone: string; image: string;
};

export default function Market() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [groups, setGroups] = useState<Group[]>([]);
  const [featured, setFeatured] = useState<Supplier[]>([]);
  const [q, setQ] = useState("");
  const [searchResults, setSearchResults] = useState<Supplier[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeGroup, setActiveGroup] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const [g, s] = await Promise.all([
          api.get<Group[]>("/market/groups"),
          api.get<Supplier[]>("/market/suppliers?featured_only=true"),
        ]);
        setGroups(g);
        setFeatured(s);
        if (g.length && !activeGroup) setActiveGroup(g[0].id);
      } finally { setLoading(false); }
    })();
  }, []);

  useEffect(() => {
    const t = setTimeout(async () => {
      if (!q.trim()) { setSearchResults(null); return; }
      try {
        const r = await api.get<Supplier[]>(`/market/suppliers?q=${encodeURIComponent(q.trim())}`);
        setSearchResults(r);
      } catch { setSearchResults([]); }
    }, 350);
    return () => clearTimeout(t);
  }, [q]);

  const activeCategories = useMemo(() => {
    const g = groups.find(x => x.id === activeGroup);
    return g?.categories ?? [];
  }, [groups, activeGroup]);

  const renderSupplierRow = (s: Supplier) => (
    <Pressable
      key={s.id}
      testID={`supplier-card-${s.id}`}
      onPress={() => router.push(`/supplier/${s.id}` as any)}
      style={styles.supplierCard}
    >
      <Image source={{ uri: s.image }} style={styles.supplierImg} contentFit="cover" transition={200} />
      <View style={{ flex: 1 }}>
        <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
          <Text style={styles.supplierName} numberOfLines={1}>{s.name}</Text>
          {s.verified && <Icon name="shield-checkmark" size={14} color={colors.success} />}
        </View>
        <Text style={styles.supplierTag} numberOfLines={1}>{s.tagline}</Text>
        <View style={styles.supplierMetaRow}>
          <View style={styles.ratingPill}>
            <Icon name="star" size={11} color={colors.onBrandPrimary} />
            <Text style={styles.ratingText}>{s.rating.toFixed(1)}</Text>
          </View>
          <Text style={styles.supplierMeta} numberOfLines={1}>{s.reviews} reviews · {s.area}</Text>
        </View>
        {s.starting_price && s.starting_price !== "—" ? (
          <Text style={styles.supplierPrice}>from {s.starting_price}</Text>
        ) : null}
      </View>
    </Pressable>
  );

  return (
    <View style={{ flex: 1, backgroundColor: colors.surfaceSecondary }}>
      {/* Sticky header + search + group chips */}
      <View style={{ paddingTop: insets.top + spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border }}>
        <View style={{ paddingHorizontal: spacing.xl }}>
          <Text style={styles.title}>Market</Text>
          <Text style={styles.sub}>Everything from design to move-in, in one place.</Text>
          <View style={styles.searchWrap}>
            <Icon name="search" size={18} color={colors.muted} />
            <TextInput
              testID="market-search-input"
              placeholder="Cement, architects, tiles, movers..."
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

        {!q && (
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.groupChipsRow}>
            {groups.map(g => {
              const active = activeGroup === g.id;
              return (
                <Pressable
                  key={g.id}
                  testID={`market-group-${g.id}`}
                  onPress={() => setActiveGroup(g.id)}
                  style={[styles.groupChip, active && styles.groupChipActive]}
                >
                  <Icon name={g.icon as any} size={16} color={active ? colors.onBrandPrimary : colors.onSurface} />
                  <Text style={[styles.groupChipText, active && styles.groupChipTextActive]}>{g.name}</Text>
                </Pressable>
              );
            })}
          </ScrollView>
        )}
      </View>

      {loading ? (
        <ActivityIndicator color={colors.brand} style={{ marginTop: spacing.xxl }} />
      ) : q ? (
        <FlatList
          data={searchResults ?? []}
          keyExtractor={(s) => s.id}
          renderItem={({ item }) => renderSupplierRow(item)}
          contentContainerStyle={{ padding: spacing.xl, paddingBottom: spacing.xxxl }}
          ListEmptyComponent={<Text style={styles.empty}>{searchResults === null ? "Searching…" : "No suppliers found."}</Text>}
        />
      ) : (
        <ScrollView contentContainerStyle={{ paddingBottom: spacing.xxxl }}>
          {/* Category grid */}
          <View style={styles.section}>
            {(() => {
              const g = groups.find(x => x.id === activeGroup);
              return g ? <Text style={styles.groupSub}>{g.subtitle}</Text> : null;
            })()}
            <View style={styles.catGrid}>
              {activeCategories.map(c => (
                <Pressable
                  key={c.id}
                  testID={`market-cat-${c.id}`}
                  onPress={() => router.push(`/market-category/${c.id}` as any)}
                  style={styles.catTile}
                >
                  <Image source={{ uri: c.image }} style={styles.catImg} contentFit="cover" />
                  <View style={styles.catBody}>
                    <Text style={styles.catName} numberOfLines={1}>{c.name}</Text>
                    <Text style={styles.catCount}>{c.suppliers_count ?? 0} listed</Text>
                  </View>
                </Pressable>
              ))}
            </View>
          </View>

          {/* Featured suppliers */}
          {featured.length > 0 && (
            <View style={{ marginTop: spacing.xl }}>
              <View style={styles.sectionHeader}>
                <Text style={styles.sectionTitle}>Featured near you</Text>
              </View>
              <View style={{ paddingHorizontal: spacing.xl }}>
                {featured.map(renderSupplierRow)}
              </View>
            </View>
          )}

          <Text style={styles.footer}>Demo directory · Real suppliers can be onboarded later</Text>
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  title: { fontSize: 26, fontWeight: "800", color: colors.onSurface, letterSpacing: -0.3 },
  sub: { fontSize: 13, color: colors.muted, marginTop: 4 },
  searchWrap: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    backgroundColor: colors.surfaceSecondary,
    borderRadius: radius.lg,
    paddingHorizontal: spacing.md,
    height: 46,
    marginTop: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  searchInput: { flex: 1, color: colors.onSurface, fontSize: 14 },
  groupChipsRow: { paddingHorizontal: spacing.xl, gap: spacing.sm, paddingVertical: spacing.md },
  groupChip: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    paddingHorizontal: 14,
    height: 36,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surface,
    flexShrink: 0,
  },
  groupChipActive: { backgroundColor: colors.brandPrimary, borderColor: colors.brandPrimary },
  groupChipText: { color: colors.onSurface, fontSize: 13, fontWeight: "600" },
  groupChipTextActive: { color: colors.onBrandPrimary },
  section: { paddingHorizontal: spacing.xl, paddingTop: spacing.lg },
  groupSub: { color: colors.muted, fontSize: 13, marginBottom: spacing.md },
  catGrid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.md },
  catTile: {
    width: "48%",
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    overflow: "hidden",
    borderWidth: 1,
    borderColor: colors.border,
  },
  catImg: { width: "100%", height: 90, backgroundColor: colors.surfaceSecondary },
  catBody: { padding: spacing.md },
  catName: { fontSize: 14, fontWeight: "700", color: colors.onSurface },
  catCount: { fontSize: 11, color: colors.muted, marginTop: 2 },
  sectionHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingHorizontal: spacing.xl, marginBottom: spacing.md },
  sectionTitle: { fontSize: 18, fontWeight: "700", color: colors.onSurface },
  supplierCard: {
    flexDirection: "row",
    gap: spacing.md,
    padding: spacing.md,
    marginBottom: spacing.md,
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.border,
  },
  supplierImg: { width: 84, height: 84, borderRadius: radius.md, backgroundColor: colors.surfaceSecondary },
  supplierName: { fontSize: 15, fontWeight: "700", color: colors.onSurface, flex: 1 },
  supplierTag: { fontSize: 12, color: colors.muted, marginTop: 2 },
  supplierMetaRow: { flexDirection: "row", alignItems: "center", gap: 8, marginTop: 8 },
  ratingPill: { flexDirection: "row", alignItems: "center", gap: 3, backgroundColor: colors.success, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 6 },
  ratingText: { color: colors.onBrandPrimary, fontSize: 11, fontWeight: "700" },
  supplierMeta: { fontSize: 11, color: colors.muted, flex: 1 },
  supplierPrice: { fontSize: 12, color: colors.brandPrimary, fontWeight: "700", marginTop: 6 },
  empty: { textAlign: "center", color: colors.muted, marginTop: spacing.xxl, fontSize: 13 },
  footer: { textAlign: "center", color: colors.muted, fontSize: 11, marginTop: spacing.xxxl, paddingHorizontal: spacing.xl },
});
