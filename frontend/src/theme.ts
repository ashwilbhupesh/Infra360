import { useMemo } from "react";
import { Appearance, StyleSheet, useColorScheme } from "react-native";

export type ColorScheme = "light" | "dark";

const light = {
  surface: "#FFFFF0",
  onSurface: "#1A1C1E",
  surfaceSecondary: "#F8F8F2",
  onSurfaceSecondary: "#1A1C1E",
  surfaceTertiary: "#EBEBE6",
  onSurfaceTertiary: "#1A1C1E",
  surfaceInverse: "#1A1C1E",
  onSurfaceInverse: "#FFFFF0",
  muted: "#686E74",

  brand: "#0A192F",
  onBrand: "#FFFFFF",
  brandPrimary: "#C25934",
  onBrandPrimary: "#FFFFFF",
  brandSecondary: "#0A192F",
  onBrandSecondary: "#FFFFFF",
  brandTertiary: "#EAE3D9",
  onBrandTertiary: "#1A1C1E",

  success: "#2E6D4D",
  onSuccess: "#FFFFFF",
  warning: "#B8860B",
  onWarning: "#FFFFFF",
  error: "#8B0000",
  onError: "#FFFFFF",
  info: "#0A192F",
  onInfo: "#FFFFFF",

  border: "#EBEBE6",
  borderStrong: "#D6D6D0",
  divider: "#EBEBE6",
};

const dark: typeof light = {
  surface: "#1A1C1E",
  onSurface: "#FFFFF0",
  surfaceSecondary: "#25282B",
  onSurfaceSecondary: "#FFFFF0",
  surfaceTertiary: "#303438",
  onSurfaceTertiary: "#FFFFF0",
  surfaceInverse: "#FFFFF0",
  onSurfaceInverse: "#1A1C1E",
  muted: "#9E9C99",

  brand: "#0A192F",
  onBrand: "#FFFFFF",
  brandPrimary: "#C25934",
  onBrandPrimary: "#FFFFFF",
  brandSecondary: "#EAE3D9",
  onBrandSecondary: "#1A1C1E",
  brandTertiary: "#2E3338",
  onBrandTertiary: "#F8F8F2",

  success: "#2E6D4D",
  onSuccess: "#FFFFFF",
  warning: "#B8860B",
  onWarning: "#FFFFFF",
  error: "#8B0000",
  onError: "#FFFFFF",
  info: "#0A192F",
  onInfo: "#FFFFFF",

  border: "#303438",
  borderStrong: "#464A4F",
  divider: "#303438",
};

export type ThemeColors = typeof light;
export const defaultScheme = "light" satisfies ColorScheme;
export const themes: { light: ThemeColors; dark?: ThemeColors } = { light, dark };

export function setColorScheme(scheme: ColorScheme | null) {
  Appearance.setColorScheme?.(scheme ?? "unspecified");
}
setColorScheme?.(themes.dark ? null : defaultScheme);

// Force light for premium map aesthetic
setColorScheme?.("light");

export function useTheme(): { scheme: ColorScheme; colors: ThemeColors } {
  const system = useColorScheme();
  const scheme: ColorScheme = "light"; // force premium palette
  return { scheme, colors: themes[scheme] ?? themes.light };
}

export function makeStyles<T extends StyleSheet.NamedStyles<T> | StyleSheet.NamedStyles<any>>(
  factory: (colors: ThemeColors) => T & StyleSheet.NamedStyles<any>,
): () => T {
  return function useStyles(): T {
    const { colors } = useTheme();
    return useMemo(() => StyleSheet.create(factory(colors)), [colors]);
  };
}

export const colors = themes.light;

export const spacing = { xs: 4, sm: 8, md: 12, lg: 16, xl: 24, xxl: 32, xxxl: 48 };
export const radius = { sm: 6, md: 12, lg: 20, pill: 999 };
export const shadow = {
  card: {
    shadowColor: "#0A192F",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 2,
  },
  floating: {
    shadowColor: "#0A192F",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.14,
    shadowRadius: 14,
    elevation: 6,
  },
};
