import { Tabs } from "expo-router";
import { Platform } from "react-native";
import Icon from "@react-native-vector-icons/ionicons";
import { colors } from "@/src/theme";

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.brand,
        tabBarInactiveTintColor: colors.muted,
        tabBarStyle: {
          backgroundColor: colors.surface,
          borderTopColor: colors.border,
          ...(Platform.OS === "web" ? { height: 64 } : {}),
        },
        tabBarItemStyle: { alignSelf: "center" },
        tabBarLabelStyle: { fontSize: 10, fontWeight: "600" },
      }}
    >
      <Tabs.Screen
        name="explore"
        options={{
          title: "Explore",
          tabBarIcon: ({ color, size }) => <Icon name="map-outline" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="agents"
        options={{
          title: "Experts",
          tabBarIcon: ({ color, size }) => <Icon name="people-outline" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="news"
        options={{
          title: "News",
          tabBarIcon: ({ color, size }) => <Icon name="newspaper-outline" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="market"
        options={{
          title: "Market",
          tabBarIcon: ({ color, size }) => <Icon name="storefront-outline" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="saved"
        options={{
          title: "Saved",
          tabBarIcon: ({ color, size }) => <Icon name="heart-outline" size={size} color={color} />,
        }}
      />
    </Tabs>
  );
}
