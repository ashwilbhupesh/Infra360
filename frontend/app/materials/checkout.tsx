import React, { useEffect, useMemo, useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, TextInput, Alert, KeyboardAvoidingView, Platform } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter, Stack } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius } from "@/src/theme";
import { api, getUser } from "@/src/api";
import { useMaterialsCart, CartLine } from "@/src/stores/materials-cart";

type Method = "upi" | "card" | "cod";

export default function MaterialsCheckout() {
  const insets = useSafeAreaInsets();
  const router = useRouter();

  const hydrate = useMaterialsCart((s) => s.hydrate);
  const items = useMaterialsCart((s) => s.items);
  const clear = useMaterialsCart((s) => s.clear);

  const [name, setName] = useState("");
  const [mobile, setMobile] = useState("");
  const [address, setAddress] = useState("");
  const [landmark, setLandmark] = useState("");
  const [note, setNote] = useState("");
  const [method, setMethod] = useState<Method>("upi");
  const [upi, setUpi] = useState("");
  const [cardName, setCardName] = useState("");
  const [cardNo, setCardNo] = useState("");
  const [cardExp, setCardExp] = useState("");
  const [cardCvv, setCardCvv] = useState("");
  const [paying, setPaying] = useState(false);

  const groups = useMemo(() => {
    const g: Record<string, { store_id: string; store_name: string; store_phone?: string; items: CartLine[]; subtotal: number }> = {};
    for (const l of Object.values(items)) {
      const b = (g[l.store_id] ||= { store_id: l.store_id, store_name: l.store_name, store_phone: l.store_phone, items: [], subtotal: 0 });
      b.items.push(l);
      b.subtotal += l.price * l.qty;
    }
    return Object.values(g);
  }, [items]);

  const subtotal = useMemo(() => groups.reduce((s, g) => s + g.subtotal, 0), [groups]);
  const deliveryFee = useMemo(
    () => groups.reduce((s, g) => s + (g.subtotal >= 2500 ? 0 : 99), 0),
    [groups]
  );
  const total = subtotal + deliveryFee;
  const totalItems = useMemo(() => Object.values(items).reduce((s, l) => s + l.qty, 0), [items]);

  useEffect(() => {
    hydrate();
    (async () => {
      const u = await getUser();
      if (u) { setName(u.name || ""); setMobile(u.mobile || ""); }
    })();
  }, [hydrate]);

  const fullAddress = () => [address.trim(), landmark.trim()].filter(Boolean).join(", ");

  const validate = () => {
    if (!name.trim()) return "Please add your name.";
    if (mobile.trim().length < 10) return "10-digit mobile needed.";
    if (fullAddress().length < 10) return "Please add a complete delivery address.";
    if (method === "upi" && (!upi.trim() || !upi.includes("@"))) return "Enter a valid UPI ID (e.g. name@okhdfc).";
    if (method === "card") {
      if (cardName.trim().length < 3) return "Enter the name on the card.";
      if (cardNo.replace(/\s/g, "").length < 15) return "Enter a valid card number.";
      if (!/^\d{2}\/\d{2}$/.test(cardExp)) return "Expiry must be in MM/YY format.";
      if (cardCvv.length < 3) return "Enter the 3-digit CVV.";
    }
    return null;
  };

  const payNow = async () => {
    const err = validate();
    if (err) { Alert.alert("Can't place order yet", err); return; }
    setPaying(true);
    try {
      // Mock a 1.2s payment delay for realism
      await new Promise((r) => setTimeout(r, 1200));
      const u = await getUser();
      const res = await api.post<{ group_id: string; orders: any[]; total: number }>(
        "/materials/orders",
        {
          user_id: u?.id,
          name: name.trim(),
          mobile: mobile.trim(),
          address: fullAddress(),
          note: note.trim() || undefined,
          payment_method: method,
          payment_ref: method === "cod" ? null : `MOCK-${Date.now()}`,
          items: Object.values(items).map((l) => ({ product_id: l.id, store_id: l.store_id, qty: l.qty })),
        }
      );
      clear();
      // Navigate to first shipment's tracking (user can view others from Enquiries & Orders)
      const first = res.orders[0];
      router.replace({ pathname: "/materials/tracking/[id]", params: { id: first.id } } as any);
    } catch (e: any) {
      Alert.alert("Payment failed", e?.message || "Please try again.");
    } finally { setPaying(false); }
  };

  if (totalItems === 0) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.surfaceSecondary, paddingTop: insets.top + spacing.md }}>
        <Stack.Screen options={{ headerShown: false }} />
        <View style={styles.header}>
          <Pressable testID="checkout-back" onPress={() => router.back()} hitSlop={12}>
            <Icon name="chevron-back" size={26} color={colors.onSurface} />
          </Pressable>
          <Text style={styles.title}>Checkout</Text>
          <View style={{ width: 26 }} />
        </View>
        <View style={{ padding: spacing.xxxl, alignItems: "center" }}>
          <Icon name="cart-outline" size={44} color={colors.muted} />
          <Text style={{ fontSize: 15, fontWeight: "700", color: colors.onSurface, marginTop: 12 }}>
            Nothing to checkout
          </Text>
          <Text style={{ fontSize: 12, color: colors.muted, marginTop: 4 }}>Add items to your cart first.</Text>
        </View>
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: colors.surfaceSecondary }}>
      <Stack.Screen options={{ headerShown: false }} />
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="checkout-back" onPress={() => router.back()} hitSlop={12}>
          <Icon name="chevron-back" size={26} color={colors.onSurface} />
        </Pressable>
        <Text style={styles.title}>Checkout</Text>
        <View style={{ width: 26 }} />
      </View>

      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
        <ScrollView contentContainerStyle={{ padding: spacing.xl, paddingBottom: 220 }} keyboardShouldPersistTaps="handled">
          {/* Contact */}
          <Text style={styles.sectionKicker}>CONTACT</Text>
          <View style={styles.card}>
            <View style={styles.inputRow}>
              <Icon name="person-outline" size={14} color={colors.muted} />
              <TextInput testID="co-name" value={name} onChangeText={setName} placeholder="Full name" placeholderTextColor={colors.muted} style={styles.input} />
            </View>
            <View style={styles.inputRow}>
              <Icon name="call-outline" size={14} color={colors.muted} />
              <TextInput testID="co-mobile" value={mobile} onChangeText={setMobile} placeholder="10-digit mobile" placeholderTextColor={colors.muted} keyboardType="number-pad" maxLength={10} style={styles.input} />
            </View>
          </View>

          {/* Delivery address */}
          <Text style={styles.sectionKicker}>DELIVERY ADDRESS</Text>
          <View style={styles.card}>
            <View style={[styles.inputRow, { alignItems: "flex-start" }]}>
              <Icon name="home-outline" size={14} color={colors.muted} style={{ marginTop: 10 }} />
              <TextInput
                testID="co-address"
                value={address}
                onChangeText={setAddress}
                placeholder="House / flat no., street, locality"
                placeholderTextColor={colors.muted}
                style={[styles.input, { height: 60, textAlignVertical: "top" }]}
                multiline
              />
            </View>
            <View style={styles.inputRow}>
              <Icon name="flag-outline" size={14} color={colors.muted} />
              <TextInput testID="co-landmark" value={landmark} onChangeText={setLandmark} placeholder="Landmark (optional)" placeholderTextColor={colors.muted} style={styles.input} />
            </View>
            <View style={[styles.inputRow, { alignItems: "flex-start" }]}>
              <Icon name="chatbubble-outline" size={14} color={colors.muted} style={{ marginTop: 10 }} />
              <TextInput testID="co-note" value={note} onChangeText={setNote} placeholder="Delivery note (floor, gate code...)" placeholderTextColor={colors.muted} multiline style={[styles.input, { height: 50, textAlignVertical: "top" }]} />
            </View>
          </View>

          {/* Payment method */}
          <Text style={styles.sectionKicker}>PAYMENT</Text>
          <View style={{ flexDirection: "row", gap: 8 }}>
            {[
              { k: "upi", label: "UPI", icon: "flash-outline" as const },
              { k: "card", label: "Card", icon: "card-outline" as const },
              { k: "cod", label: "Cash on Delivery", icon: "cash-outline" as const },
            ].map((p) => {
              const active = method === p.k;
              return (
                <Pressable
                  key={p.k}
                  testID={`co-method-${p.k}`}
                  onPress={() => setMethod(p.k as Method)}
                  style={[styles.methodTile, active && styles.methodTileActive]}
                >
                  <Icon name={p.icon} size={18} color={active ? colors.onBrandPrimary : colors.onSurface} />
                  <Text style={[styles.methodText, active && { color: colors.onBrandPrimary }]} numberOfLines={1}>{p.label}</Text>
                </Pressable>
              );
            })}
          </View>

          {method === "upi" ? (
            <View style={[styles.card, { marginTop: spacing.md }]}>
              <View style={styles.upiHeader}>
                <View style={styles.upiLogos}>
                  <Text style={styles.upiLogoText}>UPI</Text>
                </View>
                <Text style={styles.upiTitle}>Enter UPI ID to pay</Text>
              </View>
              <View style={styles.inputRow}>
                <Icon name="at-outline" size={14} color={colors.muted} />
                <TextInput testID="co-upi" value={upi} onChangeText={setUpi} placeholder="yourname@okhdfc" placeholderTextColor={colors.muted} autoCapitalize="none" style={styles.input} />
              </View>
              <Text style={styles.hint}>You'll get a collect request on your UPI app. (Mock payment — nothing is charged.)</Text>
            </View>
          ) : method === "card" ? (
            <View style={[styles.card, { marginTop: spacing.md }]}>
              <View style={styles.inputRow}>
                <Icon name="person-outline" size={14} color={colors.muted} />
                <TextInput testID="co-card-name" value={cardName} onChangeText={setCardName} placeholder="Name on card" placeholderTextColor={colors.muted} style={styles.input} />
              </View>
              <View style={styles.inputRow}>
                <Icon name="card-outline" size={14} color={colors.muted} />
                <TextInput
                  testID="co-card-no"
                  value={cardNo}
                  onChangeText={(t) => setCardNo(t.replace(/[^\d]/g, "").slice(0, 16).replace(/(.{4})/g, "$1 ").trim())}
                  placeholder="1234 5678 9012 3456"
                  placeholderTextColor={colors.muted}
                  keyboardType="number-pad"
                  style={styles.input}
                />
              </View>
              <View style={{ flexDirection: "row", gap: 8 }}>
                <View style={[styles.inputRow, { flex: 1 }]}>
                  <Icon name="calendar-outline" size={14} color={colors.muted} />
                  <TextInput
                    testID="co-card-exp"
                    value={cardExp}
                    onChangeText={(t) => {
                      const d = t.replace(/[^\d]/g, "").slice(0, 4);
                      setCardExp(d.length >= 3 ? `${d.slice(0, 2)}/${d.slice(2)}` : d);
                    }}
                    placeholder="MM/YY"
                    placeholderTextColor={colors.muted}
                    keyboardType="number-pad"
                    style={styles.input}
                    maxLength={5}
                  />
                </View>
                <View style={[styles.inputRow, { flex: 1 }]}>
                  <Icon name="lock-closed-outline" size={14} color={colors.muted} />
                  <TextInput testID="co-card-cvv" value={cardCvv} onChangeText={(t) => setCardCvv(t.replace(/[^\d]/g, "").slice(0, 4))} placeholder="CVV" placeholderTextColor={colors.muted} keyboardType="number-pad" secureTextEntry style={styles.input} />
                </View>
              </View>
              <Text style={styles.hint}>Mock payment for demo — no card is actually charged.</Text>
            </View>
          ) : (
            <View style={[styles.card, { marginTop: spacing.md, flexDirection: "row", gap: 10, alignItems: "flex-start" }]}>
              <Icon name="information-circle-outline" size={18} color={colors.brand} />
              <Text style={{ flex: 1, fontSize: 12, color: colors.onSurface, lineHeight: 17 }}>
                Pay the delivery agent in cash when your order arrives. Keep the exact amount ready.
              </Text>
            </View>
          )}

          {/* Order summary */}
          <Text style={styles.sectionKicker}>ORDER SUMMARY</Text>
          <View style={styles.card}>
            {groups.map(g => (
              <View key={g.store_id} style={{ marginBottom: 10 }}>
                <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 4 }}>
                  <Text style={styles.sumStore}>{g.store_name}</Text>
                  <Text style={styles.sumVal}>₹{g.subtotal.toLocaleString("en-IN")}</Text>
                </View>
                <Text style={styles.sumSub}>{g.items.length} item{g.items.length > 1 ? "s" : ""} · delivery {g.subtotal >= 2500 ? "free" : "₹99"}</Text>
              </View>
            ))}
            <View style={styles.divider} />
            <View style={styles.sumLine}><Text style={styles.sumKey}>Subtotal</Text><Text style={styles.sumVal}>₹{subtotal.toLocaleString("en-IN")}</Text></View>
            <View style={styles.sumLine}><Text style={styles.sumKey}>Delivery</Text><Text style={styles.sumVal}>{deliveryFee ? `₹${deliveryFee}` : "FREE"}</Text></View>
            <View style={[styles.sumLine, { marginTop: 6 }]}>
              <Text style={[styles.sumKey, { fontWeight: "800", color: colors.onSurface }]}>Total</Text>
              <Text style={[styles.sumVal, { fontSize: 18, fontWeight: "800" }]}>₹{total.toLocaleString("en-IN")}</Text>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>

      <View style={[styles.footer, { paddingBottom: Math.max(insets.bottom, 10) + 10 }]}>
        <View>
          <Text style={styles.footerKey}>Total payable</Text>
          <Text style={styles.footerTotal}>₹{total.toLocaleString("en-IN")}</Text>
        </View>
        <Pressable
          testID="co-pay-now"
          onPress={payNow}
          disabled={paying}
          style={[styles.payBtn, paying && { opacity: 0.6 }]}
        >
          <Icon name={method === "cod" ? "cart" : "lock-closed"} size={14} color={colors.onBrandPrimary} />
          <Text style={styles.payText}>{paying ? "Processing…" : method === "cod" ? "Place order" : "Pay securely"}</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", paddingHorizontal: spacing.xl, paddingBottom: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  title: { fontSize: 18, fontWeight: "800", color: colors.onSurface, letterSpacing: -0.2 },
  sectionKicker: { fontSize: 10, fontWeight: "800", color: colors.muted, letterSpacing: 1, marginTop: spacing.lg, marginBottom: 6, paddingLeft: 4 },
  card: { backgroundColor: colors.surface, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, padding: spacing.md, gap: 8 },
  inputRow: { flexDirection: "row", alignItems: "center", gap: 8, backgroundColor: colors.surfaceSecondary, borderRadius: radius.md, paddingHorizontal: 12, paddingVertical: 10, borderWidth: 1, borderColor: colors.border },
  input: { flex: 1, fontSize: 13, color: colors.onSurface, padding: 0 },
  hint: { fontSize: 11, color: colors.muted, marginTop: 4, paddingHorizontal: 2 },
  methodTile: { flex: 1, backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, paddingVertical: 12, paddingHorizontal: 10, alignItems: "center", gap: 4 },
  methodTileActive: { backgroundColor: colors.brandPrimary, borderColor: colors.brandPrimary },
  methodText: { fontSize: 12, fontWeight: "700", color: colors.onSurface },
  upiHeader: { flexDirection: "row", alignItems: "center", gap: 10, marginBottom: 4 },
  upiLogos: { backgroundColor: colors.brand, paddingHorizontal: 10, paddingVertical: 4, borderRadius: radius.sm },
  upiLogoText: { color: colors.onBrand, fontSize: 11, fontWeight: "800", letterSpacing: 0.6 },
  upiTitle: { fontSize: 13, fontWeight: "700", color: colors.onSurface },
  sumStore: { fontSize: 13, fontWeight: "700", color: colors.onSurface },
  sumSub: { fontSize: 11, color: colors.muted, marginTop: 2 },
  divider: { height: 1, backgroundColor: colors.border, marginVertical: 6 },
  sumLine: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingVertical: 2 },
  sumKey: { fontSize: 13, color: colors.onSurfaceSecondary },
  sumVal: { fontSize: 13, color: colors.onSurface, fontWeight: "600" },
  footer: { position: "absolute", bottom: 0, left: 0, right: 0, flexDirection: "row", alignItems: "center", justifyContent: "space-between", gap: spacing.md, paddingHorizontal: spacing.xl, paddingTop: 10, backgroundColor: colors.surface, borderTopWidth: 1, borderTopColor: colors.border },
  footerKey: { fontSize: 11, color: colors.muted },
  footerTotal: { fontSize: 20, fontWeight: "800", color: colors.onSurface, letterSpacing: -0.3 },
  payBtn: { flexDirection: "row", alignItems: "center", gap: 6, backgroundColor: colors.brandPrimary, paddingHorizontal: 20, paddingVertical: 14, borderRadius: radius.pill },
  payText: { color: colors.onBrandPrimary, fontSize: 14, fontWeight: "800" },
});
