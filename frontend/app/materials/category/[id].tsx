import React, { useEffect, useMemo, useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, ActivityIndicator, FlatList } from "react-native";
import { Image } from "expo-image";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useLocalSearchParams, useRouter, Stack } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius } from "@/src/theme";
import { api } from "@/src/api";
import { useMaterialsCart } from "@/src/stores/materials-cart";

type Product = {
  id: string; store_id: string; category_id: string; name: string;
  brand?: string; image: string; unit?: string; price: number; mrp?: number;
};
type Store = {
  id: string; name: string; tagline: string; area: string; city: string;
  rating: number; reviews: number; verified: boolean; featured: boolean;
  delivery_mins?: number; min_order?: string; phone: string; image?: string;
  products: Product[]; products_count: number;
};
type Category = { id: string; name: string; image: string };

export default function MaterialsCategoryPage() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [cat, setCat] = useState<Category | null>(null);
  const [stores, setStores] = useState<Store[]>([]);
  const [loading, setLoading] = useState(true);
  const [verifiedOnly, setVerifiedOnly] = useState(false);
  const [sort, setSort] = useState<"featured" | "rating" | "price" | null>(null);

  const hydrate = useMaterialsCart((s) => s.hydrate);
  const totalItems = useMaterialsCart((s) => s.totalItems());
  const qtyOf = useMaterialsCart((s) => s.qtyOf);
  const add = useMaterialsCart((s) => s.add);
  const increment = useMaterialsCart((s) => s.increment);
  const decrement = useMaterialsCart((s) => s.decrement);

  useEffect(() => { hydrate(); }, [hydrate]);

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const [cats, s] = await Promise.all([
          api.get<Category[]>(`/materials/categories`),
          api.get<Store[]>(`/materials/categories/${id}/stores`),
        ]);
        setCat(cats.find((c) => c.id === id) || null);
        setStores(s);
      } finally { setLoading(false); }
    })();
  }, [id]);

  const visibleStores = useMemo(() => {
    let list = [...stores];
    if (verifiedOnly) list = list.filter((s) => s.verified);
    if (sort === "rating") list.sort((a, b) => b.rating - a.rating);
    else if (sort === "price") {
      list.sort((a, b) => {
        const aMin = Math.min(...(a.products.map((p) => p.price) || [Infinity]));
        const bMin = Math.min(...(b.products.map((p) => p.price) || [Infinity]));
        return aMin - bMin;
      });
    } else {
      list.sort((a, b) => (b.featured ? 1 : 0) - (a.featured ? 1 : 0) || b.rating - a.rating);
    }
    return list;
  }, [stores, verifiedOnly, sort]);

  const totalProducts = useMemo(
    () => stores.reduce((sum, s) => sum + s.products_count, 0),
    [stores]
  );

  const handleAdd = (p: Product, store: Store) => {
    add({
      id: p.id,
      store_id: store.id,
      store_name: store.name,
      store_phone: store.phone,
      name: p.name,
      brand: p.brand,
      image: p.image,
      unit: p.unit,
      price: p.price,
      category_id: p.category_id,
    });
  };

  const renderProductCard = (p: Product, store: Store) => {
    const qty = qtyOf(p.id);
    const discount = p.mrp && p.mrp > p.price ? Math.round(((p.mrp - p.price) / p.mrp) * 100) : 0;
    return (
      <View key={p.id} style={styles.productCard} testID={`product-${p.id}`}>
        <Pressable onPress={() => router.push(`/materials/store/${store.id}` as any)}>
          <Image source={{ uri: p.image }} style={styles.productImg} contentFit="cover" transition={200} />
          {discount > 0 ? (
            <View style={styles.discountBadge}><Text style={styles.discountText}>-{discount}%</Text></View>
          ) : null}
        </Pressable>
        <View style={{ padding: 10, flex: 1 }}>
          {p.brand ? <Text style={styles.productBrand} numberOfLines={1}>{p.brand}</Text> : null}
          <Text style={styles.productName} numberOfLines={2}>{p.name}</Text>
          <View style={styles.priceRow}>
            <Text style={styles.productPrice}>₹{p.price.toLocaleString("en-IN")}</Text>
            {p.mrp && p.mrp > p.price ? (
              <Text style={styles.productMrp}>₹{p.mrp.toLocaleString("en-IN")}</Text>
            ) : null}
          </View>
          {p.unit ? <Text style={styles.productUnit}>per {p.unit}</Text> : null}
          {qty === 0 ? (
            <Pressable
              testID={`add-${p.id}`}
              onPress={() => handleAdd(p, store)}
              style={styles.addBtn}
            >
              <Icon name="add" size={14} color={colors.brandPrimary} />
              <Text style={styles.addBtnText}>ADD</Text>
            </Pressable>
          ) : (
            <View style={styles.qtyBtn}>
              <Pressable testID={`dec-${p.id}`} onPress={() => decrement(p.id)} style={styles.qtyAction} hitSlop={6}>
                <Icon name="remove" size={14} color={colors.onBrandPrimary} />
              </Pressable>
              <Text style={styles.qtyText}>{qty}</Text>
              <Pressable testID={`inc-${p.id}`} onPress={() => increment(p.id)} style={styles.qtyAction} hitSlop={6}>
                <Icon name="add" size={14} color={colors.onBrandPrimary} />
              </Pressable>
            </View>
          )}
        </View>
      </View>
    );
  };

  const renderStoreBlock = ({ item: store }: { item: Store }) => (
    <View style={styles.storeBlock}>
      <Pressable
        testID={`store-header-${store.id}`}
        onPress={() => router.push(`/materials/store/${store.id}` as any)}
        style={styles.storeHeader}
      >
        <View style={{ flex: 1 }}>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
            <Text style={styles.storeName} numberOfLines={1}>{store.name}</Text>
            {store.verified && <Icon name="shield-checkmark" size={14} color={colors.success} />}
            {store.featured && (
              <View style={styles.featuredPill}><Text style={styles.featuredText}>FEATURED</Text></View>
            )}
          </View>
          <Text style={styles.storeTag} numberOfLines={1}>{store.tagline}</Text>
          <View style={styles.storeMetaRow}>
            <View style={styles.ratingPill}>
              <Icon name="star" size={10} color={colors.onBrandPrimary} />
              <Text style={styles.ratingText}>{store.rating.toFixed(1)}</Text>
            </View>
            <Text style={styles.storeMeta}>{store.area}</Text>
            {store.delivery_mins ? (
              <>
                <Text style={styles.storeMetaDot}>·</Text>
                <Icon name="time-outline" size={11} color={colors.muted} />
                <Text style={styles.storeMeta}>{store.delivery_mins} min</Text>
              </>
            ) : null}
          </View>
        </View>
        <Icon name="chevron-forward" size={20} color={colors.muted} />
      </Pressable>

      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.productRow}
      >
        {store.products.map((p) => renderProductCard(p, store))}
        <Pressable
          testID={`view-all-${store.id}`}
          onPress={() => router.push(`/materials/store/${store.id}` as any)}
          style={styles.viewAllCard}
        >
          <Icon name="arrow-forward-circle" size={28} color={colors.brandPrimary} />
          <Text style={styles.viewAllText}>View all</Text>
          <Text style={styles.viewAllSub}>{store.products_count} items</Text>
        </Pressable>
      </ScrollView>
    </View>
  );

  return (
    <View style={{ flex: 1, backgroundColor: colors.surfaceSecondary }}>
      <Stack.Screen options={{ headerShown: false }} />
      <View
        style={{
          paddingTop: insets.top + spacing.md,
          paddingHorizontal: spacing.xl,
          paddingBottom: spacing.md,
          backgroundColor: colors.surface,
          borderBottomWidth: 1,
          borderBottomColor: colors.border,
        }}
      >
        <View style={{ flexDirection: "row", alignItems: "center", gap: spacing.sm }}>
          <Pressable testID="mat-cat-back" onPress={() => router.back()} hitSlop={12}>
            <Icon name="chevron-back" size={26} color={colors.onSurface} />
          </Pressable>
          <View style={{ flex: 1 }}>
            <Text style={styles.title} numberOfLines={1}>{cat?.name ?? "Category"}</Text>
            <Text style={styles.sub}>{stores.length} stores · {totalProducts} products</Text>
          </View>
          <Pressable
            testID="mat-cat-cart"
            onPress={() => router.push("/materials/cart" as any)}
            style={styles.headerCartBtn}
            hitSlop={10}
          >
            <Icon name="cart-outline" size={22} color={colors.onSurface} />
            {totalItems > 0 && (
              <View style={styles.cartBadge}>
                <Text style={styles.cartBadgeText}>{totalItems > 99 ? "99+" : totalItems}</Text>
              </View>
            )}
          </Pressable>
        </View>

        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chipsRow}>
          <Pressable testID="sort-featured" onPress={() => setSort(sort === "featured" ? null : "featured")} style={[styles.chip, sort === "featured" && styles.chipActive]}>
            <Text style={[styles.chipText, sort === "featured" && styles.chipTextActive]}>Featured</Text>
          </Pressable>
          <Pressable testID="sort-rating" onPress={() => setSort(sort === "rating" ? null : "rating")} style={[styles.chip, sort === "rating" && styles.chipActive]}>
            <Text style={[styles.chipText, sort === "rating" && styles.chipTextActive]}>Top rated</Text>
          </Pressable>
          <Pressable testID="sort-price" onPress={() => setSort(sort === "price" ? null : "price")} style={[styles.chip, sort === "price" && styles.chipActive]}>
            <Text style={[styles.chipText, sort === "price" && styles.chipTextActive]}>Low price</Text>
          </Pressable>
          <Pressable testID="filter-verified" onPress={() => setVerifiedOnly((v) => !v)} style={[styles.chip, verifiedOnly && styles.chipActive]}>
            <Icon name="shield-checkmark-outline" size={13} color={verifiedOnly ? colors.onBrandPrimary : colors.onSurface} />
            <Text style={[styles.chipText, verifiedOnly && styles.chipTextActive]}>Verified only</Text>
          </Pressable>
        </ScrollView>
      </View>

      {loading ? (
        <ActivityIndicator color={colors.brand} style={{ marginTop: spacing.xxl }} />
      ) : (
        <FlatList
          data={visibleStores}
          keyExtractor={(s) => s.id}
          renderItem={renderStoreBlock}
          contentContainerStyle={{ paddingVertical: spacing.lg, paddingBottom: 120 }}
          ListEmptyComponent={<Text style={styles.empty}>No stores match. Try removing filters.</Text>}
        />
      )}

      {totalItems > 0 && (
        <Pressable
          testID="view-cart-bottom"
          onPress={() => router.push("/materials/cart" as any)}
          style={[styles.cartBar, { paddingBottom: Math.max(insets.bottom, 10) + 10 }]}
        >
          <View style={styles.cartBarInner}>
            <View>
              <Text style={styles.cartBarCount}>{totalItems} item{totalItems > 1 ? "s" : ""}</Text>
              <Text style={styles.cartBarSub}>Tap to review cart</Text>
            </View>
            <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
              <Text style={styles.cartBarCta}>View cart</Text>
              <Icon name="arrow-forward" size={16} color={colors.onBrandPrimary} />
            </View>
          </View>
        </Pressable>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  title: { fontSize: 20, fontWeight: "800", color: colors.onSurface, letterSpacing: -0.2 },
  sub: { fontSize: 12, color: colors.muted, marginTop: 2 },
  headerCartBtn: {
    width: 40, height: 40, borderRadius: radius.pill,
    backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border,
    alignItems: "center", justifyContent: "center",
  },
  cartBadge: {
    position: "absolute", top: -4, right: -4, minWidth: 20, height: 20, borderRadius: 10,
    paddingHorizontal: 4, backgroundColor: colors.brandPrimary, alignItems: "center", justifyContent: "center",
    borderWidth: 2, borderColor: colors.surface,
  },
  cartBadgeText: { color: colors.onBrandPrimary, fontSize: 10, fontWeight: "800" },

  chipsRow: { gap: spacing.sm, paddingVertical: spacing.md },
  chip: {
    flexDirection: "row", alignItems: "center", gap: 4,
    paddingHorizontal: 12, height: 32, borderRadius: radius.pill,
    borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, flexShrink: 0,
  },
  chipActive: { backgroundColor: colors.brandPrimary, borderColor: colors.brandPrimary },
  chipText: { color: colors.onSurface, fontSize: 12, fontWeight: "600" },
  chipTextActive: { color: colors.onBrandPrimary },

  storeBlock: {
    backgroundColor: colors.surface, marginHorizontal: spacing.xl, marginBottom: spacing.lg,
    borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, overflow: "hidden",
  },
  storeHeader: {
    flexDirection: "row", alignItems: "center", gap: spacing.sm,
    paddingHorizontal: spacing.lg, paddingVertical: spacing.md,
    borderBottomWidth: 1, borderBottomColor: colors.border,
  },
  storeName: { fontSize: 15, fontWeight: "700", color: colors.onSurface },
  storeTag: { fontSize: 12, color: colors.muted, marginTop: 2 },
  storeMetaRow: { flexDirection: "row", alignItems: "center", gap: 6, marginTop: 6 },
  ratingPill: { flexDirection: "row", alignItems: "center", gap: 3, backgroundColor: colors.success, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 6 },
  ratingText: { color: colors.onBrandPrimary, fontSize: 10, fontWeight: "700" },
  storeMeta: { fontSize: 11, color: colors.muted },
  storeMetaDot: { fontSize: 11, color: colors.muted, marginHorizontal: 2 },
  featuredPill: { backgroundColor: colors.brandPrimary, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 },
  featuredText: { fontSize: 9, fontWeight: "800", color: colors.onBrandPrimary, letterSpacing: 0.5 },

  productRow: { gap: spacing.md, padding: spacing.lg },
  productCard: {
    width: 160, backgroundColor: colors.surface, borderRadius: radius.md,
    borderWidth: 1, borderColor: colors.border, overflow: "hidden",
  },
  productImg: { width: "100%", height: 120, backgroundColor: colors.surfaceSecondary },
  discountBadge: {
    position: "absolute", top: 8, left: 8,
    backgroundColor: colors.success, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4,
  },
  discountText: { color: colors.onSuccess, fontSize: 10, fontWeight: "800" },
  productBrand: { fontSize: 10, fontWeight: "700", color: colors.brandPrimary, letterSpacing: 0.3, textTransform: "uppercase" },
  productName: { fontSize: 12, fontWeight: "600", color: colors.onSurface, marginTop: 2, lineHeight: 16 },
  priceRow: { flexDirection: "row", alignItems: "baseline", gap: 6, marginTop: 6 },
  productPrice: { fontSize: 14, fontWeight: "800", color: colors.onSurface },
  productMrp: { fontSize: 11, color: colors.muted, textDecorationLine: "line-through" },
  productUnit: { fontSize: 10, color: colors.muted, marginTop: 2 },
  addBtn: {
    marginTop: 8, borderWidth: 1, borderColor: colors.brandPrimary,
    paddingVertical: 7, borderRadius: radius.sm,
    flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 4,
    backgroundColor: colors.surface,
  },
  addBtnText: { fontSize: 12, fontWeight: "800", color: colors.brandPrimary, letterSpacing: 0.3 },
  qtyBtn: {
    marginTop: 8, flexDirection: "row", alignItems: "center",
    justifyContent: "space-between",
    backgroundColor: colors.brandPrimary, borderRadius: radius.sm,
  },
  qtyAction: { width: 30, height: 30, alignItems: "center", justifyContent: "center" },
  qtyText: { color: colors.onBrandPrimary, fontSize: 13, fontWeight: "800" },

  viewAllCard: {
    width: 110, backgroundColor: colors.surfaceSecondary, borderRadius: radius.md,
    borderWidth: 1, borderColor: colors.border, borderStyle: "dashed",
    alignItems: "center", justifyContent: "center", gap: 4, padding: spacing.md,
  },
  viewAllText: { fontSize: 12, fontWeight: "700", color: colors.onSurface, marginTop: 4 },
  viewAllSub: { fontSize: 10, color: colors.muted },

  empty: { textAlign: "center", color: colors.muted, marginTop: spacing.xxl, fontSize: 13 },

  cartBar: {
    position: "absolute", bottom: 0, left: 0, right: 0,
    paddingHorizontal: spacing.xl, paddingTop: 10,
    backgroundColor: colors.surface, borderTopWidth: 1, borderTopColor: colors.border,
  },
  cartBarInner: {
    flexDirection: "row", alignItems: "center", justifyContent: "space-between",
    backgroundColor: colors.brand, paddingHorizontal: spacing.lg, paddingVertical: 12,
    borderRadius: radius.lg,
  },
  cartBarCount: { color: colors.onBrand, fontSize: 14, fontWeight: "800" },
  cartBarSub: { color: colors.onBrand, fontSize: 11, opacity: 0.75 },
  cartBarCta: { color: colors.onBrand, fontSize: 13, fontWeight: "800" },
});
