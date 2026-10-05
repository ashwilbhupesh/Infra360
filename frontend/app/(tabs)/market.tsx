import React, { useEffect, useMemo, useState } from "react";
import { View, Text, StyleSheet, ScrollView, TextInput, Pressable, ActivityIndicator, FlatList, Dimensions } from "react-native";
import { Image } from "expo-image";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter, useFocusEffect } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";
import { useMaterialsCart } from "@/src/stores/materials-cart";

type Category = { id: string; group_id: string; name: string; image: string; suppliers_count?: number };
type Group = { id: string; name: string; subtitle: string; icon: string; categories: Category[] };
type Supplier = {
  id: string; category_id: string; name: string; tagline: string; city: string; area: string;
  rating: number; reviews: number; verified: boolean; featured: boolean;
  starting_price: string; min_project: string; offerings: string[]; phone: string; image: string;
};
type MaterialsCategory = { id: string; name: string; image: string; order: number; stores_count?: number };
type MaterialsProduct = {
  id: string; store_id: string; category_id: string; name: string; brand?: string;
  image: string; unit?: string; price: number; mrp?: number;
  store?: { id: string; name: string; area: string; rating: number; verified: boolean };
};

const MATERIALS_GROUP_ID = "grp-materials";
const screen = Dimensions.get("window");

