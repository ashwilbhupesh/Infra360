import React, { useEffect, useState, useCallback } from "react";
import { View, Text, StyleSheet, Pressable, ScrollView, ActivityIndicator } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useFocusEffect, useRouter } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius } from "@/src/theme";
import { api } from "@/src/api";
import { PropertyCard } from "@/src/components/property-card";
import { getHistory, clearHistory } from "@/src/utils/history";

export default function History() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const ids = await getHistory();
      if (!ids.length) { setItems([]); return; }
      const results = await Promise.all(ids.map(id => api.get<any>(`/properties/${id}`).catch(() => null)));
      setItems(results.filter(Boolean));
    } finally { setLoading(false); }
  }, []);

  useFocusEffect(useCallback(() => { load(); }, [load]));

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="history-back-btn" onPress={() => router.back()} hitSlop={12}>
          <Icon name="chevron-back" size={26} color={colors.onSurface} />
        </Pressable>
        <Text style={styles.title}>Recently viewed</Text>
        {items.length > 0 && (
          <Pressable testID="history-clear-btn" onPress={async () => { await clearHistory(); load(); }} hitSlop={8}>
            <Text style={styles.clear}>Clear</Text>
          </Pressable>
        )}
      </View>
      {loading ? (
        <ActivityIndicator style={{ marginTop: spacing.xxxl }} color={colors.brand} />
      ) : items.length === 0 ? (
        <View style={styles.empty}>
          <Icon name="time-outline" size={40} color={colors.muted} />
          <Text style={styles.emptyText}>No properties viewed yet</Text>
          <Pressable testID="history-explore-btn" onPress={() => router.replace("/(tabs)/explore" as any)} style={styles.primaryBtn}>
            <Text style={styles.primaryText}>Explore properties</Text>
          </Pressable>
        </View>
      ) : (
        <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingBottom: 60 }}>
          {items.map(p => <PropertyCard key={p.id} property={p} />)}
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingHorizontal: spacing.lg, paddingBottom: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  title: { flex: 1, fontSize: 20, fontWeight: "800", color: colors.onSurface },
  clear: { color: colors.brand, fontSize: 13, fontWeight: "700" },
  empty: { alignItems: "center", marginTop: 90, paddingHorizontal: spacing.xl, gap: spacing.md },
  emptyText: { color: colors.muted, fontSize: 14 },
  primaryBtn: { marginTop: spacing.md, paddingHorizontal: spacing.xl, height: 44, borderRadius: radius.md, backgroundColor: colors.brandPrimary, alignItems: "center", justifyContent: "center" },
  primaryText: { color: colors.onBrandPrimary, fontWeight: "700" },
});
