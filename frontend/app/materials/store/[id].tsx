import React, { useEffect, useMemo, useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, ActivityIndicator, TextInput } from "react-native";
import { Image } from "expo-image";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useLocalSearchParams, useRouter, Stack } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius } from "@/src/theme";
import { api } from "@/src/api";
import { useMaterialsCart } from "@/src/stores/materials-cart";
import { openWhatsApp } from "@/src/utils/contact";

type Product = {
  id: string; store_id: string; category_id: string; name: string;
  brand?: string; image: string; unit?: string; price: number; mrp?: number;
};
type Category = { id: string; name: string; image: string };
type Store = {
  id: string; name: string; tagline: string; area: string; city: string;
  rating: number; reviews: number; verified: boolean; featured: boolean;
  delivery_mins?: number; min_order?: string; phone: string; image?: string;
  about?: string; products_count: number;
  catalogue: { category: Category; products: Product[] }[];
};

export default function MaterialsStorePage() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [store, setStore] = useState<Store | null>(null);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [activeCat, setActiveCat] = useState<string | null>(null);

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
        const s = await api.get<Store>(`/materials/stores/${id}`);
        setStore(s);
        if (s.catalogue?.length) setActiveCat(s.catalogue[0].category.id);
      } finally { setLoading(false); }
    })();
  }, [id]);

  const activeProducts = useMemo(() => {
    if (!store) return [];
    const section = activeCat
      ? store.catalogue.find((c) => c.category.id === activeCat)
      : store.catalogue[0];
    let list = section?.products ?? [];
    if (query.trim()) {
      const q = query.trim().toLowerCase();
      list = list.filter(
        (p) => p.name.toLowerCase().includes(q) || (p.brand?.toLowerCase().includes(q) ?? false)
      );
    }
    return list;
  }, [store, activeCat, query]);

  const handleAdd = (p: Product) => {
    if (!store) return;
    add({
      id: p.id, store_id: store.id, store_name: store.name, store_phone: store.phone,
      name: p.name, brand: p.brand, image: p.image, unit: p.unit, price: p.price, category_id: p.category_id,
    });
  };

  const renderProductTile = (p: Product) => {
    const qty = qtyOf(p.id);
    const discount = p.mrp && p.mrp > p.price ? Math.round(((p.mrp - p.price) / p.mrp) * 100) : 0;
    return (
      <View key={p.id} style={styles.productCard}>
        <View style={{ position: "relative" }}>
          <Image source={{ uri: p.image }} style={styles.productImg} contentFit="cover" />
          {discount > 0 ? (
            <View style={styles.discountBadge}><Text style={styles.discountText}>-{discount}%</Text></View>
          ) : null}
        </View>
        <View style={{ flex: 1, padding: 10 }}>
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
            <Pressable testID={`add-${p.id}`} onPress={() => handleAdd(p)} style={styles.addBtn}>
              <Icon name="add" size={14} color={colors.brandPrimary} />
              <Text style={styles.addBtnText}>ADD</Text>
            </Pressable>
          ) : (
            <View style={styles.qtyBtn}>
              <Pressable onPress={() => decrement(p.id)} style={styles.qtyAction} hitSlop={6}>
                <Icon name="remove" size={14} color={colors.onBrandPrimary} />
              </Pressable>
              <Text style={styles.qtyText}>{qty}</Text>
              <Pressable onPress={() => increment(p.id)} style={styles.qtyAction} hitSlop={6}>
                <Icon name="add" size={14} color={colors.onBrandPrimary} />
              </Pressable>
            </View>
          )}
        </View>
      </View>
    );
  };

  if (loading || !store) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.surfaceSecondary, paddingTop: insets.top + 20 }}>
        <Stack.Screen options={{ headerShown: false }} />
        <ActivityIndicator color={colors.brand} style={{ marginTop: spacing.xxl }} />
      </View>
    );
  }

  const multiCat = store.catalogue.length > 1;

  return (
    <View style={{ flex: 1, backgroundColor: colors.surfaceSecondary }}>
      <Stack.Screen options={{ headerShown: false }} />

      {/* Header */}
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
          <Pressable testID="store-back" onPress={() => router.back()} hitSlop={12}>
            <Icon name="chevron-back" size={26} color={colors.onSurface} />
          </Pressable>
          <View style={{ flex: 1 }}>
            <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
              <Text style={styles.storeName} numberOfLines={1}>{store.name}</Text>
              {store.verified && <Icon name="shield-checkmark" size={16} color={colors.success} />}
            </View>
            <Text style={styles.storeTag} numberOfLines={1}>{store.tagline}</Text>
          </View>
          <Pressable
            testID="store-cart"
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

        <View style={styles.statsRow}>
          <View style={styles.ratingPill}>
            <Icon name="star" size={11} color={colors.onBrandPrimary} />
            <Text style={styles.ratingText}>{store.rating.toFixed(1)}</Text>
          </View>
          <Text style={styles.statText}>{store.reviews} reviews</Text>
          <Text style={styles.statDot}>·</Text>
          <Icon name="location-outline" size={11} color={colors.muted} />
          <Text style={styles.statText}>{store.area}</Text>
          {store.delivery_mins ? (
            <>
              <Text style={styles.statDot}>·</Text>
              <Icon name="time-outline" size={11} color={colors.muted} />
              <Text style={styles.statText}>{store.delivery_mins} min</Text>
            </>
          ) : null}
        </View>

        <View style={styles.searchWrap}>
          <Icon name="search" size={16} color={colors.muted} />
          <TextInput
            testID="store-search"
            value={query}
            onChangeText={setQuery}
            placeholder="Search in this catalogue"
            placeholderTextColor={colors.muted}
            style={styles.searchInput}
          />
          {query ? (
            <Pressable onPress={() => setQuery("")} hitSlop={10}>
              <Icon name="close-circle" size={16} color={colors.muted} />
            </Pressable>
          ) : null}
        </View>

        <View style={{ flexDirection: "row", gap: 8, marginTop: spacing.sm }}>
          <Pressable
            testID="store-whatsapp"
            style={[styles.ctaBtn, { backgroundColor: colors.success }]}
            onPress={() =>
              openWhatsApp(
                store.phone,
                `Hi ${store.name}, I'd like to enquire about products in your catalogue.`
              )
            }
          >
            <Icon name="logo-whatsapp" size={14} color={colors.onSuccess} />
            <Text style={[styles.ctaText, { color: colors.onSuccess }]}>WhatsApp</Text>
          </Pressable>
          <Pressable
            testID="store-view-supplier"
            style={[styles.ctaBtn, { backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border }]}
            onPress={() => router.push("/contact-us" as any)}
          >
            <Icon name="information-circle-outline" size={14} color={colors.onSurface} />
            <Text style={[styles.ctaText, { color: colors.onSurface }]}>Support</Text>
          </Pressable>
        </View>
      </View>

      {/* Category tabs (when store spans multiple cats) */}
      {multiCat ? (
        <View style={{ backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border }}>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.catTabs}>
            {store.catalogue.map((c) => {
              const active = activeCat === c.category.id;
              return (
                <Pressable
                  key={c.category.id}
                  testID={`cat-tab-${c.category.id}`}
                  onPress={() => setActiveCat(c.category.id)}
                  style={[styles.catTab, active && styles.catTabActive]}
                >
                  <Text style={[styles.catTabText, active && styles.catTabTextActive]}>
                    {c.category.name}
                  </Text>
                </Pressable>
              );
            })}
          </ScrollView>
        </View>
      ) : null}

      <ScrollView contentContainerStyle={{ padding: spacing.xl, paddingBottom: 140 }}>
        <Text style={styles.catHeading}>
          {activeProducts.length} product{activeProducts.length !== 1 ? "s" : ""}
        </Text>
        <View style={styles.grid}>
          {activeProducts.map(renderProductTile)}
        </View>
        {activeProducts.length === 0 && (
          <Text style={styles.empty}>No products match “{query}”.</Text>
        )}
      </ScrollView>

      {totalItems > 0 && (
        <Pressable
          testID="store-view-cart"
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
  storeName: { fontSize: 18, fontWeight: "800", color: colors.onSurface, letterSpacing: -0.2 },
  storeTag: { fontSize: 12, color: colors.muted, marginTop: 2 },
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

  statsRow: { flexDirection: "row", alignItems: "center", gap: 6, marginTop: spacing.sm },
  ratingPill: { flexDirection: "row", alignItems: "center", gap: 3, backgroundColor: colors.success, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 6 },
  ratingText: { color: colors.onBrandPrimary, fontSize: 11, fontWeight: "700" },
  statText: { fontSize: 11, color: colors.muted },
  statDot: { fontSize: 11, color: colors.muted, marginHorizontal: 2 },

  searchWrap: {
    flexDirection: "row", alignItems: "center", gap: 8,
    backgroundColor: colors.surfaceSecondary, borderRadius: radius.lg,
    paddingHorizontal: 12, height: 40, marginTop: spacing.sm,
    borderWidth: 1, borderColor: colors.border,
  },
  searchInput: { flex: 1, fontSize: 13, color: colors.onSurface },

  ctaBtn: {
    flex: 1, flexDirection: "row", alignItems: "center", justifyContent: "center",
    gap: 6, paddingVertical: 10, borderRadius: radius.pill,
  },
  ctaText: { fontSize: 12, fontWeight: "700" },

  catTabs: { paddingHorizontal: spacing.xl, gap: spacing.sm, paddingVertical: spacing.sm },
  catTab: {
    paddingHorizontal: 12, height: 32, justifyContent: "center",
    borderBottomWidth: 2, borderBottomColor: "transparent",
  },
  catTabActive: { borderBottomColor: colors.brandPrimary },
  catTabText: { color: colors.muted, fontSize: 13, fontWeight: "600" },
  catTabTextActive: { color: colors.brandPrimary, fontWeight: "800" },

  catHeading: { fontSize: 14, fontWeight: "700", color: colors.onSurface, marginBottom: spacing.md },

  grid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.md },
  productCard: {
    width: "48%", backgroundColor: colors.surface, borderRadius: radius.md,
    borderWidth: 1, borderColor: colors.border, overflow: "hidden",
  },
  productImg: { width: "100%", height: 130, backgroundColor: colors.surfaceSecondary },
  discountBadge: {
    position: "absolute", top: 8, left: 8, backgroundColor: colors.success,
    paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4,
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
    marginTop: 8, flexDirection: "row", alignItems: "center", justifyContent: "space-between",
    backgroundColor: colors.brandPrimary, borderRadius: radius.sm,
  },
  qtyAction: { width: 30, height: 30, alignItems: "center", justifyContent: "center" },
  qtyText: { color: colors.onBrandPrimary, fontSize: 13, fontWeight: "800" },

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
