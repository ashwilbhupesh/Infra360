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
def badge(m, rid, at, text, dx=20, dy=-110, size=30):
    """White text badge pinned to a map point (company names shown as text, no logos)."""
    x, y = m.px(K(at) if isinstance(at, str) else at); x += dx; y += dy
    w = len(text) * size * 0.6 + 40
    x = max(48, min(1080 - 48 - w, x))
    m.html.append(f'<div id="{m.cid}-{rid}" style="position:absolute;left:{x:.0f}px;top:{y - 90:.0f}px;padding:10px 18px;border-radius:14px;background:#FFFFFF;box-shadow:0 8px 24px rgba(0,0,0,0.5);font-family:Inter,sans-serif;font-weight:800;font-size:{size}px;color:#1B140F;white-space:nowrap">{text}</div>')
    return f"#{m.cid}-{rid}"
def pin(m, rid, at, color="#F5B04A"):
    p = K(at) if isinstance(at, str) else at; u = m.u
    m.svg.append(f'<g id="{m.cid}-{rid}" style="opacity:0"><circle cx="{p[0]:.3f}" cy="{p[1]:.3f}" r="{22*u:.3f}" style="fill:none;stroke:{color};stroke-width:{4*u};filter:url(#{m.cid}-glow)"/>'
                 f'<circle cx="{p[0]:.3f}" cy="{p[1]:.3f}" r="{9*u:.3f}" style="fill:{color}"/></g>')
    return f"#{m.cid}-{rid}"
def line(m, rid, pts, color="#F5B04A", width=8, dash=None, glow=True):
    pts = [K(p) if isinstance(p, str) else p for p in pts]; u = m.u
    da = f"stroke-dasharray:{dash[0]*u} {dash[1]*u};" if dash else "stroke-dasharray:1;"
    m.svg.append(f'<path id="{m.cid}-{rid}" {"" if dash else "class=\"draw\" pathLength=\"1\""} d="{smooth(pts, False)}" style="fill:none;stroke:{color};stroke-width:{width*u};stroke-linecap:round;{da}{"filter:url(#" + m.cid + "-glow);" if glow else ""}{"opacity:0;" if dash else ""}"/>')
    return f"#{m.cid}-{rid}"
def mask_draw(m, rid, pts, t, d, color="#B8E07A", width=7, dash=(10, 8)):
    """A dashed road that 'draws' itself: a dashed path revealed by an animated solid mask."""
    pts = [K(p) if isinstance(p, str) else p for p in pts]; u = m.u
    m.svg.append(f'<mask id="{m.cid}-{rid}m" maskUnits="userSpaceOnUse"><path id="{m.cid}-{rid}k" pathLength="1" d="{smooth(pts, False)}" style="fill:none;stroke:#fff;stroke-width:{(width+8)*u};stroke-dasharray:1;stroke-dashoffset:1"/></mask>'
                 f'<path d="{smooth(pts, False)}" mask="url(#{m.cid}-{rid}m)" style="fill:none;stroke:{color};stroke-width:{width*u};stroke-linecap:round;stroke-dasharray:{dash[0]*u} {dash[1]*u};filter:url(#{m.cid}-glow)"/>')
    return f'      tl.fromTo("#{m.cid}-{rid}k", {{ strokeDashoffset: 1 }}, {{ strokeDashoffset: 0, duration: {d}, ease: "power1.inOut" }}, {t});\n'
def popup(m, rid, src, at, t_on, t_off, cap, w=400, h=260, img=None, sub=None, box=(48, 360)):
    """Clip (or photo) pop-up placed in a clear slot of the map, with a leader line to its spot."""
    p = K(at) if isinstance(at, str) else at; x, y = m.px(p)
    bx, by = box
    ax = min(max(x, bx + 20), bx + w - 20); ay = by + h if y > by + h else (by if y < by else by + h / 2)
    if by <= y <= by + h: ax = bx + w if x > bx + w else bx
    media = (f'<img src="{IMG}{img}" style="width:100%;height:100%;object-fit:cover;display:block"/>' if img else
             f'<video id="{m.cid}-{rid}v" class="clip" src="assets/broll/{src}.mp4" data-start="{max(0, round(t_on - 0.1, 2))}" data-duration="{round(t_off - t_on + 0.5, 2)}" muted playsinline style="width:100%;height:100%;object-fit:cover"></video>')
    sb = f'<div style="font-weight:600;font-size:24px;color:#E8D9BF;margin-top:2px">{sub}</div>' if sub else ""
    m.html.append(f'<svg id="{m.cid}-{rid}l" data-layout-allow-overlap style="position:absolute;left:0;top:-90px;width:1080px;height:1920px;overflow:visible;opacity:0;pointer-events:none"><path d="M{ax:.0f} {ay:.0f} L{x:.0f} {y:.0f}" style="stroke:#F5B04A;stroke-width:3;fill:none"/><circle cx="{x:.0f}" cy="{y:.0f}" r="7" style="fill:#F5B04A"/></svg>'
                  f'<div id="{m.cid}-{rid}" data-layout-allow-overlap style="position:absolute;left:{bx:.0f}px;top:{by - 90:.0f}px;width:{w}px;height:{h}px;border-radius:16px;overflow:hidden;border:3px solid #F5B04A;box-shadow:0 12px 32px rgba(0,0,0,0.65);background:#1B140F;opacity:0">{media}'
                  f'<div style="position:absolute;left:0;right:0;bottom:0;padding:26px 14px 8px;background:linear-gradient(180deg,rgba(18,13,10,0),rgba(18,13,10,.92));font-family:Inter,sans-serif;font-weight:800;font-size:32px;line-height:1.1;color:#F3E7D3">{cap}{sb}</div></div>')
    sel = f"#{m.cid}-{rid}"
    return (f'      tl.fromTo("{sel}", {{ opacity: 0, scale: 0.6, transformOrigin: "50% 100%" }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "back.out(1.6)" }}, {t_on});\n'
            f'      tl.fromTo("{sel}l", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, {t_on});\n'
            f'      tl.to(["{sel}", "{sel}l"], {{ opacity: 0, scale: 0.9, duration: 0.3, ease: "power2.in" }}, {t_off});\n')
