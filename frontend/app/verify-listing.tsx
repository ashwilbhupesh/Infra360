import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable, ActivityIndicator, Alert, TextInput } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useLocalSearchParams, useRouter } from "expo-router";
import * as ImagePicker from "expo-image-picker";
import Icon from "@react-native-vector-icons/ionicons";
import { Image } from "expo-image";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api, backendUrl as BURL } from "@/src/api";
import { useAuth } from "@/src/auth-context";

const DOC_TYPES = [
  { id: "patta", label: "Patta / Title Deed" },
  { id: "sale_deed", label: "Sale Deed" },
  { id: "khasra", label: "Khasra / Survey" },
  { id: "rera", label: "RERA Registration" },
  { id: "owner_id", label: "Owner ID (PAN / Aadhaar)" },
];

type Doc = { type: string; label: string; url: string };

export default function VerifyListing() {
  const { property_id } = useLocalSearchParams<{ property_id: string }>();
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { user } = useAuth();
  const [prop, setProp] = useState<any>(null);
  const [docs, setDocs] = useState<Doc[]>([]);
  const [docType, setDocType] = useState<string>("patta");
  const [note, setNote] = useState("");
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const p = await api.get(`/properties/${property_id}`);
        setProp(p);
      } finally { setLoading(false); }
    })();
  }, [property_id]);

  const addDoc = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== "granted") {
      Alert.alert("Permission needed", "Please allow photo access to upload documents.");
      return;
    }
    const res = await ImagePicker.launchImageLibraryAsync({ allowsEditing: false, quality: 0.7, mediaTypes: ["images"] });
    if (res.canceled || !res.assets?.[0]) return;
    setUploading(true);
    try {
      const file = res.assets[0];
      const form = new FormData();
      // @ts-ignore
      form.append("file", { uri: file.uri, name: `doc-${Date.now()}.jpg`, type: "image/jpeg" });
      if (user?.id) form.append("user_id", user.id);
      const upRes = await fetch(`${BURL}/api/upload`, { method: "POST", body: form });
      if (!upRes.ok) throw new Error(`Upload failed ${upRes.status}`);
      const data = await upRes.json();
      const t = DOC_TYPES.find(d => d.id === docType) || DOC_TYPES[0];
      setDocs(ds => [...ds, { type: t.id, label: t.label, url: data.url }]);
    } catch (e: any) {
      Alert.alert("Upload failed", e?.message || "Try again");
    } finally { setUploading(false); }
  };

  const removeDoc = (idx: number) => setDocs(ds => ds.filter((_, i) => i !== idx));

  const submit = async () => {
    if (docs.length === 0) {
      Alert.alert("Add at least one document", "Upload at least one proof document.");
      return;
    }
    setSubmitting(true);
    try {
      await api.post(`/properties/${property_id}/verification-request`, {
        user_id: user?.id,
        docs: docs.map(d => ({ type: d.type, label: d.label, url: d.url })),
        note: note.trim() || null,
      });
      Alert.alert(
        "Verification submitted 🎯",
        "Our team will review your documents within 48 hours. You'll see a verified badge once approved.",
        [{ text: "Done", onPress: () => router.back() }],
      );
    } catch (e: any) {
      Alert.alert("Submission failed", e?.message || "Try again");
    } finally { setSubmitting(false); }
  };

  if (loading) return <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}><ActivityIndicator color={colors.brand} /></View>;

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="verify-back-btn" onPress={() => router.back()} hitSlop={12}><Icon name="chevron-back" size={26} color={colors.onSurface} /></Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.title}>Verify listing</Text>
          <Text style={styles.sub}>Submit docs to earn the Verified badge</Text>
        </View>
      </View>

      <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingBottom: 140, gap: spacing.lg }}>
        {prop ? (
          <View style={styles.listingPreview}>
            <Icon name="shield-checkmark" size={16} color={colors.success} />
            <View style={{ flex: 1 }}>
              <Text style={styles.lpTitle} numberOfLines={1}>{prop.title}</Text>
              <Text style={styles.lpMeta}>Status: {prop.verification_status || "Not Submitted"}</Text>
            </View>
          </View>
        ) : null}

        <View style={styles.infoCard}>
          <Icon name="information-circle-outline" size={16} color={colors.brand} />
          <Text style={styles.infoTxt}>Verified listings get <Text style={{ fontWeight: "800" }}>2× more enquiries</Text> on average. Buyers trust the shield badge for serious transactions.</Text>
        </View>

        <Text style={styles.sectionTitle}>Document type</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 8 }}>
          {DOC_TYPES.map(t => {
            const active = docType === t.id;
            return (
              <Pressable key={t.id} testID={`doc-type-${t.id}`} onPress={() => setDocType(t.id)} style={[styles.docTypeChip, active && styles.docTypeChipActive]}>
                <Text style={[styles.docTypeTxt, active && styles.docTypeTxtActive]}>{t.label}</Text>
              </Pressable>
            );
          })}
        </ScrollView>

        <Pressable testID="verify-upload-btn" onPress={addDoc} disabled={uploading} style={[styles.uploadBtn, uploading && { opacity: 0.6 }]}>
          {uploading
            ? <ActivityIndicator color={colors.brand} />
            : <><Icon name="cloud-upload-outline" size={18} color={colors.brand} /><Text style={styles.uploadTxt}>Upload document photo</Text></>}
        </Pressable>

        {docs.length > 0 && (
          <View style={{ gap: 10 }}>
            <Text style={styles.sectionTitle}>{docs.length} attached</Text>
            {docs.map((d, i) => (
              <View key={i} style={styles.docRow} testID={`doc-row-${i}`}>
                <Image source={{ uri: `${BURL}${d.url}` }} style={styles.docThumb} contentFit="cover" />
                <View style={{ flex: 1 }}>
                  <Text style={styles.docLabel}>{d.label}</Text>
                  <Text style={styles.docType}>{d.type}</Text>
                </View>
                <Pressable testID={`doc-remove-${i}`} onPress={() => removeDoc(i)} hitSlop={10}>
                  <Icon name="trash-outline" size={18} color={colors.error} />
                </Pressable>
              </View>
            ))}
          </View>
        )}

        <Text style={styles.sectionTitle}>Note (optional)</Text>
        <TextInput
          testID="verify-note-input"
          style={styles.noteInput}
          placeholder="Anything our review team should know?"
          placeholderTextColor={colors.muted}
          multiline
          value={note}
          onChangeText={setNote}
        />
      </ScrollView>

      <View style={[styles.cta, { paddingBottom: insets.bottom + spacing.md }]}>
        <Pressable
          testID="verify-submit-btn"
          onPress={submit}
          disabled={submitting || docs.length === 0}
          style={[styles.ctaBtn, (submitting || docs.length === 0) && { opacity: 0.4 }]}
        >
          {submitting
            ? <ActivityIndicator color={colors.onBrandPrimary} />
            : <Text style={styles.ctaText}>Submit {docs.length} doc{docs.length === 1 ? "" : "s"} for review</Text>}
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingHorizontal: spacing.lg, paddingBottom: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  title: { fontSize: 20, fontWeight: "800", color: colors.onSurface },
  sub: { fontSize: 11, color: colors.muted, marginTop: 2 },
  sectionTitle: { fontSize: 11, fontWeight: "800", color: colors.muted, letterSpacing: 0.8, textTransform: "uppercase" },
  listingPreview: { flexDirection: "row", gap: 10, alignItems: "center", padding: spacing.md, borderRadius: radius.md, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border },
  lpTitle: { fontSize: 13, fontWeight: "700", color: colors.onSurface },
  lpMeta: { fontSize: 11, color: colors.muted, marginTop: 2 },
  infoCard: { flexDirection: "row", gap: 10, padding: spacing.md, borderRadius: radius.md, backgroundColor: "#EDF4FF", borderWidth: 1, borderColor: "#C8DBF9" },
  infoTxt: { flex: 1, fontSize: 12, color: colors.onSurface, lineHeight: 17 },
  docTypeChip: { paddingHorizontal: 12, height: 36, borderRadius: radius.pill, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, justifyContent: "center" },
  docTypeChipActive: { backgroundColor: colors.brand, borderColor: colors.brand },
  docTypeTxt: { fontSize: 12, fontWeight: "700", color: colors.onSurface },
  docTypeTxtActive: { color: colors.onBrand },
  uploadBtn: { flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 8, paddingVertical: 14, borderRadius: radius.md, borderWidth: 2, borderColor: colors.brand, borderStyle: "dashed", backgroundColor: colors.surfaceSecondary },
  uploadTxt: { color: colors.brand, fontWeight: "700" },
  docRow: { flexDirection: "row", alignItems: "center", gap: 10, padding: spacing.md, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface },
  docThumb: { width: 44, height: 44, borderRadius: 6, backgroundColor: colors.surfaceSecondary },
  docLabel: { fontSize: 13, fontWeight: "700", color: colors.onSurface },
  docType: { fontSize: 11, color: colors.muted, marginTop: 2 },
  noteInput: { minHeight: 80, borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, backgroundColor: colors.surface, padding: spacing.md, color: colors.onSurface, textAlignVertical: "top" },
  cta: { position: "absolute", left: 0, right: 0, bottom: 0, padding: spacing.lg, backgroundColor: colors.surface, borderTopWidth: 1, borderTopColor: colors.border },
  ctaBtn: { height: 52, borderRadius: radius.md, backgroundColor: colors.success, alignItems: "center", justifyContent: "center", ...shadow.card },
  ctaText: { color: colors.onSuccess, fontWeight: "800", fontSize: 15 },
});
