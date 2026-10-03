import React, { useEffect, useMemo, useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, TextInput, Alert } from "react-native";
import { Image } from "expo-image";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter, Stack } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius } from "@/src/theme";
import { useMaterialsCart, CartLine } from "@/src/stores/materials-cart";
import { openWhatsApp } from "@/src/utils/contact";
import { getUser, api } from "@/src/api";

export default function MaterialsCartPage() {
  const insets = useSafeAreaInsets();
  const router = useRouter();

  const hydrate = useMaterialsCart((s) => s.hydrate);
  const items = useMaterialsCart((s) => s.items);
  const increment = useMaterialsCart((s) => s.increment);
  const decrement = useMaterialsCart((s) => s.decrement);
  const remove = useMaterialsCart((s) => s.remove);
  const clear = useMaterialsCart((s) => s.clear);

  // Derive memoised totals / groups from items — avoids zustand selector returning new refs each render.
  const totalItems = useMemo(
    () => Object.values(items).reduce((sum, l) => sum + l.qty, 0),
    [items]
  );
  const totalAmount = useMemo(
    () => Object.values(items).reduce((sum, l) => sum + l.qty * l.price, 0),
    [items]
  );
  const groups = useMemo(() => {
    const g: Record<string, { store_id: string; store_name: string; store_phone?: string; items: CartLine[]; subtotal: number }> = {};
    for (const l of Object.values(items)) {
      const bucket = (g[l.store_id] ||= {
        store_id: l.store_id, store_name: l.store_name, store_phone: l.store_phone,
        items: [], subtotal: 0,
      });
      bucket.items.push(l);
      bucket.subtotal += l.price * l.qty;
    }
    return Object.values(g);
  }, [items]);

  const [note, setNote] = useState("");
  const [address, setAddress] = useState("");
  const [name, setName] = useState("");
  const [mobile, setMobile] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    hydrate();
    (async () => {
      const u = await getUser();
      if (u) {
        setName(u.name || "");
        setMobile(u.mobile || "");
      }
    })();
  }, [hydrate]);

  const buildWaMessage = (storeName: string, lines: typeof groups[number]["items"], subtotal: number) => {
    const lineText = lines
      .map((l) => `• ${l.name}${l.brand ? ` (${l.brand})` : ""} — ${l.qty} × ₹${l.price.toLocaleString("en-IN")}${l.unit ? "/" + l.unit : ""}`)
      .join("\n");
    return (
      `Hi ${storeName}, I'd like to place an enquiry via InfraJagat:\n\n` +
      lineText +
      `\n\nSubtotal: ₹${subtotal.toLocaleString("en-IN")}\n` +
      (name ? `Name: ${name}\n` : "") +
      (mobile ? `Mobile: ${mobile}\n` : "") +
      (address ? `Delivery: ${address}\n` : "") +
      (note ? `Note: ${note}\n` : "") +
      `\nPlease confirm final rates and availability.`
    );
  };

  const submitAll = async () => {
    if (!name.trim() || mobile.trim().length < 10) {
      Alert.alert("Missing details", "Please enter your name and 10-digit mobile.");
      return;
    }
    setSubmitting(true);
    try {
      const u = await getUser();
      await api.post("/materials/cart-enquiry", {
        user_id: u?.id,
        name: name.trim(),
        mobile: mobile.trim(),
        address: address.trim() || undefined,
        note: note.trim() || undefined,
        items: Object.values(items).map((l) => ({
          product_id: l.id,
          store_id: l.store_id,
          qty: l.qty,
        })),
      });
      Alert.alert(
        "Enquiry sent",
        "Stores will reach out shortly. You can also follow up on WhatsApp from each store below.",
        [{ text: "OK" }]
      );
    } catch (e: any) {
      Alert.alert("Something went wrong", e?.message || "Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  if (totalItems === 0) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.surfaceSecondary, paddingTop: insets.top }}>
        <Stack.Screen options={{ headerShown: false }} />
        <View style={styles.header}>
          <Pressable testID="cart-back" onPress={() => router.back()} hitSlop={12}>
            <Icon name="chevron-back" size={26} color={colors.onSurface} />
          </Pressable>
          <Text style={styles.headerTitle}>Your cart</Text>
          <View style={{ width: 26 }} />
        </View>
        <View style={styles.emptyWrap}>
          <View style={styles.emptyIconWrap}>
            <Icon name="cart-outline" size={48} color={colors.muted} />
          </View>
          <Text style={styles.emptyTitle}>Your cart is empty</Text>
          <Text style={styles.emptySub}>Browse categories and add products to request a bulk quote from Jaipur stores.</Text>
          <Pressable
            testID="browse-materials"
            onPress={() => router.replace("/(tabs)/market" as any)}
            style={styles.browseBtn}
          >
            <Text style={styles.browseText}>Browse materials</Text>
          </Pressable>
        </View>
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: colors.surfaceSecondary }}>
      <Stack.Screen options={{ headerShown: false }} />
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="cart-back" onPress={() => router.back()} hitSlop={12}>
          <Icon name="chevron-back" size={26} color={colors.onSurface} />
        </Pressable>
        <Text style={styles.headerTitle}>Your cart ({totalItems})</Text>
        <Pressable testID="cart-clear" onPress={() => Alert.alert("Clear cart?", "Remove all items?", [
          { text: "Cancel", style: "cancel" },
          { text: "Clear", style: "destructive", onPress: () => clear() },
        ])} hitSlop={10}>
          <Text style={styles.clearText}>Clear</Text>
        </Pressable>
      </View>

      <ScrollView contentContainerStyle={{ padding: spacing.xl, paddingBottom: 220 }}>
        {groups.map((g) => (
          <View key={g.store_id} style={styles.storeGroup} testID={`cart-group-${g.store_id}`}>
            <View style={styles.storeHead}>
              <View style={{ flex: 1 }}>
                <Text style={styles.storeHeadName} numberOfLines={1}>{g.store_name}</Text>
                <Text style={styles.storeHeadSub}>{g.items.length} item{g.items.length > 1 ? "s" : ""}</Text>
              </View>
              {g.store_phone ? (
                <Pressable
                  testID={`store-wa-${g.store_id}`}
                  onPress={() => openWhatsApp(g.store_phone!, buildWaMessage(g.store_name, g.items, g.subtotal))}
                  style={styles.waBtn}
                >
                  <Icon name="logo-whatsapp" size={14} color={colors.onSuccess} />
                  <Text style={styles.waBtnText}>Send on WhatsApp</Text>
                </Pressable>
              ) : null}
            </View>

            {g.items.map((l) => (
              <View key={l.id} style={styles.lineRow}>
                <Image source={{ uri: l.image }} style={styles.lineImg} contentFit="cover" />
                <View style={{ flex: 1 }}>
                  {l.brand ? <Text style={styles.lineBrand}>{l.brand}</Text> : null}
                  <Text style={styles.lineName} numberOfLines={2}>{l.name}</Text>
                  <Text style={styles.linePrice}>
                    ₹{l.price.toLocaleString("en-IN")}
                    {l.unit ? <Text style={styles.lineUnit}> / {l.unit}</Text> : null}
                  </Text>
                </View>
                <View style={{ alignItems: "flex-end" }}>
                  <View style={styles.qtyBtn}>
                    <Pressable testID={`cart-dec-${l.id}`} onPress={() => decrement(l.id)} style={styles.qtyAction} hitSlop={6}>
                      <Icon name="remove" size={14} color={colors.onBrandPrimary} />
                    </Pressable>
                    <Text style={styles.qtyText}>{l.qty}</Text>
                    <Pressable testID={`cart-inc-${l.id}`} onPress={() => increment(l.id)} style={styles.qtyAction} hitSlop={6}>
                      <Icon name="add" size={14} color={colors.onBrandPrimary} />
                    </Pressable>
                  </View>
                  <Text style={styles.lineTotal}>₹{(l.price * l.qty).toLocaleString("en-IN")}</Text>
                  <Pressable testID={`remove-${l.id}`} onPress={() => remove(l.id)}>
                    <Text style={styles.removeTxt}>Remove</Text>
                  </Pressable>
                </View>
              </View>
            ))}

            <View style={styles.subtotalRow}>
              <Text style={styles.subtotalLabel}>Store subtotal</Text>
              <Text style={styles.subtotalValue}>₹{g.subtotal.toLocaleString("en-IN")}</Text>
            </View>
          </View>
        ))}

        {/* Enquiry details */}
        <View style={styles.detailsCard}>
          <Text style={styles.detailsHead}>Your details</Text>
          <View style={styles.inputWrap}>
            <Icon name="person-outline" size={14} color={colors.muted} />
            <TextInput
              testID="cart-name"
              value={name}
              onChangeText={setName}
              placeholder="Full name"
              placeholderTextColor={colors.muted}
              style={styles.input}
            />
          </View>
          <View style={styles.inputWrap}>
            <Icon name="call-outline" size={14} color={colors.muted} />
            <TextInput
              testID="cart-mobile"
              value={mobile}
              onChangeText={setMobile}
              placeholder="10-digit mobile"
              placeholderTextColor={colors.muted}
              keyboardType="number-pad"
              maxLength={10}
              style={styles.input}
            />
          </View>
          <View style={styles.inputWrap}>
            <Icon name="location-outline" size={14} color={colors.muted} />
            <TextInput
              testID="cart-address"
              value={address}
              onChangeText={setAddress}
              placeholder="Delivery area (optional)"
              placeholderTextColor={colors.muted}
              style={styles.input}
            />
          </View>
          <View style={[styles.inputWrap, { alignItems: "flex-start" }]}>
            <Icon name="chatbubble-outline" size={14} color={colors.muted} style={{ marginTop: 6 }} />
            <TextInput
              testID="cart-note"
              value={note}
              onChangeText={setNote}
              placeholder="Add a note (optional)"
              placeholderTextColor={colors.muted}
              multiline
              style={[styles.input, { height: 60, textAlignVertical: "top" }]}
            />
          </View>
        </View>
      </ScrollView>

      {/* Sticky submit */}
      <View style={[styles.footer, { paddingBottom: Math.max(insets.bottom, 10) + 10 }]}>
        <View style={{ flex: 1 }}>
          <Text style={styles.footerLabel}>Est. total</Text>
          <Text style={styles.footerAmount}>₹{totalAmount.toLocaleString("en-IN")}</Text>
          <Text style={styles.footerSub}>Final rates confirmed on enquiry</Text>
        </View>
        <Pressable
          testID="cart-submit-all"
          disabled={submitting}
          onPress={submitAll}
          style={[styles.submitBtn, submitting && { opacity: 0.6 }]}
        >
          <Text style={styles.submitText}>{submitting ? "Sending…" : "Request quotes"}</Text>
          <Icon name="paper-plane" size={14} color={colors.onBrandPrimary} />
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  header: {
    flexDirection: "row", alignItems: "center", justifyContent: "space-between",
    paddingHorizontal: spacing.xl, paddingBottom: spacing.md,
    backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border,
  },
  headerTitle: { fontSize: 17, fontWeight: "800", color: colors.onSurface, letterSpacing: -0.2 },
  clearText: { color: colors.error, fontSize: 13, fontWeight: "700" },

  emptyWrap: { alignItems: "center", padding: spacing.xxl, marginTop: spacing.xxxl },
  emptyIconWrap: {
    width: 88, height: 88, borderRadius: 44,
    backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border,
    alignItems: "center", justifyContent: "center",
  },
  emptyTitle: { fontSize: 17, fontWeight: "800", color: colors.onSurface, marginTop: spacing.lg },
  emptySub: { fontSize: 13, color: colors.muted, textAlign: "center", marginTop: spacing.sm, lineHeight: 19 },
  browseBtn: {
    marginTop: spacing.xl, backgroundColor: colors.brandPrimary,
    paddingHorizontal: 20, paddingVertical: 12, borderRadius: radius.pill,
  },
  browseText: { color: colors.onBrandPrimary, fontSize: 13, fontWeight: "800" },

  storeGroup: {
    backgroundColor: colors.surface, borderRadius: radius.lg,
    borderWidth: 1, borderColor: colors.border, marginBottom: spacing.lg, overflow: "hidden",
  },
  storeHead: {
    flexDirection: "row", alignItems: "center", gap: spacing.md,
    padding: spacing.md, borderBottomWidth: 1, borderBottomColor: colors.border,
  },
  storeHeadName: { fontSize: 14, fontWeight: "800", color: colors.onSurface },
  storeHeadSub: { fontSize: 11, color: colors.muted, marginTop: 2 },
  waBtn: {
    flexDirection: "row", alignItems: "center", gap: 4,
    backgroundColor: colors.success, paddingVertical: 7, paddingHorizontal: 12, borderRadius: radius.pill,
  },
  waBtnText: { color: colors.onSuccess, fontSize: 11, fontWeight: "700" },

  lineRow: {
    flexDirection: "row", gap: spacing.md, padding: spacing.md,
    borderBottomWidth: 1, borderBottomColor: colors.border,
  },
  lineImg: { width: 60, height: 60, borderRadius: radius.sm, backgroundColor: colors.surfaceSecondary },
  lineBrand: { fontSize: 9, fontWeight: "700", color: colors.brandPrimary, textTransform: "uppercase", letterSpacing: 0.3 },
  lineName: { fontSize: 13, fontWeight: "600", color: colors.onSurface, marginTop: 2, lineHeight: 17 },
  linePrice: { fontSize: 12, fontWeight: "700", color: colors.onSurface, marginTop: 4 },
  lineUnit: { fontSize: 11, color: colors.muted, fontWeight: "500" },
  qtyBtn: {
    flexDirection: "row", alignItems: "center", justifyContent: "space-between",
    backgroundColor: colors.brandPrimary, borderRadius: radius.sm, marginBottom: 4,
  },
  qtyAction: { width: 26, height: 26, alignItems: "center", justifyContent: "center" },
  qtyText: { color: colors.onBrandPrimary, fontSize: 12, fontWeight: "800", paddingHorizontal: 2 },
  lineTotal: { fontSize: 13, fontWeight: "800", color: colors.onSurface, marginTop: 2 },
  removeTxt: { fontSize: 10, color: colors.error, fontWeight: "700", marginTop: 2 },

  subtotalRow: {
    flexDirection: "row", justifyContent: "space-between", alignItems: "center",
    paddingHorizontal: spacing.md, paddingVertical: 10, backgroundColor: colors.surfaceSecondary,
  },
  subtotalLabel: { fontSize: 12, color: colors.muted, fontWeight: "600" },
  subtotalValue: { fontSize: 14, fontWeight: "800", color: colors.onSurface },

  detailsCard: {
    backgroundColor: colors.surface, borderRadius: radius.lg,
    borderWidth: 1, borderColor: colors.border, padding: spacing.lg, gap: spacing.sm,
  },
  detailsHead: { fontSize: 13, fontWeight: "800", color: colors.onSurface, marginBottom: 4 },
  inputWrap: {
    flexDirection: "row", alignItems: "center", gap: 8,
    backgroundColor: colors.surfaceSecondary, borderRadius: radius.md,
    paddingHorizontal: 12, paddingVertical: 10, borderWidth: 1, borderColor: colors.border,
  },
  input: { flex: 1, fontSize: 13, color: colors.onSurface, padding: 0 },

  footer: {
    position: "absolute", bottom: 0, left: 0, right: 0,
    flexDirection: "row", alignItems: "center", gap: spacing.md,
    paddingHorizontal: spacing.xl, paddingTop: 12,
    backgroundColor: colors.surface, borderTopWidth: 1, borderTopColor: colors.border,
  },
  footerLabel: { fontSize: 11, color: colors.muted },
  footerAmount: { fontSize: 20, fontWeight: "800", color: colors.onSurface, letterSpacing: -0.3 },
  footerSub: { fontSize: 10, color: colors.muted, marginTop: 1 },
  submitBtn: {
    flexDirection: "row", alignItems: "center", gap: 8,
    backgroundColor: colors.brandPrimary, paddingHorizontal: 20, paddingVertical: 14,
    borderRadius: radius.pill,
  },
  submitText: { color: colors.onBrandPrimary, fontSize: 14, fontWeight: "800" },
});
