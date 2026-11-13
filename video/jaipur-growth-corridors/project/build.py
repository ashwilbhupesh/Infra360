import sys, json, re, math
P, WJ, PJ = sys.argv[1], sys.argv[2], sys.argv[3]
VIDEO_END = 103.8
END = 109.3
exec(open(__file__.replace("build.py", "base_part.py")).read())  # BASE, INSERTS, rel(), scene()

# ---------- captions: Parakeet words on the edited timeline; place names spelled correctly ----------
FIX = {"Jepur,": "Jaipur,", "Jaiper.": "Jaipur.", "Vishali": "Vaishali", "Malvi": "Malviya", "Vaishalnagar": "Vaishali Nagar", "Malviyanagar,": "Malviya Nagar,",
       "roadbelt,": "Road belt,", "roadbelt.": "Road belt.", "Ajme": "Ajmer", "Digi": "Diggi–", "Newai": "Niwai", "wall": "walled", "areas": "areas"}
EM = {"walled", "jaipur", "center", "vaishali", "malviya", "nagar", "far", "c-scheme", "higher", "saturated", "suburbs", "periphery", "developing",
      "ajmer", "tonk", "niwai", "diggi", "malpura", "road", "belt", "30-40", "kilometers", "city", "20", "years"}
heard = json.load(open(WJ))
toks = []
for i, w in enumerate(heard):
    t = FIX.get(w["text"], w["text"])
    if w["text"] == "areas" and 95.2 < w["start"] < 95.3: t = "areas."
    if w["text"] == "today." and 37 < w["start"] < 38: t = "today"
    if w["text"] == "Is" and 38 < w["start"] < 39.5: t = "is"
    if t == "Diggi–" and i + 1 < len(heard): t = "Diggi–"
    k = re.sub(r"[^\w:%-]", "", t.lower())
    toks.append({"t": t, "s": round(w["start"], 3), "em": k in EM})
for k in range(1, len(toks)):
    if toks[k-1]["t"][-1] in ".?" and toks[k]["t"][0].islower(): toks[k]["t"] = toks[k]["t"][0].upper() + toks[k]["t"][1:]
    if toks[k-1]["t"][-1] not in ".?" and toks[k]["t"] in ("The", "Is") and k > 1: toks[k]["t"] = toks[k]["t"].lower()
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
FLAGS = {"privilege": "Word unclear (≈25.2 s source): heard as “the privilege”; Whisper omits it. Please confirm.", "date,": "Heard as “development of the date” (≈35.1 s source); possibly “of the day”. Please confirm."}
flags = [{"start": a, "end": b, "text": ctext(g), "note": n} for a, b, g in caps for w in g for key, n in FLAGS.items() if w["t"] == key]
json.dump({"captions": [{"start": a, "end": b, "text": ctext(g)} for a, b, g in caps], "flags": flags}, open(f"{P}/../captions.json", "w"), indent=1, ensure_ascii=False)

