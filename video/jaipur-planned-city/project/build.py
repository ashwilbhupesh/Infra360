"""Jaipur planning reel: satellite + OSM world in one SVG with an animated viewBox camera.
World units = Web-Mercator pixels at zoom 14, origin at tile (11640, 6916)."""
import json, math, glob, re, os
P = "proj"
def wp(lat, lon):
    n = 256 * 2 ** 14
    x = (lon + 180) / 360 * n; y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    return (x - 11640 * 256, y - 6916 * 256)

# ---------------- script → caption timings (estimated until the real recording arrives) ----------------
WORDS_JSON = "words.json"
SCRIPT = [
 "Jaipur was designed 300 years ago — on paper.",
 "In 1727, Maharaja Sawai Jai Singh II decided to move his capital down from Amer fort.",
 "And he gave the job to a young architect from Bengal — Vidyadhar Bhattacharya.",
 "Vidyadhar used the ancient Vastu Shastra — a grid of nine squares, like a mandala.",
 "Each block became a neighbourhood, for a trade or a community.", "The palace sits right in the centre.",
 "Then the roads.", "Three wide streets east to west, crossed by streets north to south.",
 "Where they meet — the great chaupars: Badi Chaupar, Choti Chaupar — once with water tanks in the middle.",
 "All of it inside a city wall, with seven gates.",
 "And in 1876, the whole city was painted pink to welcome the Prince of Wales — which is why we're the Pink City.",
 "In 2019, UNESCO declared the walled city a World Heritage Site — for its planning.",
 "And the planning didn't stop.", "C-Scheme and MI Road in the 1940s.",
 "Then Malviya Nagar, Jawahar Nagar, and Vidyadhar Nagar — named after the architect himself.",
 "Then Mansarovar, one of Jaipur's biggest planned colonies.", "And today — the Ring Road and the Metro.",
 "300 years later, Jaipur is still growing on a plan.",
 "Send this to someone who loves Jaipur — and tell me in the comments: which area do you live in?"]
if os.path.exists(WORDS_JSON):
    words = [{"t": w["text"], "s": w["start"]} for w in json.load(open(WORDS_JSON))]
    ESTIMATED = False
else:
    words, t = [], 0.45
    for sent in SCRIPT:
        for tok in sent.replace("—", " — ").split():
            if tok == "—": t += 0.18; continue
            words.append({"t": tok, "s": round(t, 2)})
            t += 0.30 + 0.035 * max(0, len(tok) - 4)
        t += 0.38
    ESTIMATED = True
END = round(words[-1]["s"] + 1.6, 2)
def cue(*seq, after=0.0):
    """Time of the first word matching the sequence (case-insensitive prefix match), searching after `after` seconds."""
    seq = [s.lower() for s in seq]
    for i, w in enumerate(words):
        if w["s"] < after: continue
        if all(i + k < len(words) and re.sub(r"[^\w]", "", words[i + k]["t"].lower()).startswith(seq[k]) for k in range(len(seq))): return w["s"]
    raise KeyError(seq)

EM = {"designed", "1727,", "amer", "vidyadhar", "bhattacharya.", "nine", "mandala.", "palace", "roads.", "chaupars:", "wall,", "seven", "pink", "1876,", "2019,",
      "unesco", "heritage", "c-scheme", "mi", "malviya", "jawahar", "mansarovar,", "ring", "metro.", "300", "plan.", "jaipur", "jaipur."}
def glen(g): return len(" ".join(w["t"] for w in g))
groups, cur = [], []
for i, w in enumerate(words):
    cur.append(w); nx = words[i + 1] if i + 1 < len(words) else None
    if nx is None or glen(cur + [nx]) > 22 or w["t"][-1] in ".?!:" or (w["t"][-1] == "," and glen(cur) >= 10) or (nx["s"] - w["s"] > 1.0):
        groups.append(cur); cur = []
caps = []
for gi, g in enumerate(groups):
    nx = groups[gi + 1][0]["s"] - 0.03 if gi + 1 < len(groups) else END
    caps.append((round(max(0.02, g[0]["s"] - 0.05), 2), round(min(nx, g[-1]["s"] + 0.8), 2), g))
json.dump({"captions": [{"start": a, "end": b, "text": " ".join(w["t"] for w in g)} for a, b, g in caps], "estimated": ESTIMATED}, open("captions.json", "w"), indent=1)

# ---------------- OSM data ----------------
def elems(f):
    out = []
    for p in glob.glob(f):
        try: out += json.load(open(p)).get("elements", [])
        except Exception: pass
    return out
def geom(e): return [wp(g["lat"], g["lon"]) for g in e.get("geometry", [])]
def pd(pts, close=False): return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + (" Z" if close else "")
BLD = [geom(e) for e in elems("osm/bld*.json") if e.get("geometry")]
ROADS = [(e.get("tags", {}), geom(e)) for e in elems("osm/roads_*.json") if e.get("geometry")]
WALL = [geom(e) for e in elems("osm/wall.json") if e.get("geometry")]
METRO = [geom(e) for e in elems("osm/metro.json") if e.get("geometry")]
def named(*names): return [p for t, p in ROADS if any(n.lower() == (t.get("name") or "").lower() for n in names)]
EW = named("Chandpol Bazaar", "Tripolia Bazaar", "Ramganj Bazaar", "Sujrapol Bazaar Road")
NS = named("Kishanpole Bazar Road", "Chaura Rasta", "Johari Bazar", "Gangauri Bazaar", "Ghat Darwaja Bazaar Road")
MIR = named("Mirza Ismail Road")
def ptc(lat, lon): return wp(lat, lon)
L = {"amer": ptc(26.9855, 75.8513), "palace": ptc(26.9258, 75.8237), "hawa": ptc(26.92393, 75.82687), "jantar": ptc(26.92473, 75.82451),
     "badi": ptc(26.9239, 75.8273), "choti": ptc(26.9244, 75.8203), "chandpole": ptc(26.9262, 75.8090), "surajpole": ptc(26.9205, 75.8445),
     "ajmeri": ptc(26.9157, 75.8133), "sanganeri": ptc(26.9150, 75.8231), "ghat": ptc(26.9123, 75.8394), "newgate": ptc(26.9151, 75.8186),
     "cscheme": ptc(26.906, 75.803), "miroad": ptc(26.915, 75.805), "malviya": ptc(26.854, 75.814), "jawahar": ptc(26.889, 75.838),
     "vidyadhar": ptc(26.960, 75.785), "mansarovar": ptc(26.857, 75.763), "talkatora": ptc(26.9329, 75.8250)}
