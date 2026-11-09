"""Jaipur Expansion reel (Digital Banjaaraa), synced to the Hinglish voice. World = z11 web-mercator px from tile (1450, 860)."""
import json, math, random
P = "proj"
PH = json.load(open("rec/phrases.json"))
def S(k): return PH[k]["s"]
def E(k): return PH[k]["e"]
def wt(k, word):
    """estimated time a word is spoken inside phrase k (char-proportional)."""
    t = PH[k]["t"]; i = t.lower().find(word.lower())
    return S(k) + (E(k) - S(k)) * max(0, i) / len(t)
END = round(E(33) + 1.0, 2)
def wp(lat, lon):
    n = 256 * 2 ** 11
    return ((lon + 180) / 360 * n - 1450 * 256, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n - 860 * 256)
PXKM = 256 * 2 ** 11 / 40075 / math.cos(math.radians(26.9))
CEN = wp(26.91, 75.81)
SVG, H, J, SFX = [], [], [], []
def vb(c, w): h = w * 1920 / 1080; return f"{c[0] - w / 2:.1f} {c[1] - h / 2:.1f} {w:.1f} {h:.1f}"
CAMS = []
def cam(t, c, w, d=1.0, ease="power2.inOut"):
    J.append(f'tl.to("#world", {{attr:{{viewBox:"{vb(c, w)}"}}, duration:{d}, ease:"{ease}"}}, {t:.2f});'); CAMS.append((t, d, c, w))
def scr(p, t):
    c, w = CAMS[0][2], CAMS[0][3]
    for t0, d, c1, w1 in sorted(CAMS, key=lambda q: q[0]):
        if t0 + d <= t + 1e-6: c, w = c1, w1
    h = w * 1920 / 1080
    return ((p[0] - (c[0] - w / 2)) / w * 1080, (p[1] - (c[1] - h / 2)) / h * 1920)
def camw(t):
    w = CAMS[0][3]
    for t0, d, c1, w1 in sorted(CAMS, key=lambda q: q[0]):
        if t0 + d <= t + 1e-6: w = w1
    return w
def sfx(n, t, v=.3): SFX.append(f'<audio id="sx{len(SFX)}" class="clip" src="assets/sfx/{n}.mp3" data-start="{t:.2f}" data-duration="2" data-track-index="{20 + len(SFX)}" data-volume="{v}"></audio>')
def pd(pts, close=False): return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + (" Z" if close else "")
def inout(sel, t, until, frm="opacity:0, scale:.6", to="opacity:1, scale:1", d=.28, ease="back.out(2)"):
    J.append(f'tl.fromTo("{sel}", {{{frm}}}, {{{to}, duration:{d}, ease:"{ease}"}}, {t:.2f}); tl.to("{sel}", {{opacity:0, duration:.2}}, {until - .2:.2f});')
def label(i, p, text, t, until, at=None, cls="", dx=0, dy=0):
    x, y = scr(p, at if at is not None else t)
    x = min(max(x + dx, 120), 900)
    H.append(f'<div class="lab {cls}" id="{i}" style="left:{x:.0f}px;top:{y + dy:.0f}px">{text}</div>'); inout(f"#{i}", t, until)
def pin(i, p, col, t, until, r=6):
    SVG.append(f'<g id="{i}" style="opacity:0"><circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{r * 2.4:.1f}" style="fill:{col};opacity:.3"/><circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{r:.1f}" style="fill:{col};stroke:#fff;stroke-width:{r / 3:.1f}"/></g>')
    J.append(f'tl.to("#{i}", {{opacity:1, duration:.2}}, {t:.2f}); tl.to("#{i}", {{opacity:0, duration:.3}}, {until:.2f});')
GOLD, RED, PINK, GREEN, CYAN, BLUE, YEL = "#FFC42E", "#FF3246", "#FF50AA", "#3CFF96", "#3CDCFF", "#50A0FF", "#FFE03A"

# ---------------- base ----------------
SVG.append('<rect x="-20000" y="-20000" width="45000" height="45000" style="fill:#080a0f"/>')
SVG.append('<image href="assets/img/r10.jpg" x="-1024" y="-1536" width="5120" height="5632" preserveAspectRatio="none"/>')
SVG.append('<image href="assets/img/r11.webp" x="0" y="0" width="2560" height="2560" preserveAspectRatio="none"/>')
SVG.append('<image id="city" href="assets/img/c13.webp" x="1088" y="1024" width="448" height="576" preserveAspectRatio="none" style="opacity:0"/>')
SVG.append('<rect id="dim" x="-20000" y="-20000" width="45000" height="45000" style="fill:#000;opacity:.2"/>')

