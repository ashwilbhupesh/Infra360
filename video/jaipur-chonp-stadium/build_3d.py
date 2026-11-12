"""Jaipur (Chonp) cricket stadium reel — Digital Banjaaraa. Text+music draft; uses rec/phrases.json when the voice arrives.
World = z13 web-mercator px from tile (5791, 3466) (same frame as the Ajmer episode, so India/Rajasthan layers line up)."""
import json, math, os
P = "proj"
ASP = json.load(open("aspects.json"))
LINES = [
    "Jaipur mein ban raha hai duniya ka teesra sabse bada cricket stadium, Anil Agarwal International Cricket Stadium.",
    "2023 mein Vedanta aur RCA ke beech MoU hua, aur Vedanta ne 300 crore dene ka vaada kiya.",
    "Duniya mein isse bade sirf do hain: Ahmedabad ka Narendra Modi Stadium, aur Melbourne Cricket Ground.",
    "Yeh ban raha hai Chonp mein, Delhi Road par, shehar se karib 25 km door, 100 acre mein. Delhi highway seedha jodta hai.",
    "Yahan IPL, international matches, bade concerts aur events honge. Aur saath mein aas paas hotels, restaurants, cafe, aur zameen ki demand badhegi.",
    "Par abhi kaam ruka hua hai. 2022 mein neev rakhi gayi, karib 191 crore kharch hue, phir kaam ruk gaya.",
    "Ab IIT Bombay jaanch kar rahi hai. Aapko kya lagta hai, kab tak banega? Comment karo.",
]
VOICE = os.path.exists("rec/phrases.json")
if VOICE: PH = json.load(open("rec/phrases.json"))
else:
    PH = []; t = .3
    for l in LINES:
        d = len(l) / 15 + .2; PH.append({"s": round(t, 2), "e": round(t + d, 2), "t": l}); t += d + .35
def S(k): return PH[k]["s"]
def E(k): return PH[k]["e"]
def wt(k, w):
    t = PH[k]["t"]; i = t.lower().find(w.lower()); assert i >= 0, (k, w)
    return S(k) + (E(k) - S(k)) * i / len(t)
END = round(E(6) + 1.3, 2)
def wp(lat, lon):
    n = 2 ** 13
    return (((lon + 180) / 360 * n) - 5791) * 256, (((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n) - 3466) * 256
SVG, H, J, SFX, CARDS = [], [], [], [], []
def vb(c, w): h = w * 1920 / 1080; return f"{c[0] - w / 2:.1f} {c[1] - h / 2:.1f} {w:.1f} {h:.1f}"
def sfx(n, t, v=.3): SFX.append(f'<audio id="sx{len(SFX)}" class="clip" src="assets/sfx/{n}.mp3" data-start="{t:.2f}" data-duration="2" data-track-index="{20 + len(SFX)}" data-volume="{v}"></audio>')
GOLD, PINK, CYAN, GRN, ORG = "#FFC42E", "#FF4FA3", "#3CDCFF", "#3CFF96", "#FF8A00"
CAMS = []
def cam(t, c, w, d=.9, e="power2.inOut"):
    J.append(f'tl.to("#world", {{attr:{{viewBox:"{vb(c, w)}"}}, duration:{d}, ease:"{e}"}}, {t:.2f});'); CAMS.append((t, d, c, w))
def scr(p, t):
    c, w = CAMS[0][2], CAMS[0][3]
    for t0, d, c1, w1 in sorted(CAMS, key=lambda q: q[0]):
        if t0 + d <= t + 1e-6: c, w = c1, w1
    h = w * 1920 / 1080
    return ((p[0] - (c[0] - w / 2)) / w * 1080, (p[1] - (c[1] - h / 2)) / h * 1920)
def pd(pts): return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)

# ---------- base ----------
BD = json.load(open("data/bounds.json"))
def pdr(rings): return " ".join("M" + " L".join(f"{wp(la, lo)[0]:.1f} {wp(la, lo)[1]:.1f}" for lo, la in r) + " Z" for r in rings)
def bbw(rings):
    pts = [wp(la, lo) for r in rings for lo, la in r]; xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)
def fitb(bb, top, bot, pad=1.12):
    x0, y0, x1, y1 = bb; w = max((x1 - x0) * pad, (y1 - y0) * pad * 1080 / (bot - top))
    return ((x0 + x1) / 2, (y0 + y1) / 2 - ((top + bot) / 2 - 960) * w / 1080), w
SVG.append('<rect x="-900000" y="-900000" width="2000000" height="2000000" style="fill:#0b1a2a"/>')
SVG.append('<image href="assets/img/bm4.jpg" x="-302848" y="-363008" width="786432" height="786432" preserveAspectRatio="none"/>')
SVG.append('<image href="assets/img/bm5.jpg" x="-171776" y="-166400" width="327680" height="393216" preserveAspectRatio="none"/>')
SVG.append('<image href="assets/img/bm7.webp" x="-40704" y="-35328" width="81920" height="65536" preserveAspectRatio="none"/>')
SVG.append('<image href="assets/img/jp11.webp" x="4352" y="-6656" width="7168" height="8192" preserveAspectRatio="none"/>')
SVG.append('<image href="assets/img/ch15.webp" x="7680" y="-3072" width="256" height="320" preserveAspectRatio="none"/>')
SVG.append(f'<path id="bind" d="{pdr(BD["india"])}" style="fill:#fff;fill-opacity:.06;stroke:#fff;stroke-width:3;vector-effect:non-scaling-stroke"/>')
SVG.append(f'<path id="braj" d="{pdr(BD["raj"])}" style="fill:{PINK};fill-opacity:0;stroke:{PINK};stroke-width:5;vector-effect:non-scaling-stroke;opacity:0"/>')
SVG.append(f'<path id="bjp" d="{pdr(BD["jaipur"])}" style="fill:{GOLD};fill-opacity:0;stroke:{GOLD};stroke-width:6;vector-effect:non-scaling-stroke;opacity:0"/>')
JPR = wp(26.9124, 75.7873); CHP = wp(27.1122, 75.8253)
ROUTE = [JPR, wp(26.99, 75.83), wp(27.06, 75.86), wp(27.10, 75.845), CHP]
SVG.append(f'<path id="rtg" d="{pd(ROUTE)}" pathLength="1" style="fill:none;stroke:{GOLD};stroke-width:16;stroke-opacity:.35;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>'
           f'<path id="rt" d="{pd(ROUTE)}" pathLength="1" style="fill:none;stroke:{GOLD};stroke-width:7;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>')
for k, p, c in [("jpin", JPR, PINK), ("cpin", CHP, GRN)]:
    SVG.append(f'<g id="{k}" style="opacity:0"><circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="22" style="fill:{c};opacity:.3"/><circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="9" style="fill:{c};stroke:#fff;stroke-width:3"/></g>')
SVG.append(f'<circle id="ring" cx="{CHP[0]:.1f}" cy="{CHP[1]:.1f}" r="10" style="fill:none;stroke:#fff;stroke-width:3;vector-effect:non-scaling-stroke;opacity:0"/>')
DLR = [JPR, wp(26.99, 75.83), wp(27.06, 75.86), wp(27.12, 75.86), wp(27.20, 75.89), wp(27.39, 75.96), wp(27.70, 76.20), wp(27.89, 76.29), wp(27.99, 76.38), wp(28.21, 76.79), wp(28.46, 77.03), wp(28.61, 77.21)]
DLP = wp(28.61, 77.21)
SVG.append(f'<path id="dlg" d="{pd(DLR)}" pathLength="1" style="fill:none;stroke:{GOLD};stroke-width:46;stroke-opacity:.35;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1"/>'
           f'<path id="dl" d="{pd(DLR)}" pathLength="1" style="fill:none;stroke:{GOLD};stroke-width:18;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1;filter:drop-shadow(0 0 8px {GOLD})"/>')