export default function Market() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [groups, setGroups] = useState<Group[]>([]);
  const [featured, setFeatured] = useState<Supplier[]>([]);
  const [q, setQ] = useState("");
  const [searchResults, setSearchResults] = useState<Supplier[] | null>(null);
  const [productSearch, setProductSearch] = useState<MaterialsProduct[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeGroup, setActiveGroup] = useState<string>(MATERIALS_GROUP_ID);
  const [matCats, setMatCats] = useState<MaterialsCategory[]>([]);

  const hydrate = useMaterialsCart((s) => s.hydrate);
  const totalItems = useMaterialsCart((s) => s.totalItems());

  useEffect(() => { hydrate(); }, [hydrate]);

  useEffect(() => {
    (async () => {
      try {
        const [g, s, mc] = await Promise.all([
          api.get<Group[]>("/market/groups"),
          api.get<Supplier[]>("/market/suppliers?featured_only=true"),
          api.get<MaterialsCategory[]>("/materials/categories"),
        ]);
        setGroups(g);
        setFeatured(s);
        setMatCats(mc);
      } finally { setLoading(false); }
    })();
  }, []);

  useEffect(() => {
    const t = setTimeout(async () => {
      if (!q.trim()) { setSearchResults(null); setProductSearch(null); return; }
      try {
        if (activeGroup === MATERIALS_GROUP_ID) {
          const r = await api.get<MaterialsProduct[]>(`/materials/products?q=${encodeURIComponent(q.trim())}`);
          setProductSearch(r);
          setSearchResults(null);
        } else {
          const r = await api.get<Supplier[]>(`/market/suppliers?q=${encodeURIComponent(q.trim())}`);
          setSearchResults(r);
          setProductSearch(null);
        }
      } catch {
        if (activeGroup === MATERIALS_GROUP_ID) setProductSearch([]);
        else setSearchResults([]);
      }
    }, 350);
    return () => clearTimeout(t);
  }, [q, activeGroup]);

  const activeCategories = useMemo(() => {
    const g = groups.find(x => x.id === activeGroup);
    return g?.categories ?? [];
  }, [groups, activeGroup]);

  const isMaterials = activeGroup === MATERIALS_GROUP_ID;

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

  const renderProductSearchItem = ({ item }: { item: MaterialsProduct }) => (
    <Pressable
      key={item.id}
      testID={`mat-product-search-${item.id}`}
      onPress={() => router.push(`/materials/store/${item.store_id}` as any)}
      style={styles.productSearchCard}
    >
      <Image source={{ uri: item.image }} style={styles.productSearchImg} contentFit="cover" />
      <View style={{ flex: 1 }}>
        {item.brand ? <Text style={styles.productBrand}>{item.brand}</Text> : null}
        <Text style={styles.productName} numberOfLines={2}>{item.name}</Text>
        <View style={{ flexDirection: "row", alignItems: "baseline", gap: 6, marginTop: 4 }}>
          <Text style={styles.productPrice}>₹{item.price.toLocaleString("en-IN")}</Text>
          {item.unit ? <Text style={styles.productUnit}>/ {item.unit}</Text> : null}
        </View>
        {item.store ? (
          <Text style={styles.productStore} numberOfLines={1}>
            {item.store.name} · {item.store.area}
          </Text>
        ) : null}
      </View>
    </Pressable>
  );

  // --- Materials home: shopping-style layout ---
  const renderMaterialsHome = () => (
    <ScrollView contentContainerStyle={{ paddingBottom: spacing.xxxl }}>
      <Text style={styles.sectionHeading}>Shop by category</Text>
      <View style={styles.matGrid}>
        {matCats.map((c) => (
          <Pressable
            key={c.id}
            testID={`mat-cat-${c.id}`}
            onPress={() => router.push(`/materials/category/${c.id}` as any)}
            style={styles.matTile}
          >
            <View style={styles.matImgWrap}>
              <Image source={{ uri: c.image }} style={styles.matImg} contentFit="cover" transition={200} />
            </View>
            <Text style={styles.matName} numberOfLines={2}>{c.name}</Text>
          </Pressable>
        ))}
      </View>

      <View style={styles.parchaBanner}>
        <View style={{ flex: 1 }}>
          <Text style={styles.parchaTitle}>Stuck with a 'parcha'?</Text>
          <Text style={styles.parchaSub}>If you have a handwritten materials list, we'll quote it for you via WhatsApp.</Text>
        </View>
        <Pressable
          testID="bulk-order-btn"
          onPress={() => router.push("/contact-us" as any)}
          style={styles.parchaCta}
        >
          <Icon name="logo-whatsapp" size={16} color={colors.onSuccess} />
          <Text style={styles.parchaCtaText}>Bulk order?</Text>
        </Pressable>
      </View>

      <Text style={styles.footer}>Prices indicative · Final rates confirmed by store on enquiry</Text>
    </ScrollView>
  );

  return (
    <View style={{ flex: 1, backgroundColor: colors.surfaceSecondary }}>
      {/* Sticky header + search + group chips */}
      <View style={{ paddingTop: insets.top + spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border }}>
        <View style={{ paddingHorizontal: spacing.xl }}>
          <View style={{ flexDirection: "row", alignItems: "flex-start", justifyContent: "space-between" }}>
            <View style={{ flex: 1 }}>
              {isMaterials ? (
                <>
                  <Text style={styles.title}>Materials</Text>
                  <View style={{ flexDirection: "row", alignItems: "center", gap: 4, marginTop: 2 }}>
                    <Icon name="location-outline" size={13} color={colors.muted} />
                    <Text style={styles.sub}>Materials across <Text style={{ fontWeight: "700", color: colors.onSurface }}>Jaipur</Text></Text>
                  </View>
                </>
              ) : (
                <>
                  <Text style={styles.title}>Market</Text>
                  <Text style={styles.sub}>Everything from design to move-in, in one place.</Text>
                </>
              )}
            </View>
            {isMaterials && (
              <View style={{ flexDirection: "row", gap: 8 }}>
                <Pressable
                  testID="materials-cart-btn"
                  onPress={() => router.push("/materials/cart" as any)}
                  style={styles.cartBtn}
                  hitSlop={10}
                >
                  <Icon name="cart-outline" size={22} color={colors.onSurface} />
                  {totalItems > 0 && (
                    <View style={styles.cartBadge}>
                      <Text style={styles.cartBadgeText}>{totalItems > 99 ? "99+" : totalItems}</Text>
                    </View>
                  )}
                </Pressable>
                <Pressable
                  testID="market-menu-btn"
                  onPress={() => router.push("/profile" as any)}
                  style={styles.cartBtn}
                  hitSlop={10}
                >
                  <Icon name="menu-outline" size={22} color={colors.onSurface} />
                </Pressable>
              </View>
            )}
            {!isMaterials && (
              <Pressable
                testID="market-menu-btn"
                onPress={() => router.push("/profile" as any)}
                style={styles.cartBtn}
                hitSlop={10}
              >
                <Icon name="menu-outline" size={22} color={colors.onSurface} />
              </Pressable>
            )}
          </View>

          <View style={styles.searchWrap}>
            <Icon name="search" size={18} color={colors.muted} />
            <TextInput
              testID="market-search-input"
              placeholder={isMaterials ? 'Search for "LED panel"' : "Cement, architects, tiles, movers..."}
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
        isMaterials ? (
          <FlatList
            data={productSearch ?? []}
            keyExtractor={(p) => p.id}
            renderItem={renderProductSearchItem}
            contentContainerStyle={{ padding: spacing.xl, paddingBottom: spacing.xxxl }}
            ListEmptyComponent={<Text style={styles.empty}>{productSearch === null ? "Searching…" : "No products found."}</Text>}
          />
        ) : (
          <FlatList
            data={searchResults ?? []}
            keyExtractor={(s) => s.id}
            renderItem={({ item }) => renderSupplierRow(item)}
            contentContainerStyle={{ padding: spacing.xl, paddingBottom: spacing.xxxl }}
            ListEmptyComponent={<Text style={styles.empty}>{searchResults === null ? "Searching…" : "No suppliers found."}</Text>}
          />
        )
      ) : isMaterials ? (
        renderMaterialsHome()
      ) : (
        <ScrollView contentContainerStyle={{ paddingBottom: spacing.xxxl }}>
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

const TILE_W = (screen.width - spacing.xl * 2 - spacing.md * 2) / 3;

const styles = StyleSheet.create({
  title: { fontSize: 26, fontWeight: "800", color: colors.onSurface, letterSpacing: -0.3 },
  sub: { fontSize: 13, color: colors.muted, marginTop: 2 },
  cartBtn: {
    width: 44, height: 44, borderRadius: radius.pill,
    backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border,
    alignItems: "center", justifyContent: "center",
  },
  cartBadge: {
    position: "absolute", top: -4, right: -4,
    minWidth: 20, height: 20, borderRadius: 10, paddingHorizontal: 4,
    backgroundColor: colors.brandPrimary, alignItems: "center", justifyContent: "center",
    borderWidth: 2, borderColor: colors.surface,
  },
  cartBadgeText: { color: colors.onBrandPrimary, fontSize: 10, fontWeight: "800" },

  searchWrap: {
    flexDirection: "row", alignItems: "center", gap: 10,
    backgroundColor: colors.surfaceSecondary, borderRadius: radius.lg,
    paddingHorizontal: spacing.md, height: 48, marginTop: spacing.md,
    borderWidth: 1, borderColor: colors.border,
  },
  searchInput: { flex: 1, color: colors.onSurface, fontSize: 14 },

  groupChipsRow: { paddingHorizontal: spacing.xl, gap: spacing.sm, paddingVertical: spacing.md },
  groupChip: {
    flexDirection: "row", alignItems: "center", gap: 6,
    paddingHorizontal: 14, height: 36, borderRadius: radius.pill,
    borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, flexShrink: 0,
  },
  groupChipActive: { backgroundColor: colors.brandPrimary, borderColor: colors.brandPrimary },
  groupChipText: { color: colors.onSurface, fontSize: 13, fontWeight: "600" },
  groupChipTextActive: { color: colors.onBrandPrimary },

  // Non-materials grid (existing)
  section: { paddingHorizontal: spacing.xl, paddingTop: spacing.lg },
  groupSub: { color: colors.muted, fontSize: 13, marginBottom: spacing.md },
  catGrid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.md },
  catTile: {
    width: "48%", backgroundColor: colors.surface, borderRadius: radius.lg,
    overflow: "hidden", borderWidth: 1, borderColor: colors.border,
  },
  catImg: { width: "100%", height: 90, backgroundColor: colors.surfaceSecondary },
  catBody: { padding: spacing.md },
  catName: { fontSize: 14, fontWeight: "700", color: colors.onSurface },
  catCount: { fontSize: 11, color: colors.muted, marginTop: 2 },

  // Materials shopping-style 3-col grid
  sectionHeading: {
    fontSize: 20, fontWeight: "800", color: colors.onSurface,
    paddingHorizontal: spacing.xl, paddingTop: spacing.xl, paddingBottom: spacing.md,
    letterSpacing: -0.2,
  },
  matGrid: {
    flexDirection: "row", flexWrap: "wrap",
    paddingHorizontal: spacing.xl, columnGap: spacing.md, rowGap: spacing.lg,
  },
  matTile: { width: TILE_W, alignItems: "center" },
  matImgWrap: {
    width: TILE_W, height: TILE_W, borderRadius: radius.lg,
    backgroundColor: colors.surface, overflow: "hidden",
    borderWidth: 1, borderColor: colors.border,
    alignItems: "center", justifyContent: "center",
    ...shadow.card,
  },
  matImg: { width: "100%", height: "100%" },
  matName: {
    marginTop: spacing.sm, fontSize: 13, fontWeight: "600",
    color: colors.onSurface, textAlign: "center", lineHeight: 17,
  },

  parchaBanner: {
    flexDirection: "row", alignItems: "center", gap: spacing.md,
    margin: spacing.xl, padding: spacing.lg,
    backgroundColor: colors.brand, borderRadius: radius.lg,
  },
  parchaTitle: { color: colors.onBrand, fontSize: 15, fontWeight: "800" },
  parchaSub: { color: colors.onBrand, fontSize: 12, marginTop: 4, opacity: 0.8 },
  parchaCta: {
    flexDirection: "row", alignItems: "center", gap: 6,
    backgroundColor: colors.success, paddingVertical: 10, paddingHorizontal: 14,
    borderRadius: radius.pill,
  },
  parchaCtaText: { color: colors.onSuccess, fontSize: 12, fontWeight: "700" },

  sectionHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingHorizontal: spacing.xl, marginBottom: spacing.md },
  sectionTitle: { fontSize: 18, fontWeight: "700", color: colors.onSurface },
  supplierCard: {
    flexDirection: "row", gap: spacing.md, padding: spacing.md, marginBottom: spacing.md,
    backgroundColor: colors.surface, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border,
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

  // Product search card
  productSearchCard: {
    flexDirection: "row", gap: spacing.md, padding: spacing.md, marginBottom: spacing.sm,
    backgroundColor: colors.surface, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border,
  },
  productSearchImg: { width: 70, height: 70, borderRadius: radius.md, backgroundColor: colors.surfaceSecondary },
  productBrand: { fontSize: 10, fontWeight: "700", color: colors.brandPrimary, letterSpacing: 0.3, textTransform: "uppercase" },
  productName: { fontSize: 13, fontWeight: "600", color: colors.onSurface, marginTop: 2 },
  productPrice: { fontSize: 15, fontWeight: "800", color: colors.onSurface },
  productUnit: { fontSize: 11, color: colors.muted },
  productStore: { fontSize: 11, color: colors.muted, marginTop: 6 },
});
