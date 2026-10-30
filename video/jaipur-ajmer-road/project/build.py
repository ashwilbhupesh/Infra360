import sys, json, re, math
P, WJ, PJ = sys.argv[1], sys.argv[2], sys.argv[3]
VIDEO_END = 153.55
ED_CARD = 5.5
CRED = 7.0
END = round(VIDEO_END + ED_CARD + CRED, 2)
exec(open(__file__.replace("build.py", "base_part.py")).read())  # BASE, INSERTS, rel(), scene()

# ---------- captions: Parakeet timings, spellings checked against Whisper ----------
FIX = {"Ajmehi": "Ajmer", "Dosofut": "200-feet", "Dozafud": "200-feet", "Keshupura,": "Keshopura,", "Bhakrotta.": "Bhankrota.", "Mangalam": "Manglam", "Pinkwest": "PinkWest",
       "Bergana": "Bagrana", "Jaipur-Bandikwe": "Jaipur–Bandikui", "Ajme": "Ajmer", "Chitrolli": "Chitroli", "Ajmir": "Ajmer", "Nadan": "Northern", "nadan": "northern",
       "Ark": "arc", "City,": "City", "Approach": "approach", "Kalwada.": "Kalwara.", "Infosy's": "Infosys,", "Deutsch": "Deutsche", "Dhammikala,": "Dehmi Kalan,", "dental": "rental",
       "Mehala,": "Mahla,", "Mohumpura,": "Mokhampura,", "Fulera,": "Phulera,", "Sambor.": "Sambhar.", "Kishangar,": "Kishangarh,", "Kishangar": "Kishangarh", "Margaret": "marble",
       "Trading": "trading", "Processing,": "processing,", "JME": "Ajmer", "stress": "stretch"}
MULTI = [(("west", "vay", "heights"), "Westway Heights"), (("bandha", "sindhri"), "Bandar Sindri"), (("code", "podli"), "Kotputli–"), (("delhi", "ajmir"), "Delhi–Ajmer")]
EM = {"ajmer", "200-feet", "hirapura", "westway", "bhankrota", "vrb", "pinkwest", "flyovers", "underpasses", "signal", "mahapura", "southern", "bagrana", "jaipur–bandikui",
      "chitroli", "bagru", "northern", "mahindra", "kalwara", "infosys", "deutsche", "dehmi", "manipal", "dudu", "kishangarh", "airport", "pushkar", "kotputli–", "expressway", "logistics", "warehouses"}
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
    if w["text"] == "the" and i > 0 and heard[i - 1]["text"] == "Pushkar.": t = "The"
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
APPROX = {"bhankrota": (26.862, 75.676), "chitroli": (26.840, 75.585), "bagrana": (26.885, 75.930), "cscheme": (26.906, 75.803),
          # this video: OpenStreetMap (Nominatim) lookups; Westway/VRB/PinkWest, Mahla, Mokhampura, Bandar Sindri placed approximately
          "hirapura": (26.8891, 75.7374), "keshopura": (26.8850, 75.7027), "westway": (26.866, 75.690), "vrb": (26.871, 75.684), "pinkwest": (26.874, 75.700),
          "kalwara": (26.7975, 75.6362), "manipal": (26.8429, 75.5654), "mahla": (26.790, 75.430), "mokhampura": (26.735, 75.330), "dudu": (26.6811, 75.2321),
          "phulera": (26.8751, 75.2456), "narena": (26.7491, 74.9772), "sambhar": (26.9110, 75.1848), "bandarsindri": (26.630, 74.990), "kishangarh": (26.5886, 74.8611),
          "kgairport": (26.5870, 74.8126), "ajmer": (26.4691, 74.6390), "pushkar": (26.4876, 74.5578), "kotputli": (27.7072, 76.1996), "bandikui": (27.0457, 76.5753)}
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
ROADS.update({
  "nh48w": [K("hirapura"), K("keshopura"), K("pinkwest"), K("bhankrota"), K("mahapura"), K("chitroli"), K("bagru"), K("mahla"), K("mokhampura"), K("dudu"), K("bandarsindri"), K("kishangarh"), km(26.53, 74.75), K("ajmer")],
  "delhiNH": [K("hawa"), K("amer"), km(27.03, 75.89), K("achrol"), km(27.45, 76.05), K("kotputli")],
  "bdk": [K("bagrana"), km(26.93, 76.10), km(26.99, 76.33), K("bandikui")],
  "dme": [km(27.80, 76.95), km(27.35, 76.75), K("bandikui"), km(26.75, 76.45), km(26.40, 76.30)],
  "kk": [K("kotputli"), km(27.45, 75.85), km(27.15, 75.55), K("jobner"), km(26.80, 75.15), K("kishangarh")],
  "phulera": [K("dudu"), km(26.78, 75.24), K("phulera")], "sambhar": [K("phulera"), K("sambhar")], "narena": [K("dudu"), km(26.72, 75.10), K("narena")],
})
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
    def render(self, start, end, js, note="Schematic · positions: OpenStreetMap", keep=False, fade_in=True):
        glow = f'<defs><filter id="{self.cid}-glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{5*self.u:.3f}" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
        svg = f'<svg id="{self.cid}-map" style="position:absolute;left:0;top:{MT - 90}px;width:1080px;height:{MH}px" viewBox="{self.vx:.3f} {self.vy:.3f} {self.w:.3f} {self.h:.3f}">{glow}{"".join(self.svg)}</svg>'
        nt = f'<div class="note" style="top:{MT + MH - 90 - 40}px;left:auto;right:64px;font-size:26px;color:rgba(201,183,156,0.85)">{note}</div>' if note else ""
        scene(self.cid, start, end, svg + "".join(self.html) + nt,
              f'      tl.fromTo("#{self.cid}-map", {{ scale: 1.0 }}, {{ scale: 1.04, duration: {round(end - start, 2)}, ease: "none", transformOrigin: "50% 50%" }}, 0);\n' + js, keep=keep, fade_in=fade_in)

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
# ===================== v16: one continuous map with a camera (real OpenStreetMap geometry) =====================
import glob, os
KM = 10                                     # world px per km
OSMD = __file__.replace("gen/build.py", "osm").replace("build.py", "osm")
def _ways(pattern):
    out = []
    for f in sorted(glob.glob(os.path.join(OSMD, pattern))):
        try: d = json.load(open(f))
        except Exception: continue
        for el in d.get("elements", []):
            if el.get("type") == "way" and el.get("geometry"):
                out.append((el.get("tags", {}), [km(g["lat"], g["lon"]) for g in el["geometry"]], el["id"]))
            elif el.get("type") == "relation":
                for mbr in el.get("members", []):
                    if mbr.get("geometry") and mbr.get("role") in ("outer", ""):
                        out.append((el.get("tags", {}), [km(g["lat"], g["lon"]) for g in mbr["geometry"]], el["id"]))
    seen, res = set(), []
    for t, p, i in out:
        if (i, len(p), p[0]) in seen: continue
        seen.add((i, len(p), p[0])); res.append((t, p))
    return res
def rdp(pts, eps):
    if len(pts) < 3: return pts
    a, b = pts[0], pts[-1]; dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy)
    if L < 1e-6:   # closed ring: split at the farthest vertex
        i = max(range(len(pts)), key=lambda i: math.hypot(pts[i][0] - a[0], pts[i][1] - a[1]))
        return rdp(pts[:i + 1], eps)[:-1] + rdp(pts[i:], eps)
    dmax, idx = 0, 0
    for i in range(1, len(pts) - 1):
        d = abs(dy * (pts[i][0] - a[0]) - dx * (pts[i][1] - a[1])) / L
        if d > dmax: dmax, idx = d, i
    if dmax > eps: return rdp(pts[:idx + 1], eps)[:-1] + rdp(pts[idx:], eps)
    return [a, b]
