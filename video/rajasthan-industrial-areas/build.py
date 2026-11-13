"""Rajasthan upcoming industrial areas — 3D map tour. Pin positions approximate. Sources: RIICO MIS Jun-2026, RIICO DAP 2025, Rising Rajasthan brochure."""
import json, math, os, random
P = "proj"
LINES = [
    "Rajasthan mein pichhle do saal mein 30 se zyada naye industrial areas khule hain, aur aur bhi aa rahe hain. Chaliye north se south dekhte hain.",
    "Sabse upar, Bhiwadi mein Salarpur, Honda, Hero aur Maruti ke paas.",
    "Bikaner mein Gajner, ceramic industry ke liye.",
    "Jaipur mein Bichoon, Phulera freight corridor ke paas. Tonk Road par naya Fintech Park. Kunjbiharipura, Bagru ke paas, auto aur heavy engineering ke liye. Aur Hukkan-Nimodia, Jaipur-Kota highway par.",
    "Jodhpur mein Boranada Extension aur Medical Device Park.",
    "Bhilwara mein Rupaheli Textile Park, jahan allotment shuru ho chuka hai.",
    "Balotra mein Petro Zone, refinery ke bilkul paas.",
    "Chittorgarh mein Soniyana, glass aur ceramic ke liye.",
    "Aur sabse neeche, Kota mein Gundi Fatehpur.",
    "Real estate ka funda simple hai: jahan industry, wahan naukri, aur jahan naukri, wahan ghar aur plot ki demand.",
    "Aapke zile mein kaunsa industrial area aa raha hai? Comment karo.",
]
VOICE = os.path.exists("rec/phrases.json")
if VOICE: PH = json.load(open("rec/phrases.json"))
else:
    PH = []; t = .3
    for l in LINES:
        d = len(l) / 15 + .15
        if not PH: d += 1.0
        PH.append({"s": round(t, 2), "e": round(t + d, 2), "t": l}); t += d + .3
def S(k): return PH[k]["s"]
def E(k): return PH[k]["e"]
def wt(k, w):
    t = PH[k]["t"]; i = t.lower().find(w.lower()); assert i >= 0, (k, w)
    return S(k) + (E(k) - S(k)) * i / len(t)