def popups(m, items, end, **kw):
    """items: (rid, src, at, t, cap, box[, img, sub]); each pop-up stays until the next one appears."""
    js = ""
    for k, it in enumerate(items):
        rid, src, at, t, cap, box = it[:6]; img = it[6] if len(it) > 6 else None; sub = it[7] if len(it) > 7 else None
        t_off = items[k + 1][3] + 0.1 if k + 1 < len(items) else end
        js += popup(m, rid, src, at, t, t_off, cap, box=box, img=img, sub=sub, **kw)
    return js
def news(m, rid, outlet, date, headline, t_on, t_off, top=360):
    """Original news card quoting a published headline (outlet + date), not a scan."""
    m.html.append(f'<div id="{m.cid}-{rid}" data-layout-allow-overlap style="position:absolute;left:70px;right:70px;top:{top - 90}px;padding:22px 30px 20px;background:#F2EBDD;border-radius:8px;box-shadow:0 14px 36px rgba(0,0,0,0.6);transform:rotate(-1deg);opacity:0">'
                  f'<div style="display:flex;justify-content:space-between;align-items:baseline;border-bottom:2px solid #1B140F;padding-bottom:8px;margin-bottom:12px;font-family:Inter,sans-serif;color:#1B140F">'
                  f'<span style="font-weight:900;font-size:34px">{outlet}</span><span style="font-family:JetBrains Mono,monospace;font-size:26px">{date}</span></div>'
                  f'<div style="font-family:Instrument Serif,serif;font-size:50px;line-height:1.08;color:#1B140F">“{headline}”</div>'
                  f'<div style="font-family:JetBrains Mono,monospace;font-size:22px;color:#5A4A3A;margin-top:10px">Headline as published · card recreated for this video</div></div>')
    sel = f"#{m.cid}-{rid}"
    return (f'      tl.fromTo("{sel}", {{ opacity: 0, y: -30, rotation: -4 }}, {{ opacity: 1, y: 0, rotation: -1, duration: 0.5, ease: "back.out(1.4)" }}, {t_on});\n'
            f'      tl.to("{sel}", {{ opacity: 0, y: -20, duration: 0.3, ease: "power2.in" }}, {t_off});\n')
ON1 = lambda sel, t: f'      tl.fromTo("{sel}", {{ opacity: 0, scale: 0.6, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2)" }}, {t});\n'
OFF = lambda sel, t: f'      tl.to("{sel}", {{ opacity: 0, duration: 0.3 }}, {t});\n'
def P_(rid, at, t, m, label=None, dx=24, dy=-20, amb=True, right=False, size=30):
    """Pin + label at word time t (scene-relative)."""
    js = ON1(pin(m, rid, at), t)
    if label: js += SHOW(m.tag(rid + "t", label, at, dx=dx, dy=dy, amb=amb, right=right, size=size), t + 0.05)
    return js
OV = 0.35  # scene overlap: the next map fades in over the previous one
def go(m, s, e, js, focus=None, note="Schematic · positions: OpenStreetMap", last=False):
    """Render a map scene with a gentle zoom-in on entry and a dissolve into the next scene."""
    fx, fy = m.px(K(focus) if isinstance(focus, str) else focus) if focus else (540, MT + MH / 2)
    js = f'      tl.fromTo("#{m.cid}-fg", {{ scale: 1.12 }}, {{ scale: 1, duration: 1.0, ease: "power2.out", transformOrigin: "{fx:.0f}px {fy:.0f}px" }}, 0);\n' + js
    if not last:
        js += f'      tl.to("#{m.cid}-fg", {{ opacity: 0, scale: 1.08, duration: {OV}, ease: "power1.in", transformOrigin: "{fx:.0f}px {fy:.0f}px" }}, {round(e - s, 2)});\n'
    m.render(s, round(e + (0 if last else OV), 2), js, note=note, keep=not last)