# ---------------- data: highways ----------------
NH = json.load(open("data/nh_jaipur.json"))
def bearing(p): return math.degrees(math.atan2(-(p[1] - CEN[1]), p[0] - CEN[0]))  # 0=east, 90=north
ROADS = {k: [] for k in ["delhi", "sikar", "ajmer", "tonk", "agra", "ring", "bypass"]}
for f in NH:
    nm = (f["name"] or "").strip()
    for L in f["lines"]:
        pts = [wp(la, lo) for lo, la in L]
        mx = sum(p[0] for p in pts) / len(pts); my = sum(p[1] for p in pts) / len(pts)
        dist = math.hypot(mx - CEN[0], my - CEN[1]) / PXKM
        if dist > 75: continue
        b = bearing((mx, my))
        if nm == "NH 148C": ROADS["ring"].append(pts)
        elif nm == "NH 48,  NH 52": ROADS["bypass"].append(pts)
        elif nm == "NH 48" and 10 <= b <= 100: ROADS["delhi"].append(pts)
        elif nm == "NH 48" and (b > 150 or b < -140): ROADS["ajmer"].append(pts)
        elif nm == "NH 52" and 95 <= b <= 170: ROADS["sikar"].append(pts)
        elif nm == "NH 52" and -110 <= b <= -40: ROADS["tonk"].append(pts)
        elif nm == "NH 21" and -40 <= b <= 40: ROADS["agra"].append(pts)
