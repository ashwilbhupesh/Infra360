import sys, json, re, math
P, WJ, PJ = sys.argv[1], sys.argv[2], sys.argv[3]
VIDEO_END = 115.9
ED_CARD = 5.5
CRED = 9.0
END = round(VIDEO_END + ED_CARD + CRED, 2)
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
HOT = json.load(open(__file__.replace("gen/build.py", "hotels.json")))
def HK(k): return km(HOT[k][0], HOT[k][1])
IMG = "assets/img/"
def logo(f, h=64, extra=""):
    return f'<div style="display:inline-flex;align-items:center;height:{h + 24}px;padding:0 22px;border-radius:14px;background:#FFFFFF;{extra}"><img src="{IMG}{f}" style="height:{h}px;width:auto;display:block"/></div>'
def clipping(cid, outlet, date, headline, top=640, rot=-1.2, w=880):
    """Original newsprint-style card that QUOTES a published headline (no publisher logo or page layout copied)."""
    return (f'<div id="{cid}" style="position:absolute;left:{(1080 - w) // 2}px;top:{top}px;width:{w}px;padding:26px 34px 22px;background:#F2EBDD;border-radius:6px;'
            f'box-shadow:0 18px 40px rgba(0,0,0,0.45);transform:rotate({rot}deg);font-family:Instrument Serif,serif;color:#1B140F">'
            f'<div style="display:flex;justify-content:space-between;align-items:baseline;border-bottom:2px solid #1B140F;padding-bottom:8px;margin-bottom:14px">'
            f'<span style="font-size:40px;font-weight:700;letter-spacing:0.02em">{outlet}</span><span style="font-family:JetBrains Mono,monospace;font-size:24px">{date}</span></div>'
            f'<div style="font-size:52px;line-height:1.08">“{headline}”</div>'
            f'<div style="font-family:JetBrains Mono,monospace;font-size:20px;margin-top:12px;color:#5A4A3A">Headline quoted · {outlet}</div></div>')
def photo(cid, f, x, y, w, h, cap=None, credit=None):
    c = f'<div style="position:absolute;left:0;right:0;bottom:0;padding:10px 14px;background:linear-gradient(180deg,rgba(18,13,10,0),rgba(18,13,10,.9));font-family:Inter,sans-serif;font-weight:800;font-size:28px;line-height:1.1;color:#F3E7D3">{cap}</div>' if cap else ""
    cr = f'<div style="position:absolute;right:8px;top:6px;font-family:JetBrains Mono,monospace;font-size:16px;color:rgba(255,255,255,0.85);text-shadow:0 1px 3px #000">{credit}</div>' if credit else ""
    return f'<div id="{cid}" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;border-radius:16px;overflow:hidden;border:2px solid rgba(243,231,211,0.35);background:#1B140F"><img src="{IMG}{f}" style="width:100%;height:100%;object-fit:cover;display:block"/>{c}{cr}</div>'
def vtile(cid, src, x, y, w, h, cap, dur):
    return (f'<div id="{cid}" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;border-radius:18px;overflow:hidden;border:2px solid rgba(243,231,211,0.35)">'
            f'<video id="{cid}-v" class="clip" src="assets/broll/{src}.mp4" data-start="0" data-duration="{dur}" muted playsinline style="position:absolute;left:50%;top:0;height:100%;width:auto;min-width:100%;transform:translateX(-50%);object-fit:cover"></video>'
            f'<div style="position:absolute;left:0;right:0;bottom:0;padding:12px 16px;background:linear-gradient(180deg,rgba(18,13,10,0),rgba(18,13,10,.92));font-family:Inter,sans-serif;font-weight:800;font-size:34px;line-height:1.1;color:#F3E7D3">{cap}</div></div>')