# ---------- map geometry (km from the Walled City centre; positions from OpenStreetMap / Nominatim) ----------
PL = json.load(open(PJ))
APPROX = {"cscheme": (26.906, 75.803), "bhankrota": (26.862, 75.676), "civillines": (26.906, 75.790), "vaishaliext": (26.912, 75.712), "malviya": (26.856, 75.818)}
def ll(k): return tuple(APPROX[k]) if k in APPROX else (PL[k][0], PL[k][1])
LAT0, LON0 = 26.924, 75.827
def km(lat, lon): return ((lon - LON0) * 99.25, (LAT0 - lat) * 111.0)
def K(k): return km(*ll(k))
WALL = [km(*p) for p in [(26.9266, 75.8079), (26.9335, 75.8112), (26.9398, 75.8240), (26.9385, 75.8352), (26.9305, 75.8440), (26.9153, 75.8462), (26.9153, 75.8243), (26.9176, 75.8166)]]
ROADS = {
  "ajmer": [K("ajmerigate"), km(26.912, 75.795), K("sodala"), km(26.888, 75.745), K("bhankrota"), km(26.835, 75.630), K("bagru"), km(26.780, 75.440)],
  "tonk": [K("sanganerigate"), K("rambagh"), km(26.868, 75.799), km(26.830, 75.806), K("sitapura"), K("shivdaspura"), K("chaksu"), K("niwai")],
  "sikar": [K("chandpole"), km(26.950, 75.792), K("vki"), K("chomu"), km(27.30, 75.68)],
  "delhi": [K("hawa"), K("jalmahal"), K("amer"), km(27.03, 75.89), km(27.12, 75.98)],
  "agra": [km(26.913, 75.846), km(26.900, 75.880), K("kanota"), km(26.86, 76.05)],
  "diggi": [K("sanganer"), km(26.70, 75.68), km(26.58, 75.58), K("diggi")],
  "jln": [K("albert"), K("birla"), K("wtp"), km(26.828, 75.810)],
  "ring": [K("bhankrota"), km(26.807, 75.700), km(26.770, 75.780), km(26.745, 75.850), K("goner"), km(26.840, 75.950), K("kanota")],
}
CORE = [km(26.995, 75.770), km(26.990, 75.800), km(26.960, 75.840), km(26.925, 75.865), km(26.880, 75.870), km(26.830, 75.845), km(26.770, 75.840),
        km(26.800, 75.790), km(26.815, 75.760), km(26.850, 75.730), km(26.890, 75.700), km(26.925, 75.715), km(26.955, 75.750)]
def smooth(pts, closed=True):
    n = len(pts); d = f"M{pts[0][0]:.3f} {pts[0][1]:.3f}"
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0, p1, p2, p3 = pts[(i - 1) % n] if closed or i > 0 else pts[0], pts[i], pts[(i + 1) % n], pts[(i + 2) % n] if closed or i + 2 < n else pts[-1]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6); c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.3f} {c1[1]:.3f} {c2[0]:.3f} {c2[1]:.3f} {p2[0]:.3f} {p2[1]:.3f}"
    return d + (" Z" if closed else "")
def dist(a, b): return math.hypot(a[0] - b[0], a[1] - b[1])
MH = 1270  # map area height in the frame (px)

