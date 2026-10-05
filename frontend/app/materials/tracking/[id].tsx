import React, { useEffect, useRef, useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, ActivityIndicator, Linking } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useLocalSearchParams, useRouter, Stack } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius } from "@/src/theme";
import { api } from "@/src/api";
import { WebMap, WebMapMarker } from "@/src/components/web-map";

type Order = {
  id: string;
  group_id?: string;
  status: "placed" | "picked_up" | "en_route" | "nearby" | "delivered";
  mins_left?: number;
  pct?: number;
  driver_pos?: { lat: number; lng: number };
  pickup: { lat: number; lng: number };
  drop: { lat: number; lng: number };
  waypoints?: { lat: number; lng: number }[];
  store: { id?: string; name: string; phone?: string; area?: string };
  items: { product_id: string; name: string; brand?: string; qty: number; price: number; image?: string; unit?: string }[];
  subtotal: number;
  delivery_fee: number;
  total: number;
  address: string;
  payment_method: "upi" | "card" | "cod";
  payment_status: string;
  created_at: string;
  eta_mins: number;
};

const STEPS: { k: Order["status"]; label: string; icon: any }[] = [
  { k: "picked_up", label: "Picked up from store", icon: "cube-outline" },
  { k: "en_route", label: "On the way", icon: "bicycle-outline" },
  { k: "nearby", label: "Nearly there", icon: "navigate-outline" },
  { k: "delivered", label: "Delivered", icon: "checkmark-done-outline" },
];