TL, TR, BL, BR = (48, 360), (632, 360), (48, 1090), (632, 1090)
NOTE_C = "Schematic · clips: representative footage"

# 0 · cover (0–2.45): Ajmer Road hero, fully formed on frame 0 for the reel thumbnail
cv = Map("cv", -66, 22, 140)
cv.svg.append(f'<g style="stroke:rgba(243,231,211,0.05);stroke-width:{cv.u}">' + "".join(f'<path d="M{x} -120 V120"/>' for x in range(-150, 40, 10)) + "</g>")
cv.svg.append(f'<path d="{smooth(CORE)}" style="fill:rgba(243,231,211,0.10);stroke:rgba(243,231,211,0.3);stroke-width:{2*cv.u}"/>')
for r in ("sring", "delhiNH", "tonk", "agra"): cv.svg.append(f'<path d="{smooth(ROADS[r], False)}" style="fill:none;stroke:rgba(243,231,211,0.22);stroke-width:{3*cv.u}"/>')
cv.svg.append(f'<path d="{smooth(ROADS["nh48w"], False)}" style="fill:none;stroke:#F5B04A;stroke-width:{14*cv.u};stroke-linecap:round;filter:url(#cv-glow)"/>')
cv.svg.append(f'<path d="{smooth([K("ajmer"), K("pushkar")], False)}" style="fill:none;stroke:#F5B04A;stroke-width:{8*cv.u};stroke-linecap:round;filter:url(#cv-glow)"/>')
cvjs = ""
for k, (key, lab, dx, dy) in enumerate([("hirapura", "JAIPUR", -40, 40), ("bagru", "BAGRU", -60, 40), ("dudu", "DUDU", -40, 40), ("kishangarh", "KISHANGARH", -110, 40), ("ajmer", "AJMER", -30, 44), ("pushkar", "PUSHKAR", -60, -80)]):
    cv.dot(key, big=True)
    cv.html.append(f'<div class="tag amb" style="left:{min(870, max(48, cv.px(K(key))[0] + dx)):.0f}px;top:{cv.px(K(key))[1] + dy - 90:.0f}px;font-size:30px;padding:8px 16px">{lab}</div>')
cv.html.append('<div style="position:absolute;left:70px;right:70px;top:250px;font-family:Inter,sans-serif;font-weight:900;font-size:170px;line-height:0.92;letter-spacing:-0.01em;color:#F3E7D3;text-shadow:0 8px 40px rgba(0,0,0,0.6)">AJMER<br><span style="color:#F5B04A">ROAD</span></div>'
               '<div style="position:absolute;left:76px;right:70px;top:620px;font-family:Inter,sans-serif;font-weight:800;font-size:52px;line-height:1.1;color:#F3E7D3">Jaipur → Ajmer<br>every stretch, decoded</div>'
               '<div style="position:absolute;left:76px;top:1210px;padding:12px 22px;border-radius:14px;background:rgba(60,38,14,0.92);border:2px solid #E3A23B;font-family:Inter,sans-serif;font-weight:800;font-size:40px;color:#F3E7D3">NH-48 · 9 stretches · 2 new expressways</div>')
cvjs += f'      tl.to("#cv-fg", {{ scale: 2.4, opacity: 0, duration: 0.6, ease: "power2.in", transformOrigin: "{cv.px(K("hirapura"))[0]:.0f}px {cv.px(K("hirapura"))[1]:.0f}px" }}, 2.0);\n'
cv.render(0, 2.6, cvjs, note=None, keep=True, fade_in=False)

