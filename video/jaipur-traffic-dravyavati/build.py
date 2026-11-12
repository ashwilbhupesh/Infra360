"""Jaipur traffic: E-W roads vs missing N-S link; Dravyavati elevated road (proposed). Road lines approximate."""
import json, math, os
P = "proj"
ASP = json.load(open("aspects.json"))
LINES = [
    "Nadi ke upar yeh road ab aapke area ke daam badha sakti hai.",
    "Jaipur ki zyada sadkein, jaise Sikar Road, Khatipura Road, Ajmer Road, Shyam Nagar Janpath, New Sanganer Road, Gopalpura Road, Jaipur Jodhpur Road, Haldighati Marg, NH 52 aur Mahal Road, nadi ko 90 degree par kaat ke east se west jaati hain.",
    "Par west Jaipur mein, Dravyavati nadi ke saath, north se south jaane ka koi seedha aur tez raasta nahi hai.",
    "Isliye Sikar Road se Sitapura jaana ho, toh gaadiyan shehar ke beech se ghoom ke jaati hain, aur har chauraahe par jam lagta hai.",
    "Ab Dravyavati nadi ke upar 25 se 30 km ka 6 lane elevated road prastavit hai, single pillar par.",
    "Yeh road in sabhi das sadkon ko seedha jodega. Shehar ke andar jam kam hoga.",
    "Aur jahan connectivity aati hai, wahan ke areas ki demand aur daam badhte hain.",
    "Aapko kis road par sabse zyada jam milta hai? Comment karo.",
]
VOICE = os.path.exists("rec/phrases.json")
if VOICE: PH = json.load(open("rec/phrases.json"))
else:
    PH = []; t = .3
    for l in LINES:
        d = len(l) / 15 + .15; PH.append({"s": round(t, 2), "e": round(t + d, 2), "t": l}); t += d + .35
def S(k): return PH[k]["s"]
def E(k): return PH[k]["e"]
def wt(k, w):
    t = PH[k]["t"]; i = t.lower().find(w.lower()); assert i >= 0, (k, w)
    return S(k) + (E(k) - S(k)) * i / len(t)
