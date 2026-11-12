"""Ram Jal Setu Link (ERCP) reel — 3D tilted map of eastern Rajasthan. River/canal lines are illustrative (not the official alignment)."""
import json, math, os, random
P = "proj"
LINES = [
    "Rajasthan ke 17 zilon ki pyaas bujhane wala project, aur iske saath aapke area ki zameen ka future bhi badal sakta hai. Naam hai Ram Jal Setu Link, purana naam ERCP.",
    "Plan yeh hai ki Chambal aur uski nadiyon, Parbati aur Kalisindh, ka extra paani barrages aur canals se poorvi Rajasthan tak pahunchaya jaaye.",
    "Jaipur, Ajmer, Tonk, Kota, Bundi, Baran, Jhalawar, Sawai Madhopur, Dausa, Karauli, Dholpur, Bharatpur, Deeg, Alwar, Khairthal-Tijara, Kotputli-Behror aur Beawar.",
    "Karib 3.25 crore logon ko peene ka paani, aur lagbhag 2.8 lakh hectare zameen ko sinchai.",
    "Real estate ka seedha funda hai, jahan paani, wahan growth. Paani aane se kheti, industry aur nayi colonies, teeno ko faayda hota hai, khaaskar un ilakon mein jahan aaj paani sabse badi dikkat hai.",
    "2024 mein Kendra, Rajasthan aur MP ke beech MoU hua. 90 percent paisa Kendra dega, aur DPR ke hisaab se lagat karib 91 hazaar crore hai.",
    "Par kaam abhi shuruaati daur mein hai. July 2026 tak sirf karib 4 percent paisa kharch hua hai.",
    "Aapke zile mein paani ki kya situation hai? Comment karo.",
]
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
END = round(E(7) + 1.0, 2)
def wp(lat, lon):
    n = 2 ** 13
    return (((lon + 180) / 360 * n) - 5791) * 256, (((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n) - 3466) * 256
SVG, H, J, SFX, IN = [], [], [], [], []
def sfx(n, t, v=.3): SFX.append(f'<audio id="sx{len(SFX)}" class="clip" src="assets/sfx/{n}.mp3" data-start="{t:.2f}" data-duration="2" data-track-index="{20 + len(SFX)}" data-volume="{v}"></audio>')
def pd(pts, close=False): return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + (" Z" if close else "")
def smooth(pts, n=8):
    out = []; P_ = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = P_[i - 1], P_[i], P_[i + 1], P_[i + 2]
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(tuple(.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    return out + [pts[-1]]
GOLD, CREAM, WATER, WATER2, GRN = "#C9A24A", "#F3E6C8", "#3FB4FF", "#9BE3FF", "#3CE65A"

CX, CY, CW = 9300, 2600, 29500
CH = CW * 1920 / 1080
VB = f"{CX - CW / 2:.0f} {CY - CH / 2:.0f} {CW:.0f} {CH:.0f}"
def scr(p): return ((p[0] - (CX - CW / 2)) / CW * 1080, (p[1] - (CY - CH / 2)) / CH * 1920)
U = CW / 1080

SVG.append('<rect x="-900000" y="-900000" width="2000000" height="2000000" style="fill:#1b1b1d"/>')
for href, x, y, w, h in [("bm4.jpg", -302848, -363008, 786432, 786432), ("bm5.jpg", -171776, -166400, 327680, 393216), ("bm7.webp", -40704, -35328, 81920, 65536)]:
    SVG.append(f'<image href="assets/img/{href}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="none"/>')
SVG.append('<rect x="-900000" y="-900000" width="2000000" height="2000000" style="fill:#000;opacity:.32"/>')
ST = json.load(open("data/states.json"))
def ring(rs): return " ".join(pd([wp(la, lo) for lo, la in r], True) for r in rs)
SVG.append(f'<path id="raj" d="{ring(ST["Rajasthan"])}" style="fill:{GOLD};fill-opacity:.0;stroke:{GOLD};stroke-width:4;vector-effect:non-scaling-stroke;opacity:.85"/>')
SVG.append(f'<path id="mp" d="{ring(ST["Madhya Pradesh"])}" style="fill:#fff;fill-opacity:.04;stroke:#bbb;stroke-width:2;stroke-dasharray:10 8;vector-effect:non-scaling-stroke;opacity:.6"/>')
SVG.append(f'<defs><filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{U * 4:.0f}" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
           f'<radialGradient id="dg"><stop offset="0" stop-color="{WATER}" stop-opacity=".6"/><stop offset="1" stop-color="{WATER}" stop-opacity="0"/></radialGradient></defs>')

# ---------- rivers (illustrative) ----------
RIV = {
    "chambal": [(24.45, 75.55), (24.70, 75.60), (24.95, 75.62), (25.18, 75.83), (25.50, 76.10), (25.78, 76.42), (26.05, 76.80), (26.35, 77.25), (26.62, 77.70), (26.70, 77.95), (26.55, 78.50)],
    "parbati": [(24.30, 77.10), (24.65, 76.95), (25.00, 76.80), (25.35, 76.70), (25.75, 76.55), (25.85, 76.50)],
    "kalisindh": [(24.10, 76.20), (24.40, 76.15), (24.65, 76.18), (24.95, 76.10), (25.25, 76.12), (25.48, 76.08)],
}
RP = {}
for k, pts in RIV.items():
    P_ = smooth([wp(*p) for p in pts], 8); RP[k] = P_
    SVG.append(f'<path class="rv" id="rv_{k}" d="{pd(P_)}" pathLength="1" style="fill:none;stroke:{WATER};stroke-width:18;stroke-opacity:.35;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>'
               f'<path class="rv" id="rc_{k}" d="{pd(P_)}" pathLength="1" style="fill:none;stroke:{WATER};stroke-width:7;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1;filter:url(#glow)"/>'
               f'<path class="fl" id="fl_{k}" d="{pd(P_)}" pathLength="1" style="fill:none;stroke:{WATER2};stroke-width:3;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:.03 .05;opacity:0"/>')
BARR = [wp(25.20, 76.05), wp(25.80, 76.50), wp(25.92, 75.45)]
for i, (x, y) in enumerate(BARR):
    SVG.append(f'<g class="bar" id="br{i}" style="opacity:0"><rect x="{x - U * 14:.0f}" y="{y - U * 14:.0f}" width="{U * 28:.0f}" height="{U * 28:.0f}" style="fill:{GOLD};stroke:#fff;stroke-width:3;vector-effect:non-scaling-stroke"/></g>')

# ---------- districts ----------
DIST = [("Jaipur", 26.91, 75.79), ("Ajmer", 26.45, 74.64), ("Tonk", 26.17, 75.79), ("Kota", 25.18, 75.83), ("Bundi", 25.44, 75.64), ("Baran", 25.10, 76.51),
        ("Jhalawar", 24.60, 76.16), ("Sawai Madhopur", 26.02, 76.35), ("Dausa", 26.89, 76.34), ("Karauli", 26.50, 77.02), ("Dholpur", 26.70, 77.89), ("Bharatpur", 27.22, 77.49),
        ("Deeg", 27.47, 77.33), ("Alwar", 27.55, 76.61), ("Khairthal-Tijara", 27.80, 76.64), ("Kotputli-Behror", 27.70, 76.20), ("Beawar", 26.10, 74.32)]
DP = {nm: wp(la, lo) for nm, la, lo in DIST}
# canals (illustrative): from barrages fan out to districts
SRC = {"Jaipur": 2, "Ajmer": 2, "Tonk": 2, "Beawar": 2, "Kota": 0, "Bundi": 0, "Baran": 0, "Jhalawar": 0, "Sawai Madhopur": 1, "Dausa": 1, "Karauli": 1,
       "Dholpur": 1, "Bharatpur": 1, "Deeg": 1, "Alwar": 1, "Khairthal-Tijara": 1, "Kotputli-Behror": 1}
CAN = {}
for i, (nm, la, lo) in enumerate(DIST):
    a = BARR[SRC[nm]]; b = DP[nm]
    if math.hypot(b[0] - a[0], b[1] - a[1]) < U * 30: continue
    m = ((a[0] + b[0]) / 2 + (b[1] - a[1]) * .12, (a[1] + b[1]) / 2 - (b[0] - a[0]) * .12)
    d = f"M{a[0]:.0f} {a[1]:.0f} Q{m[0]:.0f} {m[1]:.0f} {b[0]:.0f} {b[1]:.0f}"; CAN[nm] = (a, m, b)
    SVG.append(f'<path class="cn" id="cn{i}" d="{d}" pathLength="1" style="fill:none;stroke:{WATER};stroke-width:5;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1;opacity:.9"/>'
               f'<path class="cf" id="cf{i}" d="{d}" pathLength="1" style="fill:none;stroke:#fff;stroke-width:3;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:.04 .08;opacity:0"/>')
for i, (nm, la, lo) in enumerate(DIST):
    x, y = DP[nm]
    SVG.append(f'<g class="dt" id="dt{i}" style="opacity:0"><circle class="dgl" cx="{x:.0f}" cy="{y:.0f}" r="{U * 46:.0f}" style="fill:url(#dg)"/><circle cx="{x:.0f}" cy="{y:.0f}" r="{U * 11:.0f}" style="fill:{WATER2};stroke:#fff;stroke-width:3;vector-effect:non-scaling-stroke"/></g>')
# green growth halos (real estate)
for i, (nm, la, lo) in enumerate(DIST):
    x, y = DP[nm]
    SVG.append(f'<circle class="gh" id="gh{i}" cx="{x:.0f}" cy="{y:.0f}" r="{U * 70:.0f}" style="fill:{GRN};fill-opacity:.18;stroke:{GRN};stroke-width:3;vector-effect:non-scaling-stroke;opacity:0"/>')

# billboard labels in the plane
def pin(i, p, text, cls=""):
    x, y = scr(p); IN.append(f'<div class="bb {cls}" id="{i}" style="left:{x:.0f}px;top:{y - 18:.0f}px"><span>{text}</span></div>')
for i, (nm, la, lo) in enumerate(DIST): pin(f"dl{i}", DP[nm], nm.upper(), "sm")
pin("lchm", wp(25.95, 76.95), "CHAMBAL", "blue"); pin("lpar", wp(24.75, 76.95), "PARBATI", "blue"); pin("lkal", wp(24.55, 76.20), "KALISINDH", "blue")
pin("lmp", wp(24.30, 77.60), "MADHYA PRADESH", "wht"); pin("lraj", wp(27.70, 74.55), "RAJASTHAN", "gold")
# 3D water towers rising in districts (real-estate beat) — standing elements
for i, (nm, la, lo) in enumerate(DIST):
    x, y = scr(DP[nm]); h = random.Random(i).uniform(55, 95)
    IN.append(f'<div class="tw" id="tw{i}" style="left:{x - 9:.0f}px;top:{y - h:.0f}px;width:18px;height:{h:.0f}px"></div>')

def lux(i, html, t, until, x, y, cls=""):
    H.append(f'<div class="lx {cls}" id="lx{i}" style="left:{x}px;top:{y}px">{html}</div>')
    J.append(f'tl.fromTo("#lx{i}", {{opacity:0, y:24, clipPath:"inset(0 100% 0 0)"}}, {{opacity:1, y:0, clipPath:"inset(0 0% 0 0)", duration:.45, ease:"power3.out"}}, {t:.2f}); tl.to("#lx{i}", {{opacity:0, y:-14, duration:.3}}, {until - .3:.2f});')
    sfx("click-soft", t, .3)
def bb(i, t, until):
    J.append(f'tl.fromTo("#{i}", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)", immediateRender:false}}, {t:.2f}); tl.to("#{i}", {{opacity:0, duration:.25}}, {until - .25:.2f});')
def plane(t, rx, sc, x, y, d=1.0):
    J.append(f'tl.to("#plane", {{rotationX:{rx}, scale:{sc}, x:{x}, y:{y}, duration:{d}, ease:"power2.inOut"}}, {t:.2f});')
def focus(p, rx, sc, ty=1060):
    x, y = scr(p); return rx, sc, (540 - x) * sc, (ty - y) * sc
def draw(sel, t, d=1.0): J.append(f'tl.to("{sel}", {{strokeDashoffset:0, duration:{d}, ease:"power2.inOut"}}, {t:.2f});')

J.append('tl.set("#plane", {rotationX:44, scale:1.0, x:0, y:0, transformOrigin:"50% 55%"}, 0); tl.set(".bb", {opacity:0, xPercent:-50, yPercent:-100, rotationX:-44, transformOrigin:"50% 100%"}, 0); tl.set(".tw", {scaleY:0.001, rotationX:-90, transformOrigin:"50% 100%"}, 0);')

# ---------- 0 HOOK ----------
J.append('tl.fromTo("#plane", {rotationX:20, scale:.8}, {rotationX:44, scale:1.0, duration:1.6, ease:"power3.out"}, 0);')
J.append(f'tl.to("#raj", {{fillOpacity:.12, duration:.6}}, .2); tl.to("#raj", {{fillOpacity:.04, duration:.6}}, 1.4);')
bb("lraj", .3, S(1)); bb("lmp", .5, S(2))
for k in RIV: draw(f"#rv_{k}, #rc_{k}", .3, 1.3)
for i in range(len(DIST)):
    t = .9 + i * .07
    J.append(f'tl.to("#dt{i}", {{opacity:1, duration:.2}}, {t:.2f}); tl.fromTo("#dt{i} .dgl", {{attr:{{r:{U * 10:.0f}}}}}, {{attr:{{r:{U * 46:.0f}}}, duration:.5, immediateRender:false}}, {t:.2f}); tl.to("#dt{i}", {{opacity:.35, duration:.3}}, {S(1) - .2:.2f});')
sfx("riser", .9, .3)
H.append('<div id="hook"><small>17 ZILE &middot; 3.25 CRORE LOG</small><b>RAM JAL SETU</b><span>purana naam <i>ERCP</i></span></div>')
J.append(f'tl.fromTo("#hook", {{opacity:0, scale:1.12}}, {{opacity:1, scale:1, duration:.45, ease:"power3.out"}}, 0); tl.fromTo("#hook span", {{opacity:0, y:16}}, {{opacity:1, y:0, duration:.35}}, {wt(0, "Naam") - .1:.2f}); tl.to("#hook", {{opacity:0, y:-30, duration:.3}}, {S(1) - .2:.2f});')
lux(0, "ZAMEEN KA <b>FUTURE</b> &#9650;", wt(0, "zameen") - .1, wt(0, "Naam") - .1, 270, 1270, "grn")
sfx("impact-bass-1", 0, .45); sfx("impact-bass-1", wt(0, "Ram Jal"), .35)

# ---------- 1 rivers -> barrages -> canals ----------
rx, sc, x, y = focus(wp(25.4, 76.3), 50, 1.35, 1000)
plane(S(1) - .2, rx, sc, x, y, 1.1)
for k, w in [("chambal", "Chambal"), ("parbati", "Parbati"), ("kalisindh", "Kalisindh")]:
    t = wt(1, w) - .1
    J.append(f'tl.fromTo("#rc_{k}", {{strokeWidth:7}}, {{strokeWidth:16, duration:.35, yoyo:true, repeat:1, immediateRender:false}}, {t:.2f}); tl.set("#fl_{k}", {{opacity:1}}, {t:.2f}); tl.fromTo("#fl_{k}", {{strokeDashoffset:0}}, {{strokeDashoffset:-2, duration:4, ease:"none", repeat:6, immediateRender:false}}, {t:.2f});')
    bb({"chambal": "lchm", "parbati": "lpar", "kalisindh": "lkal"}[k], t, S(2) + .2); sfx("pop", t, .3)
for i in range(len(BARR)):
    t = wt(1, "barrages") - .1 + i * .15
    J.append(f'tl.fromTo("#br{i}", {{opacity:0, scale:3, svgOrigin:"{BARR[i][0]:.0f} {BARR[i][1]:.0f}"}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2.5)", immediateRender:false}}, {t:.2f});'); sfx("click-soft", t, .3)
lux(1, "EXTRA PAANI &rarr; <b>BARRAGE</b> &rarr; <b>CANAL</b>", wt(1, "extra") - .1, S(2), 60, 1270)
for i, (nm, la, lo) in enumerate(DIST):
    if nm not in CAN: continue
    t = wt(1, "canals") - .1 + (i % 6) * .08
    draw(f"#cn{i}", t, 1.3)
    J.append(f'tl.set("#cf{i}", {{opacity:.9}}, {t + 1.0:.2f}); tl.fromTo("#cf{i}", {{strokeDashoffset:0}}, {{strokeDashoffset:-1.2, duration:2.2, ease:"none", repeat:8, immediateRender:false}}, {t + 1.0:.2f});')
sfx("whoosh", wt(1, "canals") - .1, .35)

# ---------- 2 districts light up ----------
plane(S(2) - .3, 46, 1.0, 0, 40, 1.0)
for i, (nm, la, lo) in enumerate(DIST):
    t = wt(2, nm.split("-")[0]) - .08
    J.append(f'tl.to("#dt{i}", {{opacity:1, duration:.15}}, {t:.2f}); tl.fromTo("#dt{i} .dgl", {{attr:{{r:{U * 15:.0f}}}}}, {{attr:{{r:{U * 60:.0f}}}, duration:.45, ease:"power3.out", immediateRender:false}}, {t:.2f});')
    bb(f"dl{i}", t, S(4) - .1); sfx("click-soft", t, .18)
lux(2, "<b>17</b> ZILE", S(2) + .1, S(3), 60, 300)

# ---------- 3 numbers ----------
H.append('<div id="nums"><div class="n1"><b>3.25 CRORE</b><span>LOG &middot; PEENE KA PAANI</span></div><div class="n2"><b>2.8 LAKH HA</b><span>ZAMEEN &middot; SINCHAI</span></div></div>')
J.append(f'tl.to("#dim", {{opacity:.35, duration:.3}}, {S(3) - .1:.2f}); tl.fromTo("#nums .n1", {{opacity:0, y:40, scale:.9}}, {{opacity:1, y:0, scale:1, duration:.45, ease:"power3.out"}}, {wt(3, "3.25") - .15:.2f}); tl.fromTo("#nums .n2", {{opacity:0, y:40, scale:.9}}, {{opacity:1, y:0, scale:1, duration:.45, ease:"power3.out"}}, {wt(3, "2.8") - .15:.2f}); tl.to("#nums > div", {{opacity:0, duration:.3}}, {S(4) - .2:.2f}); tl.to("#dim", {{opacity:0, duration:.3}}, {S(4) - .1:.2f});')
J.append(f'tl.set("#nums", {{opacity:1}}, 0);')
sfx("impact-bass-1", wt(3, "3.25") - .1, .35); sfx("impact-bass-1", wt(3, "2.8") - .1, .3)
H.append('<div id="drops">' + "".join(f'<i style="left:{80 + (k * 97) % 920}px"></i>' for k in range(12)) + '</div>')
J.append(f'tl.set("#drops", {{opacity:1}}, {S(3):.2f}); tl.fromTo("#drops i", {{y:-80, opacity:0}}, {{y:1500, opacity:1, duration:1.4, stagger:{{each:.12, repeat:1}}, ease:"power1.in", immediateRender:false}}, {S(3):.2f}); tl.to("#drops", {{opacity:0, duration:.3}}, {S(4) - .2:.2f});')

# ---------- 4 real estate: jahan paani wahan growth ----------
plane(S(4) - .2, 56, 1.15, 0, 120, 1.0)
for i in range(len(DIST)):
    t = S(4) + .3 + i * .06
    J.append(f'tl.fromTo("#gh{i}", {{opacity:0, attr:{{r:{U * 20:.0f}}}}}, {{opacity:1, attr:{{r:{U * 70:.0f}}}, duration:.5, ease:"power3.out", immediateRender:false}}, {t:.2f}); tl.to("#gh{i}", {{opacity:0, duration:.3}}, {S(5) - .1:.2f});')
J.append(f'tl.fromTo(".tw", {{scaleY:0.001, rotationX:-90, transformOrigin:"50% 100%"}}, {{scaleY:1, rotationX:-90, duration:.4, stagger:.05, ease:"back.out(1.8)", immediateRender:false}}, {wt(4, "growth") - .3:.2f}); tl.to(".tw", {{scaleY:0.001, rotationX:-90, duration:.3}}, {S(5) - .1:.2f});')
H.append('<div id="growth"><span>JAHAN PAANI</span><i>&rarr;</i><b>WAHAN GROWTH</b></div>')
J.append(f'tl.fromTo("#growth", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.45, ease:"power3.out"}}, {wt(4, "jahan") - .1:.2f}); tl.fromTo("#growth b", {{opacity:0, x:40}}, {{opacity:1, x:0, duration:.4}}, {wt(4, "wahan") - .1:.2f}); tl.to("#growth", {{opacity:0, duration:.3}}, {S(5) - .1:.2f});')
for k, (w, txt) in enumerate([("kheti", "KHETI"), ("industry", "INDUSTRY"), ("colonies", "NAYI COLONIES")]):
    lux(10 + k, f"<b>&#9670;</b> {txt}", wt(4, w) - .1, S(5), 60 + k * 0, 1130 + k * 85, "grn")
sfx("riser", wt(4, "growth") - .3, .3)

# ---------- 5 MoU + money ----------
H.append('<div id="mou"><small>MoU &middot; 2024</small><div class="seals"><span>KENDRA</span><span>RAJASTHAN</span><span>MP</span></div>'
         '<div class="bar"><div class="k"><b>90%</b> KENDRA</div><div class="r">10%</div></div><div class="cost"><b>~&#8377;91,000 CR</b><span>DPR LAGAT</span></div></div>')
J.append(f'tl.to("#dim", {{opacity:.45, duration:.3}}, {S(5) - .1:.2f}); tl.fromTo("#mou", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:.45, ease:"power3.out"}}, {S(5):.2f});'
         f'tl.fromTo("#mou .seals span", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.3, stagger:.15, ease:"back.out(2)"}}, {wt(5, "Kendra") - .1:.2f});'
         f'tl.set("#mou .bar .k", {{width:"0%"}}, 0); tl.set("#mou .cost", {{opacity:0}}, 0); tl.fromTo("#mou .bar .k", {{width:"0%"}}, {{width:"90%", duration:.8, ease:"power3.out", immediateRender:false}}, {wt(5, "90") - .1:.2f}); tl.fromTo("#mou .cost", {{opacity:0, y:20}}, {{opacity:1, y:0, duration:.4, immediateRender:false}}, {wt(5, "lagat") - .1:.2f}); tl.to("#mou", {{opacity:0, duration:.3}}, {S(6) - .1:.2f});')
sfx("click-soft", wt(5, "Kendra") - .1, .35); sfx("impact-bass-1", wt(5, "91"), .35)

# ---------- 6 status ----------
H.append('<div id="stat"><small>ZAMEEN PAR KAAM</small><div class="track"><div class="fill"></div><em>~4%</em></div><span>July 2026 tak kharch &middot; Vidhan Sabha data</span><i>SHURUAATI DAUR</i></div>')
J.append(f'tl.fromTo("#stat", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:.45, ease:"power3.out"}}, {S(6):.2f}); tl.fromTo("#stat .fill", {{width:"0%"}}, {{width:"4%", duration:1.0, ease:"power2.out", immediateRender:false}}, {wt(6, "4 percent") - .3:.2f}); tl.fromTo("#stat em", {{opacity:0}}, {{opacity:1, duration:.3, immediateRender:false}}, {wt(6, "4 percent") - .1:.2f}); tl.set("#stat em", {{opacity:0}}, 0); tl.set("#stat .fill", {{width:"0%"}}, 0); tl.to("#stat", {{opacity:0, duration:.3}}, {S(7) - .1:.2f});')
sfx("click-soft", wt(6, "4 percent"), .4)

# ---------- 7 CTA ----------
H.append('<div id="cta"><b>AAPKE ZILE MEIN PAANI KI KYA SITUATION HAI?</b><span>COMMENT KARO</span></div>')
J.append(f'tl.to("#dim", {{opacity:.5, duration:.3}}, {S(7):.2f}); tl.fromTo("#cta", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.45, ease:"power3.out"}}, {S(7):.2f}); tl.to("#cta span", {{scale:1.06, duration:.4, yoyo:true, repeat:3}}, {wt(7, "Comment"):.2f});')
sfx("sparkle", wt(7, "Comment"), .3)

# ---------- captions ----------
HI = ["17 zilon", "Ram Jal Setu Link", "ERCP", "Chambal", "Parbati", "Kalisindh", "barrages", "canals", "3.25 crore", "2.8 lakh hectare", "jahan paani, wahan growth", "kheti", "industry", "nayi colonies",
      "MoU", "90 percent", "91 hazaar crore", "4 percent", "Comment"]
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
    J.append('tl.set("#face", {opacity:1}, 0); tl.to("#face", {opacity:0, scale:1.06, duration:.12}, .85);')
H.append('<div id="cred">River &amp; canal lines illustrative, not official alignment &middot; Sources: Rajasthan Vidhan Sabha data (Aug 2026), Patrika, HT &middot; Imagery: NASA Blue Marble, Sentinel-2 (EOX)</div>')

CSS = """@font-face{font-family:Anton;src:url(assets/fonts/anton.woff2)}@font-face{font-family:Mont;font-weight:700;src:url(assets/fonts/mont700.woff2)}@font-face{font-family:Mont;font-weight:800;src:url(assets/fonts/mont800.woff2)}@font-face{font-family:Mont;font-weight:900;src:url(assets/fonts/mont900.woff2)}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#0d0b09}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif}.y{color:#111;background:#F2B23E;border-radius:6px;padding:0 6px}
#sky{position:absolute;inset:0;background:linear-gradient(180deg,#081428 0%,#16294a 22%,#3d4a5c 40%,#1d1a15 58%)}
#stage{position:absolute;inset:0;perspective:1500px;perspective-origin:50% 26%;overflow:hidden}#plane{position:absolute;inset:0;transform-style:preserve-3d}
#world{position:absolute;left:-2160px;top:-3840px;width:5400px;height:9600px}
.bb{position:absolute;white-space:nowrap}
.bb span{display:inline-block;padding:6px 14px;border-radius:4px;background:linear-gradient(135deg,rgba(14,12,9,.94),rgba(34,27,18,.94));border:1.5px solid #C9A24A;color:#F3E6C8;font:700 30px Mont;letter-spacing:.12em}
.bb.sm span{font-size:24px;padding:4px 10px;border-color:#3FB4FF;color:#D6F1FF}.bb.blue span{border-color:#3FB4FF;color:#9BE3FF}.bb.wht span{border-color:#bbb;color:#ddd}.bb.gold span{color:#F7E3A8;font-size:36px}
.tw{position:absolute;transform-origin:50% 100%;transform:rotateX(-90deg);background:linear-gradient(90deg,#2a8fd8,#9BE3FF 50%,#2a8fd8);border-radius:4px 4px 0 0;box-shadow:0 0 18px rgba(63,180,255,.7)}
#dim{position:absolute;inset:0;background:#000;opacity:0;z-index:5;pointer-events:none}
#face{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:40}
#cred{position:absolute;left:40px;right:40px;top:1650px;text-align:center;font:700 17px Mont;color:rgba(255,255,255,.6);z-index:20}
#hook{position:absolute;left:60px;right:60px;top:140px;z-index:16;text-align:center;padding:24px 20px;border-radius:8px;border:1.5px solid #C9A24A;background:linear-gradient(135deg,rgba(14,12,9,.93),rgba(34,27,18,.93))}
#hook small{display:block;font:700 28px Mont;letter-spacing:.26em;color:#9BE3FF}#hook b{display:block;margin-top:10px;font:400 118px/1 Anton;background:linear-gradient(180deg,#F7E3A8,#C9A24A);-webkit-background-clip:text;color:transparent;letter-spacing:.02em}
#hook span{display:inline-block;margin-top:10px;font:700 30px Mont;letter-spacing:.14em;color:#F3E6C8}#hook span i{font-style:normal;padding:2px 12px;border-radius:4px;background:#3FB4FF;color:#06121f;font-weight:900}
.lx{position:absolute;opacity:0;z-index:14;padding:16px 28px;border-radius:6px;background:linear-gradient(135deg,rgba(14,12,9,.93),rgba(34,27,18,.93));border:1.5px solid #C9A24A;color:#F3E6C8;font:700 30px/1.1 Mont;letter-spacing:.12em;box-shadow:0 18px 50px rgba(0,0,0,.55);white-space:nowrap}
.lx b{font:400 44px/1 Anton;letter-spacing:.04em;background:linear-gradient(180deg,#F7E3A8,#C9A24A);-webkit-background-clip:text;color:transparent}
.lx.grn{border-color:#3CE65A}.lx.grn b{background:none;color:#3CE65A}
#nums{position:absolute;left:60px;right:60px;top:330px;z-index:14;display:flex;flex-direction:column;gap:26px;opacity:0}
#nums > div{padding:26px 30px;border-radius:8px;border:1.5px solid #3FB4FF;background:linear-gradient(135deg,rgba(8,18,30,.95),rgba(14,30,46,.95));text-align:center;opacity:0}
#nums b{display:block;font:400 120px/1 Anton;background:linear-gradient(180deg,#E6F7FF,#3FB4FF);-webkit-background-clip:text;color:transparent}#nums span{display:block;margin-top:10px;font:700 30px Mont;letter-spacing:.2em;color:#F3E6C8}
#nums .n2{border-color:#3CE65A}#nums .n2 b{background:linear-gradient(180deg,#E8FFEE,#3CE65A);-webkit-background-clip:text}
#drops{position:absolute;inset:0;z-index:13;opacity:0;pointer-events:none}#drops i{position:absolute;top:0;width:18px;height:28px;border-radius:50% 50% 50% 50%/60% 60% 40% 40%;background:linear-gradient(180deg,#E6F7FF,#3FB4FF);opacity:0}
#growth{position:absolute;left:0;right:0;top:250px;margin:0 auto;width:max-content;opacity:0;z-index:14;display:flex;align-items:center;gap:22px;padding:22px 34px;border-radius:8px;border:1.5px solid #C9A24A;background:linear-gradient(135deg,rgba(14,12,9,.95),rgba(34,27,18,.95))}
#growth span{font:400 64px/1 Anton;color:#9BE3FF}#growth i{font:300 60px Mont;color:#C9A24A;font-style:normal}#growth b{font:400 64px/1 Anton;color:#3CE65A}
#mou{position:absolute;left:60px;right:60px;top:330px;opacity:0;z-index:14;padding:30px;border-radius:8px;border:1.5px solid #C9A24A;background:linear-gradient(135deg,rgba(14,12,9,.96),rgba(34,27,18,.96));text-align:center}
#mou small{font:700 28px Mont;letter-spacing:.3em;color:#C9A24A}#mou .seals{display:flex;justify-content:center;gap:16px;margin-top:20px}#mou .seals span{padding:14px 20px;border-radius:4px;border:1.5px solid #F3E6C8;font:400 44px/1 Anton;color:#F3E6C8}
#mou .bar{position:relative;display:flex;margin-top:30px;height:70px;border-radius:4px;overflow:hidden;background:#3a2f22}#mou .bar .k{display:flex;align-items:center;justify-content:center;gap:12px;background:linear-gradient(90deg,#C9A24A,#F7E3A8);color:#111;font:800 30px Mont;letter-spacing:.14em;white-space:nowrap;overflow:hidden}
#mou .bar .k b{font:400 48px Anton}#mou .bar .r{flex:1;display:flex;align-items:center;justify-content:center;font:800 26px Mont;color:#F3E6C8}
#mou .cost{margin-top:28px}#mou .cost b{display:block;font:400 110px/1 Anton;background:linear-gradient(180deg,#F7E3A8,#C9A24A);-webkit-background-clip:text;color:transparent}#mou .cost span{font:700 26px Mont;letter-spacing:.3em;color:#F3E6C8}
#stat{position:absolute;left:60px;right:60px;top:380px;opacity:0;z-index:14;padding:34px;border-radius:8px;border:1.5px solid #C9A24A;background:linear-gradient(135deg,rgba(14,12,9,.96),rgba(34,27,18,.96));text-align:center}
#stat small{font:700 28px Mont;letter-spacing:.3em;color:#C9A24A}#stat .track{position:relative;margin-top:26px;height:70px;border-radius:4px;background:#2a241c;border:1.5px solid #5a4a33}
#stat .fill{position:absolute;left:0;top:0;bottom:0;background:linear-gradient(90deg,#3FB4FF,#9BE3FF);box-shadow:0 0 20px #3FB4FF}#stat em{position:absolute;left:7%;top:50%;transform:translateY(-50%);font:400 64px/1 Anton;color:#9BE3FF;font-style:normal}
#stat span{display:block;margin-top:18px;font:700 26px Mont;color:#ccc;letter-spacing:.06em}#stat i{display:inline-block;margin-top:16px;padding:8px 24px;border-radius:4px;border:1.5px solid #E5484D;color:#FF8A8A;font:400 44px/1 Anton;font-style:normal;letter-spacing:.04em}
#cta{position:absolute;left:60px;right:60px;top:420px;opacity:0;text-align:center;z-index:16}#cta b{display:block;padding:24px;border-radius:6px;background:linear-gradient(135deg,rgba(14,12,9,.95),rgba(34,27,18,.95));border:1.5px solid #C9A24A;color:#F3E6C8;font:400 76px/1.05 Anton}
#cta span{display:inline-block;margin-top:24px;padding:14px 34px;border-radius:4px;background:#C9A24A;color:#111;font:900 40px Mont;letter-spacing:.22em}
.cp{position:absolute;left:40px;right:40px;top:1440px;text-align:center;opacity:0;z-index:35}
.cp div{display:inline-block;padding:4px 20px 8px;border-radius:10px;background:#fff;font:900 60px/1.12 Mont;color:#111;box-shadow:0 8px 24px rgba(0,0,0,.45)}"""
audio = (f'<audio id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{END}" data-track-index="1" data-volume="1"></audio><audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.12" data-fade-out="1.5"></audio>' if VOICE
         else f'<audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.55" data-fade-out="1.5"></audio>')
open(f"{P}/index.html", "w").write(f"""<!doctype html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="30">
<div id="sky"></div><div id="stage"><div id="plane"><svg id="world" viewBox="{CX - 2.5 * CW:.0f} {CY - 2.5 * CH:.0f} {5 * CW:.0f} {5 * CH:.0f}" preserveAspectRatio="xMidYMid slice">{"".join(SVG)}</svg>{"".join(IN)}</div></div><div id="dim"></div>
{"".join(H)}
{audio}
{"".join(SFX)}
</div><script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(J)}
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>""")
print("END", END, [p["s"] for p in PH])