# 1 · 200-ft bypass → Bhankrota: bus terminal, Westway Heights, PinkWest (2.45–23.4)
s, e = 2.45, 23.4; m = Map("m1", -12, 5.6, 10).base(sring=False, nring=False)
rN = line(m, "rn", ROADS["nh48w"][:4], width=10)
js = DR(rN, 0.5, 1.4) + SHOW(m.tag("t0", "AJMER ROAD (NH-48)", km(26.880, 75.718), dx=-60, dy=60, amb=True), 0.9)
js += P_("p0", "hirapura", rel(3.3, s), m, "200-ft Bypass", dx=24, dy=-70)
js += P_("p1", "hirapura", rel(4.9, s), m, None) + SHOW(m.tag("p1t", "Hirapura bus terminal", "hirapura", dx=24, dy=10, size=28), rel(4.95, s))
js += P_("p2", "keshopura", rel(6.5, s), m, "Keshopura", dx=-10, dy=-80)
js += P_("p3", "westway", rel(7.7, s), m, "Westway Heights", dx=24, dy=-80) + OFF("#m1-t0", rel(7.5, s))
js += P_("p4", "bhankrota", rel(8.7, s), m, "Bhankrota", dx=-30, dy=-80, right=True)
js += ON1(badge(m, "b1", "vrb", "VRB Golden Tower · upcoming", dx=-300, dy=-150, size=28), rel(12.2, s))
js += news(m, "n1", "Construction World", "", "Manglam Group Launches Rs 1,000 Cr PinkWest in West Jaipur", rel(14.6, s), rel(17.0, s))
js += popup(m, "q0", "freeway", "hirapura", rel(5.0, s), rel(12.1, s), "Bus terminal", box=BR)
js += popup(m, "pv", None, "vrb", rel(12.3, s), rel(16.9, s), "VRB Golden Tower", w=330, h=590, img="vrb.jpg", sub="Developer render · supplied", box=(700, 800))
js += popup(m, "pp", None, "pinkwest", rel(13.9, s), rel(20.9, s), "Manglam PinkWest", w=430, h=430, img="pinkwest.jpg", sub="Developer render · supplied", box=(48, 980))
js += popups(m, [("q2", "freeway", "hirapura", rel(17.0, s), "Transport anchor", BR), ("q3", "market", "pinkwest", rel(21.2, s), "Shops", BL),
                 ("q4", "office", "vrb", rel(21.8, s), "Offices", BR), ("q5", "dining", "westway", rel(22.6, s), "Services", BL)], rel(23.4, s) - 0.1)
go(m, s, e, js, focus="hirapura", note="Schematic · positions approx. (OpenStreetMap)")

# 2 · the 200-ft bypass junction goes signal-free (23.4–31.25)
s, e = 23.4, 31.25
J = K("hirapura"); m = Map("m2", J[0], J[1] + 0.2, 4.2).base(sring=False, nring=False, core=False, wall=False)
ew = [km(26.8925, 75.700), J, km(26.8840, 75.775)]; ns = [km(26.950, 75.745), J, km(26.830, 75.725)]
m.svg.append(f'<path d="{smooth(ew, False)}" style="fill:none;stroke:rgba(243,231,211,0.35);stroke-width:{26*m.u};stroke-linecap:round"/><path d="{smooth(ns, False)}" style="fill:none;stroke:rgba(243,231,211,0.35);stroke-width:{26*m.u};stroke-linecap:round"/>')
f1 = line(m, "f1", [km(26.8915, 75.717), km(26.8905, 75.733), km(26.8880, 75.744), km(26.8860, 75.758)], color="#F5B04A", width=12)
f2 = line(m, "f2", [km(26.8870, 75.757), km(26.8890, 75.745), km(26.8912, 75.732), km(26.8922, 75.716)], color="#F5B04A", width=12)
u1 = line(m, "u1", [km(26.912, 75.7425), km(26.8895, 75.7378), km(26.866, 75.733)], color="#7FC8F8", width=10)
u2 = line(m, "u2", [km(26.866, 75.7355), km(26.8888, 75.7400), km(26.911, 75.7450)], color="#7FC8F8", width=10)
js = SHOW(m.tag("j0", "200-ft Bypass junction", J, dx=30, dy=-150, amb=True), 0.3)
js += SHOW(m.tag("j1", "Ajmer Rd", km(26.8925, 75.704), dx=0, dy=-70, size=28), 0.5) + SHOW(m.tag("j2", "Delhi / Mansarovar", km(26.935, 75.743), dx=20, dy=0, size=28), 0.5)
js += DR(f1, rel(26.0, s), 0.8) + DR(f2, rel(26.3, s), 0.8) + SHOW(m.tag("j3", "▲ 2 flyovers", km(26.8935, 75.722), dx=0, dy=-80, size=30, amb=True), rel(26.1, s))
js += DR(u1, rel(26.9, s), 0.8) + DR(u2, rel(27.2, s), 0.8) + SHOW(m.tag("j4", "▼ 2 underpasses", km(26.870, 75.733), dx=30, dy=-60, size=30), rel(27.0, s))
js += news(m, "n1", "Construction World", "Mar 2026", "NHAI Awards Contract for Flyovers and Underpasses at Jaipur Junction", rel(27.8, s), rel(31.2, s))
js += SHOW(m.chip("c1", "Awarded · NHAI (EPC)", "₹130.65 cr · signal-free junction on NH-48"), rel(28.6, s))
js += popups(m, [("q0", "avenue", J, rel(24.7, s), "Flyovers", BL)], rel(27.7, s))
go(m, s, e, js, focus="hirapura", note="Schematic layout · reported scope")

