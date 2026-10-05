import { create } from "zustand";

export type VoiceLine = {
  product_id: string; name: string; brand?: string; image?: string; unit?: string;
  price: number; mrp?: number; store_id: string; store_name?: string; store_area?: string;
  qty: number; subtotal: number;
  query?: { name?: string; brand?: string; raw?: string; quantity?: number; unit?: string };
};

export type VoiceDraft = {
  source: "voice" | "scan";
  transcript?: string;
  translation?: string;
  items: VoiceLine[];
  unmatched: any[];
  total_estimated: number;
  created_at: string;
};

type S = {
  draft: VoiceDraft | null;
  setDraft: (d: VoiceDraft | null) => void;
  updateQty: (index: number, qty: number) => void;
  removeLine: (index: number) => void;
};

export const useVoiceDraft = create<S>((set) => ({
  draft: null,
  setDraft: (d) => set({ draft: d }),
  updateQty: (index, qty) => set((s) => {
    if (!s.draft) return s;
    const next = [...s.draft.items];
    const q = Math.max(0, qty);
    next[index] = { ...next[index], qty: q, subtotal: q * next[index].price };
    const total = next.reduce((sum, l) => sum + (l.subtotal || 0), 0);
    return { draft: { ...s.draft, items: next, total_estimated: total } };
  }),
  removeLine: (index) => set((s) => {
    if (!s.draft) return s;
    const next = s.draft.items.filter((_, i) => i !== index);
    const total = next.reduce((sum, l) => sum + (l.subtotal || 0), 0);
    return { draft: { ...s.draft, items: next, total_estimated: total } };
  }),
}));