# walled city outline from the OSM wall pieces (convex hull for the pink wash)
allw = [q for p in WALL for q in p]
def hull(pts):
    pts = sorted(set((round(x, 1), round(y, 1)) for x, y in pts))
    def cr(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]
WH = hull(allw)
wx = [p[0] for p in allw]; wy = [p[1] for p in allw]
WC = ((min(wx) + max(wx)) / 2, (min(wy) + max(wy)) / 2); WW = max(wx) - min(wx)
# ---- the plan, fitted to the real streets (OSM): main bazaar axis Chandpole → Suraj Pol, cross streets at the chaupars ----
G = {"chandpole": ptc(26.92656, 75.80791), "surajpole": ptc(26.91916, 75.84494), "choti": ptc(26.92470, 75.81850), "badi": ptc(26.92275, 75.82670),
     "sanganeri": ptc(26.91587, 75.82480), "ajmeri": ptc(26.91710, 75.81649), "newgate": ptc(26.91615, 75.82022), "ghat": ptc(26.91357, 75.83281)}
for k in ("choti", "badi", "chandpole", "surajpole", "sanganeri", "ajmeri", "newgate", "ghat"): L[k] = G[k]
O = G["chandpole"]; ex, ey = G["surajpole"][0] - O[0], G["surajpole"][1] - O[1]; ln = math.hypot(ex, ey); E = (ex / ln, ey / ln); N = (E[1], -E[0])
def uv(p): return ((p[0] - O[0]) * E[0] + (p[1] - O[1]) * E[1], (p[0] - O[0]) * N[0] + (p[1] - O[1]) * N[1])
def xy(u, v): return (O[0] + E[0] * u + N[0] * v, O[1] + E[1] * u + N[1] * v)
US = [0, uv(G["choti"])[0], uv(G["badi"])[0], ln]
VS0 = uv(G["sanganeri"])[1]; VS = [VS0, 0, -VS0, -2 * VS0]          # south wall, main bazaar, two rows north
# ---- the real plan: the 8 chowkris (districts) from the supplied plan diagram, pinned to the real streets ----
PX_X = [37, 202, 282, 359, 510, 700]
U_X = [0, uv(G["choti"])[0], uv(G["newgate"])[0], uv(G["badi"])[0], uv(G["ghat"])[0], ln]
VSOUTH = sum(uv(G[k])[1] for k in ("sanganeri", "ajmeri", "newgate", "ghat")) / 4
def interp(x, xs, ys):
    for k in range(len(xs) - 1):
        if x <= xs[k + 1] or k == len(xs) - 2:
            t = (x - xs[k]) / (xs[k + 1] - xs[k]); return ys[k] + t * (ys[k + 1] - ys[k])
def pm(x, y):  # plan-diagram pixel → world
    return xy(interp(x, PX_X, U_X), (y - 282) / (396 - 282) * VSOUTH)
DIST_PX = {
 "Purani Basti": [(37,281),(37,220),(50,200),(75,165),(135,128),(160,140),(165,153),(200,155),(202,281)],
 "Topkhana Desh": [(37,283),(202,283),(202,395),(37,395)],
 "Modikhana": [(202,283),(282,283),(282,395),(202,395)],
 "Visheshraji": [(282,283),(359,283),(359,395),(282,395)],
 "Ghat": [(359,283),(513,283),(513,395),(359,395)],
 "Topkhana Hazuri": [(513,283),(695,283),(695,352),(708,352),(708,395),(513,395)],
 "Ramchandraji": [(364,170),(513,170),(513,281),(364,281)],
 "Gangapol": [(362,170),(410,75),(445,75),(445,47),(500,47),(500,22),(532,22),(532,52),(513,55),(513,170)],
 "Sarhad · City Palace": [(178,75),(410,75),(362,170),(362,281),(202,281),(202,155),(178,153)]}
DNAMES = list(DIST_PX)
CELLS = [[pm(*p) for p in DIST_PX[n]] for n in DNAMES]
# snap the Sarhad / Gangapol boundary to the real Amer Road (OSM), via the Hawa Mahal road corner
_C1 = pm(362, 170); _A0 = (816.25, 672.6); _AMER = [(830.0, 615.0), (838.75, 587.5)]
_gi = DNAMES.index("Gangapol"); _si = DNAMES.index("Sarhad · City Palace")
CELLS[_gi] = [_A0] + _AMER + [pm(*p) for p in DIST_PX["Gangapol"][2:]]
CELLS[_si] = [pm(178, 75)] + _AMER[::-1] + [_A0, _C1] + [pm(*p) for p in DIST_PX["Sarhad · City Palace"][3:]]
_gx = json.load(open("gates_extra.json")); L["zorawar"] = tuple(_gx["zorawar"]); L["gangapol"] = tuple(_gx["gangapol"])   # from the supplied gate map, georeferenced (±20–65 m)
DCEN = [(sum(p[0] for p in c) / len(c), sum(p[1] for p in c) / len(c)) for c in CELLS]
QUAD = [pm(37,395), pm(708,395), pm(708,283), pm(520,283), pm(520,55), pm(532,52), pm(532,22), pm(500,22), pm(445,75), pm(178,75), pm(165,153), pm(135,128), pm(75,165), pm(37,220)]
GXS = [p[0] for c in CELLS for p in c]; GYS = [p[1] for c in CELLS for p in c]
GC = ((min(GXS) + max(GXS)) / 2, (min(GYS) + max(GYS)) / 2); GW = (max(GXS) - min(GXS)) * 1.1