# 3 · Mahapura and the Southern Ring Road to Tonk Rd and Bagrana (31.25–39.5)
s, e = 31.25, 39.5; m = Map("m3", -2, 12, 40).base(sring=False, nring=False)
rS = line(m, "rs", ROADS["sring"], width=10)
js = P_("p0", "mahapura", rel(32.4, s), m, "Mahapura", dx=-30, dy=-80, right=True)
js += DR(rS, rel(34.1, s), 2.6) + SHOW(m.tag("t0", "SOUTHERN RING ROAD", km(26.745, 75.850), dx=-180, dy=40, amb=True), rel(34.6, s))
js += P_("p1", km(26.765, 75.800), rel(36.9, s), m, "Tonk Rd", dx=20, dy=10, amb=False)
js += P_("p2", "bagrana", rel(37.8, s), m, "Bagrana · Agra Rd", dx=-40, dy=40, right=True)
js += popups(m, [("q0", "cityhwy", "mahapura", rel(32.6, s), "Ring Road link", TR), ("q1", "hwysun", "bagrana", rel(37.9, s), "Agra Road", BL)], rel(39.4, s))
go(m, s, e, js, focus="mahapura")

# 4 · Jaipur–Bandikui link to the Delhi–Mumbai Expressway (39.5–47.5)
s, e = 39.5, 47.5; m = Map("m4", 32, -3, 125).base(sring=True, nring=False, wall=False)
for r in ("nh48w", "delhiNH"): m.svg.append(f'<path d="{smooth(ROADS[r], False)}" style="fill:none;stroke:rgba(243,231,211,0.30);stroke-width:{3*m.u}"/>')
rB = line(m, "rb", ROADS["bdk"], width=10); rE = line(m, "re", ROADS["dme"], color="#7FC8F8", width=10)
js = SHOW(m.tag("t9", "Jaipur", "hawa", dx=-140, dy=-30, size=30), 0.2) + ON1(pin(m, "pb", "bagrana"), 0.3)
js += DR(rB, rel(40.4, s), 1.4) + SHOW(m.tag("t0", "Jaipur–Bandikui link", km(26.97, 76.25), dx=-120, dy=50, amb=True), rel(40.8, s))
js += P_("p1", "bandikui", rel(41.6, s), m, "Bandikui", dx=24, dy=10)
js += DR(rE, rel(42.4, s), 1.4) + SHOW(m.tag("t1", "Delhi–Mumbai Expressway", km(27.45, 76.75), dx=-330, dy=-40, amb=True), rel(42.8, s))
js += f'      tl.to("#m4-rn", {{ opacity: 1, duration: 0.4 }}, {rel(44.6, s)});\n'
m.svg.append(f'<path id="m4-rn" d="{smooth(ROADS["nh48w"][:8], False)}" style="fill:none;stroke:#F5B04A;stroke-width:{9*m.u};stroke-linecap:round;opacity:0;filter:url(#m4-glow)"/>')
js += SHOW(m.tag("t2", "Ajmer Rd", K("bagru"), dx=-60, dy=30, amb=True), rel(44.7, s))
js += news(m, "n1", "Swarajya", "Jul 2025", "Bagrana–Bandikui link of Delhi–Mumbai Expressway opens to reduce Jaipur–Delhi travel time to 3.5 hours", rel(44.9, s), rel(47.4, s))
js += popups(m, [("q0", "hwypov", "bandikui", rel(41.7, s), "Expressway link", BR)], rel(44.8, s))
go(m, s, e, js, focus="bagrana")

# 5 · Chitroli and the proposed Northern Ring Road arc (47.5–59.25)
s, e = 47.5, 59.25; m = Map("m5", -3, -6, 62).base(sring=True, nring=False)
js = P_("p0", "chitroli", rel(48.1, s), m, "Chitroli", dx=-30, dy=-80, right=True) + P_("p1", "bagru", rel(49.2, s), m, "Bagru", dx=-30, dy=20, right=True, amb=False)
js += DR(line(m, "nr", ROADS["nring"], color="#B8E07A", width=7), rel(51.8, s), 6.2)
js += SHOW(m.tag("t0", "NORTHERN RING ROAD · proposed", km(27.05, 75.60), dx=-120, dy=-90, amb=True, size=30), rel(52.2, s))
for k, (key, lab, t, dx, dy) in enumerate([("kalwar", "Kalwar Rd", 55.1, -40, 20), (km(27.110, 75.700), "Sikar Rd", 56.2, -30, -70), (km(27.135, 75.830), "Delhi Rd", 57.1, -10, -70), (km(27.020, 75.985), "Agra Rd", 58.0, -160, 20)]):
    js += P_(f"r{k}", key, rel(t, s), m, lab, dx=dx, dy=dy, amb=False)
js += news(m, "n1", "Patrika", "Dec 2025", "Jaipur Northern Ring Road project: land measurement and survey for 99 km ring begins", rel(50.3, s), rel(53.6, s))
js += popups(m, [("q0", "build", "chitroli", rel(48.3, s), "Proposed link", TR)], rel(50.2, s))
go(m, s, e, js, focus="chitroli", note="Schematic · proposed alignment as reported")

