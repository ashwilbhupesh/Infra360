import React, { useEffect, useState, useCallback } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, ActivityIndicator } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter, useFocusEffect } from "expo-router";
import { Image } from "expo-image";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api, clearUser } from "@/src/api";
import { useAuth } from "@/src/auth-context";

type Activity = {
  quote_requests: any[];
  agent_enquiries: any[];
  my_listings: any[];
  saved: any[];
  follows: any[];
};

export default function Profile() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { user, setUser } = useAuth();
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

  const signOut = async () => {
    await clearUser();
    await setUser(null);
    router.replace("/onboarding");
  };

  const initials = (user?.name || "?").split(/\s+/).map(s => s[0]).slice(0, 2).join("").toUpperCase();
  const enqCount = (act?.agent_enquiries?.length ?? 0) + (act?.quote_requests?.length ?? 0);
  const savedCount = act?.saved?.length ?? 0;
  const followCount = act?.follows?.length ?? 0;
  const listingCount = act?.my_listings?.length ?? 0;

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="profile-back-btn" onPress={() => router.back()} hitSlop={12}>
          <Icon name="chevron-back" size={26} color={colors.onSurface} />
        </Pressable>
        <Text style={styles.title}>Profile</Text>
        <View style={{ width: 26 }} />
      </View>

      <ScrollView contentContainerStyle={{ paddingBottom: 60 }}>
        <View style={styles.userCard}>
          <View style={styles.avatar}><Text style={styles.avatarText}>{initials}</Text></View>
          <View style={{ flex: 1 }}>
            <Text style={styles.name}>{user?.name || "Guest"}</Text>
            {user?.mobile ? <Text style={styles.meta}>+91 {user.mobile}</Text> : null}
            <View style={{ flexDirection: "row", gap: 6, marginTop: 6, flexWrap: "wrap" }}>
              {user?.profession ? <View style={styles.pill}><Text style={styles.pillText}>{user.profession}</Text></View> : null}
              {user?.area ? <View style={styles.pill}><Icon name="location-outline" size={10} color={colors.brand} /><Text style={styles.pillText}> {user.area}</Text></View> : null}
            </View>
          </View>
        </View>

        {loading ? <ActivityIndicator style={{ marginTop: spacing.lg }} color={colors.brand} /> : (
          <View style={styles.statsRow}>
            <Stat label="Saved" value={savedCount} icon="heart-outline" onPress={() => router.push("/(tabs)/saved" as any)} testID="stat-saved" />
            <Stat label="Following" value={followCount} icon="star-outline" onPress={() => router.push("/(tabs)/saved" as any)} testID="stat-following" />
            <Stat label="Enquiries" value={enqCount} icon="chatbubbles-outline" onPress={() => router.push("/orders")} testID="stat-enquiries" />
            <Stat label="Listings" value={listingCount} icon="pricetag-outline" onPress={() => router.push("/list-property")} testID="stat-listings" />
          </View>
        )}

        <SectionTitle>Account</SectionTitle>
        <MenuRow icon="location-outline" title="My addresses" subtitle="Save multiple home / work addresses" onPress={() => router.push("/addresses" as any)} testID="menu-addresses" />
        <MenuRow icon="time-outline" title="History" subtitle="Recently viewed properties" onPress={() => router.push("/history")} testID="menu-history" />
        <MenuRow icon="bookmark-outline" title="Offline reads" subtitle="News articles you saved" onPress={() => router.push("/offline-news" as any)} testID="menu-offline-news" />
        <MenuRow icon="receipt-outline" title="Enquiries & orders" subtitle="Your agent & supplier requests" onPress={() => router.push("/orders")} testID="menu-orders" />
        <MenuRow icon="gift-outline" title="Important dates" subtitle="Birthdate, spouse birthdate, anniversary" onPress={() => router.push("/personal-dates" as any)} testID="menu-personal-dates" />
        <MenuRow icon="card-outline" title="Subscriptions" subtitle="Free · Pro · Agent tiers" onPress={() => router.push("/subscriptions")} testID="menu-subscriptions" />

        <SectionTitle>Business</SectionTitle>
        <MenuRow icon="briefcase-outline" title="Work with us / Become an agent" subtitle="Broker, developer, lawyer, loan advisor..." onPress={() => router.push("/become-agent")} testID="menu-become-agent" />
        <MenuRow icon="add-circle-outline" title="List with us" subtitle="Post your property in 7 quick steps" onPress={() => router.push("/list-property")} testID="menu-list-with-us" />

        <SectionTitle>Help</SectionTitle>
        <MenuRow icon="help-circle-outline" title="Contact us / Help" subtitle="WhatsApp, call or email" onPress={() => router.push("/contact-us")} testID="menu-contact" />
        <MenuRow icon="shield-checkmark-outline" title="News admin" subtitle="Review reader submissions" onPress={() => router.push("/admin-news" as any)} testID="menu-admin-news" />
        <MenuRow icon="file-tray-full-outline" title="Verification admin" subtitle="Approve listing document proofs" onPress={() => router.push("/admin-verification" as any)} testID="menu-admin-verification" />
        <MenuRow icon="information-circle-outline" title="About InfraJagat" subtitle="Know Before You Buy." onPress={() => {}} testID="menu-about" />

        <Pressable testID="signout-btn" onPress={signOut} style={styles.signOut}>
          <Icon name="log-out-outline" size={16} color={colors.error} />
          <Text style={styles.outText}>Sign out</Text>
        </Pressable>
        <Text style={styles.footer}>InfraJagat · Know Before You Buy.</Text>
      </ScrollView>
    </View>
  );
}

