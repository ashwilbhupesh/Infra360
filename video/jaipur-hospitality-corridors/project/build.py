import sys, json, re, math
P, WJ, PJ = sys.argv[1], sys.argv[2], sys.argv[3]
VIDEO_END = 115.9
END = 121.4
exec(open(__file__.replace("build.py", "base_part.py")).read())  # BASE, INSERTS, rel(), scene()

# ---------- captions: Parakeet timings, spellings checked against Whisper ----------
FIX = {"IAG": "IHG", "Maxin": "Makson", "Mangalum": "Manglam", "Marit": "Marriott", "Sri": "Shri", "Achool": "Achrol–", "Cucus": "Kukas", "Belt": "belt",
       "Ajme": "Ajmer", "gateway": "Gateway", "programme,": "programme,", "Kimpton": "Kimpton"}
MULTI = [(("eighty", "four", "lakh"), "84 lakh"), (("twenty", "twenty", "six"), "2026"), (("twenty", "thousand", "crores"), "20,000 crores"),
         (("sixteen",), "16"), (("twenty", "thirty"), "2030")]
EM = {"golden", "triangle", "84", "lakh", "three", "corridors.", "airport", "adani", "city", "ihg", "kimpton", "20,000", "six", "delhi", "achrol", "intercontinental",
      "16", "2030", "ajmer", "manglam", "350", "sheraton", "marriott", "mahapura", "tata", "gateway", "kukas", "commercial", "rental", "weddings", "conferences", "business"}
heard = json.load(open(WJ))
toks = []
i = 0
while i < len(heard):
    w = heard[i]; done = False
    for seq, rep in MULTI:
        n = len(seq)
        words = [re.sub(r"[^\w]", "", x["text"].lower()) for x in heard[i:i + n]]
        if tuple(words) == seq:
            tail = re.sub(r"[\w]", "", heard[i + n - 1]["text"])
            toks.append({"t": rep + tail, "s": round(w["start"], 3), "em": True}); i += n; done = True; break
    if done: continue
    t = FIX.get(w["text"], w["text"])
    if w["text"] == "Ajme": t = "Ajmer"
    if w["text"] == "Road" and i + 1 < len(heard) and heard[i + 1]["text"] in ("Already", "Mangalum"): t = "Road."
    if w["text"] == "intercontinental": t = "InterContinental"
    k = re.sub(r"[^\w:%–,-]", "", t.lower())
    toks.append({"t": t, "s": round(w["start"], 3), "em": k in EM or k.rstrip(".,") in EM}); i += 1
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
    def chip(self, rid, kicker, text, y=1205):
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

ROADS["delhi"] = [K("hawa"), K("jalmahal"), K("amer"), K("kukas"), K("achrol"), km(27.25, 75.98)]
def card(cid, start, end, kicker, title, lines, src, extra_js="", hl=None):
    """Original 'news card' graphic: kicker, headline, fact rows, source line."""
    rows = "".join(f'<div class="row" id="{cid}-r{k}" style="top:{560 + k*92}px;font-size:38px"><b>&#8226;</b>{txt}</div>' for k, (txt, _) in enumerate(lines))
    body = (f'<div class="lbl" style="position:absolute;left:96px;top:300px;color:#E3A23B">{kicker}</div>'
            f'<div id="{cid}-h" class="serif" style="position:absolute;left:96px;right:96px;top:350px;font-size:76px;line-height:1.02;color:#F3E7D3">{title}</div>'
            + rows + f'<div class="note" style="top:{570 + len(lines)*92}px;font-size:26px;white-space:normal;right:96px">Source: {src}</div>')
    js = f'      IN("#{cid}-h", 0.1);\n' + "".join(f'      IN("#{cid}-r{k}", {max(0.2, round(t - start, 2))}, {{ x: -20, y: 0 }}, {{ x: 0 }});\n' for k, (_, t) in enumerate(lines)) + extra_js
    scene(cid, start, end, body, js)

# 0 · golden triangle (1.3–4.35)
s = 1.3; m = Map("m0", 105, -80, 300).base(sring=False, nring=False, core=False, wall=False)
D, A = km(28.6139, 77.2090), km(27.1753, 78.0098)
m.svg.append(f'<path id="m0-tri" class="draw" pathLength="1" d="M0 0 L{D[0]:.1f} {D[1]:.1f} L{A[0]:.1f} {A[1]:.1f} Z" style="fill:rgba(245,176,74,0.10);stroke:#F5B04A;stroke-width:{8*m.u};filter:url(#m0-glow)"/>')
for p in [(0, 0), D, A]: m.dot(p, big=True)
js = DR("#m0-tri", 0.3, 1.6) + SHOW(m.tag("j", "Jaipur", (0, 0), dx=-40, dy=30, amb=True), 0.4)
js += SHOW(m.tag("d", "Delhi", D, dx=-40, dy=-70, amb=True), 0.9) + SHOW(m.tag("a", "Agra", A, dx=-30, dy=30, amb=True), 1.3)
js += SHOW(m.tag("g", "India's Golden Triangle", (118, -60), dx=-190, dy=0), 1.6)
m.render(s, 4.35, js, note="Schematic · positions: OpenStreetMap")

