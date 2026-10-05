import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, TextInput, Alert, ActivityIndicator } from "react-native";
import { Image } from "expo-image";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter, Stack } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { colors, spacing, radius } from "@/src/theme";
import { api } from "@/src/api";

type Pending = {
  id: string; title: string; summary: string; category: string;
  locality_id?: string | null; locality_name?: string;
  image?: string | null; source: string; date: string;
};

const TOKEN_KEY = "infrajagat.admin_token";

export default function AdminNewsReview() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [token, setToken] = useState("");
  const [authed, setAuthed] = useState(false);
  const [items, setItems] = useState<Pending[]>([]);
  const [loading, setLoading] = useState(false);
  const [busyId, setBusyId] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      const t = (await AsyncStorage.getItem(TOKEN_KEY)) || "";
      if (t) {
        setToken(t);
        setAuthed(true);
      }
    })();
  }, []);

  const load = async () => {
    setLoading(true);
    try {
      const data = await api.get<Pending[]>(`/news?status=pending`);
      setItems(data);
    } catch (e: any) {
      Alert.alert("Couldn't load", e?.message || "Try again");
    } finally { setLoading(false); }
  };

  useEffect(() => { if (authed) load(); }, [authed]);

  const decide = async (id: string, decision: "approve" | "reject") => {
    setBusyId(id);
    try {
      await api.post(`/news/${id}/review`, { decision, admin_token: token });
      setItems(items => items.filter(i => i.id !== id));
    } catch (e: any) {
      Alert.alert("Failed", e?.message || "Try again");
    } finally { setBusyId(null); }
  };

  if (!authed) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.surfaceSecondary }}>
        <Stack.Screen options={{ headerShown: false }} />
        <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
          <Pressable testID="admin-back" onPress={() => router.back()} hitSlop={12}>
            <Icon name="chevron-back" size={26} color={colors.onSurface} />
          </Pressable>
          <Text style={styles.title}>News admin</Text>
          <View style={{ width: 26 }} />
        </View>
        <View style={{ padding: spacing.xl, gap: 12 }}>
          <Text style={styles.notice}>Enter the admin token to review reader submissions.</Text>
          <TextInput
            testID="admin-token"
            value={token}
            onChangeText={setToken}
            placeholder="Admin token"
            placeholderTextColor={colors.muted}
            secureTextEntry
            style={styles.input}
          />
          <Pressable
            testID="admin-signin"
            onPress={async () => {
              if (!token.trim()) return;
              await AsyncStorage.setItem(TOKEN_KEY, token.trim());
              setAuthed(true);
            }}
            style={styles.submitBtn}
          >
            <Text style={styles.submitText}>Continue</Text>
          </Pressable>
          <Text style={styles.footerHint}>MVP default: `infrajagat-admin`. Set via `ADMIN_TOKEN` in backend/.env for production.</Text>
        </View>
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: colors.surfaceSecondary }}>
      <Stack.Screen options={{ headerShown: false }} />
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="admin-back" onPress={() => router.back()} hitSlop={12}>
          <Icon name="chevron-back" size={26} color={colors.onSurface} />
        </Pressable>
        <View style={{ flex: 1, alignItems: "center" }}>
          <Text style={styles.title}>Pending ({items.length})</Text>
        </View>
        <Pressable
          testID="admin-signout"
          onPress={async () => { await AsyncStorage.removeItem(TOKEN_KEY); setAuthed(false); setToken(""); }}
          hitSlop={10}
        >
          <Text style={{ fontSize: 12, color: colors.error, fontWeight: "700" }}>Sign out</Text>
        </Pressable>
      </View>

      {loading ? (
        <ActivityIndicator color={colors.brand} style={{ marginTop: spacing.xxl }} />
      ) : (
        <ScrollView contentContainerStyle={{ padding: spacing.xl, paddingBottom: 100 }}>
          {items.length === 0 ? (
            <View style={styles.empty}>
              <Icon name="checkmark-done-circle-outline" size={40} color={colors.muted} />
              <Text style={styles.emptyTitle}>Inbox zero</Text>
              <Text style={styles.emptySub}>No pending submissions right now.</Text>
            </View>
          ) : items.map(n => (
            <View key={n.id} style={styles.card} testID={`pending-${n.id}`}>
              {n.image ? <Image source={{ uri: n.image }} style={styles.cardImg} contentFit="cover" /> : null}
              <View style={{ padding: spacing.lg }}>
                <View style={styles.row}>
                  <View style={styles.badge}><Text style={styles.badgeText}>{n.category}</Text></View>
                  {n.locality_name ? <Text style={styles.meta}>{n.locality_name}</Text> : null}
                </View>
                <Text style={styles.cardTitle}>{n.title}</Text>
                <Text style={styles.cardSummary}>{n.summary}</Text>
                <View style={styles.actions}>
                  <Pressable
                    testID={`approve-${n.id}`}
                    onPress={() => decide(n.id, "approve")}
                    disabled={busyId === n.id}
                    style={[styles.btn, { backgroundColor: colors.success }]}
                  >
                    <Icon name="checkmark" size={14} color={colors.onSuccess} />
                    <Text style={[styles.btnText, { color: colors.onSuccess }]}>Approve</Text>
                  </Pressable>
                  <Pressable
                    testID={`reject-${n.id}`}
                    onPress={() => decide(n.id, "reject")}
                    disabled={busyId === n.id}
                    style={[styles.btn, { backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.error }]}
                  >
                    <Icon name="close" size={14} color={colors.error} />
                    <Text style={[styles.btnText, { color: colors.error }]}>Reject</Text>
                  </Pressable>
                </View>
              </View>
            </View>
          ))}
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", paddingHorizontal: spacing.xl, paddingBottom: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border, gap: spacing.sm },
  title: { fontSize: 17, fontWeight: "800", color: colors.onSurface },
  notice: { fontSize: 13, color: colors.onSurfaceSecondary, lineHeight: 18 },
  input: { backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, paddingHorizontal: 14, paddingVertical: 12, fontSize: 14, color: colors.onSurface },
  submitBtn: { backgroundColor: colors.brandPrimary, paddingVertical: 14, borderRadius: radius.pill, alignItems: "center" },
  submitText: { color: colors.onBrandPrimary, fontSize: 14, fontWeight: "800" },
  footerHint: { fontSize: 11, color: colors.muted, textAlign: "center", marginTop: 4 },
  card: { backgroundColor: colors.surface, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, marginBottom: spacing.md, overflow: "hidden" },
  cardImg: { width: "100%", height: 150, backgroundColor: colors.surfaceSecondary },
  row: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: 6 },
  badge: { backgroundColor: colors.brandTertiary, paddingHorizontal: 10, paddingVertical: 3, borderRadius: radius.pill },
  badgeText: { fontSize: 10, fontWeight: "700", color: colors.brand, letterSpacing: 0.3 },
  meta: { fontSize: 11, color: colors.muted, fontWeight: "600" },
  cardTitle: { fontSize: 15, fontWeight: "800", color: colors.onSurface, lineHeight: 21 },
  cardSummary: { fontSize: 13, color: colors.onSurfaceSecondary, marginTop: 6, lineHeight: 19 },
  actions: { flexDirection: "row", gap: spacing.sm, marginTop: spacing.md },
  btn: { flex: 1, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 6, paddingVertical: 12, borderRadius: radius.pill },
  btnText: { fontSize: 13, fontWeight: "800" },
  empty: { alignItems: "center", padding: spacing.xxxl, gap: 8, marginTop: spacing.xxl },
  emptyTitle: { fontSize: 15, fontWeight: "800", color: colors.onSurface },
  emptySub: { fontSize: 12, color: colors.muted },
});
