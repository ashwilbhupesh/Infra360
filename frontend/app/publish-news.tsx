import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, TextInput, Alert, KeyboardAvoidingView, Platform, ActivityIndicator } from "react-native";
import { Image } from "expo-image";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter, Stack } from "expo-router";
import * as ImagePicker from "expo-image-picker";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius } from "@/src/theme";
import { api, backendUrl } from "@/src/api";
import { useAuth } from "@/src/auth-context";

const CATS = ["Infrastructure", "Government", "Development", "Residential", "Industrial", "Commercial"];

type Locality = { id: string; name: string };
type Submission = {
  id: string; title: string; summary: string; category: string;
  locality_id?: string | null; image?: string | null;
  status: "pending" | "published" | "rejected";
  date: string; submitted_at?: string;
};

export default function PublishNews() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { user } = useAuth();

  const [title, setTitle] = useState("");
  const [summary, setSummary] = useState("");
  const [category, setCategory] = useState("Development");
  const [locId, setLocId] = useState<string | null>(null);
  const [image, setImage] = useState<string | null>(null);
  const [localities, setLocalities] = useState<Locality[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [mine, setMine] = useState<Submission[]>([]);

  useEffect(() => {
    (async () => {
      try {
        const [locs, m] = await Promise.all([
          api.get<Locality[]>("/localities"),
          user ? api.get<Submission[]>(`/news/mine?user_id=${user.id}`) : Promise.resolve([] as Submission[]),
        ]);
        setLocalities(locs);
        setMine(m);
      } catch {}
    })();
  }, [user]);

  const pickImage = async () => {
    const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!perm.granted) {
      Alert.alert("Photo access needed", "Enable photo access to attach an image.");
      return;
    }
    const res = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.7,
      allowsEditing: true,
      aspect: [16, 9],
    });
    if (res.canceled || !res.assets?.[0]) return;
    const asset = res.assets[0];
    setUploading(true);
    try {
      const form = new FormData();
      // @ts-ignore RN FormData file shape
      form.append("file", { uri: asset.uri, name: `news-${Date.now()}.jpg`, type: "image/jpeg" });
      const r = await fetch(`${backendUrl}/api/upload`, { method: "POST", body: form });
      if (!r.ok) throw new Error("Upload failed");
      const j = await r.json();
      setImage(j.url || null);
    } catch (e: any) {
      Alert.alert("Upload failed", e?.message || "Try another photo");
    } finally { setUploading(false); }
  };

  const canSubmit = title.trim().length >= 6 && summary.trim().length >= 20 && !submitting;

  const submit = async () => {
    if (!canSubmit) {
      Alert.alert("Fill required fields", "Give your story a title (6+ chars) and a 20+ character summary.");
      return;
    }
    setSubmitting(true);
    try {
      await api.post("/news/submit", {
        title: title.trim(),
        summary: summary.trim(),
        category,
        locality_id: locId,
        image,
        submitted_by: user?.id,
      });
      Alert.alert(
        "Submitted for review",
        "Thanks! Our team will approve genuine news within 24 hours. You'll see it in your submissions.",
        [{ text: "OK", onPress: () => router.back() }]
      );
      // reset
      setTitle(""); setSummary(""); setImage(null); setLocId(null);
    } catch (e: any) {
      Alert.alert("Couldn't submit", e?.message || "Please try again.");
    } finally { setSubmitting(false); }
  };

  const statusPill = (s: Submission["status"]) => {
    const map = {
      pending: { bg: colors.brandTertiary, fg: colors.brand, label: "Pending review" },
      published: { bg: colors.success, fg: colors.onSuccess, label: "Published" },
      rejected: { bg: colors.surfaceSecondary, fg: colors.error, label: "Not approved" },
    } as const;
    const m = map[s] ?? map.pending;
    return (
      <View style={[styles.statusPill, { backgroundColor: m.bg }]}>
        <Text style={[styles.statusText, { color: m.fg }]}>{m.label}</Text>
      </View>
    );
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.surfaceSecondary }}>
      <Stack.Screen options={{ headerShown: false }} />
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="publish-back" onPress={() => router.back()} hitSlop={12}>
          <Icon name="chevron-back" size={26} color={colors.onSurface} />
        </Pressable>
        <Text style={styles.title}>Publish news</Text>
        <View style={{ width: 26 }} />
      </View>

      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
        <ScrollView contentContainerStyle={{ padding: spacing.xl, paddingBottom: 120 }} keyboardShouldPersistTaps="handled">
          <View style={styles.notice}>
            <Icon name="information-circle-outline" size={16} color={colors.brand} />
            <Text style={styles.noticeText}>
              All submissions are reviewed by our team before going live. Share real, verifiable news from your area.
            </Text>
          </View>

          <Text style={styles.label}>Headline *</Text>
          <TextInput
            testID="publish-title"
            value={title}
            onChangeText={setTitle}
            placeholder="e.g. New flyover approved for Vaishali Nagar"
            placeholderTextColor={colors.muted}
            style={styles.input}
            maxLength={120}
          />
          <Text style={styles.hint}>{title.length}/120</Text>

          <Text style={styles.label}>Story *</Text>
          <TextInput
            testID="publish-summary"
            value={summary}
            onChangeText={setSummary}
            placeholder="Share the facts, source, timeline and impact in 2-3 lines."
            placeholderTextColor={colors.muted}
            style={[styles.input, { height: 110, textAlignVertical: "top" }]}
            multiline
            maxLength={400}
          />
          <Text style={styles.hint}>{summary.length}/400</Text>

          <Text style={styles.label}>Topic</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chipsRow}>
            {CATS.map(c => (
              <Pressable
                key={c}
                testID={`publish-cat-${c.toLowerCase()}`}
                onPress={() => setCategory(c)}
                style={[styles.chip, category === c && styles.chipActive]}
              >
                <Text style={[styles.chipText, category === c && styles.chipTextActive]}>{c}</Text>
              </Pressable>
            ))}
          </ScrollView>

          <Text style={styles.label}>Area</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chipsRow}>
            <Pressable
              testID="publish-loc-none"
              onPress={() => setLocId(null)}
              style={[styles.chip, locId === null && styles.chipActive]}
            >
              <Text style={[styles.chipText, locId === null && styles.chipTextActive]}>City-wide</Text>
            </Pressable>
            {localities.map(l => (
              <Pressable
                key={l.id}
                testID={`publish-loc-${l.id}`}
                onPress={() => setLocId(l.id)}
                style={[styles.chip, locId === l.id && styles.chipActive]}
              >
                <Text style={[styles.chipText, locId === l.id && styles.chipTextActive]}>{l.name}</Text>
              </Pressable>
            ))}
          </ScrollView>

          <Text style={styles.label}>Photo (optional)</Text>
          <Pressable testID="publish-image-picker" onPress={pickImage} style={styles.imagePicker} disabled={uploading}>
            {uploading ? (
              <ActivityIndicator color={colors.brand} />
            ) : image ? (
              <Image source={{ uri: image }} style={styles.imagePreview} contentFit="cover" />
            ) : (
              <View style={{ alignItems: "center", gap: 6 }}>
                <Icon name="image-outline" size={28} color={colors.muted} />
                <Text style={styles.imageHint}>Tap to add a photo (16:9 works best)</Text>
              </View>
            )}
          </Pressable>
          {image ? (
            <Pressable testID="publish-image-remove" onPress={() => setImage(null)} hitSlop={10} style={{ alignSelf: "center", marginTop: 6 }}>
              <Text style={{ fontSize: 12, color: colors.error, fontWeight: "700" }}>Remove photo</Text>
            </Pressable>
          ) : null}

          {mine.length > 0 && (
            <>
              <Text style={[styles.label, { marginTop: spacing.xl }]}>Your submissions</Text>
              {mine.map(s => (
                <View key={s.id} style={styles.submissionCard}>
                  <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
                    <Text style={styles.submTitle} numberOfLines={2}>{s.title}</Text>
                    {statusPill(s.status)}
                  </View>
                  <Text style={styles.submSummary} numberOfLines={2}>{s.summary}</Text>
                </View>
              ))}
            </>
          )}
        </ScrollView>
      </KeyboardAvoidingView>

      <View style={[styles.footer, { paddingBottom: Math.max(insets.bottom, 10) + 10 }]}>
        <Pressable
          testID="publish-submit"
          onPress={submit}
          disabled={!canSubmit}
          style={[styles.submitBtn, !canSubmit && { opacity: 0.5 }]}
        >
          <Icon name="paper-plane" size={14} color={colors.onBrandPrimary} />
          <Text style={styles.submitText}>{submitting ? "Submitting…" : "Submit for review"}</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", paddingHorizontal: spacing.xl, paddingBottom: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  title: { fontSize: 18, fontWeight: "800", color: colors.onSurface, letterSpacing: -0.2 },
  notice: { flexDirection: "row", gap: 8, backgroundColor: colors.brandTertiary, padding: spacing.md, borderRadius: radius.md, marginBottom: spacing.lg, alignItems: "flex-start" },
  noticeText: { flex: 1, fontSize: 12, color: colors.brand, lineHeight: 17 },
  label: { fontSize: 11, fontWeight: "800", color: colors.muted, letterSpacing: 0.6, textTransform: "uppercase", marginTop: spacing.md, marginBottom: 6 },
  input: { backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, paddingHorizontal: 14, paddingVertical: 12, fontSize: 14, color: colors.onSurface },
  hint: { fontSize: 10, color: colors.muted, textAlign: "right", marginTop: 4 },
  chipsRow: { gap: spacing.sm, paddingVertical: 4 },
  chip: { paddingHorizontal: 14, height: 34, justifyContent: "center", borderRadius: radius.pill, backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, flexShrink: 0 },
  chipActive: { backgroundColor: colors.brand, borderColor: colors.brand },
  chipText: { color: colors.onSurface, fontSize: 12, fontWeight: "600" },
  chipTextActive: { color: colors.onBrand },
  imagePicker: { height: 160, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, borderStyle: "dashed", backgroundColor: colors.surface, alignItems: "center", justifyContent: "center", overflow: "hidden" },
  imagePreview: { width: "100%", height: "100%" },
  imageHint: { fontSize: 12, color: colors.muted },
  submissionCard: { backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, padding: spacing.md, marginTop: 8 },
  submTitle: { flex: 1, fontSize: 13, fontWeight: "800", color: colors.onSurface, marginRight: 8 },
  submSummary: { fontSize: 11, color: colors.muted, marginTop: 6, lineHeight: 15 },
  statusPill: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: radius.pill },
  statusText: { fontSize: 10, fontWeight: "800", letterSpacing: 0.3 },
  footer: { position: "absolute", bottom: 0, left: 0, right: 0, paddingHorizontal: spacing.xl, paddingTop: 10, backgroundColor: colors.surface, borderTopWidth: 1, borderTopColor: colors.border },
  submitBtn: { flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 8, backgroundColor: colors.brandPrimary, paddingVertical: 14, borderRadius: radius.pill },
  submitText: { color: colors.onBrandPrimary, fontSize: 14, fontWeight: "800" },
});