def tiles_scene(cid, s, e, kicker, items, cols=2, top=300, h=420, rep=True):
    W = (936 - (cols - 1) * 18) // cols; dur = round(e - s, 2)
    body = f'<div class="lbl" style="position:absolute;left:72px;top:250px;color:#E3A23B">{kicker}</div>'
    for k, (src, cap, t) in enumerate(items):
        x = 72 + (k % cols) * (W + 18); y = top + (k // cols) * (h + 18)
        body += vtile(f"{cid}-k{k}", src, x, y, W, h, cap, dur)
    if rep: body += '<div class="note" style="top:250px;left:auto;right:72px;font-size:24px">Representative footage</div>'
    scene(cid, s, e, body, "\n".join(f'      IN("#{cid}-k{k}", {round(max(0.05, t - s - 0.1), 2)}, {{ scale: 0.94 }}, {{ scale: 1 }});' for k, (_, _, t) in enumerate(items)))

# 0 · Golden Triangle on India's physical map (0.9–4.35); map bounds 37.5N–5N, 67E–99E (Module:Location map/data/India)
s = 0.9
IW, IH = 1200, round(1200 * 1615 / 1500)
def ipx(lat, lon): return ((lon - 67.0) / 32.0 * IW, (37.5 - lat) / 32.5 * IH)
PJ, PD, PA = ipx(26.924, 75.827), ipx(28.6139, 77.2090), ipx(27.1753, 78.0098)
def hav(a, b):
    import math as M
    la1, lo1, la2, lo2 = map(M.radians, (a[0], a[1], b[0], b[1]))
    return 6371 * 2 * M.asin(M.sqrt(M.sin((la2 - la1) / 2) ** 2 + M.cos(la1) * M.cos(la2) * M.sin((lo2 - lo1) / 2) ** 2))
dJD, dDA, dAJ = hav((26.924, 75.827), (28.6139, 77.209)), hav((28.6139, 77.209), (27.1753, 78.0098)), hav((27.1753, 78.0098), (26.924, 75.827))
GS = 2.6; CX, CY = (PJ[0] + PD[0] + PA[0]) / 3, (PJ[1] + PD[1] + PA[1]) / 3
OX, OY = 540 - CX * GS, 780 - CY * GS   # body coordinates (frame y − 90)
def sp(p): return (OX + p[0] * GS, OY + p[1] * GS)
J, D, A = sp(PJ), sp(PD), sp(PA)
def mid(a, b): return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
def gtag(i, txt, p, dx, dy, amb=False, size=30): return f'<div class="tag{" amb" if amb else ""}" id="g0-{i}" style="left:{p[0] + dx:.0f}px;top:{p[1] + dy:.0f}px;font-size:{size}px;padding:8px 16px">{txt}</div>'
tri = (f'<svg style="position:absolute;left:0;top:0;width:1080px;height:1830px" viewBox="0 0 1080 1830"><path id="g0-t" class="draw" pathLength="1" d="M{J[0]:.1f} {J[1]:.1f} L{D[0]:.1f} {D[1]:.1f} L{A[0]:.1f} {A[1]:.1f} Z" style="fill:rgba(245,176,74,0.22);stroke:#E8664A;stroke-width:6"/>'
       + "".join(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="11" style="fill:#120D0A;stroke:#F5B04A;stroke-width:5"/>' for p in (J, D, A)) + "</svg>")
scene("g0", s, 4.35, f'<div id="g0-z" style="position:absolute;left:0;top:0;width:1080px;height:1830px;transform-origin:540px 780px">'
      f'<img src="{IMG}indiamap.png" style="position:absolute;left:{OX:.0f}px;top:{OY:.0f}px;width:{IW * GS:.0f}px;height:{IH * GS:.0f}px"/>{tri}</div>'
      + gtag("j", "Jaipur", J, -170, -20, True) + gtag("d", "Delhi", D, -50, -90, True) + gtag("a", "Agra", A, 24, -20, True)
      + gtag("e1", f"≈{dJD:.0f} km", mid(J, D), -190, -40) + gtag("e2", f"≈{dDA:.0f} km", mid(D, A), 30, -30) + gtag("e3", f"≈{dAJ:.0f} km", mid(A, J), -60, 30)
      + '<div class="tag amb" id="g0-g" style="left:72px;top:1060px;font-size:36px">India\'s Golden Triangle</div>'
      + '<div class="note" style="top:1140px;font-size:24px;background:rgba(18,13,10,0.8);padding:6px 12px;border-radius:8px;color:#F3E7D3">Map: Milenioscuro, CC BY 4.0 · straight-line distances</div>',
      '      tl.fromTo("#g0-z", { scale: 0.82 }, { scale: 1, duration: 3.4, ease: "power1.out" }, 0);\n' + DR("#g0-t", 0.5, 0.9)
      + "".join(SHOW(f"#g0-{i}", t) for i, t in [("j", 0.6), ("d", 0.8), ("a", 1.0), ("e1", 1.3), ("e2", 1.4), ("e3", 1.5), ("g", 1.7)]))

# 1 · 84 lakh visits + Jaipur snapshots (4.35–13.2)
s = 4.35
SN1 = [("hawa", "Hawa Mahal"), ("amer", "Amer Fort"), ("jalmahal", "Jal Mahal"), ("ghoomar", "Ghoomar"), ("kalbelia", "Kalbelia"), ("block", "Bagru block print")]
SN2 = [("pottery", "Blue pottery"), ("kathputli", "Kathputli"), ("patrika", "Patrika Gate")]
grid = "".join(photo(f"st-p{k}", f + ".jpg", 72 + (k % 3) * 318, 640 + (k // 3) * 318, 300, 300, cap) for k, (f, cap) in enumerate(SN1))
grid2 = "".join(photo(f"st-q{k}", f + ".jpg", 72 + k * 318, 640, 300, 618, cap) for k, (f, cap) in enumerate(SN2))
scene("st", s, 13.2, '<div class="lbl" style="position:absolute;left:96px;top:250px;color:#E3A23B">Jaipur · Jan–Jun 2026</div>'
      '<div id="st-n" class="serif" style="position:absolute;left:88px;top:290px;font-size:200px;line-height:1;color:#E3A23B">84 lakh</div>'
      '<div id="st-t" style="position:absolute;left:96px;right:96px;top:500px;font-family:Inter,sans-serif;font-weight:700;font-size:38px;color:#F3E7D3">tourist visits · 81.5 L domestic + 2.56 L foreign</div>'
      + f'<div id="st-g1">{grid}</div><div id="st-g2" style="opacity:0">{grid2}</div>'
      '<div class="note" style="top:1275px;font-size:22px;white-space:normal;right:96px">Data: Rajasthan Tourism Dept (BOTT India) · Photos: Wikimedia Commons contributors (see credits)</div>',
      f'      IN("#st-n", {rel(4.8, s)}, {{ scale: 0.94 }}, {{ scale: 1 }}); IN("#st-t", {rel(5.84, s)});\n'
      + "".join(f'      IN("#st-p{k}", {round(rel(6.2, s) + 0.25 * k, 2)}, {{ scale: 0.9 }}, {{ scale: 1 }});\n' for k in range(6))
      + f'      tl.to("#st-g1", {{ opacity: 0, duration: 0.3 }}, {rel(10.0, s)}); tl.to("#st-g2", {{ opacity: 1, duration: 0.3 }}, {rel(10.1, s)});\n'
      + "".join(f'      IN("#st-q{k}", {round(rel(10.1, s) + 0.2 * k, 2)}, {{ scale: 0.92 }}, {{ scale: 1 }});\n' for k in range(3)))

# 2 · three corridors (13.2–17.0)
s = 13.2; m = Map("m1", -2, 2, 66).base(sring=False, nring=False)
cA = m.circle("ca", "airport", 4.5, "rgba(245,176,74,0.25)", "#F5B04A"); cD = m.circle("cd", km(27.08, 75.92), 6.0, "rgba(245,176,74,0.25)", "#F5B04A"); cM = m.circle("cm", "mahapura", 4.5, "rgba(245,176,74,0.25)", "#F5B04A")
js = POP(cA, rel(13.84, s)) + POP(cD, rel(14.0, s)) + POP(cM, rel(14.16, s))
js += SHOW(m.tag("t1", "1 · Airport belt", "airport", dx=40, dy=20, amb=True), rel(14.5, s))
js += SHOW(m.tag("t2", "2 · Delhi Rd", km(27.08, 75.92), dx=-60, dy=80, amb=True), rel(14.3, s)) + SHOW(m.tag("t3", "3 · Ajmer Rd", "mahapura", dx=-150, dy=60, amb=True), rel(14.4, s))
m.render(s, 17.0, js)

# 3 · airport belt: real airport photo + Adani logo (17.0–20.4), then hospitality / retail / commercial (20.4–24.4)
s = 17.0
scene("ap", s, 20.4, photo("ap-p", "airport.jpg", 72, 300, 936, 620, "Jaipur International Airport", "Photo: Chainwit., CC BY-SA 4.0")
      + f'<div id="ap-l" style="position:absolute;left:72px;top:950px;display:flex;gap:18px;align-items:center">{logo("logo_adani.png", 56)}<div class="tag amb" style="position:static">Airport City programme</div></div>',
      f'      IN("#ap-p", 0.1, {{ scale: 0.96 }}, {{ scale: 1 }}); IN("#ap-l", {rel(17.6, s)});')
tiles_scene("ab", 20.4, 24.4, "Bringing together", [("checkin", "Hospitality", 21.4), ("mall", "Retail", 22.36), ("office", "Commercial", 23.24)], cols=3, h=560)

# 4 · IHG × Adani + Kimpton (24.4–29.6)
s = 24.4
scene("k1", s, 29.6, f'<div id="k1-l" style="position:absolute;left:72px;top:290px;display:flex;gap:16px;flex-wrap:wrap;align-items:center">{logo("logo_ihg.png", 54)}{logo("logo_adani.png", 46)}<div class="tag amb" style="position:static;font-size:32px">Kimpton</div></div>'
      + photo("k1-p", "kimpton.jpg", 72, 430, 936, 470, "Kimpton Saint George, Toronto · existing hotel, not the Jaipur project", "Photo: Nick Number, CC BY 4.0")
      + clipping("k1-c", "IHG", "14 May 2026", "IHG Hotels & Resorts signs landmark five-hotel deal with Adani Airport Holdings", top=930),
      f'      IN("#k1-l", 0.1); IN("#k1-p", {rel(26.0, s)}, {{ scale: 0.96 }}, {{ scale: 1 }}); IN("#k1-c", {rel(25.3, s)}, {{ y: 40, rotation: -4 }}, {{ y: 0, rotation: -1.2 }});')

# 5 · ₹20,000 cr (29.6–35.55)
s = 29.6
scene("k2", s, 35.55, f'<div id="k2-l" style="position:absolute;left:72px;top:290px">{logo("logo_adani.png", 54)}</div>'
      + clipping("k2-c", "Business Standard", "June 2026", "Adani to invest ₹20k cr in six ‘airport city’ projects across 5 states", top=430, rot=1.0)
      + '<div id="k2-f" style="position:absolute;left:72px;right:72px;top:800px">'
      + "".join(f'<div class="row" id="k2-r{k}" style="position:relative;left:0;right:0;top:0;font-size:36px;height:76px"><b>&#8226;</b>{t}</div>' for k, t in enumerate(["Mumbai · Navi Mumbai · Ahmedabad", "Lucknow · Jaipur · Guwahati", "≈70% of it in the Mumbai region"]))
      + '</div>',
      f'      IN("#k2-l", 0.1); IN("#k2-c", 0.3, {{ y: 40, rotation: 4 }}, {{ y: 0, rotation: 1.0 }});\n' + "".join(f'      IN("#k2-r{k}", {round(rel(32.0, s) + 0.5 * k, 2)}, {{ x: -20, y: 0 }}, {{ x: 0 }});\n' for k in range(3)))

# 6 · Delhi Road with existing hotels labelled (35.55–42.3)
s = 35.55; m = Map("m3", 5, -10, 30).base(sring=False, nring=False)
for kk in ("amer", "kukas", "achrol", "jalmahal"): m.dot(kk)
for hk in ("fairmont", "lemeridien", "trident"): m.dot(HK(hk), color="#B8E07A")
rD = m.road("rd", "delhi", width=9)
cA = m.circle("ca", "achrol", 2.2, "rgba(245,176,74,0.25)", "#F5B04A")
js = DR(rD, rel(36.24, s), 1.2) + SHOW(m.tag("t0", "DELHI ROAD (NH-48)", "achrol", dx=-420, dy=40, amb=True), rel(36.3, s))
js += SHOW(m.tag("t1", "Amer Fort", "amer", dx=-30, dy=-10, size=26, right=True), rel(36.8, s)) + SHOW(m.tag("t2", "Jal Mahal", "jalmahal", dx=-30, dy=-10, size=26, right=True), rel(36.9, s))
js += SHOW(m.tag("h1", "Fairmont Jaipur", HK("fairmont"), dx=24, dy=-40, size=28), rel(37.5, s)) + SHOW(m.tag("h2", "Le Méridien Jaipur", HK("lemeridien"), dx=24, dy=10, size=28), rel(37.8, s))
js += SHOW(m.tag("h3", "Trident Jaipur", HK("trident"), dx=24, dy=-10, size=28), rel(38.1, s)) + SHOW(m.tag("t3", "Kukas", "kukas", dx=-30, dy=30, size=26, right=True), rel(38.4, s))
js += POP(cA, rel(39.84, s)) + SHOW(m.tag("t4", "Achrol · InterContinental (planned)", "achrol", dx=-30, dy=-80, amb=True, right=True), rel(39.84, s))
m.render(s, 42.3, js, note="Existing hotels: positions from OpenStreetMap")

# 7 · InterContinental Achrol (42.3–49.6)
s = 42.3
scene("ic", s, 49.6, f'<div id="ic-l" style="position:absolute;left:72px;top:290px;display:flex;gap:16px;align-items:center">{logo("logo_ihg.png", 54)}<div class="tag" style="position:static;font-size:30px">× Makson India Hospitality</div></div>'
      + photo("ic-p", "intercontinental.jpg", 72, 430, 936, 470, "InterContinental Melbourne · existing hotel, not the Jaipur project", "Photo: IHG, CC BY-SA 4.0")
      + clipping("ic-c", "IHG", "2026", "IHG inks deal for InterContinental Jaipur Achrol Resort", top=930, rot=-1.0)
      + '<div id="ic-f" style="position:absolute;left:72px;top:1180px;display:flex;gap:14px"><div class="tag amb" style="position:static">225 keys</div><div class="tag amb" style="position:static">16 acres</div><div class="tag amb" style="position:static">Early 2030</div></div>',
      f'      IN("#ic-l", 0.1); IN("#ic-p", 0.3, {{ scale: 0.96 }}, {{ scale: 1 }}); IN("#ic-c", {rel(43.6, s)}, {{ y: 40, rotation: -4 }}, {{ y: 0, rotation: -1.0 }});'
      f' IN("#ic-f", {rel(46.72, s)});')

# 8 · resort & wedding corridor (49.6–53.55)
tiles_scene("rw", 49.6, 53.55, "Resort &amp; wedding corridor", [("resort", "Resorts", 49.8), ("wedding", "Weddings", 52.4)], cols=2, h=700)

# 9 · Sheraton on Ajmer Road (53.55–60.3)
s = 53.55
scene("sh", s, 60.3, f'<div id="sh-l" style="position:absolute;left:72px;top:290px;display:flex;gap:16px;align-items:center">{logo("logo_sheraton.png", 70)}{logo("logo_marriott.png", 60)}'
      '<div class="tag amb" style="position:static;font-size:30px">Manglam Group</div></div>'
      + photo("sh-p", "sheraton.jpg", 72, 450, 936, 450, "Sheraton, Toronto · existing hotel, not the Jaipur project", "Photo: Chris Woodrich, CC BY-SA 4.0")
      + clipping("sh-c", "Business Standard", "June 2026", "Manglam Group ties up with Marriott for ₹350 crore Sheraton hotel in Jaipur", top=930, rot=1.0)
      + '<div id="sh-f" style="position:absolute;left:72px;top:1200px;display:flex;gap:14px"><div class="tag amb" style="position:static">220 keys</div><div class="tag amb" style="position:static">Jaipur–Ajmer Hwy</div></div>',
      f'      IN("#sh-l", {rel(55.2, s)}); IN("#sh-p", {rel(57.52, s)}, {{ scale: 0.96 }}, {{ scale: 1 }}); IN("#sh-c", {rel(56.2, s)}, {{ y: 40, rotation: 4 }}, {{ y: 0, rotation: 1.0 }}); IN("#sh-f", {rel(58.6, s)});')

# 10 · Gateway Mahapura by IHCL (Tata) (60.3–66.75)
s = 60.3
scene("gw", s, 66.75, f'<div id="gw-l" style="position:absolute;left:72px;top:290px;display:flex;gap:16px;align-items:center">{logo("logo_tata.png", 64)}{logo("logo_taj.png", 64)}'
      '<div class="tag" style="position:static;font-size:30px">IHCL × Shri Modi Group</div></div>'
      + photo("gw-p", "rambagh.jpg", 72, 450, 936, 450, "Rambagh Palace (Taj · IHCL), Jaipur · existing hotel", "Photo: Sunnya343, CC BY-SA 4.0")
      + clipping("gw-c", "IHCL", "20 Nov 2025", "IHCL signs a Gateway in Mahapura, Jaipur", top=930, rot=-1.0)
      + '<div id="gw-f" style="position:absolute;left:72px;top:1180px;display:flex;gap:14px"><div class="tag amb" style="position:static">161 keys</div><div class="tag amb" style="position:static">Mahapura · NH48</div></div>',
      f'      IN("#gw-l", {rel(61.36, s)}); IN("#gw-p", 0.3, {{ scale: 0.96 }}, {{ scale: 1 }}); IN("#gw-c", {rel(63.9, s)}, {{ y: 40, rotation: -4 }}, {{ y: 0, rotation: -1.0 }}); IN("#gw-f", {rel(64.8, s)});')

# 11 · opportunity map (69.6–74.5) then what to watch for (74.5–82.2)
s = 69.6; m = Map("m5", -2, 2, 66).base(sring=False, nring=False)
c1 = m.circle("c1", "airport", 4.5); c2 = m.circle("c2", km(27.08, 75.92), 6.0); c3 = m.circle("c3", "mahapura", 4.5)
js = POP(c1, rel(70.02, s)) + SHOW(m.tag("t1", "Airport-connected neighbourhoods", "airport", dx=-120, dy=80, amb=True), rel(70.02, s))
js += POP(c2, rel(71.94, s)) + SHOW(m.tag("t2", "Achrol–Kukas belt", km(27.08, 75.92), dx=-140, dy=90, amb=True), rel(71.94, s))
js += POP(c3, rel(73.62, s)) + SHOW(m.tag("t3", "Mahapura", "mahapura", dx=-80, dy=70, amb=True), rel(73.62, s))
m.render(s, 74.5, js, note="Speaker's view · not a guarantee")
tiles_scene("op", 74.5, 82.2, "Watch for", [("office", "Commercial space", 74.66), ("rental", "Rental accommodation", 75.86), ("dining", "Businesses serving visitors", 77.54), ("coworkers", "…and employees", 79.54)], cols=2, h=440)

# 12 · where visitors spend (82.2–89.35)
tiles_scene("sp", 82.2, 89.35, "Visitors spend across", [("corridor", "Hotels", 85.54), ("dining", "Restaurants", 86.18), ("traffic", "Transport", 87.06), ("shoppers", "Shopping", 87.86), ("gala", "Weddings", 88.58)], cols=2, h=290)

# 13 · customers, employment, supporting services (89.35–94.6)
tiles_scene("em", 89.35, 94.6, "Hotels also bring", [("checkin", "Customers", 90.76), ("coworkers", "Employment", 91.72), ("present", "Supporting services", 93.32)], cols=3, h=560)

# 14 · beyond sightseeing (96.9–104.6)
tiles_scene("nx", 96.9, 104.6, "Beyond sightseeing", [("gala", "Destination weddings", 98.44), ("present", "Conferences", 99.8), ("pool", "Luxury experiences", 100.92), ("landing", "Business travel", 102.52)], cols=2, h=440)

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
ED = ED_CARD
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

MIXKIT = ["Swiming pool in resort garden — ivz", "Two businessmen in suits reviewing some documents — m0de0n", "Aerial travel above a highway in the city", "A family checking in a luxury hotel — barselona_dreams",
          "A man is presenting a business report — FrameStock", "Airplane landing in illuminated airport tracks — ivz", "Busy shopping mall time lapse — YanMednis", "Corridor of an elegant hotel — Ilya2k",
          "Customers in a minimalist style restaurant", "Decorations on the ceiling of a wedding party", "Gala party seen from above a table", "Interior of a room with terrace", "Luxury swimming pool",
          "Open office space", "Shoppers walking through a mall — Grey_Coast_Media", "Two coworkers talking and laughing"]

# ---------- credits roll ----------
CR = json.load(open(__file__.replace("gen/build.py", "img/credits.json")))
lines = ["<b>Photos &amp; maps — Wikimedia Commons</b>"] + [f"{v['title'][5:]} — {v['artist']} — {v['license']}" for k, v in CR.items() if not k.startswith("logo_")]
lines += ["<b>Logos</b> — trademarks of their owners, shown for identification only (Wikimedia Commons files)"] + [f"{v['title'][5:]}" for k, v in CR.items() if k.startswith("logo_")]
lines += ["<b>Footage — Mixkit (Free licence)</b>"] + MIXKIT
lines += ["<b>News</b> — headlines quoted from: IHG (May 2026) · Business Standard (Jun 2026) · IHCL (Nov 2025) · BOTT India / Rajasthan Tourism (2026) · Hotel News Resource",
          "<b>Map data</b> © OpenStreetMap contributors (ODbL)"]
roll = "".join(f'<div style="margin-bottom:12px">{l}</div>' for l in lines)
scene("cr", round(VIDEO_END + ED_CARD, 2), END, f'<div class="lbl" style="position:absolute;left:72px;top:150px;color:#E3A23B">Credits</div><div style="position:absolute;left:72px;right:72px;top:220px;height:1250px;overflow:hidden"><div id="cr-r" style="position:absolute;left:0;right:0;top:40px;font-family:Inter,sans-serif;font-size:24px;line-height:1.3;color:#F3E7D3">{roll}</div></div>',
      f'      tl.fromTo("#cr-r", {{ y: 0 }}, {{ y: -900, duration: {CRED - 1.2}, ease: "none" }}, 0.6);')

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
