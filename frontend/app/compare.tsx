import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, Pressable } from "react-native";
import { Image } from "expo-image";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useLocalSearchParams, useRouter, Stack } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius } from "@/src/theme";
import { api } from "@/src/api";
import { formatINR, indianComma } from "@/src/utils/format";

type CompareProp = {
  id: string; title: string; type: string; price: number; area: number; area_unit: string;
  price_per_unit: number; bedrooms?: number | null; facing?: string; road_width_ft?: number;
  address: string; verified: boolean; source: string;
  images: string[]; locality_name: string;
  infravalue?: { low: number; high: number; confidence: string };
  govt_value?: number;
};

const COL_WIDTH = 180;

export default function Compare() {
  const { ids } = useLocalSearchParams<{ ids: string }>();
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [items, setItems] = useState<CompareProp[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      if (!ids) return;
      try {
        const data = await api.get<CompareProp[]>(`/compare?ids=${ids}`);
        setItems(data);
      } finally { setLoading(false); }
    })();
  }, [ids]);

  const rows: Array<{ label: string; render: (p: CompareProp) => React.ReactNode; highlight?: (p: CompareProp) => boolean }> = [
    { label: "Price", render: (p) => <Text style={styles.big}>{formatINR(p.price)}</Text> },
    { label: "Area", render: (p) => <Text style={styles.val}>{p.area} {p.area_unit}</Text> },
    { label: "Price / unit", render: (p) => <Text style={styles.val}>{`₹${indianComma(p.price_per_unit)}/${p.area_unit.split(" ")[0]}`}</Text> },
    { label: "Type", render: (p) => <Text style={styles.val}>{p.type}</Text> },
    { label: "Bedrooms", render: (p) => <Text style={styles.val}>{p.bedrooms ? `${p.bedrooms} BHK` : "—"}</Text> },
    { label: "Facing", render: (p) => <Text style={styles.val}>{p.facing || "—"}</Text> },
    { label: "Road width", render: (p) => <Text style={styles.val}>{p.road_width_ft ? `${p.road_width_ft} ft` : "—"}</Text> },
    { label: "Locality", render: (p) => <Text style={styles.val}>{p.locality_name}</Text> },
    { label: "Source", render: (p) => <Text style={styles.val}>{p.source}</Text> },
    { label: "Verified", render: (p) => p.verified ? <Icon name="shield-checkmark" size={18} color={colors.success} /> : <Text style={styles.val}>—</Text> },
  ];

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <Stack.Screen options={{ headerShown: false }} />
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="compare-back-btn" onPress={() => router.back()} hitSlop={12}>
          <Icon name="chevron-back" size={26} color={colors.onSurface} />
        </Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.title}>Compare</Text>
          <Text style={styles.sub}>{items.length} properties side-by-side</Text>
        </View>
      </View>

      {loading ? (
        <ActivityIndicator color={colors.brand} style={{ marginTop: spacing.xxl }} />
      ) : items.length === 0 ? (
        <Text style={styles.empty}>No properties to compare. Go back and select at least 2.</Text>
      ) : (
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <View>
            {/* Header row */}
            <View style={styles.row}>
              <View style={[styles.labelCell]}>
                <Text style={styles.labelHead}>Property</Text>
              </View>
              {items.map(p => (
                <Pressable
                  key={p.id}
                  testID={`compare-col-${p.id}`}
                  onPress={() => router.push(`/property/${p.id}` as any)}
                  style={[styles.cellCard]}
                >
                  <Image source={{ uri: p.images?.[0] }} style={styles.thumb} contentFit="cover" />
                  <Text style={styles.cardTitle} numberOfLines={2}>{p.title}</Text>
                  <Text style={styles.cardAddr} numberOfLines={1}>{p.address}</Text>
                </Pressable>
              ))}
            </View>

            {rows.map((r, idx) => (
              <View key={r.label} style={[styles.row, idx % 2 === 1 && styles.rowAlt]}>
                <View style={styles.labelCell}><Text style={styles.labelText}>{r.label}</Text></View>
                {items.map(p => (
                  <View key={p.id} style={styles.valueCell}>
                    {r.render(p)}
                  </View>
                ))}
              </View>
            ))}
          </View>
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", gap: spacing.sm, paddingHorizontal: spacing.xl, paddingBottom: spacing.md, borderBottomWidth: 1, borderBottomColor: colors.border },
  title: { fontSize: 22, fontWeight: "800", color: colors.onSurface },
  sub: { fontSize: 12, color: colors.muted, marginTop: 2 },
  empty: { textAlign: "center", color: colors.muted, marginTop: spacing.xxl, fontSize: 13 },
  row: { flexDirection: "row", alignItems: "stretch" },
  rowAlt: { backgroundColor: colors.surfaceSecondary },
  labelCell: { width: 120, padding: spacing.md, justifyContent: "center", borderRightWidth: 1, borderRightColor: colors.border },
  labelHead: { fontSize: 11, fontWeight: "800", color: colors.muted, letterSpacing: 0.8 },
  labelText: { fontSize: 12, color: colors.muted, fontWeight: "600" },
  valueCell: { width: COL_WIDTH, padding: spacing.md, justifyContent: "center", borderRightWidth: 1, borderRightColor: colors.border },
  cellCard: { width: COL_WIDTH, padding: spacing.md, borderRightWidth: 1, borderRightColor: colors.border },
  thumb: { width: "100%", height: 90, borderRadius: radius.sm, backgroundColor: colors.surfaceSecondary },
  cardTitle: { fontSize: 13, fontWeight: "700", color: colors.onSurface, marginTop: spacing.sm },
  cardAddr: { fontSize: 11, color: colors.muted, marginTop: 2 },
  val: { fontSize: 13, color: colors.onSurface, fontWeight: "600" },
  big: { fontSize: 16, color: colors.onSurface, fontWeight: "800", letterSpacing: -0.2 },
  badge: { alignSelf: "flex-start", paddingHorizontal: 8, paddingVertical: 3, borderRadius: radius.pill },
  badgeGreen: { backgroundColor: "rgba(46, 109, 77, 0.12)" },
  badgeRed: { backgroundColor: "rgba(139, 0, 0, 0.10)" },
  badgeText: { fontSize: 11, fontWeight: "800" },
});