CB = json.load(open("data/jaipur_boundary.geojson"))["features"][0]["geometry"]["coordinates"][0]
SVG.append(f'<path id="jcb" d="M{" L".join(f"{wp(la, lo)[0]:.1f} {wp(la, lo)[1]:.1f}" for lo, la in CB[::2])} Z" style="fill:{PINK};fill-opacity:.22;stroke:{PINK};stroke-width:6;vector-effect:non-scaling-stroke;stroke-linejoin:round;opacity:0;filter:drop-shadow(0 0 10px {PINK})"/>')
SVG.append(f'<g id="dpin" style="opacity:0"><circle cx="{DLP[0]:.1f}" cy="{DLP[1]:.1f}" r="300" style="fill:{CYAN};opacity:.3"/><circle cx="{DLP[0]:.1f}" cy="{DLP[1]:.1f}" r="140" style="fill:{CYAN};stroke:#fff;stroke-width:4;vector-effect:non-scaling-stroke"/></g>')
SVG.append(f'<g id="chl" style="opacity:0"><circle cx="{CHP[0]:.1f}" cy="{CHP[1]:.1f}" r="110" style="fill:{GRN};fill-opacity:.25;stroke:{GRN};stroke-width:7;vector-effect:non-scaling-stroke;filter:drop-shadow(0 0 10px {GRN})"/></g>')
SVG.append('<rect id="dim" x="-900000" y="-900000" width="2000000" height="2000000" style="fill:#000;opacity:.12"/>')

# ---------- helpers ----------
def card(cid, img, t0, t1, title, sub="", tag=None, top=380, maxw=900, maxh=640, rot=0, left=None, info=None):
    a = ASP[img]; w = maxw; h = w / a
    if h > maxh: h = maxh; w = h * a
    cw = max(w + 28, 760) if info else w + 28; lx = (1080 - cw) / 2 if left is None else left
    tg = f'<div class="tg" style="background:{tag[1]}">{tag[0]}</div>' if tag else ''
    H.append(f'<div class="card" id="{cid}" style="left:{lx:.0f}px;top:{top}px;width:{cw:.0f}px;rotate:{rot}deg">{tg}<img src="assets/img/{img}.jpg" style="width:{w:.0f}px;height:{h:.0f}px"/>'
             f'<div class="ct">{title}</div>' + (f'<div class="cs">{sub}</div>' if sub else '') + (f'<div class="ci">{info}</div>' if info else '') + '</div>')
    J.append(f'tl.fromTo("#{cid}", {{opacity:0, scale:.55, y:60}}, {{opacity:1, scale:1, y:0, duration:.32, ease:"back.out(1.7)"}}, {t0:.2f});'); CARDS.append([cid, t0, t1])
    sfx("pop", t0, .25)
def theme(i, txt, t, until):
    H.append(f'<div class="th" id="th{i}">{txt}</div>')
    J.append(f'tl.fromTo("#th{i}", {{opacity:0, x:-60}}, {{opacity:1, x:0, duration:.3, ease:"power3.out"}}, {t:.2f}); tl.to("#th{i}", {{opacity:0, duration:.2}}, {until - .2:.2f});')
    J.append(f'tl.fromTo("#flash", {{opacity:.4}}, {{opacity:0, duration:.25, immediateRender:false}}, {t:.2f});')
def pl(i, p, text, t, until, at, dy=-60, cls=""):
    x, y = scr(p, at); H.append(f'<div class="pl {cls}" id="{i}" style="left:{min(max(x, 200), 880):.0f}px;top:{y + dy:.0f}px">{text}</div>')
    J.append(f'tl.fromTo("#{i}", {{opacity:0, scale:.5}}, {{opacity:1, scale:1, duration:.25, ease:"back.out(2)"}}, {t:.2f}); tl.to("#{i}", {{opacity:0, duration:.2}}, {until - .2:.2f});')

# ---------- 3D stadium (CSS 3D, sits on the map plane at Chonp) ----------
# modelled on the RCA design render: oval bowl full of crowd, white ribbed roof ring, white V-column facade on blue glass,
# plaza + two practice grounds + parking around it (illustrative, not to scale)
A, B = 250, 205          # outer half-axes of the stadium (px, before plane scale)
FH = 64                  # facade height
NT = 9                   # seating tiers
def ell(cls, a, b, z=0, extra="", inner=None):
    m = f"-webkit-mask:radial-gradient(closest-side,transparent {inner * 100:.1f}%,#000 {inner * 100 + .6:.1f}%);mask:radial-gradient(closest-side,transparent {inner * 100:.1f}%,#000 {inner * 100 + .6:.1f}%);" if inner else ""
    return f'<div class="{cls}" style="width:{2 * a:.0f}px;height:{2 * b:.0f}px;margin:{-b:.0f}px 0 0 {-a:.0f}px;{m}{extra}" data-z="{z}"></div>'
parts = []
# site: plaza, roads, practice grounds, parking
parts.append(ell("plaza", A * 1.45, B * 1.5))
parts.append('<div class="road" style="width:60px;height:900px;margin:-450px 0 0 -500px"></div><div class="road" style="width:1100px;height:50px;margin:300px 0 0 -560px"></div>')
for (cx, cy) in [(-430, -170), (-420, 120)]:
    parts.append(f'<div class="prac" style="width:200px;height:200px;margin:{cy - 100}px 0 0 {cx - 100}px"><i></i></div>')
for (cx, cy, w, h) in [(330, -230, 220, 150), (340, 140, 200, 190), (-60, 330, 300, 120)]:
    parts.append(f'<div class="park" style="width:{w}px;height:{h}px;margin:{cy - h / 2}px 0 0 {cx - w / 2}px"></div>')
# field
parts.append(ell("field", A * .5, B * .5, extra=""))
parts.append('<div class="pitch2"></div>')
# seating bowl (stepped annuli with crowd texture)
tiers = []
for i in range(NT):
    f = (i + 1) / NT; a = A * (.54 + .40 * f); b = B * (.54 + .40 * f); prev = (.54 + .40 * i / NT) / (.54 + .40 * f)
    tiers.append(ell("tier", a, b, z=round(4 + i * FH / NT, 1), inner=prev - .02))
# facade: V-column panels standing around the oval
NP = 44; pan = []
for k in range(NP):
    th = 2 * math.pi * k / NP; x = A * math.cos(th); y = B * math.sin(th)
    seg = 2 * math.pi * math.sqrt((A * A + B * B) / 2) / NP + 1
    ph = math.degrees(math.atan2(B * math.cos(th), -A * math.sin(th)))
    pan.append(f'<div class="fac" style="width:{seg:.1f}px;height:{FH}px;margin:{-FH}px 0 0 {-seg / 2:.1f}px;transform:translate({x:.1f}px,{y:.1f}px) rotateZ({ph:.1f}deg) rotateX(-90deg)"></div>')
roof = ell("roof", A * 1.04, B * 1.05, z=FH + 3, inner=.80)
screen = f'<div class="scr" style="transform:translate({-A * .62:.0f}px,{-B * .62:.0f}px) rotateZ(-50deg) rotateX(-90deg)"></div>'
ST = f'<div id="std">{"".join(parts)}{"".join(tiers)}{"".join(pan)}{screen}{roof}</div>'


# ---------- 0 HOOK: aerial -> connectivity -> picture -> 3D stadium ----------
IND_C, IND_W = fitb(bbw(BD["india"]), 700, 1400, 1.08)
RAJ_C, RAJ_W = fitb(bbw(BD["raj"]), 720, 1380, 1.1)
JP_C, JP_W = fitb(bbw(BD["jaipur"]), 760, 1380, 1.15)
LC_C, LC_W = fitb((JPR[0] - 60, CHP[1] - 40, JPR[0] + 220, JPR[1] + 40), 760, 1330, 1.25)
C3, W3 = (CHP[0], CHP[1]), 150
J.append('const VB = document.getElementById("world"); function zoomTo(t, c0, w0, c1, w1, d){ const o = {z:0}; tl.to(o, {z:1, duration:d, ease:"power2.inOut", onUpdate:()=>{ const w = Math.exp(Math.log(w0) + (Math.log(w1) - Math.log(w0)) * o.z); const f = Math.abs(w0 - w1) < 1e-6 ? o.z : (w0 - w) / (w0 - w1); const cx = c0[0] + (c1[0] - c0[0]) * f, cy = c0[1] + (c1[1] - c0[1]) * f; const h = w * 1920 / 1080; VB.setAttribute("viewBox", (cx - w / 2) + " " + (cy - h / 2) + " " + w + " " + h); }}, t); }')
CAMS.append((0, 0, IND_C, IND_W))
def zm(t, c1, w1, d):
    c0, w0 = CAMS[-1][2], CAMS[-1][3]
    J.append(f'zoomTo({t:.2f}, [{c0[0]:.1f},{c0[1]:.1f}], {w0:.1f}, [{c1[0]:.1f},{c1[1]:.1f}], {w1:.1f}, {d});'); CAMS.append((t, d, c1, w1))
