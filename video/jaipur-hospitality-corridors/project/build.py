import sys, json, re, math
P, WJ, PJ = sys.argv[1], sys.argv[2], sys.argv[3]
VIDEO_END = 92.23
ED_CARD = 5.5
CRED = 7.0
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
HOT = json.load(open(__file__.replace("build.py", "hotels.json")))
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


STRIP = "".join(photo(f"g0-s{k}", f + ".jpg", 72 + k * 237, 1190, 222, 160, cap) for k, (f, cap) in enumerate([("hawa", "Hawa Mahal"), ("amer", "Amer Fort"), ("jalmahal", "Jal Mahal"), ("ghoomar", "Ghoomar")]))
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
scene("g0", s, 4.3, f'<div id="g0-z" style="position:absolute;left:0;top:0;width:1080px;height:1830px;transform-origin:540px 780px">'
      f'<img src="{IMG}indiamap.png" style="position:absolute;left:{OX:.0f}px;top:{OY:.0f}px;width:{IW * GS:.0f}px;height:{IH * GS:.0f}px"/>{tri}</div>'
      + gtag("j", "Jaipur", J, -170, -20, True) + gtag("d", "Delhi", D, -50, -90, True) + gtag("a", "Agra", A, 24, -20, True)
      + gtag("e1", f"≈{dJD:.0f} km", mid(J, D), -190, -40) + gtag("e2", f"≈{dDA:.0f} km", mid(D, A), 30, -30) + gtag("e3", f"≈{dAJ:.0f} km", mid(A, J), -60, 30)
      + '<div class="tag amb" id="g0-g" style="left:72px;top:1060px;font-size:36px">India\'s Golden Triangle</div>'
      + STRIP + '<div class="note" style="top:1135px;font-size:24px;background:rgba(18,13,10,0.8);padding:6px 12px;border-radius:8px;color:#F3E7D3">Map: Milenioscuro, CC BY 4.0 · straight-line distances</div>',
      '      tl.fromTo("#g0-z", { scale: 0.82 }, { scale: 1, duration: 3.4, ease: "power1.out" }, 0);\n' + DR("#g0-t", 0.5, 0.9)
      + "".join(SHOW(f"#g0-{i}", t) for i, t in [("j", 0.6), ("d", 0.8), ("a", 1.0), ("e1", 1.3), ("e2", 1.4), ("e3", 1.5), ("g", 1.7)]) + "".join(f'      IN("#g0-s{k}", {round(2.0 + 0.15 * k, 2)}, {{ scale: 0.9 }}, {{ scale: 1 }});\n' for k in range(4)))



def badge(m, rid, at, logos, dx=20, dy=-110, h=40, label=None):
    """Brand badge pinned to a map point: white pill with logo(s) and optional text."""
    x, y = m.px(K(at) if isinstance(at, str) else at); x += dx; y += dy
    inner = "".join(f'<img src="{IMG}{f}" style="height:{h}px;width:auto;display:block"/>' for f in logos)
    lab = f'<span style="font-family:Inter,sans-serif;font-weight:800;font-size:28px;color:#1B140F">{label}</span>' if label else ""
    w = 70 * len(logos) + (len(label) * 16 if label else 0) + 60
    x = max(48, min(1080 - 48 - w, x))
    m.html.append(f'<div id="{m.cid}-{rid}" style="position:absolute;left:{x:.0f}px;top:{y - 90:.0f}px;display:flex;gap:12px;align-items:center;padding:10px 16px;border-radius:14px;background:#FFFFFF;box-shadow:0 8px 24px rgba(0,0,0,0.5)">{inner}{lab}</div>')
    return f"#{m.cid}-{rid}"
def pin(m, rid, at, color="#F5B04A"):
    p = K(at) if isinstance(at, str) else at; u = m.u
    m.svg.append(f'<g id="{m.cid}-{rid}" style="opacity:0"><circle cx="{p[0]:.3f}" cy="{p[1]:.3f}" r="{22*u:.3f}" style="fill:none;stroke:{color};stroke-width:{4*u};filter:url(#{m.cid}-glow)"/>'
                 f'<circle cx="{p[0]:.3f}" cy="{p[1]:.3f}" r="{9*u:.3f}" style="fill:{color}"/></g>')
    return f"#{m.cid}-{rid}"