def pd(pts, close=False):
    return "M" + " L".join(f"{p[0]*KM:.1f} {p[1]*KM:.1f}" for p in pts) + (" Z" if close else "")
MAJOR = _ways("major_*.json"); CITY = _ways("city_*.json"); RAIL = _ways("rail_*.json"); WATER = _ways("water.json")
def pick(cond): return [p for t, p in MAJOR if cond(t)]
def _nm(t): return (t.get("name", "") + " " + t.get("name:en", "") + " " + t.get("ref", "")).lower()
NH48 = pick(lambda t: ((t.get("ref", "") == "NH48") or ("ajmer road" in t.get("name", "").lower()) or ("kishangarh expressway" in t.get("name", "").lower())) and t.get("highway") in ("trunk", "motorway"))
NH48 = [p for p in NH48 if min(q[0] for q in p) < -8 and max(q[1] for q in p) > -2]          # west of Jaipur: the Ajmer Road
if NH48 and min(min(q[0] for q in p) for p in NH48) > -100: NH48.append([K("kishangarh"), km(26.53, 74.75), K("ajmer")])   # Ajmer end: schematic until the OSM tile loads
SRING = pick(lambda t: "outer ring road" in _nm(t) or t.get("ref") == "ORR")
BDK = pick(lambda t: "bandikui" in _nm(t))
DME = pick(lambda t: ("mumbai" in _nm(t) and "delhi" in _nm(t)) or t.get("ref", "").replace(" ", "").upper() == "NE4")
print("osm ways: major", len(MAJOR), "city", len(CITY), "rail", len(RAIL), "water", len(WATER), "| nh48", len(NH48), "sring", len(SRING), "bdk", len(BDK), "dme", len(DME))

# ---------- camera ----------
OVR = (-62, 22, 150)          # overview: the whole Ajmer Road, Jaipur → Ajmer/Pushkar
WIDE = (-25, -12, 235)        # wider still: Kotputli and Bandikui in frame
CAMS = []                     # (t0, t1, view_from, view_to)
CUR = [OVR]
def sc(v): return 1080 / (v[2] * KM)
def cam(t, v, d=1.0):
    CAMS.append((round(t, 2), round(t + d, 2), CUR[0], v)); CUR[0] = v
def view_at(t):
    v = CAMS[0][2] if CAMS else OVR
    for a, b, v0, v1 in CAMS:
        if t >= b: v = v1
        elif t >= a: return v1
    return v
def scr(p, v): s = sc(v); return (540 + (p[0] - v[0]) * KM * s, 875 + (p[1] - v[1]) * KM * s)
def cam_js(rel0):
    js = []
    def put(t, d, v):
        s = sc(v); tr = f"translate(540 785) scale({s:.5f}) translate({-v[0]*KM:.2f} {-v[1]*KM:.2f})"
        js.append(f'      tl.to("#mp-W", {{ "--s": {s:.5f}, "--cx": {v[0]*KM:.2f}, "--cy": {v[1]*KM:.2f}, duration: {d:.3f}, ease: "none" }}, {t:.3f});\n')
        js.append(f'      tl.to("#mp-G", {{ attr: {{ transform: "{tr}" }}, "--s": {s:.5f}, duration: {d:.3f}, ease: "none" }}, {t:.3f});\n')
    for a, b, v0, v1 in CAMS:
        N = 10; s0, s1 = sc(v0), sc(v1)
        for i in range(N):
            u0, u1 = i / N, (i + 1) / N
            e = lambda u: 0.5 - 0.5 * math.cos(math.pi * u)            # ease in-out over the move
            ta, tb = a + (b - a) * e(u0), a + (b - a) * e(u1)
            s = s0 * (s1 / s0) ** u1                                     # geometric zoom
            f = u1 if abs(s1 - s0) < 1e-9 else (1 / s - 1 / s0) / (1 / s1 - 1 / s0)
            v = (v0[0] + (v1[0] - v0[0]) * f, v0[1] + (v1[1] - v0[1]) * f, 1080 / (s * KM))
            put(ta - rel0, tb - ta, v)
    return "".join(js)

# ---------- world layers ----------
SVG, HTML, JS = [], [], []
def layer(svg): SVG.append(svg)
CORE_PTS = CORE
layer(f'<path d="{pd(CORE_PTS, True)}" style="fill:rgba(243,231,211,0.08);stroke:rgba(243,231,211,0.18);stroke-width:1.5"/>')
for t, p in WATER:
    layer(f'<path d="{pd(rdp(p, 0.05), True)}" style="fill:rgba(96,165,214,0.55);stroke:rgba(127,200,248,0.8);stroke-width:1.2"/>')
for t, p in RAIL:
    layer(f'<path d="{pd(rdp(p, 0.08))}" style="fill:none;stroke:rgba(200,180,160,0.30);stroke-width:1.2;stroke-dasharray:5 4"/>')
for t, p in CITY:
    layer(f'<path d="{pd(rdp(p, 0.03))}" style="fill:none;stroke:rgba(243,231,211,0.16);stroke-width:1"/>')
for t, p in MAJOR:
    w = 2.6 if t.get("highway") == "motorway" else 2.0
    layer(f'<path d="{pd(rdp(p, 0.05))}" style="fill:none;stroke:rgba(243,231,211,0.42);stroke-width:{w}"/>')
if not MAJOR:   # fallback when OpenStreetMap was unreachable: schematic radials
    for r in ("ajmer", "tonk", "sikar", "delhiNH", "agra", "nh48w"): layer(f'<path d="{pd(ROADS[r])}" style="fill:none;stroke:rgba(243,231,211,0.35);stroke-width:2"/>')
layer(f'<path d="{pd(WALL, True)}" style="fill:rgba(232,102,74,0.35);stroke:#E8664A;stroke-width:1.5"/>')

def route(rid, segs, start, t0, d, color="#F5B04A", width=6, halo=18, dash=None, op=1.0):
    """Highlight a route made of OSM way segments: each segment draws in order of its distance from `start`."""
    if not segs: return ""
    st = K(start) if isinstance(start, str) else start
    def dist(p): return math.hypot(p[0] - st[0], p[1] - st[1])
    items = []
    for p in segs:
        p = rdp(p, 0.04)
        if dist(p[0]) > dist(p[-1]): p = p[::-1]
        items.append((dist(p[0]), dist(p[-1]), p))
    lo = min(a for a, _, _ in items); hi = max(b for _, b, _ in items) or 1
    js = ""
    for k, (a, b, p) in enumerate(items):
        da = "" if not dash else f"stroke-dasharray:{dash};"
        SVG.append(f'<g id="mp-{rid}{k}" style="opacity:0"><path d="{pd(p)}" style="fill:none;stroke:{color};stroke-opacity:0.28;stroke-width:{halo};stroke-linecap:round"/>'
                   f'<path class="dr" pathLength="1" d="{pd(p)}" style="fill:none;stroke:{color};stroke-width:{width};stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/></g>')
        ta = t0 + d * (a - lo) / (hi - lo); tb = max(ta + 0.15, t0 + d * (b - lo) / (hi - lo))
        js += f'      tl.set("#mp-{rid}{k}", {{ opacity: {op} }}, {ta:.3f});\n      tl.fromTo("#mp-{rid}{k} .dr", {{ strokeDashoffset: 1 }}, {{ strokeDashoffset: 0, duration: {tb - ta:.3f}, ease: "none" }}, {ta:.3f});\n'
    return js
