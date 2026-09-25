import AsyncStorage from "@react-native-async-storage/async-storage";

const BASE = process.env.EXPO_PUBLIC_BACKEND_URL || "";

export const api = {
  async get<T>(path: string): Promise<T> {
    const res = await fetch(`${BASE}/api${path}`);
    if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
    return res.json();
  },
  async post<T>(path: string, body: any): Promise<T> {
    const res = await fetch(`${BASE}/api${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`POST ${path} failed: ${res.status}`);
    return res.json();
  },
};

export const backendUrl = BASE;

export const USER_KEY = "infralocal.user";

export type CurrentUser = { id: string; name: string; mobile: string; area?: string; profession?: string };

export async function getUser(): Promise<CurrentUser | null> {
  const raw = await AsyncStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
}

export async function saveUser(user: CurrentUser) {
  await AsyncStorage.setItem(USER_KEY, JSON.stringify(user));
}

export async function clearUser() {
  await AsyncStorage.removeItem(USER_KEY);
}
