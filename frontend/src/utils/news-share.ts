import AsyncStorage from "@react-native-async-storage/async-storage";
import { Share, Linking, Platform } from "react-native";
import * as Sharing from "expo-sharing";

const KEY = "infrajagat.offline_news.v1";

export type OfflineNewsItem = {
  id: string;
  title: string;
  summary: string;
  category: string;
  source: string;
  date: string;
  image?: string | null;
  locality_name?: string | null;
  saved_at: string;
};

export async function getOfflineNews(): Promise<OfflineNewsItem[]> {
  try {
    const raw = await AsyncStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as OfflineNewsItem[]) : [];
  } catch { return []; }
}

export async function isOfflineSaved(id: string): Promise<boolean> {
  const list = await getOfflineNews();
  return list.some(n => n.id === id);
}

export async function saveOffline(n: Omit<OfflineNewsItem, "saved_at">): Promise<OfflineNewsItem[]> {
  const list = await getOfflineNews();
  const already = list.find(x => x.id === n.id);
  const next = already ? list : [{ ...n, saved_at: new Date().toISOString() }, ...list].slice(0, 100);
  await AsyncStorage.setItem(KEY, JSON.stringify(next));
  return next;
}

export async function removeOffline(id: string): Promise<OfflineNewsItem[]> {
  const list = await getOfflineNews();
  const next = list.filter(x => x.id !== id);
  await AsyncStorage.setItem(KEY, JSON.stringify(next));
  return next;
}

export async function clearOfflineNews() {
  await AsyncStorage.removeItem(KEY);
}

type ShareInput = { title: string; summary: string; source: string; locality_name?: string | null };

function composeMessage({ title, summary, source, locality_name }: ShareInput) {
  const bits = [
    `📰 ${title}`,
    summary,
    locality_name ? `📍 ${locality_name}` : null,
    `— via ${source} on InfraJagat`,
  ].filter(Boolean);
  return bits.join("\n\n");
}

export async function shareNewsNative(input: ShareInput) {
  const message = composeMessage(input);
  try {
    await Share.share({ title: input.title, message });
    return true;
  } catch {
    return false;
  }
}

export async function shareOnWhatsApp(input: ShareInput) {
  const message = composeMessage(input);
  const url = `whatsapp://send?text=${encodeURIComponent(message)}`;
  const can = await Linking.canOpenURL(url);
  if (!can) {
    // Fallback: web whatsapp
    return Linking.openURL(`https://api.whatsapp.com/send?text=${encodeURIComponent(message)}`);
  }
  return Linking.openURL(url);
}

export async function shareOnInstagram(input: ShareInput) {
  // Instagram has no public text-share URL; copy caption + open Instagram DMs if possible.
  const message = composeMessage(input);
  const can = Platform.OS !== "web" ? await Linking.canOpenURL("instagram://library") : false;
  if (can) {
    try { await Linking.openURL("instagram://library"); } catch {}
  } else {
    try { await Linking.openURL("https://www.instagram.com/"); } catch {}
  }
  // Also offer the native share sheet so user can pick Instagram Stories / Direct
  if (await Sharing.isAvailableAsync()) {
    // Sharing.shareAsync requires a file URI; use the generic Share API instead
    await Share.share({ title: input.title, message });
  }
  return true;
}
