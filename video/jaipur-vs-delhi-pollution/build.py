"""Delhi vs Jaipur pollution reel — 3D tilted North-India map. World = z13 web-mercator px from tile (5791, 3466).
Wind/smoke/inversion graphics are explanatory illustrations, not measured data."""
import json, math, os
P = "proj"
LINES = [""] * 9
VOICE = os.path.exists("rec/phrases.json")
if VOICE: PH = json.load(open("rec/phrases.json"))
else:
    PH = []; t = .3
    for l in LINES:
        d = len(l) / 15 + .15; PH.append({"s": round(t, 2), "e": round(t + d, 2), "t": l}); t += d + .3
def S(k): return PH[k]["s"]
def E(k): return PH[k]["e"]
def wt(k, w):
    t = PH[k]["t"]; i = t.lower().find(w.lower()); assert i >= 0, (k, w)
    return S(k) + (E(k) - S(k)) * i / len(t)
END = round(E(8) + .9, 2)
def wp(lat, lon):
    n = 2 ** 13
    return (((lon + 180) / 360 * n) - 5791) * 256, (((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n) - 3466) * 256
SVG, H, J, SFX, IN = [], [], [], [], []   # IN = html placed inside the 3D plane
def sfx(n, t, v=.3): SFX.append(f'<audio id="sx{len(SFX)}" class="clip" src="assets/sfx/{n}.mp3" data-start="{t:.2f}" data-duration="2" data-track-index="{20 + len(SFX)}" data-volume="{v}"></audio>')
def pd(pts, close=False): return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + (" Z" if close else "")
GOLD, CREAM, RED, GRN, SKY = "#C9A24A", "#F3E6C8", "#E5484D", "#3CE65A", "#7FD0FF"

# ---------- fixed camera (all motion is CSS 3D on #plane) ----------
CX, CY, CW = 10300, -14500, 40000
CH = CW * 1920 / 1080
VB = f"{CX - CW / 2:.0f} {CY - CH / 2:.0f} {CW:.0f} {CH:.0f}"
def scr(p): return ((p[0] - (CX - CW / 2)) / CW * 1080, (p[1] - (CY - CH / 2)) / CH * 1920)
U = CW / 1080   # world units per screen px

# ---------- base ----------
SVG.append('<rect x="-900000" y="-900000" width="2000000" height="2000000" style="fill:#1b1b1d"/>')
for href, x, y, w, h in [("bm4.jpg", -302848, -363008, 786432, 786432), ("bm5.jpg", -171776, -166400, 327680, 393216), ("bm7.webp", -40704, -35328, 81920, 65536)]:
    SVG.append(f'<image href="assets/img/{href}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="none"/>')
SVG.append('<rect x="-900000" y="-900000" width="2000000" height="2000000" style="fill:#000;opacity:.28"/>')
ST = json.load(open("data/states.json"))
def ring(rs): return " ".join(pd([wp(la, lo) for lo, la in r], True) for r in rs)
for nm, col in [("Rajasthan", GOLD), ("Haryana", "#9aa"), ("Delhi", "#bbb")]:
    SVG.append(f'<path id="st_{nm}" d="{ring(ST[nm])}" style="fill:none;stroke:{col};stroke-width:3;stroke-opacity:.6;vector-effect:non-scaling-stroke;stroke-dasharray:10 8"/>')

DEL, JPR = wp(28.61, 77.21), wp(26.91, 75.79)
PUN = [wp(30.9, 75.0), wp(30.4, 75.9), wp(31.3, 74.5), wp(30.2, 74.8), wp(29.9, 76.3), wp(29.4, 76.8), wp(30.7, 76.4), wp(29.7, 75.6)]
# smog dome / bowl over the Indo-Gangetic plain
BOWL = [wp(*p) for p in [(31.0, 74.3), (31.6, 75.6), (30.9, 77.2), (29.8, 78.4), (28.6, 79.6), (27.2, 79.8), (26.6, 78.6), (27.6, 77.6), (28.2, 76.7), (29.2, 75.4), (30.2, 74.2)]]
SVG.append(f'<defs><radialGradient id="smg"><stop offset="0" stop-color="#9a958c" stop-opacity=".95"/><stop offset=".6" stop-color="#7d7870" stop-opacity=".7"/><stop offset="1" stop-color="#6b665e" stop-opacity="0"/></radialGradient>'
           f'<radialGradient id="cln"><stop offset="0" stop-color="{SKY}" stop-opacity=".55"/><stop offset="1" stop-color="{SKY}" stop-opacity="0"/></radialGradient>'
           f'<filter id="blur"><feGaussianBlur stdDeviation="{U * 14:.0f}"/></filter>'
           f'<marker id="ah" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="3.2" markerHeight="3.2" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#fff"/></marker>'
           f'<marker id="ahb" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="3.2" markerHeight="3.2" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="{SKY}"/></marker></defs>')
SVG.append(f'<path id="bowl" d="{pd(BOWL, True)}" style="fill:#8a857c;fill-opacity:.0;stroke:#c9c3b6;stroke-width:3;stroke-opacity:0;vector-effect:non-scaling-stroke;filter:url(#blur)"/>')
SVG.append(f'<circle id="smog" cx="{DEL[0]:.0f}" cy="{DEL[1]:.0f}" r="{U * 260:.0f}" style="fill:url(#smg);opacity:0"/>')
SVG.append(f'<circle id="clean" cx="{JPR[0]:.0f}" cy="{JPR[1]:.0f}" r="{U * 200:.0f}" style="fill:url(#cln);opacity:0"/>')
SVG.append(f'<circle id="jring" cx="{JPR[0]:.0f}" cy="{JPR[1]:.0f}" r="{U * 60:.0f}" style="fill:none;stroke:{GRN};stroke-width:5;vector-effect:non-scaling-stroke;opacity:0"/>')
SVG.append(f'<circle id="dring" cx="{DEL[0]:.0f}" cy="{DEL[1]:.0f}" r="{U * 60:.0f}" style="fill:none;stroke:{RED};stroke-width:5;vector-effect:non-scaling-stroke;opacity:0"/>')
# fires (Punjab / Haryana)
for i, p in enumerate(PUN):
    SVG.append(f'<g class="fire" id="fr{i}" style="opacity:0"><circle cx="{p[0]:.0f}" cy="{p[1]:.0f}" r="{U * 26:.0f}" style="fill:#FF6A00;opacity:.35"/><circle class="fc" cx="{p[0]:.0f}" cy="{p[1]:.0f}" r="{U * 11:.0f}" style="fill:#FFB000"/></g>')
# wind arrows NW -> SE into Delhi
WIND = []
for k, (a, b) in enumerate([((31.6, 73.6), (29.0, 76.6)), ((31.0, 74.8), (28.8, 77.0)), ((30.4, 75.8), (28.7, 77.3)), ((31.9, 75.2), (29.6, 77.4))]):
    p0, p1 = wp(*a), wp(*b); m = ((p0[0] + p1[0]) / 2 + U * 40, (p0[1] + p1[1]) / 2 - U * 30)
    d = f"M{p0[0]:.0f} {p0[1]:.0f} Q{m[0]:.0f} {m[1]:.0f} {p1[0]:.0f} {p1[1]:.0f}"; WIND.append((p0, m, p1))
    SVG.append(f'<path class="wind" id="wd{k}" d="{d}" pathLength="1" marker-end="url(#ah)" style="fill:none;stroke:#fff;stroke-width:7;stroke-linecap:round;vector-effect:non-scaling-stroke;stroke-dasharray:1;stroke-dashoffset:1;opacity:.9"/>')
# smoke particles that travel along the wind curves
NPART = 26
for k in range(NPART):
    SVG.append(f'<circle class="pt" id="pt{k}" r="{U * (8 + (k % 4) * 3):.0f}" cx="0" cy="0" style="fill:#a7a29a;opacity:0"/>')
def qb(p0, m, p1, t): return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * m[0] + t * t * p1[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * m[1] + t * t * p1[1])
# clean wind over Jaipur (Aravalli section)
for k, (a, b) in enumerate([((27.6, 74.4), (26.4, 76.9)), ((27.3, 74.2), (26.1, 76.7)), ((27.9, 74.7), (26.7, 77.2))]):
    p0, p1 = wp(*a), wp(*b); m = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 - U * 40)
    SVG.append(f'<path class="cw" id="cw{k}" d="M{p0[0]:.0f} {p0[1]:.0f} Q{m[0]:.0f} {m[1]:.0f} {p1[0]:.0f} {p1[1]:.0f}" pathLength="1" marker-end="url(#ahb)" style="fill:none;stroke:{SKY};stroke-width:6;stroke-linecap:round;vector-effect:non-scaling-stroke;stroke-dasharray:.25 .08;stroke-dashoffset:0;opacity:0"/>')