def bbp(pts, pad):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; return fitb((min(xs), min(ys), max(xs), max(ys)), 640, 1380, pad)
WD_C, WD_W = bbp(DLR, 1.3)
CAMS[0] = (0, 0, WD_C, WD_W); J.append(f'tl.set("#world", {{attr:{{viewBox:"{vb(WD_C, WD_W)}"}}}}, 0);')
IND_C, IND_W = WD_C, WD_W
J.append('tl.set(["#braj", "#bind"], {opacity:0}, 0);')
# connectivity: wide Delhi + Jaipur, thick Delhi Road strip, Jaipur border, then circle Chonp
TC = 0.0
J.append(f'tl.to("#jcb", {{opacity:1, duration:.3}}, {TC:.2f}); tl.fromTo("#jcb", {{fillOpacity:.6}}, {{fillOpacity:.22, duration:.6, immediateRender:false}}, {TC + .3:.2f}); tl.to(["#dl", "#dlg"], {{strokeDashoffset:0, duration:.55, ease:"power2.inOut"}}, {TC + .05:.2f}); tl.to("#dpin", {{opacity:1, duration:.2}}, {TC + .45:.2f});')
pl("ljp", JPR, "JAIPUR", TC + .05, TC + .75, TC, dy=60)
pl("ldl", DLP, "DELHI", TC + .4, TC + .75, TC, cls="")
pl("lrd", DLR[6], "DELHI ROAD &middot; NH-48", TC + .25, TC + .75, TC, dy=0, cls="y")
sfx("whoosh-short", TC + .05, .3); sfx("pop", TC + .45, .3)
zm(TC + .6, LC_C, LC_W, .55)
TCH = TC + 1.1
J.append(f'tl.fromTo("#chl", {{opacity:0, scale:3, svgOrigin:"{CHP[0]:.1f} {CHP[1]:.1f}"}}, {{opacity:1, scale:1, duration:.4, ease:"back.out(2)"}}, {TCH:.2f}); tl.fromTo("#ring", {{attr:{{r:6}}, opacity:1}}, {{attr:{{r:120}}, opacity:0, duration:.8, repeat:1, immediateRender:false}}, {TCH:.2f});')
pl("ljp1", JPR, "JAIPUR", TCH - .1, TCH + .6, TCH + .2, dy=60)
pl("lch", CHP, "CHONP &middot; STADIUM SITE", TCH, TCH + 1.55, TCH + .2, dy=-90, cls="g")
sfx("pop", TCH, .35)
# hook title
H.append('<div id="hook"><small>DUNIYA KA</small><b>3RD</b><span>SABSE BADA CRICKET STADIUM</span><i>JAIPUR MEIN</i></div>')
J.append(f'tl.fromTo("#hook", {{opacity:1, scale:1.15}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, .0); tl.to("#hook", {{opacity:0, y:-40, duration:.2}}, {TC + .55:.2f});')
sfx("impact-bass-1", .15, .5)
# picture (render) at Chonp
TPIC = TCH + .35
H.append('<div id="hero"><img src="assets/img/render.jpg"/><div>ANIL AGARWAL INTERNATIONAL CRICKET STADIUM</div><span>PLAN &middot; DESIGN RENDER</span></div>')
J.append(f'tl.fromTo("#hero", {{opacity:1, scale:1.12}}, {{opacity:1, scale:1, duration:.35, ease:"power2.out"}}, 0);'
         f'tl.to("#hero", {{left:600, top:250, width:440, duration:.45, ease:"power2.inOut"}}, {TC + .55:.2f});'
         f'tl.to("#hero", {{left:190, top:70, width:700, duration:.45, ease:"power2.inOut"}}, {TPIC:.2f});'
         f'tl.to("#hero", {{opacity:0, scale:.6, y:500, duration:.4, ease:"power2.in"}}, {TPIC + 1.35:.2f});')
# 3D: zoom to Chonp, tilt the ground, stadium rises
T3 = TPIC + 1.4
zm(T3 - .4, C3, W3, 1.0)
J.append(f'tl.to(["#dl", "#dlg", "#jcb", "#dpin", "#chl"], {{opacity:0, duration:.3}}, {T3 - .3:.2f});')
H.insert(0, '<div id="fog"></div>')
J.append(f'tl.to("#fog", {{opacity:1, duration:1}}, {T3 + .2:.2f}); tl.to("#fog", {{opacity:0, duration:.6}}, {S(3) - .3:.2f}); tl.to("#fog", {{opacity:1, duration:.8}}, {S(4) - .1:.2f});')
J.append(f'tl.fromTo("#plane", {{rotationX:0, scale:1}}, {{rotationX:58, scale:1.35, duration:1.2, ease:"power2.inOut"}}, {T3:.2f});')
J.append(f'tl.set("#std", {{opacity:1}}, {T3 + .5:.2f}); tl.fromTo(["#std .plaza", "#std .road", "#std .park"], {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.4, stagger:.05, ease:"back.out(1.6)"}}, {T3 + .5:.2f}); tl.fromTo("#std .prac", {{scale:0}}, {{scale:1, duration:.35, stagger:.12, ease:"back.out(2.5)"}}, {T3 + .8:.2f});')
J.append(f'tl.fromTo(["#std .field", "#std .pitch2"], {{scale:0}}, {{scale:1, duration:.35, ease:"back.out(2)"}}, {T3 + .7:.2f});')
J.append(f'tl.fromTo("#std .tier", {{z:0, opacity:0}}, {{z:(i, el)=>parseFloat(el.dataset.z), opacity:1, duration:.45, stagger:.07, ease:"back.out(1.5)"}}, {T3 + .9:.2f});')
J.append(f'tl.fromTo("#std .fac", {{scaleY:0}}, {{scaleY:1, duration:.35, stagger:{{each:.02, from:"start"}}, ease:"back.out(2)"}}, {T3 + 1.3:.2f}); tl.fromTo("#std .scr", {{scaleY:0}}, {{scaleY:1, duration:.3, ease:"back.out(2)"}}, {T3 + 1.9:.2f});')
J.append(f'tl.fromTo("#std .roof", {{z:{FH + 160}, opacity:0}}, {{z:{FH + 3}, opacity:1, duration:.55, ease:"bounce.out"}}, {T3 + 2.0:.2f});')

J.append(f'tl.fromTo("#std", {{rotationZ:-20}}, {{rotationZ:340, duration:{END - T3:.2f}, ease:"none"}}, {T3 + .6:.2f});')
sfx("riser", T3, .35); sfx("impact-bass-1", T3 + 1.9, .45); sfx("sparkle", T3 + 2.5, .3)
H.append('<div id="name3d"><small>ANIL AGARWAL</small><b>INTERNATIONAL CRICKET STADIUM</b><span>Chonp &middot; Jaipur</span></div>')
J.append(f'tl.fromTo("#name3d", {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:.35, ease:"back.out(2)"}}, {T3 + 1.9:.2f}); tl.to("#name3d", {{opacity:0, duration:.2}}, {wt(1, "Vedanta") - .3:.2f});')

# ---------- hook pop-ups (keep the first seconds busy) ----------
def sticker(i, html, t, until, x, y, rot, cls=""):
    H.append(f'<div class="stk {cls}" id="stk{i}" style="left:{x}px;top:{y}px;rotate:{rot}deg">{html}</div>')
    J.append(f'tl.fromTo("#stk{i}", {{opacity:0, y:24, clipPath:"inset(0 100% 0 0)"}}, {{opacity:1, y:0, clipPath:"inset(0 0% 0 0)", duration:.45, ease:"power3.out"}}, {t:.2f}); tl.to("#stk{i}", {{opacity:0, y:-16, duration:.3, ease:"power2.in"}}, {until - .3:.2f});')
    sfx("click-soft", t, .3)
