import { Linking, Platform } from "react-native";

function cleanPhone(phone: string) {
  return phone.replace(/[^\d]/g, "");
}

export async function openWhatsApp(phone: string, message?: string) {
  const p = cleanPhone(phone);
  if (!p) return;
  const text = message ? encodeURIComponent(message) : "";
  const nativeUrl = `whatsapp://send?phone=${p}${text ? `&text=${text}` : ""}`;
  const webUrl = `https://wa.me/${p}${text ? `?text=${text}` : ""}`;
  try {
    if (Platform.OS === "web") {
      window.open(webUrl, "_blank");
      return;
    }
    const supported = await Linking.canOpenURL(nativeUrl);
    if (supported) {
      await Linking.openURL(nativeUrl);
    } else {
      await Linking.openURL(webUrl);
    }
  } catch {
    Linking.openURL(webUrl).catch(() => {});
  }
}

export function openTel(phone: string) {
  const p = cleanPhone(phone);
  if (!p) return;
  Linking.openURL(`tel:+${p.length === 10 ? "91" + p : p}`).catch(() => {});
}
