import React, { useEffect, useState, useCallback } from "react";
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, Pressable } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useFocusEffect, useRouter } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";
import { useAuth } from "@/src/auth-context";
import { PropertyCard, Property } from "@/src/components/property-card";
import { LocalityCard, Locality } from "@/src/components/locality-card";

export default function Saved() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { user, setUser } = useAuth();
  const [saved, setSaved] = useState<Property[]>([]);
  const [follows, setFollows] = useState<Locality[]>([]);
  const [tab, setTab] = useState<"props" | "locs">("props");
  const [loading, setLoading] = useState(true);
  const [compareMode, setCompareMode] = useState(false);
  const [selected, setSelected] = useState<string[]>([]);

  const toggleSelect = (pid: string) => {
    setSelected(prev => {
      if (prev.includes(pid)) return prev.filter(x => x !== pid);
      if (prev.length >= 4) return prev;
      return [...prev, pid];
    });
  };

  const load = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    try {
      const [s, f] = await Promise.all([
        api.get<Property[]>(`/saved?user_id=${user.id}`),
        api.get<Locality[]>(`/follows?user_id=${user.id}`),
      ]);
      setSaved(s); setFollows(f);
    } finally { setLoading(false); }
  }, [user]);

  useFocusEffect(useCallback(() => { load(); }, [load]));

  const startCompare = () => {
    if (selected.length < 2) return;
    router.push(`/compare?ids=${selected.join(",")}` as any);
    setCompareMode(false);
    setSelected([]);
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <View style={{ paddingTop: insets.top + spacing.md, paddingHorizontal: spacing.xl, paddingBottom: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border }}>
        <View style={styles.headerRow}>
          <View style={{ flexDirection: "row", alignItems: "center", gap: spacing.sm, flex: 1 }}>
            <View>
              <Text style={styles.title}>Saved</Text>
              <Text style={styles.sub}>Your properties & followed localities</Text>
            </View>
          </View>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
            {tab === "props" && saved.length >= 2 && (
              <Pressable
                testID="compare-mode-toggle"
                onPress={() => { setCompareMode(v => !v); setSelected([]); }}
                style={[styles.compareToggle, compareMode && styles.compareToggleActive]}
              >
                <Icon name="git-compare-outline" size={14} color={compareMode ? colors.onBrandPrimary : colors.onSurface} />
                <Text style={[styles.compareToggleText, compareMode && { color: colors.onBrandPrimary }]}>
                  {compareMode ? "Cancel" : "Compare"}
                </Text>
              </Pressable>
            )}
            <Pressable
              testID="saved-menu-btn"
              onPress={() => router.push("/profile" as any)}
              style={styles.menuBtn}
              hitSlop={10}
            >
              <Icon name="menu-outline" size={22} color={colors.onSurface} />
            </Pressable>
          </View>
        </View>
        <View style={styles.tabs}>
          <Pressable testID="saved-tab-properties" onPress={() => setTab("props")} style={[styles.tab, tab === "props" && styles.tabActive]}>
            <Text style={[styles.tabText, tab === "props" && styles.tabTextActive]}>Properties · {saved.length}</Text>
          </Pressable>
          <Pressable testID="saved-tab-localities" onPress={() => setTab("locs")} style={[styles.tab, tab === "locs" && styles.tabActive]}>
            <Text style={[styles.tabText, tab === "locs" && styles.tabTextActive]}>Localities · {follows.length}</Text>
          </Pressable>
        </View>
        {compareMode && (
          <View style={styles.compareHint}>
            <Text style={styles.compareHintText}>Select 2–4 properties to compare · {selected.length} chosen</Text>
          </View>
        )}
      </View>

      <ScrollView contentContainerStyle={{ padding: spacing.xl, paddingBottom: compareMode ? 120 : spacing.xxxl }}>
        {loading ? <ActivityIndicator color={colors.brand} style={{ marginTop: spacing.xxl }} /> :
          tab === "props" ? (
            saved.length === 0 ? <Empty text="No saved properties yet. Tap the heart on any property to save." /> :
              saved.map(p => (
                <View key={p.id} style={{ position: "relative" }}>
                  {compareMode && (
                    <Pressable
                      testID={`compare-select-${p.id}`}
                      onPress={() => toggleSelect(p.id)}
                      style={styles.checkOverlay}
                    >
                      <View style={[styles.checkBox, selected.includes(p.id) && styles.checkBoxActive]}>
                        {selected.includes(p.id) && <Icon name="checkmark" size={16} color={colors.onBrandPrimary} />}
                      </View>
                    </Pressable>
                  )}
                  <View pointerEvents={compareMode ? "none" : "auto"}>
                    <PropertyCard property={p} />
                  </View>
                </View>
              ))
          ) : (
            follows.length === 0 ? <Empty text="Follow localities to get updates and news." /> :
              follows.map(l => <LocalityCard key={l.id} locality={l} wide />)
          )
        }

        {!compareMode && (
          <Pressable testID="logout-btn" onPress={() => { setUser(null); router.replace("/onboarding"); }} style={styles.logout}>
            <Icon name="log-out-outline" size={16} color={colors.muted} />
            <Text style={styles.logoutText}>Sign out</Text>
          </Pressable>
        )}
      </ScrollView>

      {compareMode && (
        <View style={[styles.compareBar, { paddingBottom: insets.bottom + spacing.sm }]}>
          <Pressable
            testID="run-compare-btn"
            onPress={startCompare}
            disabled={selected.length < 2}
            style={[styles.compareBtn, { opacity: selected.length < 2 ? 0.5 : 1 }]}
          >
            <Icon name="git-compare-outline" size={18} color={colors.onBrandPrimary} />
            <Text style={styles.compareBtnText}>Compare {selected.length} propert{selected.length === 1 ? "y" : "ies"}</Text>
          </Pressable>
        </View>
      )}
    </View>
  );
}