def route_fx(rid, n, t, kind):
    """Pulse (highlight) or dim an already-drawn route."""
    sels = ", ".join(f'"#mp-{rid}{k}"' for k in range(n))
    if kind == "pulse": return f'      tl.fromTo([{sels}], {{ opacity: 1, filter: "brightness(1)" }}, {{ opacity: 1, filter: "brightness(1.8)", duration: 0.4, yoyo: true, repeat: 3, immediateRender: false }}, {t:.3f});\n'
    return f'      tl.to([{sels}], {{ opacity: {kind}, duration: 0.4 }}, {t:.3f});\n'
def sch(rid, pts, t0, d, color="#B8E07A", width=6, dash="10 8"):
    """Schematic (proposed) route: dashed line revealed along its length with a moving clip of its solid twin."""
    pts = [K(p) if isinstance(p, str) else p for p in pts]
    SVG.append(f'<g id="mp-{rid}" style="opacity:0"><path d="{pd(pts)}" style="fill:none;stroke:{color};stroke-opacity:0.25;stroke-width:16;stroke-linecap:round"/>'
               f'<path class="dr" pathLength="1" d="{pd(pts)}" style="fill:none;stroke:{color};stroke-width:{width};stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>'
               (f'<path class="ds" d="{pd(pts)}" style="fill:none;stroke:#120D0A;stroke-width:{width + 1};stroke-dasharray:{dash};opacity:0"/>' if dash != "1 0" else "") + '</g>')
    return (f'      tl.set("#mp-{rid}", {{ opacity: 1 }}, {t0:.3f});\n      tl.fromTo("#mp-{rid} .dr", {{ strokeDashoffset: 1 }}, {{ strokeDashoffset: 0, duration: {d:.3f}, ease: "power1.inOut" }}, {t0:.3f});\n'
            f'      tl.to("#mp-{rid} .ds", {{ opacity: 1, duration: 0.3 }}, {t0 + d:.3f});\n')
LBL = {}
def label(rid, at, text, t, tier="minor", dx=16, dy=-24, amb=True, size=30, right=False, until=None):
    """Counter-scaled label + dot in the world. 'major' labels persist (what we've covered stays visible)."""
    p = K(at) if isinstance(at, str) else at
    cls = "tag amb" if amb else "tag"
    tx = f"translate(calc(-100% - {dx}px), {dy}px)" if right else f"translate({dx}px, {dy}px)"
    rid = "L" + rid
    HTML.append(f'<div class="lb" id="mp-{rid}" style="left:{p[0]*KM:.1f}px;top:{p[1]*KM:.1f}px;opacity:0"><i class="pd"></i>'
                f'<div class="{cls}" style="position:absolute;left:0;top:0;transform:{tx};font-size:{size}px;padding:8px 16px">{text}</div></div>')
    LBL[rid] = (tier, t)
    js = f'      tl.fromTo("#mp-{rid}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35 }}, {t:.3f});\n      tl.fromTo("#mp-{rid} .pd", {{ scale: 0 }}, {{ scale: 1, duration: 0.4, ease: "back.out(2.5)" }}, {t:.3f});\n'
    if until is not None:
        js += (f'      tl.to("#mp-{rid} .tag", {{ opacity: 0, duration: 0.3 }}, {until:.3f});\n      tl.to("#mp-{rid} .pd", {{ scale: 0.6, opacity: 0.8, duration: 0.3 }}, {until:.3f});\n'
               if tier == "major" else f'      tl.to("#mp-{rid}", {{ opacity: 0, duration: 0.3 }}, {until:.3f});\n')
    return js
def ring(rid, at, r_km, t, color="#F5B04A", until=None):
    p = K(at) if isinstance(at, str) else at
    SVG.append(f'<circle id="mp-{rid}" cx="{p[0]*KM:.1f}" cy="{p[1]*KM:.1f}" r="{r_km*KM:.1f}" style="fill:{color};fill-opacity:0.18;stroke:{color};stroke-width:3;opacity:0"/>')
    js = f'      tl.fromTo("#mp-{rid}", {{ opacity: 0, attr: {{ r: 0 }} }}, {{ opacity: 1, attr: {{ r: {r_km*KM:.1f} }}, duration: 0.6, ease: "back.out(1.6)" }}, {t:.3f});\n'
    if until is not None: js += f'      tl.to("#mp-{rid}", {{ opacity: 0, duration: 0.4 }}, {until:.3f});\n'
    return js

# ---------- screen overlays (pop-ups, news, chips) ----------
OVL = []
TL, TR, BL, BR = (48, 360), (632, 360), (48, 1090), (632, 1090)
def popup(rid, src, at, t_on, t_off, cap, box=TL, w=400, h=260, img=None, sub=None):
    p = K(at) if isinstance(at, str) else at; x, y = scr(p, view_at(t_on + 0.01 + R0))
    bx, by = box
    ax = min(max(x, bx + 20), bx + w - 20); ay = by + h if y > by + h else (by if y < by else by + h / 2)
    if by <= y <= by + h: ax = bx + w if x > bx + w else bx
    media = (f'<img src="{IMG}{img}" style="width:100%;height:100%;object-fit:cover;display:block"/>' if img else
             f'<video id="mp-{rid}v" class="clip" src="assets/broll/{src}.mp4" data-start="{max(0, round(t_on - 0.1, 2))}" data-duration="{round(t_off - t_on + 0.5, 2)}" muted playsinline style="width:100%;height:100%;object-fit:cover"></video>')
    sb = f'<div style="font-weight:600;font-size:24px;color:#E8D9BF;margin-top:2px">{sub}</div>' if sub else ""
    OVL.append(f'<svg id="mp-{rid}l" data-layout-allow-overlap style="position:absolute;left:0;top:-90px;width:1080px;height:1920px;overflow:visible;opacity:0;pointer-events:none"><path d="M{ax:.0f} {ay:.0f} L{x:.0f} {y:.0f}" style="stroke:#F5B04A;stroke-width:3;fill:none"/><circle cx="{x:.0f}" cy="{y:.0f}" r="7" style="fill:#F5B04A"/></svg>'
               f'<div id="mp-{rid}" data-layout-allow-overlap style="position:absolute;left:{bx}px;top:{by - 90}px;width:{w}px;height:{h}px;border-radius:16px;overflow:hidden;border:3px solid #F5B04A;box-shadow:0 12px 32px rgba(0,0,0,0.65);background:#1B140F;opacity:0">{media}'
               f'<div style="position:absolute;left:0;right:0;bottom:0;padding:26px 14px 8px;background:linear-gradient(180deg,rgba(18,13,10,0),rgba(18,13,10,.92));font-family:Inter,sans-serif;font-weight:800;font-size:32px;line-height:1.1;color:#F3E7D3">{cap}{sb}</div></div>')
    sel = f"#mp-{rid}"
    return (f'      tl.fromTo("{sel}", {{ opacity: 0, scale: 0.6, transformOrigin: "50% 100%" }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "back.out(1.6)" }}, {t_on:.3f});\n'
            f'      tl.fromTo("{sel}l", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, {t_on:.3f});\n'
            f'      tl.to(["{sel}", "{sel}l"], {{ opacity: 0, scale: 0.9, duration: 0.3, ease: "power2.in" }}, {t_off:.3f});\n')
