import React from "react";
import { View, Text, StyleSheet } from "react-native";
import Svg, { Path, Line, Circle, Text as SvgText } from "react-native-svg";
import { colors, spacing } from "@/src/theme";

type Point = { year: number; listing: number; govt: number; est_low: number; est_high: number };

export function PriceChart({ data, width = 320, height = 180 }: { data: Point[]; width?: number; height?: number }) {
  if (!data || data.length === 0) return null;
  const padL = 40, padR = 12, padT = 16, padB = 24;
  const w = width - padL - padR;
  const h = height - padT - padB;
  const xs = data.map(d => d.year);
  const allVals = data.map(d => d.listing);
  const yMin = Math.min(...allVals) * 0.9;
  const yMax = Math.max(...allVals) * 1.05;
  const xAt = (i: number) => padL + (w * i) / (data.length - 1);
  const yAt = (v: number) => padT + h - ((v - yMin) / (yMax - yMin)) * h;

  const line = (arr: number[]) => arr.map((v, i) => `${i === 0 ? "M" : "L"} ${xAt(i)} ${yAt(v)}`).join(" ");

  return (
    <View>
      <Svg width={width} height={height}>
        {/* Y grid */}
        {[0, 0.25, 0.5, 0.75, 1].map(t => (
          <Line key={t} x1={padL} x2={padL + w} y1={padT + h - t * h} y2={padT + h - t * h} stroke={colors.divider} strokeWidth={0.5} />
        ))}
        {/* listing line */}
        <Path d={line(data.map(d => d.listing))} stroke={colors.brand} strokeWidth={2.5} fill="none" />
        {data.map((d, i) => (
          <Circle key={d.year} cx={xAt(i)} cy={yAt(d.listing)} r={3} fill={colors.brand} />
        ))}
        {/* X labels */}
        {xs.map((y, i) => (
          <SvgText key={y} x={xAt(i)} y={height - 6} fill={colors.muted} fontSize={10} textAnchor="middle">{y}</SvgText>
        ))}
        {/* Y labels */}
        {[yMin, (yMin + yMax) / 2, yMax].map((v, i) => (
          <SvgText key={i} x={padL - 4} y={yAt(v) + 3} fill={colors.muted} fontSize={9} textAnchor="end">
            ₹{Math.round(v / 1000)}k
          </SvgText>
        ))}
      </Svg>
      <View style={styles.legend}>
        <LegendDot color={colors.brand} label="Listing" />
      </View>
    </View>
  );
}

function LegendDot({ color, label, opacity = 1, dashed = false }: { color: string; label: string; opacity?: number; dashed?: boolean }) {
  return (
    <View style={styles.legendItem}>
      <View style={{ width: 14, height: 3, backgroundColor: color, opacity, borderRadius: 2, borderStyle: dashed ? "dashed" : "solid" }} />
      <Text style={styles.legendText}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  legend: { flexDirection: "row", gap: spacing.md, marginTop: spacing.sm, flexWrap: "wrap" },
  legendItem: { flexDirection: "row", alignItems: "center", gap: 4 },
  legendText: { fontSize: 11, color: colors.muted, fontWeight: "500" },
});