# ---------------- SVG world ----------------
S = []
S.append(f'<image href="assets/img/s2_z13.jpg" x="-1024" y="-1024" width="3584" height="3584" preserveAspectRatio="none"/>')
S.append(f'<image href="assets/img/s2_z14.jpg" x="0" y="0" width="1792" height="1536" preserveAspectRatio="none"/>')
S.append('<rect id="dim" x="-1024" y="-1024" width="3584" height="3584" style="fill:#0b0d10;opacity:0"/>')
bp = "".join(pd(b, True) for b in BLD if len(b) > 2)
S.append(f'<g id="city" style="opacity:0"><path id="bldp" d="{bp}" style="fill:#d9c9ae;fill-opacity:.82;stroke:#7d6b55;stroke-width:0.06"/>'
         + "".join(f'<path d="{pd(p)}" style="fill:none;stroke:#f2ead9;stroke-opacity:.55;stroke-width:{0.5 if t.get("highway") in ("residential","unclassified","living_street") else 1.3}"/>' for t, p in ROADS) + "</g>")
_bx = [float(v) for v in open("plan_overlay_box.txt").read().split()]
S.append(f'<image id="planimg" href="assets/img/plan_overlay.png" x="{_bx[0]:.1f}" y="{_bx[1]:.1f}" width="{_bx[2]:.1f}" height="{_bx[3]:.1f}" preserveAspectRatio="none" style="opacity:0"/>')
S.append(f'<path id="pink" d="{pd(QUAD, True)}" style="fill:#ff5fa2;fill-opacity:0;stroke:none"/>')
Y = "#FFE03A"
def ypath(i, pts, w=6, close=False, cls="dr", vw=None):
    w = w * (vw or WW * 1.08) / 1080
    return f'<path id="{i}" class="{cls}" pathLength="1" d="{pd(pts, close)}" style="fill:none;stroke:{Y};stroke-width:{w:.2f};stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1;filter:drop-shadow(0 0 3px rgba(0,0,0,.6))"/>'
_ax0, _ax1 = L["amer"], (WC[0], WC[1] - 40)
_amid = ((_ax0[0] + _ax1[0]) / 2 + 40, (_ax0[1] + _ax1[1]) / 2)
_u = 1500 / 1080
S.append(f'<circle id="amerzone" cx="{_ax0[0]:.1f}" cy="{_ax0[1]:.1f}" r="{60*_u:.1f}" style="fill:#FFE03A;fill-opacity:.25;stroke:#FFE03A;stroke-width:{5*_u:.1f};opacity:0"/>')
S.append(f'<path id="newzone" d="{pd(QUAD, True)}" style="fill:#FFE03A;fill-opacity:.28;stroke:#FFE03A;stroke-width:{6*_u:.1f};stroke-linejoin:round;opacity:0"/>')
S.append(f'<path id="amerhalo" d="M{_ax0[0]:.1f} {_ax0[1]:.1f} Q{_amid[0]:.1f} {_amid[1]:.1f} {_ax1[0]:.1f} {_ax1[1]:.1f}" style="fill:none;stroke:#000;stroke-opacity:.45;stroke-width:{26*_u:.1f};stroke-linecap:round;opacity:0"/>')
S.append(f'<path id="amerarrow" class="dr" pathLength="1" d="M{_ax0[0]:.1f} {_ax0[1]:.1f} Q{_amid[0]:.1f} {_amid[1]:.1f} {_ax1[0]:.1f} {_ax1[1]:.1f}" style="fill:none;stroke:#FFE03A;stroke-width:{16*_u:.1f};stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>')
S.append(f'<path id="amerflow" pathLength="1" d="M{_ax0[0]:.1f} {_ax0[1]:.1f} Q{_amid[0]:.1f} {_amid[1]:.1f} {_ax1[0]:.1f} {_ax1[1]:.1f}" style="fill:none;stroke:#1a1300;stroke-width:{7*_u:.1f};stroke-linecap:round;stroke-dasharray:0.03 0.07;opacity:0"/>')
_ang = math.degrees(math.atan2(_ax1[1] - _amid[1], _ax1[0] - _amid[0]))
S.append(f'<g id="amerhead" style="opacity:0" transform="translate({_ax1[0]:.1f} {_ax1[1]:.1f}) rotate({_ang:.1f})"><path d="M{8*_u:.1f} 0 L{-40*_u:.1f} {-28*_u:.1f} L{-40*_u:.1f} {28*_u:.1f} Z" style="fill:#FFE03A;stroke:#000;stroke-opacity:.5;stroke-width:{2*_u:.1f}"/></g>')
for k, c in enumerate(CELLS):
    S.append(f'<path id="cell{k}" d="{pd(c, True)}" style="fill:{Y};fill-opacity:0;stroke:{Y};stroke-width:5;vector-effect:non-scaling-stroke;opacity:0"/>')