def popups(items, end):
    js = ""
    for k, it in enumerate(items):
        rid, src, at, t, cap, box = it[:6]; img = it[6] if len(it) > 6 else None; sub = it[7] if len(it) > 7 else None
        wh = it[8] if len(it) > 8 else (400, 260)
        t_off = items[k + 1][3] + 0.1 if k + 1 < len(items) else end
        js += popup(rid, src, at, t, t_off, cap, box=box, img=img, sub=sub, w=wh[0], h=wh[1])
    return js
def news(rid, outlet, date, headline, t_on, t_off, top=360):
    OVL.append(f'<div id="mp-{rid}" data-layout-allow-overlap style="position:absolute;left:70px;right:70px;top:{top - 90}px;padding:22px 30px 20px;background:#F2EBDD;border-radius:8px;box-shadow:0 14px 36px rgba(0,0,0,0.6);transform:rotate(-1deg);opacity:0">'
               f'<div style="display:flex;justify-content:space-between;align-items:baseline;border-bottom:2px solid #1B140F;padding-bottom:8px;margin-bottom:12px;font-family:Inter,sans-serif;color:#1B140F">'
               f'<span style="font-weight:900;font-size:34px">{outlet}</span><span style="font-family:JetBrains Mono,monospace;font-size:26px">{date}</span></div>'
               f'<div style="font-family:Instrument Serif,serif;font-size:50px;line-height:1.08;color:#1B140F">“{headline}”</div>'
               f'<div style="font-family:JetBrains Mono,monospace;font-size:22px;color:#5A4A3A;margin-top:10px">Headline as published · card recreated for this video</div></div>')
    return (f'      tl.fromTo("#mp-{rid}", {{ opacity: 0, y: -30, rotation: -4 }}, {{ opacity: 1, y: 0, rotation: -1, duration: 0.5, ease: "back.out(1.4)" }}, {t_on:.3f});\n'
            f'      tl.to("#mp-{rid}", {{ opacity: 0, y: -20, duration: 0.3, ease: "power2.in" }}, {t_off:.3f});\n')
def chip(rid, kicker, text, t_on, t_off, y=1205, left=64, right=64):
    OVL.append(f'<div id="mp-{rid}" style="position:absolute;left:{left}px;right:{right}px;top:{y - 90}px;padding:16px 24px;border-radius:18px;background:rgba(18,13,10,0.94);border:1.5px solid #E3A23B;opacity:0">'
               f'<div class="lbl" style="color:#E3A23B;font-size:26px">{kicker}</div><div style="font-family:Inter,sans-serif;font-weight:700;font-size:33px;line-height:1.2;color:#F3E7D3;margin-top:4px">{text}</div></div>')
    return f'      IN("#mp-{rid}", {t_on:.3f});\n      tl.to("#mp-{rid}", {{ opacity: 0, duration: 0.3 }}, {t_off:.3f});\n'
def logo_badge(rid, at, files, t_on, t_off, dx=0, dy=60, h=54, text=None):
    p = K(at) if isinstance(at, str) else at; x, y = scr(p, view_at(t_on + 0.01 + R0))
    inner = "".join(f'<img src="{IMG}{f}" style="height:{h}px;width:auto;display:block"/>' for f in files) + (f'<span style="font-family:Inter,sans-serif;font-weight:800;font-size:30px;color:#1B140F">{text}</span>' if text else "")
    OVL.append(f'<div id="mp-{rid}" style="position:absolute;left:{x + dx:.0f}px;top:{y + dy - 90:.0f}px;display:flex;gap:12px;align-items:center;padding:12px 18px;border-radius:14px;background:#FFFFFF;box-shadow:0 8px 24px rgba(0,0,0,0.5);opacity:0">{inner}</div>')
    return f'      tl.fromTo("#mp-{rid}", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2)" }}, {t_on:.3f});\n      tl.to("#mp-{rid}", {{ opacity: 0, duration: 0.3 }}, {t_off:.3f});\n'
NOTES = []
def note(t_on, t_off, text): NOTES.append((t_on, t_off, text)); return ""
R0 = 2.3                      # the map composition starts here (after the poster + a beat of the speaker's face)
def r(t): return round(t - R0, 3)
FACE = [(31.45, 32.35), (88.55, 89.35), (126.85, 127.75)]   # short face breaks inside the map run

# ---------- 0 · poster (0–1.15), then the speaker for a beat (1.15–2.3) ----------
cv = Map("cv", -62, 22, 140)
cv.svg.append(f'<g style="stroke:rgba(243,231,211,0.05);stroke-width:{cv.u}">' + "".join(f'<path d="M{x} -120 V160"/>' for x in range(-150, 40, 10)) + "</g>")
for t, p in MAJOR: cv.svg.append(f'<path d="{smooth(rdp(p, 0.3), False) if len(rdp(p, 0.3)) > 1 else ""}" style="fill:none;stroke:rgba(243,231,211,0.22);stroke-width:{2*cv.u}"/>')
for t, p in WATER: cv.svg.append(f'<path d="{"M" + " L".join(f"{q[0]:.2f} {q[1]:.2f}" for q in rdp(p, 0.1)) + " Z"}" style="fill:rgba(96,165,214,0.5)"/>')
cv.svg.append(f'<path d="{smooth(CORE)}" style="fill:rgba(243,231,211,0.10);stroke:rgba(243,231,211,0.3);stroke-width:{2*cv.u}"/>')
for p in (NH48 or [ROADS["nh48w"]]): cv.svg.append(f'<path d="{"M" + " L".join(f"{q[0]:.2f} {q[1]:.2f}" for q in rdp(p, 0.1))}" style="fill:none;stroke:#F5B04A;stroke-width:{12*cv.u};stroke-linecap:round;filter:url(#cv-glow)"/>')
cv.svg.append(f'<path d="{smooth([K("ajmer"), K("pushkar")], False)}" style="fill:none;stroke:#F5B04A;stroke-width:{7*cv.u};stroke-linecap:round;filter:url(#cv-glow)"/>')
for k, (key, lab, dx, dy) in enumerate([("hirapura", "JAIPUR", -40, 40), ("bagru", "BAGRU", -60, 40), ("dudu", "DUDU", -40, 40), ("kishangarh", "KISHANGARH", -110, 40), ("ajmer", "AJMER", -30, 44), ("pushkar", "PUSHKAR", -60, -80)]):
    cv.dot(key, big=True)
    cv.html.append(f'<div class="tag amb" style="left:{min(870, max(48, cv.px(K(key))[0] + dx)):.0f}px;top:{cv.px(K(key))[1] + dy - 90:.0f}px;font-size:30px;padding:8px 16px">{lab}</div>')
cv.html.append('<div style="position:absolute;left:70px;right:70px;top:250px;font-family:Inter,sans-serif;font-weight:900;font-size:170px;line-height:0.92;letter-spacing:-0.01em;color:#F3E7D3;text-shadow:0 8px 40px rgba(0,0,0,0.6)">AJMER<br><span style="color:#F5B04A">ROAD</span></div>'
               '<div style="position:absolute;left:76px;right:70px;top:620px;font-family:Inter,sans-serif;font-weight:800;font-size:52px;line-height:1.1;color:#F3E7D3">Jaipur → Ajmer<br>every stretch, decoded</div>'
               '<div style="position:absolute;left:76px;top:1210px;padding:12px 22px;border-radius:14px;background:rgba(60,38,14,0.92);border:2px solid #E3A23B;font-family:Inter,sans-serif;font-weight:800;font-size:40px;color:#F3E7D3">NH-48 · 9 stretches · 2 new expressways</div>')
cv.render(0, 1.15, "", note="Map data © OpenStreetMap contributors", keep=False, fade_in=False)

