import sys, json, re, math
P, WJ, PJ = sys.argv[1], sys.argv[2], sys.argv[3]
VIDEO_END = 115.77
ED_CARD = 5.5
CRED = 7.0
END = round(VIDEO_END + ED_CARD + CRED, 2)
exec(open(__file__.replace("build.py", "base_part.py")).read())  # BASE, INSERTS, rel(), scene()

# ---------- captions: Parakeet timings, spellings checked against Whisper ----------
FIX = {"Delhi-Jaipur-Bombay": "Delhi–Jaipur–Bombay", "Delhi-Mumbai": "Delhi–Mumbai", "Sona": "Sohna", "Alvar": "Alwar", "Balgana": "Bagrana", "Dossa.": "Dausa.",
       "Bandikwi": "Bandikui", "Dosa": "Dausa", "Bandarage": "Bhandarej", "Ranthampore": "Ranthambore", "Bandi": "Bandikui",
       "Bedoli,": "Bhedoli,", "Kurikot,": "Khurikurd,", "Bergana.": "Bagrana.", "Bergana,": "Bagrana,", "Japur": "Jaipur", "Jeepo's": "Jaipur's", "Delhi-Bombay": "Delhi–Bombay",
       "Mark": "mark", "Interchange": "interchange", "Junction": "junction", "Highway.": "highway."}
MULTI = [(("exits", "serve"), "exits serve"), (("by", "passing"), "bypassing"), (("baroda", "maiv"), "Barodameo"), (("chan", "bowdy"), "Chand Baori"), (("lal", "soot"), "Lalsot,"), (("swaimadhipur",), "Sawai Madhopur"),
         (("savai", "madafur"), "Sawai Madhopur"), (("gilaki", "nangal"), "Geela ki Nangal"), (("sixty", "seven", "kilometre"), "67-km")]
EM = {"expressway.", "delhi–mumbai", "sohna", "alwar", "bandikui.", "bandikui", "67-km", "bagrana,", "bagrana.", "dausa.", "barodameo,", "sariska.", "chand", "baori",
      "dausa", "bhandarej", "lalsot,", "sawai", "madhopur", "ranthambore", "bhedoli,", "khurikurd,", "sundarpura,", "geela", "ncr", "tourism,", "weddings,", "hotels,", "warehouses,", "exits."}
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
MAJOR = _ways("major_*.json") + _ways("majorx_*.json"); CITY = _ways("city_*.json"); RAIL = _ways("rail_*.json"); WATER = _ways("water.json")
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
               + (f'<path class="ds" d="{pd(pts)}" style="fill:none;stroke:#120D0A;stroke-width:{width + 1};stroke-dasharray:{dash};opacity:0"/>' if dash != "1 0" else "") + '</g>')
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
# ===================== Delhi–Mumbai Expressway reel: the story on one continuous map =====================
def _load(f):
    try: return json.load(open(os.path.join(OSMD, f))).get("elements", [])
    except Exception: return []
NE4_ALL = [(e.get("tags", {}), [km(g["lat"], g["lon"]) for g in e["geometry"]]) for e in _load("ne4.json") if e.get("geometry")]
DMEW = pick(lambda t: "vadodara" in t.get("name", "").lower() or t.get("ref", "").replace("-", "") == "NE4") + [p for t, p in NE4_ALL if t.get("ref") == "NE4"]   # Delhi–Mumbai Expressway (NE-4)
LINK = pick(lambda t: "bandikui" in t.get("name", "").lower() and t.get("highway") == "motorway") or [p for t, p in NE4_ALL if t.get("ref") == "NE4C"]             # Jaipur–Bandikui Expressway (NE4C)
NH21 = pick(lambda t: "NH21" in t.get("ref", "") or "agra jaipur" in t.get("name", "").lower())
NH21 = [p for p in NH21 if max(q[0] for q in p) < 80 and min(q[0] for q in p) > 5 and -5 < min(q[1] for q in p) < 25]
OLDNH = pick(lambda t: t.get("ref", "") in ("NH48", "NH48;NH52") and t.get("highway") in ("trunk", "motorway"))
OLDNH = [p for p in OLDNH if min(q[1] for q in p) < -2 and max(q[0] for q in p) > 5]   # Jaipur → Delhi on NH-48
print("ne4", len(DMEW), "link", len(LINK), "nh21", len(NH21), "oldnh", len(OLDNH))
def near_on(segs, p):
    best = None
    for s in segs:
        for q in s:
            d = math.hypot(q[0] - p[0], q[1] - p[1])
            if best is None or d < best[0]: best = (d, q)
    return best[1] if best else p
