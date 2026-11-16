import sys, json, re, math
P, WJ, PJ = sys.argv[1], sys.argv[2], sys.argv[3]
VIDEO_END = 126.2
END = 131.7
exec(open(__file__.replace("build.py", "base_part.py")).read())  # BASE, INSERTS, rel(), scene()

# ---------- captions: Parakeet timings, spellings checked against Whisper ----------
FIX = {"Jappus": "Jaipur", "Ajmeer,": "Ajmer,", "Torque": "Tonk", "Jepu's": "Jaipur's", "Ajmir": "Ajmer", "Bhakrata": "Bhankrota–", "Mahapura": "Mahapura",
       "Shabdaspura": "Shivdaspura", "Bagrana": "Bagrana", "good": "goods", "Nadan": "Northern", "Kishangar": "Kishangarh", "Dhyajme": "the Ajmer",
       "Says": "SEZ", "Shepdaspura": "Shivdaspura–", "site,": "side,", "Belt": "belt", "Junction": "junction", "Nadin": "Northern", "Kalwa": "Kalwar–", "Jobny": "Jobner", "Dhabri": "Dabri", "Research": "research", "99km": "99 km"}
EM = {"ring", "road", "ajmer", "tonk", "agra", "crowded", "around", "south", "47", "km", "bhankrota–", "mahapura", "shivdaspura", "bagrana", "northern",
      "99", "bagru", "kishangarh", "bandikui", "expressway", "mahindra", "sez", "sitapura", "chitroli", "kalwar–", "jobner", "rampura", "dabri", "chomu",
      "exits", "jobs", "industries", "housing", "logistics", "opportunity"}
heard = json.load(open(WJ))
toks = []
for w in heard:
    t = FIX.get(w["text"], w["text"])
    if w["text"] == "Mahapura" and 66 < w["start"] < 67: t = "Mahapura–"
    k = re.sub(r"[^\w:%–-]", "", t.lower())
    toks.append({"t": t, "s": round(w["start"], 3), "em": k in EM or k.rstrip(".,") in EM})
def glen(g): return len(" ".join(w["t"] for w in g))
groups, cur = [], []
for i, w in enumerate(toks):
    cur.append(w); nxt = toks[i + 1] if i + 1 < len(toks) else None
    brk = nxt is None or glen(cur + [nxt]) > 30 or w["t"][-1] in ".?" or (w["t"][-1] == "," and glen(cur) >= 14) or (nxt and nxt["s"] - w["s"] > 1.3)
    if w["t"].endswith("–"): brk = False
    if brk: groups.append(cur); cur = []
merged = []
for g in groups:
    if merged and len(g) == 1 and glen(merged[-1] + g) <= 36 and merged[-1][-1]["t"][-1] not in ".?": merged[-1] += g
    else: merged.append(g)
groups = merged
caps = []
for gi, g in enumerate(groups):
    nxt = groups[gi + 1][0]["s"] - 0.04 if gi + 1 < len(groups) else VIDEO_END
    last = g[-1]["s"] + max(0.35, 0.06 * len(g[-1]["t"]))
    caps.append((round(max(0.08, g[0]["s"] - 0.06), 2), round(min(nxt, last + 0.55), 2), g))
def ctext(g): return "".join(w["t"] + ("" if w["t"].endswith("–") or k == len(g) - 1 else " ") for k, w in enumerate(g))
json.dump({"captions": [{"start": a, "end": b, "text": ctext(g)} for a, b, g in caps]}, open(f"{P}/../captions.json", "w"), indent=1, ensure_ascii=False)

# ---------- map geometry: km from the Walled City centre; positions from OpenStreetMap (Nominatim) ----------
PL = json.load(open(PJ))
APPROX = {"bhankrota": (26.862, 75.676), "chitroli": (26.840, 75.585), "bagrana": (26.885, 75.930), "cscheme": (26.906, 75.803)}
def ll(k): return tuple(APPROX[k]) if k in APPROX else (PL[k][0], PL[k][1])
LAT0, LON0 = 26.924, 75.827
def km(lat, lon): return ((lon - LON0) * 99.25, (LAT0 - lat) * 111.0)
def K(k): return km(*ll(k))
WALL = [km(*p) for p in [(26.9266, 75.8079), (26.9335, 75.8112), (26.9398, 75.8240), (26.9385, 75.8352), (26.9305, 75.8440), (26.9153, 75.8462), (26.9153, 75.8243), (26.9176, 75.8166)]]
ROADS = {
  "ajmer": [K("ajmerigate"), km(26.912, 75.795), K("sodala"), km(26.888, 75.745), K("bhankrota"), K("mahapura"), km(26.835, 75.630), K("bagru"), km(26.780, 75.440)],
  "tonk": [K("sanganerigate"), K("rambagh"), km(26.868, 75.799), km(26.830, 75.806), K("sitapura"), K("shivdaspura"), K("chaksu")],
  "sikar": [K("chandpole"), km(26.950, 75.792), K("vki"), K("rampuradabri"), K("chomu"), km(27.30, 75.68)],
  "delhi": [K("hawa"), K("jalmahal"), K("amer"), km(27.03, 75.89), K("achrol"), km(27.25, 75.98)],
  "agra": [km(26.913, 75.846), km(26.900, 75.880), K("bagrana"), K("kanota"), K("bassi"), km(26.83, 76.12)],
  "sring": [K("bhankrota"), km(26.807, 75.700), km(26.770, 75.780), km(26.745, 75.850), K("goner"), km(26.840, 75.940), K("bagrana")],
  "nring": [K("chitroli"), km(26.930, 75.570), K("kalwar"), km(27.075, 75.640), K("rampuradabri"), km(27.135, 75.830), km(27.110, 75.950), km(27.020, 75.985), km(26.940, 75.960), K("bagrana")],
}
CORE = [km(26.995, 75.770), km(26.990, 75.800), km(26.960, 75.840), km(26.925, 75.865), km(26.880, 75.870), km(26.830, 75.845), km(26.770, 75.840),
        km(26.800, 75.790), km(26.815, 75.760), km(26.850, 75.730), km(26.890, 75.700), km(26.925, 75.715), km(26.955, 75.750)]