# ---------- the map run (2.3 → 147.4) ----------
js = ""
# overview: the whole road draws, key towns appear
js += route("nh", NH48 or [ROADS["nh48w"]], "hirapura", r(2.45), 1.6, width=7, halo=20)
for k, (key, lab, t, dx, dy, right) in enumerate([("hirapura", "Jaipur", 2.6, 16, -60, True), ("bagru", "Bagru", 2.9, 16, 10, False), ("dudu", "Dudu", 3.1, 16, 10, False),
                                                   ("kishangarh", "Kishangarh", 3.3, 16, 10, False), ("ajmer", "Ajmer", 3.5, 16, 10, False), ("pushkar", "Pushkar", 3.6, 16, -60, False)]):
    js += label(f"o{k}", key, lab, r(t), tier="major", dx=dx, dy=dy, right=right, size=28)
js += label("sbl", km(26.95, 75.08), "Sambhar Lake", r(3.7), tier="major", amb=False, size=26, dx=16, dy=-60)
# stretch 1 (zoom in)
S1 = (-12, 5.4, 10); cam(3.8, S1, 1.1)
js += label("p1", "hirapura", "Hirapura bus terminal", r(4.9), until=r(30.4), dx=16, dy=10, size=28)
js += label("p2", "keshopura", "Keshopura", r(6.5), until=r(30.4), dx=16, dy=-70)
js += label("p3", "westway", "Westway Heights", r(7.7), until=r(30.4), dx=16, dy=-80)
js += label("p4", "bhankrota", "Bhankrota", r(8.7), until=r(30.4), dx=16, dy=-80, right=True)
js += label("p5", "vrb", "VRB Golden Tower · upcoming", r(12.2), until=r(23.3), dx=16, dy=20, size=26, amb=False)
js += label("p6", "pinkwest", "Manglam PinkWest", r(13.8), until=r(23.3), dx=16, dy=-20, size=26, amb=False)
js += popup("q0", None, "hirapura", r(5.0), r(12.1), "Hirapura bus terminal", box=BR, img="busterminal.jpg", sub="Photo", w=400, h=300) if os.path.exists(f"{P}/assets/img/busterminal.jpg") else popup("q0", "freeway", "hirapura", r(5.0), r(12.1), "Bus terminal", box=BR)
js += popup("pv", None, "vrb", r(12.3), r(16.9), "VRB Golden Tower", w=330, h=590, img="vrb.jpg", sub="Developer render · supplied", box=(700, 800))
js += popup("pp", None, "pinkwest", r(13.9), r(20.9), "Manglam PinkWest", w=430, h=430, img="pinkwest.jpg", sub="Developer render · supplied", box=(48, 980))
js += news("n1", "Construction World", "", "Manglam Group Launches Rs 1,000 Cr PinkWest in West Jaipur", r(14.6), r(17.0))
js += popups([("q2", "freeway", "hirapura", r(17.0), "Transport anchor", BR), ("q3", "market", "pinkwest", r(21.2), "Shops", BL),
              ("q4", "office", "vrb", r(21.8), "Offices", BR), ("q5", "dining", "westway", r(22.6), "Services", BL)], r(23.3))
# 200-ft bypass junction (zoom further in)
J = (K("hirapura")[0], K("hirapura")[1] + 0.2, 3.2); cam(23.4, J, 0.9)
for k, (pts, col, t) in enumerate([([km(26.8915, 75.717), km(26.8905, 75.733), km(26.8880, 75.744), km(26.8860, 75.758)], "#F5B04A", 26.0), ([km(26.8870, 75.757), km(26.8890, 75.745), km(26.8912, 75.732), km(26.8922, 75.716)], "#F5B04A", 26.3),
                                    ([km(26.912, 75.7425), km(26.8895, 75.7378), km(26.866, 75.733)], "#7FC8F8", 26.9), ([km(26.866, 75.7355), km(26.8888, 75.7400), km(26.911, 75.7450)], "#7FC8F8", 27.2)]):
    SVG.append(f'<path id="mp-fx{k}" class="dr" pathLength="1" d="{pd(pts)}" style="fill:none;stroke:{col};stroke-width:9;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>')
    js += f'      tl.fromTo("#mp-fx{k}", {{ strokeDashoffset: 1 }}, {{ strokeDashoffset: 0, duration: 0.8, ease: "power2.inOut" }}, {r(t)});\n      tl.to("#mp-fx{k}", {{ opacity: 0, duration: 0.4 }}, {r(30.4)});\n'
js += label("j3", km(26.8935, 75.722), "▲ 2 flyovers", r(26.1), until=r(30.4), dx=0, dy=-70, size=30)
js += label("j4", km(26.870, 75.733), "▼ 2 underpasses", r(27.0), until=r(30.4), dx=16, dy=-60, size=30, amb=False)
bypass_img = os.path.exists(f"{P}/assets/img/bypass.jpg")
js += popup("qj", None if bypass_img else "avenue", "hirapura", r(24.4), r(27.7), "200-ft Bypass" if bypass_img else "Flyovers", box=BL, img="bypass.jpg" if bypass_img else None, sub="Photo" if bypass_img else None, w=440 if bypass_img else 400, h=300 if bypass_img else 260)
js += news("n2", "Construction World", "Mar 2026", "NHAI Awards Contract for Flyovers and Underpasses at Jaipur Junction", r(27.8), r(31.2))
js += chip("c2", "Awarded · NHAI (EPC)", "₹130.65 cr · signal-free junction on NH-48", r(28.6), r(31.2))
# → overview → Mahapura + Southern Ring Road (highlighted while he talks about it)
cam(30.6, OVR, 0.85)
M = (-4, 11, 42); cam(32.35, M, 1.1)
js += label("m0", "mahapura", "Mahapura", r(32.4), tier="major", until=r(47.0), dx=16, dy=-70, right=True)
js += ring("mr", "mahapura", 1.4, r(32.4), until=r(39.4))
js += route("sr", SRING or [ROADS["sring"]], "mahapura", r(34.1), 3.6, color="#F5B04A", width=6, halo=20)
js += label("m1", "SRL", "SOUTHERN RING ROAD · existing", r(34.6), tier="minor", until=r(47.0), dx=16, dy=40, size=28) if False else ""
js += label("m1", km(26.745, 75.850), "SOUTHERN RING ROAD · existing", r(34.6), until=r(39.4), dx=-180, dy=40, size=28)
js += label("m2", km(26.765, 75.800), "Tonk Rd", r(36.9), until=r(39.4), dx=16, dy=10, amb=False)
js += label("m3", "bagrana", "Bagrana · Agra Rd", r(37.8), tier="major", until=r(47.0), dx=16, dy=10)
js += popups([("qm0", "cityhwy", "mahapura", r(33.6), "Ring Road link", TR), ("qm1", "hwysun", "bagrana", r(37.9), "Agra Road", BL)], r(39.4))
# → zoom out east: the Bandikui link and the Delhi–Mumbai Expressway
E = (30, -5, 130); cam(39.4, E, 1.1)
js += route("bk", BDK or [ROADS["bdk"]], "bagrana", r(40.4), 1.4, color="#F5B04A", width=6, halo=18)
js += label("e0", km(26.97, 76.25), "Jaipur–Bandikui link", r(40.8), until=r(47.0), dx=-120, dy=40, size=28)
js += label("e1", "bandikui", "Bandikui", r(41.6), tier="major", until=r(47.0), dx=16, dy=10)
js += route("dm", DME or [ROADS["dme"]], "bandikui", r(42.4), 1.4, color="#7FC8F8", width=6, halo=18)
js += label("e2", km(27.45, 76.75), "Delhi–Mumbai Expressway", r(42.8), until=r(47.0), dx=-330, dy=-40, size=28)
js += route_fx("nh", len(NH48 or [1]), r(44.4), "pulse")
js += news("n3", "Swarajya", "Jul 2025", "Bagrana–Bandikui link of Delhi–Mumbai Expressway opens to reduce Jaipur–Delhi travel time to 3.5 hours", r(44.9), r(47.3))
js += popup("qe", "hwypov", "bandikui", r(41.7), r(44.8), "Expressway link", box=BR)
# → overview → Chitroli + Northern Ring Road (proposed), highlighted while he talks about it
cam(47.1, OVR, 0.8)
N = (-6, -4, 64); cam(47.9, N, 1.0)
js += label("n0", "chitroli", "Chitroli", r(48.1), tier="major", until=r(66.0), dx=16, dy=-70, right=True)
js += ring("nr0", "chitroli", 1.4, r(48.1), color="#B8E07A", until=r(59.2))
js += route_fx("sr", len(SRING or [1]), r(48.0), 0.35)
js += sch("nring", ROADS["nring"], r(51.8), 6.2)
js += label("n1", km(27.05, 75.60), "NORTHERN RING ROAD · proposed", r(52.2), until=r(59.2), dx=-120, dy=-90, size=28)
for k, (key, lab, t, dx, dy) in enumerate([("kalwar", "Kalwar Rd", 55.1, -40, 20), (km(27.110, 75.700), "Sikar Rd", 56.2, -30, -70), (km(27.135, 75.830), "Delhi Rd", 57.1, -10, -70), (km(27.020, 75.985), "Agra Rd", 58.0, -160, 20)]):
    js += label(f"n{k+2}", key, lab, r(t), until=r(59.2), dx=dx, dy=dy, amb=False, size=28)
