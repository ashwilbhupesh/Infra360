import React from "react";
import { View, Text, StyleSheet, Pressable, ScrollView } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { openWhatsApp, openTel } from "@/src/utils/contact";
import { Linking } from "react-native";

const SUPPORT_WA = "+91 90000 00000";
const SUPPORT_PHONE = "+91 90000 00000";
const SUPPORT_EMAIL = "help@infralocal.in";

export default function ContactUs() {
  const insets = useSafeAreaInsets();
  const router = useRouter();

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="contact-back" onPress={() => router.back()} hitSlop={12}><Icon name="chevron-back" size={26} color={colors.onSurface} /></Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.title}>Contact us</Text>
          <Text style={styles.sub}>We reply within 24 hours, usually within 2</Text>
        </View>
      </View>

      <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingBottom: 60, gap: spacing.md }}>
        <Pressable
          testID="contact-whatsapp"
          onPress={() => openWhatsApp(SUPPORT_WA, "Hi InfraLocal team, I need help with...")}
          style={[styles.row, { backgroundColor: "#25D366" }]}
        >
          <Icon name="logo-whatsapp" size={24} color="#FFFFFF" />
          <View style={{ flex: 1 }}>
            <Text style={[styles.rowTitle, { color: "#FFFFFF" }]}>Chat on WhatsApp</Text>
            <Text style={[styles.rowSub, { color: "rgba(255,255,255,0.9)" }]}>{SUPPORT_WA}</Text>
          </View>
          <Icon name="chevron-forward" size={18} color="#FFFFFF" />
        </Pressable>

        <Pressable testID="contact-call" onPress={() => openTel(SUPPORT_PHONE)} style={styles.row}>
          <Icon name="call-outline" size={22} color={colors.brand} />
          <View style={{ flex: 1 }}>
            <Text style={styles.rowTitle}>Call helpdesk</Text>
            <Text style={styles.rowSub}>Mon–Sat, 10 AM to 8 PM · {SUPPORT_PHONE}</Text>
          </View>
          <Icon name="chevron-forward" size={18} color={colors.muted} />
        </Pressable>

        <Pressable testID="contact-email" onPress={() => Linking.openURL(`mailto:${SUPPORT_EMAIL}`)} style={styles.row}>
          <Icon name="mail-outline" size={22} color={colors.brand} />
          <View style={{ flex: 1 }}>
            <Text style={styles.rowTitle}>Email us</Text>
            <Text style={styles.rowSub}>{SUPPORT_EMAIL}</Text>
          </View>
          <Icon name="chevron-forward" size={18} color={colors.muted} />
        </Pressable>

        <Text style={styles.section}>Common help topics</Text>

        <Pressable testID="help-list" onPress={() => router.push("/list-property")} style={styles.helpRow}>
          <Icon name="pricetag-outline" size={20} color={colors.brand} />
          <View style={{ flex: 1 }}>
            <Text style={styles.helpTitle}>How do I list my property?</Text>
            <Text style={styles.helpSub}>Free basic listing · 7 quick steps</Text>
          </View>
          <Icon name="chevron-forward" size={16} color={colors.muted} />
        </Pressable>

        <Pressable testID="help-verify" onPress={() => router.push("/become-agent")} style={styles.helpRow}>
          <Icon name="shield-checkmark-outline" size={20} color={colors.brand} />
          <View style={{ flex: 1 }}>
            <Text style={styles.helpTitle}>How do I get verified?</Text>
            <Text style={styles.helpSub}>Submit RERA / firm details in Work with us</Text>
          </View>
          <Icon name="chevron-forward" size={16} color={colors.muted} />
        </Pressable>

        <Pressable testID="help-infravalue" onPress={() => {}} style={styles.helpRow}>
          <Icon name="analytics-outline" size={20} color={colors.brand} />
          <View style={{ flex: 1 }}>
            <Text style={styles.helpTitle}>What is InfraValue™?</Text>
            <Text style={styles.helpSub}>Estimated market range using listings + locality data</Text>
          </View>
          <Icon name="chevron-forward" size={16} color={colors.muted} />
        </Pressable>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingHorizontal: spacing.lg, paddingBottom: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  title: { fontSize: 20, fontWeight: "800", color: colors.onSurface },
  sub: { fontSize: 11, color: colors.muted, marginTop: 2 },
  row: { flexDirection: "row", alignItems: "center", gap: spacing.md, padding: spacing.md, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, ...shadow.card },
  rowTitle: { fontSize: 14, fontWeight: "800", color: colors.onSurface },
  rowSub: { fontSize: 11, color: colors.muted, marginTop: 2 },
  section: { fontSize: 12, fontWeight: "800", color: colors.muted, letterSpacing: 0.8, marginTop: spacing.md, textTransform: "uppercase" },
  helpRow: { flexDirection: "row", alignItems: "center", gap: spacing.md, padding: spacing.md, borderRadius: radius.md, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border },
  helpTitle: { fontSize: 13, fontWeight: "700", color: colors.onSurface },
  helpSub: { fontSize: 11, color: colors.muted, marginTop: 2 },
});
