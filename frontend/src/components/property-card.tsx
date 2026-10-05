import React from "react";
import { View, Text, Pressable, StyleSheet } from "react-native";
import { Image } from "expo-image";
import Icon from "@react-native-vector-icons/ionicons";
import { useRouter } from "expo-router";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { formatINR, indianComma } from "@/src/utils/format";

export type Property = {
  id: string;
  title: string;
  type: string;
  price: number;
  area: number;
  area_unit: string;
  price_per_unit: number;
  address: string;
  images: string[];
  verified: boolean;
  featured?: boolean;
  featured_tier?: string;
  source: string;
  bedrooms?: number | null;
  locality_name?: string;
};

export function PropertyCard({ property, compact = false, onPress }: { property: Property; compact?: boolean; onPress?: () => void }) {
  const router = useRouter();
  const go = onPress || (() => router.push(`/property/${property.id}`));
  return (
    <Pressable testID={`property-card-${property.id}`} onPress={go} style={[styles.card, compact && styles.cardCompact, property.featured && styles.cardFeatured]}>
      <Image source={{ uri: property.images?.[0] }} style={compact ? styles.imgCompact : styles.img} contentFit="cover" transition={200} />
      {property.featured && (
        <View style={styles.featuredBadge}>
          <Icon name="star" size={11} color="#FFFFFF" />
          <Text style={styles.featuredText}>Featured</Text>
        </View>
      )}
      {property.verified && (
        <View style={[styles.verifiedBadge, property.featured ? { top: compact ? 6 : spacing.md + 28, left: spacing.md } : null]}>
          <Icon name="checkmark-circle" size={12} color={colors.onSuccess} />
          <Text style={styles.verifiedText}>Verified</Text>
        </View>
      )}
      <View style={styles.body}>
        <Text style={styles.price}>{formatINR(property.price)}</Text>
        <Text style={styles.title} numberOfLines={1}>{property.title}</Text>
        <View style={styles.metaRow}>
          <Text style={styles.meta}>{property.area} {property.area_unit}</Text>
          <View style={styles.dot} />
          <Text style={styles.meta}>{`₹${indianComma(property.price_per_unit)}/${property.area_unit.split(' ')[0]}`}</Text>
        </View>
        <View style={styles.footRow}>
          <Icon name="location-outline" size={12} color={colors.muted} />
          <Text style={styles.address} numberOfLines={1}>{property.address}</Text>
        </View>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface, borderRadius: radius.lg, overflow: "hidden",
    marginBottom: spacing.md, borderWidth: 1, borderColor: colors.border,
  },
  cardCompact: { flexDirection: "row", height: 110, marginBottom: spacing.sm },
  cardFeatured: { borderColor: "#D4A72C", borderWidth: 2 },
  img: { width: "100%", height: 180, backgroundColor: colors.surfaceTertiary },
  imgCompact: { width: 130, height: "100%", backgroundColor: colors.surfaceTertiary },
  featuredBadge: {
    position: "absolute", top: spacing.sm, left: spacing.sm, flexDirection: "row",
    alignItems: "center", gap: 3, backgroundColor: "#D4A72C",
    paddingHorizontal: 8, paddingVertical: 3, borderRadius: radius.pill,
  },
  featuredText: { color: "#FFFFFF", fontSize: 10, fontWeight: "800", letterSpacing: 0.3 },
  verifiedBadge: {
    position: "absolute", top: spacing.md, left: spacing.md, flexDirection: "row",
    alignItems: "center", gap: 4, backgroundColor: colors.success,
    paddingHorizontal: spacing.sm, paddingVertical: 3, borderRadius: radius.pill,
  },
  verifiedText: { color: colors.onSuccess, fontSize: 10, fontWeight: "700", letterSpacing: 0.3 },
  body: { padding: spacing.md, flex: 1, justifyContent: "center" },
  price: { fontSize: 20, fontWeight: "700", color: colors.brand, letterSpacing: -0.3 },
  title: { fontSize: 14, color: colors.onSurface, marginTop: 2, fontWeight: "500" },
  metaRow: { flexDirection: "row", alignItems: "center", gap: spacing.sm, marginTop: spacing.sm - 2 },
  meta: { color: colors.onSurfaceSecondary, fontSize: 12 },
  dot: { width: 3, height: 3, borderRadius: 2, backgroundColor: colors.muted },
  footRow: { flexDirection: "row", alignItems: "center", gap: 4, marginTop: 6 },
  address: { color: colors.muted, fontSize: 12, flex: 1 },
});