function Stat({ label, value, icon, onPress, testID }: { label: string; value: number; icon: string; onPress: () => void; testID?: string }) {
  return (
    <Pressable testID={testID} onPress={onPress} style={styles.statCard}>
      <Icon name={icon as any} size={18} color={colors.brand} />
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </Pressable>
  );
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return <Text style={styles.sectionTitle}>{children}</Text>;
}

function MenuRow({ icon, title, subtitle, onPress, testID }: { icon: string; title: string; subtitle?: string; onPress: () => void; testID?: string }) {
  return (
    <Pressable testID={testID} onPress={onPress} style={styles.menuRow}>
      <View style={styles.menuIcon}><Icon name={icon as any} size={20} color={colors.brand} /></View>
      <View style={{ flex: 1 }}>
        <Text style={styles.menuTitle}>{title}</Text>
        {subtitle ? <Text style={styles.menuSub}>{subtitle}</Text> : null}
      </View>
      <Icon name="chevron-forward" size={18} color={colors.muted} />
    </Pressable>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", gap: spacing.md, paddingHorizontal: spacing.lg, paddingBottom: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  title: { fontSize: 18, fontWeight: "800", color: colors.onSurface },
  userCard: { flexDirection: "row", alignItems: "center", gap: spacing.md, padding: spacing.lg, backgroundColor: colors.surfaceSecondary, marginHorizontal: spacing.lg, marginTop: spacing.md, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border },
  avatar: { width: 56, height: 56, borderRadius: 28, backgroundColor: colors.brandPrimary, alignItems: "center", justifyContent: "center" },
  avatarText: { color: colors.onBrandPrimary, fontSize: 20, fontWeight: "800" },
  name: { fontSize: 18, fontWeight: "800", color: colors.onSurface },
  meta: { fontSize: 12, color: colors.muted, marginTop: 2 },
  pill: { flexDirection: "row", alignItems: "center", paddingHorizontal: 8, paddingVertical: 3, borderRadius: radius.pill, backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border },
  pillText: { fontSize: 10, fontWeight: "700", color: colors.brand, letterSpacing: 0.3 },
  statsRow: { flexDirection: "row", gap: 8, paddingHorizontal: spacing.lg, marginTop: spacing.md },
  statCard: { flex: 1, gap: 4, paddingVertical: spacing.md, paddingHorizontal: 4, borderRadius: radius.md, backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, alignItems: "center" },
  statValue: { fontSize: 18, fontWeight: "800", color: colors.onSurface },
  statLabel: { fontSize: 10, color: colors.muted, fontWeight: "700", letterSpacing: 0.3, textTransform: "uppercase" },
  sectionTitle: { fontSize: 11, fontWeight: "800", color: colors.muted, letterSpacing: 0.8, textTransform: "uppercase", paddingHorizontal: spacing.lg, marginTop: spacing.xl, marginBottom: spacing.sm },
  menuRow: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingHorizontal: spacing.lg, paddingVertical: spacing.md, backgroundColor: colors.surface, borderTopWidth: 1, borderTopColor: colors.border },
  menuIcon: { width: 36, height: 36, borderRadius: 18, backgroundColor: colors.surfaceSecondary, alignItems: "center", justifyContent: "center" },
  menuTitle: { fontSize: 14, fontWeight: "700", color: colors.onSurface },
  menuSub: { fontSize: 11, color: colors.muted, marginTop: 2 },
  signOut: { flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 8, padding: spacing.md, marginTop: spacing.xxl, marginHorizontal: spacing.lg, borderRadius: radius.md, borderWidth: 1, borderColor: colors.error },
  outText: { color: colors.error, fontWeight: "700" },
  footer: { textAlign: "center", color: colors.muted, fontSize: 10, marginTop: spacing.xl },
});