# 1 · 84 lakh visits (4.35–10.0)
s = 4.35
scene("st", s, 10.0, '<div class="lbl" style="position:absolute;left:96px;top:300px;color:#E3A23B">Jaipur · Jan–Jun 2026</div>'
      '<div id="st-n" class="serif" style="position:absolute;left:88px;top:340px;font-size:250px;line-height:1;color:#E3A23B">84 lakh</div>'
      '<div id="st-t" style="position:absolute;left:96px;right:96px;top:610px;font-family:Inter,sans-serif;font-weight:700;font-size:46px;line-height:1.2;color:#F3E7D3">tourist visits in six months</div>'
      '<div id="st-b" style="position:absolute;left:96px;right:96px;top:720px;display:flex;gap:20px"><div class="tag" style="position:static">81.5 lakh domestic</div><div class="tag amb" style="position:static">2.56 lakh foreign</div></div>'
      '<div class="note" style="top:850px;font-size:26px">Source: Rajasthan Tourism Dept data (BOTT India, 2026)</div>',
      f'      IN("#st-n", {rel(4.8, s)}, {{ scale: 0.94 }}, {{ scale: 1 }}); IN("#st-t", {rel(5.84, s)}); IN("#st-b", {rel(6.96, s)});')

# 2 · three corridors (13.2–17.0)
s = 13.2; m = Map("m1", -2, 2, 66).base(sring=False, nring=False)
cA = m.circle("ca", "airport", 4.5, "rgba(245,176,74,0.25)", "#F5B04A"); cD = m.circle("cd", km(27.08, 75.92), 6.0, "rgba(245,176,74,0.25)", "#F5B04A"); cM = m.circle("cm", "mahapura", 4.5, "rgba(245,176,74,0.25)", "#F5B04A")
js = POP(cA, rel(13.84, s)) + POP(cD, rel(14.0, s)) + POP(cM, rel(14.16, s))
js += SHOW(m.tag("t1", "1 · Airport belt", "airport", dx=40, dy=20, amb=True), rel(14.5, s))
js += SHOW(m.tag("t2", "2 · Delhi Rd", km(27.08, 75.92), dx=-60, dy=80, amb=True), rel(14.3, s)) + SHOW(m.tag("t3", "3 · Ajmer Rd", "mahapura", dx=-150, dy=60, amb=True), rel(14.4, s))
m.render(s, 17.0, js)

# 3 · airport belt (17.0–24.4)
s = 17.0; m = Map("m2", 0.5, 9, 22).base(sring=False, nring=False)
m.dot("airport", big=True); m.dot("sitapura"); m.dot("malviya"); m.dot("jagatpura")
cA = m.circle("ca", "airport", 3.0, "rgba(245,176,74,0.22)", "#F5B04A")
js = POP(cA, 0.2) + SHOW(m.tag("t0", "Jaipur International Airport", "airport", dx=-200, dy=-110, amb=True), 0.3)
js += SHOW(m.chip("c1", "Adani Airport City programme", "Jaipur is one of six airports in phase one"), rel(17.72, s))
for k, (txt, t) in enumerate([("Hospitality", 21.4), ("Retail", 22.36), ("Commercial", 23.24)]):
    js += SHOW(m.tag(f"h{k}", txt, "airport", dx=-260 + k * 230, dy=150, size=32), rel(t, s))
js += SHOW(m.tag("t2", "Malviya Nagar", "malviya", dx=20, dy=-30, size=26), 0.6) + SHOW(m.tag("t3", "Jagatpura", "jagatpura", dx=20, dy=-30, size=26), 0.7) + SHOW(m.tag("t4", "Sitapura", "sitapura", dx=20, dy=-10, size=26), 0.8)
m.render(s, 24.4, js)

# 4 · IHG + Kimpton (24.4–29.6) and ₹20,000 cr (29.6–35.55)
card("k1", 24.4, 29.6, "In the news · 14 May 2026", "IHG × Adani Airport Holdings",
     [("5-hotel deal · ≈1,500 keys", 25.48), ("Kimpton's India debut", 26.6), ("Includes a Kimpton in Jaipur", 27.5)], "IHG press release, May 2026")
