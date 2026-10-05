import React, { useCallback, useState } from "react";
import { View, Text, StyleSheet, Pressable, ScrollView, Alert } from "react-native";
import { Image } from "expo-image";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useFocusEffect, useRouter, Stack } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius } from "@/src/theme";
import { getOfflineNews, removeOffline, clearOfflineNews, OfflineNewsItem, shareOnWhatsApp } from "@/src/utils/news-share";

export default function OfflineNews() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [list, setList] = useState<OfflineNewsItem[]>([]);

  const load = useCallback(async () => setList(await getOfflineNews()), []);
  useFocusEffect(useCallback(() => { load(); }, [load]));

  const remove = (id: string) => {
    Alert.alert("Remove?", "Delete this saved article?", [
      { text: "Cancel", style: "cancel" },
      { text: "Remove", style: "destructive", onPress: async () => { await removeOffline(id); load(); } },
    ]);
  };

  const clearAll = () => {
    if (list.length === 0) return;
    Alert.alert("Clear all offline reads?", `Delete ${list.length} saved articles.`, [
      { text: "Cancel", style: "cancel" },
      { text: "Clear all", style: "destructive", onPress: async () => { await clearOfflineNews(); load(); } },
    ]);
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <Stack.Screen options={{ headerShown: false }} />
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="offline-back" onPress={() => router.back()} hitSlop={12}>
          <Icon name="chevron-back" size={26} color={colors.onSurface} />
        </Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.title}>Offline reads</Text>
          <Text style={styles.sub}>{list.length} saved · ready without internet</Text>
        </View>
        {list.length > 0 && (
          <Pressable testID="offline-clear" onPress={clearAll} hitSlop={10}>
            <Icon name="trash-outline" size={20} color={colors.error} />
          </Pressable>
        )}
      </View>

      <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingBottom: 60, gap: spacing.md }}>
        {list.length === 0 ? (
          <View style={styles.empty}>
            <Icon name="bookmark-outline" size={40} color={colors.muted} />
            <Text style={styles.emptyTitle}>No saved articles yet</Text>
            <Text style={styles.emptySub}>Tap "Save offline" on any news story to read it later without internet.</Text>
            <Pressable testID="go-news" onPress={() => router.push("/(tabs)/news" as any)} style={styles.goBtn}>
              <Icon name="newspaper-outline" size={14} color={colors.onBrandPrimary} />
              <Text style={styles.goTxt}>Browse news</Text>
            </Pressable>
          </View>
        ) : list.map(n => (
          <View key={n.id} style={styles.card} testID={`offline-row-${n.id}`}>
            {n.image ? <Image source={{ uri: n.image }} style={styles.img} contentFit="cover" /> : null}
            <View style={{ padding: spacing.md }}>
              <View style={styles.topRow}>
                <View style={styles.badge}><Text style={styles.badgeTxt}>{n.category}</Text></View>
                <Text style={styles.date}>{new Date(n.saved_at).toLocaleDateString("en-IN", { day: "2-digit", month: "short" })}</Text>
              </View>
              <Text style={styles.newsTitle}>{n.title}</Text>
              <Text style={styles.newsSummary} numberOfLines={4}>{n.summary}</Text>
              {n.locality_name ? (
                <View style={styles.metaRow}>
                  <Icon name="location-outline" size={11} color={colors.muted} />
                  <Text style={styles.meta}>{n.locality_name}</Text>
                  <Text style={styles.meta}>·</Text>
                  <Text style={styles.meta}>{n.source}</Text>
                </View>
              ) : <Text style={styles.meta}>{n.source}</Text>}
              <View style={styles.actionRow}>
                <Pressable
                  testID={`offline-share-${n.id}`}
                  onPress={() => shareOnWhatsApp({ title: n.title, summary: n.summary, source: n.source, locality_name: n.locality_name })}
                  style={[styles.actionBtn, { backgroundColor: "#25D366" }]}
                >
                  <Icon name="logo-whatsapp" size={14} color="#FFFFFF" />
                  <Text style={styles.actionTxt}>WhatsApp</Text>
                </Pressable>
                <Pressable
                  testID={`offline-remove-${n.id}`}
                  onPress={() => remove(n.id)}
                  style={[styles.actionBtn, { backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.error }]}
                >
                  <Icon name="trash-outline" size={14} color={colors.error} />
                  <Text style={[styles.actionTxt, { color: colors.error }]}>Remove</Text>
                </Pressable>
              </View>
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
  empty: { alignItems: "center", gap: 8, padding: spacing.xxl },
  emptyTitle: { fontSize: 15, fontWeight: "800", color: colors.onSurface, marginTop: spacing.md },
  emptySub: { fontSize: 12, color: colors.muted, textAlign: "center", lineHeight: 17 },
  goBtn: { flexDirection: "row", alignItems: "center", gap: 6, paddingVertical: 10, paddingHorizontal: 16, borderRadius: radius.pill, backgroundColor: colors.brandPrimary, marginTop: spacing.md },
  goTxt: { color: colors.onBrandPrimary, fontWeight: "700", fontSize: 13 },
  card: { borderRadius: radius.lg, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border, overflow: "hidden" },
  img: { width: "100%", height: 140, backgroundColor: colors.surfaceTertiary },
  topRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.sm },
  badge: { backgroundColor: colors.brandTertiary, paddingHorizontal: 10, paddingVertical: 3, borderRadius: radius.pill },
  badgeTxt: { fontSize: 10, fontWeight: "700", color: colors.brand },
  date: { fontSize: 11, color: colors.muted, fontWeight: "600" },
  newsTitle: { fontSize: 15, fontWeight: "800", color: colors.onSurface, lineHeight: 20 },
  newsSummary: { fontSize: 12, color: colors.onSurfaceSecondary, marginTop: 6, lineHeight: 17 },
  metaRow: { flexDirection: "row", alignItems: "center", gap: 4, marginTop: spacing.md },
  meta: { fontSize: 11, color: colors.muted },
  actionRow: { flexDirection: "row", gap: 8, marginTop: spacing.md },
  actionBtn: { flex: 1, flexDirection: "row", gap: 6, alignItems: "center", justifyContent: "center", paddingVertical: 10, borderRadius: radius.md },
  actionTxt: { fontSize: 12, fontWeight: "800", color: "#FFFFFF" },
});
