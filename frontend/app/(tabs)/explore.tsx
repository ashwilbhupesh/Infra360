import React, { useEffect, useState } from "react";
import { View, Text, ScrollView, Pressable, StyleSheet, TextInput, ActivityIndicator, RefreshControl } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";
import { useAuth } from "@/src/auth-context";
import { LocalityCard, Locality } from "@/src/components/locality-card";
import { PropertyCard, Property } from "@/src/components/property-card";

const CATEGORIES = [
  { key: "Apartment", label: "Buy", icon: "home-outline" },
  { key: "Rent", label: "Rent", icon: "key-outline" },
  { key: "Residential Plot", label: "Plots", icon: "grid-outline" },
  { key: "Agricultural Land", label: "Agri", icon: "leaf-outline" },
  { key: "Commercial", label: "Commercial", icon: "business-outline" },
  { key: "Villa", label: "Villa", icon: "diamond-outline" },
];

export default function Explore() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { user } = useAuth();
  const [localities, setLocalities] = useState<Locality[]>([]);
  const [featured, setFeatured] = useState<Property[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = async () => {
    try {
      const [locs, props] = await Promise.all([
        api.get<Locality[]>("/localities"),
        api.get<Property[]>("/properties?verified_only=true&limit=6"),
      ]);
      setLocalities(locs);
      setFeatured(props);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => { load(); }, []);

  const submitSearch = () => {
    router.push({ pathname: "/(tabs)/map", params: { q: search } });
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <ScrollView
        contentContainerStyle={{ paddingTop: insets.top + spacing.md, paddingBottom: spacing.xxl }}
        showsVerticalScrollIndicator={false}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); load(); }} />}
      >
        <View style={styles.header}>
          <View>
            <Text style={styles.hi}>Hi, {user?.name?.split(" ")[0] || "there"}</Text>
            <Text style={styles.brand}>InfraLocal</Text>
          </View>
          <Pressable testID="header-list-property-btn" onPress={() => router.push("/list-property")} style={styles.listBtn}>
            <Icon name="add" size={16} color={colors.onBrandPrimary} />
            <Text style={styles.listBtnText}>List</Text>
          </Pressable>
        </View>

        <View style={styles.heroBlock}>
          <Text style={styles.hero}>Understand a locality{"\n"}before you invest in it.</Text>
          <Text style={styles.heroSub}>Prices, DLC rates, infrastructure & hyperlocal market intelligence.</Text>
        </View>

        <View style={styles.searchWrap}>
          <Icon name="search-outline" size={18} color={colors.muted} />
          <TextInput
            testID="home-search-input"
            style={styles.searchInput}
            placeholder="Search Jaipur, Ajmer Road, Jagatpura..."
            placeholderTextColor={colors.muted}
            value={search}
            onChangeText={setSearch}
            onSubmitEditing={submitSearch}
            returnKeyType="search"
          />
        </View>

        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chipsRow}>
          {CATEGORIES.map((c) => (
            <Pressable
              key={c.key}
              testID={`category-chip-${c.key.replace(/\s/g, "-").toLowerCase()}`}
              onPress={() => router.push({ pathname: "/(tabs)/map", params: { type: c.key } })}
              style={styles.chip}
            >
              <Icon name={c.icon as any} size={14} color={colors.brand} />
              <Text style={styles.chipText}>{c.label}</Text>
            </Pressable>
          ))}
        </ScrollView>

        <Pressable testID="explore-map-cta" style={styles.mapCta} onPress={() => router.push("/(tabs)/map")}>
          <View style={{ flex: 1 }}>
            <Text style={styles.mapCtaTitle}>Explore on Map</Text>
            <Text style={styles.mapCtaSub}>Zillow-style search with live property pins</Text>
          </View>
          <Icon name="arrow-forward" size={20} color={colors.onBrandPrimary} />
        </Pressable>

        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Trending Localities</Text>
          <Text style={styles.sectionCount}>{localities.length}</Text>
        </View>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ paddingHorizontal: spacing.xl, gap: spacing.md }}>
          {loading ? <ActivityIndicator style={{ marginVertical: spacing.xl }} color={colors.brand} /> :
            localities.map((l) => <LocalityCard key={l.id} locality={l} />)}
        </ScrollView>

        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Featured Properties</Text>
          <Pressable onPress={() => router.push("/(tabs)/map")}><Text style={styles.viewAll}>See all</Text></Pressable>
        </View>
        <View style={{ paddingHorizontal: spacing.xl }}>
          {featured.map((p) => <PropertyCard key={p.id} property={p} />)}
        </View>

        <View style={styles.infoBlock}>
          <Text style={styles.infoTitle}>How InfraValue™ Works</Text>
          <Text style={styles.infoBody}>
            InfraValue combines active listings, locality data, and government valuation to produce a market
            range for any property. It is an estimate, never a formal valuation. Every locality page shows
            confidence level and methodology.
          </Text>
        </View>

        <Text style={styles.footer}>Demo data for Jaipur • Real datasets can be integrated later</Text>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingHorizontal: spacing.xl, marginBottom: spacing.md },
  hi: { color: colors.muted, fontSize: 12, letterSpacing: 0.5, textTransform: "uppercase", fontWeight: "600" },
  brand: { color: colors.brand, fontSize: 22, fontWeight: "700", letterSpacing: -0.3 },
  listBtn: { flexDirection: "row", alignItems: "center", gap: 4, backgroundColor: colors.brandPrimary, paddingHorizontal: spacing.md, paddingVertical: spacing.sm, borderRadius: radius.pill },
  listBtnText: { color: colors.onBrandPrimary, fontWeight: "700", fontSize: 12 },
  heroBlock: { paddingHorizontal: spacing.xl, marginTop: spacing.md, marginBottom: spacing.lg },
  hero: { fontSize: 26, fontWeight: "700", color: colors.brand, lineHeight: 32, letterSpacing: -0.5 },
  heroSub: { color: colors.muted, marginTop: spacing.sm, fontSize: 14 },
  searchWrap: {
    flexDirection: "row", alignItems: "center", marginHorizontal: spacing.xl, paddingHorizontal: spacing.lg,
    height: 48, borderRadius: radius.md, backgroundColor: colors.surfaceSecondary,
    borderWidth: 1, borderColor: colors.border, gap: spacing.sm,
  },
  searchInput: { flex: 1, fontSize: 15, color: colors.onSurface },
  chipsRow: { paddingHorizontal: spacing.xl, gap: spacing.sm, paddingVertical: spacing.md },
  chip: { flexDirection: "row", alignItems: "center", gap: 6, paddingHorizontal: spacing.md, paddingVertical: spacing.sm, backgroundColor: colors.surfaceSecondary, borderRadius: radius.pill, borderWidth: 1, borderColor: colors.border, flexShrink: 0 },
  chipText: { color: colors.onSurface, fontSize: 13, fontWeight: "500" },
  mapCta: {
    flexDirection: "row", alignItems: "center", marginHorizontal: spacing.xl, marginTop: spacing.sm,
    padding: spacing.lg, borderRadius: radius.lg, backgroundColor: colors.brand,
    ...shadow.card,
  },
  mapCtaTitle: { color: colors.onBrand, fontSize: 16, fontWeight: "700" },
  mapCtaSub: { color: "#B3BAC5", fontSize: 12, marginTop: 2 },
  sectionHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingHorizontal: spacing.xl, marginTop: spacing.xxl, marginBottom: spacing.md },
  sectionTitle: { fontSize: 18, fontWeight: "700", color: colors.onSurface, letterSpacing: -0.3 },
  sectionCount: { color: colors.muted, fontSize: 12, fontWeight: "600" },
  viewAll: { color: colors.brandPrimary, fontSize: 13, fontWeight: "600" },
  infoBlock: { marginHorizontal: spacing.xl, marginTop: spacing.xxl, padding: spacing.lg, borderRadius: radius.lg, backgroundColor: colors.brandTertiary },
  infoTitle: { fontSize: 15, fontWeight: "700", color: colors.brand },
  infoBody: { fontSize: 13, color: colors.onSurfaceSecondary, marginTop: spacing.sm, lineHeight: 20 },
  footer: { textAlign: "center", color: colors.muted, fontSize: 11, marginTop: spacing.xxl },
});