sticker(0, "<b>No. 3</b> DUNIYA MEIN", wt(0, "teesra") - .1, wt(0, "teesra") + 1.3, 60, 1080, 0)
sticker(1, "CRICKET STADIUM", wt(0, "cricket") - .1, wt(0, "cricket") + 1.2, 520, 1180, 0)
for i, (txt, dt, x, y) in enumerate([("100 ACRE", 1.0, 60, 1240), ("PRACTICE GROUNDS", 1.35, 470, 1290), ("PARKING", 1.7, 120, 1330)]):
    sticker(10 + i, txt, T3 + dt, T3 + dt + 1.3, x, y, 0, "chip")
# Anil Agarwal portrait on his name
TA = wt(0, "Anil Agarwal") - .1
H.append('<div id="anil"><img src="assets/img/anil.jpg"/><div><b>ANIL AGARWAL</b><span>Chairman, Vedanta</span></div></div>')
J.append(f'tl.fromTo("#anil", {{opacity:0, x:-60}}, {{opacity:1, x:0, duration:.5, ease:"power3.out"}}, {TA:.2f}); tl.fromTo("#anil img", {{scale:1.15}}, {{scale:1, duration:.8, ease:"power2.out"}}, {TA:.2f}); tl.to("#anil", {{opacity:0, x:-60, duration:.3, ease:"power2.in"}}, {wt(1, "2023") - .2:.2f});')
sfx("whoosh-short", TA, .35)

# ---------- 1 MoU ----------
H.append('<div id="mou"><div class="mrow"><span>VEDANTA</span><b>&times;</b><span>RCA</span></div><div class="mbig">&#8377;300 CR</div><div class="msub">MoU &middot; 30 MARCH 2023</div></div>')
TM = max(S(1), T3 + 2.6)
J.append(f'tl.fromTo("#mou", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.45, ease:"power3.out"}}, {wt(1, "300") - .2:.2f}); tl.fromTo("#mou .mbig", {{letterSpacing:"0.4em", opacity:0}}, {{letterSpacing:"0.02em", opacity:1, duration:.6, ease:"power3.out"}}, {wt(1, "300") - .1:.2f}); tl.to("#mou", {{opacity:0, duration:.2}}, {S(2) - .1:.2f});')
sfx("pop", wt(1, "Vedanta"), .3); sfx("impact-bass-1", wt(1, "300"), .4)

card("clip", "statesman2", wt(1, "2023") - .1, wt(1, "300") - .15, "RCA + VEDANTA MoU", "The Statesman &middot; 30 March 2023", ("NEWS", "#C9A24A"), top=170, maxw=1000, maxh=1120)

# ---------- 2 TOP 3 ----------
J.append(f'tl.to("#dim", {{opacity:.65, duration:.3}}, {S(2) - .1:.2f}); tl.to("#dim", {{opacity:.12, duration:.3}}, {S(3):.2f});')
H.append('<div id="rank">'
         '<div class="rk" id="rk0"><img src="assets/img/modi2.jpg"/><div><i>#1</i><b>NARENDRA MODI STADIUM</b><span>Ahmedabad, India</span></div></div>'
         '<div class="rk" id="rk1"><img src="assets/img/mcg2.jpg"/><div><i>#2</i><b>MELBOURNE CRICKET GROUND</b><span>Australia</span></div></div>'
         '<div class="rk hot" id="rk2"><img src="assets/img/render.jpg"/><div><i>#3</i><b>JAIPUR &middot; CHONP</b><span>Anil Agarwal Intl. Stadium</span></div></div></div>')
J.append(f'tl.fromTo("#rank", {{opacity:0}}, {{opacity:1, duration:.2}}, {S(2):.2f}); tl.to("#rank", {{opacity:0, duration:.2}}, {S(3) - .1:.2f});')
for i, t in enumerate([wt(2, "Ahmedabad"), wt(2, "Melbourne"), wt(2, "Melbourne") + 1.0]):
    J.append(f'tl.fromTo("#rk{i}", {{opacity:0, x:-80}}, {{opacity:1, x:0, duration:.3, ease:"back.out(2)"}}, {t - .1:.2f});'); sfx("pop", t, .3)

# ---------- 3 LOCATION (flatten, map) ----------
J.append(f'tl.to("#plane", {{rotationX:0, scale:1, duration:.9, ease:"power2.inOut"}}, {S(3) - .3:.2f}); tl.to("#std", {{opacity:0, duration:.3}}, {S(3) - .3:.2f});')
zm(S(3) - .3, WD_C, WD_W, .9)
J.append(f'tl.to(["#dl", "#dlg", "#jcb", "#dpin"], {{opacity:1, duration:.3}}, {S(3) + .2:.2f}); tl.to("#chl", {{opacity:1, duration:.3}}, {wt(3, "Chonp"):.2f});')
pl("ldl2", DLP, "DELHI", S(3) + .3, wt(3, "shehar") - .1, S(3) + .7)
pl("ljpw", JPR, "JAIPUR", S(3) + .3, wt(3, "shehar") - .1, S(3) + .7, dy=60)
pl("lrdw", DLR[6], "DELHI ROAD &middot; NH-48", wt(3, "Delhi Road") - .1, wt(3, "shehar") - .1, S(3) + .7, dy=0, cls="y")
zm(wt(3, "shehar") - .2, LC_C, LC_W, .8)
TL3 = wt(3, "shehar") + .7
J.append(f'tl.fromTo("#ring", {{attr:{{r:6}}, opacity:1}}, {{attr:{{r:120}}, opacity:0, duration:.8, repeat:2, immediateRender:false}}, {TL3:.2f});')
pl("ljp2", JPR, "JAIPUR", TL3 - .3, wt(3, "100") + .5, TL3, dy=60)
pl("lch2", CHP, "CHONP &middot; STADIUM SITE", TL3 - .3, wt(3, "100") + .5, TL3, dy=-90, cls="g")
pl("lkm2", DLR[1], "~25 KM", wt(3, "25 km") - .1, wt(3, "100") + .5, TL3, dy=0, cls="y")
H.append('<div id="facts"><div><b>~25 KM</b><span>SHEHAR SE</span></div><div><b>100</b><span>ACRE</span></div></div>')
J.append(f'tl.fromTo("#facts", {{opacity:0}}, {{opacity:1, duration:.2}}, {wt(3, "25 km") - .1:.2f}); tl.from("#facts div", {{opacity:0, scale:.4, duration:.3, stagger:{max(.2, wt(3, "100") - wt(3, "25 km")):.2f}, ease:"back.out(2.2)"}}, {wt(3, "25 km") - .1:.2f}); tl.to("#facts", {{opacity:0, duration:.2}}, {wt(3, "100") + .5:.2f});')
card("site", "aerial_route", wt(3, "100") + .5, wt(3, "Delhi highway") - .1, "100 ACRE CAMPUS", "Design render &middot; practice grounds, academy, parking", ("100 ACRE", GRN), top=420, maxw=960, maxh=560)
zm(wt(3, "Delhi highway") - .3, WD_C, WD_W, .8)
J.append(f'tl.fromTo(["#dl", "#dlg"], {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:1.0, ease:"power2.inOut", immediateRender:false}}, {wt(3, "highway"):.2f});')
pl("ldl3", DLP, "DELHI", wt(3, "highway") + .8, S(4) - .2, wt(3, "highway") + .6)
pl("ljp3", JPR, "JAIPUR", wt(3, "Delhi highway"), S(4) - .2, wt(3, "highway") + .6, dy=60)
sfx("pop", wt(3, "25 km"), .3); sfx("pop", wt(3, "100"), .3); sfx("whoosh-short", wt(3, "highway") - .2, .3)