def arc(m, rid, a, b, bend=0.25, color="#B8E07A"):
    a = K(a) if isinstance(a, str) else a; b = K(b) if isinstance(b, str) else b
    mx, my = (a[0] + b[0]) / 2 - (b[1] - a[1]) * bend, (a[1] + b[1]) / 2 + (b[0] - a[0]) * bend
    m.svg.append(f'<path id="{m.cid}-{rid}" class="draw" pathLength="1" d="M{a[0]:.3f} {a[1]:.3f} Q{mx:.3f} {my:.3f} {b[0]:.3f} {b[1]:.3f}" style="fill:none;stroke:{color};stroke-width:{3*m.u};stroke-dasharray:1;filter:url(#{m.cid}-glow)"/>')
    return f"#{m.cid}-{rid}"
ON1 = lambda sel, t: f'      tl.fromTo("{sel}", {{ opacity: 0, scale: 0.6, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2)" }}, {t});\n'
OFF = lambda sel, t: f'      tl.to("{sel}", {{ opacity: 0, duration: 0.25 }}, {t});\n'
ACH, KUK = K("achrol"), K("kukas")
SHER = km(26.885, 75.720)   # Sheraton: on the Jaipur–Ajmer Highway per reports; exact plot not public

# 1 · three corridors (4.3–5.95)
s = 4.3; m = Map("m1", -2, 2, 66).base(sring=False, nring=False)
cA = m.circle("ca", "airport", 4.5, "rgba(245,176,74,0.25)", "#F5B04A"); cD = m.circle("cd", km(27.08, 75.92), 6.0, "rgba(245,176,74,0.25)", "#F5B04A"); cM = m.circle("cm", "mahapura", 4.5, "rgba(245,176,74,0.25)", "#F5B04A")
js = POP(cA, 0.3) + POP(cD, 0.5) + POP(cM, 0.7)
js += SHOW(m.tag("t1", "1 · Airport belt", "airport", dx=40, dy=20, amb=True), 0.4) + SHOW(m.tag("t2", "2 · Delhi Rd", km(27.08, 75.92), dx=-60, dy=80, amb=True), 0.6) + SHOW(m.tag("t3", "3 · Ajmer Rd", "mahapura", dx=-150, dy=60, amb=True), 0.8)
m.render(s, 5.95, js)

# 2 · airport belt (5.95–14.65)
s = 5.95; m = Map("ma", 0.5, 8, 24).base(sring=False, nring=False)
for kk in ("malviya", "jagatpura", "sitapura"): m.dot(kk)
cA = m.circle("ca", "airport", 3.2, "rgba(245,176,74,0.22)", "#F5B04A"); pA = pin(m, "pa", "airport")
bA = badge(m, "ba", "airport", ["logo_adani.png"], dx=-80, dy=-150, label="Airport City")
icons = [("Hospitality", km(26.836, 75.835), 11.99), ("Retail", km(26.815, 75.790), 12.87), ("Commercial", km(26.805, 75.830), 13.67)]
arcs = [arc(m, f"r{k}", "airport", p) for k, (_, p, _) in enumerate(icons)]
js = POP(cA, 0.2) + ON1(pA, 0.3) + SHOW(m.tag("t0", "Jaipur International Airport", "airport", dx=-200, dy=60, amb=True), 0.4)
js += SHOW(m.tag("t2", "Malviya Nagar", "malviya", dx=20, dy=-30, size=26), 0.6) + SHOW(m.tag("t3", "Jagatpura", "jagatpura", dx=20, dy=-30, size=26), 0.7) + SHOW(m.tag("t4", "Sitapura", "sitapura", dx=20, dy=-10, size=26), 0.8)
js += OFF("#ma-t2, #ma-t3, #ma-t4", rel(9.6, s)) + OFF("#ma-t0", rel(11.75, s))
js += ON1(bA, rel(8.0, s)) + SHOW(m.chip("c1", "Adani Airport City programme", "Jaipur is one of six airports in phase one"), rel(9.9, s))
for k, (txt, p, t) in enumerate(icons):
    js += DR(arcs[k], rel(t, s) - 0.1, 0.4) + SHOW(m.tag(f"i{k}", "◆ " + txt, p, dx=-60, dy=20, amb=True, size=30), rel(t, s))
m.render(s, 14.65, js)

