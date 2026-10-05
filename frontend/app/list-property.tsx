import React, { useState } from "react";
import { View, Text, StyleSheet, ScrollView, TextInput, Pressable, ActivityIndicator, KeyboardAvoidingView, Platform, Alert, Linking } from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import Icon from "@react-native-vector-icons/ionicons";
import * as ImagePicker from "expo-image-picker";
import * as Location from "expo-location";
import { Image } from "expo-image";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api, backendUrl } from "@/src/api";
import { useAuth } from "@/src/auth-context";
import { formatINR } from "@/src/utils/format";

const TYPES = ["Apartment", "Villa", "Residential Plot", "Agricultural Land", "Commercial", "Industrial"];
const UNITS = ["sq yd", "sq ft", "acre", "bigha"];
const LOCALITIES = [
  { id: "loc-ajmer-road", name: "Ajmer Road" },
  { id: "loc-jagatpura", name: "Jagatpura" },
  { id: "loc-tonk-road", name: "Tonk Road" },
  { id: "loc-vaishali-nagar", name: "Vaishali Nagar" },
  { id: "loc-mansarovar", name: "Mansarovar" },
  { id: "loc-sikar-road", name: "Sikar Road" },
  { id: "loc-sirsi-road", name: "Sirsi Road" },
];
const SOURCES = ["Owner", "Broker", "Developer"];

type Form = {
  type: string; locality_id: string; title: string;
  area: string; area_unit: string; price: string;
  bedrooms: string; facing: string; road_width_ft: string;
  source: string; description: string; images: string[];
  lat: string; lng: string; street_address: string;
};

const empty: Form = {
  type: "", locality_id: "", title: "",
  area: "", area_unit: "sq yd", price: "",
  bedrooms: "", facing: "East", road_width_ft: "",
  source: "Owner", description: "", images: [],
  lat: "", lng: "", street_address: "",
};

