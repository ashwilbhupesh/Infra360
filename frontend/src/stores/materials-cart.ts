import { create } from "zustand";
import AsyncStorage from "@react-native-async-storage/async-storage";

export type CartProduct = {
  id: string;
  store_id: string;
  store_name: string;
  store_phone?: string;
  name: string;
  brand?: string;
  image?: string;
  unit?: string;
  price: number;
  category_id?: string;
};

export type CartLine = CartProduct & { qty: number };

type State = {
  items: Record<string, CartLine>; // keyed by product id
  hydrated: boolean;
};

type Actions = {
  hydrate: () => Promise<void>;
  add: (product: CartProduct, qty?: number) => void;
  increment: (productId: string) => void;
  decrement: (productId: string) => void;
  remove: (productId: string) => void;
  clear: () => void;
  qtyOf: (productId: string) => number;
  totalItems: () => number;
  totalAmount: () => number;
  groupedByStore: () => Array<{
    store_id: string;
    store_name: string;
    store_phone?: string;
    items: CartLine[];
    subtotal: number;
  }>;
};

const KEY = "infrajagat.materials.cart.v1";

const persist = async (items: Record<string, CartLine>) => {
  try {
    await AsyncStorage.setItem(KEY, JSON.stringify(items));
  } catch {}
};

export const useMaterialsCart = create<State & Actions>((set, get) => ({
  items: {},
  hydrated: false,

  hydrate: async () => {
    try {
      const raw = await AsyncStorage.getItem(KEY);
      if (raw) set({ items: JSON.parse(raw) || {}, hydrated: true });
      else set({ hydrated: true });
    } catch {
      set({ hydrated: true });
    }
  },

  add: (product, qty = 1) => {
    const items = { ...get().items };
    const existing = items[product.id];
    items[product.id] = { ...product, qty: (existing?.qty ?? 0) + qty };
    set({ items });
    persist(items);
  },

  increment: (productId) => {
    const items = { ...get().items };
    if (!items[productId]) return;
    items[productId] = { ...items[productId], qty: items[productId].qty + 1 };
    set({ items });
    persist(items);
  },

  decrement: (productId) => {
    const items = { ...get().items };
    const cur = items[productId];
    if (!cur) return;
    if (cur.qty <= 1) {
      delete items[productId];
    } else {
      items[productId] = { ...cur, qty: cur.qty - 1 };
    }
    set({ items });
    persist(items);
  },

  remove: (productId) => {
    const items = { ...get().items };
    delete items[productId];
    set({ items });
    persist(items);
  },

  clear: () => {
    set({ items: {} });
    persist({});
  },

  qtyOf: (productId) => get().items[productId]?.qty ?? 0,

  totalItems: () =>
    Object.values(get().items).reduce((sum, l) => sum + l.qty, 0),

  totalAmount: () =>
    Object.values(get().items).reduce((sum, l) => sum + l.qty * l.price, 0),

  groupedByStore: () => {
    const groups: Record<string, {
      store_id: string;
      store_name: string;
      store_phone?: string;
      items: CartLine[];
      subtotal: number;
    }> = {};
    for (const line of Object.values(get().items)) {
      const g = (groups[line.store_id] ||= {
        store_id: line.store_id,
        store_name: line.store_name,
        store_phone: line.store_phone,
        items: [],
        subtotal: 0,
      });
      g.items.push(line);
      g.subtotal += line.price * line.qty;
    }
    return Object.values(groups);
  },
}));