card("k2", 29.6, 35.55, "In the news · June 2026", "₹20,000 cr+ · phase one",
     [("Six airports, incl. Jaipur", 31.0), ("Mumbai · Navi Mumbai · Ahmedabad", 31.6), ("Lucknow · Jaipur · Guwahati", 32.2), ("≈70% is in the Mumbai region", 33.0)],
     "Business Standard / PTI, Free Press Journal, June 2026")

# 5 · Delhi Road / Achrol (35.55–49.6)
s = 35.55; m = Map("m3", 5, -11, 40).base(sring=False, nring=False)
for kk in ("amer", "kukas", "achrol", "jalmahal"): m.dot(kk)
rD = m.road("rd", "delhi", width=9)
cA = m.circle("ca", "achrol", 2.6, "rgba(245,176,74,0.25)", "#F5B04A")
js = DR(rD, rel(36.24, s), 1.2) + SHOW(m.tag("t0", "DELHI ROAD (NH-48)", "kukas", dx=40, dy=-10, amb=True), rel(36.3, s))
js += SHOW(m.tag("t1", "Amer Fort", "amer", dx=-30, dy=0, size=28, right=True), rel(37.3, s)) + SHOW(m.tag("t2", "Jal Mahal", "jalmahal", dx=-30, dy=0, size=28, right=True), rel(37.6, s))
js += SHOW(m.tag("t3", "Kukas", "kukas", dx=-30, dy=0, size=28, right=True), rel(38.2, s))
js += POP(cA, rel(39.84, s)) + SHOW(m.tag("t4", "Achrol", "achrol", dx=-30, dy=-10, amb=True, right=True), rel(39.84, s))
js += SHOW(m.chip("c1", "In the news · IHG × Makson India Hospitality", "InterContinental Jaipur Achrol · 225 keys · 16 acres · early 2030"), rel(41.4, s))
m.render(s, 49.6, js)
foot("f1", 49.6, 53.55, "resort", "Resort &amp; wedding corridor", 49.9)

# 6 · Ajmer Road / Mahapura (53.55–66.75)
s = 53.55; m = Map("m4", -10, 5, 30).base(sring=True, nring=False)
for kk in ("sodala", "mahapura", "vaishali"): m.dot(kk)
rA = m.road("ra", "ajmer", width=9)
cM = m.circle("cm", "mahapura", 2.4, "rgba(245,176,74,0.25)", "#F5B04A")
js = DR(rA, rel(54.0, s), 1.2) + SHOW(m.tag("t0", "AJMER ROAD (NH-48)", "bhankrota", dx=-200, dy=-120, amb=True), rel(54.0, s))
js += SHOW(m.chip("c1", "In the news · June 2026", "Manglam Group × Marriott · Sheraton · ₹350 cr · 220 keys · Jaipur–Ajmer Hwy"), rel(55.2, s)) + HIDE("#m4-c1", rel(60.2, s))
js += POP(cM, rel(60.48, s)) + SHOW(m.tag("t1", "Mahapura", "mahapura", dx=30, dy=-10, amb=True), rel(60.48, s))
js += SHOW(m.chip("c2", "In the news · 20 Nov 2025", "IHCL × Shri Modi Group · Gateway Mahapura · 161 keys"), rel(61.36, s))
m.render(s, 66.75, js, note="Sheraton: Jaipur–Ajmer Hwy · plot not shown")

# 7 · where opportunity could emerge (69.6–82.2)
s = 69.6; m = Map("m5", -2, 2, 66).base(sring=False, nring=False)
c1 = m.circle("c1", "airport", 4.5); c2 = m.circle("c2", km(27.08, 75.92), 6.0); c3 = m.circle("c3", "mahapura", 4.5)
js = POP(c1, rel(70.02, s)) + SHOW(m.tag("t1", "Airport-connected neighbourhoods", "airport", dx=-120, dy=80, amb=True), rel(70.02, s))
js += POP(c2, rel(71.94, s)) + SHOW(m.tag("t2", "Achrol–Kukas belt", km(27.08, 75.92), dx=-140, dy=90, amb=True), rel(71.94, s))
js += POP(c3, rel(73.62, s)) + SHOW(m.tag("t3", "Mahapura", "mahapura", dx=-80, dy=70, amb=True), rel(73.62, s))
js += SHOW(m.chip("c1x", "Watch for", "Commercial space · rental accommodation · businesses serving visitors &amp; staff"), rel(74.66, s))
m.render(s, 82.2, js, note="Speaker's view · not a guarantee")

