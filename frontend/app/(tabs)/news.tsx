import React, { useEffect, useMemo, useState, useCallback } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, ActivityIndicator, RefreshControl, TextInput, Modal, Alert } from "react-native";
import { Image } from "expo-image";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useFocusEffect, useRouter } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius } from "@/src/theme";
import { api } from "@/src/api";
import { getOfflineNews, saveOffline, removeOffline, shareNewsNative, shareOnWhatsApp, shareOnInstagram } from "@/src/utils/news-share";
import { HeaderLocationPill } from "@/src/components/header-location-pill";

const CATS = ["All", "Infrastructure", "Government", "Development", "Residential", "Industrial", "Commercial"];

type NewsItem = {
  id: string; title: string; summary: string; category: string;
  locality_id?: string; locality_name?: string; date: string;
  source: string; image?: string | null; status?: string;
};
type Locality = { id: string; name: string; city: string };

export default function News() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [items, setItems] = useState<NewsItem[]>([]);
  const [localities, setLocalities] = useState<Locality[]>([]);
  const [cat, setCat] = useState("All");
  const [locId, setLocId] = useState<string>("");
  const [q, setQ] = useState("");
  const [debouncedQ, setDebouncedQ] = useState("");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [savedIds, setSavedIds] = useState<Set<string>>(new Set());
  const [shareFor, setShareFor] = useState<NewsItem | null>(null);

  const refreshSaved = useCallback(async () => {
    const list = await getOfflineNews();
    setSavedIds(new Set(list.map(n => n.id)));
  }, []);
  useEffect(() => { refreshSaved(); }, [refreshSaved]);
  useFocusEffect(useCallback(() => { refreshSaved(); }, [refreshSaved]));

  const toggleSave = async (n: NewsItem) => {
    if (savedIds.has(n.id)) {
      await removeOffline(n.id);
    } else {
      await saveOffline({
        id: n.id, title: n.title, summary: n.summary, category: n.category,
        source: n.source, date: n.date, image: n.image, locality_name: n.locality_name,
      });
    }
    refreshSaved();
  };

  const openShare = (n: NewsItem) => setShareFor(n);
  const closeShare = () => setShareFor(null);
  const doShare = async (channel: "whatsapp" | "instagram" | "more") => {
    if (!shareFor) return;
    const input = { title: shareFor.title, summary: shareFor.summary, source: shareFor.source, locality_name: shareFor.locality_name };
    try {
      if (channel === "whatsapp") await shareOnWhatsApp(input);
      else if (channel === "instagram") await shareOnInstagram(input);
      else await shareNewsNative(input);
    } catch (e: any) {
      Alert.alert("Share failed", e?.message || "Try again");
    } finally { closeShare(); }
  };

  // Debounce the search input
  useEffect(() => {
    const t = setTimeout(() => setDebouncedQ(q.trim()), 350);
    return () => clearTimeout(t);
  }, [q]);

  const load = async () => {
    try {
      const qs = new URLSearchParams();
      if (cat !== "All") qs.set("category", cat);
      if (locId) qs.set("locality_id", locId);
      if (debouncedQ) qs.set("q", debouncedQ);
      const data = await api.get<NewsItem[]>(`/news${qs.toString() ? `?${qs}` : ""}`);
      setItems(data);
    } finally { setLoading(false); setRefreshing(false); }
  };
  useEffect(() => { setLoading(true); load(); }, [cat, locId, debouncedQ]);

  useEffect(() => {
    (async () => {
      try {
        const locs = await api.get<Locality[]>("/localities");
        setLocalities(locs);
      } catch {}
    })();
  }, []);

  const selectedArea = useMemo(
    () => locId ? (localities.find(l => l.id === locId)?.name || "Area") : "All of Jaipur",
    [locId, localities]
  );

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <View style={{ paddingTop: insets.top + spacing.md, paddingHorizontal: spacing.xl, paddingBottom: spacing.sm, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border }}>
        <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between", gap: spacing.sm, marginBottom: spacing.sm }}>
          <HeaderLocationPill testID="news-location-pill" compact />
          <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
            <Pressable
              testID="news-publish-btn"
              onPress={() => router.push("/publish-news" as any)}
              style={styles.publishBtn}
              hitSlop={8}
            >
              <Icon name="add" size={14} color={colors.onBrandPrimary} />
              <Text style={styles.publishText}>Publish</Text>
            </Pressable>
            <Pressable
              testID="news-menu-btn"
              onPress={() => router.push("/profile" as any)}
              style={styles.menuBtn}
              hitSlop={10}
            >
              <Icon name="settings-outline" size={20} color={colors.onSurface} />
            </Pressable>
          </View>
        </View>
        <View style={{ flexDirection: "row", alignItems: "flex-start", justifyContent: "space-between" }}>
          <View style={{ flex: 1 }}>
            <Text style={styles.title}>InfraJagat News</Text>
            <View style={{ flexDirection: "row", alignItems: "center", gap: 4, marginTop: 2 }}>
              <Icon name="location-outline" size={13} color={colors.muted} />
              <Text style={styles.sub} numberOfLines={1}>{selectedArea}</Text>
            </View>
          </View>
        </View>

        <View style={styles.searchWrap}>
          <Icon name="search" size={16} color={colors.muted} />
          <TextInput
            testID="news-search"
            value={q}
            onChangeText={setQ}
            placeholder="Search news — metro, DLC, Vaishali Nagar..."
            placeholderTextColor={colors.muted}
            style={styles.searchInput}
            returnKeyType="search"
          />
          {q ? (
            <Pressable onPress={() => setQ("")} hitSlop={10}>
              <Icon name="close-circle" size={16} color={colors.muted} />
            </Pressable>
          ) : null}
        </View>

        <Text style={styles.sectionLabel}>Sub-area</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chipsRow}>
          <Pressable
            testID="news-loc-all"
            onPress={() => setLocId("")}
            style={[styles.chip, locId === "" && styles.chipActive]}
          >
            <Icon name="globe-outline" size={13} color={locId === "" ? colors.onBrand : colors.onSurface} />
            <Text style={[styles.chipText, locId === "" && styles.chipTextActive]}>All areas</Text>
          </Pressable>
          {localities.map(l => (
            <Pressable
              key={l.id}
              testID={`news-loc-${l.id}`}
              onPress={() => setLocId(l.id)}
              style={[styles.chip, locId === l.id && styles.chipActive]}
            >
              <Text style={[styles.chipText, locId === l.id && styles.chipTextActive]}>{l.name}</Text>
            </Pressable>
          ))}
        </ScrollView>

        <Text style={styles.sectionLabel}>Topic</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chipsRow}>
          {CATS.map(c => (
            <Pressable key={c} testID={`news-cat-${c.toLowerCase()}`} onPress={() => setCat(c)} style={[styles.chip, cat === c && styles.chipActive]}>
              <Text style={[styles.chipText, cat === c && styles.chipTextActive]}>{c}</Text>
            </Pressable>
          ))}
        </ScrollView>
      </View>

      <ScrollView contentContainerStyle={{ padding: spacing.xl, paddingBottom: 40 }} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); load(); }} />}>
        {loading ? <ActivityIndicator color={colors.brand} style={{ marginTop: spacing.xxl }} /> :
          items.length === 0 ? (
            <View style={styles.empty}>
              <Icon name="newspaper-outline" size={32} color={colors.muted} />
              <Text style={styles.emptyTitle}>No news for this filter yet</Text>
              <Text style={styles.emptySub}>Try changing area, topic or search.</Text>
            </View>
          ) : (
          items.map(n => (
            <Pressable
              key={n.id}
              testID={`news-card-${n.id}`}
              style={styles.card}
              onPress={() => n.locality_id && router.push(`/locality/${n.locality_id}` as any)}
            >
              {n.image ? (
                <Image source={{ uri: n.image }} style={styles.cardImg} contentFit="cover" transition={200} />
              ) : null}
              <View style={{ padding: spacing.lg }}>
                <View style={styles.cardTop}>
                  <View style={styles.badge}><Text style={styles.badgeText}>{n.category}</Text></View>
                  <Text style={styles.date}>{new Date(n.date).toLocaleDateString("en-IN", { day: "2-digit", month: "short" })}</Text>
                </View>
                <Text style={styles.newsTitle}>{n.title}</Text>
                <Text style={styles.newsSummary}>{n.summary}</Text>
                <View style={styles.metaRow}>
                  <Icon name="newspaper-outline" size={12} color={colors.muted} />
                  <Text style={styles.source}>{n.source}</Text>
                  {n.locality_name ? (
                    <>
                      <Text style={styles.dot}>·</Text>
                      <Icon name="location-outline" size={11} color={colors.muted} />
                      <Text style={styles.source}>{n.locality_name}</Text>
                    </>
                  ) : null}
                </View>
                <View style={styles.actionsRow}>
                  <Pressable
                    testID={`news-share-${n.id}`}
                    onPress={() => openShare(n)}
                    style={styles.actionChip}
                    hitSlop={8}
                  >
                    <Icon name="share-social-outline" size={14} color={colors.brand} />
                    <Text style={styles.actionTxt}>Share</Text>
                  </Pressable>
                  <Pressable
                    testID={`news-save-${n.id}`}
                    onPress={() => toggleSave(n)}
                    style={[styles.actionChip, savedIds.has(n.id) && styles.actionChipActive]}
                    hitSlop={8}
                  >
                    <Icon
                      name={savedIds.has(n.id) ? "bookmark" : "bookmark-outline"}
                      size={14}
                      color={savedIds.has(n.id) ? colors.onBrandPrimary : colors.brand}
                    />
                    <Text style={[styles.actionTxt, savedIds.has(n.id) && { color: colors.onBrandPrimary }]}>
                      {savedIds.has(n.id) ? "Saved offline" : "Save offline"}
                    </Text>
                  </Pressable>
                </View>
              </View>
            </Pressable>
          )))
        }
      </ScrollView>

      <Modal visible={!!shareFor} transparent animationType="fade" onRequestClose={closeShare}>
        <Pressable style={styles.shareBackdrop} onPress={closeShare}>
          <Pressable style={styles.shareSheet} onPress={() => {}}>
            <View style={styles.shareHandle} />
            <Text style={styles.shareTitle} numberOfLines={2}>{shareFor?.title}</Text>
            <Text style={styles.shareSub}>Share this story with your network</Text>
            <View style={styles.shareRow}>
              <Pressable testID="share-whatsapp" onPress={() => doShare("whatsapp")} style={[styles.shareBtn, { backgroundColor: "#25D366" }]}>
                <Icon name="logo-whatsapp" size={22} color="#FFFFFF" />
                <Text style={styles.shareBtnTxt}>WhatsApp</Text>
              </Pressable>
              <Pressable testID="share-instagram" onPress={() => doShare("instagram")} style={[styles.shareBtn, { backgroundColor: "#E1306C" }]}>
                <Icon name="logo-instagram" size={22} color="#FFFFFF" />
                <Text style={styles.shareBtnTxt}>Instagram</Text>
              </Pressable>
              <Pressable testID="share-more" onPress={() => doShare("more")} style={[styles.shareBtn, { backgroundColor: colors.brand }]}>
                <Icon name="ellipsis-horizontal" size={22} color={colors.onBrand} />
                <Text style={styles.shareBtnTxt}>More</Text>
              </Pressable>
            </View>
            <Pressable testID="share-cancel" onPress={closeShare} style={styles.shareCancel}>
              <Text style={styles.shareCancelTxt}>Cancel</Text>
            </Pressable>
          </Pressable>
        </Pressable>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  title: { fontSize: 24, fontWeight: "800", color: colors.brand, letterSpacing: -0.3 },
  sub: { color: colors.muted, fontSize: 13 },
  menuBtn: {
    width: 36, height: 36, borderRadius: 18,
    backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border,
    alignItems: "center", justifyContent: "center",
  },
  publishBtn: {
    flexDirection: "row", alignItems: "center", gap: 4,
    paddingHorizontal: 12, height: 36, borderRadius: radius.pill,
    backgroundColor: colors.brandPrimary,
  },
  publishText: { color: colors.onBrandPrimary, fontSize: 12, fontWeight: "800" },
  searchWrap: {
    flexDirection: "row", alignItems: "center", gap: 8,
    backgroundColor: colors.surfaceSecondary, borderRadius: radius.pill,
    paddingHorizontal: 14, height: 42, marginTop: spacing.md,
    borderWidth: 1, borderColor: colors.border,
  },
  searchInput: { flex: 1, fontSize: 13, color: colors.onSurface, padding: 0 },
  sectionLabel: { fontSize: 10, fontWeight: "800", color: colors.muted, letterSpacing: 0.8, marginTop: spacing.md },
  chipsRow: { paddingTop: 6, gap: spacing.sm, paddingBottom: 2 },
  chip: { flexDirection: "row", alignItems: "center", gap: 4, paddingHorizontal: spacing.md, height: 34, borderRadius: radius.pill, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border, flexShrink: 0 },
  chipActive: { backgroundColor: colors.brand, borderColor: colors.brand },
  chipText: { color: colors.onSurface, fontSize: 12, fontWeight: "600" },
  chipTextActive: { color: colors.onBrand },

  card: { borderRadius: radius.lg, backgroundColor: colors.surfaceSecondary, marginBottom: spacing.md, borderWidth: 1, borderColor: colors.border, overflow: "hidden" },
  cardImg: { width: "100%", height: 160, backgroundColor: colors.surfaceSecondary },
  cardTop: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.sm },
  badge: { backgroundColor: colors.brandTertiary, paddingHorizontal: spacing.md, paddingVertical: 3, borderRadius: radius.pill },
  badgeText: { fontSize: 10, fontWeight: "700", color: colors.brand, letterSpacing: 0.3 },
  date: { fontSize: 11, color: colors.muted, fontWeight: "600" },
  newsTitle: { fontSize: 15, fontWeight: "700", color: colors.onSurface, letterSpacing: -0.2, lineHeight: 21 },
  newsSummary: { fontSize: 13, color: colors.onSurfaceSecondary, marginTop: spacing.sm, lineHeight: 19 },
  metaRow: { flexDirection: "row", alignItems: "center", gap: 4, marginTop: spacing.md, flexWrap: "wrap" },
  source: { fontSize: 11, color: colors.muted, fontWeight: "500" },
  dot: { fontSize: 11, color: colors.muted, marginHorizontal: 2 },
  empty: { alignItems: "center", paddingVertical: spacing.xxxl, gap: 8 },
  emptyTitle: { fontSize: 14, fontWeight: "700", color: colors.onSurface },
  actionsRow: { flexDirection: "row", gap: 8, marginTop: spacing.md },
  actionChip: { flexDirection: "row", alignItems: "center", gap: 6, paddingHorizontal: 12, height: 32, borderRadius: radius.pill, borderWidth: 1, borderColor: colors.brand, backgroundColor: colors.surface },
  actionChipActive: { backgroundColor: colors.brandPrimary, borderColor: colors.brandPrimary },
  actionTxt: { fontSize: 11, fontWeight: "800", color: colors.brand },
  shareBackdrop: { flex: 1, backgroundColor: "rgba(0,0,0,0.5)", justifyContent: "flex-end" },
  shareSheet: { backgroundColor: colors.surface, borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: spacing.lg, paddingBottom: spacing.xxl, gap: spacing.md },
  shareHandle: { alignSelf: "center", width: 40, height: 4, borderRadius: 2, backgroundColor: colors.borderStrong },
  shareTitle: { fontSize: 15, fontWeight: "800", color: colors.onSurface, lineHeight: 20 },
  shareSub: { fontSize: 12, color: colors.muted },
  shareRow: { flexDirection: "row", gap: 10, marginTop: 6 },
  shareBtn: { flex: 1, alignItems: "center", justifyContent: "center", gap: 6, paddingVertical: 14, borderRadius: radius.md },
  shareBtnTxt: { fontSize: 12, fontWeight: "800", color: "#FFFFFF" },
  shareCancel: { paddingVertical: 12, alignItems: "center", borderRadius: radius.md, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border, marginTop: 4 },
  shareCancelTxt: { fontSize: 13, fontWeight: "700", color: colors.onSurface },
  emptySub: { fontSize: 12, color: colors.muted },
});