for k, p in enumerate(EW): S.append(ypath(f"ew{k}", p, 9, vw=WW * 0.8))
for k, p in enumerate(NS): S.append(ypath(f"ns{k}", p, 9, vw=WW * 0.8))
for k, p in enumerate(WALL): S.append(ypath(f"wall{k}", p, 7, vw=WW * 1.15))
S.append(ypath("outline", QUAD, 9, close=True, vw=GW))
for k, p in enumerate(MIR): S.append(ypath(f"mi{k}", p, 7, vw=1550))
for k, p in enumerate(METRO): S.append(f'<path id="met{k}" class="dr" pathLength="1" d="{pd(p)}" style="fill:none;stroke:#ff4fa0;stroke-width:{7*2100/1080:.1f};stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>')
# ring road (from the earlier reel's OSM data, if present)
RING = []
for e in elems("/home/user/Infra360/video/jaipur-ajmer-road/project/osm/major_26.70_75.60.json"):
    t = e.get("tags", {})
    if t.get("ref") == "ORR" or "outer ring road" in (t.get("name") or "").lower(): RING.append(geom(e))
for k, p in enumerate(RING): S.append(f'<path id="ring{k}" class="dr" pathLength="1" d="{pd(p)}" style="fill:none;stroke:{Y};stroke-width:{6*2100/1080:.1f};stroke-dasharray:1;stroke-dashoffset:1"/>')
def disc(i, at, r, col=Y, fo=.55, sw=4):
    S.append(f'<circle id="{i}" cx="{at[0]:.1f}" cy="{at[1]:.1f}" r="{r}" style="fill:{col};fill-opacity:{fo};stroke:{col};stroke-width:{sw};vector-effect:non-scaling-stroke;opacity:0"/>')
for k in ("badi", "choti"): disc(k + "d", L[k], 9)
disc("palaced", L["palace"], 16, "#FFB000")
for k in ("cscheme", "malviya", "jawahar", "vidyadhar", "mansarovar"): disc(k + "d", L[k], 85, fo=.35, sw=7)
disc("hawad", L["hawa"], 6)
GATES = ("chandpole", "ajmeri", "sanganeri", "ghat", "surajpole", "gangapol", "zorawar", "newgate")
for g in GATES: disc(g + "gd", L[g], 5, "#FF5A5A")
# UNESCO World Heritage Site boundary, traced from the supplied georeferenced map (graticule: 75°49′ = x399, 75°51′ = x798; 26°56′ = y797, 26°55′ = y1005)
def wh(x, y): return ptc(26 + 55 / 60 - (y - 1076) / 226 / 60, 75 + 49 / 60 + (x - 406) / 202 / 60)   # calibrated: scale bar 122 px/km; Chand Pol, Sanganeri, Ghat Gate, Suraj Pol on the line
WHS = [wh(*p) for p in [(277,1018),(277,1038),(298,1040),(705,1133),(704,1141),(740,1152),(742,1138),(720,1128),(740,1028),(622,1004),(624,895),(642,893),(645,822),(676,824),(678,808),(622,800),(620,818),(522,804),(520,788),(556,782),(560,725),(528,738),(518,745),(470,770),(440,792),(400,812),(350,836),(322,858),(314,880),(310,893),(305,935),(298,940),(300,1018)]]
S[:] = [s if not s.startswith('<path id="pink"') else f'<path id="pink" d="{pd(WHS, True)}" style="fill:#ff5fa2;fill-opacity:0;stroke:none"/>' for s in S]
S.append(f'<path id="whs" class="dr" pathLength="1" d="{pd(WHS, True)}" style="fill:#E0312B;fill-opacity:0;stroke:#E0312B;stroke-width:{8 * GW * 1.02 / 1080:.2f};stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1"/>')

# ---------------- camera (viewBox) ----------------
AR = 1920 / 1080
def vb(c, w): return f"{c[0] - w / 2:.1f} {c[1] - w * AR / 2:.1f} {w:.1f} {w * AR:.1f}"
J, H = [], []
CAMS = []
def cam(t, c, w, d=1.6, ease="power2.inOut"):
    CAMS.append((t, c, w)); J.append(f'tl.to("#world", {{attr:{{viewBox:"{vb(c, w)}"}}, duration:{d}, ease:"{ease}"}}, {t:.2f});')
def view_at(t):
    v = CAMS[0]
    for c in CAMS:
        if c[0] <= t: v = c
    return v
def scr(p, t):
    _, c, w = view_at(t); s = 1080 / w
    return (540 + (p[0] - c[0]) * s, 960 + (p[1] - c[1]) * s)
def draw(sel, t, d=1.0): J.append(f'tl.fromTo("{sel}", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:{d}, ease:"power1.inOut"}}, {t:.2f});')
def on(sel, t, d=0.4, op=1): J.append(f'tl.to("{sel}", {{opacity:{op}, duration:{d}}}, {t:.2f});')
def label(i, p, text, t, until, dx=0, dy=-70, big=False, small=False):
    x, y = scr(p, t + 1.7)
    H.append(f'<div class="lab{" big" if big else ""}{" small" if small else ""}" id="{i}" style="left:{x + dx:.0f}px;top:{y + dy:.0f}px">{text}</div>')
    J.append(f'tl.fromTo("#{i}", {{opacity:0, y:10}}, {{opacity:1, y:0, duration:0.35}}, {t:.2f}); tl.to("#{i}", {{opacity:0, duration:0.25}}, {until:.2f});')
def photo(i, src, cap, credit, t, until, x=60, y=1090, w=460, h=330):
    H.append(f'<div class="ph" id="{i}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px"><img src="assets/img/{src}"/><div class="pc">{cap}<em>{credit}</em></div></div>')
    J.append(f'tl.fromTo("#{i}", {{opacity:0, scale:0.7}}, {{opacity:1, scale:1, duration:0.4, ease:"back.out(1.6)"}}, {t:.2f}); tl.to("#{i}", {{opacity:0, scale:0.9, duration:0.3}}, {until:.2f});')
def chip(i, kick, text, t, until, y=300):
    H.append(f'<div class="chip" id="{i}" style="top:{y}px"><b>{kick}</b>{text}</div>')
    J.append(f'tl.fromTo("#{i}", {{opacity:0, y:-14}}, {{opacity:1, y:0, duration:0.4}}, {t:.2f}); tl.to("#{i}", {{opacity:0, duration:0.3}}, {until:.2f});')

