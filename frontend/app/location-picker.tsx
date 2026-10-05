import React, { useState, useCallback } from "react";
import { View, Text, StyleSheet, Pressable, ScrollView, TextInput, ActivityIndicator, Alert, Platform } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useRouter, Stack } from "expo-router";
import * as Location from "expo-location";
import Icon from "@react-native-vector-icons/ionicons";
import { colors, spacing, radius, shadow } from "@/src/theme";
import { api } from "@/src/api";
import { useLocationStore, SavedAddress } from "@/src/stores/location";

type Locality = { id: string; name: string; city: string; state: string };

const POPULAR_CITIES = ["Jaipur", "Jodhpur", "Udaipur", "Ajmer", "Kota", "Bikaner"];

export default function LocationPicker() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { addresses, active_id, setActive, addAddress, removeAddress } = useLocationStore();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Locality[]>([]);
  const [searching, setSearching] = useState(false);
  const [detecting, setDetecting] = useState(false);

  const detect = useCallback(async () => {
    setDetecting(true);
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== "granted") {
        Alert.alert("Permission needed", "Enable location access to detect your current area.");
        return;
      }
      const pos = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced });
      let city = "Jaipur";
      let area = "Current location";
      try {
        const places = await Location.reverseGeocodeAsync({ latitude: pos.coords.latitude, longitude: pos.coords.longitude });
        if (places?.[0]) {
          city = places[0].city || places[0].subregion || city;
          area = places[0].district || places[0].name || places[0].street || area;
        }
      } catch {}
      const id = addAddress({
        label: `Near ${area}`,
        city,
        area,
        lat: pos.coords.latitude,
        lng: pos.coords.longitude,
        tag: "other",
      });
      setActive(id);
      Alert.alert("Location set", `${area}, ${city}`, [{ text: "Done", onPress: () => router.back() }]);
    } catch (e: any) {
      Alert.alert("Could not detect", e?.message || "Try again.");
    } finally { setDetecting(false); }
  }, [addAddress, router, setActive]);

  const runSearch = useCallback(async (q: string) => {
    setQuery(q);
    if (!q.trim()) { setResults([]); return; }
    setSearching(true);
    try {
      const all = await api.get<Locality[]>("/localities");
      const low = q.toLowerCase();
      const matches = all.filter(l =>
        l.name.toLowerCase().includes(low) || l.city.toLowerCase().includes(low)
      );
      setResults(matches);
    } finally { setSearching(false); }
  }, []);

  const pickLocality = (l: Locality) => {
    const id = addAddress({ label: l.name, city: l.city, area: l.name, tag: "other" });
    setActive(id);
    router.back();
  };

  const pickCity = (city: string) => {
    const existing = addresses.find(a => a.city === city && a.area === "City-wide");
    if (existing) { setActive(existing.id); router.back(); return; }
    const id = addAddress({ label: `${city} (city-wide)`, city, area: "City-wide", tag: "other" });
    setActive(id);
    router.back();
  };

  const chooseExisting = (addr: SavedAddress) => {
    setActive(addr.id);
    router.back();
  };

  const confirmRemove = (addr: SavedAddress) => {
    Alert.alert("Remove address?", addr.label, [
      { text: "Cancel", style: "cancel" },
      { text: "Remove", style: "destructive", onPress: () => removeAddress(addr.id) },
    ]);
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.surface }}>
      <Stack.Screen options={{ headerShown: false }} />
      <View style={[styles.header, { paddingTop: insets.top + spacing.md }]}>
        <Pressable testID="loc-picker-close" onPress={() => router.back()} hitSlop={12}>
          <Icon name="close" size={26} color={colors.onSurface} />
        </Pressable>
        <View style={{ flex: 1 }}>
          <Text style={styles.title}>Set your location</Text>
          <Text style={styles.sub}>We'll tailor properties, news & agents to this place</Text>
        </View>
      </View>

      <View style={styles.searchWrap}>
        <Icon name="search" size={16} color={colors.muted} />
        <TextInput
          testID="loc-search-input"
          value={query}
          onChangeText={runSearch}
          placeholder="Search for an area, locality, or city"
          placeholderTextColor={colors.muted}
          style={styles.searchInput}
          autoFocus={Platform.OS !== "web"}
        />
        {query ? <Pressable onPress={() => runSearch("")} hitSlop={10}><Icon name="close-circle" size={16} color={colors.muted} /></Pressable> : null}
      </View>

      <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingBottom: 60, gap: spacing.lg }}>
        {!query ? (
          <>
            <Pressable testID="use-current-location" onPress={detect} style={styles.detectRow}>
              <View style={styles.detectIcon}>
                {detecting ? <ActivityIndicator color={colors.brand} /> : <Icon name="locate" size={18} color={colors.brand} />}
              </View>
              <View style={{ flex: 1 }}>
                <Text style={styles.detectTitle}>Use my current location</Text>
                <Text style={styles.detectSub}>Allow GPS access to auto-detect your area</Text>
              </View>
              <Icon name="chevron-forward" size={18} color={colors.muted} />
            </Pressable>

            <View>
              <Text style={styles.sectionLbl}>Saved places</Text>
              <View style={{ gap: 8, marginTop: 8 }}>
                {addresses.length === 0 ? (
                  <Text style={styles.hint}>No saved addresses yet. Search a locality below.</Text>
                ) : addresses.map(a => (
                  <View key={a.id} style={styles.savedRow} testID={`saved-addr-${a.id}`}>
                    <Pressable onPress={() => chooseExisting(a)} style={{ flex: 1, flexDirection: "row", alignItems: "center", gap: 10 }}>
                      <Icon
                        name={a.tag === "home" ? "home" : a.tag === "work" ? "briefcase" : "bookmark"}
                        size={16}
                        color={a.id === active_id ? colors.brandPrimary : colors.brand}
                      />
                      <View style={{ flex: 1 }}>
                        <Text style={[styles.savedLabel, a.id === active_id && { color: colors.brandPrimary }]} numberOfLines={1}>
                          {a.label}{a.id === active_id ? "  · Active" : ""}
                        </Text>
                        <Text style={styles.savedMeta} numberOfLines={1}>{a.area}, {a.city}</Text>
                      </View>
                    </Pressable>
                    {a.id !== "addr-default-jaipur" && (
                      <Pressable onPress={() => confirmRemove(a)} hitSlop={10} testID={`remove-addr-${a.id}`}>
                        <Icon name="trash-outline" size={16} color={colors.error} />
                      </Pressable>
                    )}
                  </View>
                ))}
              </View>
            </View>

            <View>
              <Text style={styles.sectionLbl}>Popular cities</Text>
              <View style={styles.cityGrid}>
                {POPULAR_CITIES.map(c => (
                  <Pressable key={c} testID={`city-${c}`} onPress={() => pickCity(c)} style={styles.cityChip}>
                    <Icon name="business-outline" size={13} color={colors.brand} />
                    <Text style={styles.cityTxt}>{c}</Text>
                  </Pressable>
                ))}
              </View>
            </View>

            <View style={styles.tip}>
              <Icon name="information-circle-outline" size={14} color={colors.brand} />
              <Text style={styles.tipTxt}>Switching areas changes trending localities, agents and news instantly across the app.</Text>
            </View>
          </>
        ) : (
          <View>
            <Text style={styles.sectionLbl}>Localities & cities</Text>
            {searching ? <ActivityIndicator color={colors.brand} style={{ marginTop: spacing.md }} /> :
              results.length === 0 ? <Text style={styles.hint}>No matches. Try "Jaipur" or an area name.</Text> :
                <View style={{ gap: 6, marginTop: 8 }}>
                  {results.map(r => (
                    <Pressable key={r.id} testID={`search-pick-${r.id}`} onPress={() => pickLocality(r)} style={styles.searchRow}>
                      <Icon name="location-outline" size={16} color={colors.brand} />
                      <View style={{ flex: 1 }}>
                        <Text style={styles.searchName}>{r.name}</Text>
                        <Text style={styles.searchMeta}>{r.city}, {r.state}</Text>
                      </View>
                      <Icon name="add-circle-outline" size={18} color={colors.muted} />
                    </Pressable>
                  ))}
                </View>}
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
  searchWrap: { flexDirection: "row", alignItems: "center", gap: 8, margin: spacing.lg, paddingHorizontal: spacing.md, height: 46, borderRadius: radius.pill, backgroundColor: colors.surfaceSecondary, borderWidth: 1, borderColor: colors.border },
  searchInput: { flex: 1, fontSize: 14, color: colors.onSurface },
  detectRow: { flexDirection: "row", alignItems: "center", gap: 10, padding: spacing.md, borderRadius: radius.md, borderWidth: 1, borderColor: colors.brandPrimary, backgroundColor: "#FFF8E7" },
  detectIcon: { width: 36, height: 36, borderRadius: 18, backgroundColor: colors.brandTertiary, alignItems: "center", justifyContent: "center" },
  detectTitle: { fontSize: 14, fontWeight: "800", color: colors.onSurface },
  detectSub: { fontSize: 11, color: colors.muted, marginTop: 2 },
  sectionLbl: { fontSize: 11, fontWeight: "800", color: colors.muted, letterSpacing: 0.8, textTransform: "uppercase" },
  savedRow: { flexDirection: "row", alignItems: "center", gap: 10, padding: spacing.md, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface },
  savedLabel: { fontSize: 14, fontWeight: "800", color: colors.onSurface },
  savedMeta: { fontSize: 11, color: colors.muted, marginTop: 2 },
  cityGrid: { flexDirection: "row", flexWrap: "wrap", gap: 8, marginTop: 8 },
  cityChip: { flexDirection: "row", alignItems: "center", gap: 6, paddingHorizontal: 12, height: 36, borderRadius: radius.pill, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surfaceSecondary },
  cityTxt: { fontSize: 13, fontWeight: "700", color: colors.onSurface },
  hint: { fontSize: 12, color: colors.muted, textAlign: "center", padding: spacing.lg },
  tip: { flexDirection: "row", gap: 8, alignItems: "flex-start", padding: spacing.md, borderRadius: radius.md, backgroundColor: colors.brandTertiary },
  tipTxt: { flex: 1, fontSize: 11, color: colors.onSurface, lineHeight: 15 },
  searchRow: { flexDirection: "row", alignItems: "center", gap: 10, padding: spacing.md, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface },
  searchName: { fontSize: 14, fontWeight: "700", color: colors.onSurface },
  searchMeta: { fontSize: 11, color: colors.muted, marginTop: 2 },
});