# ---------- 4 POTENTIAL (3D again + icons) ----------
zm(S(4) - .3, C3, W3, .9)
J.append(f'tl.to(["#dl", "#dlg", "#jcb", "#dpin", "#chl"], {{opacity:0, duration:.3}}, {S(4) - .3:.2f}); tl.to("#plane", {{rotationX:58, scale:1.35, duration:.9, ease:"power2.inOut"}}, {S(4) - .3:.2f}); tl.to("#std", {{opacity:1, duration:.3}}, {S(4) + .2:.2f});')
EV = [("01", "IPL", "IPL"), ("02", "INTERNATIONAL MATCHES", "international"), ("03", "CONCERTS", "concerts"), ("04", "BADE EVENTS", "events")]
H.append('<div id="evs">' + "".join(f'<div class="ev" id="ev{i}"><i>{ic}</i><b>{nm}</b></div>' for i, (ic, nm, _) in enumerate(EV)) + '</div>')
J.append(f'tl.set("#evs", {{opacity:1}}, {S(4):.2f}); tl.to("#evs", {{opacity:0, duration:.2}}, {wt(4, "hotels") - .3:.2f});')
for i, (_, _, w_) in enumerate(EV):
    t = wt(4, w_) - .1; J.append(f'tl.fromTo("#ev{i}", {{opacity:0, scale:.3, y:40}}, {{opacity:1, scale:1, y:0, duration:.3, ease:"back.out(2.5)"}}, {t:.2f});'); sfx("pop", t, .3)
J.append(f'tl.to("#std .roof", {{filter:"drop-shadow(0 0 30px rgba(255,79,163,1)) brightness(1.3)", duration:.15, yoyo:true, repeat:9}}, {wt(4, "concerts"):.2f});')
PH4 = [("ipl", "IPL", "IPL", "Representative &middot; Narendra Modi Stadium"), ("lightshow", "international", "INTERNATIONAL MATCHES", "Light show &middot; Ahmedabad"),
       ("concert1", "concerts", "CONCERTS", "Representative stadium concert"), ("concert2", "events", "BADE EVENTS", "Representative")]
for i, (img, w_, ttl, sb) in enumerate(PH4):
    t0 = wt(4, w_) - .05; t1 = wt(4, PH4[i + 1][1]) - .05 if i + 1 < len(PH4) else wt(4, "hotels") - .1
    POS4 = [(30, 600, 0), (545, 600, 0), (30, 1000, 0), (545, 1000, 0)]
    lx, ty, rt = POS4[i]
    card(f"pc{i}", img, t0, wt(4, "hotels") - .1, ttl, "", top=ty, maxw=470, maxh=300, rot=rt, left=lx)


# ---------- 4b AAS PAAS: top-down map, 5 km radius, pins + photos ----------
TH = wt(4, "aas paas") - .3
PXK = 256 * 2 ** 13 / 40075 / math.cos(math.radians(27.11)); RK = 5 * PXK
RC_C, RC_W = (CHP[0], CHP[1] - 60 * 2 * RK * 1.25 / 1080), 2 * RK * 1.25
SVG.insert(-1, f'<circle id="rad" cx="{CHP[0]:.1f}" cy="{CHP[1]:.1f}" r="{RK:.1f}" pathLength="1" style="fill:#C9A24A;fill-opacity:0;stroke:#C9A24A;stroke-width:4;stroke-dasharray:1;stroke-dashoffset:1;vector-effect:non-scaling-stroke;opacity:0"/>'
               f'<circle id="radr" cx="{CHP[0]:.1f}" cy="{CHP[1]:.1f}" r="{RK:.1f}" style="fill:none;stroke:#F7E3A8;stroke-width:2;stroke-dasharray:8 10;vector-effect:non-scaling-stroke;opacity:0"/>'
               f'<g id="sdot" style="opacity:0"><circle cx="{CHP[0]:.1f}" cy="{CHP[1]:.1f}" r="{RK * .09:.1f}" style="fill:#3CFF96;fill-opacity:.35;stroke:#3CFF96;stroke-width:3;vector-effect:non-scaling-stroke"/></g>')
J.append(f'tl.to("#std", {{opacity:0, duration:.3}}, {TH:.2f}); tl.to("#plane", {{rotationX:0, scale:1, duration:.8, ease:"power2.inOut"}}, {TH:.2f}); tl.to("#fog", {{opacity:0, duration:.4}}, {TH:.2f});')
zm(TH, RC_C, RC_W, .8)
J.append(f'tl.to(["#dl", "#dlg", "#sdot"], {{opacity:1, duration:.3}}, {TH + .5:.2f}); tl.set(["#rad", "#radr"], {{opacity:1}}, {TH + .6:.2f}); tl.to("#rad", {{strokeDashoffset:0, duration:.8, ease:"power2.inOut"}}, {TH + .6:.2f}); tl.to("#rad", {{fillOpacity:.12, duration:.5}}, {TH + 1.2:.2f}); tl.fromTo("#radr", {{attr:{{r:{RK * .2:.1f}}}}}, {{attr:{{r:{RK:.1f}}}, duration:1.2, repeat:3, ease:"power1.out"}}, {TH + 1.0:.2f});')
J.append(f'tl.to(["#rad", "#radr", "#sdot", "#dl", "#dlg"], {{opacity:0, duration:.3}}, {S(5) - .35:.2f});')
sfx("whoosh", TH, .3); sfx("riser", TH + .6, .25)
pl("lrad", (CHP[0] - RK * .62, CHP[1] - RK * .05), "5 KM RADIUS", TH + .9, S(5), TH + 1, dy=0, cls="lux")
pl("lsite", CHP, "STADIUM", TH + .6, S(5), TH + 1, dy=-60, cls="lux g")
PINS = [("HOTELS", (-.7, -.45), "hotels"), ("RESTAURANTS", (.62, -.55), "restaurants"), ("CAFE", (-.66, .35), "cafe"), ("PLOTS &middot; COLONIES", (.5, .62), "zameen")]
for i, (nm, (fx, fy), w_) in enumerate(PINS):
    p = (CHP[0] + fx * RK, CHP[1] + fy * RK); x, y = scr(p, TH + 1)
    H.append(f'<div class="rpin" id="rp{i}" style="left:{x:.0f}px;top:{y:.0f}px"><i></i><b>{nm}</b></div>')
    t = wt(4, w_) - .1
    J.append(f'tl.fromTo("#rp{i}", {{opacity:0, y:-40}}, {{opacity:1, y:0, duration:.4, ease:"power3.out"}}, {t:.2f}); tl.to("#rp{i}", {{opacity:0, duration:.2}}, {S(5) - .3:.2f});'); sfx("click-soft", t, .35)
card("hp0", "hotel", wt(4, "hotels") - .05, S(5) - .5, "HOTELS", "", top=200, maxw=320, maxh=240, left=20)
card("hp1", "restaurant", wt(4, "restaurants") - .05, S(5) - .5, "RESTAURANTS", "", top=200, maxw=320, maxh=240, left=372)
card("hp2", "hotel_lobby", wt(4, "cafe") - .05, S(5) - .5, "CAFE &middot; LOUNGES", "", top=200, maxw=320, maxh=240, left=724)
H.append('<div id="dem"><span>ZAMEEN KI DEMAND</span><b>&#9650;</b></div>')
J.append(f'tl.fromTo("#dem", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.45, ease:"power3.out"}}, {wt(4, "zameen") - .05:.2f}); tl.to("#dem b", {{y:-14, duration:.35, yoyo:true, repeat:5}}, {wt(4, "zameen") + .3:.2f}); tl.to("#dem", {{opacity:0, duration:.2}}, {S(5) - .2:.2f});')
# back to 3D for status
zm(S(5) - .3, C3, W3, .8)
J.append(f'tl.to("#plane", {{rotationX:58, scale:1.35, duration:.8, ease:"power2.inOut"}}, {S(5) - .3:.2f}); tl.to("#std", {{opacity:1, duration:.3}}, {S(5):.2f}); tl.to("#fog", {{opacity:1, duration:.5}}, {S(5):.2f});')

# ---------- 5 STATUS ----------
J.append(f'tl.to("#std", {{filter:"grayscale(1) brightness(.6)", duration:.5}}, {S(5):.2f}); tl.to("#dim", {{opacity:.5, duration:.3}}, {S(5):.2f});')
H.append('<div id="stamp">KAAM RUKA</div>')
J.append(f'tl.fromTo("#stamp", {{opacity:0, scale:1.6}}, {{opacity:1, scale:1, duration:.3, ease:"power4.out"}}, {S(5) + .1:.2f}); tl.to("#stamp", {{opacity:0, duration:.2}}, {wt(5, "2022") - .1:.2f});')
sfx("impact-bass-1", S(5) + .35, .5)
card("s1", "foundation", wt(5, "2022") - .1, wt(5, "191") - .1, "NEEV: FEBRUARY 2022", "Shilanyas", ("2022", "#C9A24A"), top=380, maxh=520)
card("s2", "construction", wt(5, "191") - .1, S(6) + .2, "~&#8377;191 CR KHARCH, PHIR KAAM THAP", "Site ki tasveer", ("RUKA", "#E5484D"), top=380, maxh=520)