T = {k: cue(*v) for k, v in {
    "designed": ("jaipur", "was", "designed"), "in1727": ("in", "1727"), "amer": ("amer",), "gave": ("and", "he", "gave"), "vidyadhar": ("vidyadhar", "bhattacharya"),
    "vastu": ("vidyadhar", "used"), "nine": ("nine",), "each": ("each", "block"), "palace": ("the", "palace"), "roads": ("then", "the", "roads"),
    "three": ("three", "wide"), "crossed": ("crossed",), "meet": ("where", "they", "meet"), "badi": ("badi",), "choti": ("choti",), "water": ("water",),
    "wall": ("all", "of", "it"), "seven": ("seven",), "y1876": ("and", "in", "1876"), "pink": ("pink", "to"), "pinkcity": ("pink", "city"),
    "unesco": ("in", "2019"), "didnt": ("and", "the", "planning", "didnt"), "cscheme": ("cscheme",), "malviya": ("then", "malviya"), "jawahar": ("jawahar",),
    "vidnagar": ("and", "vidyadhar", "nagar"), "named": ("named",), "mansarovar": ("then", "mansarovar"), "today": ("and", "today"), "ring": ("ring", "road"),
    "metro": ("metro",), "later": ("300", "years", "later"), "send": ("send", "this")}.items()}
# face slots (your recording shows through): opening line, closing CTA
FACE = [(0.0, T["designed"] - 0.05), (T["send"] - 0.15, END)]

# 0 · opening: face, then the walled city from above with the grid drawing
cam(0, WC, WW * 1.6, 0.01)
J.append(f'tl.fromTo("#world", {{attr:{{viewBox:"{vb(WC, WW * 1.6)}"}}}}, {{attr:{{viewBox:"{vb(GC, GW)}"}}, duration:{T["in1727"] - T["designed"]:.2f}, ease:"power1.out"}}, {T["designed"]:.2f});')
on("#city", T["designed"] + 0.2, 0.8, 0.9)
for k in range(len(CELLS)): J.append(f'tl.to("#cell{k}", {{opacity:1, duration:0.2}}, {T["designed"] + 0.35 + 0.11 * k:.2f});')
J.append(f'tl.to("[id^=cell]", {{opacity:0, duration:0.4}}, {T["in1727"] - 0.3:.2f});')
# 1 · 1727: wide view Amer → plains
mid = ((L["amer"][0] + WC[0]) / 2, (L["amer"][1] + WC[1]) / 2)
cam(T["in1727"] - 0.2, mid, 1500, 1.6)
on("#city", T["in1727"] - 0.2, 0.6, 0)
label("lyear", (mid[0] - 420, mid[1] - 470), "1727", T["in1727"] + 0.2, T["vastu"] - 0.2, big=True)
label("lamer", L["amer"], "FROM · Amer Fort", T["amer"] - 0.3, T["vastu"] - 0.2, dx=60, dy=-30)
J.append(f'tl.fromTo("#amerzone", {{opacity:0, attr:{{r:10}}}}, {{opacity:1, attr:{{r:{60*_u:.1f}}}, duration:0.5, ease:"back.out(2)"}}, {T["amer"] - 0.3:.2f}); tl.to("#amerzone", {{fillOpacity:0.5, duration:0.4, yoyo:true, repeat:5, immediateRender:false}}, {T["amer"] + 0.2:.2f});')
J.append(f'tl.to("#amerhalo", {{opacity:1, duration:0.3}}, {T["amer"] + 0.2:.2f});')
draw("#amerarrow", T["amer"] + 0.2, 1.3)
J.append(f'tl.to("#amerhead", {{opacity:1, duration:0.25}}, {T["amer"] + 1.4:.2f}); tl.to("#amerflow", {{opacity:0.8, duration:0.3}}, {T["amer"] + 1.5:.2f});')
J.append(f'tl.fromTo("#amerflow", {{strokeDashoffset:0}}, {{strokeDashoffset:-1, duration:1.2, ease:"none", repeat:4}}, {T["amer"] + 1.5:.2f});')
J.append(f'tl.fromTo("#newzone", {{opacity:0}}, {{opacity:1, duration:0.5}}, {T["amer"] + 1.4:.2f}); tl.to("#newzone", {{fillOpacity:0.5, duration:0.4, yoyo:true, repeat:5, immediateRender:false}}, {T["amer"] + 1.9:.2f});')
J.append(f'tl.to(["#amerarrow", "#amerhead", "#amerflow", "#amerhalo", "#amerzone", "#newzone"], {{opacity:0, duration:0.4}}, {T["vastu"] - 0.2:.2f});')
label("lnew", (_ax1[0], _ax1[1] + 60), "TO · new capital Jaipur", T["amer"] + 1.4, T["vastu"] - 0.2, dx=-180, dy=40)
photo("poldplan", "oldplan.jpg", "The original plan", "Image supplied", T["designed"] + 0.3, T["in1727"] - 0.2, x=60, y=1080, w=600, h=350)
photo("pjai", "jaisingh.jpg", "Sawai Jai Singh II", "c. 1725 · British Museum · public domain", T["in1727"] + 0.6, T["amer"] - 0.1, x=560, w=400, h=380, y=1060)
photo("pamer", "amer.jpg", "Amer Fort · the old capital", "A.Savin · FAL", T["amer"], T["vidyadhar"] - 0.4, x=600, y=280, w=420, h=280)
photo("paer", "aerial_jaipur.jpg", "His city, from above", "Image supplied", T["vidyadhar"] - 0.2, T["vastu"] + 0.3, x=600, y=430, w=420, h=500)
chip("cvid", "THE ARCHITECT", "Vidyadhar Bhattacharya · from Bengal", T["vidyadhar"] - 0.3, T["vastu"] - 0.2, y=300)
chip("cking", "THE VISIONARY", "Maharaja Sawai Jai Singh II", T["in1727"] + 0.5, T["gave"] - 0.1, y=300)
# 2 · the nine-square grid over the real city
cam(T["vastu"] - 0.1, GC, GW, 1.4)
on("#city", T["vastu"], 0.7, 0.95); on("#dim", T["vastu"], 0.7, 0.25)
for k in range(len(CELLS)):
    J.append(f'tl.fromTo("#cell{k}", {{opacity:0, fillOpacity:0}}, {{opacity:1, fillOpacity:0.16, duration:0.3}}, {T["each"] + 0.28 * k:.2f});')
    OFFS = {"Purani Basti": (0, 0), "Topkhana Desh": (0, 10), "Modikhana": (0, -50), "Visheshraji": (0, 40), "Ghat": (0, 0), "Topkhana Hazuri": (-30, 0), "Ramchandraji": (0, 0), "Gangapol": (0, 0), "Sarhad · City Palace": (-40, -40)}
    ox, oy = OFFS[DNAMES[k]]
    label(f"ld{k}", DCEN[k], DNAMES[k], T["each"] + 0.28 * k, T["roads"], dx=ox - len(DNAMES[k]) * 7.5, dy=oy - 16, small=True)
