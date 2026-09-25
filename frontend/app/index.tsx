import { Redirect } from "expo-router";
import { useAuth } from "@/src/auth-context";
import { View, ActivityIndicator } from "react-native";
import { colors } from "@/src/theme";

export default function Index() {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.surface, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator color={colors.brand} />
      </View>
    );
  }
  return user ? <Redirect href="/(tabs)/explore" /> : <Redirect href="/onboarding" />;
}