def smooth(pts, n=10):
    out = []; P_ = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = P_[i - 1], P_[i], P_[i + 1], P_[i + 2]
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(tuple(.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    return out + [pts[-1]]
WPT = {"kalwar": [(26.948, 75.760), (26.975, 75.66), (26.972, 75.50), (26.972, 75.388)],
       "sirsi": [(26.928, 75.735), (26.948, 75.680), (26.962, 75.620), (26.975, 75.560)],
       "diggi": [(26.826, 75.790), (26.76, 75.735), (26.66, 75.65), (26.570, 75.563)]}
for k, v in WPT.items(): ROADS[k] = [smooth([wp(*p) for p in v])]
ORDER = [("delhi", "DELHI ROAD", (27.12, 76.02)), ("sikar", "SIKAR ROAD", (27.15, 75.70)), ("kalwar", "KALWAR ROAD", (27.02, 75.40)),
         ("sirsi", "SIRSI ROAD", (26.93, 75.55)), ("ajmer", "AJMER ROAD", (26.80, 75.50)), ("diggi", "DIGGI ROAD", (26.60, 75.58)),
         ("tonk", "TONK ROAD", (26.55, 75.92)), ("agra", "AGRA ROAD", (26.93, 76.10))]
for k, segs in ROADS.items():
    col = GREEN if k == "ring" else GOLD
    wdt = 3.2 if k not in ("bypass",) else 2
    for j, pts in enumerate(segs):
        dd = pd(pts)
        SVG.append(f'<path class="r_{k}" d="{dd}" pathLength="1" style="fill:none;stroke:{col};stroke-width:{wdt * 3:.1f};stroke-opacity:.28;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>')
        SVG.append(f'<path class="r_{k}" d="{dd}" pathLength="1" style="fill:none;stroke:{col};stroke-width:{wdt:.1f};stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>')
def draw(k, t, d=.6): J.append(f'tl.to(".r_{k}", {{strokeDashoffset:0, duration:{d}, ease:"power2.out"}}, {t:.2f});')
def road_op(t, op, d=.4, ks=None):
    for k in (ks or ROADS): J.append(f'tl.to(".r_{k}", {{opacity:{op}, duration:{d}}}, {t:.2f});')

# municipal boundary
B = json.load(open("data/jaipur_boundary.geojson"))["features"][0]["geometry"]["coordinates"][0]
BND = [wp(la, lo) for lo, la in B[::3]]
SVG.append(f'<path id="bfill" d="{pd(BND, True)}" style="fill:{RED};fill-opacity:.0;stroke:none"/>')
SVG.append(f'<path id="bnd" d="{pd(BND, True)}" pathLength="1" style="fill:none;stroke:{RED};stroke-width:3;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1"/>')
SVG.append(f'<path id="bndg" d="{pd(BND, True)}" style="fill:none;stroke:{RED};stroke-width:10;stroke-opacity:.35;opacity:0"/>')

# ---------------- 0 · hook ----------------
REG_W = 150 * PXKM; CITY_W = 34 * PXKM
J.append(f'tl.set("#world", {{attr:{{viewBox:"{vb(CEN, CITY_W * 1.6)}"}}}}, 0);'); CAMS.append((0, 0, CEN, CITY_W * 1.6))
H.append('<video id="face" class="clip" src="assets/face.mp4" data-start="0" data-duration="2.0" data-track-index="2" muted playsinline></video>')
J.append('tl.set("#face", {opacity:1}, 0); tl.to("#face", {opacity:0, scale:1.06, duration:.18}, 1.6);')
cam(1.6, CEN, CITY_W * 1.15, 1.6, "power2.out")
J.append('tl.to("#bnd", {strokeDashoffset:0, duration:1.3, ease:"power2.inOut"}, 1.65); tl.to("#bfill", {fillOpacity:.12, duration:.6}, 2.6); tl.to("#bndg", {opacity:1, duration:.4}, 2.6);')
H.append('<div id="title"><span>JAIPUR</span><b>REAL ESTATE</b><i>STRUCTURE SAMJHO</i></div>')
J.append(f'tl.fromTo("#title span", {{opacity:0, scale:2}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, 1.7); tl.fromTo("#title b", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.3}}, 1.95);'
         f'tl.fromTo("#title i", {{opacity:0, scale:1.6}}, {{opacity:1, scale:1, duration:.25, ease:"back.out(2)"}}, {wt(0, "structure"):.2f}); tl.to("#title", {{opacity:0, duration:.25}}, {S(1) - .1:.2f});')
sfx("impact-bass-1", 1.6, .45); sfx("whoosh", 1.55, .3)
def chap(i, num, name, t, until):
    H.append(f'<div class="chap" id="ch{i}"><b>{num}</b>{name}</div>'); inout(f"#ch{i}", t, until, frm="opacity:0, x:-60", to="opacity:1, x:0", ease="power3.out")
    J.append(f'tl.fromTo("#flash", {{opacity:.55}}, {{opacity:0, duration:.3, immediateRender:false}}, {t:.2f});'); sfx("whoosh-short", t, .35)

# ---------------- 1 · roads ----------------
chap(1, "01", "ROADS", S(1), S(5))
cam(S(1), CEN, REG_W, 1.4)
H.append('<div class="big" id="hw8"><b>8</b>HIGHWAYS</div>'); inout("#hw8", wt(1, "highways"), S(2) + .3)
for i, (k, nm, lp) in enumerate(ORDER):
    ph = 2 if k in ("delhi", "sikar") else 3
    w = {"delhi": "Delhi", "sikar": "Sikar", "kalwar": "Kalwar", "sirsi": "Sirsi", "ajmer": "Ajmer", "diggi": "Diggi", "tonk": "Tonk", "agra": "Agra"}[k]
    t = wt(ph, w) - .05
    draw(k, t, .7)
    H.append(f'<div class="rl" id="rl{i}"><b>{i + 1}</b>{nm}</div>')
    x, y = scr(wp(*lp), S(1) + 1.5); x = min(max(x, 150), 880)
    J.append(f'tl.set("#rl{i}", {{left:{x:.0f}, top:{y:.0f}}}, 0);')
    inout(f"#rl{i}", t + .1, S(5) + .2)
    sfx("pop", t + .1, .25)
draw("bypass", S(4), .8)
draw("ring", S(4) + .1, 1.4)
H.append('<div class="lab ring" id="lring">RING ROAD</div>')
x, y = scr(wp(26.78, 75.74), S(1) + 1.5); J.append(f'tl.set("#lring", {{left:{x:.0f}, top:{y:.0f}}}, 0);'); inout("#lring", wt(4, "Ring"), S(5) + .2)
sfx("riser", S(4), .2)

# ---------------- 2 · central jaipur ----------------
chap(2, "02", "CENTRAL JAIPUR", S(5), S(10))
CORE_C = wp(26.906, 75.812); cam(S(5), CORE_C, CITY_W * .6, 1.2)
cam(S(8) + 1.2, CEN, CITY_W, 1.0)
J.append(f'tl.to("#city", {{opacity:1, duration:.8}}, {S(5) + .2:.2f}); tl.to("#bfill", {{fillOpacity:.06, duration:.5}}, {S(5):.2f});')
road_op(S(5), .45)
COFF = {'Pink City': (60, -50), 'C-Scheme': (-20, -50), 'Civil Lines': (-110, 20), 'Bani Park': (-40, -50), 'Raja Park': (80, 40), 'Jawahar Nagar': (110, 95), 'Lal Kothi': (-60, 60)}
HOFF = {'Vaishali Nagar': (-30, -42), 'Shyam Nagar': (-70, 42), 'Mansarovar': (-20, 42), 'Vidhyadhar Nagar': (60, -42), 'Murlipura': (-80, -42), 'Jagatpura': (30, 42)}
CORE = [("Pink City", (26.924, 75.824), 6, "Pink City"), ("C-Scheme", (26.906, 75.803), 6, "C-Scheme"), ("Civil Lines", (26.904, 75.783), 6, "Civil Lines"),
        ("Bani Park", (26.931, 75.792), 6, "Bani Park"), ("Raja Park", (26.895, 75.826), 7, "Raja Park"), ("Jawahar Nagar", (26.884, 75.836), 8, "Jawahar"),
        ("Lal Kothi", (26.886, 75.808), 8, "Lal Kothi")]
SVG.append(f'<circle id="heat" cx="{wp(26.905, 75.812)[0]:.1f}" cy="{wp(26.905, 75.812)[1]:.1f}" r="{4.2 * PXKM:.1f}" style="fill:url(#hg);opacity:0"/>')
J.append(f'tl.to("#heat", {{opacity:1, duration:.6}}, {S(6):.2f}); tl.to("#heat", {{opacity:0, duration:.5}}, {S(12):.2f});')
for i, (nm, ll, k, w) in enumerate(CORE):
    t = wt(k, w); p = wp(*ll)
    pin(f"corep{i}", p, PINK, t, S(12), r=1.2)
    dx, dy = COFF[nm]
    label(f"lc{i}", p, nm, t, S(8) + 1.25, at=S(5) + 1.3, cls="pink", dx=dx, dy=dy)
    sfx("pop", t, .2)
HUBS = [("Vaishali Nagar", (26.912, 75.735)), ("Shyam Nagar", (26.893, 75.765)), ("Mansarovar", (26.860, 75.760)), ("Vidhyadhar Nagar", (26.955, 75.788)),
        ("Murlipura", (26.968, 75.770)), ("Jagatpura", (26.825, 75.865))]
for i, (nm, ll) in enumerate(HUBS):
    t = wt(9, nm.split()[0]); p = wp(*ll)
    pin(f"hp{i}", p, YEL, t, S(12), r=1.8)
    dx, dy = HOFF[nm]
    label(f"lh{i}", p, nm, t, S(10) + .2, at=S(8) + 2.3, cls="yel", dx=dx, dy=dy)
    sfx("pop", t, .2)

# ---------------- price ----------------
H.append(f'<div id="price"><small>CENTRAL JAIPUR</small><b>&#8377;1 &ndash; 3 LAKH</b><em>PER GAJ</em></div>')
inout("#price", wt(10, "1 se"), S(12), frm="opacity:0, scale:1.8, rotation:-8", to="opacity:1, scale:1, rotation:-3", d=.3)
H.append('<div id="mc"><span>NAYA MIDDLE CLASS</span><b>AFFORD NAHI KAR PAATA</b></div>'); inout("#mc", S(11), S(12) + .1, frm="opacity:0, y:40", to="opacity:1, y:0")
sfx("impact-bass-1", wt(10, "1 se"), .45)

# ---------------- 3 · the shift ----------------
chap(3, "03", "THE SHIFT", S(12), S(17))
cam(S(12), (CEN[0] - 6 * PXKM, CEN[1] + 6 * PXKM), 70 * PXKM, 1.2)
J.append(f'tl.to("#city", {{opacity:.5, duration:.6}}, {S(12):.2f});')
road_op(S(12), 1)
rnd = random.Random(3)
pk = 0
for k in ["delhi", "sikar", "kalwar", "sirsi", "ajmer", "diggi", "tonk", "agra"]:
    path = max(ROADS[k], key=len) if ROADS[k] else None
    if not path: continue
    pts = sorted(path, key=lambda p: math.hypot(p[0] - CEN[0], p[1] - CEN[1]))
    near, far = pts[0], pts[min(len(pts) - 1, int(len(pts) * .55))]
    n = 26 if k in ("ajmer", "diggi", "tonk") else 12
    for j in range(n):
        t0 = S(12) + rnd.uniform(0, 3.6); d = rnd.uniform(1.4, 2.2); jx, jy = rnd.uniform(-8, 8), rnd.uniform(-8, 8)
        SVG.append(f'<circle id="pt{pk}" cx="{near[0]:.1f}" cy="{near[1]:.1f}" r="2.2" style="fill:{CYAN};opacity:0"/>')
        J.append(f'tl.fromTo("#pt{pk}", {{attr:{{cx:{near[0] + jx:.1f}, cy:{near[1] + jy:.1f}}}, opacity:.95}}, {{attr:{{cx:{far[0] + jx * 3:.1f}, cy:{far[1] + jy * 3:.1f}}}, opacity:.0, duration:{d:.2f}, ease:"power1.out", immediateRender:false}}, {t0:.2f});')
        pk += 1
H.append('<div class="big" id="outw"><b>&larr; &rarr;</b>LOG BAHAR SHIFT</div>'); inout("#outw", S(12) + .2, S(14))
# expansion wedge between Ajmer & Tonk roads (via Diggi)
WED = [wp(26.905, 75.745), wp(26.86, 75.62), wp(26.74, 75.60), wp(26.63, 75.70), wp(26.62, 75.84), wp(26.75, 75.83), wp(26.84, 75.80), wp(26.88, 75.77)]
SVG.append(f'<path id="wedge" d="{pd(smooth(WED + [WED[0]], 8), True)}" style="fill:{GREEN};fill-opacity:.22;stroke:{GREEN};stroke-width:3;stroke-dasharray:10 7;opacity:0"/>')
J.append(f'tl.to("#wedge", {{opacity:1, duration:.5}}, {wt(14, "Ajmer"):.2f}); tl.to("#wedge", {{fillOpacity:.38, duration:.35, yoyo:true, repeat:5}}, {S(16):.2f}); tl.to("#wedge", {{opacity:.55, duration:.4}}, {S(17):.2f}); tl.to("#wedge", {{opacity:0, duration:.4}}, {S(23):.2f});')
for k in ["delhi", "sikar", "kalwar", "sirsi", "agra", "bypass"]: J.append(f'tl.to(".r_{k}", {{opacity:.25, duration:.4}}, {wt(14, "Ajmer"):.2f}); tl.to(".r_{k}", {{opacity:1, duration:.4}}, {S(31):.2f});')
H.append('<div class="lab grn big2" id="lexp">NEW EXPANSION ZONE</div>')
x, y = scr(wp(26.75, 75.70), S(12) + 1.3); J.append(f'tl.set("#lexp", {{left:{x:.0f}, top:{y:.0f}}}, 0);'); inout("#lexp", S(16), S(17) + .1)
sfx("sparkle", S(16), .3)

# ---------------- colonies ----------------
COL = [("Bhankrota", (26.889, 75.664)), ("Mahapura", (26.857, 75.651)), ("Patrakar Colony", (26.836, 75.744)), ("Narayan Vihar", (26.851, 75.757)),
       ("Muhana", (26.785, 75.763)), ("Shivdaspura", (26.735, 75.842))]
H.append('<div class="big" id="newc"><b>NAYI</b>COLONIES</div>'); inout("#newc", S(17), S(20))
for i, (nm, ll) in enumerate(COL):
    k = 18 if i < 2 else 19; t = wt(k, nm.split()[0]); p = wp(*ll)
    pin(f"np{i}", p, GREEN, t, S(23), r=4)
    label(f"ln{i}", p, nm, t, S(20) + .1, at=S(12) + 1.3, cls="grn", dy=-40 if i % 2 == 0 else 40)
    sfx("pop", t, .25)
H.append('<div class="foot" id="fcol">Locations approx. · Kalwar, Sirsi, Diggi road lines indicative</div>'); inout("#fcol", S(17), S(20), frm="opacity:0", to="opacity:1")

# ---------------- why ----------------
WHY = [("&#128188;", "ROZGAAR", "rozgaar"), ("&#127973;", "HOSPITALS", "hospitals"), ("&#127979;", "SCHOOLS", "schools"), ("&#127891;", "COLLEGES", "colleges"),
       ("&#128739;", "CONNECTIVITY", "connectivity"), ("&#128722;", "SHOPS &amp; COMMERCIAL", "shops")]
H.append('<div id="why"><h3>KYUN?</h3><div class="wg">' + "".join(f'<div class="wi" id="wi{i}"><i>{a}</i><b>{b}</b></div>' for i, (a, b, _) in enumerate(WHY)) + '</div></div>')
J.append(f'tl.to("#dim", {{opacity:.55, duration:.3}}, {S(20) - .1:.2f}); tl.fromTo("#why", {{opacity:0}}, {{opacity:1, duration:.2}}, {S(20):.2f}); tl.fromTo("#why h3", {{scale:2}}, {{scale:1, duration:.3, ease:"back.out(2)"}}, {S(20):.2f}); tl.to("#why", {{opacity:0, duration:.25}}, {S(23) - .2:.2f}); tl.to("#dim", {{opacity:.2, duration:.3}}, {S(23):.2f});')
for i, (_, _, w) in enumerate(WHY):
    k = 21 if i < 2 else 22; t = wt(k, w)
    J.append(f'tl.fromTo("#wi{i}", {{opacity:0, scale:.4}}, {{opacity:1, scale:1, duration:.25, ease:"back.out(2.2)"}}, {t:.2f});'); sfx("pop", t, .25)

# ---------------- 4 · JDA region ----------------
chap(4, "04", "JDA REGION", S(23), S(27))
JW = 120 * PXKM
cam(S(23), (CEN[0], CEN[1] + 4 * PXKM), JW, 1.4)
J.append(f'tl.to("#city", {{opacity:0, duration:.5}}, {S(23):.2f});')
r1 = math.sqrt(3000 / math.pi) * PXKM; r2 = math.sqrt(7000 / math.pi) * PXKM
SVG.append(f'<circle id="c3k" cx="{CEN[0]:.1f}" cy="{CEN[1]:.1f}" r="{r1:.1f}" style="fill:#fff;fill-opacity:.06;stroke:#fff;stroke-width:4;stroke-dasharray:14 10;opacity:0"/>')
SVG.append(f'<circle id="c7k" cx="{CEN[0]:.1f}" cy="{CEN[1]:.1f}" r="{r1:.1f}" style="fill:{BLUE};fill-opacity:.2;stroke:{BLUE};stroke-width:6;opacity:0"/>')
J.append(f'tl.to("#c3k", {{opacity:1, duration:.4}}, {S(24):.2f}); tl.to("#c7k", {{opacity:1, duration:.2}}, {wt(25, "7,000") - .2:.2f}); tl.to("#c7k", {{attr:{{r:{r2:.1f}}}, duration:1.0, ease:"power2.out"}}, {wt(25, "7,000") - .2:.2f});'
         f'tl.to(["#c3k", "#c7k"], {{opacity:.35, duration:.4}}, {S(27):.2f}); tl.to(["#c3k", "#c7k"], {{opacity:0, duration:.4}}, {S(31):.2f});')
H.append(f'<div id="jda"><small>JDA NOTIFICATION · OCT 2025</small><div class="jr"><span>~3,000</span><i>&rarr;</i><b>~7,000</b><em>SQ KM</em></div><div class="jv" id="jv"><b>+693</b> NAYE GAON</div></div>')
J.append(f'tl.fromTo("#jda", {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:.3}}, {S(24):.2f}); tl.from("#jda .jr b", {{opacity:0, scale:2, duration:.3, ease:"back.out(2)"}}, {wt(25, "7,000") - .1:.2f}); tl.from("#jv", {{opacity:0, scale:.5, duration:.3, ease:"back.out(2)"}}, {wt(26, "693"):.2f}); tl.to("#jda", {{opacity:0, duration:.25}}, {S(27) - .1:.2f});')
sfx("impact-bass-1", wt(25, "7,000") - .2, .45); sfx("sparkle", wt(26, "693"), .3)
TEH = [("Bassi", (26.838, 76.044)), ("Chaksu", (26.606, 75.948)), ("Jamwa Ramgarh", (27.03, 76.06)), ("Shahpura", (27.39, 75.96)), ("Phagi", (26.57, 75.55)),
       ("Jobner", (26.972, 75.385)), ("Dudu", (26.681, 75.232)), ("Chomu", (27.17, 75.72))]
for i, (nm, ll) in enumerate(TEH):
    t = wt(26, "693") + .1 + .12 * i; p = wp(*ll)
    pin(f"tp{i}", p, GOLD, t, S(31), r=6)
    label(f"lt{i}", p, nm, t, S(27) + .1, at=S(23) + 1.5, cls="gold sm", dy=-36)
H.append('<div class="foot" id="fjda">Oct 2025 notification (Patrika) · circles show area only</div>'); inout("#fjda", S(24), S(27), frm="opacity:0", to="opacity:1")

# ---------------- opportunity ----------------
J.append(f'tl.to("#c7k", {{opacity:.8, fillOpacity:.32, duration:.4, yoyo:true, repeat:3}}, {S(27):.2f});')
H.append('<div id="opp"><small>AAJ KA MAUKA</small><b>JAIPUR KE<br/>BAHAR KE ILAAKE</b><em>Growth wahan pahunchegi</em></div>')
J.append(f'tl.fromTo("#opp", {{opacity:0, scale:.7}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, {S(28):.2f}); tl.to("#opp", {{opacity:0, duration:.25}}, {S(30) - .1:.2f});')
H.append('<div id="chk"><small>PLOT LENE SE PEHLE CHECK KARO</small><p>&#10003; JDA / layout <b>APPROVAL</b></p><p>&#10003; <b>PATTA</b></p></div>')
J.append(f'tl.to("#dim", {{opacity:.6, duration:.3}}, {S(30) - .1:.2f}); tl.fromTo("#chk", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.3}}, {S(30):.2f}); tl.fromTo("#chk p", {{opacity:0, x:-50}}, {{opacity:1, x:0, duration:.25, stagger:.4}}, {wt(30, "approval"):.2f}); tl.to("#chk", {{opacity:0, duration:.25}}, {S(31) - .1:.2f}); tl.to("#dim", {{opacity:.2, duration:.3}}, {S(31):.2f});')
sfx("whoosh-short", S(28), .3); sfx("click-soft", wt(30, "approval"), .3); sfx("click-soft", wt(30, "patta"), .3)

# ---------------- CTA ----------------
cam(S(31) - .3, CEN, REG_W, 1.0)
for i, (k, nm, lp) in enumerate(ORDER):
    H.append(f'<div class="rl" id="rc{i}"><b>{i + 1}</b>{nm}</div>')
    x, y = scr(wp(*lp), S(31) + 1); x = min(max(x, 150), 880)
    J.append(f'tl.set("#rc{i}", {{left:{x:.0f}, top:{y:.0f}}}, 0);')
    J.append(f'tl.fromTo("#rc{i}", {{opacity:0, scale:.5}}, {{opacity:1, scale:1, duration:.25, ease:"back.out(2)"}}, {S(31) + .3 + .1 * i:.2f}); tl.to("#rc{i} b", {{scale:1.3, duration:.25, yoyo:true, repeat:5}}, {S(32):.2f});')
    J.append(f'tl.to(".r_{k}", {{strokeWidth:"+=3", duration:.3, yoyo:true, repeat:5}}, {S(31) + .3 + .1 * i:.2f});')
H.append('<div id="cta"><b>KAUNSA ROAD SABSE TEZ BADHEGA?</b><span>COMMENT MEIN NUMBER LIKHO</span><i>FOLLOW FOR PART 2</i></div>')
J.append(f'tl.fromTo("#cta", {{opacity:0}}, {{opacity:1, duration:.2}}, {S(31):.2f}); tl.from("#cta b", {{opacity:0, scale:.6, duration:.3, ease:"back.out(2)"}}, {S(31):.2f}); tl.from("#cta span", {{opacity:0, y:30, duration:.3}}, {S(32):.2f}); tl.from("#cta i", {{opacity:0, scale:.5, duration:.3, ease:"back.out(2)"}}, {S(33) + .5:.2f});')
sfx("sparkle", S(32), .3)

# ---------------- captions ----------------
HI = ["Jaipur", "property", "structure", "highways", "Delhi Road", "Sikar Road", "Kalwar Road", "Sirsi Road", "Ajmer Road", "Diggi Road", "Tonk Road", "Agra Road", "Ring Road",
      "Central Jaipur", "Pink City", "C-Scheme", "Civil Lines", "Bani Park", "Raja Park", "Jawahar Nagar", "Lal Kothi", "Vaishali Nagar", "Shyam Nagar", "Mansarovar",
      "Vidhyadhar Nagar", "Murlipura", "Jagatpura", "1 se 3 lakh", "middle class", "bahar shift", "growth", "expansion zone", "nayi colonies", "Bhankrota", "Mahapura",
      "Patrakar Colony", "Narayan Vihar", "Muhana", "Shivdaspura", "rozgaar", "hospitals", "schools", "colleges", "connectivity", "commercial", "JDA", "7,000 sq km",
      "693 naye gaon", "mauka", "approval", "patta", "Comment", "Part 2"]
def hl(t):
    for h in sorted(HI, key=len, reverse=True):
        i = t.find(h)
        if i >= 0 and '"y"' not in t[max(0, i - 20):i] and '<span' not in t[i:i + len(h)]: t = t[:i] + '<span class="y">' + h + '</span>' + t[i + len(h):]
    return t
ci = 0
for n, ph in enumerate(PH):
    words = ph["t"].split(); chunks = []; cur = ""
    for w_ in words:
        if cur and len(cur) + 1 + len(w_) > 24: chunks.append(cur); cur = w_
        else: cur = (cur + " " + w_).strip()
    chunks.append(cur)
    tot = sum(len(c) for c in chunks); t = ph["s"]
    nxt = PH[n + 1]["s"] if n + 1 < len(PH) else END
    for j, c in enumerate(chunks):
        d = (ph["e"] - ph["s"]) * len(c) / tot
        a = max(.02, t if j else t - .04); b = (min(t + d + .25, nxt - .08) if j == len(chunks) - 1 else t + d - .03)
        H.append(f'<div class="cp" id="cp{ci}"><div>{hl(c)}</div></div>')
        J.append(f'tl.fromTo("#cp{ci}", {{opacity:0, scale:.88}}, {{opacity:1, scale:1, duration:.1}}, {a:.2f}); tl.to("#cp{ci}", {{opacity:0, duration:.04}}, {b - .04:.2f});')
        t += d; ci += 1

H.append('<div id="wm">DIGITAL BANJAARAA</div><div id="vig"></div><div id="flash"></div><div id="grain"></div>')
DEFS = f'<defs><radialGradient id="hg"><stop offset="0" stop-color="{RED}" stop-opacity=".55"/><stop offset=".6" stop-color="{RED}" stop-opacity=".18"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient></defs>'
CSS = """@font-face{font-family:Anton;src:url(assets/fonts/anton.woff2)}@font-face{font-family:Mont;font-weight:700;src:url(assets/fonts/mont700.woff2)}
@font-face{font-family:Mont;font-weight:800;src:url(assets/fonts/mont800.woff2)}@font-face{font-family:Mont;font-weight:900;src:url(assets/fonts/mont900.woff2)}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#080a0f}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif}#world{position:absolute;inset:0;width:1080px;height:1920px}
.y{color:#FFC42E}
#face{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:30}
#vig{position:absolute;inset:0;pointer-events:none;background:radial-gradient(80% 60% at 50% 45%,rgba(0,0,0,0) 45%,rgba(0,0,0,.65) 100%);z-index:2}
#flash{position:absolute;inset:0;background:#fff;opacity:0;z-index:25;pointer-events:none}
#wm{position:absolute;left:0;right:0;top:200px;text-align:center;font:800 24px Mont;letter-spacing:.34em;color:rgba(255,255,255,.5);z-index:20}
#title{position:absolute;left:0;right:0;top:330px;text-align:center;z-index:6}#title span{display:block;font:400 200px/1 Anton;color:#FF3246;text-shadow:0 8px 40px rgba(0,0,0,.8)}
#title b{display:block;font:400 110px/1 Anton;color:#fff;letter-spacing:.04em}#title i{display:inline-block;margin-top:18px;padding:10px 28px;border-radius:40px;background:#FFC42E;color:#111;font:900 40px Mont;font-style:normal;letter-spacing:.06em}
.chap{position:absolute;left:50px;top:262px;display:flex;align-items:center;gap:14px;padding:8px 24px 8px 8px;border-radius:40px;background:rgba(8,10,15,.88);border:2px solid #FFC42E;font:400 46px/1 Anton;color:#fff;letter-spacing:.04em;opacity:0;z-index:8}
.chap b{padding:8px 14px;border-radius:30px;background:#FFC42E;color:#111;font:400 40px/1 Anton}
.big{position:absolute;left:0;right:0;top:360px;text-align:center;opacity:0;z-index:7;font:900 50px Mont;color:#fff;letter-spacing:.08em;text-shadow:0 4px 18px #000}.big b{display:block;font:400 150px/1 Anton;color:#FFC42E}
.lab{position:absolute;opacity:0;translate:-50% -50%;padding:7px 16px;border-radius:24px;background:rgba(8,10,15,.88);border:2px solid #fff;font:800 28px Mont;color:#fff;white-space:nowrap;z-index:5}
.lab.pink{border-color:#FF50AA}.lab.yel{border-color:#FFE03A}.lab.grn{border-color:#3CFF96}.lab.gold{border-color:#FFC42E}.lab.sm{font-size:24px}.lab.ring{border-color:#3CFF96;color:#3CFF96;font-size:30px}
.lab.big2{font-size:40px;padding:12px 24px;background:#3CFF96;color:#111;border-color:#3CFF96}
.rl{position:absolute;opacity:0;translate:-50% -50%;display:flex;align-items:center;gap:10px;padding:6px 18px 6px 6px;border-radius:30px;background:rgba(8,10,15,.9);border:2px solid #FFC42E;font:900 28px Mont;color:#fff;white-space:nowrap;z-index:5}
.rl b{width:38px;height:38px;border-radius:50%;background:#FFC42E;color:#111;display:flex;align-items:center;justify-content:center;font:900 24px Mont}
#price{position:absolute;left:110px;right:110px;top:420px;opacity:0;text-align:center;padding:26px 0;border-radius:24px;border:6px solid #FFC42E;background:rgba(20,14,4,.92);z-index:7;transform:rotate(-3deg)}
#price small{display:block;font:900 30px Mont;letter-spacing:.14em;color:#fff}#price b{display:block;font:400 120px/1.05 Anton;color:#FFC42E}#price em{display:block;font-style:normal;font:900 44px Mont;color:#fff;letter-spacing:.16em}
#mc{position:absolute;left:80px;right:80px;top:790px;opacity:0;text-align:center;padding:18px;border-radius:20px;background:#FF3246;z-index:7}#mc span{display:block;font:900 30px Mont;color:#fff;letter-spacing:.1em}#mc b{display:block;font:400 56px Anton;color:#fff}
#why{position:absolute;left:50px;right:50px;top:380px;opacity:0;z-index:8;text-align:center}#why h3{font:400 120px Anton;color:#FFC42E;margin-bottom:20px}
.wg{display:grid;grid-template-columns:1fr 1fr;gap:20px}.wi{opacity:0;padding:24px 10px;border-radius:24px;background:rgba(8,10,15,.92);border:3px solid #3CFF96}.wi i{display:block;font-style:normal;font-size:72px}.wi b{display:block;margin-top:6px;font:900 34px Mont;color:#fff}
#jda{position:absolute;left:50px;right:50px;top:350px;opacity:0;padding:24px 28px;border-radius:26px;background:rgba(8,10,15,.9);border:3px solid #50A0FF;z-index:7;text-align:center}
#jda small{display:block;font:900 28px Mont;color:#50A0FF;letter-spacing:.1em}.jr{display:flex;align-items:baseline;justify-content:center;gap:18px;margin-top:6px}.jr span{font:400 80px Anton;color:#aab}.jr i{font-style:normal;font:900 60px Mont;color:#fff}.jr b{font:400 120px Anton;color:#fff}.jr em{font-style:normal;font:900 34px Mont;color:#fff}
.jv{display:inline-block;margin-top:8px;padding:8px 26px;border-radius:30px;background:#FFC42E;color:#111;font:900 40px Mont}.jv b{font:400 50px Anton}
#opp{position:absolute;left:60px;right:60px;top:420px;opacity:0;text-align:center;padding:34px 20px;border-radius:30px;background:rgba(8,10,15,.9);border:4px solid #3CFF96;z-index:7}
#opp small{display:block;font:900 34px Mont;color:#3CFF96;letter-spacing:.14em}#opp b{display:block;margin:10px 0;font:400 100px/1 Anton;color:#fff}#opp em{display:block;font-style:normal;font:800 40px Mont;color:#FFC42E}
#chk{position:absolute;left:60px;right:60px;top:520px;opacity:0;padding:30px 34px;border-radius:28px;background:rgba(8,10,15,.92);border:3px solid #FFC42E;z-index:8}#chk small{display:block;font:900 30px Mont;color:#FFC42E;letter-spacing:.06em;margin-bottom:10px}#chk p{font:800 54px/1.4 Mont;color:#fff}#chk p b{color:#FFC42E}
#cta{position:absolute;left:50px;right:50px;top:330px;opacity:0;text-align:center;z-index:8}#cta b{display:block;padding:20px;border-radius:24px;background:#FFC42E;color:#111;font:400 66px/1.05 Anton}
#cta span{display:inline-block;margin-top:16px;padding:12px 26px;border-radius:30px;background:#FF3246;color:#fff;font:900 36px Mont}#cta i{display:block;margin:16px auto 0;width:520px;padding:12px;border-radius:30px;background:#fff;color:#111;font:900 36px Mont;font-style:normal}
.foot{position:absolute;left:40px;right:40px;top:1610px;text-align:center;opacity:0;font:600 20px Mont;color:rgba(255,255,255,.7);z-index:6}
.cp{position:absolute;left:40px;right:130px;top:1400px;text-align:center;opacity:0;z-index:35}
.cp div{display:inline-block;font:900 64px/1.12 Mont;color:#fff;-webkit-text-stroke:7px #000;paint-order:stroke fill;text-shadow:0 6px 18px rgba(0,0,0,.8)}"""
open(f"{P}/index.html", "w").write(f"""<!doctype html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="30">
<svg id="world" viewBox="{vb(CEN, CITY_W * 1.6)}" preserveAspectRatio="xMidYMid slice">{DEFS}{"".join(SVG)}</svg>
{"".join(H)}
<audio id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{END}" data-track-index="1" data-volume="1"></audio>
{"".join(SFX)}
</div><script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(J)}
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>""")
print("END", END, "captions", ci, {k: len(v) for k, v in ROADS.items()})
