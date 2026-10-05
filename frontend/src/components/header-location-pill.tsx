import React from "react";
import { Pressable, Text, View, StyleSheet } from "react-native";
import { useRouter } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius } from "@/src/theme";
import { useLocationStore } from "@/src/stores/location";

/**
 * Reusable top-left pill that shows the active location and opens the
 * Zomato-style location picker on tap. Used in Explore, Market, Experts, News.
 */
type Props = {
  kicker?: string;         // small line above the location (e.g. "Hi, Rahul")
  testID?: string;
  compact?: boolean;       // slightly smaller for pages with heavier headers
};

export function HeaderLocationPill({ kicker, testID = "header-location-pill", compact }: Props) {
  const router = useRouter();
  const active = useLocationStore(s => s.getActive());
  const label = active?.label || "Jaipur";

  return (
    <Pressable
      testID={testID}
      onPress={() => router.push("/location-picker" as any)}
      style={[styles.pill, compact && styles.pillCompact]}
      hitSlop={6}
    >
      <Icon name="location-outline" size={14} color={colors.brand} />
      <View style={{ flex: 1 }}>
        {kicker ? <Text style={styles.kicker} numberOfLines={1}>{kicker}</Text> : null}
        <Text style={styles.title} numberOfLines={1}>
          {label} <Icon name="chevron-down" size={11} color={colors.onSurface} />
        </Text>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  pill: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    paddingHorizontal: spacing.md,
    paddingVertical: 6,
    backgroundColor: colors.surfaceSecondary,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: colors.border,
    maxWidth: "72%",
  },
  pillCompact: {
    paddingVertical: 4,
  },
  kicker: {
    fontSize: 10,
    color: colors.muted,
    fontWeight: "700",
  },
  title: {
    fontSize: 13,
    color: colors.onSurface,
    fontWeight: "800",
  },
});