# 3 · Delhi Road: existing hotels + InterContinental Achrol (14.65–31.05)
s = 14.65; m = Map("md", 5, -10, 30).base(sring=False, nring=False)
for kk in ("amer", "jalmahal"): m.dot(kk)
rD = m.road("rd", "delhi", width=9)
ex = [(pin(m, f"h{k}", HK(hk), "#B8E07A"), HK(hk), nm) for k, (hk, nm) in enumerate([("fairmont", "Fairmont Jaipur"), ("lemeridien", "Le Méridien Jaipur"), ("trident", "Trident Jaipur")])]
pI = pin(m, "pi", "achrol"); cI = m.circle("ci", "achrol", 2.0, "rgba(245,176,74,0.22)", "#F5B04A")
belt = smooth([km(26.955, 75.835), km(27.000, 75.870), km(27.060, 75.910), km(27.140, 75.965), km(27.150, 75.985), km(27.070, 75.935), km(27.010, 75.890), km(26.960, 75.855)])
m.svg.insert(2, f'<path id="md-belt" d="{belt}" style="fill:rgba(160,220,120,0.22);stroke:#B8E07A;stroke-width:{3*m.u};opacity:0"/>')
bI = badge(m, "bi", "achrol", ["logo_ihg.png"], dx=-330, dy=-60, label="InterContinental")
js = DR(rD, rel(15.36, s), 1.2) + SHOW(m.tag("t0", "DELHI ROAD (NH-48)", KUK, dx=60, dy=60, amb=True), rel(15.4, s))
js += SHOW(m.tag("t1", "Amer Fort", "amer", dx=-30, dy=-10, size=26, right=True), rel(15.9, s)) + SHOW(m.tag("t2", "Jal Mahal", "jalmahal", dx=-30, dy=-10, size=26, right=True), rel(16.0, s))
for k, (p, pt, nm) in enumerate(ex):
    js += ON1(p, rel(16.3, s) + 0.25 * k) + SHOW(m.tag(f"e{k}", nm, pt, dx=-30 if k < 2 else 24, dy=[-70, 20, -10][k], size=26, right=k < 2), rel(16.4, s) + 0.25 * k)
js += POP(cI, rel(18.64, s)) + ON1(pI, rel(18.64, s)) + SHOW(m.tag("ta", "Achrol", "achrol", dx=24, dy=-10, amb=True), rel(18.7, s))
js += ON1(bI, rel(19.37, s)) + SHOW(m.chip("c1", "Planned · IHG × Makson India Hospitality", "InterContinental Jaipur Achrol · 225 keys · 16 acres · early 2030"), rel(20.0, s))
js += OFF("#md-c1", rel(27.3, s)) + f'      tl.to("#md-belt", {{ opacity: 1, duration: 0.5 }}, {rel(27.6, s)});\n'
js += SHOW(m.chip("c2", "Already established", "Resort &amp; wedding corridor"), rel(28.0, s))
m.render(s, 31.05, js, note="Existing hotels: positions from OpenStreetMap")

# 4 · Ajmer Road: Sheraton + Gateway Mahapura (31.05–42.95)
s = 31.05; m = Map("mj", -9.5, 5, 26).base(sring=True, nring=False)
for kk in ("sodala", "vaishali"): m.dot(kk)
rA = m.road("ra", "ajmer", width=9)
pS = pin(m, "ps", SHER); pG = pin(m, "pg", "mahapura"); cG = m.circle("cg", "mahapura", 1.6, "rgba(245,176,74,0.22)", "#F5B04A")
bS = badge(m, "bs", SHER, ["logo_sheraton.png", "logo_marriott.png"], dx=-40, dy=-170, h=46)
bG = badge(m, "bgw", "mahapura", ["logo_tata.png", "logo_taj.png"], dx=-40, dy=60, h=46, label="Gateway")
js = DR(rA, rel(31.5, s), 1.0) + SHOW(m.tag("t0", "AJMER ROAD (NH-48)", "sodala", dx=-40, dy=40, amb=True), rel(31.6, s))
js += ON1(pS, rel(32.6, s)) + ON1(bS, rel(32.6, s)) + SHOW(m.chip("c1", "Planned · Manglam Group × Marriott", "Sheraton · ₹350 cr · 220 keys · Jaipur–Ajmer Hwy"), rel(33.9, s))
js += OFF("#mj-c1", rel(37.2, s)) + POP(cG, rel(37.4, s)) + ON1(pG, rel(37.4, s)) + SHOW(m.tag("tm", "Mahapura", "mahapura", dx=-170, dy=-20, amb=True), rel(37.45, s))
js += ON1(bG, rel(38.6, s)) + SHOW(m.chip("c2", "Planned · IHCL (Tata) × Shri Modi Group", "Gateway Mahapura · 161 keys · NH48"), rel(39.4, s))
m.render(s, 42.95, js, note="Sheraton pin: corridor only, plot not public")