J.append(f'tl.to("#planimg", {{opacity:0.9, duration:0.6}}, {T["nine"]:.2f}); tl.to("#planimg", {{opacity:0, duration:0.5}}, {T["each"] + 0.2:.2f});')
PCELL = DNAMES.index("Sarhad · City Palace") if True else min(range(9), key=lambda k: math.hypot(sum(p[0] for p in CELLS[k]) / 4 - L["palace"][0], sum(p[1] for p in CELLS[k]) / 4 - L["palace"][1]))
J.append(f'tl.to("#cell{PCELL}", {{fillOpacity:0.45, duration:0.4}}, {T["palace"]:.2f});')
on("#palaced", T["palace"], 0.4)
chip("cvastu", "VASTU SHASTRA · THE CHOWKRIS", "Nine squares · like a mandala", T["nine"] - 0.2, T["each"] - 0.1, y=300)
label("lpal", L["palace"], "City Palace", T["palace"] + 0.1, T["roads"], dx=-140, dy=10, big=True)
photo("pold", "oldpalace.jpg", "Jaipur in the 1800s", "Bourne &amp; Shepherd · public domain", T["each"], T["palace"] - 0.1, x=560, y=300, w=440, h=300)
photo("ppal", "citypalace.jpg", "City Palace · Chandra Mahal", "Jakub Hałun · CC BY-SA 4.0", T["palace"], T["roads"] - 0.1, x=60, y=300, w=440, h=300)
J.append(f'tl.to("[id^=cell]", {{opacity:0, duration:0.4}}, {T["roads"]:.2f}); tl.to("#palaced", {{opacity:0, duration:0.3}}, {T["roads"]:.2f});')
# 3 · streets and chaupars
for k in range(len(EW)): draw(f"#ew{k}", T["three"] + 0.05 * k, 1.4)
for k in range(len(NS)): draw(f"#ns{k}", T["crossed"] + 0.06 * k, 1.2)
cam(T["meet"] - 0.1, ((L["badi"][0] + L["choti"][0]) / 2, (L["badi"][1] + L["choti"][1]) / 2 - 45), WW * 0.62, 1.3)
for k in ("badi", "choti"):
    on(f"#{k}d", T[k]); J.append(f'tl.fromTo("#{k}d", {{attr:{{r:6}}}}, {{attr:{{r:18}}, duration:0.5, yoyo:true, repeat:3}}, {T[k]:.2f});')
label("lbadi", L["badi"], "Badi Chaupar", T["badi"], T["wall"] - 0.2, dx=-60, dy=60)
label("lchoti", L["choti"], "Choti Chaupar", T["choti"], T["wall"] - 0.2, dx=-80, dy=60)
photo("pchoti", "choti_aerial.jpg", "Choti Chaupar from above", "Image supplied", T["choti"] - 0.3, T["wall"] - 0.1, x=60, y=280, w=360, h=450)
photo("pbadi", "badi_supplied.jpg", "Badi Chaupar today", "Image supplied", T["badi"], T["water"] - 0.2, x=450, y=280, w=570, h=380)
photo("phawa", "hawa.jpg", "Hawa Mahal · beside Badi Chaupar", "Marcin Białek · CC BY-SA 4.0", T["water"] - 0.2, T["wall"] - 0.1, x=450, y=280, w=570, h=380)
# 4 · walls, gates, pink
cam(T["wall"] - 0.1, GC, GW * 1.02, 1.2)
J.append(f'tl.to("[id^=badi], [id^=choti]", {{opacity:0, duration:0.3}}, {T["wall"]:.2f});')
# (hill-fort wall pieces from OSM are not drawn; the walled-city outline is used instead)
draw("#outline", T["wall"] + 0.1, 2.2); J.append(f'tl.to("#outline", {{opacity:0, duration:0.4}}, {T["didnt"]:.2f});')
for k, (g, nm) in enumerate([("chandpole", "Chand Pol"), ("ajmeri", "Kishan Pol · Ajmeri"), ("sanganeri", "Shiv Pol · Sanganeri"), ("ghat", "Ghat Gate"), ("surajpole", "Suraj Pol"),
                             ("gangapol", "Ganga Pol"), ("zorawar", "Dhruv Pol · Zorawar Singh"), ("newgate", "New Gate · added later")]):
    label(f"lg{k}", L[g], nm, T["seven"] + 0.18 * k, T["unesco"] - 0.2, dx=-150 if g == "newgate" else -60, dy=60 if g == "newgate" else (-70 if k % 2 else 20), small=True)
