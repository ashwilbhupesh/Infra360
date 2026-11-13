"""Delhi–Mumbai Expressway × Jaipur — dailygeomap-style reel (Digital Banjaaraa). Text+music draft; uses rec/phrases.json when the voice arrives.
World = z13 web-mercator px from tile (5791, 3466) (same frame as the Ajmer episode)."""
import json, math, os
P = "proj"
ASP = json.load(open("aspects.json"))
LINES = [
    "Delhi se Jaipur ho kar Mumbai tak bullet train? Sach kya hai, 30 second mein samjho.",
    "Mumbai se Ahmedabad bullet train ban rahi hai, 508 km, 2027 ka target.",
    "Aur is route ke station areas mein naye projects aur zameen ki demand pehle se badh rahi hai.",
    "Ab Delhi se Ahmedabad ka corridor, Jaipur ho kar, prastavit hai, lagbhag 886 km.",
    "Delhi aur Jaipur ke beech stations: Gurugram, Rewari, Behror, Shahpura aur Jaipur.",
    "Agar yeh bana, toh inhi stations ke aas-paas zameen sabse pehle badhegi. Yahi hain hotspots.",
    "Abhi yeh DPR stage pe hai, isliye sirf approved aur patta wali zameen hi lo.",
    "Inme se kaunsa station aapke sabse paas hai? Comment karo.",
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

# ---------- routes ----------
PROP = [("Delhi", 28.59, 77.05), ("Gurugram", 28.46, 77.03), ("Rewari", 28.19, 76.62), ("Behror", 27.89, 76.28), ("Shahpura", 27.39, 75.96), ("Jaipur", 26.91, 75.79),
        ("Kishangarh", 26.59, 74.86), ("Bhilwara", 25.35, 74.63), ("Chittorgarh", 24.88, 74.62), ("Udaipur", 24.58, 73.71), ("Himmatnagar", 23.60, 72.97), ("Ahmedabad", 23.03, 72.58)]
UC = [("Ahmedabad", 23.03, 72.58), ("Anand", 22.56, 72.95), ("Vadodara", 22.31, 73.18), ("Bharuch", 21.71, 72.98), ("Surat", 21.17, 72.83), ("Vapi", 20.39, 72.91), ("Thane", 19.20, 72.97), ("Mumbai BKC", 19.07, 72.87)]
PP = smooth([wp(la, lo) for _, la, lo in PROP], 8); UP = smooth([wp(la, lo) for _, la, lo in UC], 8)
SVG.append(f'<path id="ucg" d="{pd(UP)}" pathLength="1" style="fill:none;stroke:{GRN};stroke-width:18;stroke-opacity:.3;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>'
           f'<path id="uc" d="{pd(UP)}" pathLength="1" style="fill:none;stroke:{GRN};stroke-width:7;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>')
SVG.append(f'<path id="ppg" d="{pd(PP)}" pathLength="1" style="fill:none;stroke:#fff;stroke-width:16;stroke-opacity:.2;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>'
           f'<path id="pp" d="{pd(PP)}" pathLength="1" style="fill:none;stroke:#fff;stroke-width:5;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>'
           f'<path id="ppd" d="{pd(PP)}" style="fill:none;stroke:#1b1b1d;stroke-width:5;vector-effect:non-scaling-stroke;stroke-dasharray:14 12;opacity:0"/>')
DOTS = {}
for grp, lst, col in (("p", PROP, "#fff"), ("u", UC, GRN)):
    for i, (nm, la, lo) in enumerate(lst):
        x, y = wp(la, lo); k = f"{grp}{i}"; DOTS[nm] = k
        SVG.append(f'<g id="d{k}" style="opacity:0"><circle cx="{x:.1f}" cy="{y:.1f}" r="1" class="dg" style="fill:{col};opacity:.35"/><circle cx="{x:.1f}" cy="{y:.1f}" r="1" class="dc" style="fill:{col}"/></g>')
JPR = wp(26.91, 75.79)
SVG.append(f'<circle id="grow" cx="{JPR[0]:.1f}" cy="{JPR[1]:.1f}" r="1" style="fill:{GOLD};fill-opacity:.25;stroke:{GOLD};stroke-width:4;vector-effect:non-scaling-stroke;opacity:0"/>')
SVG.append('<rect id="dim" x="-900000" y="-900000" width="2000000" height="2000000" style="fill:#000;opacity:0"/>')

# ---------- cameras ----------
ALL = [wp(la, lo) for _, la, lo in PROP + UC]
IND_C, IND_W = fitb([p for r in BD["india"] for p in [wp(la, lo) for lo, la in r]], 640, 1420, 1.08)
RT_C, RT_W = fitb(ALL, 520, 1380, 1.25)
UC_C, UC_W = fitb([wp(la, lo) for _, la, lo in UC], 560, 1360, 1.35)
RJ_C, RJ_W = fitb([wp(la, lo) for _, la, lo in PROP[2:10]], 560, 1360, 1.25)
J.append(f'tl.set("#world", {{attr:{{viewBox:"{vb((IND_C[0], IND_C[1] - IND_W * .2), IND_W * 2.4)}"}}}}, 0);')
J.append('const VB = document.getElementById("world"); function setDots(w){ document.querySelectorAll(".dc").forEach(e=>e.setAttribute("r", w/90)); document.querySelectorAll(".dg").forEach(e=>e.setAttribute("r", w/40)); document.querySelectorAll(".mvc").forEach(e=>e.setAttribute("r", w/60)); document.querySelectorAll(".mvg").forEach(e=>e.setAttribute("r", w/22)); }'
         'function zoomTo(t, c0, w0, c1, w1, d){ const o = {z:0}; tl.to(o, {z:1, duration:d, ease:"power2.inOut", onUpdate:()=>{ const w = Math.exp(Math.log(w0) + (Math.log(w1) - Math.log(w0)) * o.z); const f = Math.abs(w0 - w1) < 1e-6 ? o.z : (w0 - w) / (w0 - w1); const cx = c0[0] + (c1[0] - c0[0]) * f, cy = c0[1] + (c1[1] - c0[1]) * f; const h = w * 1920 / 1080; VB.setAttribute("viewBox", (cx - w / 2) + " " + (cy - h / 2) + " " + w + " " + h); setDots(w); }}, t); }')
CAMS.append((0, 0, (IND_C[0], IND_C[1] - IND_W * .2), IND_W * 2.4))
zoom(0, IND_C, IND_W, 1.0)

# ---------- helpers ----------
def mover(mid, pts, t0, d, col, until, N=60):
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

def card(cid, img, t0, t1, title, sub="", tag=None, top=400, maxw=900, maxh=600, info=None):
    a = ASP[img]; w = maxw; h = w / a
    if h > maxh: h = maxh; w = h * a
    cw = max(w + 28, 700) if info else w + 28; lx = (1080 - cw) / 2
    tg = f'<div class="tg" style="background:{tag[1]}">{tag[0]}</div>' if tag else ''
    H.append(f'<div class="card" id="{cid}" style="left:{lx:.0f}px;top:{top}px;width:{cw:.0f}px">{tg}<div class="iw" style="width:{w:.0f}px;height:{h:.0f}px"><img src="assets/img/{img}.jpg" style="width:{w:.0f}px;height:{h:.0f}px"/><i class="scan"></i></div>'
             f'<div class="ct">{title}</div>' + (f'<div class="cs">{sub}</div>' if sub else '') + (f'<div class="ci">{info}</div>' if info else '') + '</div>')
    J.append(f'tl.fromTo("#{cid}", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:.2, ease:"power2.out"}}, {t0:.2f}); tl.fromTo("#{cid} img", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:.55, ease:"power2.inOut"}}, {t0:.2f});'
             f'tl.fromTo("#{cid} .scan", {{left:"0%", opacity:1}}, {{left:"100%", duration:.55, ease:"power2.inOut"}}, {t0:.2f}); tl.to("#{cid} .scan", {{opacity:0, duration:.15}}, {t0 + .55:.2f});'
             f'tl.fromTo("#{cid} img", {{scale:1.0}}, {{scale:1.06, duration:{max(.5, t1 - t0):.2f}, ease:"none", immediateRender:false}}, {t0 + .5:.2f});'); CARDS.append([cid, t0, t1])
    sfx("pop", t0, .25)
def lab(i, p, text, t, until, at, dx=0, dy=0, cls=""):
    x, y = scr(p, at); H.append(f'<div class="ml {cls}" id="{i}" style="left:{min(max(x + dx, 150), 930):.0f}px;top:{y + dy:.0f}px">{text}</div>')
    J.append(f'tl.fromTo("#{i}", {{opacity:0, scale:.5}}, {{opacity:1, scale:1, duration:.25, ease:"back.out(2)"}}, {t:.2f}); tl.to("#{i}", {{opacity:0, duration:.2}}, {until - .2:.2f});')

# ---------- 0 HOOK ----------
H.append('<div id="clouds"><img id="cl0" src="assets/img/cloud0.png"/><img id="cl1" src="assets/img/cloud1.png"/></div>')
J.append('tl.fromTo("#cl0", {scale:1, y:0, opacity:1}, {scale:2.4, y:500, opacity:0, duration:1.3, ease:"power2.in"}, 0); tl.fromTo("#cl1", {scale:1, y:0, opacity:1}, {scale:2.6, y:-600, opacity:0, duration:1.1, ease:"power2.in"}, 0);')
H.append('<div id="title"><span>DELHI</span><i>&rarr;</i><span>JAIPUR</span><i>&rarr;</i><span>MUMBAI</span><b>BULLET TRAIN?</b></div>')
J.append(f'tl.fromTo("#title", {{opacity:0, scale:1.3}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, .2); tl.from("#title b", {{opacity:0, scale:2, duration:.3, ease:"back.out(2.5)"}}, {wt(0, "bullet") - .05:.2f}); tl.to("#title b", {{opacity:.5, duration:.06, yoyo:true, repeat:5}}, {wt(0, "bullet") + .35:.2f}); tl.to("#title", {{opacity:0, duration:.2}}, {S(1) - .1:.2f});')
H.append('<div id="glow">SACH KYA HAI?</div>')
J.append(f'tl.fromTo("#glow", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2.5)"}}, {wt(0, "Sach") - .1:.2f}); tl.to("#glow", {{opacity:0, duration:.2}}, {S(1) - .1:.2f});')
sfx("whoosh", 0, .45); sfx("impact-bass-1", .2, .45); sfx("impact-bass-1", wt(0, "Sach"), .4)
J.append(f'tl.to("#title", {{y:-120, duration:.3}}, {wt(0, "Sach") - .1:.2f});')

# ---------- 1 UNDER CONSTRUCTION: Mumbai–Ahmedabad ----------
zoom(S(1) - .3, UC_C, UC_W, 1.0)
J.append(f'tl.to(["#st_Gujarat", "#st_Maharashtra"], {{opacity:1, fillOpacity:.6, duration:.3}}, {S(1) - .2:.2f});')
T1, D1 = S(1) + .3, 1.8
J.append(f'tl.to(["#uc", "#ucg"], {{strokeDashoffset:0, duration:{D1}, ease:"none"}}, {T1:.2f});')
mover("tr1", list(reversed(UP)), T1, D1, GRN, S(3) - .2)
for i, (nm, la, lo) in enumerate(reversed(UC)):
    t = T1 + D1 * i / (len(UC) - 1); k = DOTS[nm]
    J.append(f'tl.to("#d{k}", {{opacity:1, duration:.15}}, {t:.2f});')
    if nm in ("Mumbai BKC", "Surat", "Vadodara", "Ahmedabad"): lab(f"lu{i}", wp(la, lo), nm, t, S(3) - .2, T1 + D1 + .1, dx=-170 if nm != "Ahmedabad" else 170); sfx("click-soft", t, .25)
H.append('<div class="big" id="b1"><b>508 KM</b><span>MUMBAI &ndash; AHMEDABAD &middot; UNDER CONSTRUCTION &middot; TARGET 2027</span></div>')
J.append(f'tl.fromTo("#b1 b", {{scale:2.2}}, {{scale:1, duration:.4, ease:"back.out(2.5)"}}, {wt(1, "508") - .1:.2f}); tl.fromTo("#b1", {{opacity:0}}, {{opacity:1, duration:.2}}, {wt(1, "508") - .1:.2f}); tl.to("#b1", {{opacity:0, duration:.2}}, {S(2) - .05:.2f});')

# ---------- 2b BELT ----------
DB_ = []
for i, (nm, la, lo) in enumerate(UC):
    p_ = wp(la, lo)
    SVG.append(f'<circle id="bl{i}" cx="{p_[0]:.1f}" cy="{p_[1]:.1f}" r="1" style="fill:{GOLD};fill-opacity:.3;stroke:{GOLD};stroke-width:3;vector-effect:non-scaling-stroke;opacity:0"/>')
    J.append(f'tl.fromTo("#bl{i}", {{attr:{{r:{UC_W / 120:.1f}}}, opacity:1}}, {{attr:{{r:{UC_W / 14:.1f}}}, opacity:0, duration:1.0, repeat:2, ease:"power2.out", immediateRender:false}}, {S(2) + .15 * i:.2f});')
H.append('<div class="big" id="bb"><b>DEMAND &uarr;</b><span>STATION AREAS &middot; MUMBAI&ndash;AHMEDABAD BELT</span></div>')
J.append(f'tl.fromTo("#bb b", {{scale:2.2}}, {{scale:1, duration:.4, ease:"back.out(2.5)"}}, {wt(2, "demand") - .2:.2f}); tl.fromTo("#bb", {{opacity:0}}, {{opacity:1, duration:.2}}, {wt(2, "demand") - .2:.2f}); tl.to("#bb", {{opacity:0, duration:.2}}, {S(3) - .1:.2f});')
sfx("sparkle", wt(2, "demand"), .3)

# ---------- 2 PROPOSED Delhi–Ahmedabad via Jaipur ----------
zoom(S(3) - .3, RT_C, RT_W, 1.0)
J.append(f'tl.to(["#st_Rajasthan", "#st_Haryana", "#st_Delhi"], {{opacity:1, fillOpacity:.6, duration:.3}}, {S(3):.2f}); tl.to(["#st_Gujarat", "#st_Maharashtra"], {{fillOpacity:.35, duration:.3}}, {S(3):.2f});')
T2, D2 = S(3) + .3, (E(3) - S(3)) - .1
J.append(f'tl.to(["#pp", "#ppg"], {{strokeDashoffset:0, duration:{D2:.2f}, ease:"none"}}, {T2:.2f}); tl.to("#ppd", {{opacity:1, duration:.3}}, {T2 + D2:.2f});')
mover("tr2", PP, T2, D2, "#fff", S(4) - .2)
for i, (nm, la, lo) in enumerate(PROP):
    t = T2 + D2 * i / (len(PROP) - 1); k = DOTS.get(nm)
    if k: J.append(f'tl.to("#d{k}", {{opacity:1, duration:.15}}, {t:.2f});')
    if nm in ("Delhi", "Jaipur"): lab(f"lp{i}", wp(la, lo), nm.upper(), t, S(4) - .25, T2 + D2 + .1, dx=150 if nm == "Delhi" else -150, cls="y" if nm == "Jaipur" else "")
H.append('<div class="big" id="b2"><b>~886 KM</b><span>DELHI &ndash; AHMEDABAD VIA JAIPUR &middot; PROPOSED</span></div>')
J.append(f'tl.fromTo("#b2 b", {{scale:2.2}}, {{scale:1, duration:.4, ease:"back.out(2.5)"}}, {wt(3, "886") - .1:.2f}); tl.fromTo("#b2", {{opacity:0}}, {{opacity:1, duration:.2}}, {wt(3, "886") - .1:.2f}); tl.to("#b2", {{opacity:0, duration:.2}}, {S(4) - .1:.2f});')
H.append('<div id="legend"><span><i style="background:#3CE65A"></i>Ban rahi hai</span><span><i class="dsh"></i>Prastavit</span></div>')
J.append(f'tl.fromTo("#legend", {{opacity:0}}, {{opacity:1, duration:.3}}, {T2 + D2:.2f}); tl.to("#legend", {{opacity:0, duration:.2}}, {S(5) - .1:.2f});')

# ---------- 4 DELHI–JAIPUR STATIONS / 5 HOTSPOTS ----------
DJ_C, DJ_W = fitb([wp(28.62, 77.10), wp(26.85, 75.75)], 600, 1330, 1.45)
zoom(S(4) - .3, DJ_C, DJ_W, 1.0)
J.append(f'tl.to(["#st_Gujarat", "#st_Maharashtra", "#st_MadhyaPradesh"], {{fillOpacity:.15, duration:.3}}, {S(4) - .3:.2f});')
HS = ["Gurugram", "Rewari", "Behror", "Shahpura", "Jaipur"]
for i, nm in enumerate(HS):
    la, lo = next((a_, b_) for n_, a_, b_ in PROP if n_ == nm); p_ = wp(la, lo); t = wt(4, nm) - .05
    lab(f"hs{i}", p_, f"<b class='nb'>{i + 1}</b> {nm.upper()}", t, S(7) - .1, S(4) + .8, dx=-190 if i % 2 == 0 else 190, cls="y" if nm == "Jaipur" else "")
    SVG.append(f'<circle id="hz{i}" cx="{p_[0]:.1f}" cy="{p_[1]:.1f}" r="1" style="fill:{GOLD};fill-opacity:.28;stroke:{GOLD};stroke-width:4;vector-effect:non-scaling-stroke;opacity:0"/>')
    J.append(f'tl.fromTo("#hz{i}", {{attr:{{r:{DJ_W / 150:.1f}}}, opacity:1}}, {{attr:{{r:{DJ_W / 26:.1f}}}, opacity:1, duration:.5, ease:"back.out(2)", immediateRender:false}}, {t:.2f}); tl.to("#hz{i}", {{fillOpacity:.5, duration:.35, yoyo:true, repeat:5}}, {wt(5, "hotspots") - .2:.2f}); tl.to("#hz{i}", {{opacity:0, duration:.3}}, {S(7) - .1:.2f});')
    sfx("pop", t, .28)
H.append('<div class="big" id="bh"><b>HOTSPOTS</b><span>PRASTAVIT STATIONS KE AAS-PAAS</span></div>')
J.append(f'tl.fromTo("#bh b", {{scale:2.2}}, {{scale:1, duration:.4, ease:"back.out(2.5)"}}, {wt(5, "hotspots") - .2:.2f}); tl.fromTo("#bh", {{opacity:0}}, {{opacity:1, duration:.2}}, {wt(5, "hotspots") - .2:.2f}); tl.to("#bh", {{opacity:0, duration:.2}}, {S(6) - .1:.2f});')
sfx("impact-bass-1", wt(5, "hotspots") - .2, .4)

# ---------- 6 STATUS ----------
H.append('<div id="stat"><b>&#9888; ABHI DPR STAGE</b><p>Sirf approved layout aur patta wali zameen lo</p></div>')
J.append(f'tl.to("#dim", {{opacity:.5, duration:.3}}, {S(6) - .1:.2f}); tl.fromTo("#stat", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)"}}, {S(6):.2f}); tl.to("#stat", {{opacity:0, duration:.2}}, {S(7) - .1:.2f});')

# ---------- FOLLOW ----------
H.append('<div id="follow"><div class="fhead"><div class="fav">DB</div><div><div class="fname">Digital Banjaaraa</div><div class="fbio">Rajasthan real estate, maps se samjho</div></div></div><div class="fbtn"><span id="fb1">Follow</span><span id="fb2">Following &#10003;</span></div></div>')
TF = S(3) - 1.3
J.append(f'tl.fromTo("#follow", {{opacity:0, y:60}}, {{opacity:1, y:0, duration:.3, ease:"back.out(2)"}}, {TF:.2f}); tl.set("#fb1", {{display:"none"}}, {TF + .6:.2f}); tl.set("#fb2", {{display:"inline"}}, {TF + .6:.2f}); tl.to("#follow", {{opacity:0, duration:.2}}, {TF + 1.2:.2f});')
sfx("click-soft", TF + .6, .45)

# ---------- 7 CTA ----------
H.append('<div id="cta"><b>KAUNSA STATION AAPKE PAAS?</b><span>COMMENT KARO</span></div>')
J.append(f'tl.to("#dim", {{opacity:.55, duration:.3}}, {S(7):.2f}); tl.fromTo("#cta", {{opacity:0, scale:.8}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)"}}, {S(7):.2f}); tl.to("#cta span", {{scale:1.08, duration:.4, yoyo:true, repeat:3}}, {wt(7, "Comment"):.2f});')
sfx("sparkle", wt(7, "Comment"), .3)

# card exits: hold until the next card arrives, never blank
CARDS.sort(key=lambda c: c[1])
for i, (cid, t0, t1) in enumerate(CARDS):
    nxt = CARDS[i + 1][1] if i + 1 < len(CARDS) else END
    out = max(t1, min(nxt + .3, t1 + .5))
    J.append(f'tl.set("#{cid}", {{zIndex:{10 + i}}}, 0); tl.to("#{cid}", {{opacity:0, scale:.9, duration:.2, ease:"power2.in"}}, {out - .2:.2f});')

# captions (white box, black bold)
HI = ["bullet train", "Sach kya hai", "508 km", "2027", "886 km", "prastavit", "Behror", "Shahpura", "Kishangarh", "Bhilwara", "Chittorgarh", "Udaipur", "320 km/h", "survey aur DPR", "zameen ki demand", "zameen", "demand", "hotspots", "Gurugram", "Rewari", "DPR stage", "patta", "approved", "Bullet", "Delhi", "Jaipur", "3 ghante", "Delhi Jaipur Mumbai Expressway", "sabse lamba", "1,350 km", "Mumbai", "67 km", "Bandikui", "Bagrana", "saadhe chaar ghante", "8 lane tunnel",
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
H.append('<div id="cred">Routes indicative &middot; Sources: NHSRCL plans via Patrika, Metro Rail News, News On AIR &middot; Imagery: NASA Blue Marble &middot; States: Natural Earth</div>')
CSS = """@font-face{font-family:Anton;src:url(assets/fonts/anton.woff2)}@font-face{font-family:Mont;font-weight:700;src:url(assets/fonts/mont700.woff2)}@font-face{font-family:Mont;font-weight:800;src:url(assets/fonts/mont800.woff2)}@font-face{font-family:Mont;font-weight:900;src:url(assets/fonts/mont900.woff2)}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#1b1b1d}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif}#world{position:absolute;inset:0;width:1080px;height:1920px}.y{color:#111;background:#FFC42E;border-radius:6px;padding:0 6px}
#face{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:40}
#clouds{position:absolute;inset:0;z-index:15;pointer-events:none;overflow:hidden}#clouds img{position:absolute;left:-260px;top:-240px;width:1600px;height:2400px}
#wm{position:absolute;left:0;right:0;top:190px;text-align:center;font:800 24px Mont;letter-spacing:.34em;color:rgba(255,255,255,.55);z-index:20}
#cred{position:absolute;left:40px;right:40px;top:1650px;text-align:center;font:700 17px Mont;color:rgba(255,255,255,.55);z-index:20}
#title{position:absolute;left:0;right:0;top:300px;text-align:center;opacity:0;z-index:16}#title span{font:400 96px/1 Anton;color:#fff;text-shadow:0 6px 30px #000}#title i{font-style:normal;font:900 70px Mont;color:#3CE65A;margin:0 10px}
#title b{display:block;margin-top:14px;font:400 150px/1 Anton;color:#3CE65A;text-shadow:0 0 30px rgba(60,230,90,.7),0 6px 30px #000;font-weight:400}
#glow{position:absolute;left:0;right:0;top:620px;text-align:center;opacity:0;z-index:16;font:900 78px/1.05 Mont;color:#B9FFB0;text-shadow:0 0 18px #3CE65A,0 0 40px #3CE65A,0 6px 20px #000}
.nb{display:inline-block;width:46px;height:46px;line-height:46px;text-align:center;border-radius:50%;background:#FFC42E;color:#111;font:900 30px Mont;text-shadow:none;margin-right:6px}.ml{position:absolute;opacity:0;translate:-50% -50%;font:900 44px Mont;color:#fff;white-space:nowrap;text-shadow:0 3px 0 #000,0 0 14px #000;z-index:6}.ml.y{color:#FFC42E}.ml.p{color:#FF4FA3}
.big{position:absolute;left:40px;right:40px;top:300px;opacity:0;text-align:center;z-index:9}.big b{display:block;font:400 150px/1 Anton;color:#3CE65A;text-shadow:0 0 24px rgba(60,230,90,.6),0 6px 20px #000;font-weight:400}
.big span{display:inline-block;margin-top:8px;padding:8px 22px;border-radius:10px;background:#fff;color:#111;font:900 32px Mont}
#time{position:absolute;left:50px;right:50px;top:330px;opacity:0;display:flex;gap:20px;z-index:9}.tb{flex:1;padding:20px;border-radius:24px;text-align:center;background:rgba(10,10,12,.9)}
.tb small{display:block;font:900 26px Mont;color:#fff;letter-spacing:.06em}.tb b{display:block;font:400 110px/1 Anton;font-weight:400}.tb.old{border:4px solid #FF3B3B}.tb.old b{color:#FF3B3B;text-decoration:line-through}.tb.new{border:4px solid #3CE65A}.tb.new b{color:#3CE65A}
.card{position:absolute;opacity:0;padding:14px 14px 16px;border-radius:24px;background:#fff;box-shadow:0 30px 70px rgba(0,0,0,.7);z-index:8;text-align:center}
.iw{position:relative;margin:0 auto;border-radius:14px;overflow:hidden}.card img{display:block;border-radius:14px;object-fit:cover;transform-origin:50% 50%}.scan{position:absolute;top:-4%;bottom:-4%;width:8px;margin-left:-4px;background:#fff;box-shadow:0 0 18px #fff,0 0 30px #3CE65A;opacity:0}.ct{margin-top:10px;font:400 52px/1.05 Anton;color:#14161c;letter-spacing:.02em}.cs{margin-top:6px;font:700 26px Mont;color:#5b6070}
.ci{margin:10px 6px 0;padding-top:10px;border-top:2px solid #e3e3e8;text-align:left;font:700 26px/1.32 Mont;color:#2a2d36}
.tg{position:absolute;left:-12px;top:-22px;padding:8px 20px;border-radius:30px;font:900 28px Mont;color:#111;box-shadow:0 6px 16px rgba(0,0,0,.4);z-index:2}
#legend{position:absolute;left:50px;top:1290px;opacity:0;display:flex;gap:24px;z-index:9}#legend span{display:flex;align-items:center;gap:10px;padding:8px 16px;border-radius:12px;background:rgba(10,10,12,.85);font:900 28px Mont;color:#fff}#legend i{display:inline-block;width:46px;height:8px;border-radius:4px}#legend i.dsh{background:repeating-linear-gradient(90deg,#fff 0 12px,transparent 12px 20px)}
#spd{position:absolute;left:60px;right:60px;top:420px;opacity:0;z-index:9}.sp{margin-bottom:22px;padding:18px 24px;border-radius:22px;background:rgba(10,10,12,.92);border:3px solid #555}.sp.hot{border-color:#3CE65A}.sp small{font:900 30px Mont;color:#fff}.sp b{float:right;font:400 70px/1 Anton;color:#3CE65A;font-weight:400}.sp u{display:block;clear:both;margin-top:10px;height:18px;border-radius:9px;background:#3CE65A;text-decoration:none}#spd em{display:block;text-align:right;font-style:normal;font:900 30px Mont;color:#fff}
#stat{position:absolute;left:60px;right:60px;top:380px;opacity:0;padding:30px;border-radius:26px;background:#fff;z-index:10;text-align:center}#stat b{display:block;font:400 76px/1 Anton;color:#D32F2F;font-weight:400}#stat p{margin-top:12px;font:900 36px Mont;color:#111}
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
