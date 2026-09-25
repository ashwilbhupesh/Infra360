import React from "react";
import { View, Text, Pressable, StyleSheet } from "react-native";
import { Image } from "expo-image";
import { useRouter } from "expo-router";
import { colors, spacing, radius } from "@/src/theme";
import { indianComma } from "@/src/utils/format";

export type Locality = {
  id: string;
  name: string;
  city: string;
  image: string;
  median_price_per_sq_yd: number;
  yoy_change_pct: number;
  listings_count: number;
};

export function LocalityCard({ locality, wide = false }: { locality: Locality; wide?: boolean }) {
  const router = useRouter();
  return (
    <Pressable
      testID={`locality-card-${locality.id}`}
      onPress={() => router.push(`/locality/${locality.id}`)}
      style={[styles.card, wide ? styles.wide : styles.normal]}
    >
      <Image source={{ uri: locality.image }} style={styles.img} contentFit="cover" transition={200} />
      <View style={styles.overlay} />
      <View style={styles.info}>
        <Text style={styles.name}>{locality.name}</Text>
        <Text style={styles.city}>{locality.city}</Text>
        <View style={styles.pillsRow}>
          <View style={styles.pill}>
            <Text style={styles.pillText}>₹{indianComma(locality.median_price_per_sq_yd)}/sq yd</Text>
          </View>
          <View style={[styles.pill, { backgroundColor: locality.yoy_change_pct > 0 ? colors.success : colors.error }]}>
            <Text style={[styles.pillText, { color: "#fff" }]}>
              {locality.yoy_change_pct > 0 ? "+" : ""}{locality.yoy_change_pct}% YoY
            </Text>
          </View>
        </View>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: { borderRadius: radius.lg, overflow: "hidden", marginRight: spacing.md, backgroundColor: colors.surfaceTertiary },
  normal: { width: 240, height: 170 },
  wide: { width: "100%", height: 200, marginRight: 0, marginBottom: spacing.md },
  img: { ...StyleSheet.absoluteFillObject },
  overlay: { ...StyleSheet.absoluteFillObject, backgroundColor: "rgba(10,25,47,0.35)" },
  info: { position: "absolute", left: spacing.lg, right: spacing.lg, bottom: spacing.lg },
  name: { color: "#FFFFF0", fontSize: 20, fontWeight: "700", letterSpacing: -0.3 },
  city: { color: "#F8F8F2", fontSize: 12, marginTop: 2, opacity: 0.9 },
  pillsRow: { flexDirection: "row", gap: spacing.sm, marginTop: spacing.sm },
  pill: { backgroundColor: "rgba(255,255,240,0.92)", paddingHorizontal: spacing.md, paddingVertical: 4, borderRadius: radius.pill },
  pillText: { fontSize: 11, fontWeight: "600", color: colors.brand },
});
