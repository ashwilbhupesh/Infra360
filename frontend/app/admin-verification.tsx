import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, TextInput, Alert, ActivityIndicator } from "react-native";
import { Image } from "expo-image";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter, Stack } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api, backendUrl as BURL } from "@/src/api";
import { formatINR } from "@/src/utils/format";

type Request = {
  id: string; property_id: string; user_id?: string;
  docs: { type: string; label?: string; url: string }[];
  note?: string | null; status: string; created_at: string;
  property?: { id: string; title: string; address: string; images: string[]; price: number };
};

const TOKEN_KEY = "infrajagat.admin_token";

export default function AdminVerification() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [token, setToken] = useState("");
  const [authed, setAuthed] = useState(false);
  const [items, setItems] = useState<Request[]>([]);
  const [loading, setLoading] = useState(false);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [tab, setTab] = useState<"Pending Review" | "Verified" | "Rejected">("Pending Review");

  useEffect(() => {
    (async () => {
      const t = (await AsyncStorage.getItem(TOKEN_KEY)) || "";
      if (t) { setToken(t); setAuthed(true); }
    })();
  }, []);

  const load = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${BURL}/api/verification-requests?status=${encodeURIComponent(tab)}&admin_token=${encodeURIComponent(token)}`);
      if (!res.ok) throw new Error(`${res.status}`);
      setItems(await res.json());
    } catch (e: any) {
      Alert.alert("Couldn't load", e?.message || "Try again");
    } finally { setLoading(false); }
  };

  useEffect(() => { if (authed) load(); }, [authed, tab]);

  const decide = async (id: string, decision: "approve" | "reject") => {
    setBusyId(id);
    try {
      await api.post(`/verification-requests/${id}/review`, { decision, admin_token: token });
      load();
    } catch (e: any) {
      Alert.alert("Action failed", e?.message || "Try again");
    } finally { setBusyId(null); }
  };

  if (!authed) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.surface }}>
        <Stack.Screen options={{ headerShown: false }} />
        <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
          <Pressable testID="admin-verif-back" onPress={() => router.back()} hitSlop={12}><Icon name="chevron-back" size={26} color={colors.onSurface} /></Pressable>
          <Text style={styles.title}>Verification admin</Text>
        </View>
        <View style={{ padding: spacing.lg, gap: spacing.md }}>
          <Text style={styles.sub}>Enter the shared admin token to review submissions.</Text>
          <TextInput
            testID="admin-verif-token-input"
            value={token}
            onChangeText={setToken}
            placeholder="admin token"
            placeholderTextColor={colors.muted}
            style={styles.input}
            autoCapitalize="none"
            secureTextEntry
          />
          <Pressable
            testID="admin-verif-login-btn"
            onPress={async () => { await AsyncStorage.setItem(TOKEN_KEY, token); setAuthed(true); }}
            style={styles.loginBtn}
          >
            <Text style={styles.loginTxt}>Unlock</Text>
          </Pressable>
        </View>
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <Stack.Screen options={{ headerShown: false }} />
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="admin-verif-back" onPress={() => router.back()} hitSlop={12}><Icon name="chevron-back" size={26} color={colors.onSurface} /></Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.title}>Verification admin</Text>
          <Text style={styles.sub}>{items.length} {tab.toLowerCase()}</Text>
        </View>
        <Pressable testID="admin-verif-refresh" onPress={load} hitSlop={10}>
          <Icon name="refresh-outline" size={20} color={colors.onSurface} />
        </Pressable>
      </View>

      <View style={styles.tabs}>
        {(["Pending Review", "Verified", "Rejected"] as const).map(t => (
          <Pressable key={t} testID={`admin-verif-tab-${t}`} onPress={() => setTab(t)} style={[styles.tab, tab === t && styles.tabActive]}>
            <Text style={[styles.tabTxt, tab === t && styles.tabTxtActive]}>{t.replace(" Review", "")}</Text>
          </Pressable>
        ))}
      </View>

      <ScrollView contentContainerStyle={{ padding: spacing.lg, gap: spacing.md }}>
        {loading ? <ActivityIndicator color={colors.brand} style={{ marginTop: spacing.xxl }} /> :
          items.length === 0 ? <Text style={styles.empty}>Nothing to review here.</Text> :
            items.map(r => (
              <View key={r.id} style={styles.card} testID={`verif-row-${r.id}`}>
                {r.property ? (
                  <Pressable onPress={() => router.push(`/property/${r.property_id}` as any)} style={styles.propRow}>
                    <Image source={{ uri: r.property.images?.[0] }} style={styles.propThumb} contentFit="cover" />
                    <View style={{ flex: 1 }}>
                      <Text style={styles.propTitle} numberOfLines={1}>{r.property.title}</Text>
                      <Text style={styles.propAddr} numberOfLines={1}>{r.property.address}</Text>
                      <Text style={styles.propPrice}>{formatINR(r.property.price)}</Text>
                    </View>
                    <Icon name="chevron-forward" size={16} color={colors.muted} />
                  </Pressable>
                ) : null}

                <Text style={styles.sectionLbl}>Documents ({r.docs.length})</Text>
                <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 8, paddingVertical: 4 }}>
                  {r.docs.map((d, i) => (
                    <View key={i} style={styles.docCard}>
                      <Image source={{ uri: `${BURL}${d.url}` }} style={styles.docImg} contentFit="cover" />
                      <Text style={styles.docLbl}>{d.label || d.type}</Text>
                    </View>
                  ))}
                </ScrollView>
                {r.note ? <Text style={styles.note}>Note: {r.note}</Text> : null}

                {tab === "Pending Review" && (
                  <View style={styles.actions}>
                    <Pressable
                      testID={`reject-${r.id}`}
                      onPress={() => decide(r.id, "reject")}
                      disabled={busyId === r.id}
                      style={[styles.actionBtn, { backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.error }]}
                    >
                      <Icon name="close" size={16} color={colors.error} />
                      <Text style={[styles.actionTxt, { color: colors.error }]}>Reject</Text>
                    </Pressable>
                    <Pressable
                      testID={`approve-${r.id}`}
                      onPress={() => decide(r.id, "approve")}
                      disabled={busyId === r.id}
                      style={[styles.actionBtn, { backgroundColor: colors.success }]}
                    >
                      {busyId === r.id ? <ActivityIndicator color={colors.onSuccess} /> : (<>
                        <Icon name="checkmark" size={16} color={colors.onSuccess} />
                        <Text style={[styles.actionTxt, { color: colors.onSuccess }]}>Approve · Mark verified</Text>
                      </>)}
                    </Pressable>
                  </View>
                )}
                <Text style={styles.ts}>Submitted {new Date(r.created_at).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })}</Text>
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
  input: { borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, padding: spacing.md, color: colors.onSurface, fontSize: 14, backgroundColor: colors.surface },
  loginBtn: { height: 48, borderRadius: radius.md, backgroundColor: colors.brand, alignItems: "center", justifyContent: "center" },
  loginTxt: { color: colors.onBrand, fontWeight: "800" },
  tabs: { flexDirection: "row", gap: 6, padding: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  tab: { flex: 1, paddingVertical: 8, borderRadius: radius.pill, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, alignItems: "center" },
  tabActive: { backgroundColor: colors.brand, borderColor: colors.brand },
  tabTxt: { fontSize: 12, fontWeight: "700", color: colors.onSurface },
  tabTxtActive: { color: colors.onBrand },
  empty: { textAlign: "center", color: colors.muted, marginTop: spacing.xxl },
  card: { padding: spacing.md, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, gap: 10, ...shadow.card },
  propRow: { flexDirection: "row", alignItems: "center", gap: 10, padding: 8, borderRadius: radius.md, backgroundColor: colors.surfaceSecondary },
  propThumb: { width: 56, height: 56, borderRadius: 8, backgroundColor: colors.surfaceTertiary },
  propTitle: { fontSize: 13, fontWeight: "800", color: colors.onSurface },
  propAddr: { fontSize: 11, color: colors.muted, marginTop: 2 },
  propPrice: { fontSize: 13, fontWeight: "700", color: colors.brandPrimary, marginTop: 2 },
  sectionLbl: { fontSize: 11, fontWeight: "800", color: colors.muted, letterSpacing: 0.6, textTransform: "uppercase" },
  docCard: { width: 110, gap: 4 },
  docImg: { width: 110, height: 100, borderRadius: 8, backgroundColor: colors.surfaceSecondary },
  docLbl: { fontSize: 11, fontWeight: "700", color: colors.onSurface },
  note: { fontSize: 12, color: colors.onSurface, fontStyle: "italic" },
  actions: { flexDirection: "row", gap: 8 },
  actionBtn: { flex: 1, flexDirection: "row", gap: 6, alignItems: "center", justifyContent: "center", paddingVertical: 10, borderRadius: radius.md },
  actionTxt: { fontSize: 13, fontWeight: "800" },
  ts: { fontSize: 10, color: colors.muted, textAlign: "right" },
});