class Map:
    def __init__(self, cid, cx, cy, w):
        self.cid, self.w, self.h = cid, w, w * MH / 1080
        self.vx, self.vy = cx - w / 2, cy - self.h / 2
        self.u = w / 1080  # km per px
        self.svg, self.html, self.js = [], [], []
    def px(self, p): return ((p[0] - self.vx) / self.u, (p[1] - self.vy) / self.u)
    def base(self, dim=("ajmer", "tonk", "sikar", "delhi", "agra", "diggi", "jln"), ring=True, wall=True, core=True):
        u = self.u
        g = "".join(f'<path d="M{x} {self.vy} V{self.vy + self.h}" />' for x in range(int(self.vx // 10 * 10), int(self.vx + self.w) + 1, 10)) + "".join(f'<path d="M{self.vx} {y} H{self.vx + self.w}" />' for y in range(int(self.vy // 10 * 10), int(self.vy + self.h) + 1, 10))
        self.svg.append(f'<g style="stroke:rgba(243,231,211,0.05);stroke-width:{u}">{g}</g>')
        if core: self.svg.append(f'<path d="{smooth(CORE)}" style="fill:rgba(243,231,211,0.06);stroke:rgba(243,231,211,0.18);stroke-width:{1.5*u};stroke-dasharray:{6*u} {6*u}"/>')
        for r in dim: self.svg.append(f'<path d="{smooth(ROADS[r], False)}" style="fill:none;stroke:rgba(243,231,211,0.30);stroke-width:{3*u};stroke-linecap:round"/>')
        if ring: self.svg.append(f'<path d="{smooth(ROADS["ring"], False)}" style="fill:none;stroke:rgba(243,231,211,0.22);stroke-width:{2.5*u};stroke-dasharray:{8*u} {6*u}"/>')
        if wall: self.svg.append(f'<path id="{self.cid}-wall" d="{smooth(WALL)}" style="fill:rgba(227,90,59,0.10);stroke:#E8664A;stroke-width:{3*u};filter:url(#{self.cid}-glow)"/>')
        return self
    def road(self, rid, key, width=7):
        u = self.u
        self.svg.append(f'<path id="{self.cid}-{rid}" class="draw" pathLength="1" d="{smooth(ROADS[key], False)}" style="fill:none;stroke:#F5B04A;stroke-width:{width*u};stroke-linecap:round;filter:url(#{self.cid}-glow)"/>')
        return f"#{self.cid}-{rid}"
    def circle(self, rid, key_or_pt, r_km, color="rgba(160,220,120,0.30)", stroke="#B8E07A"):
        p = K(key_or_pt) if isinstance(key_or_pt, str) else key_or_pt
        self.svg.append(f'<circle id="{self.cid}-{rid}" cx="{p[0]:.3f}" cy="{p[1]:.3f}" r="0" data-r="{r_km}" style="fill:{color};stroke:{stroke};stroke-width:{3*self.u};filter:url(#{self.cid}-glow)"/>')
        return f"#{self.cid}-{rid}", r_km
    def dot(self, key, big=False):
        p = K(key); r = (9 if big else 6) * self.u
        self.svg.append(f'<circle cx="{p[0]:.3f}" cy="{p[1]:.3f}" r="{r:.3f}" style="fill:{"#E3A23B" if big else "#F3E7D3"}"/>')
    def line(self, rid, a, b, dash=True):
        u = self.u
        self.svg.append(f'<path id="{self.cid}-{rid}" class="draw" pathLength="1" d="M{a[0]:.3f} {a[1]:.3f} L{b[0]:.3f} {b[1]:.3f}" style="fill:none;stroke:#F3E7D3;stroke-width:{2.5*u};{"stroke-dasharray:0.02 0.02;" if False else ""}"/>')
        return f"#{self.cid}-{rid}"
    def tag(self, rid, text, at, dx=14, dy=-22, amb=False, size=34, anchor="left"):
        x, y = self.px(K(at) if isinstance(at, str) else at); x += dx; y += dy
        wpx = len(text) * size * 0.56 + 52
        if anchor == "right": x -= wpx + 2 * dx
        x = max(48, min(1080 - 48 - wpx, x)); y = max(240, min(MH - 70, y))
        self.html.append(f'<div class="tag{" amb" if amb else ""}" id="{self.cid}-{rid}" style="left:{x:.0f}px;top:{y - 90:.0f}px;font-size:{size}px;padding:10px 20px">{text}</div>')
        return f"#{self.cid}-{rid}"
    def chip(self, rid, kicker, text, y=1040):
        self.html.append(f'<div id="{self.cid}-{rid}" style="position:absolute;left:72px;right:72px;top:{y - 90}px;padding:18px 26px;border-radius:18px;background:rgba(18,13,10,0.92);border:1.5px solid #E3A23B">'
                         f'<div class="lbl" style="color:#E3A23B;font-size:26px">{kicker}</div><div style="font-family:Inter,sans-serif;font-weight:700;font-size:34px;line-height:1.2;color:#F3E7D3;margin-top:6px">{text}</div></div>')
        return f"#{self.cid}-{rid}"
    def render(self, start, end, js, title=None, note="Schematic · positions: OpenStreetMap", videos=()):
        glow = f'<defs><filter id="{self.cid}-glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{5*self.u:.3f}" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
        svg = f'<svg id="{self.cid}-map" style="position:absolute;left:0;top:-90px;width:1080px;height:{MH}px" viewBox="{self.vx:.3f} {self.vy:.3f} {self.w:.3f} {self.h:.3f}">{glow}{"".join(self.svg)}</svg>'
        ttl = f'<div class="lbl" style="position:absolute;left:96px;top:150px;color:#E3A23B">{title}</div>' if title else ""
        nt = f'<div class="note" style="top:1128px;left:96px;font-size:26px;color:rgba(201,183,156,0.85)">{note}</div>' if note else ""
        scene(self.cid, start, end, svg + ttl + "".join(self.html) + nt,
              f'      tl.fromTo("#{self.cid}-map", {{ scale: 1.0 }}, {{ scale: 1.045, duration: {round(end - start, 2)}, ease: "none", transformOrigin: "50% 45%" }}, 0);\n' + js, videos)

def POP(sel_r, t): sel, r = sel_r; return f'      tl.fromTo("{sel}", {{ attr: {{ r: 0 }} }}, {{ attr: {{ r: {r} }}, duration: 0.5, ease: "back.out(1.6)" }}, {t});\n'
def SHOW(sel, t): return f'      IN("{sel}", {t});\n'
def HIDE(sel, t): return f'      tl.to("{sel}", {{ opacity: 0, duration: 0.25 }}, {t});\n'
def DR(sel, t, d=1.0): return f'      DRAW("{sel}", {t}, {d});\n'
FADE = '<div class="panel-fade"></div><div class="rep">Representative footage</div>'

# ===== 0 · zoom from space (opening) =====
scene("i0", 0.0, 2.45, FADE.replace("Representative footage", "Representative footage · not Jaipur-specific") + '<div class="tag amb" id="i0-t" style="left:96px;top:760px">Jaipur, Rajasthan</div>', '      IN("#i0-t", 0.9);', [("space", 0, 2.45)])

# ===== A · the Walled City =====
s = 2.40; m = Map("mA", 0.1, -0.2, 6.2).base(dim=("ajmer", "tonk", "sikar", "delhi", "agra"), ring=False, core=False)
for kk in ("hawa", "citypalace", "chandpole", "ajmerigate", "sanganerigate"): m.dot(kk)
js = f'      tl.fromTo("#mA-wall", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.6 }}, 0.2);\n'
js += SHOW(m.tag("t1", "Walled City · founded 1727", (0, -1.9), dx=-210, dy=-10, amb=True), 0.4)
js += SHOW(m.tag("t2", "Hawa Mahal", "hawa", dx=18, dy=-6), rel(3.36, s))
js += SHOW(m.tag("t3", "City Palace", "citypalace", dx=-20, dy=-10, anchor="right"), rel(3.52, s))
js += SHOW(m.tag("t4", "Chandpole", "chandpole", dx=-10, dy=10, anchor="right", size=28), rel(3.76, s))
js += SHOW(m.tag("t5", "Ajmeri Gate", "ajmerigate", dx=-10, dy=14, anchor="right", size=28), rel(3.9, s))
js += SHOW(m.tag("t6", "Sanganeri Gate", "sanganerigate", dx=10, dy=20, size=28), rel(4.05, s))
js += SHOW(m.chip("c1", "In the news", "UNESCO World Heritage City since July 2019"), rel(4.9, s))
m.render(s, 7.60, js, title="The old centre of Jaipur")

# ===== B · once "too far" =====
s = 9.55; m = Map("mB", -4.6, 3.6, 17.5).base()
m.dot("amrapali"); m.dot("wtp"); m.dot("airport")
cV = m.circle("cv", "vaishali", 1.9); cM = m.circle("cm", "malviya", 1.9)
lV = m.line("lv", (0, 0), K("vaishali")); lM = m.line("lm", (0, 0), K("malviya"))
dV, dM = dist((0, 0), K("vaishali")), dist((0, 0), K("malviya"))
js = POP(cV, rel(9.92, s)) + SHOW(m.tag("tv", "Vaishali Nagar", "vaishali", dx=-120, dy=-150, amb=True), rel(9.92, s))
js += SHOW(m.tag("tv2", "Amrapali Circle", "amrapali", dx=-60, dy=60, size=28), rel(10.6, s))
js += POP(cM, rel(11.28, s)) + SHOW(m.tag("tm", "Malviya Nagar", "malviya", dx=40, dy=-40, amb=True), rel(11.28, s))
js += SHOW(m.tag("tm2", "World Trade Park", "wtp", dx=-20, dy=50, size=28, anchor="right"), rel(11.9, s))
js += SHOW(m.tag("tm3", "JLN Marg", K("wtp"), dx=-30, dy=100, size=26, anchor="right"), rel(12.1, s))
js += DR(lV, rel(13.44, s), 0.7) + DR(lM, rel(13.6, s), 0.7)
js += SHOW(m.tag("dv", f"≈{dV:.0f} km", ((K('vaishali')[0]) / 2, K('vaishali')[1] / 2), dx=-60, dy=-60, size=30), rel(13.7, s))
js += SHOW(m.tag("dm", f"≈{dM:.0f} km", (K('malviya')[0] / 2, K('malviya')[1] / 2), dx=30, dy=-30, size=30), rel(13.9, s))
js += SHOW(m.chip("c1", "Back then", "Seen as “too far” from the Walled City"), rel(14.6, s))
m.render(s, 17.45, js, title="Once “too far”")

# ===== C · prices today =====
s = 19.55; m = Map("mC", -5.2, 3.2, 19.0).base()
for kk in ("statue", "centralpark", "sms"): m.dot(kk)
c1 = m.circle("c1", "vaishali", 1.9, "rgba(245,176,74,0.28)", "#F5B04A"); c2 = m.circle("c2", "vaishaliext", 1.5, "rgba(245,176,74,0.28)", "#F5B04A")
c3 = m.circle("c3", "malviya", 1.9, "rgba(245,176,74,0.28)", "#F5B04A"); c4 = m.circle("c4", "cscheme", 1.4, "rgba(245,176,74,0.28)", "#F5B04A")
js = POP(c1, rel(20.42, s)) + SHOW(m.tag("t1", "Vaishali Nagar", "vaishali", dx=-40, dy=-130, amb=True), rel(20.42, s))
js += POP(c2, rel(21.78, s)) + SHOW(m.tag("t2", "Vaishali Nagar Extension", "vaishaliext", dx=-120, dy=70, size=30), rel(21.78, s))
js += POP(c3, rel(24.18, s)) + SHOW(m.tag("t3", "Malviya Nagar", "malviya", dx=30, dy=-30, amb=True), rel(24.18, s))
js += POP(c4, rel(27.06, s)) + SHOW(m.tag("t4", "C-Scheme", "cscheme", dx=-30, dy=-110, amb=True), rel(27.06, s))
js += SHOW(m.tag("t5", "Statue Circle · Central Park · SMS Stadium", "sms", dx=-200, dy=40, size=26), rel(27.6, s))
js += f'      tl.to("#mC-wall", {{ opacity: 0.35, duration: 0.4 }}, {rel(28.3, s)});\n'
js += SHOW(m.chip("c1x", "Speaker's view", "Prices here now exceed many Walled City areas"), rel(28.4, s))
m.render(s, 31.65, js, title="Today")

# ===== modern today → saturated tomorrow =====
scene("g1", 33.15, 36.55, FADE + '<div class="tag" style="left:96px;top:760px" id="g1-t">What looks modern today…</div>', f'      IN("#g1-t", {rel(33.54, 33.15)});', [("modern", 0, 3.4)])
s = 36.55
scene("g2", s, 41.0, '<div class="lbl" style="position:absolute;left:96px;top:240px;color:#E3A23B">Today\'s modern areas</div>'
      '<div id="g2-a" class="serif" style="position:absolute;left:96px;right:96px;top:300px;font-size:96px;line-height:1.05;color:#F3E7D3">become tomorrow\'s</div>'
      '<div id="g2-b" class="serif" style="position:absolute;left:96px;right:96px;top:420px;font-size:120px;line-height:1.05;color:#E3A23B">saturated market</div>'
      '<div class="note">Speaker\'s view</div>',
      f'      IN("#g2-a", 0.1); IN("#g2-b", {rel(39.7, s)}, {{ scale: 0.96 }}, {{ scale: 1 }});')

# ===== D · the outer periphery =====
s = 41.0; m = Map("mD", -3, 8, 64).base()
rings = [(7, "rgba(243,231,211,0.06)", "rgba(243,231,211,0.35)"), (16, "rgba(243,231,211,0.0)", "rgba(243,231,211,0.25)"), (30, "rgba(160,220,120,0.0)", "#B8E07A")]
cs = [m.circle(f"r{k}", (0, 0), r, f, st) for k, (r, f, st) in enumerate(rings)]
m.svg.append(f'<path id="mD-band" d="M-30 0 A30 30 0 1 0 30 0 A30 30 0 1 0 -30 0 M-16 0 A16 16 0 1 1 16 0 A16 16 0 1 1 -16 0 Z" style="fill:rgba(160,220,120,0.16);opacity:0;fill-rule:evenodd"/>')
js = POP(cs[0], 0.2) + SHOW(m.tag("t0", "Developed core", (0, -7), dx=-130, dy=-30, size=30), 0.5)
js += POP(cs[1], rel(44.66, s)) + SHOW(m.tag("t1", "Suburbs", (16, 0), dx=16, dy=-24, size=30), rel(44.66, s))
js += POP(cs[2], rel(45.62, s)) + f'      tl.to("#mD-band", {{ opacity: 1, duration: 0.5 }}, {rel(45.9, s)});\n'
js += SHOW(m.tag("t2", "Outer periphery · newly developing", (0, 30), dx=-280, dy=16, amb=True), rel(46.0, s))
js += SHOW(m.chip("c1", "Where the opportunity is", "Suburbs and the outer periphery of the city"), rel(46.9, s))
m.render(s, 49.6, js, title="The opportunity", note="Illustrative rings")

# ===== E · the three corridors =====
s = 53.25; m = Map("mE", -6, 22, 64).base()
for kk in ("sodala", "mwc", "bagru", "airport", "sitapura", "chaksu", "sanganer"): m.dot(kk)
rA, rT, rD = m.road("ra", "ajmer", 9), m.road("rt", "tonk", 9), m.road("rd", "diggi", 9)
wedge = [K("bhankrota"), K("bagru"), km(26.70, 75.60), km(26.62, 75.75), K("chaksu"), K("shivdaspura"), K("sitapura"), K("sanganer"), K("sodala")]
m.svg.insert(2, f'<path id="mE-wedge" d="{smooth(wedge)}" style="fill:rgba(160,220,120,0.22);stroke:#B8E07A;stroke-width:{3*m.u};opacity:0"/>')
js = DR(rA, rel(53.62, s), 1.2) + SHOW(m.tag("a0", "AJMER ROAD · NH-48", K("bhankrota"), dx=-330, dy=-90, amb=True), rel(53.62, s))
js += SHOW(m.tag("a1", "Mahindra World City (SEZ)", "mwc", dx=-120, dy=34, size=28), rel(54.4, s))
js += SHOW(m.tag("a2", "Bagru", "bagru", dx=-10, dy=-70, size=28, anchor="right"), rel(54.8, s))
js += SHOW(m.chip("n1", "In the news · Ring Road (NH-148C)", "27 km Ajmer Road–Tonk Road stretch opened March 2019"), rel(55.3, s))
js += HIDE("#mE-n1", rel(58.5, s))
js += DR(rT, rel(58.76, s), 1.4) + SHOW(m.tag("b0", "TONK ROAD", "shivdaspura", dx=30, dy=-30, amb=True), rel(58.76, s))
js += SHOW(m.tag("b1", "Airport", "airport", dx=24, dy=-46, size=28), rel(59.2, s))
js += SHOW(m.tag("b2", "Sitapura Industrial Area", "sitapura", dx=24, dy=10, size=28), rel(59.5, s))
js += SHOW(m.tag("b3", "Chaksu", "chaksu", dx=20, dy=-20, size=28), rel(59.9, s))
js += SHOW(m.tag("b4", "↓ to Niwai (≈63 km)", K("chaksu"), dx=-60, dy=110, size=30, amb=True), rel(60.52, s))
js += SHOW(m.chip("n2", "In the news · Metro Phase-2 approved Apr 2026", "Prahladpura–Todi Mod via Tonk Road, Airport, Sitapura · target 2031"), rel(61.7, s))
js += HIDE("#mE-n2", rel(64.9, s))
js += DR(rD, rel(65.40, s), 1.2) + SHOW(m.tag("d0", "DIGGI–MALPURA ROAD", km(26.68, 75.66), dx=-300, dy=-40, amb=True), rel(65.40, s))
js += SHOW(m.tag("d1", "Sanganer", "sanganer", dx=-16, dy=-6, size=28, anchor="right"), rel(65.9, s))
js += f'      tl.to("#mE-wedge", {{ opacity: 1, duration: 0.6 }}, {rel(63.5, s)});\n'
js += SHOW(m.chip("c3", "Between the two highways", "Investment is also moving here, he says"), rel(67.2, s))
m.render(s, 69.45, js, title="Growth corridors")

# ===== belt B-roll (covers the cut at 78.0) =====
scene("h1", 74.45, 77.05, FADE + '<div class="tag amb" style="left:96px;top:760px" id="h1-t">Long-term view · not guaranteed</div>', '      IN("#h1-t", 0.5);', [("road", 0, 2.6)])
scene("h2", 77.05, 80.10, FADE + '<div class="tag" style="left:96px;top:760px" id="h2-u">Development along the corridors</div>', '      IN("#h2-u", 0.3);', [("build", 0, 3.05)])

# ===== F · 30–40 km out =====
s = 85.95; m = Map("mF", 0, 6, 100).base()
for kk in ("bagru", "chomu", "chaksu", "phagi"): m.dot(kk)
r30 = m.circle("r30", (0, 0), 30, "rgba(160,220,120,0.0)", "#B8E07A"); r40 = m.circle("r40", (0, 0), 40, "rgba(160,220,120,0.0)", "#B8E07A")
m.svg.append(f'<path id="mF-band" d="M-40 0 A40 40 0 1 0 40 0 A40 40 0 1 0 -40 0 M-30 0 A30 30 0 1 1 30 0 A30 30 0 1 1 -30 0 Z" style="fill:rgba(160,220,120,0.18);opacity:0;fill-rule:evenodd"/>')
js = POP(r30, rel(88.02, s)) + POP(r40, rel(88.3, s)) + f'      tl.to("#mF-band", {{ opacity: 1, duration: 0.5 }}, {rel(88.5, s)});\n'
js += SHOW(m.tag("t0", "30–40 km from the city", (0, 40), dx=-200, dy=14, amb=True), rel(88.6, s))
for k, (kk, dxy) in enumerate([("bagru", (-30, 26)), ("chomu", (20, -20)), ("chaksu", (20, -10))]):
    js += SHOW(m.tag(f"p{k}", f"{dict(bagru='Bagru', chomu='Chomu', chaksu='Chaksu')[kk]} ≈{dist((0, 0), K(kk)):.0f} km", kk, dx=dxy[0], dy=dxy[1], size=28, anchor="right" if kk == "bagru" else "left"), rel(89.0 + k * 0.3, s))
m.render(s, 91.80, js, title="Where to look", note="Straight-line distance from Walled City")

# ===== G · the city comes to those areas (covers the cut at 95.6) =====
s = 91.80; m = Map("mG", 0, 6, 100).base()
r30b = m.circle("r30", (0, 0), 30, "rgba(160,220,120,0.10)", "#B8E07A")
m.svg.append(f'<circle id="mG-city" cx="0" cy="3" r="11" style="fill:rgba(243,231,211,0.16);stroke:#F3E7D3;stroke-width:{3*m.u}"/>')
js = POP(r30b, 0.1) + f'      tl.fromTo("#mG-city", {{ attr: {{ r: 11 }} }}, {{ attr: {{ r: 27 }}, duration: 3.6, ease: "power1.inOut" }}, {rel(92.2, s)});\n'
js += SHOW(m.tag("t0", "Next ~20 years: the city expands outward", (0, 31), dx=-330, dy=16, amb=True), rel(92.5, s))
m.render(s, 96.40, js, title="The next 20 years", note="Illustrative · not a forecast")

# ---------- chrome ----------
SECT = [(2.40, "THE OLD CENTRE", "The Walled City"), (9.55, "ONCE “TOO FAR”", "Vaishali & Malviya Nagar"), (19.55, "TODAY", "Premium addresses"),
        (33.15, "WHAT'S NEXT", "Saturation ahead"), (41.0, "THE OPPORTUNITY", "The outer periphery"), (53.25, "GROWTH CORRIDORS", "3 belts to watch"),
        (69.45, "SPEAKER'S VIEW", "Returns are not guaranteed"), (80.10, "WHERE TO LOOK", "30–40 km out"), (91.80, "THE NEXT 20 YEARS", "The city expands"),
        (96.40, "THE TAKEAWAY", "Research the corridors")]
cards = [(f"hd-{k+1}", t, (SECT[k+1][0] if k + 1 < len(SECT) else VIDEO_END), c, h) for k, (t, c, h) in enumerate(SECT)]
CALL = []
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
    .hd {{ position: absolute; left: 96px; top: 1290px; max-width: 820px; padding: 14px 28px 16px 24px; border-radius: 18px; background: rgba(27,20,15,0.88); border-left: 6px solid #E3A23B; opacity: 0; }}
    .hd-c {{ font-family: "JetBrains Mono", monospace; font-size: 30px; letter-spacing: 0.2em; color: #E3A23B; }}
    .hd-h {{ font-family: "Inter", sans-serif; font-weight: 800; font-size: 52px; letter-spacing: 0.01em; line-height: 1.08; color: #F3E7D3; }}
    #op {{ position: absolute; left: 96px; right: 164px; top: 1270px; padding: 14px 28px 16px; border-radius: 20px; background: rgba(27,20,15,0.9); border-left: 6px solid #E3A23B; }}
    #op-a {{ font-family: "Inter", sans-serif; font-weight: 800; font-size: 54px; color: #F3E7D3; line-height: 1.05; }}
    #op-b {{ font-family: "Inter", sans-serif; font-weight: 900; font-size: 52px; color: #E3A23B; line-height: 1.05; }}
    #pg {{ position: absolute; left: 96px; right: 164px; top: 1196px; display: flex; gap: 10px; opacity: 0; }}
    #pg i {{ flex: 1; height: 7px; border-radius: 4px; background: rgba(27,20,15,0.55); box-shadow: 0 0 0 1px rgba(243,231,211,0.25); }}
    .co {{ position: absolute; left: 96px; top: 1118px; padding: 12px 22px; border-radius: 14px; background: rgba(60,38,14,0.92); border: 1.5px solid #E3A23B; font-family: "Inter", sans-serif; font-weight: 700; font-size: 38px; color: #F3E7D3; opacity: 0; white-space: nowrap; }}
  </style>
  <div id="root" data-composition-id="chrome" data-width="1080" data-height="1920">
    <div id="chrome-host" class="host clip" data-start="0" data-duration="{VIDEO_END}">
      <div id="op"><div id="op-a">JAIPUR IS SHIFTING</div><div id="op-b">WHERE TO LOOK NEXT</div></div>
      <div id="pg">{"".join(f'<i id="pg-{k+1}"></i>' for k in range(0))}</div>
      {hd_html}{co_html}
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#op", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, 0.12);
      tl.fromTo("#op-b", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35 }}, 0.5);
      tl.to("#op", {{ opacity: 0, y: -10, duration: 0.25, ease: "power2.in" }}, 2.15);
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
    .cp { position: absolute; left: 96px; width: 820px; top: 1440px; display: flex; justify-content: center; opacity: 0; }
    .cp-in { max-width: 820px; text-align: center; padding: 12px 24px 14px; border-radius: 18px; background: rgba(20,14,10,0.82);
      font-family: "Inter", sans-serif; font-weight: 700; font-size: 52px; line-height: 1.2; color: #FFF8EE; }
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
steps = ["Ajmer Road belt", "Tonk Road belt (to Niwai)", "Diggi–Malpura Road", "30–40 km from the city"]
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
        <div id="ec-t">Ashwil Bhupesh</div><div id="ec-s">Look where the city is heading.</div>
        <div id="ec-l">{lis}</div>
        <div id="ec-c"><div class="lbl">Call / WhatsApp</div><div id="ec-n">96721 19046</div></div>
        <div id="ec-b">ASHWILLPOWER</div><div class="note" style="top:1500px;left:96px;right:96px;text-align:center;white-space:normal;font-size:26px;line-height:1.45">Opinions are the speaker's · not financial advice · returns are not guaranteed<br>News: UNESCO (Jul 2019) · Ring Road NH-148C · Union Cabinet, Jaipur Metro Ph-2 (Apr 2026)<br>Map data © OpenStreetMap contributors</div>
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