def smooth(pts, closed=True):
    n = len(pts); d = f"M{pts[0][0]:.3f} {pts[0][1]:.3f}"
    for i in (range(n) if closed else range(n - 1)):
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[0]; p1 = pts[i]; p2 = pts[(i + 1) % n]; p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else pts[-1]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6); c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.3f} {c1[1]:.3f} {c2[0]:.3f} {c2[1]:.3f} {p2[0]:.3f} {p2[1]:.3f}"
    return d + (" Z" if closed else "")
def plen(pts): return sum(math.hypot(pts[i+1][0]-pts[i][0], pts[i+1][1]-pts[i][1]) for i in range(len(pts)-1))
MT, MH = 330, 1090  # map band in the frame: y 330 → 1420 (headings above, captions below)
DIMS = ("ajmer", "tonk", "sikar", "delhi", "agra")
RADIALS = {"ajmer": "Ajmer Rd", "tonk": "Tonk Rd", "sikar": "Sikar Rd", "delhi": "Delhi Rd", "agra": "Agra Rd"}

class Map:
    def __init__(self, cid, cx, cy, w):
        self.cid, self.w, self.h = cid, w, w * MH / 1080
        self.vx, self.vy = cx - w / 2, cy - self.h / 2
        self.u = w / 1080
        self.svg, self.html = [], []
    def px(self, p): return ((p[0] - self.vx) / self.u, MT + (p[1] - self.vy) / self.u)
    def base(self, sring=True, nring=True, core=True, wall=True):
        u = self.u
        g = "".join(f'<path d="M{x} {self.vy} V{self.vy + self.h}"/>' for x in range(int(self.vx // 10 * 10), int(self.vx + self.w) + 1, 10)) + "".join(f'<path d="M{self.vx} {y} H{self.vx + self.w}"/>' for y in range(int(self.vy // 10 * 10), int(self.vy + self.h) + 1, 10))
        self.svg.append(f'<g style="stroke:rgba(243,231,211,0.05);stroke-width:{u}">{g}</g>')
        if core: self.svg.append(f'<path d="{smooth(CORE)}" style="fill:rgba(243,231,211,0.07);stroke:rgba(243,231,211,0.18);stroke-width:{1.5*u};stroke-dasharray:{6*u} {6*u}"/>')
        for r in DIMS: self.svg.append(f'<path d="{smooth(ROADS[r], False)}" style="fill:none;stroke:rgba(243,231,211,0.30);stroke-width:{3*u};stroke-linecap:round"/>')
        if sring: self.svg.append(f'<path d="{smooth(ROADS["sring"], False)}" style="fill:none;stroke:rgba(245,176,74,0.35);stroke-width:{4*u}"/>')
        if nring: self.svg.append(f'<path d="{smooth(ROADS["nring"], False)}" style="fill:none;stroke:rgba(160,220,120,0.30);stroke-width:{3*u};stroke-dasharray:{9*u} {7*u}"/>')
        if wall: self.svg.append(f'<path d="{smooth(WALL)}" style="fill:rgba(232,102,74,0.25);stroke:#E8664A;stroke-width:{2.5*u}"/>')
        return self
    def road(self, rid, key, color="#F5B04A", width=8, dash=False):
        u = self.u
        self.svg.append(f'<path id="{self.cid}-{rid}" class="draw" pathLength="1" d="{smooth(ROADS[key], False)}" style="fill:none;stroke:{color};stroke-width:{width*u};stroke-linecap:round;filter:url(#{self.cid}-glow)"/>')
        if dash: self.svg.append(f'<path id="{self.cid}-{rid}d" d="{smooth(ROADS[key], False)}" style="fill:none;stroke:#120D0A;stroke-width:{(width+1)*u};stroke-dasharray:{6*u} {10*u};opacity:0"/>')
        return f"#{self.cid}-{rid}"
    def circle(self, rid, at, r_km, fill="rgba(160,220,120,0.28)", stroke="#B8E07A"):
        p = K(at) if isinstance(at, str) else at
        self.svg.append(f'<circle id="{self.cid}-{rid}" cx="{p[0]:.3f}" cy="{p[1]:.3f}" r="0" style="fill:{fill};stroke:{stroke};stroke-width:{3*self.u};filter:url(#{self.cid}-glow)"/>')
        return (f"#{self.cid}-{rid}", r_km)
    def dot(self, at, big=False, color=None):
        p = K(at) if isinstance(at, str) else at; r = (9 if big else 6) * self.u
        self.svg.append(f'<circle cx="{p[0]:.3f}" cy="{p[1]:.3f}" r="{r:.3f}" style="fill:{color or ("#E3A23B" if big else "#F3E7D3")}"/>')
    def exitmark(self, rid, at):
        p = K(at) if isinstance(at, str) else at; u = self.u
        self.svg.append(f'<g id="{self.cid}-{rid}" style="opacity:0"><circle cx="{p[0]:.3f}" cy="{p[1]:.3f}" r="{16*u:.3f}" style="fill:#120D0A;stroke:#F5B04A;stroke-width:{4*u}"/>'
                        f'<path d="M{p[0]-7*u:.3f} {p[1]:.3f} H{p[0]+7*u:.3f} M{p[0]:.3f} {p[1]-7*u:.3f} V{p[1]+7*u:.3f}" style="stroke:#F5B04A;stroke-width:{3*u}"/></g>')
        return f"#{self.cid}-{rid}"
    def tag(self, rid, text, at, dx=14, dy=-22, amb=False, size=32, right=False):
        x, y = self.px(K(at) if isinstance(at, str) else at); x += dx; y += dy
        wpx = len(text) * size * 0.56 + 48
        if right: x -= wpx + 2 * dx
        x = max(48, min(1080 - 48 - wpx, x)); y = max(MT + 10, min(MT + MH - 70, y))
        self.html.append(f'<div class="tag{" amb" if amb else ""}" id="{self.cid}-{rid}" style="left:{x:.0f}px;top:{y - 90:.0f}px;font-size:{size}px;padding:10px 18px">{text}</div>')
        return f"#{self.cid}-{rid}"
    def chip(self, rid, kicker, text, y=1255):
        self.html.append(f'<div id="{self.cid}-{rid}" style="position:absolute;left:64px;right:64px;top:{y - 90}px;padding:16px 24px;border-radius:18px;background:rgba(18,13,10,0.94);border:1.5px solid #E3A23B">'
                         f'<div class="lbl" style="color:#E3A23B;font-size:26px">{kicker}</div><div style="font-family:Inter,sans-serif;font-weight:700;font-size:33px;line-height:1.2;color:#F3E7D3;margin-top:4px">{text}</div></div>')
        return f"#{self.cid}-{rid}"
    def render(self, start, end, js, note="Schematic · positions: OpenStreetMap"):
        glow = f'<defs><filter id="{self.cid}-glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{5*self.u:.3f}" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
        svg = f'<svg id="{self.cid}-map" style="position:absolute;left:0;top:{MT - 90}px;width:1080px;height:{MH}px" viewBox="{self.vx:.3f} {self.vy:.3f} {self.w:.3f} {self.h:.3f}">{glow}{"".join(self.svg)}</svg>'
        nt = f'<div class="note" style="top:{MT + MH - 90 - 40}px;left:auto;right:64px;font-size:26px;color:rgba(201,183,156,0.85)">{note}</div>' if note else ""
        scene(self.cid, start, end, svg + "".join(self.html) + nt,
              f'      tl.fromTo("#{self.cid}-map", {{ scale: 1.0 }}, {{ scale: 1.04, duration: {round(end - start, 2)}, ease: "none", transformOrigin: "50% 50%" }}, 0);\n' + js)

def POP(c, t): sel, r = c; return f'      tl.fromTo("{sel}", {{ attr: {{ r: 0 }} }}, {{ attr: {{ r: {r} }}, duration: 0.5, ease: "back.out(1.6)" }}, {t});\n'
def SHOW(sel, t): return f'      IN("{sel}", {t});\n'
def HIDE(sel, t): return f'      tl.to("{sel}", {{ opacity: 0, duration: 0.25 }}, {t});\n'
def DR(sel, t, d=1.0): return f'      DRAW("{sel}", {t}, {d});\n'
def ON(sel, t): return f'      tl.to("{sel}", {{ opacity: 1, duration: 0.3 }}, {t});\n'
FADE = '<div class="panel-fade"></div><div class="rep">Representative footage</div>'
def foot(cid, a, b, src, tag, t, amb=True, extra="", js=""):
    scene(cid, a, b, FADE + extra + f'<div class="tag{" amb" if amb else ""}" style="left:96px;top:760px" id="{cid}-t">{tag}</div>', f'      IN("#{cid}-t", {max(0.1, round(t - a, 2))});' + js, [(src, 0, round(b - a, 2))])

print("drawn lengths km: south", round(plen(ROADS["sring"]), 1), "north", round(plen(ROADS["nring"]), 1))
VIEW = (0, 2, 92)  # whole-ring view: cx, cy, width km

# 1 · trucks through the city (4.0–11.9)
s = 4.0; m = Map("m1", *VIEW).base(sring=False, nring=False)
rA, rT, rG = m.road("ra", "ajmer"), m.road("rt", "tonk"), m.road("rg", "agra")
m.svg.append(f'<circle id="m1-x" cx="0" cy="0" r="{5}" style="fill:rgba(232,102,74,0.35);stroke:#E8664A;stroke-width:{4*m.u};opacity:0"/>')
js = DR(rA, rel(6.56, s), 0.9) + SHOW(m.tag("ta", "Ajmer", "bagru", dx=-20, dy=-60, amb=True), rel(6.56, s))
js += DR(rT, rel(7.44, s), 0.9) + SHOW(m.tag("tt", "Tonk", "chaksu", dx=20, dy=-30, amb=True), rel(7.44, s))
js += DR(rG, rel(8.16, s), 0.9) + SHOW(m.tag("tg", "Agra", "bassi", dx=-40, dy=-70, amb=True), rel(8.16, s))
js += ON("#m1-x", rel(10.1, s)) + f'      tl.fromTo("#m1-x", {{ attr: {{ r: 3 }} }}, {{ attr: {{ r: 7 }}, duration: 0.6, yoyo: true, repeat: 1 }}, {rel(10.1, s)});\n'
js += SHOW(m.tag("tx", "Through crowded city roads ✕", (0, 0), dx=40, dy=-90), rel(10.4, s))
m.render(s, 11.95, js)

# 2 · a ring road takes traffic around (11.95–19.0)
s = 11.95; m = Map("m2", *VIEW).base(sring=False, nring=False)
rS = m.road("rs", "sring", "#B8E07A", 9)
js = DR(rS, rel(12.3, s), 1.6) + SHOW(m.tag("t1", "Ring road: traffic goes around", K("goner"), dx=-380, dy=60, amb=True), rel(13.9, s))
js += SHOW(m.chip("c1", "Why it matters", "Less pressure on city roads · better links between highways"), rel(15.0, s))
m.render(s, 19.0, js)

# 3 · the existing South Ring Road (19.0–32.2)
s = 19.0; m = Map("m3", -2, 14, 70).base(nring=False)
for kk in ("bhankrota", "mahapura", "shivdaspura", "bagrana"): m.dot(kk)
rS = m.road("rs", "sring", "#F5B04A", 10)
eA, eT, eG = m.exitmark("ea", "bhankrota"), m.exitmark("et", K("shivdaspura")), m.exitmark("eg", "bagrana")
js = DR(rS, rel(20.62, s), 2.0) + SHOW(m.tag("t0", "SOUTH RING ROAD · ≈47 km", K("goner"), dx=-420, dy=70, amb=True), rel(22.7, s))
js += ON(eA, rel(24.54, s)) + SHOW(m.tag("t1", "Ajmer Rd junction · Bhankrota–Mahapura", "bhankrota", dx=-200, dy=-80, size=28), rel(24.6, s))
js += ON(eT, rel(27.98, s)) + SHOW(m.tag("t2", "Tonk Rd · Shivdaspura", "shivdaspura", dx=24, dy=10, size=28), rel(28.2, s))
js += ON(eG, rel(30.14, s)) + SHOW(m.tag("t3", "Agra Rd · Bagrana", "bagrana", dx=24, dy=-60, size=28), rel(30.3, s))
js += SHOW(m.chip("c1", "Status · NH-148C", "27 km Ajmer Rd–Tonk Rd stretch opened March 2019"), rel(25.6, s)) + HIDE("#m3-c1", rel(29.8, s))
m.render(s, 32.2, js)

# goods vehicles bypass (32.2–35.6)
foot("f1", 32.2, 35.6, "trucks", "Goods vehicles bypass the city", 33.4)

# 4 · the proposed Northern Ring Road (38.3–56.3)
s = 38.3; m = Map("m4", 0, 2, 92).base(nring=False)
for kk in ("bagru", "chitroli", "bagrana", "kalwar", "rampuradabri", "chomu"): m.dot(kk)
rN = m.road("rn", "nring", "#B8E07A", 9)
js = DR(rN, rel(40.24, s), 2.6) + SHOW(m.tag("t0", "PROPOSED NORTHERN RING ROAD", K("rampuradabri"), dx=-280, dy=-150, amb=True), rel(40.9, s))
js += SHOW(m.chip("n1", "In the news · Rising Rajasthan, 10 Dec 2024", "Announced by Union Minister Nitin Gadkari"), rel(42.48, s)) + HIDE("#m4-n1", rel(45.6, s))
js += SHOW(m.tag("t1", "≈99 km · 6 lanes", K("kalwar"), dx=-30, dy=-90), rel(45.76, s))
js += SHOW(m.chip("n2", "NHAI · land-acquisition notification", "Issued 6 November 2025 · alignment per reports"), rel(45.9, s)) + HIDE("#m4-n2", rel(49.4, s))
js += SHOW(m.tag("t2", "Start: near Bagru / Chitroli · Ajmer Rd", "chitroli", dx=-40, dy=110, size=28), rel(47.76, s))
js += SHOW(m.tag("t3", "End: Bagrana · Jaipur–Bandikui Expwy", "bagrana", dx=-260, dy=40, size=28), rel(52.0, s))
js += SHOW(m.chip("n3", "In the news · March 2026", "≈100 km, ₹3,000 cr+ · JDA asked to take over from NHAI"), rel(49.6, s))
m.render(s, 56.35, js, note="Proposed · alignment indicative")

# 4b · connects the western & northern corridors (56.35–61.4)
s = 56.35; m = Map("m4b", 0, 0, 92).base()
rA, rSk, rD = m.road("ra", "ajmer", width=7), m.road("rk", "sikar", width=7), m.road("rd", "delhi", width=7)
js = DR(rA, rel(57.9, s), 0.8) + SHOW(m.tag("ta", "Ajmer Rd (west)", "bagru", dx=-40, dy=-70, amb=True), rel(57.9, s))
js += DR(rSk, rel(58.9, s), 0.8) + SHOW(m.tag("tk", "Sikar Rd (north)", "chomu", dx=-20, dy=40, amb=True, right=True), rel(58.96, s))
js += DR(rD, rel(59.4, s), 0.8) + SHOW(m.tag("td", "Delhi Rd", "achrol", dx=-40, dy=-70, amb=True), rel(59.5, s))
m.render(s, 61.4, js, note="Proposed · alignment indicative")

# 5 · southern corridor zones (63.8–72.8)
s = 63.8; m = Map("m5", -2, 14, 70).base(nring=False)
c1 = m.circle("c1", km(26.825, 75.645), 4.5); c2 = m.circle("c2", km(26.745, 75.865), 5.5); c3 = m.circle("c3", "bagrana", 4.0)
js = POP(c1, rel(66.48, s)) + SHOW(m.tag("t1", "Mahapura · Mahindra SEZ side", km(26.825, 75.645), dx=-150, dy=-120, amb=True), rel(66.48, s))
js += POP(c2, rel(68.88, s)) + SHOW(m.tag("t2", "Shivdaspura–Sitapura belt", km(26.745, 75.865), dx=-160, dy=110, amb=True), rel(68.88, s))
js += POP(c3, rel(70.96, s)) + SHOW(m.tag("t3", "Bagrana · Agra Rd", "bagrana", dx=-60, dy=-110, amb=True), rel(70.96, s))
m.render(s, 72.85, js)

# 6 · northern belts (72.85–81.7)
s = 72.85; m = Map("m6", -6, -6, 84).base(sring=False)
rN = m.road("rn", "nring", "#B8E07A", 6)
c1 = m.circle("c1", km(26.83, 75.56), 5.0); c2 = m.circle("c2", km(26.98, 75.50), 6.5); c3 = m.circle("c3", "rampuradabri", 4.5); c4 = m.circle("c4", "chomu", 4.5)
js = f'      tl.set("{rN}", {{ strokeDashoffset: 0 }}, 0);\n'
js += POP(c1, rel(75.08, s)) + SHOW(m.tag("t1", "Bagru–Chitroli side", km(26.83, 75.56), dx=-120, dy=70, amb=True), rel(75.08, s))
js += POP(c2, rel(77.32, s)) + SHOW(m.tag("t2", "Kalwar–Jobner side", km(26.98, 75.50), dx=-150, dy=-110, amb=True), rel(77.32, s))
js += POP(c3, rel(79.56, s)) + SHOW(m.tag("t3", "Rampura Dabri", "rampuradabri", dx=40, dy=10, amb=True), rel(79.56, s))
js += POP(c4, rel(80.92, s)) + SHOW(m.tag("t4", "Chomu", "chomu", dx=40, dy=-40, amb=True), rel(80.92, s))
m.render(s, 81.75, js, note="Proposed · alignment indicative")

# 7 · exits (81.75–87.85)
s = 81.75; m = Map("m7", *VIEW).base()
crossings = {"Ajmer Rd": "bhankrota", "Tonk Rd": K("shivdaspura"), "Agra Rd": "bagrana", "Sikar Rd": "rampuradabri", "Ajmer Rd (N)": "chitroli", "Delhi Rd": km(27.06, 75.955)}
ex = [m.exitmark(f"e{k}", at) for k, at in enumerate(crossings.values())]
js = "".join(ON(e, rel(82.76, s) + 0.12 * k) for k, e in enumerate(ex))
js += SHOW(m.tag("t0", "Watch the exits / interchanges", (0, -36), dx=-260, dy=-20, amb=True), rel(83.0, s))
js += SHOW(m.chip("c1", "Speaker's view", "Exit connectivity can lift prices · not guaranteed"), rel(85.16, s))
m.render(s, 87.85, js, note="Exits on the proposed road are indicative")

# connectivity brings jobs, demand, industries, housing, logistics (87.85–93.85)
s = 87.85
tiles = [("wh", "Jobs &amp; industries", 89.16), ("homes", "Housing", 91.40), ("trucks", "Logistics", 91.96)]
th = "".join(f'<div id="j-k{k}" style="position:absolute;left:{72 + k*318}px;top:300px;width:300px;height:520px;border-radius:20px;overflow:hidden;border:2px solid rgba(243,231,211,0.35)"><video id="j-v{k}" class="clip" src="assets/broll/{src}.mp4" data-start="0" data-duration="{round(93.85 - s, 2)}" muted playsinline style="position:absolute;left:-250px;top:0;width:800px;height:520px;object-fit:cover"></video><div style="position:absolute;left:0;right:0;bottom:0;padding:14px 18px;background:linear-gradient(180deg,rgba(18,13,10,0),rgba(18,13,10,.92));font-family:Inter,sans-serif;font-weight:800;font-size:34px;line-height:1.1;color:#F3E7D3">{n}</div></div>' for k, (src, n, t) in enumerate(tiles))
scene("j", s, 93.85, '<div class="lbl" style="position:absolute;left:72px;top:250px;color:#E3A23B">Connectivity brings</div>' + th + '<div class="rep">Representative footage</div>',
      "\n".join(f'      IN("#j-k{k}", {round(max(0.05, t - s - 0.1), 2)}, {{ scale: 0.94 }}, {{ scale: 1 }});' for k, (_, _, t) in enumerate(tiles)))

# 8 · the city fills the ring (95.8–103.4)
s = 95.8; m = Map("m8", *VIEW).base()
m.svg.append(f'<circle id="m8-city" cx="-1" cy="4" r="12" style="fill:rgba(243,231,211,0.16);stroke:#F3E7D3;stroke-width:{3*m.u}"/>')
js = f'      tl.fromTo("#m8-city", {{ attr: {{ r: 12 }} }}, {{ attr: {{ r: 26 }}, duration: 4.0, ease: "power1.inOut" }}, {rel(96.3, s)});\n'
js += SHOW(m.tag("t0", "In 10–20 years: Jaipur within the ring roads", (0, -36), dx=-360, dy=-20, amb=True), rel(97.4, s))
js += SHOW(m.chip("c1", "Speaker's view", "Land inside the ring may gain value · not a forecast"), rel(99.6, s))
m.render(s, 103.45, js, note="Illustrative · not a forecast")

# exits B-roll (111.65–114.65), 9 · land near the proposed exits (114.65–121.2)
foot("f2", 111.65, 114.65, "flyover", "Near the proposed exits", 112.4)
s = 114.65; m = Map("m9", *VIEW).base()
ex = [m.exitmark(f"e{k}", at) for k, at in enumerate(crossings.values())]
cs = [m.circle(f"c{k}", K(at) if isinstance(at, str) else at, 3.2, "rgba(245,176,74,0.22)", "#F5B04A") for k, at in enumerate(crossings.values())]
js = "".join(ON(e, 0.1) for e in ex) + "".join(POP(c, rel(116.26, s) + 0.1 * k) for k, c in enumerate(cs))
js += SHOW(m.tag("t0", "Land near the exits", (0, -36), dx=-150, dy=-20, amb=True), rel(116.5, s))
js += SHOW(m.chip("c1", "Speaker's view", "Bigger opportunity near exits · do your due diligence"), rel(118.0, s))
m.render(s, 121.2, js, note="Exits on the proposed road are indicative")

# 0 · overview of both ring roads under the hook (1.4–4.0)
s = 1.4; m = Map("m0", *VIEW).base()
rS0, rN0 = m.road("rs", "sring", "#F5B04A", 8), m.road("rn", "nring", "#B8E07A", 7)
js = DR(rS0, 0.2, 1.2) + DR(rN0, 0.6, 1.6) + SHOW(m.tag("t0", "Jaipur", (0, 0), dx=20, dy=-60, size=36), 0.3)
m.render(s, 4.0, js, note="Schematic · positions: OpenStreetMap")

# ---------- chrome ----------
SECT = [(4.0, "THE IDEA", "Keep trucks out of the city"), (19.0, "EXISTING", "South Ring Road · ≈47 km"), (38.3, "NEXT PHASE · PROPOSED", "Northern Ring Road"),
        (61.4, "WHERE TO STUDY", "Southern corridor"), (72.85, "WHERE TO STUDY", "Northern corridor"), (81.75, "THE KEY", "Exits & interchanges"),
        (87.85, "WHY IT MATTERS", "Connectivity brings demand"), (93.85, "SPEAKER'S VIEW", "Opinion · not guaranteed"), (121.2, "CONTACT", "Ashwil Bhupesh")]
cards = [(f"hd-{k+1}", t, (SECT[k+1][0] if k + 1 < len(SECT) else VIDEO_END), c, h) for k, (t, c, h) in enumerate(SECT)]
CALL = [("co-c", 122.0, VIDEO_END, "Call / WhatsApp 96721 19046")]
hd_html = "".join(f'<div id="{i}" class="hd"><div class="hd-c">{c}</div><div class="hd-h">{h}</div></div>' for i, _, _, c, h in cards)
co_html = "".join(f'<div id="{i}" class="co">{t}</div>' for i, _, _, t in CALL)
js = "".join(f"""
      tl.fromTo("#{i}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01 }}, {t});
      tl.fromTo("#{i} .hd-c", {{ opacity: 0, x: -14 }}, {{ opacity: 1, x: 0, duration: 0.35, ease: "power3.out" }}, {t});
      tl.fromTo("#{i} .hd-h", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, {t + 0.06});
      tl.to("#{i}", {{ opacity: 0, duration: 0.2, ease: "power2.in" }}, {round(e - 0.2, 2)});""" for i, t, e, _, _ in cards)
js += "".join(f"""
      tl.fromTo("#{i}", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, {a});
      tl.to("#{i}", {{ opacity: 0, duration: 0.2 }}, {round(b - 0.2, 2)});""" for i, a, b, _ in CALL)
open(f"{P}/compositions/chrome.html", "w").write(f"""<template>
  <style>{BASE}
    .hd {{ position: absolute; left: 96px; top: 196px; max-width: 820px; padding: 14px 28px 16px 24px; border-radius: 18px; background: rgba(27,20,15,0.88); border-left: 6px solid #E3A23B; opacity: 0; }}
    .hd-c {{ font-family: "JetBrains Mono", monospace; font-size: 30px; letter-spacing: 0.2em; color: #E3A23B; }}
    .hd-h {{ font-family: "Inter", sans-serif; font-weight: 800; font-size: 52px; letter-spacing: 0.01em; line-height: 1.08; color: #F3E7D3; }}
    #op {{ position: absolute; left: 96px; right: 164px; top: 196px; padding: 14px 28px 16px; border-radius: 20px; background: rgba(27,20,15,0.9); border-left: 6px solid #E3A23B; }}
    #op-a {{ font-family: "Inter", sans-serif; font-weight: 800; font-size: 54px; color: #F3E7D3; line-height: 1.05; }}
    #op-b {{ font-family: "Inter", sans-serif; font-weight: 900; font-size: 52px; color: #E3A23B; line-height: 1.05; }}
    #pg {{ position: absolute; left: 96px; right: 164px; top: 1196px; display: flex; gap: 10px; opacity: 0; }}
    #pg i {{ flex: 1; height: 7px; border-radius: 4px; background: rgba(27,20,15,0.55); box-shadow: 0 0 0 1px rgba(243,231,211,0.25); }}
    .co {{ position: absolute; left: 96px; top: 336px; padding: 12px 22px; border-radius: 14px; background: rgba(60,38,14,0.92); border: 1.5px solid #E3A23B; font-family: "Inter", sans-serif; font-weight: 700; font-size: 38px; color: #F3E7D3; opacity: 0; white-space: nowrap; }}
  </style>
  <div id="root" data-composition-id="chrome" data-width="1080" data-height="1920">
    <div id="chrome-host" class="host clip" data-start="0" data-duration="{VIDEO_END}">
      <div id="op"><div id="op-a">JAIPUR RING ROAD</div><div id="op-b">WHAT TO WATCH</div></div>
      <div id="pg">{"".join(f'<i id="pg-{k+1}"></i>' for k in range(0))}</div>
      {hd_html}{co_html}
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#op", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, 0.12);
      tl.fromTo("#op-b", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35 }}, 0.5);
      tl.to("#op", {{ opacity: 0, y: -10, duration: 0.25, ease: "power2.in" }}, 3.75);
      tl.fromTo("#pg", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, 6.16);
      tl.to("#pg", {{ opacity: 0, duration: 0.3 }}, 99.7);{"".join(f"""
      tl.fromTo("#pg-{k+1}", {{ backgroundColor: "rgba(27,20,15,0.55)" }}, {{ backgroundColor: "#E3A23B", duration: 0.3 }}, {t});""" for k, (t, _, _) in enumerate(SECT[:0]))}{js}
      window.__timelines["chrome"] = tl;
    }})();
  </script>
</template>
""")

# ---------- captions ----------
spans = [f'<div id="cp-{gi}" class="cp"><div class="cp-in">' + "".join(f'<span class="w{" em" if w["em"] else ""}">{w["t"]}</span>' + ("" if w["t"].endswith("–") or k == len(g) - 1 else " ") for k, w in enumerate(g)) + "</div></div>" for gi, (a, b, g) in enumerate(caps)]
data = [[a, b, [w["s"] for w in g]] for a, b, g in caps]
open(f"{P}/compositions/captions.html", "w").write("""<template>
  <style>
    #root { position: absolute; inset: 0; pointer-events: none; }
    .cp { position: absolute; left: 96px; width: 820px; top: 1462px; display: flex; justify-content: center; opacity: 0; }
    .cp-in { max-width: 820px; text-align: center; padding: 12px 24px 14px; border-radius: 18px; background: rgba(20,14,10,0.82);
      font-family: "Inter", sans-serif; font-weight: 700; font-size: 48px; line-height: 1.18; color: #FFF8EE; }
    .w { opacity: 0.6; }
    .w.em { color: #F5B04A; }
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
    """ + "\n    ".join(spans) + """
  </div>
  <script>
    (function () {
      const tl = gsap.timeline({ paused: true });
      const G = """ + json.dumps(data) + """;
      G.forEach(([open, close, starts], i) => {
        const g = document.getElementById("cp-" + i);
        const ws = g.querySelectorAll(".w");
        tl.fromTo(g, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.12, ease: "power2.out" }, open);
        ws.forEach((w, k) => tl.fromTo(w, { opacity: 0.6 }, { opacity: 1, duration: 0.08, ease: "none" }, starts[k]));
        tl.to(g, { opacity: 0, duration: 0.1 }, close - 0.1);
        tl.set(g, { opacity: 0, visibility: "hidden" }, close);
      });
      window.__timelines["captions"] = tl;
    })();
  </script>
</template>
""")

# ---------- closing card ----------
steps = ["South Ring Road · ≈47 km · open", "Northern Ring Road · ≈99 km · proposed", "Study the belts near the exits", "Verify alignment before you buy"]
lis = "".join(f'<div class="ec-i"><b>{k+1:02d}</b>{t}</div>' for k, t in enumerate(steps))
ED = round(END - VIDEO_END, 2)
open(f"{P}/compositions/endcard.html", "w").write(f"""<template>
  <style>{BASE}
    #ec-k {{ position: absolute; left: 96px; top: 330px; }}
    #ec-t {{ position: absolute; left: 96px; right: 96px; top: 400px; font-family: "Instrument Serif", serif; font-size: 112px; line-height: 1.0; color: #F3E7D3; }}
    #ec-s {{ position: absolute; left: 96px; right: 96px; top: 530px; font-family: "Instrument Serif", serif; font-style: italic; font-size: 56px; color: #E3A23B; }}
    #ec-l {{ position: absolute; left: 96px; right: 96px; top: 690px; display: flex; flex-direction: column; gap: 20px; }}
    .ec-i {{ font-family: "Inter", sans-serif; font-weight: 600; font-size: 38px; color: #F3E7D3; display: flex; gap: 18px; align-items: baseline; white-space: nowrap; }}
    .ec-i b {{ font-family: "JetBrains Mono", monospace; font-weight: 400; font-size: 30px; color: #E3A23B; }}
    #ec-c {{ position: absolute; left: 96px; right: 164px; top: 1100px; padding: 26px 32px; border-radius: 22px; background: rgba(60,38,14,0.7); border: 2px solid #E3A23B; }}
    #ec-c .lbl {{ color: #E3A23B; }}
    #ec-n {{ font-family: "Inter", sans-serif; font-weight: 800; font-size: 76px; color: #F3E7D3; letter-spacing: 0.02em; margin-top: 6px; }}
    #ec-b {{ position: absolute; left: 0; right: 0; top: 1440px; text-align: center; font-family: "JetBrains Mono", monospace; font-size: 34px; letter-spacing: 0.3em; color: #C9B79C; }}
  </style>
  <div id="root" data-composition-id="endcard" data-width="1080" data-height="1920">
    <div id="endcard-host" class="host clip" data-start="0" data-duration="{ED}">
      <div id="endcard-bg" class="ins"><div class="grain"></div>
        <div id="ec-k" class="lbl">Jaipur Real Estate</div>
        <div id="ec-t">Ashwil Bhupesh</div><div id="ec-s">Follow the ring roads.</div>
        <div id="ec-l">{lis}</div>
        <div id="ec-c"><div class="lbl">Call / WhatsApp</div><div id="ec-n">96721 19046</div></div>
        <div id="ec-b">ASHWILLPOWER</div><div class="note" style="top:1500px;left:96px;right:96px;text-align:center;white-space:normal;font-size:26px;line-height:1.45">Opinions are the speaker's · not financial advice · returns are not guaranteed<br>News: NH-148C (Mar 2019) · Rising Rajasthan (Dec 2024) · NHAI notification (Nov 2025) · First India (Mar 2026)<br>Map data © OpenStreetMap contributors</div>
      </div>
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#endcard-bg", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, ease: "power2.out" }}, 0);
      tl.fromTo(["#ec-k", "#ec-t"], {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, 0.2);
      tl.fromTo("#ec-s", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, 0.5);
      tl.fromTo(".ec-i", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.3, stagger: 0.04, ease: "power3.out" }}, 0.6);
      tl.fromTo("#ec-c", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, 0.9);
      tl.fromTo("#ec-b", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, 1.1);
      window.__timelines["endcard"] = tl;
    }})();
  </script>
</template>
""")

# ---------- root ----------
hosts = "\n".join(f'      <div id="{c}" class="scene" style="z-index: 4" data-composition-id="{c}" data-composition-src="compositions/{c}.html" data-start="{s}" data-duration="{d}" data-track-index="{1 + k % 2}" data-track-kind="graphics" data-width="1080" data-height="1920"></div>' for k, (c, s, d) in enumerate(INSERTS))
sfx = [f'      <audio id="sfx-sec-{k+1}" class="clip" src="assets/sfx/click-soft.mp3" data-start="{t}" data-duration="0.36" data-track-index="{11 + k % 2}" data-volume="0.32"></audio>' for k, (t, _, _) in enumerate(SECT)]
sfx.append(f'      <audio id="sfx-end" class="clip" src="assets/sfx/chime.mp3" data-start="{VIDEO_END}" data-duration="2.2" data-track-index="13" data-volume="0.16" data-fade-out="0.8"></audio>')
PUNCH = [(0, 1.0)]
open(f"{P}/index.html", "w").write(f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #120D0A; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; }}
      #ground {{ position: absolute; inset: 0; background: #120D0A; }}
      #cam {{ position: absolute; inset: 0; transform-origin: 50% 30%; }}
      #avatar {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      .scene {{ position: absolute; inset: 0; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="30">
      <div id="ground"></div>
      <div id="cam" style="z-index: 1">
        <video id="avatar" class="clip" src="assets/avatar.mp4" data-start="0" data-duration="{VIDEO_END}" data-track-index="0" playsinline data-has-audio="true" data-volume="1"></video>
      </div>
{hosts}
      <div id="chrome" class="scene" style="z-index: 6" data-composition-id="chrome" data-composition-src="compositions/chrome.html" data-start="0" data-duration="{VIDEO_END}" data-track-index="3" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="captions" class="scene" style="z-index: 7" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{VIDEO_END}" data-track-index="4" data-track-kind="captions" data-width="1080" data-height="1920"></div>
      <div id="endcard" class="scene" style="z-index: 9" data-composition-id="endcard" data-composition-src="compositions/endcard.html" data-start="{VIDEO_END}" data-duration="{ED}" data-track-index="5" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.55" data-fade-in="1.0" data-fade-out="2.0"></audio>
{chr(10).join(sfx)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {json.dumps(PUNCH)}.forEach(([t, s]) => tl.set("#cam", {{ scale: s }}, t));
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
""")
json.dump({"inserts": INSERTS, "sections": SECT, "punch": PUNCH, "callouts": CALL}, open(f"{P}/../plan.json", "w"), indent=1)
tot = sum(d for _, _, d in INSERTS)
print("inserts", len(INSERTS), "seconds", round(tot, 1), f"{100*tot/VIDEO_END:.1f}%", "| caption groups", len(caps))
for a, b, g in caps: print(f"{a:6.2f}-{b:6.2f} [{glen(g):2d}] " + " ".join(("*" + w["t"] + "*") if w["em"] else w["t"] for w in g))