js += news("n4", "Patrika", "Dec 2025", "Jaipur Northern Ring Road project: land measurement and survey for 99 km ring begins", r(50.3), r(53.6))
js += popup("qn", "build", "chitroli", r(49.0), r(50.2), "Proposed link", box=TR)
# Mahapura (southern) vs Chitroli (northern) — each highlighted as it is named
C = (-19, 7.6, 26); cam(59.25, C, 0.9)
js += route_fx("sr", len(SRING or [1]), r(59.3), 1) + route_fx("sr", len(SRING or [1]), r(59.4), "pulse") + ring("cm", "mahapura", 1.3, r(59.4), until=r(66.0))
js += f'      tl.to("#mp-nring", {{ opacity: 0.35, duration: 0.3 }}, {r(59.3)});\n      tl.to("#mp-nring", {{ opacity: 1, duration: 0.3 }}, {r(60.0)});\n'
js += label("cm2", "mahapura", "Mahapura · southern", r(59.4), until=r(66.0), dx=16, dy=-80) + label("cc2", "chitroli", "Chitroli · northern", r(60.0), until=r(66.0), dx=16, dy=40, right=True)
js += ring("cc", "chitroli", 1.3, r(60.0), color="#B8E07A", until=r(66.0))
js += chip("c6a", "Mahapura · existing", "Southern Ring Road · serves the southern corridor", r(62.0), r(66.0), y=1205)
js += route_fx("sr", len(SRING or [1]), r(62.3), "pulse")
js += f'      tl.fromTo("#mp-nring", {{ filter: "brightness(1)" }}, {{ filter: "brightness(1.9)", duration: 0.4, yoyo: true, repeat: 3, immediateRender: false }}, {r(64.3)});\n'
js += chip("c6b", "Chitroli · proposed", "Northern Ring Road · its Ajmer Road end (as reported)", r(64.3), r(66.0), y=360)
# → overview → Mahindra World City
cam(66.0, OVR, 0.8)
W_ = (-19.5, 14, 20); cam(67.5, W_, 0.9)
js += f'      tl.to("#mp-nring", {{ opacity: 0.35, duration: 0.4 }}, {r(66.0)});\n'
js += ring("wr", "mwc", 2.2, r(68.4), color="#7FC8F8", until=r(77.0))
js += label("w0", "mwc", "Mahindra World City", r(68.4), tier="major", until=r(77.0), dx=16, dy=-80)
js += label("w1", "kalwara", "Kalwara", r(71.0), until=r(77.0), dx=-90, dy=10, right=True, amb=False)
ldb = os.path.exists(f"{P}/assets/img/logo_db.png"); lin = os.path.exists(f"{P}/assets/img/logo_infosys.png")
js += logo_badge("wl", "mwc", ["logo_infosys.png"], r(72.5), r(77.0), dx=-330, dy=150, h=56)
js += chip("c7", "Employment anchor", "SEZ · Infosys and Deutsche Bank were its first anchor clients", r(75.1), r(77.0))
js += popups([("qw0", "corporate", "mwc", r(68.6), "IT & business park", TL), ("qw1", None, "mwc", r(73.3), "Deutsche Bank", TR, "deutsche.jpg", "Image supplied", (420, 280)), ("qw2", "coworkers", "mwc", r(75.3), "Jobs", TL)], r(77.0))
# → overview → Dehmi Kalan · Manipal University
cam(77.0, OVR, 0.7)
U = (-26, 9, 14); cam(77.7, U, 0.9)
js += ring("ur", "manipal", 1.2, r(79.5), color="#7FC8F8", until=r(88.0))
js += label("u0", "manipal", "Manipal University · Dehmi Kalan", r(78.0), tier="major", until=r(88.0), dx=16, dy=-80, size=28)
for k, (txt, t) in enumerate([("◆ Student accommodation", 81.6), ("◆ Rental housing", 82.8), ("◆ Food outlets", 83.8), ("◆ Everyday retail", 85.5)]):
    OVL.append(f'<div class="tag amb" id="mp-uw{k}" style="left:60px;top:{1150 + k * 62 - 90}px;font-size:30px;padding:10px 18px;opacity:0">{txt}</div>')
    js += f'      IN("#mp-uw{k}", {r(t)});\n      tl.to("#mp-uw{k}", {{ opacity: 0, duration: 0.3 }}, {r(88.0)});\n'
muj = os.path.exists(f"{P}/assets/img/manipal.jpg")
js += popups([("qu0", None if muj else "campus", "manipal", r(79.6), "Manipal University Jaipur" if muj else "Campus", TL) + (("manipal.jpg", "Image supplied", (470, 345)) if muj else ()),
              ("qu1", "students", "manipal", r(81.6), "Student accommodation", TR), ("qu2", "rental", "manipal", r(82.8), "Rental housing", TL),
              ("qu3", "dining", "manipal", r(83.8), "Food outlets", TR), ("qu4", "market", "manipal", r(85.5), "Everyday retail", TL)], r(88.0))
# → overview (face beat) → Bagru
cam(88.0, OVR, 0.55)
B = (K("bagru")[0], K("bagru")[1], 22); cam(89.35, B, 0.9)
js += ring("br", "bagru", 2.0, r(89.6), color="#E8664A", until=r(97.0))
js += label("b0", "bagru", "Bagru industrial belt", r(89.6), tier="major", until=r(97.0), dx=16, dy=-80)
js += popups([("qb0", "factory", "bagru", r(90.4), "Industrial belt", TR), ("qb1", None, "bagru", r(91.9), "Bagru block printing", TL, "block.jpg", "Photo · Anildiggiwal, CC0", (470, 320))], r(97.0))
js += chip("c9", "Heritage craft", "Hand block printing on textiles · Bagru", r(93.7), r(97.0))
# → overview → Mahla … Dudu, roads to Phulera, Narena, Sambhar (the lake)
cam(97.0, OVR, 0.7)
D = (-60, 12, 62); cam(97.7, D, 0.9)
for k, (key, lab, t, dx, dy) in enumerate([("mahla", "Mahla", 98.5, 16, -70), ("mokhampura", "Mokhampura", 99.2, 16, 20), ("dudu", "Dudu", 100.1, 16, 10)]):
    js += label(f"d{k}", key, lab, r(t), tier="major" if key == "dudu" else "minor", until=None if key == "dudu" else r(116.0), dx=dx, dy=dy)