# 6 · Mahapura vs Chitroli (59.25–66.85)
s, e = 59.25, 66.85; m = Map("m6", -20.5, 8.2, 24).base(sring=True, nring=False)
js = DR(line(m, "nr", ROADS["nring"][:4], color="#B8E07A", width=7), 0.1, 1.0)
cM = m.circle("cm", "mahapura", 1.6, "rgba(245,176,74,0.25)", "#F5B04A"); cC = m.circle("cc", "chitroli", 1.6, "rgba(160,220,120,0.25)", "#B8E07A")
js += POP(cM, rel(59.4, s)) + SHOW(m.tag("t0", "Mahapura", "mahapura", dx=40, dy=-60, amb=True), rel(59.4, s))
js += POP(cC, rel(60.0, s)) + SHOW(m.tag("t1", "Chitroli", "chitroli", dx=-60, dy=60, amb=True), rel(60.0, s))
js += SHOW(m.chip("c1", "Mahapura · existing", "Southern Ring Road · serves the southern corridor", y=430), rel(62.3, s))
js += SHOW(m.chip("c2", "Chitroli · proposed", "Northern Ring Road · Ajmer Road end (as reported)", y=1180), rel(64.7, s))
go(m, s, e, js, focus=km(26.85, 75.63), note="Schematic · two separate locations")

# 7 · Mahindra World City · Kalwara (66.85–77.6)
s, e = 66.85, 77.6; m = Map("m7", -19.5, 14, 20).base(sring=True, nring=False)
cW = m.circle("cw", "mwc", 2.4, "rgba(127,200,248,0.22)", "#7FC8F8")
js = POP(cW, rel(68.4, s)) + P_("p0", "mwc", rel(68.4, s), m, "Mahindra World City", dx=30, dy=-80)
js += P_("p1", "kalwara", rel(71.0, s), m, "Kalwara", dx=-90, dy=10, right=True, amb=False)
js += ON1(badge(m, "b1", "mwc", "Infosys", dx=-330, dy=170), rel(72.5, s)) + ON1(badge(m, "b2", "mwc", "Deutsche Bank", dx=60, dy=170), rel(73.3, s))
js += SHOW(m.chip("c1", "Employment anchor", "SEZ · Infosys and Deutsche Bank were its first anchor clients"), rel(75.1, s))
js += popups(m, [("q0", "corporate", "mwc", rel(68.6, s), "IT & business park", TL), ("q1", "coworkers", "mwc", rel(74.3, s), "Jobs", TR)], rel(77.5, s))
go(m, s, e, js, focus="mwc")

# 8 · Dehmi Kalan · Manipal University: what to study around a campus (77.6–88.4)
s, e = 77.6, 88.4; m = Map("m8", -25, 8, 18).base(sring=True, nring=False)
cU = m.circle("cu", "manipal", 1.5, "rgba(127,200,248,0.22)", "#7FC8F8")
js = P_("p0", "manipal", rel(78.0, s), m, "Dehmi Kalan", dx=30, dy=-80) + POP(cU, rel(79.5, s)) + ON1(badge(m, "b1", "manipal", "Manipal University Jaipur", dx=-200, dy=110), rel(79.5, s))
for k, (txt, t) in enumerate([("◆ Student accommodation", 81.6), ("◆ Rental housing", 82.8), ("◆ Food outlets", 83.8), ("◆ Everyday retail", 85.5)]):
    m.html.append(f'<div class="tag amb" id="m8-w{k}" style="left:60px;top:{1180 + k * 62 - 90}px;font-size:30px;padding:10px 18px">{txt}</div>')
    js += SHOW(f"#m8-w{k}", rel(t, s))
js += popups(m, [("q0", "campus", "manipal", rel(79.6, s), "Campus", TL), ("q1", "students", "manipal", rel(81.6, s), "Student accommodation", TL),
                 ("q2", "rental", "manipal", rel(82.8, s), "Rental housing", TR), ("q3", "dining", "manipal", rel(83.8, s), "Food outlets", TL),
                 ("q4", "market", "manipal", rel(85.5, s), "Everyday retail", TR)], rel(88.3, s))
go(m, s, e, js, focus="manipal")

# 9 · Bagru industrial belt: block-printing heritage (88.4–97.5)
s, e = 88.4, 97.5; m = Map("m9", -30, 10, 26).base(sring=False, nring=False, wall=False)
rN = line(m, "rn", ROADS["nh48w"][3:8], width=9)
cB = m.circle("cb", "bagru", 2.2, "rgba(232,102,74,0.22)", "#E8664A")
js = DR(rN, 0.3, 1.2) + POP(cB, rel(89.6, s)) + P_("p0", "bagru", rel(89.6, s), m, "Bagru Industrial Belt", dx=30, dy=-80)
js += popups(m, [("q0", "factory", "bagru", rel(90.2, s), "Industrial belt", TR), ("q1", None, "bagru", rel(91.9, s), "Bagru block printing", TL, "block.jpg", "Photo · Anildiggiwal, CC0")], rel(97.4, s), w=470, h=320)
js += SHOW(m.chip("c1", "Heritage craft", "Hand block printing on textiles · Bagru"), rel(93.7, s))
go(m, s, e, js, focus="bagru")