# 5 · where to invest (42.95–58.9)
s = 42.95; m = Map("mo", -2, 2, 66).base(sring=False, nring=False)
c1 = m.circle("c1", "airport", 4.5); c2 = m.circle("c2", km(27.08, 75.92), 6.0); c3 = m.circle("c3", "mahapura", 4.5)
js = POP(c1, rel(46.39, s)) + SHOW(m.tag("t1", "Airport-connected neighbourhoods", "airport", dx=-120, dy=70, amb=True), rel(46.39, s))
js += POP(c2, rel(48.31, s)) + SHOW(m.tag("t2", "Achrol–Kukas belt", km(27.08, 75.92), dx=-140, dy=90, amb=True), rel(48.31, s))
js += POP(c3, rel(49.92, s)) + SHOW(m.tag("t3", "Mahapura", "mahapura", dx=-80, dy=60, amb=True), rel(49.92, s))
for k, (txt, t) in enumerate([("◆ Commercial space", 51.03), ("◆ Rental accommodation", 52.23), ("◆ Businesses serving visitors", 53.91), ("◆ …and hotel employees", 55.91)]):
    js += SHOW(m.tag(f"w{k}", txt, (0, -30 + k * 7), dx=-300, dy=0, size=32), rel(t, s))
m.render(s, 58.9, js, note="Speaker's view · not a guarantee")

# 6 · where visitors spend (58.9–65.6)
s = 58.9; m = Map("ms", 0, 2, 50).base(sring=False, nring=False)
spend = [("Hotels", HK("fairmont"), 61.91), ("Restaurants", K("cscheme") if False else km(26.906, 75.803), 62.55), ("Transport", K("airport"), 63.43), ("Shopping", K("hawa"), 64.23), ("Weddings", K("achrol"), 64.95)]
hub = km(26.88, 75.80)
arcs = [arc(m, f"a{k}", hub, p, 0.2) for k, (_, p, _) in enumerate(spend)]
m.svg.append(f'<circle cx="{hub[0]:.3f}" cy="{hub[1]:.3f}" r="{14*m.u:.3f}" style="fill:#F5B04A"/>')
js = SHOW(m.tag("hv", "Visitors", hub, dx=-150, dy=10, amb=True, size=34), 0.3)
for k, (txt, p, t) in enumerate(spend):
    js += DR(arcs[k], rel(t, s) - 0.15, 0.35) + SHOW(m.tag(f"s{k}", "◆ " + txt, p, dx=20, dy=-30, amb=True, size=32), rel(t, s))
m.render(s, 65.6, js, note="Illustrative")

# 7 · hotels bring customers, employment, services (65.6–70.4) — footage clip
scene("em", 65.6, 70.4, '<div class="panel-fade"></div><div class="rep">Representative footage</div>'
      + "".join(f'<div class="tag{" amb" if k == 1 else ""}" id="em-t{k}" style="left:96px;top:{560 + k * 100}px">{t}</div>' for k, t in enumerate(["Customers", "Employment", "Supporting services"])),
      "\n".join(f'      IN("#em-t{k}", {round(t - 65.6, 2)});' for k, t in enumerate([65.93, 68.09, 69.4])), [("coworkers", 0, 4.8)])

# 8 · beyond sightseeing on the map, with one wedding clip inset (74.5–85.9)
s = 74.5; m = Map("mn", -1, 0, 60).base(sring=False, nring=False)
uses = [("Destination weddings", K("achrol"), 74.81), ("Conferences", K("sitapura"), 76.17), ("Luxury experiences", K("amer"), 77.29), ("Business travel", K("airport"), 78.89)]
ps = [pin(m, f"p{k}", p) for k, (_, p, _) in enumerate(uses)]
cs = [m.circle("z1", "airport", 4.5), m.circle("z2", km(27.08, 75.92), 6.0), m.circle("z3", "mahapura", 4.5)]
js = ""
for k, (txt, p, t) in enumerate(uses):
    js += ON1(ps[k], rel(t, s)) + SHOW(m.tag(f"u{k}", "◆ " + txt, p, dx=24, dy=-20, amb=True, size=32), rel(t, s))