export default function ListProperty() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { user } = useAuth();
  const [step, setStep] = useState(0);
  const [form, setForm] = useState<Form>(empty);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [locBusy, setLocBusy] = useState(false);

  const STEPS = ["Type", "Location", "Details", "Price", "Photos", "Seller", "Preview"];
  const total = STEPS.length;
  const set = (k: keyof Form, v: any) => setForm(s => ({ ...s, [k]: v }));

  const useCurrentLocation = async () => {
    setErr(null);
    setLocBusy(true);
    try {
      let perm = await Location.getForegroundPermissionsAsync();
      if (!perm.granted) {
        if (!perm.canAskAgain) {
          Alert.alert(
            "Location permission needed",
            "To pin your listing on the map, allow InfraJagat to use your location from Settings.",
            [
              { text: "Cancel", style: "cancel" },
              { text: "Open Settings", onPress: () => Linking.openSettings() },
            ]
          );
          return;
        }
        perm = await Location.requestForegroundPermissionsAsync();
      }
      if (!perm.granted) return;
      const pos = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced });
      const lat = pos.coords.latitude.toFixed(6);
      const lng = pos.coords.longitude.toFixed(6);
      setForm(s => ({ ...s, lat, lng }));
      // Best-effort reverse geocode for a readable address
      try {
        const places = await Location.reverseGeocodeAsync({ latitude: pos.coords.latitude, longitude: pos.coords.longitude });
        const p = places?.[0];
        if (p) {
          const line = [p.name, p.street, p.district, p.city, p.region].filter(Boolean).join(", ");
          if (line) setForm(s => ({ ...s, street_address: s.street_address || line }));
        }
      } catch { /* reverse geocode optional */ }
    } catch (e: any) {
      setErr(e?.message || "Could not fetch location");
    } finally {
      setLocBusy(false);
    }
  };

  const canNext = () => {
    if (step === 0) return !!form.type;
    if (step === 1) return !!form.locality_id && !!form.title.trim();
    if (step === 2) return !!form.area;
    if (step === 3) return !!form.price;
    if (step === 5) return !!form.source;
    return true;
  };

  const pickImage = async () => {
    const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (perm.status !== "granted") return;
    const res = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ["images"], quality: 0.7 });
    if (res.canceled || !res.assets?.[0]) return;
    const asset = res.assets[0];
    setBusy(true);
    try {
      const fd = new FormData();
      const name = asset.fileName || `p-${Date.now()}.jpg`;
      const type = asset.mimeType || "image/jpeg";
      if (Platform.OS === "web") {
        const blob = await (await fetch(asset.uri)).blob();
        fd.append("file", blob, name);
      } else {
        fd.append("file", { uri: asset.uri, name, type } as any);
      }
      const res = await fetch(`${backendUrl}/api/upload?user_id=${user?.id || "anon"}`, { method: "POST", body: fd });
      if (!res.ok) throw new Error("Upload failed");
      const data = await res.json();
      set("images", [...form.images, `${backendUrl}${data.url}`]);
    } catch (e: any) {
      setErr(e.message || "Image upload failed");
    } finally { setBusy(false); }
  };

  const submit = async () => {
    setErr(null);
    setBusy(true);
    try {
      const loc = LOCALITIES.find(l => l.id === form.locality_id);
      // Rough coordinates near locality
      const coords: Record<string, { lat: number; lng: number }> = {
        "loc-ajmer-road": { lat: 26.8901, lng: 75.7156 },
        "loc-jagatpura": { lat: 26.8290, lng: 75.8555 },
        "loc-tonk-road": { lat: 26.8395, lng: 75.8047 },
        "loc-vaishali-nagar": { lat: 26.9124, lng: 75.7398 },
        "loc-mansarovar": { lat: 26.8541, lng: 75.7645 },
        "loc-sikar-road": { lat: 26.9605, lng: 75.7833 },
        "loc-sirsi-road": { lat: 26.9316, lng: 75.6980 },
      };
      const c = coords[form.locality_id] || { lat: 26.9, lng: 75.8 };
      const userLat = parseFloat(form.lat);
      const userLng = parseFloat(form.lng);
      const hasUserCoords = Number.isFinite(userLat) && Number.isFinite(userLng)
        && userLat >= -90 && userLat <= 90 && userLng >= -180 && userLng <= 180;
      const finalLat = hasUserCoords ? userLat : c.lat;
      const finalLng = hasUserCoords ? userLng : c.lng;
      const fallbackAddress = `${loc?.name || ""}, Jaipur`;
      const finalAddress = form.street_address.trim() ? form.street_address.trim() : fallbackAddress;
      const body = {
        title: form.title,
        type: form.type,
        price: parseFloat(form.price),
        area: parseFloat(form.area),
        area_unit: form.area_unit,
        lat: finalLat, lng: finalLng,
        locality_id: form.locality_id,
        address: finalAddress,
        bedrooms: form.bedrooms ? parseInt(form.bedrooms) : null,
        facing: form.facing || null,
        road_width_ft: form.road_width_ft ? parseInt(form.road_width_ft) : null,
        source: form.source,
        images: form.images.length ? form.images : ["https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=1200&q=80"],
        owner_user_id: user?.id,
        description: form.description,
      };
      const created = await api.post<any>("/properties", body);
      router.replace(`/property/${created.id}`);
    } catch (e: any) { setErr(e.message || "Failed to submit"); }
    finally { setBusy(false); }
  };

  return (
    <KeyboardAvoidingView style={{ flex: 1, backgroundColor: colors.surface }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <View style={[styles.header, { paddingTop: insets.top + spacing.sm }]}>
        <Pressable testID="close-btn" onPress={() => router.back()} style={styles.closeBtn}>
          <Icon name="close" size={20} color={colors.onSurface} />
        </Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.stepLabel}>Step {step + 1} / {total}</Text>
          <Text style={styles.stepTitle}>{STEPS[step]}</Text>
        </View>
      </View>
      <View style={styles.progressBar}>
        <View style={[styles.progressFill, { width: `${((step + 1) / total) * 100}%` }]} />
      </View>

      <ScrollView contentContainerStyle={styles.body} keyboardShouldPersistTaps="handled">
        {step === 0 && (
          <>
            <Text style={styles.q}>What are you listing?</Text>
            {TYPES.map(t => (
              <Pressable key={t} testID={`type-${t.replace(/\s/g, "-").toLowerCase()}`} onPress={() => set("type", t)} style={[styles.option, form.type === t && styles.optionActive]}>
                <Text style={[styles.optionText, form.type === t && styles.optionTextActive]}>{t}</Text>
                {form.type === t && <Icon name="checkmark" size={18} color={colors.onBrand} />}
              </Pressable>
            ))}
          </>
        )}
        {step === 1 && (
          <>
            <Text style={styles.q}>Where is it?</Text>
            <View style={styles.chipsWrap}>
              {LOCALITIES.map(l => (
                <Pressable key={l.id} testID={`loc-${l.id}`} onPress={() => set("locality_id", l.id)} style={[styles.chip, form.locality_id === l.id && styles.chipActive]}>
                  <Text style={[styles.chipText, form.locality_id === l.id && styles.chipTextActive]}>{l.name}</Text>
                </Pressable>
              ))}
            </View>
            <Text style={styles.label}>Listing Title</Text>
            <TextInput testID="title-input" style={styles.input} placeholder="e.g. 600 sq yd corner plot" placeholderTextColor={colors.muted} value={form.title} onChangeText={t => set("title", t)} />
          </>
        )}
        {step === 2 && (
          <>
            <Text style={styles.q}>Property details</Text>
            <Text style={styles.label}>Area</Text>
            <TextInput testID="area-input" style={styles.input} placeholder="600" placeholderTextColor={colors.muted} keyboardType="numeric" value={form.area} onChangeText={t => set("area", t)} />
            <Text style={styles.hintSmall}>Enter the number only — pick the unit below.</Text>
            <Text style={styles.label}>Unit</Text>
            <View style={styles.chipsWrap}>
              {UNITS.map(u => (
                <Pressable key={u} onPress={() => set("area_unit", u)} style={[styles.chip, form.area_unit === u && styles.chipActive]}>
                  <Text style={[styles.chipText, form.area_unit === u && styles.chipTextActive]}>{u}</Text>
                </Pressable>
              ))}
            </View>

            <Text style={styles.sectionTitle}>Pin on map</Text>
            <Text style={styles.hintSmall}>Drop a precise pin so buyers can find your property on the map (works on iOS & Android).</Text>
            <Pressable testID="use-current-location-btn" onPress={useCurrentLocation} disabled={locBusy} style={[styles.gpsBtn, locBusy && { opacity: 0.6 }]}>
              {locBusy
                ? <ActivityIndicator color={colors.brand} />
                : <Icon name="locate" size={18} color={colors.brand} />}
              <Text style={styles.gpsBtnText}>{locBusy ? "Fetching…" : "Use my current location"}</Text>
            </Pressable>

            <View style={styles.rowGap}>
              <View style={{ flex: 1 }}>
                <Text style={styles.label}>Latitude</Text>
                <TextInput
                  testID="lat-input"
                  style={styles.input}
                  placeholder="26.9124"
                  placeholderTextColor={colors.muted}
                  keyboardType="numbers-and-punctuation"
                  value={form.lat}
                  onChangeText={t => set("lat", t)}
                />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={styles.label}>Longitude</Text>
                <TextInput
                  testID="lng-input"
                  style={styles.input}
                  placeholder="75.7873"
                  placeholderTextColor={colors.muted}
                  keyboardType="numbers-and-punctuation"
                  value={form.lng}
                  onChangeText={t => set("lng", t)}
                />
              </View>
            </View>
            {(form.lat && form.lng) ? (
              <View style={styles.coordPreview}>
                <Icon name="pin" size={14} color={colors.brand} />
                <Text style={styles.coordPreviewText} numberOfLines={1}>{form.lat}, {form.lng}</Text>
              </View>
            ) : (
              <Text style={styles.hintSmall}>If left empty, we{"\u2019"}ll place the pin at the selected locality center.</Text>
            )}

            <Text style={styles.label}>Street / Landmark (optional)</Text>
            <TextInput
              testID="street-input"
              style={styles.input}
              placeholder="e.g. Near D-Mart, Sector 7, Ajmer Road"
              placeholderTextColor={colors.muted}
              value={form.street_address}
              onChangeText={t => set("street_address", t)}
            />

            {(form.type === "Apartment" || form.type === "Villa") && (
              <>
                <Text style={styles.label}>Bedrooms</Text>
                <TextInput testID="bedrooms-input" style={styles.input} placeholder="3" placeholderTextColor={colors.muted} keyboardType="numeric" value={form.bedrooms} onChangeText={t => set("bedrooms", t)} />
              </>
            )}
            <Text style={styles.label}>Road Width (ft)</Text>
            <TextInput style={styles.input} placeholder="30" placeholderTextColor={colors.muted} keyboardType="numeric" value={form.road_width_ft} onChangeText={t => set("road_width_ft", t)} />
          </>
        )}
        {step === 3 && (
          <>
            <Text style={styles.q}>Asking price</Text>
            <TextInput testID="price-input" style={[styles.input, styles.bigInput]} placeholder="7200000" placeholderTextColor={colors.muted} keyboardType="numeric" value={form.price} onChangeText={t => set("price", t)} />
            {form.price ? <Text style={styles.priceHint}>{formatINR(parseFloat(form.price) || 0)}</Text> : null}
          </>
        )}
        {step === 4 && (
          <>
            <Text style={styles.q}>Add photos</Text>
            <View style={styles.photosGrid}>
              {form.images.map((u, i) => (
                <Image key={i} source={{ uri: u }} style={styles.photoThumb} contentFit="cover" />
              ))}
              <Pressable testID="add-photo-btn" style={styles.addPhoto} onPress={pickImage}>
                {busy ? <ActivityIndicator color={colors.brand} /> : <>
                  <Icon name="camera-outline" size={22} color={colors.brand} />
                  <Text style={styles.addPhotoText}>Add photo</Text>
                </>}
              </Pressable>
            </View>
            <Text style={styles.hint}>Optional. We{"\u2019"}ll use a placeholder if none added.</Text>
          </>
        )}
        {step === 5 && (
          <>
            <Text style={styles.q}>You are the?</Text>
            {SOURCES.map(s => (
              <Pressable key={s} onPress={() => set("source", s)} style={[styles.option, form.source === s && styles.optionActive]}>
                <Text style={[styles.optionText, form.source === s && styles.optionTextActive]}>{s}</Text>
                {form.source === s && <Icon name="checkmark" size={18} color={colors.onBrand} />}
              </Pressable>
            ))}
          </>
        )}
        {step === 6 && (
          <>
            <Text style={styles.q}>Preview</Text>
            <View style={styles.preview}>
              {form.images[0] ? <Image source={{ uri: form.images[0] }} style={styles.previewImg} contentFit="cover" /> : null}
              <View style={{ padding: spacing.md }}>
                <Text style={styles.previewPrice}>{formatINR(parseFloat(form.price) || 0)}</Text>
                <Text style={styles.previewTitle}>{form.title || "—"}</Text>
                <Text style={styles.previewMeta}>{form.area} {form.area_unit} · {form.type}</Text>
                <Text style={styles.previewMeta}>{form.street_address || `${LOCALITIES.find(l => l.id === form.locality_id)?.name || "—"}, Jaipur`}</Text>
                {(form.lat && form.lng) ? (
                  <View style={styles.pinRow}>
                    <Icon name="pin" size={12} color={colors.brand} />
                    <Text style={styles.pinRowText}>Pinned at {form.lat}, {form.lng}</Text>
                  </View>
                ) : (
                  <Text style={styles.previewMeta}>Pin: locality center (no exact pin added)</Text>
                )}
                <View style={styles.pendingPill}><Text style={styles.pendingText}>Verification Pending</Text></View>
              </View>
            </View>
          </>
        )}
        {err && <Text style={styles.err}>{err}</Text>}
      </ScrollView>

      <View style={[styles.footer, { paddingBottom: insets.bottom + spacing.md }]}>
        {step > 0 && (
          <Pressable testID="back-step-btn" onPress={() => setStep(s => s - 1)} style={styles.secondaryBtn}>
            <Text style={styles.secondaryText}>Back</Text>
          </Pressable>
        )}
        {step < total - 1 ? (
          <Pressable testID="next-step-btn" disabled={!canNext()} onPress={() => setStep(s => s + 1)} style={[styles.primaryBtn, !canNext() && { opacity: 0.5 }]}>
            <Text style={styles.primaryText}>Continue</Text>
          </Pressable>
        ) : (
          <Pressable testID="submit-btn" disabled={busy} onPress={submit} style={[styles.primaryBtn, busy && { opacity: 0.5 }]}>
            {busy ? <ActivityIndicator color={colors.onBrandPrimary} /> : <Text style={styles.primaryText}>Submit Listing</Text>}
          </Pressable>
        )}
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingHorizontal: spacing.lg, paddingBottom: spacing.md },
  closeBtn: { width: 36, height: 36, borderRadius: 18, backgroundColor: colors.surfaceSecondary, alignItems: "center", justifyContent: "center" },
  stepLabel: { fontSize: 11, color: colors.muted, fontWeight: "600", letterSpacing: 0.5, textTransform: "uppercase" },
  stepTitle: { fontSize: 18, fontWeight: "700", color: colors.onSurface, marginTop: 2 },
  progressBar: { height: 3, backgroundColor: colors.border, marginHorizontal: spacing.lg, borderRadius: 2 },
  progressFill: { height: 3, backgroundColor: colors.brandPrimary, borderRadius: 2 },
  body: { padding: spacing.xl, paddingBottom: 120 },
  q: { fontSize: 20, fontWeight: "700", color: colors.onSurface, marginBottom: spacing.lg, letterSpacing: -0.3 },
  option: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", padding: spacing.lg, borderRadius: radius.md, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border, marginBottom: spacing.sm },
  optionActive: { backgroundColor: colors.brand, borderColor: colors.brand },
  optionText: { fontSize: 15, fontWeight: "600", color: colors.onSurface },
  optionTextActive: { color: colors.onBrand },
  chipsWrap: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm, marginBottom: spacing.lg },
  chip: { paddingHorizontal: spacing.md, paddingVertical: spacing.sm + 2, borderRadius: radius.pill, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border },
  chipActive: { backgroundColor: colors.brand, borderColor: colors.brand },
  chipText: { color: colors.onSurface, fontSize: 13, fontWeight: "500" },
  chipTextActive: { color: colors.onBrand, fontWeight: "600" },
  label: { fontSize: 11, fontWeight: "700", color: colors.muted, letterSpacing: 0.5, textTransform: "uppercase", marginBottom: spacing.sm, marginTop: spacing.sm },
  input: { borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, padding: spacing.md, fontSize: 15, color: colors.onSurface, backgroundColor: colors.surfaceSecondary },
  bigInput: { fontSize: 22, fontWeight: "700", padding: spacing.lg },
  priceHint: { fontSize: 24, fontWeight: "700", color: colors.brandPrimary, marginTop: spacing.md },
  photosGrid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm },
  photoThumb: { width: 100, height: 100, borderRadius: radius.md, backgroundColor: colors.surfaceTertiary },
  addPhoto: { width: 100, height: 100, borderRadius: radius.md, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.borderStrong, borderStyle: "dashed", alignItems: "center", justifyContent: "center" },
  addPhotoText: { fontSize: 11, color: colors.brand, fontWeight: "600", marginTop: 4 },
  hint: { fontSize: 11, color: colors.muted, marginTop: spacing.md },
  hintSmall: { fontSize: 11, color: colors.muted, marginTop: 4, marginBottom: spacing.sm, lineHeight: 15 },
  sectionTitle: { fontSize: 14, fontWeight: "800", color: colors.onSurface, marginTop: spacing.lg, marginBottom: 2, letterSpacing: 0.2 },
  gpsBtn: { flexDirection: "row", alignItems: "center", justifyContent: "center", gap: spacing.sm, paddingVertical: spacing.md, borderRadius: radius.md, backgroundColor: colors.brandTertiary, borderWidth: 1, borderColor: colors.brand, marginBottom: spacing.md },
  gpsBtnText: { fontSize: 14, fontWeight: "700", color: colors.brand },
  rowGap: { flexDirection: "row", gap: spacing.sm },
  coordPreview: { flexDirection: "row", alignItems: "center", gap: 6, marginTop: spacing.sm, paddingVertical: 8, paddingHorizontal: spacing.md, borderRadius: radius.md, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border },
  coordPreviewText: { fontSize: 12, fontWeight: "700", color: colors.onSurface, flex: 1 },
  preview: { borderRadius: radius.lg, backgroundColor: colors.surfaceSecondary, overflow: "hidden", borderWidth: 1, borderColor: colors.border },
  previewImg: { width: "100%", height: 180 },
  previewPrice: { fontSize: 24, fontWeight: "700", color: colors.brand },
  previewTitle: { fontSize: 15, fontWeight: "600", color: colors.onSurface, marginTop: 2 },
  previewMeta: { fontSize: 12, color: colors.muted, marginTop: 2 },
  pendingPill: { alignSelf: "flex-start", marginTop: spacing.md, backgroundColor: colors.warning, paddingHorizontal: spacing.md, paddingVertical: 4, borderRadius: radius.pill },
  pendingText: { fontSize: 10, color: colors.onWarning, fontWeight: "700", letterSpacing: 0.3 },
  pinRow: { flexDirection: "row", alignItems: "center", gap: 4, marginTop: 6 },
  pinRowText: { fontSize: 11, color: colors.brand, fontWeight: "700" },
  err: { color: colors.error, marginTop: spacing.md },
  footer: { position: "absolute", left: 0, right: 0, bottom: 0, flexDirection: "row", gap: spacing.md, padding: spacing.lg, backgroundColor: colors.surface, borderTopWidth: 1, borderTopColor: colors.border },
  primaryBtn: { flex: 1, backgroundColor: colors.brandPrimary, alignItems: "center", justifyContent: "center", paddingVertical: spacing.md + 2, borderRadius: radius.md, ...shadow.card },
  primaryText: { color: colors.onBrandPrimary, fontWeight: "700", fontSize: 15 },
  secondaryBtn: { paddingHorizontal: spacing.xl, paddingVertical: spacing.md + 2, borderRadius: radius.md, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border, alignItems: "center", justifyContent: "center" },
  secondaryText: { color: colors.onSurface, fontWeight: "600", fontSize: 15 },
});
