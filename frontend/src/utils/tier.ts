import { colors } from "@/src/theme";

export type Tier = "Gold" | "Silver" | "Bronze" | "Unverified";

export function tierColor(tier?: string): string {
  switch (tier) {
    case "Gold": return "#C9A227";
    case "Silver": return "#8892A1";
    case "Bronze": return "#A66A3D";
    default: return colors.muted;
  }
}

export function tierBgColor(tier?: string): string {
  switch (tier) {
    case "Gold": return "rgba(201, 162, 39, 0.14)";
    case "Silver": return "rgba(136, 146, 161, 0.14)";
    case "Bronze": return "rgba(166, 106, 61, 0.14)";
    default: return colors.surfaceSecondary;
  }
}