js += "".join(POP(c, rel(81.29, s) + 0.15 * k) for k, c in enumerate(cs))
js += SHOW(m.chip("c1", "Opportunity", "For property owners &amp; entrepreneurs across these corridors"), rel(81.6, s))
m.html.append('<div id="mn-v" style="position:absolute;left:600px;top:850px;width:400px;height:300px;border-radius:18px;overflow:hidden;border:3px solid #F5B04A;opacity:0">'
              '<video id="mn-vv" class="clip" src="assets/broll/gala.mp4" data-start="0" data-duration="2.6" muted playsinline style="width:100%;height:100%;object-fit:cover"></video>'
              '<div style="position:absolute;left:8px;bottom:6px;font-family:JetBrains Mono,monospace;font-size:16px;color:#fff;text-shadow:0 1px 3px #000">Representative footage</div></div>')
js += f'      tl.fromTo("#mn-v", {{ opacity: 0, scale: 0.9 }}, {{ opacity: 1, scale: 1, duration: 0.3 }}, 0.1); tl.to("#mn-v", {{ opacity: 0, duration: 0.25 }}, 2.35);\n'
m.render(s, 85.9, js)

# ---------- chrome ----------
SECT = [(4.3, "WATCH", "3 corridors"), (5.95, "CORRIDOR 1", "The airport belt"), (14.65, "CORRIDOR 2", "Delhi Road \u00b7 Achrol"), (31.05, "CORRIDOR 3", "Ajmer Road \u00b7 Mahapura"),
        (42.95, "WHERE TO INVEST", "Where it could emerge"), (58.9, "THE RIPPLE EFFECT", "Visitors spend locally"), (65.6, "THE RIPPLE EFFECT", "Jobs \u00b7 demand \u00b7 services"),
        (70.4, "WHAT'S NEXT", "Beyond sightseeing"), (81.2, "THE OPPORTUNITY", "Across these corridors"), (85.9, "SAVE THIS", "Follow the developments")]
cards = [(f"hd-{k+1}", t, (SECT[k+1][0] if k + 1 < len(SECT) else VIDEO_END), c, h) for k, (t, c, h) in enumerate(SECT)]
CALL = [("co-c", 88.6, VIDEO_END, "Call / WhatsApp 96721 19046")]
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
      tl.to("#op", {{ opacity: 0, y: -10, duration: 0.25, ease: "power2.in" }}, 4.0);
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

MIXKIT = ["Two coworkers talking and laughing", "Gala party seen from above a table"]

# ---------- credits roll ----------
CR = {k: v for k, v in json.load(open(__file__.replace("build.py", "img/credits.json"))).items() if k in ('indiamap', 'hawa', 'amer', 'jalmahal', 'ghoomar', 'logo_adani', 'logo_ihg', 'logo_sheraton', 'logo_marriott', 'logo_tata', 'logo_taj')}
lines = ["<b>Photos &amp; maps — Wikimedia Commons</b>"] + [f"{v['title'][5:]} — {v['artist']} — {v['license']}" for k, v in CR.items() if not k.startswith("logo_")]
lines += ["<b>Logos</b> — trademarks of their owners, shown for identification only (Wikimedia Commons files)"] + [f"{v['title'][5:]}" for k, v in CR.items() if k.startswith("logo_")]
lines += ["<b>Footage — Mixkit (Free licence)</b>"] + MIXKIT
lines += ["<b>News</b> — IHG (2026) · Business Standard (Jun 2026) · IHCL (Nov 2025) · Hotel News Resource",
          "<b>Map data</b> © OpenStreetMap contributors (ODbL)"]
roll = "".join(f'<div style="margin-bottom:12px">{l}</div>' for l in lines)
scene("cr", round(VIDEO_END + ED_CARD, 2), END, f'<div class="lbl" style="position:absolute;left:72px;top:150px;color:#E3A23B">Credits</div><div style="position:absolute;left:72px;right:72px;top:220px;height:1250px;overflow:hidden"><div id="cr-r" style="position:absolute;left:0;right:0;top:40px;font-family:Inter,sans-serif;font-size:24px;line-height:1.3;color:#F3E7D3">{roll}</div></div>',
      f'      tl.fromTo("#cr-r", {{ y: 0 }}, {{ y: -300, duration: {CRED - 1.2}, ease: "none" }}, 0.6);')

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