# 10 · Mahla, Mokhampura, Dudu; roads to Phulera, Narena, Sambhar; what changes here (97.5–116.4)
s, e = 97.5, 116.4; m = Map("m10", -62, 14, 62).base(sring=False, nring=False, wall=False, core=False)
rN = line(m, "rn", ROADS["nh48w"][5:10], width=9)
js = DR(rN, 0.2, 1.0)
for k, (key, lab, t, dx, dy) in enumerate([("mahla", "Mahla", 98.5, -20, -80), ("mokhampura", "Mokhampura", 99.2, -40, 30), ("dudu", "Dudu", 100.1, 30, 0)]):
    js += P_(f"p{k}", key, rel(t, s), m, lab, dx=dx, dy=dy)
for k, (r, key, lab, t, dx, dy) in enumerate([("phulera", "phulera", "Phulera", 102.7, 24, -40), ("narena", "narena", "Narena", 103.6, -30, 30), ("sambhar", "sambhar", "Sambhar", 104.5, -30, -60)]):
    js += DR(line(m, f"l{k}", ROADS[r], color="#B8E07A", width=6), rel(t, s) - 0.3, 0.7) + P_(f"s{k}", key, rel(t, s), m, lab, dx=dx, dy=dy, amb=False, right=dx < 0)
for k, (txt, t) in enumerate([("◆ Warehouses", 108.9), ("◆ Highway services", 109.7), ("◆ Larger land parcels", 111.6), ("◆ Tourism-linked businesses", 112.9)]):
    m.html.append(f'<div class="tag amb" id="m10-w{k}" style="left:48px;top:{1150 + k * 62 - 90}px;font-size:30px;padding:10px 18px">{txt}</div>')
    js += SHOW(f"#m10-w{k}", rel(t, s))
js += popups(m, [("q0", "trucks", "dudu", rel(108.9, s), "Warehouses & logistics", TR), ("q1", "hwypov", "dudu", rel(109.7, s), "Highway services", TL),
                 ("q2", "fields", "dudu", rel(111.6, s), "Larger land parcels", TR), ("q3", "rental", "sambhar", rel(112.9, s), "Tourism-linked stays", TL)], rel(116.3, s))
go(m, s, e, js, focus="dudu", note="Schematic · some positions approximate")

# 11 · Bandar Sindri → Kishangarh (marble, airport) → Ajmer, Pushkar (116.4–126.6)
s, e = 116.4, 126.6; m = Map("m11", -104, 42, 56).base(sring=False, nring=False, wall=False, core=False)
rN = line(m, "rn", ROADS["nh48w"][9:], width=9); rP = line(m, "rp", [K("ajmer"), K("pushkar")], width=7)
js = DR(rN, 0.2, 1.2)
js += P_("p0", "bandarsindri", rel(116.8, s), m, "Bandar Sindri", dx=24, dy=-70) + P_("p1", "kishangarh", rel(118.1, s), m, "Kishangarh", dx=24, dy=-10)
js += P_("p2", "kgairport", rel(120.8, s), m, "✈ Kishangarh Airport", dx=-30, dy=-80, right=True, amb=False)
js += P_("p3", "ajmer", rel(123.5, s), m, "Ajmer", dx=24, dy=0) + DR(rP, rel(124.0, s), 0.6) + P_("p4", "pushkar", rel(124.2, s), m, "Pushkar", dx=-30, dy=20, right=True)
js += SHOW(m.chip("c1", "Kishangarh", "Known as a marble trading &amp; processing hub"), rel(119.4, s))
js += popups(m, [("q0", "marble", "kishangarh", rel(119.1, s), "Marble trade", TR), ("q1", "camels", "pushkar", rel(124.4, s), "Tourism · Pushkar", TL)], rel(126.5, s))
go(m, s, e, js, focus="kishangarh")