def along(segs, a, b, f):
    """Point a fraction f of the way from a to b, snapped onto the given route."""
    return near_on(segs, (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
PL_ = {k: km(*v) for k, v in {
    "delhi": (28.614, 77.209), "gurugram": (28.465, 77.030), "sohna": (28.324, 77.085), "alwar": (27.414, 76.617), "barodameo": (27.490, 76.848),
    "sariska": (27.378, 76.435), "bandikui": (27.046, 76.575), "abhaneri": (27.007, 76.608), "dausa": (26.805, 76.444), "bhandarej": (26.805, 76.560),
    "lalsot": (26.563, 76.328), "lalsotic": (26.600, 76.345), "smadhopur": (26.010, 76.355), "smic": (25.990, 76.290), "ranthambore": (26.020, 76.480),
    "geela": (26.9135, 75.9702), "jaipur": (26.9155, 75.8190), "bagrana": (26.885, 75.930)}.items()}
# extend the expressway where the OSM tiles stop (north to Sohna, south to Lalsot and Sawai Madhopur)
ne4pts = [q for s in DMEW for q in s]
if ne4pts:
    north = min(ne4pts, key=lambda q: q[1]); south = max(ne4pts, key=lambda q: q[1])
    if north[1] > PL_["sohna"][1] + 3: DMEW.append([north, PL_["sohna"], PL_["gurugram"]])
    if south[1] < PL_["smic"][1] - 3: DMEW.append([south, PL_["lalsotic"], km(26.30, 76.32), PL_["smic"], km(25.70, 76.10)])
else:
    DMEW = [[PL_["gurugram"], PL_["sohna"], km(27.95, 77.00), PL_["barodameo"], PL_["bandikui"], PL_["bhandarej"], PL_["lalsotic"], PL_["smic"]]]
IC = {"alwar": near_on(DMEW, PL_["barodameo"]), "bandikui": near_on(DMEW, PL_["bandikui"]), "dausa": near_on(DMEW, PL_["bhandarej"]),
      "lalsot": near_on(DMEW, PL_["lalsotic"]), "smadhopur": near_on(DMEW, PL_["smic"])}
LINKI = {"bhedoli": along(LINK, IC["bandikui"], PL_["geela"], 0.18), "khurikurd": along(LINK, IC["bandikui"], PL_["geela"], 0.42),
         "sundarpura": along(LINK, IC["bandikui"], PL_["geela"], 0.68), "geela": near_on(LINK, PL_["geela"])}

OVR = (68, -40, 300); CUR[0] = OVR       # the whole corridor: Delhi → Sawai Madhopur
R0 = 3.9; MAP_END = 112.0
def r(t): return round(t - R0, 3)
FACE = [(15.3, 18.95), (76.35, 78.85)]
def ph(rid, at, t0, t1, cap, box, img, sub, w=400, h=280): return popup(rid, None, at, t0, t1, cap, box=box, w=w, h=h, img=img, sub=sub)
def xm(rid, p, t, n=None):
    SVG.append(f'<g id="mp-{rid}" style="opacity:0"><circle cx="{p[0]*KM:.1f}" cy="{p[1]*KM:.1f}" r="16" style="fill:#120D0A;stroke:#F5B04A;stroke-width:4"/></g>')
    return f'      tl.fromTo("#mp-{rid}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {t:.3f});\n'
PT = (330, 445); WIDE = (470, 280); SQ = (430, 430)

# ---------- 0 · poster (0–1.15): aerial expressway + route, fully formed on frame 0 ----------
scene("cv", 0, 1.15,
      f'<div class="ins" style="position:absolute;inset:0"></div><img src="{IMG}aerial1.jpg" style="position:absolute;left:0;top:-90px;width:1080px;height:1100px;object-fit:cover"/>'
      '<div style="position:absolute;left:0;right:0;top:-90px;height:1100px;background:linear-gradient(180deg,rgba(18,13,10,0.55) 0%,rgba(18,13,10,0.15) 35%,rgba(18,13,10,0.75) 75%,#120D0A 100%)"></div>'
      '<div style="position:absolute;left:70px;right:70px;top:150px;font-family:Inter,sans-serif;font-weight:900;font-size:120px;line-height:0.95;color:#F3E7D3;text-shadow:0 8px 40px rgba(0,0,0,0.7)">DELHI–<br>MUMBAI<br><span style="color:#F5B04A">EXPRESSWAY</span></div>'
      '<div style="position:absolute;left:76px;right:70px;top:560px;font-family:Inter,sans-serif;font-weight:800;font-size:56px;line-height:1.1;color:#F3E7D3;text-shadow:0 4px 20px rgba(0,0,0,0.8)">How it plugs Jaipur in</div>'
      '<div style="position:absolute;left:76px;top:1040px;padding:12px 22px;border-radius:14px;background:rgba(60,38,14,0.92);border:2px solid #E3A23B;font-family:Inter,sans-serif;font-weight:800;font-size:40px;color:#F3E7D3">4 exits · 67 km link · Bagrana</div>'
      '<div class="note" style="top:1130px;left:76px;font-size:22px;color:rgba(243,231,211,0.8)">Photo supplied</div>', "", fade_in=False)

js = ""
# A · Delhi and Jaipur, the crowded NH-48 (3.9–11.6)
js += label("dl", PL_["delhi"], "Delhi NCR", r(5.0), tier="major", dx=16, dy=-30, size=32)
js += label("jp", PL_["jaipur"], "Jaipur", r(4.3), tier="major", dx=16, dy=-30, right=True, size=32)
js += route("old", OLDNH or [ROADS["delhiNH"]], PL_["jaipur"], r(6.6), 1.4, color="#E8664A", width=5, halo=16)
js += label("ol", along(OLDNH or [ROADS["delhiNH"]], PL_["jaipur"], PL_["delhi"], 0.45), "NH-48 · crowded, unpredictable", r(7.3), until=r(19.0), dx=-30, dy=-20, right=True, amb=False, size=26)
js += popup("qa", "freeway", along(OLDNH or [ROADS["delhiNH"]], PL_["jaipur"], PL_["delhi"], 0.45), r(7.6), r(11.6), "Highway traffic", box=BL)
# B · the Delhi–Mumbai Expressway arrives (11.6–15.3)
js += route("dme", DMEW, PL_["sohna"], r(11.8), 2.4, color="#7FC8F8", width=6, halo=20)
js += label("dm", along(DMEW, PL_["sohna"], PL_["smic"], 0.25), "Delhi–Mumbai Expressway", r(12.8), tier="major", dx=16, dy=-10, size=28)
js += f'      tl.to(["#mp-old0"], {{ opacity: 0.35, duration: 0.5 }}, {r(13.4)});\n' if OLDNH else ""
# (B pop-ups moved into the India-map scene)
# (face 15.3–18.95) · C · "Look at this map": Sohna → south through Alwar → Bandikui (19.0–25.3)
js += ph("qc0", PL_["sohna"], r(19.0), r(20.2), "The alignment", TR, "alignment.jpg", "Image supplied", 400, 432)
cam(19.3, (PL_["sohna"][0], PL_["sohna"][1] + 6, 48), 0.9)
js += label("so", PL_["sohna"], "Sohna · start", r(20.3), tier="major", dx=16, dy=-20)
js += ph("qc1", PL_["sohna"], r(20.4), r(22.2), "Sohna, Gurugram", BL, "sohna_photo.jpg", "Image supplied", 470, 264)
cam(21.3, (88, -85, 125), 1.6)
js += label("al", PL_["alwar"], "Alwar", r(23.2), tier="major", dx=-16, dy=-20, right=True)
js += ph("qc2", PL_["alwar"], r(22.3), r(25.3), "Sohna → south on NE4", TL, "gmap_sohna_route.jpg", "Map view · supplied", PT[0], PT[1])
cam(23.8, (60, -22, 80), 1.2)
js += label("bk", PL_["bandikui"], "Bandikui", r(24.2), tier="major", dx=16, dy=-20)
# D · the 67 km Jaipur–Bandikui link to Bagrana; the old approach via Dausa (25.3–37.4)
cam(25.4, (44, -4, 88), 0.9)
js += ph("qd0", PL_["bandikui"], r(25.9), r(30.6), "Bandikui → Jaipur · 67 km", TR, "toi_bandikui.jpg", "Graphic · supplied", 430, 365)
js += route("lk", LINK, PL_["bandikui"], r(28.5), 2.2, color="#F5B04A", width=7, halo=22)
js += label("lkt", along(LINK, PL_["bandikui"], PL_["geela"], 0.5), "Jaipur–Bandikui Expressway · ≈67 km", r(29.0), until=r(69.6), dx=-20, dy=-60, size=26)
js += label("bg", PL_["bagrana"], "Bagrana", r(30.8), tier="major", dx=-16, dy=20, right=True)
js += ph("qd1", PL_["bagrana"], r(30.8), r(34.9), "Bagrana · ring road entry", BL, "gmap_bagrana.jpg", "Map view · supplied", 380, 415)
js += route("ag", NH21 or [[PL_["bagrana"], PL_["dausa"]]], PL_["bagrana"], r(32.3), 1.2, color="#E8664A", width=5, halo=14, op=0.9)
js += label("agt", along(NH21 or [[PL_["bagrana"], PL_["dausa"]]], PL_["bagrana"], PL_["dausa"], 0.5), "Agra Road (NH-21)", r(32.5), until=r(37.4), dx=16, dy=20, amb=False, size=26)
js += route("sr", SRING or [ROADS["sring"]], PL_["bagrana"], r(33.4), 1.0, color="#B8E07A", width=5, halo=14, op=0.9)
js += label("srt", K("goner"), "Ring Road", r(34.0), until=r(37.4), dx=16, dy=10, amb=False, size=26)
js += label("ds", PL_["dausa"], "Dausa · the older approach", r(36.2), until=r(37.6), dx=16, dy=20, amb=False, size=26)
js += ph("qd2", PL_["dausa"], r(35.0), r(37.4), "New expressway vs old highway", TR, "gmap_old_vs_new.jpg", "Map view · supplied", 470, 226)
# E · the key exits (37.4–40.7)
cam(37.5, OVR, 1.0)
for k, key in enumerate(["alwar", "bandikui", "dausa", "lalsot"]):
    js += xm(f"x{k}", IC[key], r(38.4) + 0.3 * k)
    js += label(f"xn{k}", IC[key], f"Exit {k + 1}", r(38.4) + 0.3 * k, until=r(40.7), dx=16, dy=-20, size=26)
# F · Exit 1: Alwar interchange near Barodameo → Alwar, Sariska (40.7–47.0)
cam(40.8, ((IC["alwar"][0] + PL_["sariska"][0]) / 2, IC["alwar"][1] + 4, 62), 0.9)
js += label("f0", IC["alwar"], "Alwar interchange · Barodameo", r(42.1), until=r(47.0), dx=16, dy=-30, size=28)
js += label("f1", PL_["sariska"], "Sariska Tiger Reserve", r(46.0), until=r(53.5), dx=16, dy=20, amb=False, size=26)
js += popups([("qf0", None, IC["alwar"], r(41.4), "Alwar interchange", TR, "gmap_pinan_exit.jpg", "Map view · supplied", PT),
              ("qf1", None, PL_["alwar"], r(44.7), "Alwar → Sariska", TR, "gmap_alwar_sariska.jpg", "Map view · supplied", PT),
              ("qf2", None, PL_["sariska"], r(46.0), "Sariska", BL, "sariska_safari.jpg", "Image supplied", SQ)], r(47.0))
# G · Exit 2: Bandikui → Jaipur; Abhaneri's Chand Baori (47.0–53.5)
cam(47.1, (IC["bandikui"][0] - 4, IC["bandikui"][1] + 2, 34), 0.8)
js += label("g0", IC["bandikui"], "Bandikui connection → Jaipur", r(48.6), until=r(53.5), dx=16, dy=-40, size=28)
js += label("g1", PL_["abhaneri"], "Abhaneri · Chand Baori", r(51.0), until=r(53.5), dx=16, dy=20, amb=False, size=26)
js += popups([("qg0", None, PL_["abhaneri"], r(49.6), "Chand Baori, Abhaneri", TL, "gmap_chandbaori.jpg", "Map view · supplied", PT),
              ("qg1", None, PL_["abhaneri"], r(51.0), "Chand Baori stepwell", TL, "chandbaori.jpg", "Image supplied", (380, 482))], r(53.5))
# H · Exit 3: Dausa interchange at Bhandarej → Jaipur–Agra highway (53.5–58.8)
cam(53.6, (IC["dausa"][0] - 6, IC["dausa"][1], 34), 0.8)
js += label("h0", IC["dausa"], "Dausa interchange · Bhandarej", r(55.0), until=r(58.8), dx=16, dy=-40, size=28)
js += route_fx("ag", len(NH21 or [1]), r(57.3), "pulse")
js += label("h1", PL_["dausa"], "Jaipur–Agra Highway", r(57.4), until=r(58.8), dx=-16, dy=30, right=True, amb=False, size=26)
js += popups([("qh0", None, IC["dausa"], r(55.0), "Dausa · Bhandarej", TL, "gmap_bhandarej.jpg", "Map view · supplied", PT),
              ("qh1", None, IC["dausa"], r(57.2), "Expressway interchange", BL, "loop.jpg", "Image supplied", (470, 314))], r(58.8))
# I · further south: Lalsot and Sawai Madhopur exits → Ranthambore (58.8–69.6)
cam(58.9, (PL_["lalsot"][0] + 6, (IC["lalsot"][1] + IC["smadhopur"][1]) / 2, 118), 1.0)
js += label("i0", IC["lalsot"], "Lalsot", r(59.9), tier="major", dx=16, dy=-20)
js += xm("x4", IC["smadhopur"], r(60.7)) + label("i1", IC["smadhopur"], "Sawai Madhopur", r(60.7), tier="major", dx=-16, dy=-20, right=True)
js += label("i2", PL_["ranthambore"], "Ranthambore", r(66.5), until=r(69.6), dx=16, dy=-10, amb=False, size=28)
js += popups([("qi0", None, IC["lalsot"], r(59.8), "Lalsot interchange", TR, "gmap_lalsot.jpg", "Map view · supplied", PT),
              ("qi1", None, IC["smadhopur"], r(61.5), "Sawai Madhopur interchange", TR, "gmap_sawaimadhopur.jpg", "Map view · supplied", PT),
              ("qi2", None, PL_["ranthambore"], r(66.4), "Ranthambore", TL, "ranthambore_lake.jpg", "Image supplied", SQ),
              ("qi3", None, PL_["ranthambore"], r(68.0), "Ranthambore Fort", TL, "ranthambore_fort.jpg", "Image supplied", (330, 485))], r(69.6))
# J · the link's own interchanges (69.6–76.35)
cam(69.6, (44, -4, 80), 1.0)
js += route_fx("lk", len(LINK), r(69.9), "pulse")
for k, (key, lab, t) in enumerate([("bhedoli", "Bhedoli", 70.6), ("khurikurd", "Khurikurd", 71.4), ("sundarpura", "Sundarpura", 72.5), ("geela", "Geela ki Nangal", 73.5)]):
    js += xm(f"y{k}", LINKI[key], r(t)) + label(f"yl{k}", LINKI[key], lab, r(t), until=r(76.2), dx=16, dy=-40 if k % 2 else 20, size=26)
js += f'      tl.fromTo("#mp-Lbg .pd", {{ scale: 1 }}, {{ scale: 1.9, duration: 0.35, yoyo: true, repeat: 1 }}, {r(75.4)});\n'
# (face 76.35–78.85) · K · why it matters (78.85–92.0)
cam(78.4, (75, -95, 210), 0.5)
SVG.append(f'<path id="mp-ncr" pathLength="1" d="{pd([PL_["delhi"], PL_["sohna"], IC["alwar"], IC["bandikui"], LINKI["geela"], PL_["jaipur"]])}" style="fill:none;stroke:#F5B04A;stroke-width:5;stroke-dasharray:0.02 0.02;opacity:0"/>')
js += f'      tl.to("#mp-ncr", {{ opacity: 1, duration: 0.3 }}, {r(79.0)});\n      tl.fromTo("#mp-ncr", {{ strokeDashoffset: 0.2 }}, {{ strokeDashoffset: 0, duration: 2.5, ease: "none", repeat: 4 }}, {r(79.0)});\n'
js += label("k0", along(DMEW, PL_["sohna"], IC["alwar"], 0.5), "Easier NCR access", r(79.5), until=r(85.4), dx=16, dy=0, size=28)
js += popups([("qk0", None, PL_["jaipur"], r(82.0), "Weekend tourism", BL, "hawa.jpg", "Photo · Wikimedia Commons", (400, 280)),
              ("qk1", None, PL_["jaipur"], r(82.9), "Destination weddings", BL, "wedding.jpg", "Image supplied", SQ),
              ("qk2", "corporate", PL_["jaipur"], r(84.3), "Business travel", BL)], r(85.5))
cam(85.5, (44, -2, 92), 0.9)
js += f'      tl.to("#mp-ncr", {{ opacity: 0, duration: 0.4 }}, {r(85.5)});\n'
for k, key in enumerate(["bandikui", "dausa"]): js += ring(f"kr{k}", IC[key], 4, r(86.6) + 0.2 * k, until=r(91.8))
js += ring("kr2", PL_["bagrana"], 3.5, r(87.0), until=r(91.8))
js += popups([("qk3", None, IC["dausa"], r(86.6), "Highway hotels", TL, "highway_king.jpg", "Image supplied", (470, 264)),
              ("qk4", None, IC["dausa"], r(88.9), "Hotels", TL, "highway_prince.jpg", "Image supplied", (470, 264)),
              ("qk5", None, PL_["bagrana"], r(89.5), "Warehouses", BL, "warehouse_aerial.jpg", "Image supplied", (470, 264)),
              ("qk6", "market", PL_["bagrana"], r(90.4), "Local businesses", BL)], r(92.0))
# L · where to start: Bagrana, Agra Road, Ring Road junction → approaches → Delhi side / Mumbai side (92.0–104.4)
cam(92.0, (PL_["bagrana"][0] + 1, PL_["bagrana"][1] + 1, 18), 1.0)
js += ring("lb", PL_["bagrana"], 1.6, r(93.8), until=r(99.5))
js += route_fx("ag", len(NH21 or [1]), r(94.6), "pulse") + route_fx("sr", len(SRING or [1]), r(95.5), "pulse")
js += label("lj", PL_["bagrana"], "Agra Rd × Ring Rd junction", r(95.5), until=r(97.2), dx=16, dy=40, size=26)
js += ph("ql0", PL_["bagrana"], r(93.8), r(97.0), "Bagrana", TR, "gmap_bagrana_region.jpg", "Map view · supplied", PT[0], PT[1])
cam(97.0, (44, -4, 82), 1.0)
for k in range(4): js += f'      tl.fromTo("#mp-y{k}", {{ scale: 1 }}, {{ scale: 1.6, duration: 0.3, yoyo: true, repeat: 1, transformOrigin: "50% 50%" }}, {r(98.0) + 0.25 * k:.3f});\n'
cam(99.8, OVR, 1.2)
js += label("ld", along(DMEW, PL_["sohna"], IC["alwar"], 0.2), "↑ Delhi side", r(101.9), until=r(111.8), dx=16, dy=0, size=30)
js += label("lm", IC["smadhopur"], "↓ Mumbai side", r(103.2), until=r(111.8), dx=16, dy=40, size=30)
js += ph("ql1", IC["bandikui"], r(100.0), r(104.3), "Delhi–Mumbai Expressway", BL, "aerial2.jpg", "Image supplied", 470, 279)
# M · access, not adjacency (104.4–112.0)
for k, key in enumerate(["alwar", "bandikui", "dausa", "lalsot", "smadhopur"]): js += ring(f"mr{k}", IC[key], 6, r(109.2) + 0.12 * k, until=r(111.8))
js += chip("cm", "Speaker's view · not a guarantee", "The value is in convenient access to the exits, not just being beside the expressway", r(105.5), r(111.8), y=560, right=300)
# notes
for k, (a, b, txt) in enumerate([(3.9, 25.3, "Map: OpenStreetMap"), (25.3, 76.35, "Map: OpenStreetMap · interchange positions approximate"), (78.85, 112.0, "Map: OpenStreetMap")]):
    OVL.append(f'<div class="note" id="mp-nt{k}" style="top:{1398 - 90}px;left:auto;right:64px;font-size:24px;color:rgba(201,183,156,0.9);opacity:0">{txt}</div>')
    js += f'      tl.to("#mp-nt{k}", {{ opacity: 1, duration: 0.3 }}, {max(0, r(a))});\n      tl.to("#mp-nt{k}", {{ opacity: 0, duration: 0.3 }}, {r(b) - 0.3:.3f});\n'
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
scene("mp", R0, MAP_END, css + f'<div id="mp-all" style="position:absolute;inset:0">{svg}{world}</div>' + "".join(OVL), cam_js(R0) + js)



# ---------- India map (11.6–15.3): the whole Delhi–Mumbai Expressway ----------
IW, IH = 1200, 1293                               # indiamap.png: bounds 37.5N–5N, 67E–99E
GW = 1000; GX, GY = 40, 300 - 90                  # shown 1000 px wide; body is shifted down 90 px
def ip(lat, lon): return (GX + (lon - 67.0) / 32.0 * GW, GY + (37.5 - lat) / 32.5 * IH * GW / IW)
CITY = {"Delhi": (28.61, 77.21), "Jaipur": (26.92, 75.82), "Kota": (25.18, 75.83), "Vadodara": (22.31, 73.18), "Surat": (21.17, 72.83), "Mumbai": (19.08, 72.88)}
RT = [(28.61, 77.21), (28.32, 77.08), (27.75, 76.95), (27.40, 76.88), (27.05, 76.62), (26.80, 76.50), (26.30, 76.32), (25.90, 76.10), (25.18, 75.95), (24.40, 75.50), (23.33, 75.04),
      (22.84, 74.25), (22.70, 73.70), (22.31, 73.18), (21.70, 72.95), (21.17, 72.90), (20.20, 72.90), (19.30, 73.05), (19.08, 72.88)]
rp = [ip(*q) for q in RT]
dpath = smooth(rp, False)
lk = [ip(26.92, 75.82), ip(26.98, 76.20), ip(27.05, 76.62)]
jx, jy = ip(26.92, 75.82); dx_, dy_ = ip(28.61, 77.21)
ox, oy = (jx + dx_) / 2, (jy + dy_) / 2
tags = "".join(f'<div class="tag{" amb" if n in ("Delhi", "Jaipur", "Mumbai") else ""}" id="in-t{k}" style="left:{ip(*p)[0] + (16 if n != "Mumbai" else -170):.0f}px;top:{ip(*p)[1] - 24:.0f}px;font-size:{30 if n in ("Delhi", "Jaipur", "Mumbai") else 26}px;padding:8px 16px">{n}</div>'
               + f'<div id="in-d{k}" style="position:absolute;left:{ip(*p)[0] - 10:.0f}px;top:{ip(*p)[1] - 10:.0f}px;width:20px;height:20px;border-radius:50%;background:#F5B04A;box-shadow:0 0 0 4px rgba(245,176,74,0.35)"></div>'
               for k, (n, p) in enumerate(CITY.items()))
body = (f'<div id="in-z" style="position:absolute;left:0;top:0;width:1080px;height:1830px;transform-origin:{ox:.0f}px {oy:.0f}px">'
        f'<img src="{IMG}indiamap.png" style="position:absolute;left:{GX}px;top:{GY}px;width:{GW}px;height:auto;opacity:0.9"/>'
        f'<svg style="position:absolute;left:0;top:0;width:1080px;height:1830px;overflow:visible"><path id="in-r" pathLength="1" d="{dpath}" style="fill:none;stroke:#1E7FD0;stroke-width:13;filter:drop-shadow(0 0 6px rgba(30,127,208,0.8));stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>'
        f'<path id="in-l" pathLength="1" d="{smooth(lk, False)}" style="fill:none;stroke:#F5B04A;stroke-width:7;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/></svg>'
        f'{tags}</div>'
        f'<div class="tag amb" id="in-k" style="left:560px;top:{ip(23.6, 75.0)[1]:.0f}px;font-size:34px;padding:12px 20px">Delhi → Mumbai · ≈1,380 km</div>'
        f'<div id="in-p" style="position:absolute;left:660px;top:{830 - 90}px;width:370px;height:440px;border-radius:16px;overflow:hidden;border:3px solid #F5B04A;box-shadow:0 12px 32px rgba(0,0,0,0.65);opacity:0">'
        f'<img src="{IMG}ht_route.jpg" style="width:100%;height:100%;object-fit:cover"/><div style="position:absolute;left:0;right:0;bottom:0;padding:22px 12px 8px;background:linear-gradient(180deg,rgba(18,13,10,0),rgba(18,13,10,.92));font-family:Inter,sans-serif;font-weight:800;font-size:28px;color:#F3E7D3">Route graphic<div style="font-weight:600;font-size:22px;color:#E8D9BF">Graphic: Ritesh Kumar · supplied</div></div></div>'
        f'<div class="note" style="top:{1398 - 90}px;left:auto;right:64px;font-size:24px;color:rgba(201,183,156,0.9)">Map: Milenioscuro, CC BY 4.0 · route schematic</div>')
ijs = (f'      tl.fromTo("#in-z", {{ scale: 4.2 }}, {{ scale: 1, duration: 1.3, ease: "power2.inOut" }}, 0);\n'
       f'      tl.fromTo("#in-r", {{ strokeDashoffset: 1 }}, {{ strokeDashoffset: 0, duration: 1.6, ease: "power1.inOut" }}, 1.0);\n'
       f'      tl.fromTo("#in-l", {{ strokeDashoffset: 1 }}, {{ strokeDashoffset: 0, duration: 0.5 }}, 2.2);\n'
       + "".join(f'      IN("#in-t{k}", {0.4 if n in ("Delhi", "Jaipur") else 1.2 + 0.18 * k:.2f});\n' for k, n in enumerate(CITY))
       + '      IN("#in-k", 2.0);\n'
       + '      tl.fromTo("#in-p", { opacity: 0, scale: 0.6, transformOrigin: "50% 100%" }, { opacity: 1, scale: 1, duration: 0.4, ease: "back.out(1.6)" }, 2.3);\n')
scene("in", 11.6, 15.6, body, ijs)

# ---------- chrome ----------
SECT = [(3.9, "THE PROBLEM", "Close on the map, far by road"), (11.6, "THE FIX", "Delhi–Mumbai Expressway"), (19.0, "THE ROUTE", "Sohna → Alwar → Bandikui"),
        (25.3, "THE JAIPUR LINK", "Bandikui → Bagrana · ≈67 km"), (37.4, "KEY EXITS", "Four to remember"), (40.7, "EXIT 1", "Alwar · Barodameo"),
        (47.0, "EXIT 2", "Bandikui → Jaipur"), (53.5, "EXIT 3", "Dausa · Bhandarej"), (58.8, "FURTHER SOUTH", "Lalsot · Sawai Madhopur"),
        (69.6, "ON THE LINK", "Four interchanges"), (78.85, "WHY IT MATTERS", "Tourism · weddings · business"), (85.5, "AROUND THE EXITS", "Hotels · warehouses · shops"),
        (92.0, "WHERE TO START", "Bagrana · Agra Rd · Ring Rd"), (104.4, "THE KEY", "Access, not adjacency"), (112.0, "SAVE THIS", "Watch the exits")]
cards = [(f"hd-{k+1}", t, (SECT[k+1][0] if k + 1 < len(SECT) else VIDEO_END), c, h) for k, (t, c, h) in enumerate(SECT)]
CALL = [("co-c", 112.6, VIDEO_END, "Call / WhatsApp 96721 19046")]
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
      tl.to("#pg", {{ opacity: 0, duration: 0.3 }}, 112.0);{"".join(f"""
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
steps = ["Exit 1 · Alwar (Barodameo)", "Exit 2 · Bandikui → Jaipur link", "Exit 3 · Dausa (Bhandarej)", "Start at Bagrana · Agra Rd × Ring Rd"]
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
        <div id="ec-t">Ashwil Bhupesh</div><div id="ec-s">Access is the opportunity.</div>
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

MIXKIT = ["Traffic on a freeway", "Corporate and business buildings in the city", "Market shoppers"]

# ---------- credits roll ----------
CR = {k: v for k, v in json.load(open(__file__.replace("build.py", "img/credits.json"))).items() if k in ('hawa', 'indiamap')}
lines = ["<b>Photos &amp; maps — Wikimedia Commons</b>"] + [f"{v['title'][5:]} — {v['artist']} — {v['license']}" for k, v in CR.items() if not k.startswith("logo_")]
lines += ["<b>Images supplied by Ashwil Bhupesh</b> — expressway aerials and interchange photos; route graphics (Delhi–Mumbai Expressway graphic by Ritesh Kumar; Bandikui–Jaipur graphic; alignment map); Google Maps views; Chand Baori; Sariska and Ranthambore; wedding; highway hotels; warehouse"]
lines += ["<b>Footage — Mixkit (Free licence)</b>"] + MIXKIT
lines += ["<b>Facts</b> — figures on screen are from the supplied graphics; Bagrana–Bandikui link: Swarajya (Jul 2025)",
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