# ---------- 3D mountain ridges (inside plane, standing up) ----------
def ridge(cls, pts, n, hmin, hmax, wpx, col, cap=None, seed=1):
    import random; rnd = random.Random(seed)
    L = [0.0]
    for a_, b_ in zip(pts, pts[1:]): L.append(L[-1] + math.hypot(b_[0] - a_[0], b_[1] - a_[1]))
    for k in range(n):
        tg = L[-1] * (k + .5) / n; j = next(m for m in range(1, len(L)) if L[m] >= tg); f = (tg - L[j - 1]) / (L[j] - L[j - 1])
        p = (pts[j - 1][0] + (pts[j][0] - pts[j - 1][0]) * f, pts[j - 1][1] + (pts[j][1] - pts[j - 1][1]) * f)
        x, y = scr(p); h = rnd.uniform(hmin, hmax); w = wpx * rnd.uniform(.8, 1.3); x += rnd.uniform(-8, 8)
        cls2 = "mh" if cap else "ma"
        IN.append(f'<div class="mt {cls} {cls2}" style="left:{x - w / 2:.0f}px;top:{y - h:.0f}px;width:{w:.0f}px;height:{h:.0f}px"></div>')
HIM = [wp(*p) for p in [(33.4, 73.6), (32.6, 75.6), (31.9, 77.0), (31.0, 78.6), (30.2, 80.0)]]
ARV = [wp(*p) for p in [(28.3, 76.9), (27.8, 76.3), (27.3, 75.9), (26.95, 75.85), (26.6, 75.5), (26.1, 74.7), (25.5, 74.0)]]
ridge("him", HIM, 26, 120, 220, 70, "#7e8796", "#ffffff", 3)
ridge("arv", ARV, 26, 28, 60, 52, "#8a6a42", None, 7)
def pin(i, p, text, cls=""):
    x, y = scr(p); IN.append(f'<div class="bb {cls}" id="{i}" style="left:{x:.0f}px;top:{y:.0f}px"><span>{text}</span></div>')
pin("bdel", DEL, "DELHI", "red"); pin("bjpr", JPR, "JAIPUR", "grn"); pin("bpun", wp(30.8, 75.3), "PUNJAB &middot; HARYANA", "org")
pin("bhim", wp(32.2, 76.6), "HIMALAYA", "wht"); pin("barv", wp(26.45, 75.45), "ARAVALI", "gold")

def lux(i, html, t, until, x, y, cls=""):
    H.append(f'<div class="lx {cls}" id="lx{i}" style="left:{x}px;top:{y}px">{html}</div>')
    J.append(f'tl.fromTo("#lx{i}", {{opacity:0, y:24, clipPath:"inset(0 100% 0 0)"}}, {{opacity:1, y:0, clipPath:"inset(0 0% 0 0)", duration:.45, ease:"power3.out"}}, {t:.2f}); tl.to("#lx{i}", {{opacity:0, y:-14, duration:.3}}, {until - .3:.2f});')
    sfx("click-soft", t, .3)
