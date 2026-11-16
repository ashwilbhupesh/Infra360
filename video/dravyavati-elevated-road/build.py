"""Delhi–Mumbai Expressway × Jaipur — dailygeomap-style reel (Digital Banjaaraa). Text+music draft; uses rec/phrases.json when the voice arrives.
World = z13 web-mercator px from tile (5791, 3466) (same frame as the Ajmer episode)."""
import json, math, os
P = "proj"
ASP = json.load(open("aspects.json"))
LINES = [
    "Jaipur ki Dravyavati nadi ke upar 6 lane elevated road aa raha hai, aur iske kinare zameen ke rates badhne ki poori ummeed hai.",
    "Nadi Vidhyadhar Nagar se shuru hokar Sikar Road, Sodala, Mansarovar aur Sanganer hote hue Sitapura tak jaati hai.",
    "Iske upar single pillar par lagbhag 25 se 30 km ka elevated corridor prastavit hai.",
    "Yeh Sikar Road, Ajmer Road, New Sanganer Road aur Tonk Road ko jodega.",
    "JDA aur Adani group ki team site visit bhi kar chuki hai.",
    "Riverfront 2018 se bana hua hai, aur iske kinare ke areas pehle se badal rahe hain.",
    "Plot lene se pehle buffer zone zaroor check karo, dono taraf karib 30 meter.",
    "Aap Dravyavati ke paas rehte ho? Comment karo River.",
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
CROSS = {"Sikar Road": (26.932, 75.795), "Ajmer Road": (26.905, 75.779), "New Sanganer Road": (26.880, 75.772), "Tonk Road": (26.795, 75.827)}
for i, (nm, (la, lo)) in enumerate(CROSS.items()):
    x, y = wp(la, lo)
    SVG.append(f'<g id="cx{i}" style="opacity:0"><circle cx="{x:.1f}" cy="{y:.1f}" r="1" class="dg" style="fill:#fff;opacity:.35"/><circle cx="{x:.1f}" cy="{y:.1f}" r="1" class="dc" style="fill:#fff;stroke:{GOLD};stroke-width:3;vector-effect:non-scaling-stroke"/></g>')
SVG.append('<rect id="dim" x="-900000" y="-900000" width="2000000" height="2000000" style="fill:#000;opacity:0"/>')

# ---------- cameras ----------
def bbr(rings):
    return [wp(la, lo) for r in rings for lo, la in r]
IND_C, IND_W = fitb(bbr(BD["india"]), 640, 1420, 1.08)
RAJ_C, RAJ_W = fitb(bbr(BD["raj"]), 700, 1380, 1.1)
JP_C, JP_W = fitb(bbr(BD["jaipur"]), 700, 1380, 1.1)
RV_C, RV_W = fitb(RP[:int(len(RP) * .8)], 470, 1360, 1.15)
J.append(f'tl.set("#world", {{attr:{{viewBox:"{vb((IND_C[0], IND_C[1] - IND_W * .2), IND_W * 2.4)}"}}}}, 0);')
J.append('const VB = document.getElementById("world"); function setDots(w){ document.querySelectorAll(".dc").forEach(e=>e.setAttribute("r", w/90)); document.querySelectorAll(".dg").forEach(e=>e.setAttribute("r", w/40)); document.querySelectorAll(".mvc").forEach(e=>e.setAttribute("r", w/70)); document.querySelectorAll(".mvg").forEach(e=>e.setAttribute("r", w/26)); }'
         'function zoomTo(t, c0, w0, c1, w1, d){ const o = {z:0}; tl.to(o, {z:1, duration:d, ease:"power2.inOut", onUpdate:()=>{ const w = Math.exp(Math.log(w0) + (Math.log(w1) - Math.log(w0)) * o.z); const f = Math.abs(w0 - w1) < 1e-6 ? o.z : (w0 - w) / (w0 - w1); const cx = c0[0] + (c1[0] - c0[0]) * f, cy = c0[1] + (c1[1] - c0[1]) * f; const h = w * 1920 / 1080; VB.setAttribute("viewBox", (cx - w / 2) + " " + (cy - h / 2) + " " + w + " " + h); setDots(w); }}, t); }')
CAMS.append((0, 0, (IND_C[0], IND_C[1] - IND_W * .2), IND_W * 2.4))
zoom(0, IND_C, IND_W, .9)
zoom(.95, RAJ_C, RAJ_W, .9)
zoom(1.9, JP_C, JP_W, .9)
zoom(2.85, RV_C, RV_W, 1.0)
J.append('tl.to("#bind", {fillOpacity:.7, duration:.3}, .3); tl.to("#bind", {fillOpacity:0, opacity:.5, duration:.3}, 1.0); tl.to("#braj", {opacity:1, fillOpacity:.75, duration:.3}, 1.0); tl.to("#braj", {fillOpacity:.1, duration:.3}, 1.95);'
         'tl.to("#bjp", {opacity:1, fillOpacity:.6, duration:.3}, 1.95); tl.to("#bjp", {fillOpacity:0, opacity:.4, duration:.4}, 2.9); tl.to(["#bind", "#braj"], {opacity:0, duration:.3}, 2.9); tl.to("#bjp", {opacity:0, duration:.3}, 3.9);')
sfx("whoosh", 0, .4); sfx("whoosh", .95, .3); sfx("whoosh", 1.9, .3); sfx("whoosh", 2.85, .3)

# ---------- helpers ----------
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
    x, y = scr(p, at); H.append(f'<div class="ml {cls}" id="{i}" style="left:{min(max(x + dx, 60 + len(text) * 11), 1020 - len(text) * 11):.0f}px;top:{y + dy:.0f}px;opacity:0">{text}</div>')
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

# ---------- 0 HOOK ----------
H.append('<div id="clouds"><img id="cl0" src="assets/img/cloud0.png"/><img id="cl1" src="assets/img/cloud1.png"/></div>')
J.append('tl.fromTo("#cl0", {scale:1, y:0, opacity:1}, {scale:2.4, y:500, opacity:0, duration:1.2, ease:"power2.in"}, 0); tl.fromTo("#cl1", {scale:1, y:0, opacity:1}, {scale:2.6, y:-600, opacity:0, duration:1.0, ease:"power2.in"}, 0);')
H.append('<div id="title"><small>JAIPUR KI NADI KE UPAR</small><b>6-LANE<br/>ELEVATED ROAD</b></div>')
J.append(f'tl.fromTo("#title", {{opacity:0, scale:1.3}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, .2); tl.to("#title b", {{opacity:.55, duration:.06, yoyo:true, repeat:5}}, {wt(0, "elevated"):.2f}); tl.to("#title", {{opacity:0, duration:.2}}, {S(1) - .1:.2f});')
J.append(f'tl.to("#elp", {{strokeDashoffset:0, duration:1.3, ease:"power1.inOut"}}, 3.9); tl.to("#elp", {{opacity:.35, duration:.3, yoyo:true, repeat:5}}, 5.3); tl.to("#elp", {{opacity:0, duration:.3}}, {S(1) - .4:.2f}); tl.set("#elp", {{strokeDashoffset:1}}, {S(1) - .05:.2f});')
sfx("whoosh", 3.9, .3)
H.append('<div id="rate"><b>ZAMEEN KE RATES &#9650;</b></div>')
J.append(f'tl.fromTo("#rate", {{opacity:0, scale:2}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2.5)"}}, {wt(0, "zameen") - .1:.2f}); tl.to("#rate b", {{scale:1.08, duration:.3, yoyo:true, repeat:3}}, {wt(0, "zameen") + .3:.2f}); tl.to("#rate", {{opacity:0, duration:.2}}, {S(1) - .1:.2f});')
sfx("sparkle", wt(0, "zameen") - .1, .35)
sfx("impact-bass-1", .2, .45); sfx("impact-bass-1", wt(0, "elevated"), .4)
H.append('<div class="ml mlab" id="mi">INDIA</div><div class="ml mlab" id="mr">RAJASTHAN</div><div class="ml mlab" id="mj">JAIPUR</div>')
for i_, (k, t_) in enumerate([("mi", .4), ("mr", 1.25), ("mj", 2.2)]):
    J.append(f'tl.fromTo("#{k}", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.25}}, {t_:.2f}); tl.to("#{k}", {{opacity:0, duration:.15}}, {t_ + .6:.2f});')

# ---------- 1 RIVER ----------
T1 = max(3.0, S(1) - .1); D1 = E(1) - T1 + .2
J.append(f'tl.to(["#rv", "#rvg"], {{strokeDashoffset:0, duration:{D1:.2f}, ease:"none"}}, {T1:.2f});')
mover("w1", RP, T1, D1, "#2EA8FF", S(2) - .1)
NAMES = [("Vidhyadhar Nagar", 26.956, 75.789, -170), ("Sikar Road", 26.932, 75.795, 170), ("Sodala", 26.904, 75.779, 160), ("Mansarovar", 26.868, 75.782, 190),
         ("Sanganer", 26.818, 75.799, -170), ("Sitapura", 26.786, 75.872, -130)]
for i, (nm, la, lo, dx) in enumerate(NAMES):
    w_ = nm.split()[0]; t = wt(1, w_) - .05
    lab(f"rn{i}", wp(la, lo), nm, t, S(2) - .1, T1 + D1, dx=dx)
H.append('<div class="big" id="b1"><b>DRAVYAVATI</b><span>JAIPUR KI NADI &middot; RIVERFRONT</span></div>')
J.append(f'tl.fromTo("#b1", {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:.3, ease:"back.out(2)"}}, {S(1):.2f}); tl.to("#b1", {{opacity:0, duration:.2}}, {S(2) - .1:.2f});')

# ---------- 2 ELEVATED ----------
J.append(f'tl.to(["#el", "#elg"], {{strokeDashoffset:0, duration:{E(2) - S(2):.2f}, ease:"none"}}, {S(2):.2f}); tl.to("#eld", {{opacity:.7, duration:.3}}, {E(2):.2f}); tl.to("#rv", {{opacity:.6, duration:.3}}, {S(2):.2f});')
mover("car", ELV, S(2), E(2) - S(2), GOLD, S(3))
H.append('<div class="big" id="b2"><b>25&ndash;30 KM</b><span>6-LANE &middot; SINGLE PILLAR &middot; PRASTAVIT</span></div>')
J.append(f'tl.fromTo("#b2 b", {{scale:2.2}}, {{scale:1, duration:.4, ease:"back.out(2.5)"}}, {wt(2, "25") - .1:.2f}); tl.fromTo("#b2", {{opacity:0}}, {{opacity:1, duration:.2}}, {wt(2, "25") - .1:.2f}); tl.to("#b2", {{opacity:0, duration:.2}}, {S(3) - .1:.2f});')
H.append('<div id="legend"><span><i style="background:#5EC8FF"></i>Nadi</span><span><i style="background:#FFC42E"></i>Elevated (prastavit)</span></div>')
J.append(f'tl.fromTo("#legend", {{opacity:0}}, {{opacity:1, duration:.3}}, {S(2) + .5:.2f}); tl.to("#legend", {{opacity:0, duration:.2}}, {S(5) - .1:.2f});')

# ---------- 3 ROADS ----------
for i, nm in enumerate(CROSS):
    t = wt(3, nm.split()[0] if nm != "New Sanganer Road" else "New Sanganer") - .05
    J.append(f'tl.to("#cx{i}", {{opacity:1, duration:.2}}, {t:.2f}); tl.to("#cx{i}", {{opacity:0, duration:.3}}, {S(5):.2f});')
    lab(f"rl{i}", wp(*CROSS[nm]), nm.upper(), t, S(4), S(3), dx=-200 if i % 2 == 0 else 200, cls="y")
    sfx("pop", t, .3)

# ---------- 4 BHASKAR ----------
card("cbh", "bhaskar", S(4) - .05, S(5) + .1, "JDA + ADANI GROUP SITE VISIT", "Dainik Bhaskar &middot; image supplied", ("NEWS", "#FF3B3B"), top=360, maxw=760, maxh=820)

# ---------- 5 RIVERFRONT ----------
H.append('<div class="big" id="b5"><b>2018 SE</b><span>RIVERFRONT &middot; PATHWAY &middot; CYCLE TRACK</span></div>')
J.append(f'tl.fromTo("#b5 b", {{scale:2.2}}, {{scale:1, duration:.4, ease:"back.out(2.5)"}}, {S(5):.2f}); tl.fromTo("#b5", {{opacity:0}}, {{opacity:1, duration:.2}}, {S(5):.2f}); tl.to("#b5", {{opacity:0, duration:.2}}, {S(6) - .1:.2f});')
J.append(f'tl.to(["#rv", "#rvg"], {{strokeWidth:"+=6", duration:.35, yoyo:true, repeat:5}}, {S(5) + .2:.2f});')

# ---------- 6 BUFFER ----------
J.append(f'tl.to("#bufz", {{strokeOpacity:.35, duration:.4}}, {S(6):.2f}); tl.to("#bufz", {{strokeOpacity:.55, duration:.35, yoyo:true, repeat:3}}, {S(6) + .4:.2f}); tl.to("#bufz", {{strokeOpacity:0, duration:.3}}, {S(7):.2f});')
H.append('<div id="stat"><b>&#9888; BUFFER ZONE CHECK KARO</b><p>Nadi ke dono taraf ~30 meter &middot; master plan</p></div>')
J.append(f'tl.fromTo("#stat", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)"}}, {S(6):.2f}); tl.to("#stat", {{opacity:0, duration:.2}}, {S(7) - .1:.2f});')
sfx("impact-bass-1", S(6), .35)

# ---------- 7 CTA ----------
H.append('<div id="cta"><b>DRAVYAVATI KE PAAS REHTE HO?</b><span>COMMENT &ldquo;RIVER&rdquo;</span></div>')
J.append(f'tl.to("#dim", {{opacity:.55, duration:.3}}, {S(7):.2f}); tl.fromTo("#cta", {{opacity:0, scale:.8}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)"}}, {S(7):.2f}); tl.to("#cta span", {{scale:1.08, duration:.4, yoyo:true, repeat:3}}, {wt(7, "Comment"):.2f});')
sfx("sparkle", wt(7, "Comment"), .3)

# captions
HI = ["Dravyavati", "6 lane elevated road", "Vidhyadhar Nagar", "Sikar Road", "Sodala", "Mansarovar", "Sanganer", "Sitapura", "single pillar", "25 se 30 km",
      "rates badhne", "Ajmer Road", "New Sanganer Road", "Tonk Road", "JDA", "Adani group", "Riverfront", "2018", "buffer zone", "30 meter", "River"]
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
H.append('<div id="cred">River traced from Google Maps (approx.) &middot; elevated alignment indicative &middot; Sources: Dainik Bhaskar, The Deep State &middot; Imagery: Sentinel-2 (EOX), NASA Blue Marble</div>')
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
