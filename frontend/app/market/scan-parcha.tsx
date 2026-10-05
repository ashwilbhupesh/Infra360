import React, { useRef, useState } from "react";
import { View, Text, StyleSheet, Pressable, ScrollView, ActivityIndicator, Alert, Platform } from "react-native";
import { Image } from "expo-image";
import { CameraView, useCameraPermissions } from "expo-camera";
import * as ImagePicker from "expo-image-picker";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter, Stack } from "expo-router";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api, backendUrl as BURL } from "@/src/api";
import { useAuth } from "@/src/auth-context";
import { useMaterialsCart } from "@/src/stores/materials-cart";
import { useVoiceDraft } from "@/src/stores/voice-draft";
import { indianComma } from "@/src/utils/format";

type Line = {
  product_id: string; name: string; brand?: string; image?: string; unit?: string;
  price: number; mrp?: number; store_id: string; store_name?: string; store_area?: string;
  qty: number; subtotal: number;
  query?: { name?: string; brand?: string; raw?: string; quantity?: number; unit?: string };
};

export default function ScanParcha() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { user } = useAuth();
  const addToCart = useMaterialsCart(s => s.add);
  const setDraft = useVoiceDraft(s => s.setDraft);

  const [permission, requestPermission] = useCameraPermissions();
  const cameraRef = useRef<CameraView>(null);
  const [capturing, setCapturing] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [uploadedPath, setUploadedPath] = useState<string | null>(null);
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState<{ items: Line[]; unmatched: any[]; total_estimated: number } | null>(null);

  const openGallery = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== "granted") { Alert.alert("Permission needed", "Allow photo access to pick a parcha image."); return; }
    const res = await ImagePicker.launchImageLibraryAsync({ quality: 0.8, mediaTypes: ["images"] });
    if (res.canceled || !res.assets?.[0]) return;
    setPreview(res.assets[0].uri);
    await upload(res.assets[0].uri);
  };

  const capture = async () => {
    if (!cameraRef.current) return;
    setCapturing(true);
    try {
      const photo = await cameraRef.current.takePictureAsync({ quality: 0.7, skipProcessing: true });
      if (!photo?.uri) throw new Error("No photo");
      setPreview(photo.uri);
      await upload(photo.uri);
    } catch (e: any) {
      Alert.alert("Capture failed", e?.message || "Try again");
    } finally { setCapturing(false); }
  };

  const upload = async (uri: string) => {
    setScanning(true);
    setResult(null);
    try {
      const form = new FormData();
      // @ts-ignore
      form.append("file", { uri, name: `parcha-${Date.now()}.jpg`, type: "image/jpeg" });
      if (user?.id) form.append("user_id", user.id);
      const upRes = await fetch(`${BURL}/api/upload`, { method: "POST", body: form });
      if (!upRes.ok) throw new Error(`Upload failed ${upRes.status}`);
      const { url } = await upRes.json();
      setUploadedPath(url);
      const scan = await api.post<{ items: Line[]; unmatched: any[]; total_estimated: number; extracted: any[] }>("/materials/scan-parcha", {
        user_id: user?.id, image_url: url,
      });
      setResult({ items: scan.items, unmatched: scan.unmatched, total_estimated: scan.total_estimated });
      if ((scan.items?.length || 0) === 0) {
        Alert.alert("Nothing matched", "We couldn't match any items from this parcha. Try a clearer photo.");
      }
    } catch (e: any) {
      Alert.alert("Scan failed", e?.message || "Try again with a clearer photo.");
    } finally { setScanning(false); }
  };

  const retake = () => { setPreview(null); setResult(null); setUploadedPath(null); };

  const addAllToCart = () => {
    if (!result?.items?.length) return;
    setDraft({
      source: "scan",
      items: result.items as any,
      unmatched: result.unmatched,
      total_estimated: result.total_estimated,
      created_at: new Date().toISOString(),
    });
    router.push("/market/voice-cart-review" as any);
  };

  // Permissions UI
  if (!permission) {
    return <View style={{ flex: 1, backgroundColor: colors.surface, alignItems: "center", justifyContent: "center" }}><ActivityIndicator color={colors.brand} /></View>;
  }
  if (!permission.granted && Platform.OS !== "web") {
    return (
      <View style={{ flex: 1, backgroundColor: colors.surface, padding: spacing.lg }}>
        <Stack.Screen options={{ headerShown: false }} />
        <View style={[styles.header, { paddingTop: insets.top }]}>
          <Pressable onPress={() => router.back()} hitSlop={12}><Icon name="chevron-back" size={26} color={colors.onSurface} /></Pressable>
          <Text style={styles.title}>Scan parcha</Text>
        </View>
        <View style={{ alignItems: "center", padding: spacing.xxxl, gap: spacing.md }}>
          <Icon name="camera-outline" size={48} color={colors.brand} />
          <Text style={styles.permTitle}>Camera access needed</Text>
          <Text style={styles.permSub}>We’ll read your handwritten material list and pick the cheapest vendor automatically.</Text>
          <Pressable testID="grant-camera-btn" onPress={requestPermission} style={styles.primaryBtn}>
            <Text style={styles.primaryTxt}>Allow camera</Text>
          </Pressable>
          <Pressable testID="use-gallery-btn" onPress={openGallery} style={styles.ghostBtn}>
            <Icon name="images-outline" size={16} color={colors.brand} />
            <Text style={styles.ghostTxt}>Pick from gallery instead</Text>
          </Pressable>
        </View>
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: "#000" }}>
      <Stack.Screen options={{ headerShown: false }} />

      {!preview ? (
        <>
          {Platform.OS !== "web" ? (
            <CameraView ref={cameraRef} style={StyleSheet.absoluteFill} facing="back" />
          ) : (
            <View style={[StyleSheet.absoluteFill, { backgroundColor: "#1A1A1A", alignItems: "center", justifyContent: "center" }]}>
              <Icon name="camera-outline" size={64} color="rgba(255,255,255,0.5)" />
              <Text style={{ color: "#FFFFFF", marginTop: spacing.md }}>Camera preview is best on the mobile app</Text>
              <Text style={{ color: "rgba(255,255,255,0.6)", fontSize: 12, marginTop: 4 }}>Use the gallery button below to try it on web.</Text>
            </View>
          )}

          {/* Overlay guide + top chrome */}
          <View style={{ flex: 1, justifyContent: "space-between" }}>
            <View style={[styles.topBar, { paddingTop: insets.top + spacing.md }]}>
              <Pressable testID="scan-back-btn" onPress={() => router.back()} hitSlop={14} style={styles.topBtn}>
                <Icon name="chevron-back" size={22} color="#FFFFFF" />
              </Pressable>
              <View style={styles.topTitlePill}>
                <Icon name="scan" size={14} color="#FFFFFF" />
                <Text style={styles.topTitleTxt}>Scan parcha</Text>
              </View>
              <Pressable testID="gallery-btn" onPress={openGallery} hitSlop={14} style={styles.topBtn}>
                <Icon name="images-outline" size={20} color="#FFFFFF" />
              </Pressable>
            </View>

            <View style={styles.guideWrap}>
              <View style={styles.guideFrame} />
              <Text style={styles.guideTxt}>Fit the full list inside the frame</Text>
              <Text style={styles.guideSub}>Hold steady · good light · brand names visible</Text>
            </View>

            <View style={[styles.shutterRow, { paddingBottom: insets.bottom + spacing.lg }]}>
              <View style={{ width: 48 }} />
              <Pressable testID="shutter-btn" onPress={capture} disabled={capturing} style={styles.shutter}>
                {capturing ? <ActivityIndicator color={colors.brand} /> : <View style={styles.shutterInner} />}
              </Pressable>
              <Pressable testID="shutter-gallery-btn" onPress={openGallery} hitSlop={14} style={styles.sideBtn}>
                <Icon name="images-outline" size={22} color="#FFFFFF" />
              </Pressable>
            </View>
          </View>
        </>
      ) : (
        <View style={{ flex: 1, backgroundColor: colors.surface }}>
          <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
            <Pressable testID="retake-btn" onPress={retake} hitSlop={12}><Icon name="chevron-back" size={26} color={colors.onSurface} /></Pressable>
            <View style={{ flex: 1 }}>
              <Text style={styles.title}>Parcha scanned</Text>
              <Text style={styles.sub}>Cheapest listed prices across vendors</Text>
            </View>
            <Pressable testID="rescan-btn" onPress={retake} hitSlop={10}>
              <Icon name="refresh-outline" size={20} color={colors.onSurface} />
            </Pressable>
          </View>

          <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingBottom: 160 }}>
            <View style={styles.previewRow}>
              <Image source={{ uri: preview }} style={styles.previewThumb} contentFit="cover" />
              <View style={{ flex: 1, gap: 4 }}>
                <Text style={styles.previewTitle}>Your parcha</Text>
                <Text style={styles.previewMeta}>
                  {scanning ? "Reading items with AI..." : result ? `${result.items.length} matched · ${result.unmatched.length} unmatched` : "Processing..."}
                </Text>
              </View>
            </View>

            {scanning ? (
              <View style={styles.scanning}>
                <ActivityIndicator color={colors.brand} />
                <Text style={styles.scanningTxt}>Finding the cheapest vendor for each line...</Text>
              </View>
            ) : result ? (
              <>
                {result.items.length > 0 && (
                  <View style={{ marginTop: spacing.lg, gap: 10 }}>
                    <Text style={styles.sectionLbl}>MATCHED ITEMS · auto-cart</Text>
                    {result.items.map((it, idx) => (
                      <View key={it.product_id + idx} style={styles.itemCard} testID={`parcha-line-${idx}`}>
                        <Image source={{ uri: it.image }} style={styles.itemImg} contentFit="cover" />
                        <View style={{ flex: 1 }}>
                          <Text style={styles.itemName} numberOfLines={2}>{it.name}</Text>
                          <Text style={styles.itemBrand}>{it.brand || "—"}{it.unit ? ` · per ${it.unit}` : ""}</Text>
                          <Text style={styles.itemStore} numberOfLines={1}>{it.store_name} · {it.store_area}</Text>
                          {it.query?.raw ? <Text style={styles.rawTxt} numberOfLines={1}>“{it.query.raw}”</Text> : null}
                        </View>
                        <View style={{ alignItems: "flex-end", gap: 4 }}>
                          <Text style={styles.qty}>×{it.qty}</Text>
                          <Text style={styles.price}>₹{indianComma(it.price)}</Text>
                          <Text style={styles.sub2}>Line ₹{indianComma(it.subtotal)}</Text>
                        </View>
                      </View>
                    ))}
                    <View style={styles.totalBar}>
                      <Text style={styles.totalLbl}>Estimated cart total</Text>
                      <Text style={styles.totalVal}>₹{indianComma(result.total_estimated)}</Text>
                    </View>
                  </View>
                )}

                {result.unmatched.length > 0 && (
                  <View style={{ marginTop: spacing.lg, gap: 10 }}>
                    <Text style={styles.sectionLbl}>WE COULDN'T MATCH</Text>
                    {result.unmatched.map((u, i) => (
                      <View key={i} style={styles.unmatchedRow}>
                        <Icon name="alert-circle-outline" size={16} color={colors.error} />
                        <View style={{ flex: 1 }}>
                          <Text style={styles.unTxt}>{u.query?.name || u.query?.raw || "Unknown item"}</Text>
                          <Text style={styles.unSub}>Reason: {u.reason || "No catalogue match"}</Text>
                        </View>
                      </View>
                    ))}
                  </View>
                )}
              </>
            ) : null}
          </ScrollView>

          {result && result.items.length > 0 && (
            <View style={[styles.cta, { paddingBottom: insets.bottom + spacing.md }]}>
              <Pressable testID="add-all-to-cart-btn" onPress={addAllToCart} style={styles.ctaBtn}>
                <Icon name="eye" size={16} color={colors.onBrandPrimary} />
                <Text style={styles.ctaTxt}>Review {result.items.length} item{result.items.length === 1 ? "" : "s"} · ₹{indianComma(result.total_estimated)}</Text>
              </Pressable>
            </View>
          )}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  // Permission screen
  header: { flexDirection: "row", alignItems: "center", gap: spacing.md, paddingHorizontal: spacing.lg, paddingBottom: spacing.md, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  title: { fontSize: 20, fontWeight: "800", color: colors.onSurface },
  sub: { fontSize: 11, color: colors.muted, marginTop: 2 },
  permTitle: { fontSize: 16, fontWeight: "800", color: colors.onSurface, marginTop: spacing.md },
  permSub: { textAlign: "center", color: colors.muted, lineHeight: 18 },
  primaryBtn: { paddingVertical: 14, paddingHorizontal: 32, borderRadius: radius.md, backgroundColor: colors.brandPrimary, marginTop: spacing.md },
  primaryTxt: { color: colors.onBrandPrimary, fontWeight: "800" },
  ghostBtn: { flexDirection: "row", alignItems: "center", gap: 6, paddingVertical: 10 },
  ghostTxt: { color: colors.brand, fontWeight: "700" },

  // Camera overlay
  topBar: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", paddingHorizontal: spacing.lg, paddingBottom: spacing.md },
  topBtn: { width: 40, height: 40, borderRadius: 20, backgroundColor: "rgba(0,0,0,0.5)", alignItems: "center", justifyContent: "center" },
  topTitlePill: { flexDirection: "row", alignItems: "center", gap: 6, paddingHorizontal: 12, height: 32, borderRadius: 16, backgroundColor: "rgba(0,0,0,0.5)" },
  topTitleTxt: { color: "#FFFFFF", fontWeight: "800", fontSize: 13, letterSpacing: 0.4 },
  guideWrap: { alignItems: "center", gap: 8, paddingBottom: spacing.lg },
  guideFrame: { width: "80%", aspectRatio: 3 / 4, borderWidth: 2, borderColor: "rgba(255,255,255,0.9)", borderRadius: 14, backgroundColor: "transparent" },
  guideTxt: { color: "#FFFFFF", fontWeight: "800", fontSize: 14, marginTop: 8 },
  guideSub: { color: "rgba(255,255,255,0.75)", fontSize: 11 },
  shutterRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", paddingHorizontal: spacing.xxl },
  shutter: { width: 76, height: 76, borderRadius: 38, backgroundColor: "#FFFFFF", borderWidth: 4, borderColor: "rgba(255,255,255,0.4)", alignItems: "center", justifyContent: "center" },
  shutterInner: { width: 56, height: 56, borderRadius: 28, backgroundColor: colors.brandPrimary },
  sideBtn: { width: 48, height: 48, borderRadius: 24, backgroundColor: "rgba(0,0,0,0.5)", alignItems: "center", justifyContent: "center" },

  // Result screen
  previewRow: { flexDirection: "row", alignItems: "center", gap: 12, padding: spacing.md, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surfaceSecondary },
  previewThumb: { width: 60, height: 60, borderRadius: 8, backgroundColor: colors.surfaceTertiary },
  previewTitle: { fontSize: 14, fontWeight: "800", color: colors.onSurface },
  previewMeta: { fontSize: 11, color: colors.muted },
  scanning: { alignItems: "center", padding: spacing.xxl, gap: spacing.md },
  scanningTxt: { color: colors.muted, fontSize: 13 },
  sectionLbl: { fontSize: 11, fontWeight: "800", color: colors.muted, letterSpacing: 0.6 },
  itemCard: { flexDirection: "row", gap: 10, padding: 10, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface, alignItems: "flex-start" },
  itemImg: { width: 56, height: 56, borderRadius: 8, backgroundColor: colors.surfaceSecondary },
  itemName: { fontSize: 13, fontWeight: "800", color: colors.onSurface, lineHeight: 17 },
  itemBrand: { fontSize: 11, color: colors.muted, marginTop: 2 },
  itemStore: { fontSize: 11, color: colors.brand, marginTop: 4, fontWeight: "700" },
  rawTxt: { fontSize: 11, color: colors.muted, marginTop: 4, fontStyle: "italic" },
  qty: { fontSize: 11, fontWeight: "800", color: colors.muted },
  price: { fontSize: 15, fontWeight: "800", color: colors.brandPrimary },
  sub2: { fontSize: 10, color: colors.muted },
  totalBar: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", padding: spacing.md, borderRadius: radius.md, backgroundColor: "#EDF4FF", borderWidth: 1, borderColor: "#C8DBF9" },
  totalLbl: { fontSize: 12, fontWeight: "800", color: colors.muted, letterSpacing: 0.6 },
  totalVal: { fontSize: 20, fontWeight: "800", color: colors.brand },
  unmatchedRow: { flexDirection: "row", gap: 10, padding: spacing.md, borderRadius: radius.md, borderWidth: 1, borderColor: colors.error, backgroundColor: "#FFF4F2" },
  unTxt: { fontSize: 13, fontWeight: "700", color: colors.onSurface },
  unSub: { fontSize: 11, color: colors.muted, marginTop: 2 },

  cta: { position: "absolute", left: 0, right: 0, bottom: 0, padding: spacing.lg, backgroundColor: colors.surface, borderTopWidth: 1, borderTopColor: colors.border, ...shadow.floating },
  ctaBtn: { flexDirection: "row", gap: 8, alignItems: "center", justifyContent: "center", height: 52, borderRadius: radius.md, backgroundColor: colors.brandPrimary },
  ctaTxt: { color: colors.onBrandPrimary, fontWeight: "800", fontSize: 14 },
});