# ---------- 6 NOW + CTA ----------
H.append('<div id="now"><p id="nw0"><b>IIT BOMBAY</b>Structure ki jaanch chal rahi hai</p></div>')
J.append(f'tl.fromTo("#now", {{opacity:0}}, {{opacity:1, duration:.2}}, {S(6):.2f}); tl.fromTo("#nw0", {{opacity:0, x:-60}}, {{opacity:1, x:0, duration:.3, ease:"back.out(2)"}}, {S(6):.2f}); tl.to("#now", {{opacity:0, duration:.2}}, {wt(6, "Aapko") - .1:.2f});')
sfx("click-soft", S(6), .3)
J.append(f'tl.to("#std", {{filter:"grayscale(0) brightness(1)", duration:.5}}, {wt(6, "Aapko"):.2f});')
H.append('<div id="cta"><b>KAB TAK BANEGA?</b><div class="opts"><span>2027</span><span>2028</span><span>2030+</span></div><em>COMMENT KARO</em></div>')
J.append(f'tl.fromTo("#cta", {{opacity:0}}, {{opacity:1, duration:.2}}, {wt(6, "Aapko"):.2f}); tl.from("#cta b", {{opacity:0, scale:.6, duration:.3, ease:"back.out(2)"}}, {wt(6, "Aapko"):.2f}); tl.from("#cta .opts span", {{opacity:0, y:30, duration:.25, stagger:.15}}, {wt(6, "kab tak") :.2f}); tl.from("#cta em", {{opacity:0, scale:.5, duration:.3, ease:"back.out(2)"}}, {wt(6, "Comment"):.2f});')
sfx("sparkle", wt(6, "Comment"), .3)

# card exits: hold until the next card arrives (never blank)
CARDS.sort(key=lambda c: c[1])
for i, (cid, t0, t1) in enumerate(CARDS):
    nxt = CARDS[i + 1][1] if i + 1 < len(CARDS) else END
    out = t1 if cid == 'pic' else max(t1, min(nxt + .3, t1 + .6))
    J.append(f'tl.set("#{cid}", {{zIndex:{10 + i}}}, 0); tl.to("#{cid}", {{opacity:0, scale:.9, duration:.2, ease:"power2.in"}}, {out - .2:.2f});')

# captions
HI = ["teesra sabse bada", "Anil Agarwal International Cricket Stadium", "Vedanta", "RCA", "MoU", "300 crore", "Narendra Modi Stadium", "Melbourne Cricket Ground", "Chonp", "Delhi Road", "25 km", "100 acre", "IPL", "international matches", "concerts", "events", "hotels", "restaurants", "zameen ki demand", "cafe", "kaam ruka", "2022", "191 crore", "IIT Bombay", "Comment"]
def hl(t):
    for h in sorted(HI, key=len, reverse=True):
        i = t.find(h)
        if i >= 0 and "<span" not in t[max(0, i - 25):i] and "span" not in t[i:i + len(h)]: t = t[:i] + '<span class="y">' + h + '</span>' + t[i + len(h):]
    return t
ci = 0
for n, ph in enumerate(PH):
    words = ph["t"].split(); chunks = []; cur = ""
    for w_ in words:
        if cur and len(cur) + 1 + len(w_) > 24: chunks.append(cur); cur = w_
        else: cur = (cur + " " + w_).strip()
    chunks.append(cur)
    tot = sum(len(c) for c in chunks); t = ph["s"]; nx = PH[n + 1]["s"] if n + 1 < len(PH) else END
    for j, c in enumerate(chunks):
        d = (ph["e"] - ph["s"]) * len(c) / tot
        a_ = max(.02, t if j else t - .04); b_ = (min(t + d + .25, nx - .08) if j == len(chunks) - 1 else t + d - .03)
        H.append(f'<div class="cp" id="cp{ci}"><div>{hl(c)}</div></div>')
        J.append(f'tl.fromTo("#cp{ci}", {{opacity:0, scale:.88}}, {{opacity:1, scale:1, duration:.1}}, {a_:.2f}); tl.to("#cp{ci}", {{opacity:0, duration:.04}}, {b_ - .04:.2f});')
        t += d; ci += 1
if os.path.exists(f"{P}/assets/face.mp4"):
    H.append('<video id="face" class="clip" src="assets/face.mp4" data-start="0" data-duration="1.0" data-track-index="2" muted playsinline></video>')
    J.append('tl.set("#face", {opacity:1}, 0); tl.to("#face", {opacity:0, scale:1.06, duration:.12}, .8);')
