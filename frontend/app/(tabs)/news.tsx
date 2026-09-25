import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, ActivityIndicator, RefreshControl } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius } from "@/src/theme";
import { api } from "@/src/api";

const CATS = ["All", "Infrastructure", "Government", "Development", "Residential", "Industrial", "Commercial"];

type NewsItem = { id: string; title: string; summary: string; category: string; locality_id: string; date: string; source: string };

export default function News() {
  const insets = useSafeAreaInsets();
  const [items, setItems] = useState<NewsItem[]>([]);
  const [cat, setCat] = useState("All");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = async () => {
    try {
      const qs = cat === "All" ? "" : `?category=${encodeURIComponent(cat)}`;
      const data = await api.get<NewsItem[]>(`/news${qs}`);
      setItems(data);
    } finally { setLoading(false); setRefreshing(false); }
  };
  useEffect(() => { setLoading(true); load(); }, [cat]);

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <View style={{ paddingTop: insets.top + spacing.md, paddingHorizontal: spacing.xl, paddingBottom: spacing.sm, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border }}>
        <Text style={styles.title}>InfraLocal News</Text>
        <Text style={styles.sub}>Hyperlocal property intelligence, short and sharp.</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chipsRow}>
          {CATS.map(c => (
            <Pressable key={c} testID={`news-cat-${c.toLowerCase()}`} onPress={() => setCat(c)} style={[styles.chip, cat === c && styles.chipActive]}>
              <Text style={[styles.chipText, cat === c && styles.chipTextActive]}>{c}</Text>
            </Pressable>
          ))}
        </ScrollView>
      </View>

      <ScrollView contentContainerStyle={{ padding: spacing.xl, paddingBottom: spacing.xxxl }} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); load(); }} />}>
        {loading ? <ActivityIndicator color={colors.brand} style={{ marginTop: spacing.xxl }} /> :
          items.map(n => (
            <View key={n.id} testID={`news-card-${n.id}`} style={styles.card}>
              <View style={styles.cardTop}>
                <View style={styles.badge}><Text style={styles.badgeText}>{n.category}</Text></View>
                <Text style={styles.date}>{new Date(n.date).toLocaleDateString("en-IN", { day: "2-digit", month: "short" })}</Text>
              </View>
              <Text style={styles.newsTitle}>{n.title}</Text>
              <Text style={styles.newsSummary}>{n.summary}</Text>
              <View style={styles.metaRow}>
                <Icon name="newspaper-outline" size={12} color={colors.muted} />
                <Text style={styles.source}>{n.source}</Text>
              </View>
            </View>
          ))
        }
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  title: { fontSize: 24, fontWeight: "700", color: colors.brand, letterSpacing: -0.3 },
  sub: { color: colors.muted, marginTop: 2, fontSize: 13 },
  chipsRow: { paddingTop: spacing.md, gap: spacing.sm, paddingBottom: spacing.xs },
  chip: { paddingHorizontal: spacing.md, height: 36, justifyContent: "center", borderRadius: radius.pill, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border, flexShrink: 0 },
  chipActive: { backgroundColor: colors.brand, borderColor: colors.brand },
  chipText: { color: colors.onSurface, fontSize: 12, fontWeight: "600" },
  chipTextActive: { color: colors.onBrand },
  card: { padding: spacing.lg, borderRadius: radius.lg, backgroundColor: colors.surfaceSecondary, marginBottom: spacing.md, borderWidth: 1, borderColor: colors.border },
  cardTop: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.sm },
  badge: { backgroundColor: colors.brandTertiary, paddingHorizontal: spacing.md, paddingVertical: 3, borderRadius: radius.pill },
  badgeText: { fontSize: 10, fontWeight: "700", color: colors.brand, letterSpacing: 0.3 },
  date: { fontSize: 11, color: colors.muted, fontWeight: "600" },
  newsTitle: { fontSize: 15, fontWeight: "700", color: colors.onSurface, letterSpacing: -0.2, lineHeight: 21 },
  newsSummary: { fontSize: 13, color: colors.onSurfaceSecondary, marginTop: spacing.sm, lineHeight: 19 },
  metaRow: { flexDirection: "row", alignItems: "center", gap: 4, marginTop: spacing.md },
  source: { fontSize: 11, color: colors.muted, fontWeight: "500" },
});