def bb(i, t, until):
    J.append(f'tl.fromTo("#{i}", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)", immediateRender:false}}, {t:.2f}); tl.to("#{i}", {{opacity:0, duration:.25}}, {until - .25:.2f});')
def plane(t, rx, sc, x, y, d=1.0):
    J.append(f'tl.to("#plane", {{rotationX:{rx}, scale:{sc}, x:{x}, y:{y}, duration:{d}, ease:"power2.inOut"}}, {t:.2f});')
def jp_focus(rx, sc):
    x, y = scr(JPR); return rx, sc, (540 - x) * sc, (1060 - y) * sc

J.append('tl.set("#plane", {rotationX:48, scale:1.0, x:0, y:0, transformOrigin:"50% 55%"}, 0); tl.set(".mt", {scaleY:0.001, rotationX:-90, transformOrigin:"50% 100%"}, 0); tl.set(".bb", {opacity:0, xPercent:-50, yPercent:-100, rotationX:-48, transformOrigin:"50% 100%"}, 0); tl.set(".wind", {opacity:0}, 0);')

# ---------- 0 HOOK: smog Delhi vs clean Jaipur ----------
J.append(f'tl.to("#smog", {{opacity:1, duration:.6}}, .1); tl.fromTo("#smog", {{attr:{{r:{U * 120:.0f}}}}}, {{attr:{{r:{U * 300:.0f}}}, duration:1.4, ease:"power2.out", immediateRender:false}}, .1); tl.to("#smog", {{attr:{{r:{U * 270:.0f}}}, duration:1.2, yoyo:true, repeat:5, ease:"sine.inOut"}}, 1.5);')
J.append(f'tl.to("#clean", {{opacity:1, duration:.6}}, {wt(0, "Jaipur") - .1:.2f}); tl.to(["#dring"], {{opacity:1, duration:.3}}, .2); tl.to("#jring", {{opacity:1, duration:.3}}, {wt(0, "Jaipur") - .1:.2f});')
bb("bdel", .2, S(6)); bb("bjpr", wt(0, "Jaipur") - .1, S(8))
H.append('<div id="hook"><small>DELHI SE JAIPUR SHIFT &middot; KYUN?</small><div class="vs"><div class="d"><b>DELHI</b><span>GAS CHAMBER</span></div><i>vs</i><div class="j"><b>JAIPUR</b><span>UTNA BURA NAHI</span></div></div><em>4 REASONS</em></div>')
J.append(f'tl.fromTo("#hook", {{opacity:1, scale:1.1}}, {{opacity:1, scale:1, duration:.4, ease:"power3.out"}}, 0); tl.fromTo("#hook .d", {{opacity:0, x:-40}}, {{opacity:1, x:0, duration:.4}}, .1);'
         f'tl.fromTo(["#hook i", "#hook .j"], {{opacity:0, x:40}}, {{opacity:1, x:0, duration:.4, stagger:.1}}, {wt(0, "Jaipur") - .15:.2f}); tl.fromTo("#hook em", {{opacity:0, y:20}}, {{opacity:1, y:0, duration:.35}}, {wt(1, "chaar") - .1:.2f}); tl.to("#hook", {{opacity:0, y:-30, duration:.3}}, {S(2) - .2:.2f});')
sfx("impact-bass-1", 0, .45); sfx("whoosh", wt(0, "Jaipur") - .15, .3)

def chapter(k, n, title):
    H.append(f'<div class="ch" id="ch{k}"><b>0{n}</b><span>{title}</span></div>')
    J.append(f'tl.fromTo("#ch{k}", {{opacity:0, x:-50}}, {{opacity:1, x:0, duration:.45, ease:"power3.out"}}, {S(k) - .05:.2f}); tl.to("#ch{k}", {{opacity:0, duration:.3}}, {S(k + 1) - .25:.2f});')
    sfx("whoosh-short", S(k), .3)

# ---------- 1 wind + stubble ----------
chapter(2, 1, "HAWA KI DISHA")
plane(S(2) - .2, 50, 1.15, 120, 260, 1.0)
bb("bpun", wt(2, "Punjab") - .1, S(3))
for i in range(len(PUN)):
    t = wt(2, "parali") - .1 + i * .06
    J.append(f'tl.to("#fr{i}", {{opacity:1, duration:.2}}, {t:.2f}); tl.fromTo("#fr{i} .fc", {{attr:{{r:{U * 8:.0f}}}}}, {{attr:{{r:{U * 15:.0f}}}, duration:.25, yoyo:true, repeat:-1, ease:"sine.inOut"}}, {t:.2f}); tl.to("#fr{i}", {{opacity:0, duration:.3}}, {S(4):.2f});')
sfx("riser", wt(2, "parali") - .1, .25)
for k in range(len(WIND)):
    J.append(f'tl.set("#wd{k}", {{opacity:.9}}, {wt(2, "north-west") - .1 + k * .15:.2f}); tl.to("#wd{k}", {{strokeDashoffset:0, duration:.9, ease:"power2.out"}}, {wt(2, "north-west") - .1 + k * .15:.2f}); tl.to("#wd{k}", {{opacity:0, duration:.3}}, {S(3) + .3:.2f});')