END = round(E(10) + 1.0, 2)
def wp(lat, lon):
    n = 2 ** 13
    return (((lon + 180) / 360 * n) - 5791) * 256, (((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n) - 3466) * 256
SVG, H, J, SFX, IN = [], [], [], [], []
def sfx(n, t, v=.3): SFX.append(f'<audio id="sx{len(SFX)}" class="clip" src="assets/sfx/{n}.mp3" data-start="{t:.2f}" data-duration="2" data-track-index="{20 + len(SFX)}" data-volume="{v}"></audio>')
def pd(pts, close=False): return "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts) + (" Z" if close else "")
GOLD, CREAM, GRN, ORG = "#C9A24A", "#F3E6C8", "#3CE65A", "#FF9A3C"

CX, CY, CW = -3400, 300, 62000
CH = CW * 1920 / 1080
def scr(p): return ((p[0] - (CX - CW / 2)) / CW * 1080, (p[1] - (CY - CH / 2)) / CH * 1920)
U = CW / 1080

SVG.append('<rect x="-900000" y="-900000" width="2000000" height="2000000" style="fill:#1b1b1d"/>')
for href, x, y, w, h in [("bm4.jpg", -302848, -363008, 786432, 786432), ("bm5.jpg", -171776, -166400, 327680, 393216), ("bm7.webp", -40704, -35328, 81920, 65536)]:
    SVG.append(f'<image href="assets/img/{href}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="none"/>')
SVG.append('<rect x="-900000" y="-900000" width="2000000" height="2000000" style="fill:#000;opacity:.35"/>')
ST = json.load(open("data/states.json"))
def ring(rs): return " ".join(pd([wp(la, lo) for lo, la in r], True) for r in rs)
SVG.append(f'<path id="raj" d="{ring(ST["Rajasthan"])}" style="fill:{GOLD};fill-opacity:.05;stroke:{GOLD};stroke-width:4;vector-effect:non-scaling-stroke"/>')
DG = {f["properties"]["district"]: f for f in json.load(open("data/rajasthan_districts.geojson"))["features"]}
def gpath(g):
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    return " ".join(pd([wp(la, lo) for lo, la in r], True) for poly in polys for r in poly[:1])
for nm, f in DG.items():
    SVG.append(f'<path class="dz" id="dz_{nm.replace(" ", "_")}" d="{gpath(f["geometry"])}" style="fill:{GRN};fill-opacity:0;stroke:#fff;stroke-width:1.5;stroke-opacity:.18;vector-effect:non-scaling-stroke;stroke-linejoin:round"/>')

# industrial areas: key, name, (lat, lon), district, tag, icon, line, keyword, status
IA = [
    ("kunj", "KUNJBIHARIPURA", (26.78, 75.52), "Jaipur", "AUTO &middot; HEAVY ENGG", "&#128663;", 1, "Kunjbiharipura", "new"),
    ("bich", "BICHOON", (26.83, 75.33), "Jaipur", "PHULERA DFC KE PAAS", "&#9728;&#65039;", 1, "Bichoon", "new"),
    ("hukk", "HUKKAN-NIMODIA", (26.62, 75.85), "Jaipur", "JAIPUR-KOTA NH-52", "&#127981;", 1, "Hukkan", "new"),
    ("fin", "FINTECH PARK", (26.83, 75.80), "Jaipur", "IT &middot; AI &middot; TONK ROAD", "&#128187;", 1, "Fintech", "soon"),
    ("sal", "SALARPUR", (28.17, 76.86), "Khairthal-Tijara", "HONDA &middot; HERO &middot; MARUTI", "&#128664;", 2, "Salarpur", "new"),
    ("bor", "BORANADA + MEDTECH PARK", (26.15, 73.07), "Jodhpur", "MEDTECH &middot; THAR DRY PORT", "&#129658;", 3, "Boranada", "new"),
    ("pet", "PETRO ZONE", (25.86, 72.25), "Balotra", "REFINERY KE PAAS", "&#128738;&#65039;", 4, "Petro", "soon"),
    ("rup", "RUPAHELI TEXTILE PARK", (25.98, 74.50), "Bhilwara", "ALLOTMENT SHURU", "&#129525;", 5, "Rupaheli", "new"),
    ("son", "SONIYANA", (25.13, 74.52), "Chittorgarh", "GLASS &middot; CERAMIC", "&#129346;", 5, "Soniyana", "new"),
    ("gaj", "GAJNER", (27.95, 73.06), "Bikaner", "CERAMIC PARK", "&#127994;", 5, "Gajner", "new"),
    ("gun", "GUNDI FATEHPUR", (24.84, 75.95), "Kota", "STONE &middot; AGRO", "&#129704;", 5, "Gundi", "new"),
]
IP = {k: wp(*ll) for k, _, ll, *_ in IA}
for k, nm, ll, dist, tag, ic, li, kw, stt in IA:
    x, y = IP[k]; col = ORG if stt == "soon" else GOLD
    SVG.append(f'<g class="pin" id="pn_{k}"><circle class="halo" cx="{x:.0f}" cy="{y:.0f}" r="{U * 14:.0f}" style="fill:{col};fill-opacity:.25;stroke:{col};stroke-width:2;vector-effect:non-scaling-stroke"/>'
               f'<circle class="core" cx="{x:.0f}" cy="{y:.0f}" r="{U * 9:.0f}" style="fill:#F7E3A8;stroke:#fff;stroke-width:2.5;vector-effect:non-scaling-stroke"/></g>')
# DMIC strip (Delhi -> Bhiwadi -> Jaipur -> Ajmer -> Marwar)
DMIC = [wp(*p) for p in [(28.61, 77.21), (28.17, 76.86), (27.70, 76.20), (26.91, 75.79), (26.45, 74.64), (25.75, 73.6)]]
SVG.append(f'<path id="dmic" d="{pd(DMIC)}" pathLength="1" style="fill:none;stroke:{GOLD};stroke-width:18;stroke-opacity:.35;stroke-linecap:round;vector-effect:non-scaling-stroke;stroke-dasharray:1;stroke-dashoffset:1"/>')

def pin3d(k):  # labels inside plane (billboards)
    x, y = scr(IP[k]); nm = [a for a in IA if a[0] == k][0]
    IN.append(f'<div class="fb" id="fb_{k}" style="left:{x - 8:.0f}px;top:{y - 30:.0f}px;width:16px;height:30px"></div>')
    dx, dy = {"kunj": (-60, 0), "bich": (-40, 22), "hukk": (40, 40), "fin": (50, -8), "rup": (0, 0), "bor": (-30, 0)}.get(k, (0, 0))
    IN.append(f'<div class="bb ov" id="ov_{k}" style="left:{x + dx:.0f}px;top:{y - 30 + dy:.0f}px"><span>{nm[1]}</span></div>')
for a in IA: pin3d(a[0])

def lux(i, html, t, until, x, y, cls=""):
    H.append(f'<div class="lx {cls}" id="lx{i}" style="left:{x}px;top:{y}px">{html}</div>')
    J.append(f'tl.fromTo("#lx{i}", {{opacity:0, y:24, clipPath:"inset(0 100% 0 0)"}}, {{opacity:1, y:0, clipPath:"inset(0 0% 0 0)", duration:.45, ease:"power3.out"}}, {t:.2f}); tl.to("#lx{i}", {{opacity:0, y:-14, duration:.3}}, {until - .3:.2f});')
    sfx("click-soft", t, .3)
def plane(t, rx, sc, x, y, d=1.0): J.append(f'tl.to("#plane", {{rotationX:{rx}, scale:{sc}, x:{x:.0f}, y:{y:.0f}, duration:{d}, ease:"power2.inOut"}}, {t:.2f});')
def focus(p, rx, sc, ty=1000):
    x, y = scr(p); return rx, sc, (540 - x) * sc, (ty - y) * sc
def dist_on(nm, t, until):
    i = nm.replace(" ", "_")
    J.append(f'tl.to("#dz_{i}", {{fillOpacity:.32, strokeOpacity:1, strokeWidth:4, duration:.4}}, {t:.2f}); tl.to("#dz_{i}", {{fillOpacity:0, strokeOpacity:.18, strokeWidth:1.5, duration:.4}}, {until:.2f});')

J.append('tl.set("#plane", {rotationX:30, scale:1, x:0, y:0, transformOrigin:"50% 50%"}, 0); tl.set(".bb", {xPercent:-50, yPercent:-100, rotationX:-30, transformOrigin:"50% 100%"}, 0); tl.set(".fb", {scaleY:0.001, rotationX:-90, transformOrigin:"50% 100%"}, 0);')

# ---------- 0 OVERVIEW (all at once, hold for screenshot) ----------
OV = focus(wp(26.6, 74.0), 30, 1.75, 900)
J.append(f'tl.fromTo("#plane", {{rotationX:10, scale:1.2, x:{OV[2] * .7:.0f}, y:{OV[3] * .7:.0f}}}, {{rotationX:30, scale:{OV[1]}, x:{OV[2]:.0f}, y:{OV[3]:.0f}, duration:1.4, ease:"power3.out"}}, 0);')
for i, a in enumerate(IA):
    k = a[0]; t = .35 + i * .06
    J.append(f'tl.fromTo("#pn_{k}", {{opacity:0}}, {{opacity:1, duration:.2}}, {t:.2f}); tl.fromTo("#pn_{k} .halo", {{attr:{{r:{U * 6:.0f}}}}}, {{attr:{{r:{U * 14:.0f}}}, duration:.5, ease:"back.out(2)", immediateRender:false}}, {t:.2f});'
             f'tl.to("#fb_{k}", {{scaleY:1, rotationX:-90, duration:.4, ease:"back.out(2)"}}, {t:.2f}); tl.fromTo("#ov_{k}", {{opacity:0}}, {{opacity:1, duration:.25, immediateRender:false}}, {t + .1:.2f}); tl.to("#ov_{k}", {{opacity:0, duration:.25}}, {S(1) - .4:.2f});')
    sfx("click-soft", t, .15)
J.append(f'tl.to("#dmic", {{strokeDashoffset:0, duration:1.2, ease:"power2.inOut"}}, 1.2);')
H.append('<div id="hook"><small>RAJASTHAN KE</small><b>NAYE INDUSTRIAL AREAS</b><span>&#128278; SAVE KAR LO</span></div>')
J.append(f'tl.fromTo("#hook", {{opacity:0, scale:1.1}}, {{opacity:1, scale:1, duration:.4, ease:"power3.out"}}, 0); tl.fromTo("#hook span", {{opacity:0, scale:1.4}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)", immediateRender:false}}, 1.6); tl.to("#hook span", {{scale:1.08, duration:.35, yoyo:true, repeat:5}}, 2.0); tl.to("#hook", {{opacity:0, y:-30, duration:.3}}, {S(1) - .3:.2f});')
lux(0, "<b>30+</b> NAYE &middot; AUR AA RAHE HAIN", wt(0, "30") - .1, wt(0, "Chaliye") - .1, 200, 1300)
lux(1, "NORTH <b>&darr;</b> SOUTH", wt(0, "Chaliye") - .1, S(1) - .1, 380, 1300)
sfx("impact-bass-1", 0, .45); sfx("riser", .5, .3)

# ---------- tour (north -> south): district zoom on 3D map + crisp labelled locator map ----------
REF = {
 "sal": ([("BHIWADI", (28.21, 76.86)), ("DHARUHERA", (28.21, 76.79)), ("TIJARA", (27.93, 76.86)), ("REWARI", (28.19, 76.62))], [("NH-48", [(28.45, 77.03), (28.21, 76.79), (27.95, 76.52)])]),
 "gaj": ([("BIKANER", (28.02, 73.31)), ("KOLAYAT", (27.84, 72.95))], [("NH-11", [(28.02, 73.31), (27.93, 73.10), (27.80, 72.92)])]),
 "bich": ([("PHULERA", (26.87, 75.24)), ("DUDU", (26.68, 75.24)), ("BAGRU", (26.81, 75.54)), ("SAMBHAR", (26.91, 75.18))], [("NH-48", [(26.91, 75.79), (26.81, 75.54), (26.68, 75.24)])]),
 "fin": ([("JAIPUR", (26.92, 75.80)), ("AIRPORT", (26.824, 75.812)), ("SITAPURA", (26.78, 75.85)), ("SANGANER", (26.82, 75.79))], [("TONK ROAD", [(26.93, 75.80), (26.86, 75.80), (26.76, 75.83)])]),
 "kunj": ([("JAIPUR", (26.91, 75.79)), ("BAGRU", (26.81, 75.54)), ("PHAGI", (26.57, 75.54))], [("NH-48", [(26.91, 75.79), (26.81, 75.54), (26.68, 75.24)])]),
 "hukk": ([("JAIPUR", (26.91, 75.79)), ("SITAPURA", (26.78, 75.85)), ("CHAKSU", (26.60, 75.95))], [("NH-52", [(26.91, 75.79), (26.79, 75.82), (26.60, 75.95), (26.42, 76.05)])]),
 "bor": ([("JODHPUR", (26.24, 73.02)), ("LUNI", (26.00, 73.00)), ("BASNI", (26.22, 73.03))], [("NH-62", [(26.24, 73.02), (26.10, 73.10), (25.90, 73.25)])]),
 "rup": ([("GULABPURA", (25.90, 74.66)), ("BHILWARA", (25.35, 74.63))], [("NH-48", [(25.35, 74.63), (25.90, 74.66), (26.20, 74.65)])]),
 "pet": ([("BALOTRA", (25.83, 72.24)), ("PACHPADRA REFINERY", (25.95, 72.27))], [("NH-25", [(25.75, 72.05), (25.83, 72.24), (25.95, 72.45)])]),
 "son": ([("HAMIRGARH", (25.18, 74.63)), ("BHILWARA", (25.35, 74.63)), ("CHITTORGARH", (24.88, 74.62))], [("NH-48", [(25.35, 74.63), (25.13, 74.63), (24.88, 74.62)])]),
 "gun": ([("KOTA", (25.18, 75.83)), ("RAMGANJ MANDI", (24.65, 75.94)), ("MORAK", (24.80, 75.98))], [("NH-52", [(25.18, 75.83), (24.95, 75.92), (24.65, 76.05)])]),
}
ORDER = [("sal", 1, "Salarpur"), ("gaj", 2, "Gajner"), ("bich", 3, "Bichoon"), ("fin", 3, "Fintech"), ("kunj", 3, "Kunjbiharipura"), ("hukk", 3, "Hukkan"),
         ("bor", 4, "Boranada"), ("rup", 5, "Rupaheli"), ("pet", 6, "Petro"), ("son", 7, "Soniyana"), ("gun", 8, "Gundi")]
PW, PHh = 960, 640
def bbox(pts):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; return min(xs), min(ys), max(xs), max(ys)
DB = {nm: bbox([wp(la, lo) for poly in (f["geometry"]["coordinates"] if f["geometry"]["type"] == "MultiPolygon" else [f["geometry"]["coordinates"]]) for r in poly[:1] for lo, la in r]) for nm, f in DG.items()}
def locator(k):
    a = [z for z in IA if z[0] == k][0]; towns, roads = REF[k]
    pts = [IP[k]] + [wp(*ll) for _, ll in towns]
    x0, y0, x1, y1 = bbox(pts); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    W = max((x1 - x0) * 1.45, (y1 - y0) * 1.45 * PW / PHh, 2600); Hh = W * PHh / PW
    vx0, vy0 = cx - W / 2, cy - Hh / 2; f = W / PW
    g = [f'<rect x="{vx0:.0f}" y="{vy0:.0f}" width="{W:.0f}" height="{Hh:.0f}" fill="#16120d"/>']
    g.append(f'<image href="assets/img/bm7.webp" x="-40704" y="-35328" width="81920" height="65536" preserveAspectRatio="none" opacity=".35"/>')
    for nm, (bx0, by0, bx1, by1) in DB.items():
        if bx1 < vx0 or bx0 > vx0 + W or by1 < vy0 or by0 > vy0 + Hh: continue
        on = nm == a[3]
        g.append(f'<path d="{gpath(DG[nm]["geometry"])}" style="fill:{GRN if on else "none"};fill-opacity:{.16 if on else 0};stroke:{"#fff" if on else "#8a7f6c"};stroke-width:{3 if on else 1.5};vector-effect:non-scaling-stroke"/>')
        if on:
            lx, ly = DG[nm]["properties"]["label"]; p = wp(ly, lx)
    for rn, rp in roads:
        P_ = [wp(*q) for q in rp]
        g.append(f'<path class="lr" d="{pd(P_)}" pathLength="1" style="fill:none;stroke:#FFC42E;stroke-width:9;stroke-linecap:round;stroke-linejoin:round;vector-effect:non-scaling-stroke;stroke-dasharray:1;stroke-dashoffset:1"/>')
        import itertools
        L_ = [0.0]
        for a_, b_ in zip(P_, P_[1:]): L_.append(L_[-1] + math.hypot(b_[0] - a_[0], b_[1] - a_[1]))
        best = None
        for fr in (.15, .3, .7, .85, .5):
            tg = L_[-1] * fr; j = next(m_ for m_ in range(1, len(L_)) if L_[m_] >= tg); u = (tg - L_[j - 1]) / max(1e-6, L_[j] - L_[j - 1])
            m = (P_[j - 1][0] + (P_[j][0] - P_[j - 1][0]) * u, P_[j - 1][1] + (P_[j][1] - P_[j - 1][1]) * u)
            dmin = min(math.hypot(m[0] - q[0], m[1] - q[1]) for q in [IP[k]] + [wp(*ll) for _, ll in towns])
            if not (vx0 + f * 60 < m[0] < vx0 + W - f * 60 and vy0 + f * 60 < m[1] < vy0 + Hh - f * 30): dmin = -1
            if best is None or dmin > best[0]: best = (dmin, m)
        m = best[1]
        g.append(f'<g class="lt"><rect x="{m[0] - f * 44:.0f}" y="{m[1] - f * 17:.0f}" width="{f * 88:.0f}" height="{f * 32:.0f}" rx="{f * 4:.0f}" fill="#FFC42E"/><text x="{m[0]:.0f}" y="{m[1] + f * 8:.0f}" text-anchor="middle" font-family="Mont" font-weight="900" font-size="{f * 22:.0f}" fill="#111">{rn}</text></g>')
    for tn, ll in towns:
        p = wp(*ll)
        g.append(f'<g class="lt"><circle cx="{p[0]:.0f}" cy="{p[1]:.0f}" r="{f * 8:.0f}" fill="#fff" stroke="#111" stroke-width="2" vector-effect="non-scaling-stroke"/>'
                 f'<text x="{p[0]:.0f}" y="{p[1] - f * 16:.0f}" text-anchor="middle" font-family="Mont" font-weight="800" font-size="{f * 26:.0f}" fill="#fff" stroke="#000" stroke-width="{f * 5:.0f}" paint-order="stroke" letter-spacing="{f * 1.5:.1f}">{tn}</text></g>')
    x, y = IP[k]
    g.append(f'<g class="lp"><circle class="lpr" cx="{x:.0f}" cy="{y:.0f}" r="{f * 30:.0f}" fill="{GOLD}" fill-opacity=".3" stroke="{GOLD}" stroke-width="3" vector-effect="non-scaling-stroke"/>'
             f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{f * 13:.0f}" fill="#F7E3A8" stroke="#fff" stroke-width="3" vector-effect="non-scaling-stroke"/>'
             f'<rect x="{x - f * (len(a[1]) * 9.2 + 20):.0f}" y="{y + f * 22:.0f}" width="{f * (len(a[1]) * 18.4 + 40):.0f}" height="{f * 44:.0f}" rx="{f * 4:.0f}" fill="#1a140c" stroke="{GOLD}" stroke-width="2" vector-effect="non-scaling-stroke"/>'
             f'<text x="{x:.0f}" y="{y + f * 53:.0f}" text-anchor="middle" font-family="Mont" font-weight="900" font-size="{f * 28:.0f}" fill="#F7E3A8" letter-spacing="{f * 1:.1f}">{a[1]}</text></g>')
    km = W / (256 * 2 ** 13 / 40075 / math.cos(math.radians(26.5)))
    H.append(f'<div class="loc" id="loc_{k}"><svg viewBox="{vx0:.0f} {vy0:.0f} {W:.0f} {Hh:.0f}" width="{PW}" height="{PHh}">{"".join(g)}</svg><div class="lh">&#128205; EXACT LOCATION &middot; {a[3].upper()} ZILA</div><div class="ls">~{km:.0f} KM VIEW &middot; approx.</div></div>')
def card(k, t, until):
    a = [x for x in IA if x[0] == k][0]
    soon = '<em>COMING SOON</em>' if a[8] == "soon" else '<em class="n">NAYA</em>'
    H.append(f'<div class="card" id="cd_{k}"><i>{a[5]}</i><div><small>{a[3].upper()} {soon}</small><b>{a[1]}</b><span>{a[4]}</span></div></div>')
    J.append(f'tl.fromTo("#cd_{k}", {{opacity:0, x:-60}}, {{opacity:1, x:0, duration:.35, ease:"power3.out"}}, {t:.2f}); tl.fromTo("#cd_{k} i", {{scale:2, rotation:-15}}, {{scale:1, rotation:0, duration:.4, ease:"back.out(2.5)"}}, {t:.2f}); tl.to("#cd_{k}", {{opacity:0, x:40, duration:.2}}, {until - .2:.2f});')
    sfx("pop", t, .3)
def show_loc(k, t, until):
    locator(k)
    J.append(f'tl.fromTo("#loc_{k}", {{opacity:0, y:60, scale:.9}}, {{opacity:1, y:0, scale:1, duration:.4, ease:"power3.out"}}, {t:.2f}); tl.to("#loc_{k}", {{opacity:0, y:30, duration:.2}}, {until - .2:.2f});'
             f'tl.to("#loc_{k} .lr", {{strokeDashoffset:0, duration:.6, ease:"power2.out"}}, {t + .2:.2f}); tl.fromTo("#loc_{k} .lt", {{opacity:0}}, {{opacity:1, duration:.25, stagger:.08, immediateRender:false}}, {t + .3:.2f});'
             f'tl.fromTo("#loc_{k} .lp", {{opacity:0, scale:2.5, transformOrigin:"50% 50%", transformBox:"fill-box"}}, {{opacity:1, scale:1, duration:.4, ease:"back.out(2.5)", immediateRender:false}}, {t + .45:.2f});'
             f'tl.fromTo("#loc_{k} .lpr", {{scale:.6, transformOrigin:"50% 50%", transformBox:"fill-box"}}, {{scale:1.8, opacity:0, duration:.9, repeat:3, immediateRender:false}}, {t + .8:.2f});')
    sfx("click-soft", t + .45, .35)
prev_d = None
for i, (k, li, kw) in enumerate(ORDER):
    a = [z for z in IA if z[0] == k][0]
    t = wt(li, kw) - .15 if li == 3 else S(li) + .05
    nk = ORDER[i + 1] if i + 1 < len(ORDER) else None
    nxt = (wt(nk[1], nk[2]) - .15 if nk[1] == 3 else S(nk[1]) + .05) if nk else S(9) - .05
    if a[3] != prev_d:
        rx, sc, x, y = focus(IP[k] if a[3] != "Jaipur" else wp(26.78, 75.6), 40, 3.0, 760); plane(t - .4, rx, sc, x, y, .7); sfx("whoosh", t - .4, .3)
        until_d = nxt
        if a[3] == "Jaipur": until_d = wt(3, "Hukkan") + 2.5 if False else S(4) - .05
        dist_on(a[3], t - .2, until_d - .1)
    J.append(f'tl.fromTo("#pn_{k} .halo", {{attr:{{r:{U * 6:.0f}}}}}, {{attr:{{r:{U * 20:.0f}}}, duration:.8, repeat:2, ease:"power2.out", immediateRender:false}}, {t:.2f});')
    card(k, t, nxt); show_loc(k, t + .25, nxt)
    prev_d = a[3]
J.append(f'tl.to("#dmic", {{strokeOpacity:.8, duration:.4}}, {S(1):.2f}); tl.to("#dmic", {{strokeOpacity:.35, duration:.4}}, {S(2):.2f});')

# ---------- 6 real estate: back to overview, rings ----------
plane(S(9) - .3, *OV, 1.1)
for i, a in enumerate(IA):
    t = S(9) + .4 + i * .06
    J.append(f'tl.fromTo("#pn_{a[0]} .halo", {{attr:{{r:{U * 10:.0f}}}, fillOpacity:.35}}, {{attr:{{r:{U * 80:.0f}}}, fillOpacity:0, duration:1.1, repeat:2, ease:"power2.out", immediateRender:false}}, {t:.2f});')
H.append('<div id="flow2"><span>INDUSTRY</span><i>&rarr;</i><span>NAUKRI</span><i>&rarr;</i><b>GHAR &amp; PLOT KI DEMAND &#9650;</b></div>')
J.append(f'tl.fromTo("#flow2", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.4, ease:"power3.out"}}, {S(9):.2f}); tl.fromTo("#flow2 b", {{opacity:0, x:30}}, {{opacity:1, x:0, duration:.4, immediateRender:false}}, {wt(9, "ghar") - .1:.2f}); tl.to("#flow2", {{opacity:0, duration:.3}}, {S(10) - .1:.2f});')
sfx("riser", S(9), .3)

# ---------- 7 CTA ----------
H.append('<div id="cta"><b>AAPKE ZILE MEIN KAUNSA INDUSTRIAL AREA AA RAHA HAI?</b><span>COMMENT KARO</span></div>')
J.append(f'tl.to("#dim", {{opacity:.5, duration:.3}}, {S(10):.2f}); tl.fromTo("#cta", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.45, ease:"power3.out"}}, {S(10):.2f}); tl.to("#cta span", {{scale:1.06, duration:.4, yoyo:true, repeat:3}}, {wt(10, "Comment"):.2f});')
sfx("sparkle", wt(10, "Comment"), .3)

# ---------- captions ----------
HI = ["30 se zyada", "Kunjbiharipura", "Bichoon", "Hukkan-Nimodia", "Fintech Park", "Salarpur", "Boranada Extension", "Medical Device Park", "Petro Zone", "Rupaheli Textile Park", "Soniyana", "Gajner", "Gundi Fatehpur", "north se south",
      "ghar ki demand", "Comment"]
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
H.append('<div id="cred">Sources: RIICO MIS (June 2026), RIICO DAP 2025, Rising Rajasthan &middot; pin locations approximate &middot; Imagery: NASA Blue Marble, Sentinel-2 (EOX)</div>')

CSS = """@font-face{font-family:Anton;src:url(assets/fonts/anton.woff2)}@font-face{font-family:Mont;font-weight:700;src:url(assets/fonts/mont700.woff2)}@font-face{font-family:Mont;font-weight:800;src:url(assets/fonts/mont800.woff2)}@font-face{font-family:Mont;font-weight:900;src:url(assets/fonts/mont900.woff2)}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#0d0b09}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif}.y{color:#111;background:#F2B23E;border-radius:6px;padding:0 6px}
#stage{position:absolute;inset:0;perspective:1500px;perspective-origin:50% 28%;overflow:hidden;background:#1b1b1d}#plane{position:absolute;inset:0;transform-style:preserve-3d}
#world{position:absolute;left:-2160px;top:-3840px;width:5400px;height:9600px}
.bb{position:absolute;white-space:nowrap;opacity:0}.bb span{display:inline-block;padding:3px 7px;border-radius:3px;background:rgba(14,12,9,.92);border:1px solid #C9A24A;color:#F7E3A8;font:800 12px Mont;letter-spacing:.04em}
.fb{position:absolute;transform-origin:50% 100%;background:linear-gradient(90deg,#a07a2a,#F7E3A8 50%,#a07a2a);clip-path:polygon(0 30%,35% 10%,35% 30%,70% 10%,70% 30%,100% 0,100% 100%,0 100%);filter:drop-shadow(0 0 8px #C9A24A)}
.rb{position:absolute;white-space:nowrap}.rb span{display:inline-block;border-radius:1px}.rb.town span{padding:.4px 1.2px;background:rgba(255,255,255,.92);color:#111;font:800 3.4px Mont;letter-spacing:.03em}
.rb.road span{padding:.4px 1.2px;background:#FFC42E;color:#111;font:900 3px Mont}.rb.main span{padding:.6px 1.6px;background:linear-gradient(135deg,#1a140c,#2e2416);border:.3px solid #C9A24A;color:#F7E3A8;font:900 4.2px Mont;letter-spacing:.04em;box-shadow:0 0 3px #C9A24A}
.loc{position:absolute;left:50px;top:720px;width:980px;opacity:0;z-index:14;padding:10px 10px 12px;border-radius:8px;border:1.5px solid #C9A24A;background:linear-gradient(135deg,rgba(14,12,9,.97),rgba(34,27,18,.97));box-shadow:0 30px 70px rgba(0,0,0,.7)}
.loc svg{display:block;border-radius:4px}.loc .lh{position:absolute;left:24px;top:22px;padding:6px 14px;border-radius:4px;background:rgba(14,12,9,.9);border:1px solid #C9A24A;color:#F3E6C8;font:800 22px Mont;letter-spacing:.12em}
.loc .ls{margin-top:8px;text-align:right;font:700 18px Mont;color:#9a8f7c;letter-spacing:.1em}
#dim{position:absolute;inset:0;background:#000;opacity:0;z-index:5;pointer-events:none}
#face{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:40}
#cred{position:absolute;left:40px;right:40px;top:1650px;text-align:center;font:700 17px Mont;color:rgba(255,255,255,.6);z-index:20}
#hook{position:absolute;left:50px;right:50px;top:120px;z-index:16;text-align:center;padding:22px 20px;border-radius:8px;border:1.5px solid #C9A24A;background:linear-gradient(135deg,rgba(14,12,9,.93),rgba(34,27,18,.93))}
#hook small{display:block;font:700 30px Mont;letter-spacing:.3em;color:#F3E6C8}#hook b{display:block;margin-top:8px;font:400 92px/1 Anton;background:linear-gradient(180deg,#F7E3A8,#C9A24A);-webkit-background-clip:text;color:transparent}
#hook span{display:inline-block;margin-top:14px;padding:8px 22px;border-radius:4px;background:#C9A24A;color:#111;font:900 30px Mont;letter-spacing:.14em}
.lx{position:absolute;opacity:0;z-index:14;padding:16px 28px;border-radius:6px;background:linear-gradient(135deg,rgba(14,12,9,.93),rgba(34,27,18,.93));border:1.5px solid #C9A24A;color:#F3E6C8;font:700 30px/1.1 Mont;letter-spacing:.12em;white-space:nowrap}
.lx b{font:400 46px/1 Anton;letter-spacing:.04em;background:linear-gradient(180deg,#F7E3A8,#C9A24A);-webkit-background-clip:text;color:transparent}
#flow,#flow2{position:absolute;left:0;right:0;top:1300px;margin:0 auto;width:max-content;opacity:0;z-index:15;display:flex;align-items:center;gap:14px;padding:16px 26px;border-radius:6px;border:1.5px solid #C9A24A;background:linear-gradient(135deg,rgba(14,12,9,.95),rgba(34,27,18,.95))}
#flow span,#flow2 span{font:400 40px Anton;color:#F3E6C8}#flow i,#flow2 i{font:300 40px Mont;color:#C9A24A;font-style:normal}#flow b,#flow2 b{font:400 40px Anton;color:#3CE65A}#flow2{top:260px}
.card{position:absolute;left:50px;right:50px;top:210px;opacity:0;z-index:15;display:flex;align-items:center;gap:24px;padding:22px 26px;border-radius:8px;border:1.5px solid #C9A24A;background:linear-gradient(135deg,rgba(14,12,9,.95),rgba(34,27,18,.95));box-shadow:0 24px 60px rgba(0,0,0,.6)}
.card i{font-style:normal;font-size:96px;line-height:1}.card small{display:flex;align-items:center;gap:12px;font:700 26px Mont;letter-spacing:.2em;color:#F3E6C8}
.card em{font-style:normal;padding:3px 10px;border-radius:3px;background:#FF9A3C;color:#111;font:900 20px Mont;letter-spacing:.1em}.card em.n{background:#3CE65A}
.card b{display:block;margin-top:6px;font:400 60px/1.02 Anton;background:linear-gradient(180deg,#F7E3A8,#C9A24A);-webkit-background-clip:text;color:transparent}.card span{display:block;margin-top:6px;font:800 26px Mont;letter-spacing:.1em;color:#9BE3FF}
#cta{position:absolute;left:60px;right:60px;top:420px;opacity:0;text-align:center;z-index:16}#cta b{display:block;padding:24px;border-radius:6px;background:linear-gradient(135deg,rgba(14,12,9,.95),rgba(34,27,18,.95));border:1.5px solid #C9A24A;color:#F3E6C8;font:400 72px/1.05 Anton}
#cta span{display:inline-block;margin-top:24px;padding:14px 34px;border-radius:4px;background:#C9A24A;color:#111;font:900 40px Mont;letter-spacing:.22em}
.cp{position:absolute;left:40px;right:40px;top:1470px;text-align:center;opacity:0;z-index:35}
.cp div{display:inline-block;padding:4px 20px 8px;border-radius:10px;background:#fff;font:900 60px/1.12 Mont;color:#111;box-shadow:0 8px 24px rgba(0,0,0,.45)}"""
audio = (f'<audio id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{END}" data-track-index="1" data-volume="1"></audio><audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.12" data-fade-out="1.5"></audio>' if VOICE
         else f'<audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.55" data-fade-out="1.5"></audio>')
open(f"{P}/index.html", "w").write(f"""<!doctype html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="30">
<div id="stage"><div id="plane"><svg id="world" viewBox="{CX - 2.5 * CW:.0f} {CY - 2.5 * CH:.0f} {5 * CW:.0f} {5 * CH:.0f}" preserveAspectRatio="xMidYMid slice">{"".join(SVG)}</svg>{"".join(IN)}</div></div><div id="dim"></div>
{"".join(H)}
{audio}
{"".join(SFX)}
</div><script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(J)}
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>""")
print("END", END, [p["s"] for p in PH])
