// Recently viewed - AsyncStorage backed history of property IDs
import AsyncStorage from "@react-native-async-storage/async-storage";

const KEY = "infralocal.history";
const MAX = 40;

export async function getHistory(): Promise<string[]> {
  try {
    const raw = await AsyncStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export async function addHistory(id: string) {
  if (!id) return;
  const cur = await getHistory();
  const next = [id, ...cur.filter(x => x !== id)].slice(0, MAX);
  await AsyncStorage.setItem(KEY, JSON.stringify(next));
}

export async function clearHistory() {
  await AsyncStorage.removeItem(KEY);
}
