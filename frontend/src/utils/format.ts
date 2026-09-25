// Indian number formatting utilities

export function formatINR(value: number): string {
  if (!isFinite(value) || value <= 0) return "\u20B90";
  if (value >= 1_00_00_000) {
    const cr = value / 1_00_00_000;
    return `\u20B9${cr.toFixed(cr >= 10 ? 1 : 2)} Cr`;
  }
  if (value >= 1_00_000) {
    const lk = value / 1_00_000;
    return `\u20B9${lk.toFixed(lk >= 10 ? 0 : 1)} L`;
  }
  return `\u20B9${indianComma(value)}`;
}

export function indianComma(value: number): string {
  const s = Math.round(value).toString();
  if (s.length <= 3) return s;
  const last3 = s.slice(-3);
  const rest = s.slice(0, -3);
  return rest.replace(/\B(?=(\d{2})+(?!\d))/g, ",") + "," + last3;
}

export function perUnit(value: number, unit: string): string {
  return `\u20B9${indianComma(value)}/${unit}`;
}

export function formatRange(low: number, high: number): string {
  return `${formatINR(low)} \u2013 ${formatINR(high)}`;
}