H.append('<div id="vig"></div><div id="flash"></div><div id="cred">Renders: RCA design &middot; hotel/restaurant photos: Gerd Eichmann, Wikimedia Commons, CC BY 4.0 &middot; 5 km radius illustrative &middot; photos: news / social media (supplied) &middot; Sources: Hindustan Zinc (Vedanta) release, Business Standard, Times Now, ETV Bharat &middot; 3D model illustrative &middot; Imagery: NASA Blue Marble, Sentinel-2 (EOX)</div>')
CSS = """@font-face{font-family:Anton;src:url(assets/fonts/anton.woff2)}@font-face{font-family:Mont;font-weight:700;src:url(assets/fonts/mont700.woff2)}@font-face{font-family:Mont;font-weight:800;src:url(assets/fonts/mont800.woff2)}@font-face{font-family:Mont;font-weight:900;src:url(assets/fonts/mont900.woff2)}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#07090d}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif}#world{position:absolute;inset:0;width:1080px;height:1920px}.y{color:#FFC42E}
#face{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:40}
#sky{position:absolute;inset:0;background:linear-gradient(180deg,#0b1730 0%,#2b3f66 30%,#c98a5a 46%,#3a3226 60%)}
#stage{position:absolute;inset:0;perspective:1500px;perspective-origin:50% 35%;overflow:hidden}#plane{position:absolute;inset:0;transform-style:preserve-3d;transform-origin:50% 55%}
#fog{position:absolute;left:0;right:0;top:0;height:900px;background:linear-gradient(180deg,rgba(201,138,90,.0) 0%,rgba(201,138,90,.55) 55%,rgba(201,138,90,0) 100%);opacity:0;z-index:3;pointer-events:none}
#std{position:absolute;left:540px;top:960px;width:0;height:0;transform-style:preserve-3d;opacity:0}
#std > div{position:absolute;left:0;top:0}
#std .plaza{border-radius:50%;background:radial-gradient(closest-side,#d9d4c9 0 92%,#bfb8aa 93% 100%);box-shadow:0 0 0 6px rgba(0,0,0,.15)}
#std .road{background:#4a4d55;border-left:3px dashed #ddd}
#std .prac{border-radius:50%;background:repeating-linear-gradient(90deg,#3f9a3b 0 22px,#49a944 22px 44px);box-shadow:0 0 0 8px #2f6d2c}#std .prac i{position:absolute;left:50%;top:50%;width:12px;height:44px;margin:-22px 0 0 -6px;background:#d8c38a}
#std .park{background:#8d9097;background-image:repeating-linear-gradient(90deg,rgba(255,255,255,.7) 0 2px,transparent 2px 16px);border:4px solid #6c6f77}
#std .field{border-radius:50%;background:repeating-linear-gradient(90deg,#3e9b3a 0 26px,#48a843 26px 52px);box-shadow:inset 0 0 0 4px rgba(255,255,255,.8),inset 0 0 30px rgba(0,0,0,.35)}
#std .pitch2{width:20px;height:66px;margin:-33px 0 0 -10px;background:#d8c38a}
#std .tier{border-radius:50%;background:url(assets/img/crowd.png);background-size:180px;box-shadow:inset 0 0 0 3px rgba(255,255,255,.35)}
#std .fac{transform-origin:50% 100%;background-color:#3c5878;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 64' preserveAspectRatio='none'><path d='M0 0 L20 64 L40 0' fill='none' stroke='white' stroke-width='5'/><rect x='0' y='0' width='40' height='5' fill='white'/></svg>");background-size:100% 100%;backface-visibility:visible}
#std .scr{width:90px;height:44px;margin:-44px 0 0 -45px;transform-origin:50% 100%;background:#111;border:4px solid #ddd}
#std .roof{border-radius:50%;background:repeating-conic-gradient(from 0deg,#f6f4ee 0 3.6deg,#c9ced6 3.6deg 4.4deg);box-shadow:0 0 30px rgba(255,255,255,.35)}
#name3d{position:absolute;left:40px;right:40px;top:300px;text-align:center;opacity:0;z-index:12}#name3d small{display:inline-block;padding:8px 26px;border-radius:30px;background:#FFC42E;color:#111;font:900 40px Mont}
#name3d b{display:block;margin-top:12px;font:400 76px/1.05 Anton;color:#fff;text-shadow:0 6px 24px #000}#name3d span{display:inline-block;margin-top:10px;padding:6px 20px;border-radius:20px;background:rgba(8,10,15,.85);border:2px solid #3CFF96;color:#3CFF96;font:800 30px Mont}
#hook b{font-size:170px !important}#hook span{font-size:56px !important}#hook i{font-size:52px !important;margin-top:8px !important}#hook{padding:16px 10px !important}
.stk{position:absolute;opacity:0;z-index:14;padding:14px 26px;border-radius:18px;background:#FFC42E;color:#111;font:400 50px/1 Anton;box-shadow:0 10px 30px rgba(0,0,0,.6)}.stk b{font-size:64px}.stk.w{background:#fff}.stk.chip{padding:10px 22px;border-radius:40px;background:rgba(8,10,15,.9);border:3px solid #3CFF96;color:#3CFF96;font:900 34px Mont}
#anil{position:absolute;left:40px;top:1020px;opacity:0;z-index:15;display:flex;align-items:center;gap:18px;padding:12px 28px 12px 12px;border-radius:120px;background:rgba(8,10,15,.92);border:3px solid #FFC42E;box-shadow:0 20px 50px rgba(0,0,0,.6)}
#anil img{width:200px;height:200px;border-radius:50%;object-fit:cover;border:5px solid #FFC42E}#anil b{display:block;font:400 64px/1 Anton;color:#fff}#anil span{display:block;margin-top:6px;font:800 30px Mont;color:#FFC42E}

/* ---- luxury styling ---- */
.stk{padding:16px 30px !important;border-radius:6px !important;background:linear-gradient(135deg,rgba(14,12,9,.92),rgba(30,24,16,.92)) !important;border:1.5px solid #C9A24A !important;color:#F3E6C8 !important;font:600 34px/1 Mont !important;letter-spacing:.22em;box-shadow:0 18px 50px rgba(0,0,0,.55) !important;backdrop-filter:blur(6px)}
.stk b{font:400 58px/1 Anton;letter-spacing:.04em;background:linear-gradient(180deg,#F7E3A8,#C9A24A);-webkit-background-clip:text;color:transparent;margin-right:10px}
.stk.chip{padding:10px 22px !important;font:700 26px Mont !important;letter-spacing:.24em;border-radius:4px !important}
#anil{border-radius:8px !important;border:1.5px solid #C9A24A !important;background:linear-gradient(135deg,rgba(14,12,9,.94),rgba(34,27,18,.94)) !important;padding:14px 34px 14px 14px !important}
#anil img{border-radius:6px !important;border:none !important;width:190px !important;height:190px !important}#anil b{letter-spacing:.06em;color:#F3E6C8 !important}#anil span{color:#C9A24A !important;letter-spacing:.18em;font:600 24px Mont !important;text-transform:uppercase}
#mou{border-radius:8px !important;border:1.5px solid #C9A24A !important;background:linear-gradient(135deg,rgba(14,12,9,.94),rgba(34,27,18,.94)) !important}
.mrow span{color:#F3E6C8 !important;letter-spacing:.12em}.mrow b{font:300 60px Mont !important;color:#C9A24A}.mbig{background:linear-gradient(180deg,#F7E3A8,#C9A24A);-webkit-background-clip:text;color:transparent !important}.msub{color:#C9A24A !important;letter-spacing:.3em !important}
.ev{border-radius:6px !important;border:1.5px solid #C9A24A !important;background:linear-gradient(135deg,rgba(14,12,9,.92),rgba(34,27,18,.92)) !important}.ev i{font:400 46px Anton !important;color:#C9A24A}.ev b{color:#F3E6C8 !important;letter-spacing:.06em}
.wpin i{font-size:40px !important;color:#C9A24A}.wpin b{border-radius:4px !important;border:1.5px solid #C9A24A !important;color:#F3E6C8 !important;letter-spacing:.16em;font:700 26px Mont !important}
.card{border-radius:10px !important}.card img{border-radius:6px !important}.tg{border-radius:3px !important;letter-spacing:.2em;color:#111 !important}
#hook{border-radius:8px !important;border:1.5px solid #C9A24A}#hook b{background:linear-gradient(180deg,#F7E3A8,#C9A24A);-webkit-background-clip:text;color:transparent !important}#hook i{border-radius:4px !important;background:#C9A24A !important;letter-spacing:.06em}
#name3d small{border-radius:3px !important;background:#C9A24A !important;letter-spacing:.2em}#name3d span{border-radius:3px !important;border-color:#C9A24A !important;color:#F3E6C8 !important}
.pl.lux{border-radius:4px;border:1.5px solid #C9A24A;background:rgba(14,12,9,.92);color:#F3E6C8;letter-spacing:.2em;font:700 26px Mont}.pl.lux.g{color:#3CFF96;border-color:#3CFF96}
.rpin{position:absolute;opacity:0;translate:-50% -100%;display:flex;flex-direction:column;align-items:center;z-index:7}.rpin b{padding:10px 18px;border-radius:4px;background:linear-gradient(135deg,rgba(14,12,9,.94),rgba(34,27,18,.94));border:1.5px solid #C9A24A;color:#F3E6C8;font:700 24px Mont;letter-spacing:.18em;white-space:nowrap}
.rpin i{order:2;width:3px;height:44px;background:linear-gradient(#C9A24A,rgba(201,162,74,0))}
#dem{position:absolute;left:0;right:0;margin:0 auto;width:max-content;top:520px;opacity:0;z-index:12;display:flex;align-items:center;gap:14px;padding:18px 26px;border-radius:6px;border:1.5px solid #C9A24A;background:linear-gradient(135deg,rgba(14,12,9,.94),rgba(34,27,18,.94))}#dem span{font:400 40px/1.05 Anton;color:#F3E6C8;letter-spacing:.04em;width:240px}#dem b{font:400 70px Anton;color:#3CFF96}
#stamp{border:2px solid #E5484D !important;border-radius:4px !important;background:rgba(14,12,9,.88) !important;color:#E5484D !important;font:400 110px/1 Anton !important;letter-spacing:.08em;padding:22px 46px !important}
#now p{border-radius:6px !important;border:1.5px solid #C9A24A !important;background:linear-gradient(135deg,rgba(14,12,9,.94),rgba(34,27,18,.94)) !important;color:#F3E6C8 !important}#now p b{color:#C9A24A !important;letter-spacing:.06em}
#cta b{border-radius:6px !important;background:linear-gradient(135deg,rgba(14,12,9,.95),rgba(34,27,18,.95)) !important;border:1.5px solid #C9A24A;color:#F3E6C8 !important}
.opts span{border-radius:4px !important;border:1.5px solid #C9A24A !important;color:#F7E3A8 !important;background:rgba(14,12,9,.9) !important}
#cta em{border-radius:4px !important;background:#C9A24A !important;color:#111 !important;letter-spacing:.22em}
#hero{position:absolute;left:160px;top:760px;width:760px;opacity:1;z-index:13;padding:12px 12px 14px;border-radius:24px;background:#fff;box-shadow:0 30px 70px rgba(0,0,0,.7);text-align:center}#hero img{display:block;width:100%;border-radius:14px}#hero div{margin-top:8px;font:400 40px/1.05 Anton;color:#14161c}#hero span{font:800 22px Mont;color:#888}
#mou{position:absolute;left:90px;right:90px;top:300px;opacity:0;z-index:12;padding:24px;border-radius:28px;background:rgba(8,10,15,.92);border:3px solid #FFC42E;text-align:center}
.mrow{display:flex;justify-content:center;align-items:center;gap:26px}.mrow span{font:400 64px/1 Anton;color:#fff}.mrow b{font-size:70px}.mbig{margin-top:6px;font:400 130px/1 Anton;color:#FFC42E}.msub{font:900 30px Mont;color:#ccc;letter-spacing:.08em}
#evs{position:absolute;left:40px;right:40px;top:300px;display:grid;grid-template-columns:1fr 1fr;gap:18px;opacity:0;z-index:12}.ev{display:flex;align-items:center;gap:14px;padding:16px 18px;border-radius:22px;background:rgba(8,10,15,.9);border:3px solid #FFC42E;opacity:0}
.ev i{font-style:normal;font-size:64px}.ev b{font:400 40px/1.05 Anton;color:#fff}
#stamp{position:absolute;left:0;right:0;top:600px;margin:0 auto;width:max-content;padding:20px 50px;border:12px solid #FF4646;border-radius:20px;font:400 140px/1 Anton;color:#FF4646;opacity:0;z-index:14;background:rgba(0,0,0,.35)}
#vig{position:absolute;inset:0;pointer-events:none;background:radial-gradient(80% 60% at 50% 45%,rgba(0,0,0,0) 50%,rgba(0,0,0,.6) 100%);z-index:2}#flash{position:absolute;inset:0;background:#fff;opacity:0;z-index:25;pointer-events:none}
#wm{position:absolute;left:0;right:0;top:190px;text-align:center;font:800 24px Mont;letter-spacing:.34em;color:rgba(255,255,255,.55);z-index:20}
#cred{position:absolute;left:40px;right:40px;top:1640px;text-align:center;font:700 17px Mont;color:rgba(255,255,255,.55);z-index:20}
#series{position:absolute;left:0;right:0;top:250px;margin:0 auto;width:max-content;padding:8px 22px;border-radius:30px;background:#FFC42E;color:#111;font:900 28px Mont;letter-spacing:.06em;opacity:0;z-index:12}
#hook{position:absolute;left:40px;right:40px;top:120px;text-align:center;opacity:0;z-index:12;padding:26px 10px;border-radius:30px;background:rgba(8,10,15,.86)}
#hook small{display:block;font:900 44px Mont;color:#fff;letter-spacing:.14em}#hook b{display:block;font:400 240px/1 Anton;color:#FFC42E}#hook span{display:block;font:400 66px/1.05 Anton;color:#fff}
#hook i{display:inline-block;margin-top:14px;padding:8px 30px;border-radius:40px;background:#FF4FA3;color:#111;font:400 64px/1.1 Anton;font-style:normal}
.th{position:absolute;left:50px;top:250px;padding:10px 24px;border-radius:40px;background:rgba(8,10,15,.9);border:2px solid #FFC42E;font:400 44px/1 Anton;color:#fff;letter-spacing:.03em;opacity:0;z-index:30}
.card{position:absolute;opacity:0;padding:14px 14px 16px;border-radius:24px;background:#fff;box-shadow:0 30px 70px rgba(0,0,0,.7);z-index:8;text-align:center}
.card img{display:block;margin:0 auto;border-radius:14px;object-fit:cover}.ct{margin-top:10px;font:400 50px/1.05 Anton;color:#14161c;letter-spacing:.02em}.cs{margin-top:6px;font:700 26px Mont;color:#5b6070}
.ci{margin:10px 6px 0;padding-top:10px;border-top:2px solid #e3e3e8;text-align:left;font:700 26px/1.32 Mont;color:#2a2d36}
.tg{position:absolute;left:-12px;top:-22px;padding:8px 20px;border-radius:30px;font:900 28px Mont;color:#111;box-shadow:0 6px 16px rgba(0,0,0,.4);z-index:2}
.pl{position:absolute;opacity:0;translate:-50% -50%;padding:8px 20px;border-radius:30px;background:rgba(8,10,15,.9);border:2px solid #FF4FA3;font:900 32px Mont;color:#fff;white-space:nowrap;z-index:6}.pl.g{border-color:#3CFF96;color:#3CFF96}.pl.y{border-color:#FFC42E;color:#FFC42E}
#facts{position:absolute;left:50px;right:50px;top:340px;opacity:0;display:flex;gap:20px;z-index:9}#facts div{flex:1;padding:16px;border-radius:24px;background:rgba(8,10,15,.9);border:3px solid #3CFF96;text-align:center}
#facts b{display:block;font:400 96px/1 Anton;color:#3CFF96}#facts span{font:900 30px Mont;color:#fff;letter-spacing:.14em}
#rank{position:absolute;left:40px;right:40px;top:350px;opacity:0;z-index:9}.rk{display:flex;gap:18px;align-items:center;margin-bottom:18px;padding:14px;border-radius:24px;background:rgba(8,10,15,.92);border:3px solid #555}
.rk.hot{border-color:#FFC42E;box-shadow:0 0 40px rgba(255,196,46,.4)}.rk img{width:300px;height:190px;object-fit:cover;border-radius:16px;flex:none}.rk div{flex:1}
.rk i{display:block;font:400 56px/1 Anton;color:#FFC42E;font-style:normal}.rk b{display:block;font:400 40px/1.05 Anton;color:#fff;margin-top:4px}.rk span{display:block;margin:6px 0 10px;font:800 26px Mont;color:#ccc}
.rk u{display:block;height:16px;border-radius:8px;background:#FFC42E;text-decoration:none}
#now{position:absolute;left:50px;right:50px;top:420px;opacity:0;z-index:9}#now p{display:flex;flex-direction:column;margin-bottom:20px;padding:22px 26px;border-radius:24px;background:rgba(8,10,15,.92);border:3px solid #3CDCFF;font:800 38px/1.25 Mont;color:#fff}
#now p b{font:400 64px/1 Anton;color:#3CDCFF;margin-bottom:6px}
.wpin{position:absolute;opacity:0;translate:-50% -50%;display:flex;flex-direction:column;align-items:center;z-index:6}.wpin i{font-style:normal;font-size:96px;line-height:1;filter:drop-shadow(0 6px 10px rgba(0,0,0,.7))}
.wpin b{margin-top:4px;padding:6px 16px;border-radius:18px;background:rgba(8,10,15,.88);border:2px solid #3CFF96;font:800 30px Mont;color:#fff;white-space:nowrap}
#cta{position:absolute;left:50px;right:50px;top:420px;opacity:0;text-align:center;z-index:12}#cta b{display:block;padding:24px;border-radius:26px;background:#FFC42E;color:#111;font:400 86px/1 Anton}
.opts{display:flex;justify-content:center;gap:20px;margin-top:26px}.opts span{padding:16px 34px;border-radius:24px;background:rgba(8,10,15,.9);border:3px solid #fff;font:400 64px/1 Anton;color:#fff}
#cta em{display:inline-block;margin-top:26px;padding:14px 34px;border-radius:30px;background:#FF4FA3;color:#111;font:900 44px Mont;font-style:normal}
.cp{position:absolute;left:40px;right:130px;top:1440px;text-align:center;opacity:0;z-index:35}
.cp div{display:inline-block;font:900 60px/1.12 Mont;color:#fff;-webkit-text-stroke:7px #000;paint-order:stroke fill;text-shadow:0 6px 18px rgba(0,0,0,.8)}"""
audio = (f'<audio id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{END}" data-track-index="1" data-volume="1"></audio><audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.13" data-fade-out="1.5"></audio>' if VOICE
         else f'<audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.55" data-fade-out="1.5"></audio>')
open(f"{P}/index.html", "w").write(f"""<!doctype html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="30">
<div id="sky"></div><div id="stage"><div id="plane"><svg id="world" viewBox="{vb(IND_C, IND_W)}" preserveAspectRatio="xMidYMid slice">{"".join(SVG)}</svg>{ST}</div></div>
{"".join(H)}
{audio}
{"".join(SFX)}
</div><script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(J)}
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>""")
print("END", END, [p["s"] for p in PH])
