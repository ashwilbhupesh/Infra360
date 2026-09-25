// Returns a heatmap color for intensity 0..1
// Uses a smooth gradient: green (low) -> yellow -> orange -> red (high)
export function heatColor(intensity: number, alpha = 0.65): string {
  const t = Math.max(0, Math.min(1, intensity));
  let r: number, g: number, b: number;
  if (t < 0.5) {
    // green -> yellow
    const k = t / 0.5;
    r = Math.round(46 + (245 - 46) * k);
    g = Math.round(160 + (200 - 160) * k);
    b = Math.round(67 + (30 - 67) * k);
  } else {
    // yellow -> red
    const k = (t - 0.5) / 0.5;
    r = Math.round(245 + (200 - 245) * k);
    g = Math.round(200 + (35 - 200) * k);
    b = Math.round(30 + (25 - 30) * k);
  }
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

export function heatLabel(intensity: number): string {
  if (intensity < 0.25) return "Value";
  if (intensity < 0.5) return "Emerging";
  if (intensity < 0.75) return "Premium";
  return "Prime";
}