function Empty({ text }: { text: string }) {
  return (
    <View style={{ padding: spacing.xxxl, alignItems: "center" }}>
      <Icon name="heart-outline" size={40} color={colors.muted} />
      <Text style={{ color: colors.muted, marginTop: spacing.md, textAlign: "center", fontSize: 14 }}>{text}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  headerRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", gap: spacing.md },
  title: { fontSize: 24, fontWeight: "700", color: colors.brand, letterSpacing: -0.3 },
  sub: { color: colors.muted, marginTop: 2, fontSize: 13 },
  compareToggle: { flexDirection: "row", alignItems: "center", gap: 4, paddingHorizontal: 12, height: 34, borderRadius: radius.pill, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface },
  compareToggleActive: { backgroundColor: colors.brandPrimary, borderColor: colors.brandPrimary },
  compareToggleText: { fontSize: 12, fontWeight: "700", color: colors.onSurface },
  menuBtn: {
    width: 40, height: 40, borderRadius: 20,
    backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border,
    alignItems: "center", justifyContent: "center",
  },
  compareHint: { marginTop: spacing.md, padding: spacing.sm, borderRadius: radius.md, backgroundColor: colors.surfaceSecondary },
  compareHintText: { fontSize: 12, color: colors.onSurface, fontWeight: "600", textAlign: "center" },
  tabs: { flexDirection: "row", gap: spacing.sm, marginTop: spacing.md },
  tab: { paddingHorizontal: spacing.md, paddingVertical: spacing.sm, borderRadius: radius.pill, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border },
  tabActive: { backgroundColor: colors.brand, borderColor: colors.brand },
  tabText: { fontSize: 12, fontWeight: "600", color: colors.onSurface },
  tabTextActive: { color: colors.onBrand },
  logout: { flexDirection: "row", alignItems: "center", gap: spacing.sm, alignSelf: "center", marginTop: spacing.xxl, padding: spacing.md },
  logoutText: { color: colors.muted, fontSize: 13, fontWeight: "600" },
  checkOverlay: { position: "absolute", top: spacing.md, right: spacing.md, zIndex: 5 },
  checkBox: { width: 28, height: 28, borderRadius: 14, borderWidth: 2, borderColor: colors.border, backgroundColor: colors.surface, alignItems: "center", justifyContent: "center" },
  checkBoxActive: { backgroundColor: colors.brandPrimary, borderColor: colors.brandPrimary },
  compareBar: { position: "absolute", left: 0, right: 0, bottom: 0, paddingHorizontal: spacing.xl, paddingTop: spacing.md, backgroundColor: colors.surface, borderTopWidth: 1, borderTopColor: colors.border },
  compareBtn: { flexDirection: "row", gap: 8, justifyContent: "center", alignItems: "center", height: 52, borderRadius: radius.md, backgroundColor: colors.brandPrimary, ...shadow.card },
  compareBtnText: { color: colors.onBrandPrimary, fontWeight: "700", fontSize: 15 },
});
