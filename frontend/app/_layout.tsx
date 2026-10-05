import { QueryClientProvider } from "@tanstack/react-query";
import { Stack, usePathname } from "expo-router";
import { View, LogBox, Platform } from "react-native";
import { KeyboardProvider } from "react-native-keyboard-controller";
import { GestureHandlerRootView } from "react-native-gesture-handler";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { StatusBar } from "expo-status-bar";

import { ErrorBoundary } from "@/src/components/error-boundary";
import { queryClient } from "@/src/query-client";
import { AuthProvider } from "@/src/auth-context";
import { PersistentTabBar } from "@/src/components/persistent-tab-bar";

LogBox.ignoreAllLogs(true);

// Routes where we never show the floating tab bar.
const HIDDEN_PREFIXES = [
  "/onboarding",
  "/otp",
  "/list-property",
];

function AppShell() {
  const pathname = usePathname() ?? "";
  // Hide on auth / modal flows
  const hideOnScreen = HIDDEN_PREFIXES.some((p) => pathname === p || pathname.startsWith(p + "/"));
  // Hide on root "/" (index redirect)
  const atRoot = pathname === "/" || pathname === "";
  // Hide inside (tabs) group — their own tab bar is already rendered there.
  // Expo Router's usePathname strips the group prefix, so (tabs) screens
  // resolve to "/explore", "/agents", "/news", "/market", "/saved".
  const TAB_PATHS = ["/explore", "/agents", "/news", "/market", "/saved"];
  const insideTabs = TAB_PATHS.some((t) => pathname === t || pathname.startsWith(t + "?"));
  const show = !hideOnScreen && !atRoot && !insideTabs;

  return (
    <View style={{ flex: 1 }}>
      <View style={{ flex: 1 }}>
        <Stack screenOptions={{ headerShown: false, animation: Platform.OS === "ios" ? "default" : "fade" }}>
          <Stack.Screen name="index" />
          <Stack.Screen name="onboarding" />
          <Stack.Screen name="(tabs)" />
          <Stack.Screen name="property/[id]" options={{ presentation: "card" }} />
          <Stack.Screen name="locality/[id]" options={{ presentation: "card" }} />
          <Stack.Screen name="list-property" options={{ presentation: "modal" }} />
        </Stack>
      </View>
      {show ? <PersistentTabBar /> : null}
    </View>
  );
}

export default function RootLayout() {
  return (
    <ErrorBoundary>
      <SafeAreaProvider>
        <GestureHandlerRootView style={{ flex: 1 }}>
          <QueryClientProvider client={queryClient}>
            <KeyboardProvider>
              <AuthProvider>
                <StatusBar style="dark" />
                <AppShell />
              </AuthProvider>
            </KeyboardProvider>
          </QueryClientProvider>
        </GestureHandlerRootView>
      </SafeAreaProvider>
    </ErrorBoundary>
  );
}