for k, (rr, key, lab, t, dx, dy) in enumerate([("phulera", "phulera", "Phulera", 102.7, 16, -40), ("narena", "narena", "Narena", 103.6, 16, 20), ("sambhar", "sambhar", "Sambhar", 104.5, 16, -60)]):
    js += sch(f"dr{k}", ROADS[rr], r(t) - 0.3, 0.7, color="#B8E07A", width=5, dash="1 0") + label(f"ds{k}", key, lab, r(t), until=r(116.0), dx=dx, dy=dy, amb=False)
js += popup("qph", None, "phulera", r(102.8), r(104.5), "Dry port · Phulera", box=TR, img="dryport.jpg", sub="Image supplied", w=420, h=360)
js += f'      tl.fromTo("#mp-Lsbl .tag", {{ scale: 1 }}, {{ scale: 1.25, duration: 0.4, yoyo: true, repeat: 1 }}, {r(104.6)});\n'
fl = os.path.exists(f"{P}/assets/img/flamingos.jpg")
js += popup("qd9", None if fl else "flamingos", km(26.93, 75.10), r(104.6), r(108.8), "Sambhar Lake · flamingos", box=BL, img="flamingos.jpg" if fl else None, sub="Photo" if fl else "Representative footage", w=470, h=320)
for k, (txt, t) in enumerate([("◆ Warehouses", 108.9), ("◆ Highway services", 109.7), ("◆ Larger land parcels", 111.6), ("◆ Tourism-linked businesses", 112.9)]):
    OVL.append(f'<div class="tag amb" id="mp-dw{k}" style="left:48px;top:{1150 + k * 62 - 90}px;font-size:30px;padding:10px 18px;opacity:0">{txt}</div>')
    js += f'      IN("#mp-dw{k}", {r(t)});\n      tl.to("#mp-dw{k}", {{ opacity: 0, duration: 0.3 }}, {r(116.0)});\n'
js += popups([("qd0", "warehouse", "dudu", r(108.9), "Warehouses", TR), ("qd1", "hwypov", "dudu", r(109.7), "Highway services", TL),
              ("qd2", "fields", "dudu", r(111.6), "Larger land parcels", TR), ("qd3", "rental", "sambhar", r(112.9), "Tourism-linked stays", TL)], r(116.0))
# → overview → Bandar Sindri, Kishangarh (marble), airport, Ajmer, Pushkar
cam(116.0, OVR, 0.6)
KG = (-108, 42, 58); cam(116.6, KG, 0.9)
js += label("k0", "bandarsindri", "Bandar Sindri", r(116.8), until=r(126.2), dx=16, dy=-70)
js += f'      tl.fromTo("#mp-Lo3 .pd", {{ scale: 1 }}, {{ scale: 1.8, duration: 0.35, yoyo: true, repeat: 1 }}, {r(118.1)});\n'
js += label("k2", "kgairport", "✈ Kishangarh Airport", r(120.8), until=r(126.2), dx=16, dy=-80, right=True, amb=False)
js += f'      tl.fromTo(["#mp-Lo4 .pd", "#mp-Lo5 .pd"], {{ scale: 1 }}, {{ scale: 1.8, duration: 0.35, yoyo: true, repeat: 1, stagger: 0.6 }}, {r(123.5)});\n'
js += chip("c11", "Kishangarh", "Known as a marble trading &amp; processing hub", r(119.4), r(126.2))
mb = os.path.exists(f"{P}/assets/img/marble.jpg")
js += popups([("qk0", None if mb else "marble", "kishangarh", r(119.1), "Marble quarry" if mb else "Marble trade", (560, 360)) + (("marble.jpg", "Image supplied", (470, 316)) if mb else ()),
              ("qk1", "camels", "pushkar", r(124.4), "Tourism · Pushkar", TL)], r(126.2))
# → wide view (face beat) → proposed Kotputli–Kishangarh expressway
cam(126.2, WIDE, 0.6)
js += label("x0", "kotputli", "Kotputli", r(128.0), tier="major", dx=16, dy=-20)
js += sch("kk", ROADS["kk"], r(129.3), 2.4, color="#F5B04A", width=6, dash="14 8")
js += label("x1", km(27.20, 75.45), "Kotputli–Kishangarh E-way · proposed", r(129.6), dx=-330, dy=-110, size=26)
js += chip("c12a", "Proposed · greenfield (as reported)", "≈181 km · ≈₹6,906 cr · bypasses Jaipur to the west", r(130.4), r(137.9), y=360, right=330)
SVG.append(f'<path id="mp-tr" d="{pd([km(27.75, 76.25), K("kotputli"), km(27.45, 75.85), km(27.15, 75.55), K("jobner"), km(26.80, 75.15), K("kishangarh"), K("ajmer")])}" pathLength="1" style="fill:none;stroke:#7FC8F8;stroke-width:4;stroke-dasharray:0.03 0.03;opacity:0"/>')
js += f'      tl.to("#mp-tr", {{ opacity: 1, duration: 0.4 }}, {r(131.4)});\n      tl.fromTo("#mp-tr", {{ strokeDashoffset: 0.3 }}, {{ strokeDashoffset: 0, duration: 3.5, ease: "none", repeat: 1 }}, {r(131.4)});\n'
js += label("x2", km(27.55, 75.95), "Delhi ↔ Ajmer through traffic", r(131.5), dx=16, dy=10, size=26, amb=False)
SVG.append(f'<circle id="mp-rd" cx="{K("hawa")[0]*KM:.1f}" cy="{K("hawa")[1]*KM:.1f}" r="{14*KM}" style="fill:#7FC8F8;fill-opacity:0.12;stroke:#7FC8F8;stroke-width:3;opacity:0"/>')
js += f'      tl.to("#mp-rd", {{ opacity: 1, duration: 0.4 }}, {r(135.4)});\n'
js += label("x3", km(26.80, 75.95), "Less pressure on existing highways", r(135.5), until=r(141.0), dx=16, dy=40, size=26, amb=False)
for k, p in enumerate([ROADS["kk"][1], ROADS["kk"][2], K("jobner"), ROADS["kk"][4]]):
    js += label(f"xi{k}", p, "", r(139.2) + 0.15 * k, tier="minor", dx=0, dy=0) if False else ""
    SVG.append(f'<g id="mp-xi{k}" style="opacity:0"><circle cx="{p[0]*KM:.1f}" cy="{p[1]*KM:.1f}" r="22" style="fill:#120D0A;stroke:#F5B04A;stroke-width:4"/></g>')
    js += f'      tl.to("#mp-xi{k}", {{ opacity: 1, duration: 0.3 }}, {r(139.2) + 0.15 * k:.3f});\n'
