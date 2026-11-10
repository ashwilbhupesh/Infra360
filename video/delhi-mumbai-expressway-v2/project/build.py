"""Delhi–Mumbai Expressway × Jaipur — dailygeomap-style reel (Digital Banjaaraa). Text+music draft; uses rec/phrases.json when the voice arrives.
World = z13 web-mercator px from tile (5791, 3466) (same frame as the Ajmer episode)."""
import json, math, os
P = "proj"
ASP = json.load(open("aspects.json"))
LINES = [
    "Delhi se Jaipur ab sirf 3 ghante mein. Kaise? Delhi Mumbai Expressway.",
    "Desh ka sabse lamba expressway, lagbhag 1,350 km, Delhi se Mumbai tak.",
    "Jaipur ke liye bana 67 km ka naya link: Bandikui se seedha Bagrana.",
    "Pehle Delhi se Jaipur saadhe chaar ghante, ab lagbhag 3 ghante.",
    "Raste mein India ki pehli 8 lane tunnel, aur wildlife ke liye green overpass.",
    "Aur jahan exit, wahan growth: hotels, food plaza, warehouses, aur zameen ki demand.",
    "Jaipur mein sabse zyada fayda Bagrana, Agra Road aur Ring Road ke aas-paas.",
    "Expressway ke paas plot loge? Comment karo Expressway.",
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

# ---------- base: dark grey world + coloured states ----------
G = 'filter:grayscale(1) brightness(.42) contrast(1.1)'
SVG.append('<rect x="-900000" y="-900000" width="2000000" height="2000000" style="fill:#1b1b1d"/>')
SVG.append(f'<image href="assets/img/bm4.jpg" x="-302848" y="-363008" width="786432" height="786432" preserveAspectRatio="none" style="{G}"/>')
SVG.append(f'<image href="assets/img/bm5.jpg" x="-171776" y="-166400" width="327680" height="393216" preserveAspectRatio="none" style="{G}"/>')
SVG.append(f'<image href="assets/img/bm7.webp" x="-40704" y="-35328" width="81920" height="65536" preserveAspectRatio="none" style="{G}"/>')
BD = json.load(open("data/bounds.json")); ST = json.load(open("data/states.json"))
def pdr(rings): return " ".join("M" + " L".join(f"{wp(la, lo)[0]:.1f} {wp(la, lo)[1]:.1f}" for lo, la in r) + " Z" for r in rings)
SVG.append(f'<path id="bind" d="{pdr(BD["india"])}" style="fill:#2a2a2d;fill-opacity:.5;stroke:#fff;stroke-width:2.5;vector-effect:non-scaling-stroke;stroke-linejoin:round"/>')
SCOL = {"Delhi": "#9E9E9E", "Haryana": "#1E8C3A", "Rajasthan": "#1530C8", "Madhya Pradesh": "#6A1B9A", "Gujarat": "#B3261E", "Maharashtra": "#D35400"}
for nm, rings in ST.items():
    sid = "st_" + nm.replace(" ", "")
    SVG.append(f'<path id="{sid}" d="{pdr(rings)}" style="fill:{SCOL[nm]};fill-opacity:0;stroke:#fff;stroke-width:2;vector-effect:non-scaling-stroke;stroke-linejoin:round;opacity:0"/>')

# ---------- route (indicative alignment through real waypoints) ----------
WPT = [("Delhi", 28.56, 77.27), ("Sohna", 28.25, 77.07), ("Nuh", 27.95, 77.00), ("Alwar", 27.45, 76.75), ("Bandikui", 27.05, 76.57), ("Dausa", 26.84, 76.35),
       ("Lalsot", 26.55, 76.33), ("Sawai Madhopur", 26.00, 76.40), ("Kota", 25.25, 75.95), ("Mukundra", 24.85, 75.85), ("", 24.40, 75.70), ("Ratlam", 23.35, 75.05),
       ("", 22.95, 74.65), ("Dahod", 22.84, 74.25), ("Godhra", 22.78, 73.62), ("Vadodara", 22.30, 73.20), ("", 21.72, 73.02), ("Surat", 21.20, 72.95),
       ("", 20.60, 72.95), ("Vasai-Virar", 19.45, 72.85), ("Mumbai", 18.95, 72.95)]
RP = smooth([wp(la, lo) for _, la, lo in WPT], 8)
SVG.append(f'<path id="rtg" d="{pd(RP)}" pathLength="1" style="fill:none;stroke:#fff;stroke-width:16;stroke-opacity:.25;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>'
           f'<path id="rt" d="{pd(RP)}" pathLength="1" style="fill:none;stroke:#fff;stroke-width:5;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1"/>')
BNK, BAG, JPR = wp(27.05, 76.57), wp(26.885, 75.93), wp(26.9124, 75.7873)
LINK = smooth([BNK, wp(26.99, 76.30), wp(26.93, 76.08), BAG], 10)
SVG.append(f'<path id="lkg" d="{pd(LINK)}" pathLength="1" style="fill:none;stroke:{GOLD};stroke-width:18;stroke-opacity:.35;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>'
           f'<path id="lk" d="{pd(LINK)}" pathLength="1" style="fill:none;stroke:{GOLD};stroke-width:7;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>')
OLD = smooth([wp(28.56, 77.27), wp(28.46, 77.03), wp(28.20, 76.62), wp(27.88, 76.30), wp(27.55, 76.07), wp(27.15, 75.95), JPR], 8)
SVG.append(f'<path id="old" d="{pd(OLD)}" pathLength="1" style="fill:none;stroke:#FF3B3B;stroke-width:5;vector-effect:non-scaling-stroke;stroke-dasharray:1;stroke-dashoffset:1;opacity:.9"/>')
for i, (nm, la, lo) in enumerate(WPT):
    if not nm: continue
    x, y = wp(la, lo)
    SVG.append(f'<g id="dot{i}" style="opacity:0"><circle cx="{x:.1f}" cy="{y:.1f}" r="1" style="fill:{GRN};opacity:.35;stroke:none" class="dg"/><circle cx="{x:.1f}" cy="{y:.1f}" r="1" class="dc" style="fill:{GRN}"/></g>')
for k, p, c in [("jpin", JPR, PINK), ("bpin", BAG, GOLD)]:
    SVG.append(f'<g id="{k}" style="opacity:0"><circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="1" class="dg" style="fill:{c};opacity:.35"/><circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="1" class="dc" style="fill:{c}"/></g>')
SVG.append('<rect id="dim" x="-900000" y="-900000" width="2000000" height="2000000" style="fill:#000;opacity:0"/>')

# ---------- cameras ----------
ALL = [wp(la, lo) for _, la, lo in WPT]
IND_C, IND_W = fitb([p for r in BD["india"] for p in [wp(la, lo) for lo, la in r]], 640, 1420, 1.08)
RT_C, RT_W = fitb(ALL, 520, 1380, 1.25)
RJ_C, RJ_W = fitb([wp(28.0, 77.3), wp(26.4, 75.5), JPR], 760, 1360, 1.2)
JL_C, JL_W = fitb([BNK, JPR, wp(27.2, 76.6)], 760, 1330, 1.3)
J.append(f'tl.set("#world", {{attr:{{viewBox:"{vb((IND_C[0], IND_C[1] - IND_W * .2), IND_W * 2.4)}"}}}}, 0);')
J.append('const VB = document.getElementById("world"); function setDots(w){ document.querySelectorAll(".dc").forEach(e=>e.setAttribute("r", w/80)); document.querySelectorAll(".dg").forEach(e=>e.setAttribute("r", w/36)); }'
         'function zoomTo(t, c0, w0, c1, w1, d){ const o = {z:0}; tl.to(o, {z:1, duration:d, ease:"power2.inOut", onUpdate:()=>{ const w = Math.exp(Math.log(w0) + (Math.log(w1) - Math.log(w0)) * o.z); const f = Math.abs(w0 - w1) < 1e-6 ? o.z : (w0 - w) / (w0 - w1); const cx = c0[0] + (c1[0] - c0[0]) * f, cy = c0[1] + (c1[1] - c0[1]) * f; const h = w * 1920 / 1080; VB.setAttribute("viewBox", (cx - w / 2) + " " + (cy - h / 2) + " " + w + " " + h); setDots(w); }}, t); }')
CAMS.append((0, 0, (IND_C[0], IND_C[1] - IND_W * .2), IND_W * 2.4))
zoom(0, IND_C, IND_W, 1.0)

# ---------- helpers ----------
def card(cid, img, t0, t1, title, sub="", tag=None, top=400, maxw=900, maxh=600, info=None):
    a = ASP[img]; w = maxw; h = w / a
    if h > maxh: h = maxh; w = h * a
    cw = max(w + 28, 700) if info else w + 28; lx = (1080 - cw) / 2
    tg = f'<div class="tg" style="background:{tag[1]}">{tag[0]}</div>' if tag else ''
    H.append(f'<div class="card" id="{cid}" style="left:{lx:.0f}px;top:{top}px;width:{cw:.0f}px">{tg}<img src="assets/img/{img}.jpg" style="width:{w:.0f}px;height:{h:.0f}px"/>'
             f'<div class="ct">{title}</div>' + (f'<div class="cs">{sub}</div>' if sub else '') + (f'<div class="ci">{info}</div>' if info else '') + '</div>')
    J.append(f'tl.fromTo("#{cid}", {{opacity:0, scale:.55, y:60}}, {{opacity:1, scale:1, y:0, duration:.32, ease:"back.out(1.7)"}}, {t0:.2f});'); CARDS.append([cid, t0, t1])
    sfx("pop", t0, .25)
def lab(i, p, text, t, until, at, dx=0, dy=0, cls=""):
    x, y = scr(p, at); H.append(f'<div class="ml {cls}" id="{i}" style="left:{min(max(x + dx, 150), 930):.0f}px;top:{y + dy:.0f}px">{text}</div>')
    J.append(f'tl.fromTo("#{i}", {{opacity:0, scale:.5}}, {{opacity:1, scale:1, duration:.25, ease:"back.out(2)"}}, {t:.2f}); tl.to("#{i}", {{opacity:0, duration:.2}}, {until - .2:.2f});')

# ---------- 0 HOOK ----------
H.append('<div id="clouds"><img id="cl0" src="assets/img/cloud0.png"/><img id="cl1" src="assets/img/cloud1.png"/></div>')
J.append('tl.fromTo("#cl0", {scale:1, y:0, opacity:1}, {scale:2.4, y:500, opacity:0, duration:1.3, ease:"power2.in"}, 0); tl.fromTo("#cl1", {scale:1, y:0, opacity:1}, {scale:2.6, y:-600, opacity:0, duration:1.1, ease:"power2.in"}, 0);')
H.append('<div id="title"><span>DELHI</span><i>&rarr;</i><span>JAIPUR</span><b>3 GHANTE</b></div>')
J.append(f'tl.fromTo("#title", {{opacity:0, scale:1.3}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, .25); tl.from("#title b", {{opacity:0, scale:2, duration:.3, ease:"back.out(2.5)"}}, {wt(0, "3 ghante"):.2f}); tl.to("#title", {{opacity:0, duration:.2}}, {wt(0, "Kaise") - .05:.2f});')
H.append('<div id="glow">DELHI&ndash;MUMBAI<br/>EXPRESSWAY</div>')
J.append(f'tl.fromTo("#glow", {{opacity:0, scale:.7}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)"}}, {wt(0, "Delhi Mumbai") - .1:.2f}); tl.to("#glow", {{opacity:0, duration:.2}}, {S(1) + 1.0:.2f});')
sfx("whoosh", 0, .45); sfx("impact-bass-1", .25, .45); sfx("impact-bass-1", wt(0, "Delhi Mumbai"), .4)

# ---------- 1 ROUTE ----------
zoom(S(1) - .3, RT_C, RT_W, 1.0)
order = ["Delhi", "Haryana", "Rajasthan", "Madhya Pradesh", "Gujarat", "Maharashtra"]
T1, D1 = S(1) + .2, (E(1) - S(1)) - .2
J.append(f'tl.to(["#rt", "#rtg"], {{strokeDashoffset:0, duration:{D1:.2f}, ease:"none"}}, {T1:.2f});')
for i, nm in enumerate(order):
    J.append(f'tl.to("#st_{nm.replace(" ", "")}", {{opacity:1, fillOpacity:.75, duration:.3}}, {T1 + D1 * i / 6:.2f});')
tot = len(RP)
for i, (nm, la, lo) in enumerate(WPT):
    if not nm: continue
    p = wp(la, lo); j = min(range(tot), key=lambda k: (RP[k][0] - p[0]) ** 2 + (RP[k][1] - p[1]) ** 2); t = T1 + D1 * j / tot
    J.append(f'tl.fromTo("#dot{i}", {{opacity:0}}, {{opacity:1, duration:.15}}, {t:.2f});')
    if nm in ("Delhi", "Alwar", "Dausa", "Kota", "Ratlam", "Vadodara", "Surat", "Mumbai"):
        dx = 120 if nm not in ("Mumbai", "Surat", "Vadodara") else -120
        lab(f"ln{i}", p, nm, t, max(S(2) - .3, t + .5), T1 + D1 + .1, dx=dx)
    if nm in ("Delhi", "Kota", "Vadodara", "Mumbai"): sfx("click-soft", t, .25)
H.append('<div class="big" id="km"><b>~1,350 KM</b><span>DESH KA SABSE LAMBA EXPRESSWAY</span></div>')
J.append(f'tl.fromTo("#km", {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:.3, ease:"back.out(2)"}}, {wt(1, "1,350") - .1:.2f}); tl.to("#km", {{opacity:0, duration:.2}}, {S(2) - .1:.2f});')

# ---------- 2 JAIPUR LINK ----------
zoom(S(2) - .3, JL_C, JL_W, 1.1)
J.append('tl.to(["#st_Haryana", "#st_MadhyaPradesh", "#st_Gujarat", "#st_Maharashtra", "#st_Delhi"], {fillOpacity:.25, duration:.4}, ' + f'{S(2) - .3:.2f}); tl.to("#st_Rajasthan", {{fillOpacity:.55, duration:.4}}, {S(2) - .3:.2f});')
J.append(f'tl.to(["#lk", "#lkg"], {{strokeDashoffset:0, duration:1.2, ease:"power2.out"}}, {wt(2, "Bandikui") - .2:.2f}); tl.to(["#jpin", "#bpin"], {{opacity:1, duration:.2}}, {wt(2, "Bagrana") - .1:.2f});')
lab("lbk", BNK, "BANDIKUI", wt(2, "Bandikui") - .2, S(4), S(2) + 1, dy=-60)
lab("lbg", BAG, "BAGRANA", wt(2, "Bagrana") - .1, S(4), S(2) + 1, dx=60, dy=60, cls="y")
lab("ljp", JPR, "JAIPUR", wt(2, "Bagrana"), S(4), S(2) + 1, dx=-60, dy=-60, cls="p")
H.append('<div class="big" id="k67"><b>67 KM</b><span>JAIPUR LINK &middot; 4-LANE &middot; OPEN SINCE 2025</span></div>')
J.append(f'tl.fromTo("#k67", {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:.3, ease:"back.out(2)"}}, {wt(2, "67") - .1:.2f}); tl.to("#k67", {{opacity:0, duration:.2}}, {S(3) - .1:.2f});')
card("c_link", "bandikui_link", wt(2, "Bagrana") + .4, S(3) - .1, "BANDIKUI &rarr; JAIPUR", "", ("67 KM", GOLD), top=1000, maxw=640, maxh=420)

# ---------- 3 TIME ----------
zoom(S(3) - .2, RJ_C, RJ_W, .9)
J.append(f'tl.to("#old", {{strokeDashoffset:0, duration:1.0}}, {S(3):.2f}); tl.to("#old", {{opacity:0, duration:.4}}, {S(4):.2f});')
H.append('<div id="time"><div class="tb old"><small>PEHLE &middot; NH-48</small><b>4.5 HRS</b></div><div class="tb new"><small>AB &middot; EXPRESSWAY</small><b>~3 HRS</b></div></div>')
J.append(f'tl.fromTo("#time", {{opacity:0}}, {{opacity:1, duration:.2}}, {S(3):.2f}); tl.from("#time .old", {{opacity:0, x:-60, duration:.3}}, {S(3):.2f}); tl.from("#time .new", {{opacity:0, x:60, duration:.3, ease:"back.out(2)"}}, {wt(3, "ab lagbhag") - .1:.2f}); tl.to("#time", {{opacity:0, duration:.2}}, {S(4) - .1:.2f});')
card("c_jam", "jam3", S(3) + .1, wt(3, "ab lagbhag"), "PEHLE: NH-48 KA JAAM", "Representative image", ("PEHLE", "#FF3B3B"), top=760, maxw=760, maxh=420)
card("c_fast", "ht_clip", wt(3, "ab lagbhag"), S(4) + .1, "DELHI TO JAIPUR IN 3 HOURS", "Hindustan Times · image supplied", ("AB", GRN), top=700, maxw=440, maxh=560)
sfx("whoosh-short", wt(3, "ab lagbhag"), .35)

# ---------- 4 TUNNEL + OVERPASS ----------
J.append(f'tl.to("#dim", {{opacity:.35, duration:.3}}, {S(4) - .1:.2f});')
card("c_tun", "tunnel", S(4), wt(4, "wildlife") - .1, "INDIA KI PEHLI 8-LANE TUNNEL", "Mukundra Hills, Kota", ("RECORD", GOLD), info="Wildlife reserve ke neeche se guzarti hai, taaki jungle na kate.")
card("c_ovp", "overpass", wt(4, "wildlife") - .1, S(5) + .1, "WILDLIFE GREEN OVERPASS", "Jaanwaron ke liye pul", ("GREEN", GRN), info="Upar jungle, neeche expressway.")

# ---------- 5 GROWTH ----------
card("c_am", "amenity2", S(5) + .05, wt(5, "food plaza") + .6, "WAYSIDE AMENITIES", "Food court &middot; EV charging &middot; parking", ("EXIT", GOLD))
card("c_ho", "hotel", wt(5, "food plaza") + .6, wt(5, "warehouses") - .1, "HIGHWAY HOTELS", "Exits ke paas naye business", ("HOTELS", GOLD))
card("c_wh", "warehouse", wt(5, "warehouses") - .1, S(6) + .1, "WAREHOUSES &amp; LOGISTICS", "Representative image", ("ZAMEEN KI DEMAND", GRN))

# ---------- 6 JAIPUR GROWTH ----------
J.append(f'tl.to("#dim", {{opacity:0, duration:.3}}, {S(6) - .1:.2f});')
JG_C, JG_W = fitb([BAG, JPR, wp(26.78, 75.80), wp(27.0, 76.05)], 760, 1300, 1.3)
zoom(S(6) - .2, JG_C, JG_W, .9)
SVG.append(f'<circle id="grow" cx="{BAG[0]:.1f}" cy="{BAG[1]:.1f}" r="1" style="fill:{GOLD};fill-opacity:.25;stroke:{GOLD};stroke-width:4;vector-effect:non-scaling-stroke;opacity:0"/>')
J.append(f'tl.set("#grow", {{attr:{{r:{JG_W / 9:.1f}}}}}, 0); tl.to("#grow", {{opacity:1, duration:.3}}, {S(6):.2f}); tl.to("#grow", {{fillOpacity:.45, duration:.35, yoyo:true, repeat:5}}, {S(6) + .3:.2f}); tl.to("#grow", {{opacity:0, duration:.3}}, {S(7):.2f});')
for i, (w_, nm, dx, dy) in enumerate([("Bagrana", "BAGRANA", 0, -90), ("Agra Road", "AGRA ROAD", 170, 40), ("Ring Road", "RING ROAD", -120, 130)]):
    lab(f"lg{i}", BAG, nm, wt(6, w_) - .1, S(7), S(6) + 1, dx=dx, dy=dy, cls="y")
    sfx("pop", wt(6, w_), .25)

# ---------- FOLLOW (mid) ----------
H.append('<div id="follow"><div class="fhead"><div class="fav">DB</div><div><div class="fname">Digital Banjaaraa</div><div class="fbio">Rajasthan real estate, maps se samjho</div></div></div><div class="fbtn"><span id="fb1">Follow</span><span id="fb2">Following &#10003;</span></div></div>')
TF = S(5) - .9
J.append(f'tl.fromTo("#follow", {{opacity:0, y:60}}, {{opacity:1, y:0, duration:.3, ease:"back.out(2)"}}, {TF:.2f}); tl.set("#fb1", {{display:"none"}}, {TF + .7:.2f}); tl.set("#fb2", {{display:"inline"}}, {TF + .7:.2f}); tl.to("#follow", {{opacity:0, duration:.2}}, {TF + 1.6:.2f});')
sfx("click-soft", TF + .7, .45)

# ---------- 7 CTA ----------
H.append('<div id="cta"><b>EXPRESSWAY KE PAAS PLOT LOGE?</b><span>COMMENT &ldquo;EXPRESSWAY&rdquo;</span></div>')
J.append(f'tl.to("#dim", {{opacity:.55, duration:.3}}, {S(7):.2f}); tl.fromTo("#cta", {{opacity:0, scale:.8}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)"}}, {S(7):.2f}); tl.to("#cta span", {{scale:1.08, duration:.4, yoyo:true, repeat:3}}, {wt(7, "Comment"):.2f});')
sfx("sparkle", wt(7, "Comment"), .3)

# card exits: hold until the next card arrives, never blank
CARDS.sort(key=lambda c: c[1])
for i, (cid, t0, t1) in enumerate(CARDS):
    nxt = CARDS[i + 1][1] if i + 1 < len(CARDS) else END
    out = max(t1, min(nxt + .3, t1 + .5))
    J.append(f'tl.set("#{cid}", {{zIndex:{10 + i}}}, 0); tl.to("#{cid}", {{opacity:0, scale:.9, duration:.2, ease:"power2.in"}}, {out - .2:.2f});')

# captions (white box, black bold)
HI = ["Delhi", "Jaipur", "3 ghante", "Delhi Mumbai Expressway", "sabse lamba", "1,350 km", "Mumbai", "67 km", "Bandikui", "Bagrana", "saadhe chaar ghante", "8 lane tunnel",
      "green overpass", "hotels", "food plaza", "warehouses", "zameen ki demand", "Agra Road", "Ring Road", "plot", "Expressway"]
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
H.append('<div id="wm">DIGITAL BANJAARAA</div><div id="cred">Route indicative &middot; Sources: NHAI-linked reports, DNA India, Tribune, HT &middot; Imagery: NASA Blue Marble &middot; States: Natural Earth</div>')
CSS = """@font-face{font-family:Anton;src:url(assets/fonts/anton.woff2)}@font-face{font-family:Mont;font-weight:700;src:url(assets/fonts/mont700.woff2)}@font-face{font-family:Mont;font-weight:800;src:url(assets/fonts/mont800.woff2)}@font-face{font-family:Mont;font-weight:900;src:url(assets/fonts/mont900.woff2)}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#1b1b1d}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif}#world{position:absolute;inset:0;width:1080px;height:1920px}.y{color:#111;background:#FFC42E;border-radius:6px;padding:0 6px}
#face{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:40}
#clouds{position:absolute;inset:0;z-index:15;pointer-events:none;overflow:hidden}#clouds img{position:absolute;left:-260px;top:-240px;width:1600px;height:2400px}
#wm{position:absolute;left:0;right:0;top:190px;text-align:center;font:800 24px Mont;letter-spacing:.34em;color:rgba(255,255,255,.55);z-index:20}
#cred{position:absolute;left:40px;right:40px;top:1650px;text-align:center;font:700 17px Mont;color:rgba(255,255,255,.55);z-index:20}
#title{position:absolute;left:0;right:0;top:300px;text-align:center;opacity:0;z-index:16}#title span{font:400 120px/1 Anton;color:#fff;text-shadow:0 6px 30px #000}#title i{font-style:normal;font:900 90px Mont;color:#3CE65A;margin:0 18px}
#title b{display:block;margin-top:14px;font:400 150px/1 Anton;color:#3CE65A;text-shadow:0 0 30px rgba(60,230,90,.7),0 6px 30px #000;font-weight:400}
#glow{position:absolute;left:0;right:0;top:330px;text-align:center;opacity:0;z-index:16;font:900 92px/1.02 Mont;color:#B9FFB0;text-shadow:0 0 18px #3CE65A,0 0 40px #3CE65A,0 6px 20px #000}
.ml{position:absolute;opacity:0;translate:-50% -50%;font:900 44px Mont;color:#fff;white-space:nowrap;text-shadow:0 3px 0 #000,0 0 14px #000;z-index:6}.ml.y{color:#FFC42E}.ml.p{color:#FF4FA3}
.big{position:absolute;left:40px;right:40px;top:300px;opacity:0;text-align:center;z-index:9}.big b{display:block;font:400 150px/1 Anton;color:#3CE65A;text-shadow:0 0 24px rgba(60,230,90,.6),0 6px 20px #000;font-weight:400}
.big span{display:inline-block;margin-top:8px;padding:8px 22px;border-radius:10px;background:#fff;color:#111;font:900 32px Mont}
#time{position:absolute;left:50px;right:50px;top:330px;opacity:0;display:flex;gap:20px;z-index:9}.tb{flex:1;padding:20px;border-radius:24px;text-align:center;background:rgba(10,10,12,.9)}
.tb small{display:block;font:900 26px Mont;color:#fff;letter-spacing:.06em}.tb b{display:block;font:400 110px/1 Anton;font-weight:400}.tb.old{border:4px solid #FF3B3B}.tb.old b{color:#FF3B3B;text-decoration:line-through}.tb.new{border:4px solid #3CE65A}.tb.new b{color:#3CE65A}
.card{position:absolute;opacity:0;padding:14px 14px 16px;border-radius:24px;background:#fff;box-shadow:0 30px 70px rgba(0,0,0,.7);z-index:8;text-align:center}
.card img{display:block;margin:0 auto;border-radius:14px;object-fit:cover}.ct{margin-top:10px;font:400 52px/1.05 Anton;color:#14161c;letter-spacing:.02em}.cs{margin-top:6px;font:700 26px Mont;color:#5b6070}
.ci{margin:10px 6px 0;padding-top:10px;border-top:2px solid #e3e3e8;text-align:left;font:700 26px/1.32 Mont;color:#2a2d36}
.tg{position:absolute;left:-12px;top:-22px;padding:8px 20px;border-radius:30px;font:900 28px Mont;color:#111;box-shadow:0 6px 16px rgba(0,0,0,.4);z-index:2}
#follow{position:absolute;left:60px;right:60px;top:1150px;opacity:0;z-index:30;padding:24px;border-radius:26px;background:#16181d;box-shadow:0 30px 80px rgba(0,0,0,.7);color:#fff}
.fhead{display:flex;align-items:center;gap:24px}.fav{width:110px;height:110px;border-radius:50%;flex:none;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#FF4FA3,#FFC42E);font:400 48px Anton;color:#111}
.fname{font:900 38px Mont}.fbio{margin-top:6px;font:700 26px Mont;color:#ccc}.fbtn{margin-top:18px;padding:14px;border-radius:14px;background:#0095F6;text-align:center;font:900 34px Mont}.fbtn #fb2{display:none}
#cta{position:absolute;left:50px;right:50px;top:440px;opacity:0;text-align:center;z-index:12}#cta b{display:block;padding:24px;border-radius:26px;background:#3CE65A;color:#111;font:400 86px/1.02 Anton;font-weight:400}
#cta span{display:inline-block;margin-top:24px;padding:16px 34px;border-radius:30px;background:#fff;color:#111;font:900 46px Mont}
.cp{position:absolute;left:40px;right:130px;top:1440px;text-align:center;opacity:0;z-index:35}
.cp div{display:inline-block;padding:4px 20px 8px;border-radius:10px;background:#fff;font:900 62px/1.12 Mont;color:#111;box-shadow:0 8px 24px rgba(0,0,0,.45)}"""
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
