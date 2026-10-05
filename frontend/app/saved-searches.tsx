import React, { useCallback, useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, ActivityIndicator, Alert } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useFocusEffect, useRouter } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";
import { useAuth } from "@/src/auth-context";

type Search = {
  id: string; name: string; params: Record<string, any>;
  notify: boolean; last_match_count: number; created_at: string;
};

function describe(params: Record<string, any>): string {
  const bits: string[] = [];
  if (params.type) bits.push(params.type);
  if (params.listing_type) bits.push(`for ${params.listing_type}`);
  if (params.bedrooms) bits.push(`${params.bedrooms} BHK`);
  if (params.min_price || params.max_price) {
    const lo = params.min_price ? `₹${(params.min_price / 1e5).toFixed(1)}L` : "any";
    const hi = params.max_price ? `₹${(params.max_price / 1e5).toFixed(1)}L` : "any";
    bits.push(`${lo}–${hi}`);
  }
  if (params.q) bits.push(`"${params.q}"`);
  if (params.verified_only) bits.push("verified");
  if (params.locality_id) bits.push("in locality");
  return bits.join(" · ") || "All properties";
}

export default function SavedSearches() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { user } = useAuth();
  const [list, setList] = useState<Search[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    try {
      const data = await api.get<Search[]>(`/saved-searches?user_id=${user.id}`);
      setList(data);
    } finally { setLoading(false); }
  }, [user]);

  useFocusEffect(useCallback(() => { load(); }, [load]));

  const openSearch = (s: Search) => {
    const qs = new URLSearchParams();
    if (s.params.type) qs.set("type", s.params.type);
    if (s.params.q) qs.set("q", s.params.q);
    router.push({ pathname: "/(tabs)/explore", params: Object.fromEntries(qs) } as any);
  };

  const removeSearch = (s: Search) => {
    Alert.alert("Delete alert?", s.name, [
      { text: "Cancel", style: "cancel" },
      { text: "Delete", style: "destructive", onPress: async () => {
        await fetch(`${process.env.EXPO_PUBLIC_BACKEND_URL || ""}/api/saved-searches/${s.id}?user_id=${user?.id}`, { method: "DELETE" });
        load();
      } },
    ]);
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="saved-searches-back-btn" onPress={() => router.back()} hitSlop={12}><Icon name="chevron-back" size={26} color={colors.onSurface} /></Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.title}>Saved searches & alerts</Text>
          <Text style={styles.sub}>We nudge you when a new match pops up</Text>
        </View>
        <Pressable testID="create-search-btn" onPress={() => router.push("/(tabs)/explore" as any)} style={styles.addBtn} hitSlop={10}>
          <Icon name="add" size={18} color={colors.onBrandPrimary} />
        </Pressable>
      </View>

      <ScrollView contentContainerStyle={{ padding: spacing.lg, gap: spacing.md, paddingBottom: 60 }}>
        {loading ? (
          <ActivityIndicator color={colors.brand} style={{ marginTop: spacing.xxl }} />
        ) : list.length === 0 ? (
          <View style={styles.empty}>
            <Icon name="notifications-outline" size={40} color={colors.muted} />
            <Text style={styles.emptyText}>No saved searches yet.</Text>
            <Text style={styles.emptySub}>Set a search in Explore and tap “Save & alert me” to never miss a new listing.</Text>
            <Pressable testID="go-explore-btn" onPress={() => router.push("/(tabs)/explore" as any)} style={styles.goBtn}>
              <Icon name="search" size={14} color={colors.onBrandPrimary} />
              <Text style={styles.goTxt}>Go to Explore</Text>
            </Pressable>
          </View>
        ) : list.map(s => (
          <View key={s.id} style={styles.card} testID={`search-row-${s.id}`}>
            <Pressable style={{ flex: 1 }} onPress={() => openSearch(s)}>
              <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
                <Icon name="notifications" size={14} color={s.notify ? colors.brandPrimary : colors.muted} />
                <Text style={styles.name} numberOfLines={1}>{s.name}</Text>
              </View>
              <Text style={styles.desc} numberOfLines={1}>{describe(s.params)}</Text>
              <View style={styles.matchRow}>
                <Icon name="layers-outline" size={11} color={colors.success} />
                <Text style={styles.matchTxt}>{s.last_match_count} match{s.last_match_count === 1 ? "" : "es"} as of now</Text>
              </View>
            </Pressable>
            <View style={{ gap: 8 }}>
              <Pressable testID={`view-search-${s.id}`} onPress={() => openSearch(s)} style={styles.viewBtn}>
                <Icon name="arrow-forward" size={14} color={colors.onBrandPrimary} />
              </Pressable>
              <Pressable testID={`delete-search-${s.id}`} onPress={() => removeSearch(s)} style={styles.delBtn}>
                <Icon name="trash-outline" size={14} color={colors.error} />
              </Pressable>
            </View>
          </View>
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingHorizontal: spacing.lg, paddingBottom: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  title: { fontSize: 20, fontWeight: "800", color: colors.onSurface },
  sub: { fontSize: 11, color: colors.muted, marginTop: 2 },
  addBtn: { width: 36, height: 36, borderRadius: 18, backgroundColor: colors.brandPrimary, alignItems: "center", justifyContent: "center" },
  empty: { padding: spacing.xxl, alignItems: "center", gap: 8 },
  emptyText: { fontSize: 15, fontWeight: "800", color: colors.onSurface, marginTop: spacing.md },
  emptySub: { fontSize: 12, color: colors.muted, textAlign: "center", lineHeight: 17, marginTop: 4 },
  goBtn: { flexDirection: "row", alignItems: "center", gap: 6, paddingVertical: 10, paddingHorizontal: 16, borderRadius: radius.pill, backgroundColor: colors.brandPrimary, marginTop: spacing.md },
  goTxt: { color: colors.onBrandPrimary, fontWeight: "700", fontSize: 13 },
  card: { flexDirection: "row", alignItems: "flex-start", gap: 10, padding: spacing.md, borderRadius: radius.lg, backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, ...shadow.card },
  name: { fontSize: 14, fontWeight: "800", color: colors.onSurface, flex: 1 },
  desc: { fontSize: 11, color: colors.muted, marginTop: 4 },
  matchRow: { flexDirection: "row", alignItems: "center", gap: 4, marginTop: 6 },
  matchTxt: { fontSize: 11, fontWeight: "700", color: colors.success },
  viewBtn: { width: 32, height: 32, borderRadius: 16, backgroundColor: colors.brand, alignItems: "center", justifyContent: "center" },
  delBtn: { width: 32, height: 32, borderRadius: 16, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border, alignItems: "center", justifyContent: "center" },
});