js += chip("c12b", "Designated interchanges", "Reported: 9 entry/exit points, incl. near Jobner", r(139.4), r(147.2), y=360, right=330)
js += news("n5", "Patrika", "Mar 2026", "Rajasthan to get 181km greenfield expressway passing through 5 districts, easing travel to Delhi", r(127.8), r(130.3))
js += popups([("qx0", "warehouse", K("jobner"), r(141.2), "Warehouses", BL), ("qx1", "trucks", K("jobner"), r(143.4), "Trucks · logistics", BL)], r(147.2))
# notes (bottom-right, screen space)
for k, (a, b, txt) in enumerate([(2.3, 23.4, "Map: OpenStreetMap · some positions approximate"), (23.4, 31.3, "Schematic layout · reported scope"), (31.3, 47.1, "Map: OpenStreetMap"),
                                  (47.1, 66.0, "Proposed alignment schematic, as reported"), (66.0, 126.2, "Map: OpenStreetMap · clips: representative footage"), (126.2, 147.4, "Proposed alignment approximate")]):
    OVL.append(f'<div class="note" id="mp-nt{k}" style="top:{1290 - 90}px;left:auto;right:64px;font-size:26px;color:rgba(201,183,156,0.9);opacity:0">{txt}</div>')
    js += f'      tl.to("#mp-nt{k}", {{ opacity: 1, duration: 0.3 }}, {max(0, r(a))});\n      tl.to("#mp-nt{k}", {{ opacity: 0, duration: 0.3 }}, {r(b) - 0.3:.3f});\n'
# face beats: the whole map fades out and back
for a, b in FACE:
    js += f'      tl.to("#mp-all", {{ opacity: 0, duration: 0.3 }}, {r(a)});\n      tl.to("#mp-all", {{ opacity: 1, duration: 0.3 }}, {r(b) - 0.3:.3f});\n'

v0 = OVR; s0 = sc(v0)
world = (f'<div id="mp-W" style="position:absolute;left:0;top:0;--s:{s0:.5f};--cx:{v0[0]*KM:.2f};--cy:{v0[1]*KM:.2f};transform-origin:0 0;'
         f'transform:translate(540px,785px) scale(var(--s)) translate(calc(var(--cx) * -1px),calc(var(--cy) * -1px))">{"".join(HTML)}</div>')
import re as _re
def _px(m): return f"stroke-width:calc({m.group(1)}px / var(--s))"
def _dash(m):
    v = m.group(1).split()
    if v == ["1"] or "0.03" in v: return m.group(0)
    return "stroke-dasharray:" + " ".join(f"calc({x}px / var(--s))" for x in v)
SVGS = _re.sub(r"stroke-dasharray:([\d. ]+)", _dash, _re.sub(r"stroke-width:([\d.]+)", _px, "".join(SVG)))
svg = (f'<svg style="position:absolute;left:0;top:0;width:1080px;height:1830px;overflow:hidden"><g id="mp-G" style="--s:{s0:.5f}" transform="translate(540 785) scale({s0:.5f}) translate({-v0[0]*KM:.2f} {-v0[1]*KM:.2f})">'
       f'{SVGS}</g></svg>')
css = ('<style>.lb { position:absolute; width:0; height:0; transform:scale(calc(1 / var(--s))); transform-origin:0 0; }'
       ' .lb .pd { position:absolute; left:-11px; top:-11px; width:22px; height:22px; border-radius:50%; background:#F5B04A; box-shadow:0 0 0 4px rgba(245,176,74,0.3); }'
       ' .lb .tag { white-space:nowrap; }</style>')
scene("mp", R0, 147.4, css + f'<div id="mp-all" style="position:absolute;inset:0">{svg}{world}</div>' + "".join(OVL), cam_js(R0) + js)


# ---------- chrome ----------
SECT = [(2.3, "THE ROAD", "Jaipur → Ajmer · NH-48"), (4.6, "STRETCH 1", "200-ft Bypass → Bhankrota"), (23.4, "200-FT BYPASS", "Going signal-free"),
        (32.35, "MAHAPURA", "Southern Ring Rd · existing"), (39.4, "WIDER NETWORK", "Link to Delhi–Mumbai E-way"), (47.9, "CHITROLI", "Northern Ring Rd · proposed"),
        (59.25, "DON'T MIX THEM UP", "Mahapura ≠ Chitroli"), (67.5, "MAHINDRA WORLD CITY", "Employment anchor"), (77.7, "DEHMI KALAN", "Manipal University"),
        (89.35, "BAGRU", "Industry &amp; block printing"), (97.7, "MAHLA → DUDU", "Highway belt · Sambhar"), (116.6, "KISHANGARH → AJMER", "Marble · airport · Pushkar"),
        (127.75, "PROPOSED", "Kotputli–Kishangarh E-way"), (147.4, "SHARE THIS", "One road, many demands")]
cards = [(f"hd-{k+1}", t, (SECT[k+1][0] if k + 1 < len(SECT) else VIDEO_END), c, h) for k, (t, c, h) in enumerate(SECT)]
CALL = [("co-c", 149.0, VIDEO_END, "Call / WhatsApp 96721 19046")]
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
      
      <div id="pg">{"".join(f'<i id="pg-{k+1}"></i>' for k in range(0))}</div>
      {hd_html}{co_html}
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#pg", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, 6.16);
      tl.to("#pg", {{ opacity: 0, duration: 0.3 }}, 150.0);{"".join(f"""
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
steps = ["Bypass → Bhankrota · retail &amp; transport", "Ring roads · Mahapura, Chitroli", "MWC · Manipal · Bagru", "Dudu → Kishangarh · logistics, marble"]
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
        <div id="ec-t">Ashwil Bhupesh</div><div id="ec-s">Each stretch, a different demand.</div>
        <div id="ec-l">{lis}</div>
        <div id="ec-c"><div class="lbl">Call / WhatsApp</div><div id="ec-n">96721 19046</div></div>
        <div id="ec-b">ASHWILLPOWER</div><div class="note" style="top:1500px;left:96px;right:96px;text-align:center;white-space:normal;font-size:26px;line-height:1.45">Opinions are the speaker's · not financial advice · returns are not guaranteed<br>Proposed projects may change · alignments approximate<br>Map data © OpenStreetMap contributors</div>
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

MIXKIT = ["Aerial shot of a busy avenue in the city", "Aerial view of a highway in a big city", "Traffic on a freeway", "Corporate and business buildings in the city", "Market shoppers", "Open office space", "Customers in a minimalist style restaurant", "Students walking on a university campus", "Students walking in a university", "Interior of a room with terrace", "Two coworkers talking and laughing", "Aerial view of a factory", "Trailers crossing a bridge over a scenic valley landscape", "Speedy point-of-view tour of a highway", "Traveling on the highway on a sunny day", "A road between a big green agriculture field", "Buildings under construction, aerial view", "Detailed texture of a smooth marble surface", "Camels walking in the desert", "Group of flamingos on the shore of a lake", "Young worker doing inventory"]

# ---------- credits roll ----------
CR = {k: v for k, v in json.load(open(__file__.replace("build.py", "img/credits.json"))).items() if k in ('block',)}
lines = ["<b>Photos &amp; maps — Wikimedia Commons</b>"] + [f"{v['title'][5:]} — {v['artist']} — {v['license']}" for k, v in CR.items() if not k.startswith("logo_")]
lines += ["<b>Project renders</b> — VRB Golden Tower; Manglam PinkWest (developer marketing images, supplied by Ashwil Bhupesh)"]
lines += ["<b>Footage — Mixkit (Free licence)</b>"] + MIXKIT
lines += ["<b>Headlines quoted</b> — Construction World (Manglam PinkWest; NHAI junction award, Mar 2026) · Swarajya (Jul 2025) · Patrika (Dec 2025; Mar 2026)", "<b>Facts</b> — DQ India / Mahindra (MWC anchor clients) · Patrika (Kotputli–Kishangarh 181 km, ₹6,906 cr)",
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