for k, g in enumerate(GATES):
    J.append(f'tl.fromTo("#{g}gd", {{opacity:0, attr:{{r:2}}}}, {{opacity:1, attr:{{r:12}}, duration:0.4, ease:"back.out(2)"}}, {T["seven"] + 0.18 * k:.2f}); tl.to("#{g}gd", {{opacity:0, duration:0.3}}, {T["didnt"]:.2f});')
J.append(f'tl.fromTo("#whs", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:1.6, ease:"power1.inOut"}}, {T["unesco"] + 0.2:.2f}); tl.to("#whs", {{fillOpacity:0.18, duration:0.5}}, {T["unesco"] + 1.8:.2f}); tl.to("#whs", {{opacity:0, duration:0.4}}, {T["didnt"]:.2f});')
J.append(f'tl.to("#pink", {{fillOpacity:0.42, duration:1.2}}, {T["pink"]:.2f}); tl.to("#bldp", {{fill:"#f1a6bd", duration:1.2}}, {T["pink"]:.2f});')
photo("pgate", "chandpole.jpg", "Chandpole Gate", "Ameer P F · CC BY-SA 4.0", T["seven"] + 0.2, T["y1876"] - 0.1, x=580, y=320, w=420, h=300)
photo("ppink", "patrika.jpg", "The Pink City", "Patrika Gate · Iloveplantsforever · CC0", T["pinkcity"] - 0.3, T["unesco"] - 0.1, x=60)
photo("pjm", "jantar.jpg", "Jantar Mantar · also UNESCO-listed", "Jakub Hałun · CC BY-SA 4.0", T["unesco"] + 0.3, T["didnt"] - 0.1, x=60, y=1100, w=420, h=300)
chip("c1876", "1876", "Painted pink to welcome the Prince of Wales", T["y1876"] + 0.2, T["unesco"] - 0.2, y=300)
# 5 · UNESCO
chip("cun", "UNESCO WORLD HERITAGE · 2019", "The red line: the protected walled city", T["unesco"], T["didnt"] - 0.1, y=300)
J.append(f'tl.fromTo("#pink", {{fillOpacity:0.42}}, {{fillOpacity:0.65, duration:0.5, yoyo:true, repeat:3, immediateRender:false}}, {T["unesco"] + 0.3:.2f});')
# 6 · the city kept planning
CW = (WC[0] - 160, WC[1] + 260)
cam(T["didnt"] - 0.1, CW, 1550, 1.8)
on("#city", T["didnt"] + 0.4, 0.6, 0.5); on("#dim", T["didnt"], 0.6, 0.15)
for k in range(len(MIR)): draw(f"#mi{k}", T["cscheme"] + 0.1, 1.0)
for key, tk, text, dec in [("cscheme", "cscheme", "C-Scheme · MI Road", "1940s"), ("malviya", "malviya", "Malviya Nagar", ""), ("jawahar", "jawahar", "Jawahar Nagar", ""),
                           ("vidyadhar", "vidnagar", "Vidyadhar Nagar", "named after the architect"), ("mansarovar", "mansarovar", "Mansarovar", "")]:
    on(f"#{key}d", T[tk]); J.append(f'tl.fromTo("#{key}d", {{attr:{{r:20}}}}, {{attr:{{r:85}}, duration:0.6, ease:"back.out(1.6)"}}, {T[tk]:.2f}); tl.to("#{key}d", {{attr:{{r:72}}, duration:0.7, ease:"sine.inOut", repeat:3, yoyo:true}}, {T[tk]+0.6:.2f});')
    label(f"l{key}", L[key], text + (f"<em>{dec}</em>" if dec else ""), T[tk] + 0.05, T["later"] - 0.2, dx=-90, dy=-150)
for k in range(len(RING)): draw(f"#ring{k}", T["ring"], 1.6)
for k in range(len(METRO)): draw(f"#met{k}", T["metro"], 1.2)
label("lring", (CW[0] + 120, CW[1] + 640), "Ring Road", T["ring"] + 0.3, T["send"] - 0.2, dx=0, dy=0)
label("lmet", L["mansarovar"], "Metro · Pink Line", T["metro"] + 0.2, T["send"] - 0.2, dx=40, dy=40)
photo("pmet", "metro.jpg", "Jaipur Metro · Badi Chaupar station", "Sam2905 · CC BY-SA 4.0", T["metro"], T["later"] + 1.5, x=560)
cam(T["later"] - 0.1, (CW[0], CW[1] - 80), 2100, 2.6, "power1.inOut")
chip("cplan", "300 YEARS LATER", "Still growing on a plan", T["later"], T["send"] - 0.2, y=300)

# face slots + map layer visibility
for a, b in FACE:
    J.append(f'tl.set("#maplayer", {{opacity:0}}, {a:.2f});')
    if b < END: J.append(f'tl.to("#maplayer", {{opacity:1, duration:0.35}}, {b:.2f});')
H.append('<div id="share"><svg viewBox="0 0 24 24" width="78" height="78"><path d="M3 11l18-8-8 18-2-8z" style="fill:none;stroke:#fff;stroke-width:2;stroke-linejoin:round"/></svg><span>Send to a Jaipur lover</span></div>')
J.append(f'tl.fromTo("#share", {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.4, ease:"back.out(2)"}}, {T["send"] + 0.2:.2f}); tl.fromTo("#share svg", {{scale:1}}, {{scale:1.18, duration:0.45, yoyo:true, repeat:5}}, {T["send"] + 0.7:.2f});')
H.append('<div id="hook"><b>JAIPUR WAS DESIGNED</b><span>— in 1727 —</span></div>')
J.append(f'tl.set("#hook", {{opacity:1}}, 0); tl.to("#hook", {{opacity:0, duration:0.3}}, {T["in1727"] - 0.3:.2f});')
H.append('<div id="credit">Satellite: Sentinel-2 cloudless 2016 by EOX (CC BY 4.0) · Map data © OpenStreetMap · plan: supplied diagram fitted to OSM streets</div>')
J.append(f'tl.set("#credit", {{opacity:0}}, 0); tl.to("#credit", {{opacity:1, duration:0.3}}, {T["designed"]:.2f}); tl.to("#credit", {{opacity:0, duration:0.3}}, {T["send"] - 0.3:.2f});')