export default function MaterialsTracking() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const pollRef = useRef<any>(null);

  const load = async () => {
    try {
      const o = await api.get<Order>(`/materials/orders/${id}`);
      setOrder(o);
    } finally { setLoading(false); }
  };

  useEffect(() => {
    load();
    // Poll every 4s for live tracking (mock simulation driven by elapsed time server-side)
    pollRef.current = setInterval(load, 4000);
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [id]);

  if (loading || !order) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.surface, paddingTop: insets.top + 20 }}>
        <Stack.Screen options={{ headerShown: false }} />
        <ActivityIndicator color={colors.brand} style={{ marginTop: spacing.xxl }} />
      </View>
    );
  }

  const activeStepIdx = STEPS.findIndex((s) => s.k === order.status);
  const center = order.driver_pos ?? order.pickup;

  const markers: WebMapMarker[] = [
    { id: "pickup", lat: order.pickup.lat, lng: order.pickup.lng, label: "🏬 " + (order.store.name || "Store") },
    { id: "drop", lat: order.drop.lat, lng: order.drop.lng, label: "📍 You" },
  ];
  if (order.driver_pos) {
    markers.push({
      id: "driver",
      lat: order.driver_pos.lat,
      lng: order.driver_pos.lng,
      label: "🛵 " + (order.status === "delivered" ? "Delivered" : `${order.mins_left ?? "--"} min`),
      active: true,
    });
  }

  const paymentLabel = order.payment_method === "upi" ? "Paid via UPI" : order.payment_method === "card" ? "Paid by card" : "Cash on delivery";

  return (
    <View style={{ flex: 1, backgroundColor: colors.surfaceSecondary }}>
      <Stack.Screen options={{ headerShown: false }} />

      {/* Map header */}
      <View style={styles.mapWrap}>
        <WebMap
          center={{ lat: center.lat, lng: center.lng }}
          zoom={13}
          markers={markers}
          highlightedId="driver"
        />
        <Pressable
          testID="track-back"
          onPress={() => router.replace("/(tabs)/market" as any)}
          style={[styles.backFab, { top: insets.top + 10 }]}
          hitSlop={10}
        >
          <Icon name="chevron-back" size={22} color={colors.onSurface} />
        </Pressable>
        <View style={[styles.etaCard, { top: insets.top + 10 }]}>
          <Text style={styles.etaLabel}>ARRIVING IN</Text>
          <Text style={styles.etaMins}>{order.status === "delivered" ? "Done" : `${order.mins_left ?? order.eta_mins} min`}</Text>
        </View>
      </View>

      {/* Bottom sheet style summary */}
      <ScrollView style={styles.sheet} contentContainerStyle={{ paddingBottom: 120 }}>
        <View style={styles.handle} />

        {/* Status timeline */}
        <View style={styles.timeline}>
          {STEPS.map((s, i) => {
            const done = i <= activeStepIdx;
            const current = i === activeStepIdx && order.status !== "delivered";
            const isLast = i === STEPS.length - 1;
            return (
              <View key={s.k} style={styles.step}>
                <View style={styles.stepLeft}>
                  <View style={[styles.stepDot, done && styles.stepDotDone, current && styles.stepDotCurrent]}>
                    {done ? (
                      <Icon name={s.icon as any} size={14} color={colors.onBrandPrimary} />
                    ) : (
                      <Icon name={s.icon as any} size={14} color={colors.muted} />
                    )}
                  </View>
                  {!isLast && <View style={[styles.stepLine, done && styles.stepLineDone]} />}
                </View>
                <View style={{ flex: 1, paddingBottom: isLast ? 0 : spacing.md }}>
                  <Text style={[styles.stepLabel, done && { color: colors.onSurface, fontWeight: "800" }]}>{s.label}</Text>
                  {current && order.status !== "delivered" && (
                    <Text style={styles.stepSub}>In progress — ETA {order.mins_left} min</Text>
                  )}
                </View>
              </View>
            );
          })}
        </View>

        {/* Store + contact */}
        <View style={styles.card}>
          <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
            <View style={{ flex: 1 }}>
              <Text style={styles.cardKicker}>FROM</Text>
              <Text style={styles.cardTitle} numberOfLines={1}>{order.store.name}</Text>
              {order.store.area ? <Text style={styles.cardSub}>{order.store.area}</Text> : null}
            </View>
            {order.store.phone ? (
              <Pressable
                testID="track-call-store"
                onPress={() => Linking.openURL(`tel:${order.store.phone}`)}
                style={styles.phoneBtn}
              >
                <Icon name="call-outline" size={14} color={colors.onBrand} />
                <Text style={styles.phoneBtnText}>Call store</Text>
              </Pressable>
            ) : null}
          </View>
        </View>

        {/* Delivery address */}
        <View style={styles.card}>
          <Text style={styles.cardKicker}>DELIVERING TO</Text>
          <Text style={styles.addressText}>{order.address}</Text>
        </View>

        {/* Items */}
        <View style={styles.card}>
          <Text style={styles.cardKicker}>{order.items.length} ITEM{order.items.length > 1 ? "S" : ""}</Text>
          {order.items.slice(0, 6).map(i => (
            <View key={i.product_id} style={styles.itemRow}>
              <Text style={{ color: colors.onSurface, fontSize: 13, flex: 1 }} numberOfLines={1}>
                {i.qty} × {i.name}
                {i.brand ? <Text style={{ color: colors.muted }}> · {i.brand}</Text> : null}
              </Text>
              <Text style={{ color: colors.onSurface, fontSize: 13, fontWeight: "700" }}>
                ₹{(i.price * i.qty).toLocaleString("en-IN")}
              </Text>
            </View>
          ))}
          {order.items.length > 6 && (
            <Text style={styles.moreText}>+ {order.items.length - 6} more</Text>
          )}
        </View>

        {/* Billing */}
        <View style={styles.card}>
          <Text style={styles.cardKicker}>BILL</Text>
          <View style={styles.sumLine}><Text style={styles.sumKey}>Subtotal</Text><Text style={styles.sumVal}>₹{order.subtotal.toLocaleString("en-IN")}</Text></View>
          <View style={styles.sumLine}><Text style={styles.sumKey}>Delivery</Text><Text style={styles.sumVal}>{order.delivery_fee ? `₹${order.delivery_fee}` : "FREE"}</Text></View>
          <View style={[styles.sumLine, { marginTop: 6 }]}>
            <Text style={[styles.sumKey, { fontWeight: "800", color: colors.onSurface }]}>Total</Text>
            <Text style={[styles.sumVal, { fontSize: 15, fontWeight: "800" }]}>₹{order.total.toLocaleString("en-IN")}</Text>
          </View>
          <View style={styles.payPill}>
            <Icon name={order.payment_method === "cod" ? "cash-outline" : "lock-closed-outline"} size={12} color={colors.brand} />
            <Text style={styles.payPillText}>{paymentLabel}</Text>
          </View>
        </View>

        <View style={{ padding: spacing.lg, alignItems: "center" }}>
          <Text style={styles.orderId}>Order #{order.id.slice(-6).toUpperCase()}</Text>
          <Text style={styles.placedAt}>Placed {new Date(order.created_at).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })}</Text>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  mapWrap: { height: "42%", backgroundColor: colors.surfaceSecondary },
  backFab: { position: "absolute", left: spacing.lg, width: 40, height: 40, borderRadius: 20, backgroundColor: colors.surface, alignItems: "center", justifyContent: "center", borderWidth: 1, borderColor: colors.border },
  etaCard: { position: "absolute", right: spacing.lg, backgroundColor: colors.surface, paddingHorizontal: 14, paddingVertical: 10, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, alignItems: "center" },
  etaLabel: { fontSize: 10, fontWeight: "800", color: colors.muted, letterSpacing: 0.6 },
  etaMins: { fontSize: 18, fontWeight: "800", color: colors.brand, letterSpacing: -0.3 },
  sheet: { flex: 1, marginTop: -24, backgroundColor: colors.surface, borderTopLeftRadius: 24, borderTopRightRadius: 24 },
  handle: { alignSelf: "center", width: 48, height: 4, borderRadius: 2, backgroundColor: colors.border, marginTop: 10, marginBottom: 8 },
  timeline: { padding: spacing.lg },
  step: { flexDirection: "row", gap: spacing.md },
  stepLeft: { width: 28, alignItems: "center" },
  stepDot: { width: 28, height: 28, borderRadius: 14, backgroundColor: colors.surfaceSecondary, alignItems: "center", justifyContent: "center", borderWidth: 1, borderColor: colors.border },
  stepDotDone: { backgroundColor: colors.success, borderColor: colors.success },
  stepDotCurrent: { backgroundColor: colors.brandPrimary, borderColor: colors.brandPrimary },
  stepLine: { width: 2, flex: 1, backgroundColor: colors.border, marginTop: 2 },
  stepLineDone: { backgroundColor: colors.success },
  stepLabel: { fontSize: 13, color: colors.muted, fontWeight: "600" },
  stepSub: { fontSize: 11, color: colors.brandPrimary, marginTop: 2 },
  card: { marginHorizontal: spacing.lg, marginBottom: spacing.md, backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, borderRadius: radius.lg, padding: spacing.md, gap: 6 },
  cardKicker: { fontSize: 10, fontWeight: "800", color: colors.muted, letterSpacing: 0.8 },
  cardTitle: { fontSize: 15, fontWeight: "800", color: colors.onSurface },
  cardSub: { fontSize: 11, color: colors.muted, marginTop: 2 },
  phoneBtn: { flexDirection: "row", alignItems: "center", gap: 6, backgroundColor: colors.brand, paddingHorizontal: 12, paddingVertical: 8, borderRadius: radius.pill },
  phoneBtnText: { color: colors.onBrand, fontSize: 12, fontWeight: "700" },
  addressText: { fontSize: 13, color: colors.onSurface, lineHeight: 18 },
  itemRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingVertical: 4 },
  moreText: { fontSize: 11, color: colors.muted, marginTop: 4 },
  sumLine: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingVertical: 2 },
  sumKey: { fontSize: 13, color: colors.onSurfaceSecondary },
  sumVal: { fontSize: 13, color: colors.onSurface, fontWeight: "600" },
  payPill: { flexDirection: "row", alignItems: "center", gap: 4, alignSelf: "flex-start", backgroundColor: colors.brandTertiary, paddingHorizontal: 10, paddingVertical: 4, borderRadius: radius.pill, marginTop: 6 },
  payPillText: { color: colors.brand, fontSize: 11, fontWeight: "700" },
  orderId: { fontSize: 12, fontWeight: "800", color: colors.onSurface, letterSpacing: 1 },
  placedAt: { fontSize: 11, color: colors.muted, marginTop: 2 },
});
