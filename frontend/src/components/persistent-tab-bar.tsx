import React from "react";
import { View, Text, Pressable, StyleSheet, Platform } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter, usePathname } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius } from "@/src/theme";

/**
 * Floating 5-tab bar that renders on every detail screen so the user always
 * has fast access to the main tabs. The real tab bar inside (tabs)/_layout.tsx
 * continues to render when inside the (tabs) group. On non-tabs screens, this
 * floating variant covers for it so the lower navigation is persistent.
 */

type Tab = { key: string; label: string; icon: any; path: any };

const TABS: Tab[] = [
  { key: "explore", label: "Explore", icon: "map-outline", path: "/(tabs)/explore" },
  { key: "agents",  label: "Experts",  icon: "people-outline", path: "/(tabs)/agents" },
  { key: "news",    label: "News",    icon: "newspaper-outline", path: "/(tabs)/news" },
  { key: "market",  label: "Market",  icon: "storefront-outline", path: "/(tabs)/market" },
  { key: "saved",   label: "Saved",   icon: "heart-outline", path: "/(tabs)/saved" },
];

export function PersistentTabBar() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const pathname = usePathname() ?? "";

  // Guess the "active" tab from the current pathname (loose match)
  const active = TABS.find((t) => pathname.includes(`/${t.key}`))?.key;

  return (
    <View
      pointerEvents="box-none"
      style={[
        styles.wrap,
        { paddingBottom: Math.max(insets.bottom, 6) },
      ]}
    >
      <View style={styles.bar}>
        {TABS.map((t) => {
          const isActive = active === t.key;
          return (
            <Pressable
              key={t.key}
              testID={`persistent-tab-${t.key}`}
              onPress={() => router.push(t.path)}
              style={styles.tab}
              android_ripple={{ color: colors.border, borderless: true }}
              hitSlop={{ top: 6, bottom: 6, left: 4, right: 4 }}
            >
              <Icon
                name={t.icon}
                size={22}
                color={isActive ? colors.brand : colors.muted}
              />
              <Text style={[styles.label, isActive && styles.labelActive]}>
                {t.label}
              </Text>
            </Pressable>
          );
        })}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    backgroundColor: colors.surface,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    ...Platform.select({
      ios: {
        shadowColor: "#000",
        shadowOpacity: 0.08,
        shadowOffset: { width: 0, height: -2 },
        shadowRadius: 8,
      },
      android: { elevation: 10 },
    }),
  },
  bar: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingTop: 6,
    paddingHorizontal: spacing.sm,
  },
  tab: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 4,
    minHeight: 44,
  },
  label: {
    fontSize: 10,
    fontWeight: "600",
    color: colors.muted,
    marginTop: 2,
  },
  labelActive: { color: colors.brand, fontWeight: "700" },
});
