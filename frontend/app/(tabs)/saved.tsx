import React, { useEffect, useState, useCallback } from "react";
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, Pressable } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useFocusEffect, useRouter } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius } from "@/src/theme";
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

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <View style={{ paddingTop: insets.top + spacing.md, paddingHorizontal: spacing.xl, paddingBottom: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border }}>
        <View style={styles.headerRow}>
          <View>
            <Text style={styles.title}>Saved</Text>
            <Text style={styles.sub}>Your properties & followed localities</Text>
          </View>
          <Pressable testID="profile-avatar" onPress={() => router.push("/list-property")} style={styles.avatar}>
            <Text style={styles.avatarText}>{user?.name?.[0]?.toUpperCase() || "?"}</Text>
          </Pressable>
        </View>
        <View style={styles.tabs}>
          <Pressable testID="saved-tab-properties" onPress={() => setTab("props")} style={[styles.tab, tab === "props" && styles.tabActive]}>
            <Text style={[styles.tabText, tab === "props" && styles.tabTextActive]}>Properties · {saved.length}</Text>
          </Pressable>
          <Pressable testID="saved-tab-localities" onPress={() => setTab("locs")} style={[styles.tab, tab === "locs" && styles.tabActive]}>
            <Text style={[styles.tabText, tab === "locs" && styles.tabTextActive]}>Localities · {follows.length}</Text>
          </Pressable>
        </View>
      </View>

      <ScrollView contentContainerStyle={{ padding: spacing.xl, paddingBottom: spacing.xxxl }}>
        {loading ? <ActivityIndicator color={colors.brand} style={{ marginTop: spacing.xxl }} /> :
          tab === "props" ? (
            saved.length === 0 ? <Empty text="No saved properties yet. Tap the heart on any property to save." /> :
              saved.map(p => <PropertyCard key={p.id} property={p} />)
          ) : (
            follows.length === 0 ? <Empty text="Follow localities to get updates and news." /> :
              follows.map(l => <LocalityCard key={l.id} locality={l} wide />)
          )
        }

        <Pressable testID="logout-btn" onPress={() => { setUser(null); router.replace("/onboarding"); }} style={styles.logout}>
          <Icon name="log-out-outline" size={16} color={colors.muted} />
          <Text style={styles.logoutText}>Sign out</Text>
        </Pressable>
      </ScrollView>
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
  headerRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  title: { fontSize: 24, fontWeight: "700", color: colors.brand, letterSpacing: -0.3 },
  sub: { color: colors.muted, marginTop: 2, fontSize: 13 },
  avatar: { width: 40, height: 40, borderRadius: 20, backgroundColor: colors.brand, alignItems: "center", justifyContent: "center" },
  avatarText: { color: colors.onBrand, fontWeight: "700" },
  tabs: { flexDirection: "row", gap: spacing.sm, marginTop: spacing.md },
  tab: { paddingHorizontal: spacing.md, paddingVertical: spacing.sm, borderRadius: radius.pill, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border },
  tabActive: { backgroundColor: colors.brand, borderColor: colors.brand },
  tabText: { fontSize: 12, fontWeight: "600", color: colors.onSurface },
  tabTextActive: { color: colors.onBrand },
  logout: { flexDirection: "row", alignItems: "center", gap: spacing.sm, alignSelf: "center", marginTop: spacing.xxl, padding: spacing.md },
  logoutText: { color: colors.muted, fontSize: 13, fontWeight: "600" },
});