# 8 · where visitors spend (82.2–89.3)
s = 82.2
spend = [("Hotels", 85.54), ("Restaurants", 86.18), ("Transport", 87.06), ("Shopping", 87.86), ("Weddings", 88.58)]
chips = "".join(f'<div class="tag{" amb" if k % 2 == 0 else ""}" id="sp-{k}" style="left:{96 + (k % 2) * 440}px;top:{430 + (k // 2) * 120}px;font-size:46px;padding:16px 28px">{t}</div>' for k, (t, _) in enumerate(spend))
scene("sp", s, 89.35, '<div class="lbl" style="position:absolute;left:96px;top:300px;color:#E3A23B">Visitors spend across</div>' + chips,
      "\n".join(f'      IN("#sp-{k}", {round(t - s, 2)}, {{ scale: 0.92 }}, {{ scale: 1 }});' for k, (_, t) in enumerate(spend)))

# 9 · beyond sightseeing (96.9–104.6)
s = 96.9
nxt = [("resort", "Destination weddings", 98.44), ("biz", "Conferences", 99.8), ("traffic", "Business travel", 102.52)]
th = "".join(f'<div id="nx-k{k}" style="position:absolute;left:{72 + k*318}px;top:330px;width:300px;height:520px;border-radius:20px;overflow:hidden;border:2px solid rgba(243,231,211,0.35)"><video id="nx-v{k}" class="clip" src="assets/broll/{src}.mp4" data-start="0" data-duration="{round(104.6 - s, 2)}" muted playsinline style="position:absolute;left:-250px;top:0;width:800px;height:520px;object-fit:cover"></video><div style="position:absolute;left:0;right:0;bottom:0;padding:14px 18px;background:linear-gradient(180deg,rgba(18,13,10,0),rgba(18,13,10,.92));font-family:Inter,sans-serif;font-weight:800;font-size:34px;line-height:1.1;color:#F3E7D3">{n}</div></div>' for k, (src, n, t) in enumerate(nxt))
scene("nx", s, 104.6, '<div class="lbl" style="position:absolute;left:72px;top:280px;color:#E3A23B">Beyond sightseeing</div>' + th +
      '<div class="tag amb" id="nx-l" style="left:72px;top:880px">+ Luxury experiences</div><div class="rep">Representative footage</div>',
      "\n".join(f'      IN("#nx-k{k}", {round(max(0.05, t - s - 0.1), 2)}, {{ scale: 0.94 }}, {{ scale: 1 }});' for k, (_, _, t) in enumerate(nxt)) + f'\n      IN("#nx-l", {rel(100.92, s)});')

# ---------- chrome ----------
SECT = [(10.0, "WHY JAIPUR", "Private investment is coming"), (13.2, "WATCH", "3 corridors"), (14.88, "CORRIDOR 1", "The airport belt"),
        (35.55, "CORRIDOR 2", "Delhi Road · Achrol"), (53.55, "CORRIDOR 3", "Ajmer Road · Mahapura"), (66.75, "THE OPPORTUNITY", "Where it could emerge"),
        (82.2, "THE RIPPLE EFFECT", "Visitors spend locally"), (89.35, "THE RIPPLE EFFECT", "Jobs · demand · services"), (94.6, "WHAT'S NEXT", "Beyond sightseeing"),
        (104.6, "SPEAKER'S VIEW", "Opportunity · not a guarantee"), (109.8, "SAVE THIS", "Follow the developments")]
cards = [(f"hd-{k+1}", t, (SECT[k+1][0] if k + 1 < len(SECT) else VIDEO_END), c, h) for k, (t, c, h) in enumerate(SECT)]
CALL = [("co-c", 112.5, VIDEO_END, "Call / WhatsApp 96721 19046")]
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
      <div id="op"><div id="op-a">JAIPUR HOSPITALITY BOOM</div><div id="op-b">3 CORRIDORS TO WATCH</div></div>
      <div id="pg">{"".join(f'<i id="pg-{k+1}"></i>' for k in range(0))}</div>
      {hd_html}{co_html}
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#op", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, 0.12);
      tl.fromTo("#op-b", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35 }}, 0.5);
      tl.to("#op", {{ opacity: 0, y: -10, duration: 0.25, ease: "power2.in" }}, 9.75);
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
steps = ["Airport belt · Adani Airport City, Kimpton", "Delhi Road · InterContinental Achrol", "Ajmer Road · Sheraton, Gateway Mahapura", "Follow the developments"]
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
        <div id="ec-t">Ashwil Bhupesh</div><div id="ec-s">Follow the hotels.</div>
        <div id="ec-l">{lis}</div>
        <div id="ec-c"><div class="lbl">Call / WhatsApp</div><div id="ec-n">96721 19046</div></div>
        <div id="ec-b">ASHWILLPOWER</div><div class="note" style="top:1500px;left:96px;right:96px;text-align:center;white-space:normal;font-size:26px;line-height:1.45">Opinions are the speaker's · not financial advice · returns are not guaranteed<br>News: Rajasthan Tourism H1 2026 · IHG (May 2026) · Business Standard (Jun 2026) · IHCL (Nov 2025)<br>Map data © OpenStreetMap contributors</div>
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
