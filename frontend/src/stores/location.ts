import AsyncStorage from "@react-native-async-storage/async-storage";
import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

export type SavedAddress = {
  id: string;
  label: string;        // Home, Work, Sarthak's House, etc.
  city: string;         // Jaipur
  area: string;         // Jagatpura, Vaishali Nagar
  address_line?: string;
  pincode?: string;
  lat?: number;
  lng?: number;
  tag?: "home" | "work" | "other";
};

type LocationState = {
  active_id: string | null;
  addresses: SavedAddress[];
  current_detected: SavedAddress | null;
  _hydrated: boolean;
  setActive: (id: string) => void;
  addAddress: (addr: Omit<SavedAddress, "id">) => string;
  updateAddress: (id: string, patch: Partial<SavedAddress>) => void;
  removeAddress: (id: string) => void;
  setDetected: (addr: SavedAddress | null) => void;
  getActive: () => SavedAddress | null;
  markHydrated: () => void;
};

const DEFAULT_JAIPUR: SavedAddress = {
  id: "addr-default-jaipur",
  label: "Jaipur (default)",
  city: "Jaipur",
  area: "City-wide",
  tag: "other",
};

export const useLocationStore = create<LocationState>()(
  persist(
    (set, get) => ({
      active_id: DEFAULT_JAIPUR.id,
      addresses: [DEFAULT_JAIPUR],
      current_detected: null,
      _hydrated: false,
      setActive: (id) => set({ active_id: id }),
      addAddress: (addr) => {
        const id = `addr-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
        set((s) => ({ addresses: [...s.addresses, { id, ...addr }], active_id: id }));
        return id;
      },
      updateAddress: (id, patch) => set((s) => ({
        addresses: s.addresses.map((a) => (a.id === id ? { ...a, ...patch } : a)),
      })),
      removeAddress: (id) => set((s) => {
        const next = s.addresses.filter((a) => a.id !== id);
        const active = s.active_id === id ? (next[0]?.id || null) : s.active_id;
        return { addresses: next, active_id: active };
      }),
      setDetected: (addr) => set({ current_detected: addr }),
      getActive: () => {
        const s = get();
        return s.addresses.find((a) => a.id === s.active_id) || s.current_detected || null;
      },
      markHydrated: () => set({ _hydrated: true }),
    }),
    {
      name: "infrajagat.location.v1",
      storage: createJSONStorage(() => AsyncStorage),
      onRehydrateStorage: () => (state) => { state?.markHydrated(); },
    },
  ),
);

export function activeAddress(): SavedAddress | null {
  return useLocationStore.getState().getActive();
}