# captions (architect style: big white bold, heavy shadow)
cap_html = "".join(f'<div class="cp" id="cp{gi}">' + " ".join(f'<span class="{"em" if w["t"].lower() in EM else ""}">{w["t"]}</span>' for w in g) + '</div>' for gi, (a, b, g) in enumerate(caps))
for gi, (a, b, g) in enumerate(caps):
    J.append(f'tl.fromTo("#cp{gi}", {{opacity:0, scale:0.92}}, {{opacity:1, scale:1, duration:0.12}}, {a}); tl.to("#cp{gi}", {{opacity:0, duration:0.06}}, {b - 0.06:.2f});')

face = ('<video id="avatar" class="clip" src="assets/avatar.mp4" data-start="0" data-duration="%s" data-track-index="0" playsinline data-has-audio="true" data-volume="1"></video>' % END
        if os.path.exists(f"{P}/assets/avatar.mp4") else '<div id="facePH"><div>🎥</div><b>YOUR VIDEO</b><span>Ashwil on camera — drops in here</span></div>')
CSS = """*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#0b0d10}
#root{position:relative;width:1080px;height:1920px;overflow:hidden}#avatar{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover}
#facePH{position:absolute;inset:0;background:radial-gradient(80% 60% at 50% 40%,#2a3442,#0b0d10);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;font-family:Inter,Arial,sans-serif;color:#9fb0c4}
#facePH div{font-size:120px}#facePH b{font-size:56px;color:#fff;letter-spacing:.08em}#facePH span{font-size:32px}
#maplayer{position:absolute;inset:0}#world{position:absolute;inset:0;width:1080px;height:1920px}
.lab{position:absolute;opacity:0;font-family:Inter,Arial,sans-serif;font-weight:900;font-size:40px;color:#fff;white-space:nowrap;text-shadow:0 3px 0 #000,0 0 16px rgba(0,0,0,.9)}
.lab.small{font-size:28px}.lab.big{font-size:64px;color:#FFE03A}.lab em{display:block;font-style:normal;font-weight:700;font-size:28px;color:#FFE03A}
.ph{position:absolute;opacity:0;border-radius:18px;overflow:hidden;border:4px solid #FFE03A;box-shadow:0 14px 40px rgba(0,0,0,.6);background:#111}
.ph img{width:100%;height:100%;object-fit:cover}.pc{position:absolute;left:0;right:0;bottom:0;padding:28px 14px 8px;background:linear-gradient(180deg,transparent,rgba(0,0,0,.85));font:800 30px Inter,Arial,sans-serif;color:#fff}
.pc em{display:block;font-style:normal;font-weight:600;font-size:20px;color:#ddd}
.chip{position:absolute;left:60px;right:60px;opacity:0;padding:18px 26px;border-radius:18px;background:rgba(10,12,16,.82);border-left:8px solid #FFE03A;font:800 40px/1.15 Inter,Arial,sans-serif;color:#fff}
.chip b{display:block;font:700 24px "JetBrains Mono",monospace;letter-spacing:.16em;color:#FFE03A;margin-bottom:6px}
#hook{position:absolute;left:0;right:0;top:230px;text-align:center;opacity:0;font-family:Inter,Arial,sans-serif;text-shadow:0 4px 0 #000,0 0 24px rgba(0,0,0,.9)}
#hook b{display:block;font-weight:900;font-size:92px;color:#fff;line-height:1}#hook span{display:block;margin-top:10px;font-weight:900;font-size:60px;color:#FFE03A}
.cp{position:absolute;left:60px;right:60px;top:1500px;text-align:center;opacity:0;font:900 72px/1.08 Inter,Arial,sans-serif;color:#fff;text-shadow:0 4px 0 #000,0 0 18px rgba(0,0,0,.95),0 0 4px #000}
.cp .em{color:#FFE03A}
#share{position:absolute;left:0;right:0;top:1180px;display:flex;flex-direction:column;align-items:center;gap:10px;opacity:0;font:900 40px Inter,Arial,sans-serif;color:#fff;text-shadow:0 3px 0 #000}
#share svg{background:#FFB000;border-radius:50%;padding:14px;box-shadow:0 0 0 10px rgba(255,176,0,.3)}
#credit{position:absolute;left:40px;right:40px;bottom:120px;text-align:center;font:500 20px "JetBrains Mono",monospace;color:rgba(255,255,255,.75);text-shadow:0 1px 3px #000}"""
fonts = '<style>@font-face{font-family:"Instrument Serif";src:url(assets/fonts/instrument-serif-latin-400-normal.woff2)}</style>'
open(f"{P}/index.html", "w").write(f"""<!doctype html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script>{fonts}<style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="30">
{face}
<div id="maplayer"><svg id="world" viewBox="{vb(WC, WW * 1.6)}" preserveAspectRatio="xMidYMid slice">{"".join(S)}</svg>{"".join(H)}</div>
{cap_html}
<audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="{0.2 if os.path.exists(P + '/assets/avatar.mp4') else 0.55}" data-fade-in="1.0" data-fade-out="2.0"></audio>
</div><script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(J)}
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>""")
print("END", END, "estimated" if ESTIMATED else "real", "| caps", len(caps), "| bld", len(BLD), "roads", len(ROADS), "wall", len(WALL), "EW", len(EW), "NS", len(NS), "MI", len(MIR), "ring", len(RING), "metro", len(METRO))
print({k: round(v, 1) for k, v in T.items()})
