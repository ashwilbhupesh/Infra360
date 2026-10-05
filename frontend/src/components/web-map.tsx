import React, { useEffect, useMemo, useRef } from "react";
import { View, StyleSheet, Platform } from "react-native";
import { WebView, WebViewMessageEvent } from "react-native-webview";
import { colors } from "@/src/theme";
import { heatColor } from "@/src/utils/heat";

export type WebMapMarker = {
  id: string;
  lat: number;
  lng: number;
  label: string;
  active?: boolean;
};

export type WebMapHeatPoint = {
  id: string;
  lat: number;
  lng: number;
  intensity: number; // 0..1
  label?: string;
};

type Props = {
  center: { lat: number; lng: number };
  zoom?: number;
  markers?: WebMapMarker[];
  heatPoints?: WebMapHeatPoint[];
  heat?: boolean;
  highlightedId?: string | null;
  onMarkerPress?: (id: string) => void;
  onReady?: () => void;
};

/**
 * Pure WebView + Leaflet (OpenStreetMap) map.
 * Works on Android, iOS and Web without ANY API keys.
 */
export function WebMap({
  center,
  zoom = 12,
  markers = [],
  heatPoints = [],
  heat = false,
  highlightedId = null,
  onMarkerPress,
  onReady,
}: Props) {
  const webRef = useRef<WebView>(null);
  const readyRef = useRef(false);

  const html = useMemo(
    () => `
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<style>
  html,body,#map { margin:0; padding:0; width:100%; height:100%; background:#f4ead5; }
  .pin {
    display:inline-block; padding:4px 8px; background:${colors.surface};
    border:1.5px solid ${colors.brand}; border-radius:999px;
    color:${colors.brand}; font-size:11px; font-weight:700;
    font-family:-apple-system,Roboto,Helvetica,Arial,sans-serif;
    white-space:nowrap; box-shadow:0 2px 6px rgba(0,0,0,.18);
    transform:translate(-50%,-50%);
  }
  .pin.active {
    background:${colors.brandPrimary}; border-color:${colors.brandPrimary};
    color:${colors.onBrandPrimary}; transform:translate(-50%,-50%) scale(1.15);
    z-index:9999;
  }
  .leaflet-pane .leaflet-marker-icon { background:transparent !important; border:none !important; }
</style>
</head>
<body>
<div id="map"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
  var map = L.map('map', { zoomControl: false, attributionControl: false })
            .setView([${center.lat}, ${center.lng}], ${zoom});
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map);
  var markerLayer = L.layerGroup().addTo(map);
  var heatLayer = L.layerGroup().addTo(map);
  function post(msg){ if(window.ReactNativeWebView){ window.ReactNativeWebView.postMessage(JSON.stringify(msg)); } }
  function setMarkers(items, highlightedId){
    markerLayer.clearLayers();
    items.forEach(function(m){
      var el = L.divIcon({
        className:'pin'+(m.id===highlightedId?' active':''),
        html:'<span class="pin'+(m.id===highlightedId?' active':'')+'">'+m.label+'</span>',
        iconSize:[1,1], iconAnchor:[0,0]
      });
      var mk = L.marker([m.lat,m.lng],{icon:el}).addTo(markerLayer);
      mk.on('click',function(){ post({type:'marker', id:m.id}); });
    });
  }
  function setHeat(points, show){
    heatLayer.clearLayers();
    if(!show) return;
    points.forEach(function(p){
      var color = p.color || '#C25934';
      L.circle([p.lat,p.lng],{
        radius:1500, color:p.strokeColor||color, weight:1,
        fillColor:color, fillOpacity:0.45
      }).addTo(heatLayer);
    });
  }
  function focus(lat,lng,zoom){ map.setView([lat,lng], zoom || map.getZoom(), { animate:true, duration:0.6 }); }
  window.__setMarkers = setMarkers;
  window.__setHeat = setHeat;
  window.__focus = focus;
  // Signal ready
  post({type:'ready'});
</script>
</body>
</html>`,
    // Only build HTML once; data flows via injectedJavaScript below
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  // Push new data whenever props change
  useEffect(() => {
    if (!readyRef.current) return;
    const colored = heatPoints.map((p) => ({
      ...p,
      color: heatColor(p.intensity, 0.45),
      strokeColor: heatColor(p.intensity, 0.9),
    }));
    const script = `
      try {
        window.__setMarkers(${JSON.stringify(markers)}, ${JSON.stringify(highlightedId)});
        window.__setHeat(${JSON.stringify(colored)}, ${heat});
      } catch(e) {}
      true;
    `;
    webRef.current?.injectJavaScript(script);
  }, [markers, heatPoints, heat, highlightedId]);

  // Pan to highlighted marker when it changes
  useEffect(() => {
    if (!readyRef.current || !highlightedId) return;
    const m = markers.find((x) => x.id === highlightedId);
    if (m) {
      webRef.current?.injectJavaScript(`try { window.__focus(${m.lat}, ${m.lng}, 15); } catch(e){} true;`);
    }
  }, [highlightedId, markers]);

  const handleMessage = (ev: WebViewMessageEvent) => {
    try {
      const data = JSON.parse(ev.nativeEvent.data);
      if (data.type === "ready") {
        readyRef.current = true;
        // flush initial data
        const colored = heatPoints.map((p) => ({
          ...p,
          color: heatColor(p.intensity, 0.45),
          strokeColor: heatColor(p.intensity, 0.9),
        }));
        webRef.current?.injectJavaScript(
          `try { window.__setMarkers(${JSON.stringify(markers)}, ${JSON.stringify(highlightedId)}); window.__setHeat(${JSON.stringify(colored)}, ${heat}); } catch(e) {} true;`
        );
        onReady?.();
      } else if (data.type === "marker" && onMarkerPress) {
        onMarkerPress(data.id);
      }
    } catch {}
  };

  return (
    <View style={styles.wrap}>
      <WebView
        ref={webRef}
        originWhitelist={["*"]}
        source={{ html }}
        onMessage={handleMessage}
        javaScriptEnabled
        domStorageEnabled
        setSupportMultipleWindows={false}
        style={styles.web}
        androidLayerType="hardware"
        startInLoadingState={false}
        allowFileAccess
        mixedContentMode="always"
        {...(Platform.OS === "android" ? { nestedScrollEnabled: true } : {})}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: "#f4ead5" },
  web: { flex: 1, backgroundColor: "transparent" },
});