# 12 · proposed Kotputli–Kishangarh expressway: through traffic around Jaipur; interchanges, logistics (126.6–147.4)
s, e = 126.6, 147.4; m = Map("m12", -28, -22, 175).base(sring=True, nring=False, wall=False)
for r in ("nh48w", "delhiNH"): m.svg.append(f'<path d="{smooth(ROADS[r], False)}" style="fill:none;stroke:rgba(243,231,211,0.40);stroke-width:{4*m.u}"/>')
js = SHOW(m.tag("t9", "Jaipur", "hawa", dx=20, dy=-20, size=30), 0.2) + P_("p0", "kotputli", rel(128.0, s), m, "Kotputli", dx=24, dy=-20) + P_("p1", "kishangarh", rel(128.7, s), m, "Kishangarh", dx=-30, dy=20, right=True)
js += DR(line(m, "kk", ROADS["kk"], color="#F5B04A", width=9), rel(129.3, s), 2.4)
js += SHOW(m.tag("t0", "Kotputli–Kishangarh Expressway · proposed", km(27.20, 75.45), dx=-330, dy=-110, amb=True, size=28), rel(129.6, s))
js += SHOW(m.chip("c1", "Proposed · greenfield (as reported)", "≈181 km · ≈₹6,906 cr · bypasses Jaipur to the west", y=360), rel(130.4, s))
m.html[-1] = m.html[-1].replace("right:64px", "right:330px")
js += f'      tl.to("#m12-c1", {{ opacity: 0, duration: 0.3 }}, {rel(137.9, s)});\n'
tr = line(m, "tr", [km(27.75, 76.25), K("kotputli"), km(27.45, 75.85), km(27.15, 75.55), K("jobner"), km(26.80, 75.15), K("kishangarh"), K("ajmer")], color="#7FC8F8", width=5)
js += f'      tl.set("#m12-tr", {{ strokeDasharray: "0.04 0.04", opacity: 0 }}, 0);\n      tl.to("#m12-tr", {{ opacity: 1, duration: 0.4 }}, {rel(131.4, s)});\n      tl.fromTo("#m12-tr", {{ strokeDashoffset: 0.4 }}, {{ strokeDashoffset: 0, duration: 3.5, ease: "none", repeat: 1 }}, {rel(131.4, s)});\n'
js += SHOW(m.tag("t1", "Delhi ↔ Ajmer through traffic", km(27.55, 75.95), dx=20, dy=10, size=28), rel(131.5, s))
js += f'      tl.to(["#m12-rd", "#m12-rdt"], {{ opacity: 1, duration: 0.4 }}, {rel(135.4, s)});\n'
m.html.append(f'<div class="tag" id="m12-rdt" style="left:{m.px(K("hawa"))[0] - 470:.0f}px;top:{m.px(K("hawa"))[1] + 60 - 90:.0f}px;font-size:28px;padding:8px 16px;opacity:0">Less pressure on existing highways</div>')
m.svg.append(f'<circle id="m12-rd" cx="{K("hawa")[0]:.3f}" cy="{K("hawa")[1]:.3f}" r="{22*m.u*4:.3f}" style="fill:rgba(127,200,248,0.12);stroke:#7FC8F8;stroke-width:{3*m.u};opacity:0"/>')
for k, p in enumerate([ROADS["kk"][1], ROADS["kk"][2], K("jobner"), ROADS["kk"][4]]):
    js += ON1(m.exitmark(f"x{k}", p), rel(139.2, s) + 0.15 * k)
js += OFF("#m12-rdt", rel(141.0, s))
js += SHOW(m.chip("c2", "Designated interchanges", "Reported: 9 entry/exit points, incl. near Jobner", y=360), rel(139.4, s))
m.html[-1] = m.html[-1].replace("right:64px", "right:330px")
js += news(m, "n1", "Patrika", "Mar 2026", "Rajasthan to get 181km greenfield expressway passing through 5 districts, easing travel to Delhi", rel(127.6, s), rel(130.3, s))
js += popups(m, [("q0", "trucks", K("jobner"), rel(141.2, s), "Logistics", BL), ("q1", "hwysun", K("jobner"), rel(143.4, s), "Trucks & warehouses", BL)], rel(147.2, s))
go(m, s, e, js, focus="jobner", note="Schematic · proposed alignment approximate", last=True)


# ---------- chrome ----------
SECT = [(2.45, "STRETCH 1", "200-ft Bypass → Bhankrota"), (23.4, "200-FT BYPASS", "Going signal-free"), (31.25, "MAHAPURA", "Southern Ring Road"),
        (39.5, "WIDER NETWORK", "Link to Delhi–Mumbai E-way"), (47.5, "CHITROLI", "Northern Ring Rd · proposed"), (59.25, "DON'T MIX THEM UP", "Mahapura ≠ Chitroli"),
        (66.85, "MAHINDRA WORLD CITY", "Employment anchor"), (77.6, "DEHMI KALAN", "Manipal University"), (88.4, "BAGRU", "Industry &amp; block printing"),
        (97.5, "MAHLA → DUDU", "Highway belt"), (116.4, "KISHANGARH → AJMER", "Marble · airport · Pushkar"), (126.6, "PROPOSED", "Kotputli–Kishangarh E-way"), (147.4, "SHARE THIS", "One road, many demands")]
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

MIXKIT = ["Aerial shot of a busy avenue in the city", "Aerial view of a highway in a big city", "Traffic on a freeway", "Corporate and business buildings in the city", "Market shoppers", "Open office space", "Customers in a minimalist style restaurant", "Students walking on a university campus", "Students walking in a university", "Interior of a room with terrace", "Two coworkers talking and laughing", "Aerial view of a factory", "Trailers crossing a bridge over a scenic valley landscape", "Speedy point-of-view tour of a highway", "Traveling on the highway on a sunny day", "A road between a big green agriculture field", "Buildings under construction, aerial view", "Detailed texture of a smooth marble surface", "Camels walking in the desert"]

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
