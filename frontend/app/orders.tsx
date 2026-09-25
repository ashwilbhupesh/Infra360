import React, { useEffect, useState, useCallback } from "react";
import { View, Text, StyleSheet, Pressable, ScrollView, ActivityIndicator } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useFocusEffect, useRouter } from "expo-router";
import { Image } from "expo-image";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius } from "@/src/theme";
import { api } from "@/src/api";
import { useAuth } from "@/src/auth-context";

type Activity = {
  quote_requests: any[];
  agent_enquiries: any[];
  my_listings: any[];
  saved: any[];
  follows: any[];
};

export default function Orders() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { user } = useAuth();
  const [act, setAct] = useState<Activity | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    try {
      const data = await api.get<Activity>(`/user/${user.id}/activity`);
      setAct(data);
    } finally { setLoading(false); }
  }, [user]);

  useFocusEffect(useCallback(() => { load(); }, [load]));

  if (loading || !act) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.surface }}>
        <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
          <Pressable onPress={() => router.back()} hitSlop={12}><Icon name="chevron-back" size={26} color={colors.onSurface} /></Pressable>
          <Text style={styles.title}>Enquiries & orders</Text>
        </View>
        <ActivityIndicator style={{ marginTop: spacing.xxxl }} color={colors.brand} />
      </View>
    );
  }

  const totalEnq = act.agent_enquiries.length + act.quote_requests.length;

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="orders-back-btn" onPress={() => router.back()} hitSlop={12}><Icon name="chevron-back" size={26} color={colors.onSurface} /></Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.title}>Enquiries & orders</Text>
          <Text style={styles.sub}>{totalEnq} enquiries · {act.my_listings.length} listings</Text>
        </View>
      </View>

      <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingBottom: 60, gap: spacing.xl }}>
        {act.agent_enquiries.length > 0 && (
          <View>
            <Text style={styles.section}>Agent enquiries</Text>
            {act.agent_enquiries.map(e => (
              <Pressable
                key={e.id}
                testID={`enq-${e.id}`}
                onPress={() => e.agent_id && router.push(`/agent/${e.agent_id}` as any)}
                style={styles.row}
              >
                {e.agent?.image ? <Image source={{ uri: e.agent.image }} style={styles.avatar} /> : <View style={styles.avatarPlaceholder}><Icon name="person-outline" size={18} color={colors.brand} /></View>}
                <View style={{ flex: 1 }}>
                  <Text style={styles.rowTitle} numberOfLines={1}>{e.agent?.name || "Agent"}</Text>
                  {e.agent?.firm ? <Text style={styles.rowMeta} numberOfLines={1}>{e.agent.firm}</Text> : null}
                  {e.message ? <Text style={styles.rowMsg} numberOfLines={2}>"{e.message}"</Text> : null}
                </View>
                <View style={styles.statusPill}><Text style={styles.statusText}>{e.status}</Text></View>
              </Pressable>
            ))}
          </View>
        )}

        {act.quote_requests.length > 0 && (
          <View>
            <Text style={styles.section}>Supplier quotes</Text>
            {act.quote_requests.map(q => (
              <Pressable
                key={q.id}
                testID={`quote-${q.id}`}
                onPress={() => q.supplier_id && router.push(`/supplier/${q.supplier_id}` as any)}
                style={styles.row}
              >
                {q.supplier?.image ? <Image source={{ uri: q.supplier.image }} style={styles.avatar} /> : <View style={styles.avatarPlaceholder}><Icon name="storefront-outline" size={18} color={colors.brand} /></View>}
                <View style={{ flex: 1 }}>
                  <Text style={styles.rowTitle} numberOfLines={1}>{q.supplier?.name || "Supplier"}</Text>
                  {q.message ? <Text style={styles.rowMsg} numberOfLines={2}>"{q.message}"</Text> : null}
                </View>
                <View style={styles.statusPill}><Text style={styles.statusText}>{q.status}</Text></View>
              </Pressable>
            ))}
          </View>
        )}

        {totalEnq === 0 && (
          <View style={styles.empty}>
            <Icon name="paper-plane-outline" size={40} color={colors.muted} />
            <Text style={styles.emptyText}>No enquiries yet</Text>
            <Text style={styles.emptyHint}>Contact an agent or supplier — your requests will show up here.</Text>
          </View>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingHorizontal: spacing.lg, paddingBottom: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  title: { fontSize: 20, fontWeight: "800", color: colors.onSurface },
  sub: { fontSize: 11, color: colors.muted, marginTop: 2 },
  section: { fontSize: 12, fontWeight: "800", color: colors.muted, letterSpacing: 0.8, marginBottom: spacing.sm },
  row: { flexDirection: "row", alignItems: "center", gap: spacing.md, padding: spacing.md, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, marginBottom: spacing.sm },
  avatar: { width: 44, height: 44, borderRadius: 22 },
  avatarPlaceholder: { width: 44, height: 44, borderRadius: 22, backgroundColor: colors.surfaceSecondary, alignItems: "center", justifyContent: "center" },
  rowTitle: { fontSize: 14, fontWeight: "700", color: colors.onSurface },
  rowMeta: { fontSize: 11, color: colors.muted, marginTop: 2 },
  rowMsg: { fontSize: 11, color: colors.onSurfaceSecondary, marginTop: 4, fontStyle: "italic" },
  statusPill: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: radius.pill, backgroundColor: "rgba(46, 109, 77, 0.12)" },
  statusText: { fontSize: 10, fontWeight: "800", color: colors.success, letterSpacing: 0.4 },
  empty: { alignItems: "center", marginTop: 90, paddingHorizontal: spacing.xl, gap: spacing.sm },
  emptyText: { color: colors.onSurface, fontSize: 15, fontWeight: "700" },
  emptyHint: { color: colors.muted, fontSize: 12, textAlign: "center", lineHeight: 17 },
});