lux(1, "<b>&#8600;</b> NORTH-WEST WINDS", wt(2, "north-west") - .1, wt(2, "parali") - .1, 60, 1290)
T0 = wt(2, "dhuaan") - .3
for k in range(NPART):
    p0, m, p1 = WIND[k % len(WIND)]
    st = T0 + (k // len(WIND)) * .35 + (k % len(WIND)) * .08; dur = 2.2
    pts = [qb(p0, m, p1, s / 10) for s in range(11)]
    J.append(f'tl.set("#pt{k}", {{attr:{{cx:{pts[0][0]:.0f}, cy:{pts[0][1]:.0f}}}, opacity:.0}}, {st - .01:.2f}); tl.to("#pt{k}", {{opacity:.75, duration:.2}}, {st:.2f});')
    for s in range(1, 11):
        J.append(f'tl.to("#pt{k}", {{attr:{{cx:{pts[s][0]:.0f}, cy:{pts[s][1]:.0f}}}, duration:{dur / 10:.3f}, ease:"none"}}, {st + dur * (s - 1) / 10:.3f});')
    J.append(f'tl.to("#pt{k}", {{opacity:0, duration:.4}}, {st + dur:.2f});')
J.append(f'tl.to("#smog", {{opacity:1, attr:{{r:{U * 290:.0f}}}, duration:1.2}}, {T0 + 1.6:.2f});')
lux(2, "<b>&#10006;</b> JAIPUR IS RAASTE MEIN NAHI", wt(2, "Jaipur") - .1, S(3), 60, 1290, "grn")
J.append(f'tl.fromTo("#jring", {{attr:{{r:{U * 40:.0f}}}}}, {{attr:{{r:{U * 120:.0f}}}, opacity:0, duration:.9, repeat:2, immediateRender:false}}, {wt(2, "Jaipur") - .1:.2f}); tl.set("#jring", {{opacity:1, attr:{{r:{U * 60:.0f}}}}}, {wt(2, "Jaipur") + 2.6:.2f});')

# ---------- 2 bowl (Indo-Gangetic plain + Himalaya) ----------
chapter(3, 2, "DELHI KI KATORI")
plane(S(3) - .2, 58, 1.05, 0, 330, 1.0)
J.append(f'tl.fromTo(".him", {{scaleY:0.001, rotationX:-90, transformOrigin:"50% 100%"}}, {{scaleY:1, rotationX:-90, duration:.5, stagger:.03, ease:"back.out(1.6)", immediateRender:false}}, {S(3) + .2:.2f});')
bb("bhim", S(3) + .7, S(6))
J.append(f'tl.to("#bowl", {{fillOpacity:.55, strokeOpacity:.8, duration:1.0}}, {wt(3, "maidan") - .2:.2f}); tl.to("#bowl", {{fillOpacity:.7, duration:.6, yoyo:true, repeat:3}}, {wt(3, "katori") - .1:.2f}); tl.to("#bowl", {{fillOpacity:.3, strokeOpacity:0, duration:.5}}, {S(5) - .1:.2f});')
lux(3, "INDO-GANGETIC PLAIN &middot; <b>BOWL</b>", wt(3, "Indo") - .1, wt(3, "katori") - .4, 60, 1290)
lux(4, "HAWA DHEEMI &middot; POLLUTION <b>TRAPPED</b>", wt(3, "dheemi") - .1, S(4), 60, 1190, "red")
sfx("impact-bass-1", wt(3, "katori"), .35)
H.append(f'''<div id="arc"><svg viewBox="0 0 960 600" width="960" height="600">
<defs><linearGradient id="arcsky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1c2740"/><stop offset="1" stop-color="#3b4a63"/></linearGradient>
<linearGradient id="arcg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6b5a3e"/><stop offset="1" stop-color="#2a2218"/></linearGradient>
<radialGradient id="arcsm" cx=".5" cy=".7" r=".6"><stop offset="0" stop-color="#b9b3a8" stop-opacity="1"/><stop offset=".7" stop-color="#9a958b" stop-opacity=".8"/><stop offset="1" stop-color="#8a857c" stop-opacity="0"/></radialGradient></defs>
<rect width="960" height="600" fill="url(#arcsky)"/>
<path class="hm" d="M0 600 L0 120 L40 60 L80 130 L120 40 L170 150 L200 110 L230 230 L230 600 Z" fill="#6e7684"/><path d="M40 60 L58 92 L28 92 Z M120 40 L142 80 L98 80 Z" fill="#fff"/>
<path class="bowl" d="M200 600 L200 230 Q 300 520 430 520 Q 560 520 640 360 L640 600 Z" fill="url(#arcg)"/>
<path class="plat" d="M630 600 L630 370 Q 660 330 700 318 L760 300 L790 268 L815 300 L850 285 L875 262 L900 296 L960 290 L960 600 Z" fill="#7a6544"/>
<ellipse class="smog" cx="430" cy="440" rx="230" ry="120" fill="url(#arcsm)"/>
<g class="dl"><circle cx="430" cy="512" r="12" fill="#E5484D"/><rect x="370" y="452" width="120" height="40" rx="4" fill="#1a1510" stroke="#E5484D" stroke-width="2"/><text x="430" y="480" text-anchor="middle" font-family="Mont" font-weight="700" font-size="22" letter-spacing="4" fill="#FFB4B4">DELHI</text><text x="452" y="522" text-anchor="start" font-family="Anton" font-size="30" fill="#FFB4B4">~215 M</text></g>
<g class="jp"><circle cx="820" cy="292" r="12" fill="#3CE65A"/><rect x="755" y="226" width="130" height="40" rx="4" fill="#1a1510" stroke="#3CE65A" stroke-width="2"/><text x="820" y="254" text-anchor="middle" font-family="Mont" font-weight="700" font-size="22" letter-spacing="4" fill="#B8FFC6">JAIPUR</text><text x="820" y="340" text-anchor="middle" font-family="Anton" font-size="30" fill="#B8FFC6">~430 M</text>
<path class="jw" d="M640 200 Q 800 170 950 210" fill="none" stroke="{SKY}" stroke-width="5" stroke-dasharray="26 14" marker-end="url(#ahb2)"/></g>
<defs><marker id="ahb2" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="{SKY}"/></marker></defs>
<text x="115" y="590" text-anchor="middle" font-family="Mont" font-weight="700" font-size="20" letter-spacing="4" fill="#ddd">HIMALAYA</text>
<text x="430" y="590" text-anchor="middle" font-family="Mont" font-weight="700" font-size="20" letter-spacing="4" fill="#ddd">INDO-GANGETIC KATORI</text><text x="940" y="40" text-anchor="end" font-family="Mont" font-weight="700" font-size="18" letter-spacing="3" fill="#C9A24A">SAMUDRA TAL SE OONCHAI</text>
<text x="820" y="590" text-anchor="middle" font-family="Mont" font-weight="700" font-size="20" letter-spacing="4" fill="#ddd">ARAVALI &middot; OONCHAI</text>
</svg></div>''')
TK = wt(3, "katori")
J.append(f'tl.fromTo("#arc", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:.45, ease:"power3.out"}}, {TK - .5:.2f}); tl.to("#arc", {{opacity:0, duration:.3}}, {S(4) - .1:.2f});'
         f'tl.set("#arc .plat", {{scaleY:.35, transformOrigin:"50% 100%"}}, 0); tl.set(["#arc .jp", "#arc .dl"], {{opacity:0}}, 0); tl.fromTo("#arc .smog", {{opacity:0, scale:.4, transformOrigin:"50% 80%"}}, {{opacity:1, scale:1, duration:.8, ease:"power2.out", immediateRender:false}}, {TK - .2:.2f});'
         f'tl.fromTo("#arc .dl", {{opacity:0, y:-60}}, {{opacity:1, y:0, duration:.5, ease:"bounce.out", immediateRender:false}}, {TK - .3:.2f}); tl.to("#arc .smog", {{scaleY:1.08, duration:.6, yoyo:true, repeat:3, transformOrigin:"50% 80%"}}, {TK + .6:.2f});'
         f'tl.to("#arc .plat", {{scaleY:1, duration:.7, ease:"back.out(1.6)"}}, {TK + .7:.2f}); tl.fromTo("#arc .jp", {{opacity:0, y:120}}, {{opacity:1, y:0, duration:.7, ease:"back.out(1.6)", immediateRender:false}}, {TK + .7:.2f});'
         f'tl.fromTo("#arc .jw", {{strokeDashoffset:0}}, {{strokeDashoffset:-120, duration:1.5, ease:"none", repeat:2, immediateRender:false}}, {TK + 1.3:.2f});')
sfx("whoosh", TK - .5, .3); sfx("riser", TK + .7, .25)

# ---------- 3 inversion lid (2D cross-section) ----------
chapter(4, 3, "HIGH PRESSURE KA DHAKKAN")
H.append(f'''<div id="inv"><svg viewBox="0 0 960 760" width="960" height="760">
<defs><linearGradient id="skyg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#25324d"/><stop offset="1" stop-color="#41506b"/></linearGradient>
<linearGradient id="lidg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E8964A" stop-opacity=".0"/><stop offset=".5" stop-color="#E8964A" stop-opacity=".85"/><stop offset="1" stop-color="#E8964A" stop-opacity=".0"/></linearGradient></defs>
<rect width="960" height="760" fill="url(#skyg)"/>
<rect class="cold" x="0" y="420" width="960" height="260" fill="#6FA8DC" opacity=".25"/>
<rect class="lid" x="0" y="340" width="960" height="110" fill="url(#lidg)"/>
<text class="lidt" x="480" y="402" text-anchor="middle" font-family="Mont" font-weight="700" font-size="30" letter-spacing="8" fill="#fff">GARAM HAWA KA DHAKKAN</text>
<text class="coldt" x="40" y="520" font-family="Mont" font-weight="700" font-size="24" letter-spacing="6" fill="#cfe6ff">THANDI HAWA</text>
<g class="hp"><circle cx="820" cy="150" r="70" fill="none" stroke="{GOLD}" stroke-width="4"/><text x="820" y="168" text-anchor="middle" font-family="Anton" font-size="56" fill="{GOLD}">H</text>
<path d="M820 230 L820 300" stroke="{GOLD}" stroke-width="5" marker-end="url(#ahg)"/><text x="820" y="60" text-anchor="middle" font-family="Mont" font-weight="700" font-size="22" letter-spacing="5" fill="{CREAM}">HIGH PRESSURE</text></g>
<defs><marker id="ahg" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="{GOLD}"/></marker></defs>
<rect x="0" y="680" width="960" height="80" fill="#2f281d"/>
''' + "".join(f'<rect x="{60 + i * 85}" y="{680 - h}" width="56" height="{h}" fill="#4a4237"/>' for i, h in enumerate([90, 140, 70, 180, 110, 160, 80, 130, 100, 150])) +
''.join(f'<circle class="sm" cx="{90 + (i * 61) % 820}" cy="660" r="{10 + i % 3 * 4}" fill="#b3ada3" opacity=".8"/>' for i in range(22)) +
'</svg></div>')
J.append(f'tl.fromTo("#inv", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:.45, ease:"power3.out"}}, {S(4) + .1:.2f}); tl.to("#inv", {{opacity:0, duration:.3}}, {S(5) - .1:.2f});'
         f'tl.fromTo("#inv .hp", {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:.4}}, {wt(4, "high") - .1:.2f}); tl.fromTo("#inv .cold, #inv .coldt", {{opacity:0}}, {{opacity:1, duration:.4}}, {wt(4, "thandi") - .1:.2f});'
         f'tl.fromTo(["#inv .lid", "#inv .lidt"], {{opacity:0, scaleX:.2, transformOrigin:"50% 50%"}}, {{opacity:1, scaleX:1, duration:.5, ease:"power3.out"}}, {wt(4, "dhakkan") - .1:.2f});')
for i in range(22):
    st = S(4) + .4 + (i % 7) * .18
    top = 455 + (i * 37) % 50
    J.append(f'tl.fromTo("#inv .sm:nth-of-type({i + 1})", {{attr:{{cy:660}}}}, {{attr:{{cy:{top}}}, duration:{1.2 + (i % 3) * .2:.2f}, ease:"power1.out", repeat:2, immediateRender:false}}, {st:.2f});')
sfx("whoosh", S(4) + .1, .3); sfx("impact-bass-1", wt(4, "dhakkan"), .35)

# ---------- 4 Aravalli + open land, Jaipur breathes ----------
chapter(5, 4, "ARAVALI &middot; OONCHAI &middot; KHULI HAWA")
rx, sc, x, y = jp_focus(55, 1.45)
plane(S(5) - .2, rx, sc, x, y, 1.1)
J.append(f'tl.fromTo(".arv", {{scaleY:0.001, rotationX:-90, transformOrigin:"50% 100%"}}, {{scaleY:1, rotationX:-90, duration:.45, stagger:.03, ease:"back.out(1.6)", immediateRender:false}}, {wt(5, "Aravali") - .1:.2f});')
bb("barv", wt(5, "Aravali") + .3, S(6))
J.append(f'tl.to(["#smog", "#bowl"], {{opacity:.3, duration:.5}}, {S(5):.2f}); tl.to(".fire", {{opacity:0, duration:.3}}, {S(5):.2f}); tl.to("#clean", {{opacity:1, attr:{{r:{U * 260:.0f}}}, duration:1}}, {wt(5, "hawa") - .2:.2f});')
for k in range(3):
    J.append(f'tl.to("#cw{k}", {{opacity:1, duration:.3}}, {wt(5, "hawa") - .2 + k * .12:.2f}); tl.fromTo("#cw{k}", {{strokeDashoffset:0}}, {{strokeDashoffset:-1.33, duration:2.4, ease:"none", repeat:2, immediateRender:false}}, {wt(5, "hawa") - .2:.2f}); tl.to("#cw{k}", {{opacity:0, duration:.3}}, {S(6):.2f});')
lux(5, "JAIPUR <b>~430 M</b> &nbsp;&middot;&nbsp; DELHI <b>~215 M</b>", wt(5, "430") - .1, wt(5, "hawa") - .1, 60, 1290)
lux(6, "<b>&#10004;</b> HAWA CHALTI RAHE &middot; JALDI SAAF", wt(5, "hawa") - .1, S(6), 60, 1290, "grn")
sfx("whoosh", wt(5, "hawa") - .2, .3)

# ---------- 5 honesty: Jaipur AQI also poor in winter ----------
plane(S(6) - .2, 48, 1.0, 0, 0, 1.0)
J.append(f'tl.to("#clean", {{opacity:.35, duration:.4}}, {S(6):.2f}); tl.to("#bdel", {{opacity:1, duration:.2}}, {S(6):.2f});')
H.append(f'<div id="aqi"><small>SARDIYON MEIN</small><div class="row"><div class="c j"><b>JAIPUR</b><span>KABHI KABHI &lsquo;POOR&rsquo;</span><i>dhool &middot; traffic</i></div><div class="c d"><b>DELHI</b><span>&lsquo;SEVERE&rsquo; TAK</span><i>har saal</i></div></div></div>')
J.append(f'tl.fromTo("#aqi", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.45, ease:"power3.out"}}, {wt(6, "AQI") - .2:.2f}); tl.fromTo("#aqi .d", {{opacity:0, x:40}}, {{opacity:1, x:0, duration:.4}}, {wt(6, "Delhi jitna") - .1:.2f}); tl.to("#aqi", {{opacity:0, duration:.3}}, {S(7) - .1:.2f});')

# ---------- 6 real estate ----------
rx, sc, x, y = jp_focus(50, 2.4)
plane(S(7) - .2, rx, sc, x, y, 1.0)
J.append(f'tl.to("#clean", {{opacity:1, attr:{{r:{U * 160:.0f}}}, duration:.8}}, {S(7):.2f}); tl.fromTo("#jring", {{attr:{{r:{U * 20:.0f}}}, opacity:1}}, {{attr:{{r:{U * 90:.0f}}}, opacity:0, duration:1, repeat:2, immediateRender:false}}, {S(7):.2f});')
H.append('<div id="re"><span>SAAF HAWA</span><b>+</b><span>BEHTAR LIVING</span><em>JAIPUR &#9650;</em></div>')
J.append(f'tl.fromTo("#re", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.45, ease:"power3.out"}}, {S(7) + .1:.2f}); tl.fromTo("#re em", {{opacity:0, scale:1.4}}, {{opacity:1, scale:1, duration:.4}}, {wt(7, "Jaipur") - .1:.2f}); tl.to("#re", {{opacity:0, duration:.3}}, {S(8) - .1:.2f});')
sfx("sparkle", wt(7, "Jaipur"), .3)

# ---------- 7 CTA ----------
H.append('<div id="cta"><b>KYA AAP BHI DELHI SE JAIPUR SHIFT HONE KA SOCH RAHE HO?</b><span>COMMENT KARO</span></div>')
J.append(f'tl.to("#dim", {{opacity:.5, duration:.3}}, {S(8):.2f}); tl.fromTo("#cta", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.45, ease:"power3.out"}}, {S(8):.2f}); tl.to("#cta span", {{scale:1.06, duration:.4, yoyo:true, repeat:3}}, {wt(8, "Comment"):.2f});')
sfx("sparkle", wt(8, "Comment"), .3)

# ---------- captions ----------
HI = ["gas chamber", "Jaipur", "chaar", "shift", "Reason two", "Reason three", "Reason four", "Number one", "north-west", "Punjab", "Haryana", "parali", "dhuaan", "Delhi", "Indo-Gangetic", "katori", "high pressure", "dhakkan", "Aravali", "oonchai", "430 meter", "215 meter",
      "khula ilaka", "jaldi saaf", "AQI", "dhool", "traffic", "Saaf hawa", "Comment"]
def hl(t):
    for h in sorted(HI, key=len, reverse=True):
        i = t.find(h)
        if i >= 0 and "<span" not in t[max(0, i - 25):i] and "span" not in t[i:i + len(h)]: t = t[:i] + '<span class="y">' + h + '</span>' + t[i + len(h):]
    return t
ci = 0
for n, ph in enumerate(PH):
    words = ph["t"].split(); chunks = []; cur = ""
    for w_ in words:
        if cur and len(cur) + 1 + len(w_) > 22: chunks.append(cur); cur = w_
        else: cur = (cur + " " + w_).strip()
    chunks.append(cur)
    tot_ = sum(len(c) for c in chunks); t = ph["s"]; nx = PH[n + 1]["s"] if n + 1 < len(PH) else END
    for j, c in enumerate(chunks):
        d = (ph["e"] - ph["s"]) * len(c) / tot_
        a_ = max(.02, t if j else t - .04); b_ = (min(t + d + .25, nx - .08) if j == len(chunks) - 1 else t + d - .03)
        H.append(f'<div class="cp" id="cp{ci}"><div>{hl(c)}</div></div>')
        J.append(f'tl.fromTo("#cp{ci}", {{opacity:0, scale:.88}}, {{opacity:1, scale:1, duration:.1}}, {a_:.2f}); tl.to("#cp{ci}", {{opacity:0, duration:.04}}, {b_ - .04:.2f});')
        t += d; ci += 1
if os.path.exists(f"{P}/assets/face.mp4"):
    H.append('<video id="face" class="clip" src="assets/face.mp4" data-start="0" data-duration="1.0" data-track-index="2" muted playsinline></video>')
    J.append('tl.set("#face", {opacity:1}, 0); tl.to("#face", {opacity:0, scale:1.06, duration:.12}, .8);')
H.append('<div id="cred">Wind, smoke &amp; inversion graphics are explanatory illustrations &middot; 3D terrain not to scale &middot; Imagery: NASA Blue Marble, Sentinel-2 (EOX)</div>')

CSS = """@font-face{font-family:Anton;src:url(assets/fonts/anton.woff2)}@font-face{font-family:Mont;font-weight:700;src:url(assets/fonts/mont700.woff2)}@font-face{font-family:Mont;font-weight:800;src:url(assets/fonts/mont800.woff2)}@font-face{font-family:Mont;font-weight:900;src:url(assets/fonts/mont900.woff2)}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#0d0b09}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif}.y{color:#111;background:#F2B23E;border-radius:6px;padding:0 6px}
#sky{position:absolute;inset:0;background:linear-gradient(180deg,#0b1730 0%,#22314f 22%,#6b5a4a 40%,#2a241c 58%)}
#stage{position:absolute;inset:0;perspective:1500px;perspective-origin:50% 26%;overflow:hidden}#plane{position:absolute;inset:0;transform-style:preserve-3d}
#world{position:absolute;left:-2160px;top:-3840px;width:5400px;height:9600px}
.mt{position:absolute;transform-origin:50% 100%;transform:rotateX(-90deg);background-size:100% 100%;background-repeat:no-repeat}.mh{background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' preserveAspectRatio='none'><defs><linearGradient id='g' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='%23fff'/><stop offset='.25' stop-color='%23e8eef5'/><stop offset='.38' stop-color='%237e8796'/><stop offset='1' stop-color='%232a2a2e'/></linearGradient></defs><polygon points='50,0 100,100 0,100' fill='url(%23g)'/><polygon points='50,0 100,100 50,100' fill='%23000' opacity='.22'/></svg>")}.ma{background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' preserveAspectRatio='none'><defs><linearGradient id='g' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='%23c49a62'/><stop offset='.25' stop-color='%23b08a58'/><stop offset='.38' stop-color='%238a6a42'/><stop offset='1' stop-color='%233a2c1c'/></linearGradient></defs><polygon points='50,0 100,100 0,100' fill='url(%23g)'/><polygon points='50,0 100,100 50,100' fill='%23000' opacity='.22'/></svg>")}
.bb{position:absolute;transform:translate(-50%,-100%) rotateX(-48deg);transform-origin:50% 100%;white-space:nowrap}
.bb span{display:inline-block;padding:8px 18px;border-radius:4px;background:linear-gradient(135deg,rgba(14,12,9,.94),rgba(34,27,18,.94));border:1.5px solid #C9A24A;color:#F3E6C8;font:700 34px Mont;letter-spacing:.14em}
.bb.red span{border-color:#E5484D;color:#FFB4B4}.bb.grn span{border-color:#3CE65A;color:#B8FFC6}.bb.org span{border-color:#FF8A00;color:#FFD3A0}.bb.wht span{border-color:#fff}.bb.gold span{color:#F7E3A8}
#dim{position:absolute;inset:0;background:#000;opacity:0;z-index:5;pointer-events:none}
#face{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:40}
#cred{position:absolute;left:40px;right:40px;top:1650px;text-align:center;font:700 17px Mont;color:rgba(255,255,255,.6);z-index:20}
#hook{position:absolute;left:50px;right:50px;top:150px;z-index:16;text-align:center;padding:24px 20px;border-radius:8px;border:1.5px solid #C9A24A;background:linear-gradient(135deg,rgba(14,12,9,.93),rgba(34,27,18,.93))}
#hook small{display:block;font:700 28px Mont;letter-spacing:.3em;color:#F3E6C8}#hook .vs{display:flex;align-items:center;justify-content:center;gap:26px;margin-top:14px}
#hook .vs b{display:block;font:400 92px/1 Anton}#hook .d b{color:#FF7A7A}#hook .j b{background:linear-gradient(180deg,#F7E3A8,#C9A24A);-webkit-background-clip:text;color:transparent}
#hook .vs span{display:block;margin-top:6px;font:700 22px Mont;letter-spacing:.2em;color:#F3E6C8}#hook i{font:300 44px Mont;color:#C9A24A;font-style:normal}
#hook em{display:inline-block;margin-top:16px;padding:8px 26px;border-radius:4px;background:#C9A24A;color:#111;font:400 46px/1 Anton;letter-spacing:.06em;font-style:normal}
.ch{position:absolute;left:50px;top:150px;opacity:0;z-index:15;display:flex;align-items:center;gap:18px;padding:14px 26px 14px 14px;border-radius:6px;border:1.5px solid #C9A24A;background:linear-gradient(135deg,rgba(14,12,9,.94),rgba(34,27,18,.94))}
.ch b{font:400 64px/1 Anton;background:linear-gradient(180deg,#F7E3A8,#C9A24A);-webkit-background-clip:text;color:transparent}.ch span{font:700 30px Mont;letter-spacing:.16em;color:#F3E6C8}
.lx{position:absolute;opacity:0;z-index:14;padding:16px 28px;border-radius:6px;background:linear-gradient(135deg,rgba(14,12,9,.93),rgba(34,27,18,.93));border:1.5px solid #C9A24A;color:#F3E6C8;font:700 30px/1.1 Mont;letter-spacing:.12em;box-shadow:0 18px 50px rgba(0,0,0,.55);white-space:nowrap}
.lx b{font:400 44px/1 Anton;letter-spacing:.04em;background:linear-gradient(180deg,#F7E3A8,#C9A24A);-webkit-background-clip:text;color:transparent}
.lx.red{border-color:#E5484D}.lx.red b{background:none;color:#FF7A7A}.lx.grn{border-color:#3CE65A}.lx.grn b{background:none;color:#3CE65A}
#inv{position:absolute;left:60px;top:300px;opacity:0;z-index:13;border-radius:8px;overflow:hidden;border:1.5px solid #C9A24A;box-shadow:0 30px 70px rgba(0,0,0,.7)}#inv svg{display:block}
#arc{position:absolute;left:60px;top:250px;opacity:0;z-index:13;border-radius:8px;overflow:hidden;border:1.5px solid #C9A24A;box-shadow:0 30px 70px rgba(0,0,0,.7)}#arc svg{display:block}
#aqi{position:absolute;left:60px;right:60px;top:360px;opacity:0;z-index:14;text-align:center;padding:26px;border-radius:8px;border:1.5px solid #C9A24A;background:linear-gradient(135deg,rgba(14,12,9,.95),rgba(34,27,18,.95))}
#aqi small{font:700 26px Mont;letter-spacing:.3em;color:#C9A24A}#aqi .row{display:flex;gap:20px;margin-top:18px}#aqi .c{flex:1;padding:18px;border-radius:6px;border:1.5px solid}
#aqi .j{border-color:#F2B23E}#aqi .d{border-color:#E5484D}#aqi b{display:block;font:400 64px/1 Anton;color:#F3E6C8}#aqi span{display:block;margin-top:8px;font:800 30px Mont}#aqi .j span{color:#F2B23E}#aqi .d span{color:#FF7A7A}
#aqi i{display:block;margin-top:6px;font:700 22px Mont;letter-spacing:.14em;color:#bbb;font-style:normal}
#re{position:absolute;left:0;right:0;top:300px;margin:0 auto;width:max-content;opacity:0;z-index:14;text-align:center;padding:24px 40px;border-radius:8px;border:1.5px solid #C9A24A;background:linear-gradient(135deg,rgba(14,12,9,.95),rgba(34,27,18,.95))}
#re span{display:block;font:400 64px/1.05 Anton;color:#F3E6C8}#re b{display:block;font:300 50px Mont;color:#C9A24A}#re em{display:inline-block;margin-top:14px;padding:8px 26px;border-radius:4px;background:#3CE65A;color:#0d0d0d;font:400 52px/1 Anton;font-style:normal}
#cta{position:absolute;left:60px;right:60px;top:420px;opacity:0;text-align:center;z-index:16}#cta b{display:block;padding:24px;border-radius:6px;background:linear-gradient(135deg,rgba(14,12,9,.95),rgba(34,27,18,.95));border:1.5px solid #C9A24A;color:#F3E6C8;font:400 76px/1.05 Anton}
#cta span{display:inline-block;margin-top:24px;padding:14px 34px;border-radius:4px;background:#C9A24A;color:#111;font:900 40px Mont;letter-spacing:.22em}
.cp{position:absolute;left:40px;right:40px;top:1440px;text-align:center;opacity:0;z-index:35}
.cp div{display:inline-block;padding:4px 20px 8px;border-radius:10px;background:#fff;font:900 60px/1.12 Mont;color:#111;box-shadow:0 8px 24px rgba(0,0,0,.45)}"""
audio = (f'<audio id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{END}" data-track-index="1" data-volume="1"></audio><audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.12" data-fade-out="1.5"></audio>' if VOICE
         else f'<audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.55" data-fade-out="1.5"></audio>')
open(f"{P}/index.html", "w").write(f"""<!doctype html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="30">
<svg width="0" height="0" style="position:absolute"><defs><linearGradient id="gh" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/><stop offset=".25" stop-color="#e8eef5"/><stop offset=".38" stop-color="#7e8796"/><stop offset="1" stop-color="#2a2a2e"/></linearGradient><linearGradient id="ga" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b08a58"/><stop offset="1" stop-color="#3a2c1c"/></linearGradient></defs></svg><div id="sky"></div><div id="stage"><div id="plane"><svg id="world" viewBox="{CX - 2.5 * CW:.0f} {CY - 2.5 * CH:.0f} {5 * CW:.0f} {5 * CH:.0f}" preserveAspectRatio="xMidYMid slice">{"".join(SVG)}</svg>{"".join(IN)}</div></div><div id="dim"></div>
{"".join(H)}
{audio}
{"".join(SFX)}
</div><script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(J)}
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>""")
print("END", END, [p["s"] for p in PH])