END = round(E(7) + 1.3, 2)
def wp(lat, lon):
    n = 2 ** 13
    return (((lon + 180) / 360 * n) - 5791) * 256, (((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n) - 3466) * 256
SVG, H, J, SFX, CARDS = [], [], [], [], []
def vb(c, w): h = w * 1920 / 1080; return f"{c[0] - w / 2:.1f} {c[1] - h / 2:.1f} {w:.1f} {h:.1f}"
def sfx(n, t, v=.3): SFX.append(f'<audio id="sx{len(SFX)}" class="clip" src="assets/sfx/{n}.mp3" data-start="{t:.2f}" data-duration="2" data-track-index="{20 + len(SFX)}" data-volume="{v}"></audio>')
GRN, GOLD, PINK = "#3CE65A", "#FFC42E", "#FF4FA3"
CAMS = []
def zoom(t, c1, w1, d=1.0):
    c0, w0 = CAMS[-1][2], CAMS[-1][3]
    J.append(f'zoomTo({t:.2f}, [{c0[0]:.1f},{c0[1]:.1f}], {w0:.1f}, [{c1[0]:.1f},{c1[1]:.1f}], {w1:.1f}, {d});'); CAMS.append((t, d, c1, w1))
def scr(p, t):
    c, w = CAMS[0][2], CAMS[0][3]
    for t0, d, c1, w1 in CAMS:
        if t0 + d <= t + 1e-6: c, w = c1, w1
    h = w * 1920 / 1080
    return ((p[0] - (c[0] - w / 2)) / w * 1080, (p[1] - (c[1] - h / 2)) / h * 1920)
def pd(pts): return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
def smooth(pts, n=10):
    out = []; P_ = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = P_[i - 1], P_[i], P_[i + 1], P_[i + 2]
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(tuple(.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    return out + [pts[-1]]
def fitb(pts, top, bot, pad=1.15):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    w = max((x1 - x0) * pad, (y1 - y0) * pad * 1080 / (bot - top))
    return ((x0 + x1) / 2, (y0 + y1) / 2 - ((top + bot) / 2 - 960) * w / 1080), w

# ---------- base ----------
SVG.append('<rect x="-900000" y="-900000" width="2000000" height="2000000" style="fill:#1b1b1d"/>')
for href, x, y, w, h in [("bm4.jpg", -302848, -363008, 786432, 786432), ("bm5.jpg", -171776, -166400, 327680, 393216), ("bm7.webp", -40704, -35328, 81920, 65536),
                         ("jp11.webp", 4352, -6656, 7168, 8192), ("jp14.webp", 7040, -2176, 1536, 1792)]:
    SVG.append(f'<image href="assets/img/{href}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="none"/>')
SVG.append('<rect id="shade" x="-900000" y="-900000" width="2000000" height="2000000" style="fill:#000;opacity:.25"/>')
BD = json.load(open("data/bounds.json"))
def pdr(rings): return " ".join("M" + " L".join(f"{wp(la, lo)[0]:.1f} {wp(la, lo)[1]:.1f}" for lo, la in r) + " Z" for r in rings)
SVG.append(f'<path id="bind" d="{pdr(BD["india"])}" style="fill:#9A4E1C;fill-opacity:.0;stroke:#fff;stroke-width:3;vector-effect:non-scaling-stroke"/>')
SVG.append(f'<path id="braj" d="{pdr(BD["raj"])}" style="fill:#1530C8;fill-opacity:0;stroke:#fff;stroke-width:4;vector-effect:non-scaling-stroke;opacity:0"/>')
SVG.append(f'<path id="bjp" d="{pdr(BD["jaipur"])}" style="fill:#FFC42E;fill-opacity:0;stroke:#fff;stroke-width:4;vector-effect:non-scaling-stroke;opacity:0"/>')
# river traced from the creator's Google Maps screenshots (approximate)
RIV = [(26.958, 75.788), (26.951, 75.790), (26.945, 75.789), (26.940, 75.786), (26.936, 75.790), (26.932, 75.795), (26.926, 75.789), (26.919, 75.784), (26.912, 75.781),
       (26.905, 75.779), (26.898, 75.776), (26.892, 75.771), (26.886, 75.770), (26.880, 75.772), (26.873, 75.775), (26.868, 75.782), (26.861, 75.786), (26.854, 75.788),
       (26.846, 75.789), (26.838, 75.791), (26.829, 75.794), (26.818, 75.799), (26.808, 75.806), (26.800, 75.815), (26.795, 75.827), (26.793, 75.838), (26.791, 75.848),
       (26.789, 75.860), (26.786, 75.872), (26.782, 75.884), (26.774, 75.895), (26.760, 75.905), (26.745, 75.912), (26.725, 75.920), (26.700, 75.929), (26.675, 75.932),
       (26.650, 75.929), (26.625, 75.925), (26.600, 75.920)]
RP = smooth([wp(a_, b_) for a_, b_ in RIV], 6)
ELV = smooth([wp(a_, b_) for a_, b_ in RIV[:31]], 6)
def plen(pts): return sum(math.hypot(b_[0] - a_[0], b_[1] - a_[1]) for a_, b_ in zip(pts, pts[1:]))
PXKM = 256 * 2 ** 13 / 40075 / math.cos(math.radians(26.85))
print("river km", round(plen(RP) / PXKM, 1), "elevated km", round(plen(ELV) / PXKM, 1))
SVG.append(f'<path id="rvg" d="{pd(RP)}" pathLength="1" style="fill:none;stroke:#2EA8FF;stroke-width:22;stroke-opacity:.35;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1"/>'
           f'<path id="rv" d="{pd(RP)}" pathLength="1" style="fill:none;stroke:#5EC8FF;stroke-width:7;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1"/>')
SVG.append(f'<path id="elp" d="{pd(ELV)}" pathLength="1" style="fill:none;stroke:{GOLD};stroke-width:14;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1;filter:drop-shadow(0 0 12px {GOLD})"/>')
SVG.append(f'<path id="bufz" d="{pd(ELV)}" style="fill:none;stroke:#3CE65A;stroke-width:44;stroke-opacity:.0;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-linejoin:round"/>')
SVG.append(f'<path id="elg" d="{pd(ELV)}" pathLength="1" style="fill:none;stroke:{GOLD};stroke-width:20;stroke-opacity:.35;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1"/>'
           f'<path id="el" d="{pd(ELV)}" pathLength="1" style="fill:none;stroke:{GOLD};stroke-width:6;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1"/>'
           f'<path id="eld" d="{pd(ELV)}" style="fill:none;stroke:#111;stroke-width:6;vector-effect:non-scaling-stroke;stroke-dasharray:10 10;opacity:0"/>')
CROSS = {"Sikar Road": (26.932, 75.795), "Khatipura Road": (26.919, 75.784), "Ajmer Road": (26.905, 75.779), "Shyam Nagar Janpath": (26.892, 75.771), "New Sanganer Road": (26.880, 75.772), "Gopalpura Road": (26.861, 75.786), "Jaipur Jodhpur Road": (26.835, 75.792), "Haldighati Marg": (26.806, 75.808), "NH 52": (26.795, 75.827), "Mahal Road": (26.788, 75.862)}
for i, (nm, (la, lo)) in enumerate(CROSS.items()):
    x, y = wp(la, lo)
    SVG.append(f'<g id="cx{i}" style="opacity:0"><circle cx="{x:.1f}" cy="{y:.1f}" r="1" class="dg" style="fill:#fff;opacity:.35"/><circle cx="{x:.1f}" cy="{y:.1f}" r="1" class="dc" style="fill:#fff;stroke:{GOLD};stroke-width:3;vector-effect:non-scaling-stroke"/></g>')
SVG.append('<rect id="dim" x="-900000" y="-900000" width="2000000" height="2000000" style="fill:#000;opacity:0"/>')

def card(cid, img, t0, t1, title, sub="", tag=None, top=400, maxw=900, maxh=600):
    a = ASP[img]; w = maxw; h = w / a
    if h > maxh: h = maxh; w = h * a
    cw = w + 28; lx = (1080 - cw) / 2
    tg = f'<div class="tg" style="background:{tag[1]}">{tag[0]}</div>' if tag else ''
    H.append(f'<div class="card" id="{cid}" style="left:{lx:.0f}px;top:{top}px;width:{cw:.0f}px">{tg}<div class="iw" style="width:{w:.0f}px;height:{h:.0f}px"><img src="assets/img/{img}.jpg" style="width:{w:.0f}px;height:{h:.0f}px"/><i class="scan"></i></div>'
             f'<div class="ct">{title}</div>' + (f'<div class="cs">{sub}</div>' if sub else '') + '</div>')
    J.append(f'tl.fromTo("#{cid}", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:.2}}, {t0:.2f}); tl.fromTo("#{cid} img", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:.55, ease:"power2.inOut"}}, {t0:.2f});'
             f'tl.fromTo("#{cid} .scan", {{left:"0%", opacity:1}}, {{left:"100%", duration:.55, ease:"power2.inOut"}}, {t0:.2f}); tl.to("#{cid} .scan", {{opacity:0, duration:.15}}, {t0 + .55:.2f}); tl.to("#{cid}", {{opacity:0, duration:.2}}, {t1 - .2:.2f});')
    sfx("pop", t0, .25)
def lab(i, p, text, t, until, at, dx=0, dy=0, cls=""):
    x, y = scr(p, at); H.append(f'<div class="ml {cls}" id="{i}" style="left:{min(max(x + dx, 40 + len(text) * 9), 1040 - len(text) * 9):.0f}px;top:{y + dy:.0f}px;opacity:0">{text}</div>')
    J.append(f'tl.fromTo("#{i}", {{opacity:0, scale:.5}}, {{opacity:1, scale:1, duration:.25, ease:"back.out(2)", immediateRender:false}}, {t:.2f}); tl.fromTo("#{i}", {{opacity:1}}, {{opacity:0, duration:.2, immediateRender:false}}, {until - .2:.2f});')
def mover(mid, pts, t0, d, col, until, N=70):
    L = [0.0]
    for a_, b_ in zip(pts, pts[1:]): L.append(L[-1] + math.hypot(b_[0] - a_[0], b_[1] - a_[1]))
    samp = []
    for k in range(N + 1):
        tg = L[-1] * k / N; j = next((m for m in range(1, len(L)) if L[m] >= tg), len(L) - 1)
        f = (tg - L[j - 1]) / max(1e-6, L[j] - L[j - 1]); a_, b_ = pts[j - 1], pts[j]
        samp.append((a_[0] + (b_[0] - a_[0]) * f, a_[1] + (b_[1] - a_[1]) * f))
    SVG.append(f'<g id="{mid}" style="opacity:0" transform="translate({samp[0][0]:.1f},{samp[0][1]:.1f})"><circle class="mvg" r="1" style="fill:{col};opacity:.45"/><circle class="mvc" r="1" style="fill:#fff;stroke:{col};stroke-width:3;vector-effect:non-scaling-stroke"/></g>')
    J.append(f'tl.to("#{mid}", {{opacity:1, duration:.1}}, {t0:.2f}); tl.to("#{mid}", {{opacity:0, duration:.2}}, {until:.2f});')
    for k in range(1, N + 1):
        x, y = samp[k]; J.append(f'tl.to("#{mid}", {{attr:{{transform:"translate({x:.1f},{y:.1f})"}}, duration:{d / N:.4f}, ease:"none"}}, {t0 + d * (k - 1) / N:.4f});')

# ---------- extra layers ----------
CB = json.load(open("data/jaipur_boundary.geojson"))["features"][0]["geometry"]["coordinates"][0]
CITYP = [wp(la, lo) for lo, la in CB[::2]]
SVG.insert(-1, f'<path id="city" d="M{" L".join(f"{x:.1f} {y:.1f}" for x, y in CITYP)} Z" style="fill:#fff;fill-opacity:.05;stroke:#F3E6C8;stroke-width:3;stroke-dasharray:10 8;vector-effect:non-scaling-stroke;opacity:0"/>')
def perp(la, lo, km_):
    p = wp(la, lo); j = min(range(len(RP)), key=lambda k: (RP[k][0] - p[0]) ** 2 + (RP[k][1] - p[1]) ** 2)
    a_, b_ = RP[max(0, j - 3)], RP[min(len(RP) - 1, j + 3)]; dx, dy = b_[0] - a_[0], b_[1] - a_[1]; L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L; c = RP[j]; d = km_ * PXKM
    return [(c[0] - nx * d, c[1] - ny * d), c, (c[0] + nx * d, c[1] + ny * d)]
EW = {nm.upper(): ll for nm, ll in CROSS.items()}
EWP = {}
for i, (nm, pts) in enumerate(EW.items()):
    P_ = perp(*pts, 2.6); EWP[nm] = P_
    SVG.insert(-1, f'<path class="ew" id="ew{i}" d="{pd(P_)}" pathLength="1" style="fill:none;stroke:{GOLD};stroke-width:30;stroke-opacity:.3;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>'
                       f'<path class="ew" id="ewc{i}" d="{pd(P_)}" pathLength="1" style="fill:none;stroke:{GOLD};stroke-width:11;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>')
# red "gap" strip along the river (no direct N-S route)
GAPP = ELV
SVG.insert(-1, f'<path id="gap" d="{pd(GAPP)}" style="fill:none;stroke:#E5484D;stroke-width:16;stroke-dasharray:22 16;vector-effect:non-scaling-stroke;opacity:0"/>')
# zig-zag route through the centre
ZZ = smooth([wp(*p) for p in [(26.95, 75.79), (26.935, 75.81), (26.926, 75.822), (26.918, 75.83), (26.912, 75.818), (26.90, 75.815), (26.885, 75.82), (26.865, 75.812), (26.845, 75.815), (26.82, 75.83), (26.80, 75.85), (26.786, 75.872)]], 8)
SVG.insert(-1, f'<path id="zz" d="{pd(ZZ)}" pathLength="1" style="fill:none;stroke:#E5484D;stroke-width:9;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1;opacity:.95"/>')
JAMS = [(26.935, 75.81), (26.926, 75.822), (26.917, 75.828), (26.90, 75.815), (26.875, 75.817), (26.848, 75.814), (26.815, 75.834)]
for i, (la, lo) in enumerate(JAMS):
    x, y = wp(la, lo)
    SVG.insert(-1, f'<g class="jam" id="jm{i}" style="opacity:0"><circle cx="{x:.1f}" cy="{y:.1f}" r="1" class="dg" style="fill:#E5484D;opacity:.45"/><circle cx="{x:.1f}" cy="{y:.1f}" r="1" class="dc" style="fill:#E5484D;stroke:#fff;stroke-width:2;vector-effect:non-scaling-stroke"/></g>')
AREAS = [("SIKAR ROAD", 26.932, 75.795), ("SODALA", 26.904, 75.779), ("MANSAROVAR", 26.868, 75.782), ("SANGANER", 26.818, 75.799), ("SITAPURA", 26.786, 75.872)]
for i, (nm, la, lo) in enumerate(AREAS):
    x, y = wp(la, lo)
    SVG.insert(-1, f'<circle class="ar" id="ar{i}" cx="{x:.1f}" cy="{y:.1f}" r="230" style="fill:{GOLD};fill-opacity:.18;stroke:{GOLD};stroke-width:2;vector-effect:non-scaling-stroke;opacity:0"/>')

# ---------- cameras ----------
def bbr(rings): return [wp(la, lo) for r in rings for lo, la in r]
RAJ_C, RAJ_W = fitb(bbr(BD["raj"]), 700, 1380, 1.1)
ALL = [p for P_ in EWP.values() for p in P_]
CT_C, CT_W = fitb(ALL, 420, 1380, 1.25)
RV_C, RV_W = fitb(ELV, 420, 1380, 1.2)
J.append('const VB = document.getElementById("world"); function setDots(w){ document.querySelectorAll(".dc").forEach(e=>e.setAttribute("r", w/90)); document.querySelectorAll(".dg").forEach(e=>e.setAttribute("r", w/40)); document.querySelectorAll(".mvc").forEach(e=>e.setAttribute("r", w/70)); document.querySelectorAll(".mvg").forEach(e=>e.setAttribute("r", w/26)); }'
         'function zoomTo(t, c0, w0, c1, w1, d){ const o = {z:0}; tl.to(o, {z:1, duration:d, ease:"power2.inOut", onUpdate:()=>{ const w = Math.exp(Math.log(w0) + (Math.log(w1) - Math.log(w0)) * o.z); const f = Math.abs(w0 - w1) < 1e-6 ? o.z : (w0 - w) / (w0 - w1); const cx = c0[0] + (c1[0] - c0[0]) * f, cy = c0[1] + (c1[1] - c0[1]) * f; const h = w * 1920 / 1080; VB.setAttribute("viewBox", (cx - w / 2) + " " + (cy - h / 2) + " " + w + " " + h); setDots(w); }}, t); }')
CAMS.append((0, 0, RV_C, RV_W * 1.15)); J.append(f'tl.set("#world", {{attr:{{viewBox:"{vb(RV_C, RV_W * 1.15)}"}}}}, 0);')
J.append('tl.set(["#bind", "#braj", "#bjp"], {opacity:0}, 0);')
zoom(0, RV_C, RV_W, 2.0)

def lux(i, html, t, until, x, y, cls=""):
    H.append(f'<div class="lx {cls}" id="lx{i}" style="left:{x}px;top:{y}px">{html}</div>')
    J.append(f'tl.fromTo("#lx{i}", {{opacity:0, y:24, clipPath:"inset(0 100% 0 0)"}}, {{opacity:1, y:0, clipPath:"inset(0 0% 0 0)", duration:.45, ease:"power3.out"}}, {t:.2f}); tl.to("#lx{i}", {{opacity:0, y:-14, duration:.3}}, {until - .3:.2f});')
    sfx("click-soft", t, .3)

# ---------- 0 HOOK: river + elevated road + price ----------
J.append(f'tl.to(["#rv", "#rvg"], {{strokeDashoffset:0, duration:.6, ease:"power2.out"}}, 0); tl.to(["#el", "#elg"], {{strokeDashoffset:0, duration:1.0, ease:"power2.inOut"}}, .25); tl.to("#elp", {{strokeDashoffset:0, duration:1.0, ease:"power2.inOut"}}, .25);')
mover("car0", ELV, .3, 1.6, GOLD, S(1) - .2, 50)
J.append(f'tl.to(["#el", "#elg", "#elp"], {{opacity:0, duration:.3}}, {S(1) - .2:.2f}); tl.set(["#el", "#elg", "#elp"], {{strokeDashoffset:1, opacity:1}}, {S(1) + .2:.2f});')
H.append('<div id="hook"><small>NADI KE UPAR YEH ROAD</small><b>AAPKE AREA KE DAAM</b><span>BADHA SAKTI HAI &#9650;</span></div>')
J.append(f'tl.fromTo("#hook", {{opacity:1, scale:1.12}}, {{opacity:1, scale:1, duration:.4, ease:"power3.out"}}, 0); tl.fromTo("#hook span", {{opacity:0, y:20}}, {{opacity:1, y:0, duration:.4, ease:"power3.out"}}, {wt(0, "daam") - .1:.2f}); tl.to("#hook", {{opacity:0, y:-30, duration:.3}}, {S(1) - .2:.2f});')
lab("lriv", RP[25], "DRAVYAVATI", .4, S(1) - .1, 1.0, dx=-190, cls="blue")
lab("lelv", ELV[60], "ELEVATED ROAD", .9, S(1) - .1, 1.0, dx=200, cls="y")
sfx("impact-bass-1", 0, .45); sfx("whoosh", .25, .3); sfx("sparkle", wt(0, "daam"), .3)

# ---------- 1 E-W roads ----------
zoom(S(1) - .3, CT_C, CT_W, .9)
J.append(f'tl.to("#city", {{opacity:1, duration:.4}}, {S(1):.2f}); tl.to(["#rv", "#rvg"], {{opacity:.35, duration:.3}}, {S(1):.2f});')
for i, nm in enumerate(EW):
    t = wt(1, {"NH 52": "NH 52"}.get(nm, nm.title().replace("Nh 52", "NH 52").split(" Road")[0].split(" Marg")[0])) - .1
    J.append(f'tl.to(["#ew{i}", "#ewc{i}"], {{strokeDashoffset:0, duration:.6, ease:"power2.out"}}, {t:.2f});'); sfx("whoosh-short", t, .25)
    P_ = EWP[nm]; lab(f"lew{i}", P_[1], nm, t + .2, S(2) - .1, S(1) + .8, dx=-1000 if i % 2 == 0 else 1000, dy=0, cls="y sm")
lux(0, "<b>90&deg;</b> NADI KO KAAT-TI SADKEIN", wt(1, "90") - .1, S(2), 200, 300)

# ---------- 2 gap ----------
J.append(f'tl.to(".ew", {{opacity:.25, duration:.3}}, {S(2):.2f}); tl.to(["#rv", "#rvg"], {{opacity:1, duration:.3}}, {S(2):.2f}); tl.fromTo(["#rvg"], {{strokeWidth:22}}, {{strokeWidth:46, duration:.4, yoyo:true, repeat:3}}, {S(2) + .2:.2f});')
J.append(f'tl.to("#gap", {{opacity:1, duration:.3}}, {wt(2, "north"):.2f}); tl.fromTo("#gap", {{strokeDashoffset:0}}, {{strokeDashoffset:-300, duration:2.5, ease:"none"}}, {wt(2, "north"):.2f}); tl.to("#gap", {{opacity:0, duration:.3}}, {S(3) - .1:.2f});')
lux(1, "<b>&#10006;</b> NORTH &ndash; SOUTH: KOI SEEDHA RAASTA NAHI", wt(2, "north") - .1, S(3), 90, 300, "red")
sfx("impact-bass-1", wt(2, "north"), .4)

# ---------- 3 zig-zag + jams ----------
J.append(f'tl.to("#zz", {{strokeDashoffset:0, duration:{E(3) - S(3) - .6:.2f}, ease:"none"}}, {S(3) + .2:.2f}); tl.to("#zz", {{opacity:0, duration:.3}}, {S(5) - .2:.2f});')
mover("car1", ZZ, S(3) + .2, E(3) - S(3) - .6, "#E5484D", S(4) - .1, 60)
for i in range(len(JAMS)):
    t = S(3) + .5 + i * (E(3) - S(3) - .8) / len(JAMS)
    J.append(f'tl.to("#jm{i}", {{opacity:1, duration:.15}}, {t:.2f}); tl.fromTo("#jm{i} .dg", {{opacity:.6}}, {{opacity:.15, duration:.35, yoyo:true, repeat:-1}}, {t:.2f});'); sfx("click-soft", t, .2)
lab("lsk", ZZ[0], "SIKAR ROAD", S(3) + .1, S(4) - .1, S(3) + .5, dx=-150)
lab("lst", ZZ[-1], "SITAPURA", S(3) + .1, S(4) - .1, S(3) + .5, dy=50)
lux(2, "JAM &bull; JAM &bull; JAM", wt(3, "jam") - .2, S(4), 330, 300, "red")
H.append('<div id="clock">ZYADA TIME &bull; ZYADA FUEL</div>')
J.append(f'tl.fromTo("#clock", {{opacity:0, scale:.7}}, {{opacity:1, scale:1, duration:.35, ease:"power3.out"}}, {wt(3, "ghoom"):.2f}); tl.to("#clock", {{opacity:0, duration:.2}}, {S(4) - .1:.2f});')

# ---------- 4 solution: elevated road ----------
zoom(S(4) - .3, RV_C, RV_W, .9)
J.append(f'tl.to(["#city", ".ew"], {{opacity:.15, duration:.4}}, {S(4) - .2:.2f}); tl.to(["#el", "#elg", "#elp"], {{strokeDashoffset:0, duration:1.4, ease:"power2.inOut"}}, {S(4) + .1:.2f});')
mover("car2", ELV, S(4) + .3, 1.6, GOLD, S(5) + 2, 50)
sfx("riser", S(4), .3)
lux(3, "<b>25&ndash;30 KM</b> &middot; 6 LANE &middot; SINGLE PILLAR", wt(4, "25") - .1, S(5) - .2, 60, 300)
H.append('''<div id="xsec"><svg viewBox="0 0 900 380" width="900" height="380">
<rect x="0" y="300" width="900" height="80" fill="#2E8FD8"/><path d="M0 300 Q 225 285 450 300 T 900 300" fill="none" stroke="#7FD0FF" stroke-width="4"/>
<rect class="pil" x="415" y="140" width="70" height="165" fill="#C9C2B4"/>
<g class="deck"><rect x="60" y="110" width="780" height="34" fill="#E9E3D6"/><rect x="60" y="104" width="780" height="8" fill="#C9A24A"/>
<rect class="cr a" x="100" y="86" width="60" height="22" rx="5" fill="#F3E6C8"/><rect class="cr b" x="640" y="86" width="60" height="22" rx="5" fill="#C9A24A"/></g>
<text x="450" y="60" text-anchor="middle" font-family="Mont" font-weight="700" font-size="30" letter-spacing="6" fill="#F3E6C8">SINGLE PILLAR &middot; 6 LANE</text>
<text x="450" y="355" text-anchor="middle" font-family="Mont" font-weight="700" font-size="26" letter-spacing="6" fill="#fff">DRAVYAVATI</text></svg></div>''')
J.append(f'tl.fromTo("#xsec", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:.45, ease:"power3.out"}}, {wt(4, "single") - .4:.2f}); tl.fromTo("#xsec .pil", {{scaleY:0, transformOrigin:"50% 100%"}}, {{scaleY:1, duration:.4, ease:"power3.out"}}, {wt(4, "single") - .3:.2f}); tl.fromTo("#xsec .deck", {{opacity:0, y:-40}}, {{opacity:1, y:0, duration:.4, ease:"power3.out"}}, {wt(4, "single"):.2f});'
         f'tl.fromTo("#xsec .a", {{x:0}}, {{x:620, duration:2.2, ease:"none", repeat:2}}, {wt(4, "single") + .2:.2f}); tl.fromTo("#xsec .b", {{x:0}}, {{x:-560, duration:2.0, ease:"none", repeat:2}}, {wt(4, "single") + .2:.2f}); tl.to("#xsec", {{opacity:0, duration:.25}}, {S(5) - .1:.2f});')

# ---------- 5 connections, jams fade ----------
for i, nm in enumerate(CROSS):
    t = wt(5, "das sadkon") - .1 + i * .18
    J.append(f'tl.to("#cx{i}", {{opacity:1, duration:.2}}, {t:.2f}); tl.to("#cx{i}", {{opacity:0, duration:.3}}, {S(6) + .2:.2f});')
    lab(f"rl{i}", wp(*CROSS[nm]), nm.upper(), t, S(6), S(5), dx=-1000 if i % 2 == 0 else 1000, cls="y sm"); sfx("pop", t, .25)
    J.append(f'tl.to(["#ew{i}", "#ewc{i}"], {{opacity:1, duration:.3}}, {t:.2f});')
J.append(f'tl.to(".jam", {{opacity:0, duration:.4, stagger:.1}}, {wt(5, "jam kam"):.2f});')
lux(4, "<b>&#10004;</b> JAM KAM", wt(5, "jam kam") - .1, S(6), 340, 300, "grn")

# ---------- 6 real estate ----------
for i, (nm, la, lo) in enumerate(AREAS):
    t = S(6) + .2 + i * .3
    J.append(f'tl.to("#ar{i}", {{opacity:1, duration:.35}}, {t:.2f}); tl.fromTo("#ar{i}", {{attr:{{r:80}}}}, {{attr:{{r:230}}, duration:.6, ease:"power3.out", immediateRender:false}}, {t:.2f}); tl.to("#ar{i}", {{opacity:0, duration:.3}}, {S(7):.2f});')
    lab(f"la{i}", wp(la, lo), nm, t + .1, S(7), S(6) + .5, dx=-190 if i % 2 == 0 else 190); sfx("click-soft", t, .2)
lux(5, "DEMAND <b>&#9650;</b> &nbsp;DAAM <b>&#9650;</b>", wt(6, "demand") - .1, S(7), 290, 300, "grn")

# ---------- 7 CTA ----------
H.append('<div id="cta"><b>AAPKO KIS ROAD PAR SABSE ZYADA JAM MILTA HAI?</b><span>COMMENT KARO</span></div>')
J.append(f'tl.to("#dim", {{opacity:.5, duration:.3}}, {S(7):.2f}); tl.fromTo("#cta", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.45, ease:"power3.out"}}, {S(7):.2f}); tl.to("#cta span", {{scale:1.06, duration:.4, yoyo:true, repeat:3}}, {wt(7, "Comment"):.2f});')
sfx("sparkle", wt(7, "Comment"), .3)

# captions
HI = ["daam", "Ajmer Road", "Khatipura", "Shyam Nagar Janpath", "Janpath", "Gopalpura", "New Sanganer", "90 degree", "Jaipur Jodhpur Road", "Haldighati Marg", "NH 52", "Mahal Road", "das sadkon", "east se west", "north se south", "Dravyavati", "jam", "25 se 30 km", "6 lane elevated road", "single pillar", "Sikar Road", "New Sanganer Road", "Tonk Road", "jam kam", "demand", "Sitapura", "Comment"]
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
    H.append('<video id="face" class="clip" src="assets/face.mp4" data-start="0" data-duration="1.8" data-track-index="2" muted playsinline></video>')
    J.append('tl.set("#face", {opacity:1}, 0); tl.to("#face", {opacity:0, scale:1.06, duration:.15}, 1.45);')
H.append('<div id="cred">River traced from Google Maps (approx.) &middot; road crossings approximate &middot; elevated road proposed (DPR stage), alignment indicative &middot; Source: Dainik Bhaskar &middot; Imagery: Sentinel-2 (EOX), NASA Blue Marble</div>')
CSS = """@font-face{font-family:Anton;src:url(assets/fonts/anton.woff2)}@font-face{font-family:Mont;font-weight:700;src:url(assets/fonts/mont700.woff2)}@font-face{font-family:Mont;font-weight:800;src:url(assets/fonts/mont800.woff2)}@font-face{font-family:Mont;font-weight:900;src:url(assets/fonts/mont900.woff2)}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#1b1b1d}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif}#world{position:absolute;inset:0;width:1080px;height:1920px}.y{color:#111;background:#FFC42E;border-radius:6px;padding:0 6px}
#face{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:40}
#clouds{position:absolute;inset:0;z-index:15;pointer-events:none;overflow:hidden}#clouds img{position:absolute;left:-260px;top:-240px;width:1600px;height:2400px}
#cred{position:absolute;left:40px;right:40px;top:1650px;text-align:center;font:700 17px Mont;color:rgba(255,255,255,.6);z-index:20}
#rate{position:absolute;left:0;right:0;top:640px;text-align:center;opacity:0;z-index:16}#rate b{display:inline-block;padding:12px 30px;border-radius:14px;background:#19C25A;color:#fff;font:400 78px/1 Anton;box-shadow:0 8px 30px rgba(0,0,0,.6)}
#title{position:absolute;left:0;right:0;top:280px;text-align:center;opacity:0;z-index:16}#title small{display:inline-block;padding:8px 22px;border-radius:10px;background:#fff;color:#111;font:900 34px Mont}
#title b{display:block;margin-top:14px;font:400 130px/1 Anton;color:#FFC42E;text-shadow:0 0 30px rgba(255,196,46,.6),0 6px 30px #000;font-weight:400}
.ml{position:absolute;opacity:0;translate:-50% -50%;padding:6px 16px;border-radius:8px;background:#fff;font:900 34px Mont;color:#111;white-space:nowrap;box-shadow:0 6px 16px rgba(0,0,0,.5);z-index:6}.ml.y{background:#FFC42E}.ml.mlab{left:540px;top:1180px;font-size:46px}
.big{position:absolute;left:40px;right:40px;top:290px;opacity:0;text-align:center;z-index:9}.big b{display:block;font:400 130px/1 Anton;color:#5EC8FF;text-shadow:0 0 24px rgba(46,168,255,.6),0 6px 20px #000;font-weight:400}
#b2 b{color:#FFC42E;text-shadow:0 0 24px rgba(255,196,46,.6),0 6px 20px #000}
.big span{display:inline-block;margin-top:8px;padding:8px 22px;border-radius:10px;background:#fff;color:#111;font:900 30px Mont}
#legend{position:absolute;left:50px;top:1290px;opacity:0;display:flex;gap:20px;z-index:9}#legend span{display:flex;align-items:center;gap:10px;padding:8px 16px;border-radius:12px;background:rgba(10,10,12,.85);font:900 28px Mont;color:#fff}#legend i{display:inline-block;width:46px;height:10px;border-radius:5px}
.card{position:absolute;opacity:0;padding:14px 14px 16px;border-radius:24px;background:#fff;box-shadow:0 30px 70px rgba(0,0,0,.7);z-index:8;text-align:center}
.iw{position:relative;margin:0 auto;border-radius:14px;overflow:hidden}.card img{display:block;border-radius:14px;object-fit:cover}.scan{position:absolute;top:-4%;bottom:-4%;width:8px;margin-left:-4px;background:#fff;box-shadow:0 0 18px #fff,0 0 30px #FFC42E;opacity:0}
.ct{margin-top:10px;font:400 50px/1.05 Anton;color:#14161c;letter-spacing:.02em}.cs{margin-top:6px;font:700 26px Mont;color:#5b6070}
.tg{position:absolute;left:-12px;top:-22px;padding:8px 20px;border-radius:30px;font:900 28px Mont;color:#fff;box-shadow:0 6px 16px rgba(0,0,0,.4);z-index:2}
#stat{position:absolute;left:60px;right:60px;top:330px;opacity:0;padding:28px;border-radius:26px;background:#fff;z-index:10;text-align:center}#stat b{display:block;font:400 64px/1 Anton;color:#D32F2F;font-weight:400}#stat p{margin-top:12px;font:900 34px Mont;color:#111}
#cta{position:absolute;left:50px;right:50px;top:440px;opacity:0;text-align:center;z-index:12}#cta b{display:block;padding:24px;border-radius:26px;background:#5EC8FF;color:#111;font:400 86px/1.02 Anton;font-weight:400}
#cta span{display:inline-block;margin-top:24px;padding:16px 34px;border-radius:30px;background:#fff;color:#111;font:900 46px Mont}

.lx{position:absolute;opacity:0;z-index:14;padding:16px 28px;border-radius:6px;background:linear-gradient(135deg,rgba(14,12,9,.93),rgba(34,27,18,.93));border:1.5px solid #C9A24A;color:#F3E6C8;font:700 32px/1.1 Mont;letter-spacing:.14em;box-shadow:0 18px 50px rgba(0,0,0,.55);white-space:nowrap}
.lx b{font:400 46px/1 Anton;letter-spacing:.04em;background:linear-gradient(180deg,#F7E3A8,#C9A24A);-webkit-background-clip:text;color:transparent}
.lx.red{border-color:#E5484D;font-size:26px}.lx.red b{background:none;color:#E5484D}.lx.grn{border-color:#3CE65A}.lx.grn b{background:none;color:#3CE65A}
#hook{position:absolute;left:60px;right:60px;top:240px;z-index:16;text-align:center;padding:26px 20px;border-radius:8px;border:1.5px solid #C9A24A;background:linear-gradient(135deg,rgba(14,12,9,.92),rgba(34,27,18,.92))}
#hook small{display:block;font:700 30px Mont;letter-spacing:.24em;color:#F3E6C8}#hook b{display:block;margin-top:10px;font:400 96px/1 Anton;background:linear-gradient(180deg,#F7E3A8,#C9A24A);-webkit-background-clip:text;color:transparent}
#hook span{display:inline-block;margin-top:12px;padding:8px 24px;border-radius:4px;background:#3CE65A;color:#0d0d0d;font:400 58px/1 Anton;letter-spacing:.04em}
#clock{position:absolute;left:60px;top:1250px;opacity:0;z-index:14;padding:14px 26px;border-radius:6px;border:1.5px solid #E5484D;background:rgba(14,12,9,.92);color:#E5484D;font:400 48px/1 Anton}
#xsec{position:absolute;left:90px;top:1020px;opacity:0;z-index:14;padding:10px;border-radius:8px;border:1.5px solid #C9A24A;background:linear-gradient(135deg,rgba(14,12,9,.94),rgba(34,27,18,.94));transform-origin:50% 50%}#xsec svg{display:block}
#cta b{border-radius:6px !important;background:linear-gradient(135deg,rgba(14,12,9,.95),rgba(34,27,18,.95)) !important;border:1.5px solid #C9A24A;color:#F3E6C8 !important;font:400 76px/1.05 Anton !important}
#cta span{border-radius:4px !important;background:#C9A24A !important;color:#111 !important;letter-spacing:.22em}
.ml.sm{font-size:24px;padding:4px 12px}
.ml.blue{background:#2EA8FF;color:#fff}
.cp{position:absolute;left:40px;right:130px;top:1440px;text-align:center;opacity:0;z-index:35}
.cp div{display:inline-block;padding:4px 20px 8px;border-radius:10px;background:#fff;font:900 60px/1.12 Mont;color:#111;box-shadow:0 8px 24px rgba(0,0,0,.45)}"""
audio = (f'<audio id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{END}" data-track-index="1" data-volume="1"></audio>' if VOICE
         else f'<audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.55" data-fade-out="1.5"></audio>')
c0, w0 = CAMS[0][2], CAMS[0][3]
open(f"{P}/index.html", "w").write(f"""<!doctype html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="30">
<svg id="world" viewBox="{vb(c0, w0)}" preserveAspectRatio="xMidYMid slice">{"".join(SVG)}</svg>
{"".join(H)}
{audio}
{"".join(SFX)}
</div><script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(J)}
setDots({w0:.1f});
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>""")
print("END", END, [p["s"] for p in PH])
