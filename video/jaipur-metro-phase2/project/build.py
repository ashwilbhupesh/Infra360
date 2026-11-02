"""Jaipur Metro reel (text-led): dark satellite map, Pink Line (OSM) + Phase-2 Orange Line (indicative, via Tonk Rd / Sikar Rd) drawing on with stations."""
import json, math, os
import numpy as np
P = "proj"; Z = 13; OXT, OYT = 5816, 3455
def wp(lat, lon):
    n = 256 * 2 ** Z
    return ((lon + 180) / 360 * n - OXT * 256, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n - OYT * 256)
def vb(c, w): h = w * 1920 / 1080; return f"{c[0] - w / 2:.1f} {c[1] - h / 2:.1f} {w:.1f} {h:.1f}"
def cat(pts, n=14):
    """Catmull-Rom through pts -> dense polyline."""
    P_ = [pts[0]] + pts + [pts[-1]]; out = []
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = map(np.array, P_[i - 1:i + 3])
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(tuple(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)))
    out.append(tuple(pts[-1])); return out
def cum(pl):
    d = [0.0]
    for a, b in zip(pl, pl[1:]): d.append(d[-1] + math.dist(a, b))
    return d
def nearest_s(pl, cs, p): i = min(range(len(pl)), key=lambda k: math.dist(pl[k], p)); return cs[i], pl[i]
def pd(pl): return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pl)

# ---------- Pink Line from OSM (ordered chain of ways) ----------
segs = [[wp(g["lat"], g["lon"]) for g in e["geometry"]] for e in json.load(open("/home/user/work/plan/osm/metro.json"))["elements"]
        if e.get("geometry") and e.get("tags", {}).get("name") == "Pink Line (Jaipur Metro)"]
PST = {"Mansarovar": (26.87944, 75.75024), "New Aatish Market": (26.88015, 75.76447), "Vivek Vihar": (26.88845, 75.76841), "Shyam Nagar": (26.89648, 75.77063),
       "Ram Nagar": None, "Civil Lines": (26.90968, 75.78125), "Railway Station": (26.91811, 75.79013), "Sindhi Camp": (26.92247, 75.79963),
       "Chandpole": (26.9266, 75.80789), "Choti Chaupar": (26.92473, 75.81846), "Badi Chaupar": (26.92296, 75.82682)}
# chain: start from the way end nearest Mansarovar
start = wp(*PST["Mansarovar"]); chain = []; pool = [s for s in segs]
cur = min(pool, key=lambda s: min(math.dist(s[0], start), math.dist(s[-1], start)))
pool.remove(cur)
if math.dist(cur[-1], start) < math.dist(cur[0], start): cur = cur[::-1]
chain = list(cur)
while pool:
    e = chain[-1]; nx = min(pool, key=lambda s: min(math.dist(s[0], e), math.dist(s[-1], e)))
    if min(math.dist(nx[0], e), math.dist(nx[-1], e)) > 25: break
    pool.remove(nx)
    if math.dist(nx[-1], e) < math.dist(nx[0], e): nx = nx[::-1]
    chain += nx[1:]
PINK = chain; PC = cum(PINK)
# stations on the line, by arclength
PS = []
for nm, ll in PST.items():
    if ll is None: continue
    s, p = nearest_s(PINK, PC, wp(*ll)); PS.append((nm, s, p))
sA = [s for n, s, p in PS if n == "Shyam Nagar"][0]; sB = [s for n, s, p in PS if n == "Civil Lines"][0]
sm = (sA + sB) / 2; i = min(range(len(PINK)), key=lambda k: abs(PC[k] - sm)); PS.append(("Ram Nagar", PC[i], PINK[i]))
PS.sort(key=lambda x: x[1])
PINK = PINK[:min(range(len(PINK)), key=lambda k: math.dist(PINK[k], wp(*PST["Badi Chaupar"]))) + 1]; PC = cum(PINK)

# ---------- Orange Line (indicative) ----------
OST = [("Prahladpura", 26.7389, 75.8647), ("India Gate · Sitapura", 26.7854, 75.8223), ("Kumbha Marg", 26.7992, 75.8119), ("Haldighati Gate", 26.8060, 75.8067),
       ("Pinjrapole Gaushala", 26.8121, 75.8021), ("Sanganer", 26.8262, 75.7984), ("B2 Bypass", 26.8385, 75.7939), ("Durgapura", 26.8465, 75.7942),
       ("Mahaveer Nagar", 26.8573, 75.7953), ("Dev Nagar", 26.8650, 75.7964), ("Gandhi Nagar", 26.8710, 75.7971), ("Tonk Phatak", 26.8790, 75.7989),
       ("Rambagh Circle", 26.8948, 75.8087), ("Narayan Singh Circle", 26.8996, 75.8125), ("SMS Hospital", 26.9050, 75.8148), ("Ashok Marg", 26.9134, 75.8110),
       ("Govt Hostel", 26.9171, 75.8004), ("Collectorate", 26.9265, 75.7922), ("Subhash Nagar", 26.9345, 75.7940), ("Pani Pech", 26.9380, 75.7866), ("Ambabari", 26.93973, 75.7778)]
OW = [wp(la, lo) for _, la, lo in OST]
ORANGE = cat(OW, 16); OC = cum(ORANGE)
OS = [(nm, nearest_s(ORANGE, OC, w)[0], w) for (nm, _, _), w in zip(OST, OW)]
rd = json.load(open("roads.json"))
SK = sorted([p for p in rd["sikar"] if 26.9397 <= p[0] <= 26.985 and p[1] < 75.785], key=lambda p: p[0])
TODI = [OW[-1]] + [wp(*p) for p in SK[::6]]
# ---------- background roads (OSM city) ----------
import glob
BG = []
for f in glob.glob("/home/user/Infra360/video/jaipur-ajmer-road/project/osm/city_*.json"):
    for e in json.load(open(f)).get("elements", []):
        t = e.get("tags", {})
        if t.get("highway") in ("motorway", "trunk", "primary", "secondary") and e.get("geometry"):
            BG.append([wp(g["lat"], g["lon"]) for g in e["geometry"]][::2])

S, H, J, SFX = [], [], [], []
def sfx(name, t, vol=0.4): SFX.append(f'<audio class="clip" src="assets/sfx/{name}.mp3" data-start="{t:.2f}" data-duration="2" data-track-index="{20 + len(SFX)}" data-volume="{vol}"></audio>')
CAM = [(0.0, None, None)]
def cam(t, c, w, d=1.4, ease="power2.inOut"): J.append(f'tl.to("#world", {{attr:{{viewBox:"{vb(c, w)}"}}, duration:{d}, ease:"{ease}"}}, {t:.2f});')
def story(i, html, t, until):
    H.append(f'<div class="st" id="{i}">{html}</div>')
    J.append(f'tl.fromTo("#{i}", {{opacity:0, y:22, scale:.94}}, {{opacity:1, y:0, scale:1, duration:.26, ease:"back.out(2)"}}, {t:.2f}); tl.to("#{i}", {{opacity:0, y:-10, duration:.16}}, {until - .16:.2f});')
def chip(i, kick, text, t, until, y=250, col="#FF8A1F"):
    H.append(f'<div class="chip" id="{i}" style="top:{y}px;border-left-color:{col}"><b style="color:{col}">{kick}</b>{text}</div>')
    J.append(f'tl.fromTo("#{i}", {{opacity:0, x:-40}}, {{opacity:1, x:0, duration:.35, ease:"power3.out"}}, {t:.2f}); tl.to("#{i}", {{opacity:0, duration:.25}}, {until - .25:.2f});')
def photo(i, src, cap, credit, t, until, x=60, y=420, w=960, h=600, fit="cover"):
    H.append(f'<div class="ph" id="{i}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px"><img src="assets/img/{src}" style="object-fit:{fit}"/><div class="pc">{cap}<em>{credit}</em></div></div>')
    J.append(f'tl.fromTo("#{i}", {{opacity:0, scale:.7, rotation:-2}}, {{opacity:1, scale:1, rotation:0, duration:.45, ease:"back.out(1.6)"}}, {t:.2f}); tl.to("#{i}", {{opacity:0, scale:.92, duration:.3}}, {until - .3:.2f});')
    sfx("pop", t, .3)
Y, E = '<span class="y">', '</span>'; O_, E2 = '<span class="o">', '</span>'

# world layers
S.append('<image href="assets/img/sat12.jpg" x="-1024" y="-1792" width="4608" height="6656" preserveAspectRatio="none"/>')
S.append(f'<image href="assets/img/sat.jpg" x="0" y="0" width="2304" height="2560" preserveAspectRatio="none"/>')
S.append('<rect x="-3000" y="-3000" width="9000" height="9000" style="fill:#0b1220;opacity:.38"/>')
S.append('<g style="fill:none;stroke:#9fb3c8;stroke-opacity:.30;stroke-width:1.6;stroke-linejoin:round">' + "".join(f'<path d="{pd(p)}"/>' for p in BG) + '</g>')
S.append(f'<path id="pinkglow" pathLength="1" d="{pd(PINK)}" style="fill:none;stroke:#FF5FA2;stroke-opacity:.35;stroke-width:16;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1"/>')
S.append(f'<path id="pink" pathLength="1" d="{pd(PINK)}" style="fill:none;stroke:#FF5FA2;stroke-width:6;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1"/>')
S.append(f'<path id="orglow" pathLength="1" d="{pd(ORANGE)}" style="fill:none;stroke:#FF8A1F;stroke-opacity:.35;stroke-width:18;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1"/>')
S.append(f'<path id="orange" pathLength="1" d="{pd(ORANGE)}" style="fill:none;stroke:#FF8A1F;stroke-width:7;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1"/>')
S.append(f'<path id="todi" d="{pd(TODI)}" style="fill:none;stroke:#FF8A1F;stroke-width:5;stroke-dasharray:10 9;stroke-linecap:round;opacity:0"/>')
S.append(f'<path id="flow" pathLength="1" d="{pd(ORANGE)}" style="fill:none;stroke:#FFF1DC;stroke-width:5;stroke-linecap:round;stroke-dasharray:.06 .94;stroke-dashoffset:.06;opacity:0"/>')
for k, (nm, s, p) in enumerate(OS):
    S.append(f'<circle id="ring{k}" cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="58" style="fill:#FF8A1F;fill-opacity:.10;stroke:#FF8A1F;stroke-opacity:.5;stroke-width:1.5;opacity:0"/>')
DENSE = {"Choti Chaupar", "Chandpole", "Sindhi Camp", "Pani Pech", "New Aatish Market", "Railway Station"}
def stn(i, p, nm, col, side=1, fs=15):
    S.append(f'<g id="{i}" style="opacity:0"><circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="6.5" style="fill:#fff;stroke:{col};stroke-width:3.5"/>'
             f'<text class="{"dense" if nm in DENSE else ""}" x="{p[0] + side * 12:.1f}" y="{p[1] + 5:.1f}" text-anchor="{"start" if side > 0 else "end"}" style="font:800 {fs}px Inter,Arial,sans-serif;fill:#fff;paint-order:stroke;stroke:#05080d;stroke-width:4.5px">{nm}</text></g>')
PSIDE = {"Mansarovar": -1, "New Aatish Market": 1, "Vivek Vihar": 1, "Shyam Nagar": 1, "Ram Nagar": -1, "Civil Lines": -1, "Railway Station": -1, "Sindhi Camp": -1, "Chandpole": -1, "Choti Chaupar": 1, "Badi Chaupar": 1}
for k, (nm, s, p) in enumerate(PS): stn(f"ps{k}", p, nm, "#FF5FA2", PSIDE[nm])
OSIDE = {"Prahladpura": -1, "India Gate · Sitapura": 1, "Kumbha Marg": 1, "Haldighati Gate": 1, "Pinjrapole Gaushala": 1, "Sanganer": -1, "B2 Bypass": 1, "Durgapura": -1,
         "Mahaveer Nagar": 1, "Dev Nagar": -1, "Gandhi Nagar": 1, "Tonk Phatak": -1, "Rambagh Circle": 1, "Narayan Singh Circle": 1, "SMS Hospital": 1, "Ashok Marg": 1,
         "Govt Hostel": 1, "Collectorate": -1, "Subhash Nagar": 1, "Pani Pech": 1, "Ambabari": -1}
for k, (nm, s, p) in enumerate(OS): stn(f"os{k}", p, nm, "#FF8A1F", OSIDE[nm])
S.append(f'<text id="todil" x="{TODI[-1][0] + 12:.1f}" y="{TODI[-1][1]:.1f}" style="font:900 17px Inter,Arial,sans-serif;fill:#FFB36B;paint-order:stroke;stroke:#05080d;stroke-width:5px;opacity:0">→ Todi Mod</text>')
INT = wp(26.9225, 75.7975)
S.append(f'<circle id="xring" cx="{INT[0]:.1f}" cy="{INT[1]:.1f}" r="16" style="fill:none;stroke:#fff;stroke-width:3;opacity:0"/>')

allp = np.array(PINK + ORANGE + TODI); BB = (allp.min(0), allp.max(0))
CALL = (float((BB[0][0] + BB[1][0]) / 2), float((BB[0][1] + BB[1][1]) / 2)); WALL = float((BB[1][1] - BB[0][1]) * 1.18 * 1080 / 1920)
pa = np.array(PINK); PCEN = (float(pa[:, 0].mean()), float(pa[:, 1].mean()) + 25)

# ---------------- timeline ----------------
END = 58.5
# cover 0–0.55
J.append(f'tl.set("#world", {{attr:{{viewBox:"{vb(CALL, WALL * 1.25)}"}}}}, 0);')
# 0.6 · SAVE & SHARE + hook
H.append('<div id="ss"><span><svg viewBox="0 0 24 24" width="40" height="40"><path d="M6 3h12v18l-6-4-6 4z" style="fill:#FFE03A"/></svg>SAVE this map</span>'
         '<span><svg viewBox="0 0 24 24" width="40" height="40"><path d="M3 11l18-8-8 18-2-8z" style="fill:none;stroke:#fff;stroke-width:2.4;stroke-linejoin:round"/></svg>SHARE it</span></div>')
J.append('tl.fromTo("#ss", {opacity:0, y:-30}, {opacity:1, y:0, duration:.35, ease:"back.out(2)"}, 0.6); tl.to("#ss span", {scale:1.08, duration:.3, yoyo:true, repeat:3, stagger:.15}, 1.1); tl.to("#ss", {opacity:0, duration:.3}, 4.4);')
H.append('<div id="hook"><b><span id="crore">0</span></b><em>CRORE · 41 KM OF NEW METRO</em></div>')
J.append('tl.fromTo("#hook", {opacity:0, scale:1.2}, {opacity:1, scale:1, duration:.35, ease:"back.out(2)"}, 0.7); tl.to("#hook", {opacity:0, duration:.3}, 3.9);')
J.append('const cr={v:0}; tl.to(cr, {v:13037, duration:1.3, ease:"power2.out", onUpdate:()=>{document.getElementById("crore").textContent="₹"+Math.round(cr.v).toLocaleString("en-IN")}}, 0.8);')
J.append('tl.to(["#orange","#orglow"], {strokeDashoffset:0, duration:2.2, ease:"power2.inOut"}, 0.9); tl.to(["#orange","#orglow"], {opacity:0, duration:.4}, 3.7); tl.set(["#orange","#orglow"], {strokeDashoffset:1}, 4.2); tl.set(["#orange","#orglow"], {opacity:1}, 4.3);')
story("s0", f"Is the new metro coming {Y}near YOU?{E}", 1.2, 3.9)
sfx("impact-bass-1", 0.7, .5); sfx("riser", 0.9, .3)
cam(0.6, CALL, WALL, 3.0, "power2.out")

# 3.9 · Phase 1 Pink Line
cam(3.8, PCEN, 760, 1.6)
J.append('tl.to(["#pink","#pinkglow"], {strokeDashoffset:0, duration:3.6, ease:"none"}, 4.3);')
for k, (nm, s, p) in enumerate(PS):
    t = 4.3 + 3.6 * s / PC[-1]; J.append(f'tl.fromTo("#ps{k}", {{opacity:0, scale:.4, transformOrigin:"{p[0]:.1f}px {p[1]:.1f}px"}}, {{opacity:1, scale:1, duration:.25, ease:"back.out(3)"}}, {t:.2f});'); sfx("click-soft", t, .25)
chip("c1", "PHASE 1 · PINK LINE", "Mansarovar → Badi Chaupar · 11 stations · ~12 km", 4.2, 11.4, col="#FF5FA2")
story("s1", f"Today, Jaipur has {Y}ONE{E} metro line.", 4.0, 7.2)
story("s2", f"Opened {Y}2015{E} · extended underground {Y}2020{E}", 7.2, 11.4)
photo("ptrain", "train.jpg", "Pink Line today", "Image supplied", 8.2, 11.3, x=60, y=420, w=960, h=520)

# 11.4 · approval
J.append('tl.to("[id^=ps] text", {opacity:0, duration:.3}, 11.3);')
cam(11.3, CALL, WALL, 1.6)
photo("pdd", "ddnews.jpg", "8 April 2026", "DD News · screenshot supplied", 11.6, 15.2, x=150, y=330, w=780, h=870, fit="contain")
story("s3", f"Then, April 2026: {O_}Phase 2 approved.{E2}", 11.6, 15.2)
sfx("whoosh", 11.4, .35)

# 15.2 · Orange Line forms, camera follows the head north
T0, T1 = 15.6, 31.6
J.append(f'tl.to(["#orange","#orglow"], {{strokeDashoffset:0, duration:{T1 - T0}, ease:"none"}}, {T0});')
W = 720
def head(t): s = (t - T0) / (T1 - T0) * OC[-1]; i = min(range(len(ORANGE)), key=lambda k: abs(OC[k] - s)); return ORANGE[i]
cam(15.0, (head(T0)[0], head(T0)[1] + 150), W, 0.8)
tt = T0
while tt < T1 - 0.01:
    t2 = min(T1, tt + 1.0); h = head(min(T1, t2 + 0.5)); J.append(f'tl.to("#world", {{attr:{{viewBox:"{vb((h[0], h[1] + 150), W)}"}}, duration:{t2 - tt:.2f}, ease:"none"}}, {tt:.2f});'); tt = t2
for k, (nm, s, p) in enumerate(OS):
    t = T0 + (T1 - T0) * s / OC[-1]
    J.append(f'tl.fromTo("#os{k}", {{opacity:0, scale:.4, transformOrigin:"{p[0]:.1f}px {p[1]:.1f}px"}}, {{opacity:1, scale:1, duration:.25, ease:"back.out(3)"}}, {t:.2f});'); sfx("click-soft", t, .25)
J.append(f'tl.to("#todi", {{opacity:1, duration:.5}}, {T1:.2f}); tl.to("#todil", {{opacity:1, duration:.4}}, {T1 + .3:.2f});')
def at(nm): return T0 + (T1 - T0) * [s for n, s, p in OS if n == nm][0] / OC[-1]
chip("c2", "PHASE 2 · ORANGE LINE", "Prahladpura → Todi Mod · 41 km · ~36 stations", 15.2, 19.6)
story("s4", f"It starts at {O_}Prahladpura{E2}, Sitapura", 15.4, 17.6)
chip("c3", "FIRST STRETCH", "Prahladpura → Pinjrapole Gaushala · ~12 km · 10 stations", 19.6, at("B2 Bypass"))
story("s5", f"Then straight up {O_}Tonk Road{E2}", 17.6, at("B2 Bypass") - 0.6)
story("s6", f"Past the {Y}airport{E}", at("B2 Bypass") - 0.6, at("Gandhi Nagar"))
photo("pair", "airport.jpg", "Jaipur International Airport", "Image supplied", at("Sanganer"), at("Mahaveer Nagar"), x=440, y=250, w=580, h=380)
story("s7", f"Gandhi Nagar · Tonk Phatak · {Y}Rambagh{E}", at("Gandhi Nagar"), at("SMS Hospital") - 0.2)
photo("pram", "rambagh.jpg", "Rambagh Palace · by Rambagh Circle", "Image supplied", at("Rambagh Circle") - 0.3, at("SMS Hospital") - 0.25, x=440, y=250, w=580, h=330)
story("s8", f"{Y}SMS Hospital{E}", at("SMS Hospital") - 0.2, at("Govt Hostel"))
photo("psms", "sms.jpg", "SMS Hospital", "Image supplied", at("SMS Hospital") - 0.2, at("Govt Hostel") + 0.4, x=500, y=250, w=520, h=340)
J.append(f'tl.fromTo("#xring", {{opacity:0, attr:{{r:10}}}}, {{opacity:1, attr:{{r:26}}, duration:.5, yoyo:true, repeat:5}}, {at("Govt Hostel"):.2f}); tl.to("#pink", {{opacity:1, duration:.2}}, {at("Govt Hostel"):.2f});')
story("s9", f"Meets the {Y}Pink Line{E} downtown", at("Govt Hostel"), at("Subhash Nagar"))
story("s10", f"Then up {O_}Sikar Road{E2} → Todi Mod", at("Subhash Nagar"), 33.4)
H.append('<div id="indic">Phase 2 route &amp; stations: indicative, based on published route maps · key stations shown</div>')
J.append(f'tl.fromTo("#indic", {{opacity:0}}, {{opacity:1, duration:.4}}, 15.4); tl.to("#indic", {{opacity:0, duration:.4}}, 52.5);')

# 33.4 · zoom out, the big picture
cam(31.8, CALL, WALL, 1.8)
J.append('tl.to("[id^=os] text, [id^=ps] text", {opacity:0, duration:.3}, 31.8);')
J.append('tl.to("#orange", {strokeWidth:12, duration:1.2}, 31.9); tl.to("#pink", {strokeWidth:11, duration:1.2}, 31.9);')
J.append('tl.set("#flow", {opacity:1}, 33.0); tl.fromTo("#flow", {strokeDashoffset:.06}, {strokeDashoffset:-.94, duration:2.4, ease:"none", repeat:1}, 33.0); tl.to("#flow", {opacity:0, duration:.3}, 37.6);')
H.append('<div id="stats"><div><b>41</b><i>km</i></div><div><b>~36</b><i>stations</i></div><div><b>₹13,037</b><i>crore</i></div><div><b>~2031</b><i>target</i></div></div>')
J.append('tl.fromTo("#stats", {opacity:0, y:-20}, {opacity:1, y:0, duration:.35}, 33.3); tl.from("#stats div", {scale:.5, opacity:0, duration:.35, stagger:.18, ease:"back.out(2)"}, 33.4); tl.to("#stats", {opacity:0, duration:.3}, 38.5);')
story("s11", f"North ↔ South. {O_}Sitapura to Sikar Road.{E2}", 33.4, 36.0)
story("s12", f"Target: around {Y}2031{E}", 36.0, 38.6)
photo("pcon", "construction.jpg", "Metro piling work", "Image supplied", 36.0, 38.6, x=560, y=560, w=440, h=580)

# 38.6 · why it matters: walking-distance rings
for k in range(len(OS)): J.append(f'tl.fromTo("#ring{k}", {{opacity:0, attr:{{r:10}}}}, {{opacity:1, attr:{{r:58}}, duration:.5, ease:"back.out(1.6)"}}, {38.7 + 0.05 * k:.2f});')
cam(38.6, (CALL[0], CALL[1] + 60), WALL * 0.85, 1.4)
chip("w0", "WHY IT MATTERS", "Rings ≈ 1 km walk from each station", 38.8, 47.5, y=250, col="#FFE03A")
story("s13", f"Homes near a station {Y}usually see more demand.{E}", 38.8, 42.2)
story("s14", f"But {Y}'near metro'{E} in ads can mean 3 km.", 42.2, 44.8)
story("s15", f"Check the {Y}actual station{E}. Timelines can slip.", 44.8, 47.6)
sfx("whoosh-short", 38.6, .3)

# 47.6 · save moment: all stations labelled
cam(47.4, (CALL[0] + 120, CALL[1] - 40), WALL * 1.14, 1.0)
for k in range(len(OS)): J.append(f'tl.to("#ring{k}", {{opacity:.35, duration:.3}}, 47.4);')
J.append('tl.to("[id^=os] text:not(.dense), [id^=ps] text:not(.dense)", {opacity:1, duration:.4}, 47.8);')
H.append('<div id="save"><svg viewBox="0 0 24 24" width="64" height="64"><path d="M6 3h12v18l-6-4-6 4z" style="fill:#FFE03A"/></svg><b>SAVE THIS MAP</b><i>you will need it</i></div>')
J.append('tl.fromTo("#save", {opacity:0, scale:.6}, {opacity:1, scale:1, duration:.4, ease:"back.out(2)"}, 47.7); tl.to("#save svg", {scale:1.2, duration:.35, yoyo:true, repeat:5}, 48.2); tl.to("#save", {opacity:0, duration:.3}, 52.6);')
story("s16", f"Find your {O_}nearest station{E2} 👆", 47.8, 52.6)
sfx("sparkle", 47.7, .35)

# 52.6 · CTA
S.append('<rect id="ctadim" x="-3000" y="-3000" width="9000" height="9000" style="fill:#05080d;opacity:0"/>')
J.append('tl.to("#ctadim", {opacity:.55, duration:.5}, 52.5);')
story("s17", f"Comment your area — {Y}I'll tell you your station.{E}", 52.6, END + .2)
H.append('<div id="share"><svg viewBox="0 0 24 24" width="84" height="84"><path d="M3 11l18-8-8 18-2-8z" style="fill:none;stroke:#fff;stroke-width:2;stroke-linejoin:round"/></svg><span>Send to someone on Tonk Road or Sikar Road</span></div>')
J.append('tl.fromTo("#share", {opacity:0, scale:.6}, {opacity:1, scale:1, duration:.4, ease:"back.out(2)"}, 52.8); tl.fromTo("#share svg", {scale:1}, {scale:1.18, duration:.45, yoyo:true, repeat:5}, 53.3);')
H.append('<div id="brand">ASHWILLPOWER · JAIPUR REAL ESTATE</div>'); J.append('tl.to("#brand", {opacity:0, duration:.3}, 15.0);')
H.append('<div id="credit">Satellite: Sentinel-2 cloudless 2016 by EOX (CC BY 4.0) · Map data © OpenStreetMap contributors</div>')

# ---------------- cover (Ajmer-road style) ----------------
cb = np.array(PINK + ORANGE + TODI); x0, y0 = cb.min(0); x1, y1 = cb.max(0)
CS = min(560 / (x1 - x0), 760 / (y1 - y0)); CX, CY = 600 - (x1 - x0) * CS / 2 + 150, 720
def cp(p): return (CX + (p[0] - x0) * CS, CY + (p[1] - y0) * CS)
def cpd(pl): return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in map(cp, pl))
csvg = "".join(f'<path d="{cpd(p)}" style="fill:none;stroke:rgba(243,231,211,.10);stroke-width:1.5"/>' for p in BG[::2])
csvg += f'<path d="{cpd(PINK)}" style="fill:none;stroke:#FF5FA2;stroke-width:9;stroke-linecap:round;filter:url(#cg)"/>'
csvg += f'<path d="{cpd(ORANGE)}" style="fill:none;stroke:#FF8A1F;stroke-width:11;stroke-linecap:round;filter:url(#cg)"/>'
csvg += f'<path d="{cpd(TODI)}" style="fill:none;stroke:#FF8A1F;stroke-width:7;stroke-dasharray:12 10;stroke-linecap:round"/>'
tags = ""
for nm, side, dy in [("Prahladpura", -1, 0), ("Ambabari", -1, -40), ("Mansarovar", -1, 10), ("Badi Chaupar", 1, -20), ("SMS Hospital", 1, 0), ("B2 Bypass", 1, 0)]:
    p = dict((n, q) for n, s, q in OS + PS)[nm]; X, Yy = cp(p); csvg += f'<circle cx="{X:.1f}" cy="{Yy:.1f}" r="7" style="fill:#fff"/>'
    tags += f'<div class="cvtag" style="{"left" if side > 0 else "right"}:{(X + 16) if side > 0 else (1080 - X + 16):.0f}px;top:{Yy - 24 + dy:.0f}px">{nm.upper()}</div>'
H2 = ['<div id="cover"><svg width="1080" height="1920" style="position:absolute;inset:0"><defs><pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="rgba(243,231,211,.07)"/></pattern>'
      '<filter id="cg" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
      f'<rect width="1080" height="1920" fill="url(#dots)"/>{csvg}</svg>'
      '<div id="cvt">JAIPUR<br/><span>METRO 2.0</span></div><div id="cvs">Is it coming<br/>near you?</div>'
      f'{tags}<div id="cvpill">₹13,037 cr · 41 km · ~36 stations</div></div>']
J.append('tl.set("#cover", {opacity:1}, 0); tl.to("#cover", {opacity:0, duration:.25}, 0.55);')

CSS = """*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#070b12}
#root{position:relative;width:1080px;height:1920px;overflow:hidden}#world{position:absolute;inset:0;width:1080px;height:1920px}
.y{color:#FFE03A}.o{color:#FF9B3D}
.st{position:absolute;left:50px;right:50px;top:1330px;text-align:center;opacity:0;font:900 70px/1.08 Inter,Arial,sans-serif;color:#fff;text-shadow:0 4px 0 #000,0 0 20px rgba(0,0,0,.95),0 0 4px #000}
#hook{position:absolute;left:0;right:0;top:470px;text-align:center;opacity:0;font-family:Inter,Arial,sans-serif;text-shadow:0 6px 0 #000,0 0 30px rgba(0,0,0,.9)}
#hook b{display:block;font-weight:900;font-size:170px;line-height:1;color:#FF9B3D;letter-spacing:-.02em}#hook em{display:block;margin-top:14px;font-style:normal;font:800 44px Inter,Arial,sans-serif;color:#fff;letter-spacing:.04em}
#ss{position:absolute;left:0;right:0;top:250px;display:flex;justify-content:center;gap:22px;opacity:0}
#ss span{display:flex;align-items:center;gap:12px;padding:14px 24px;border-radius:40px;background:rgba(8,12,20,.85);border:2px solid rgba(255,255,255,.25);font:900 36px Inter,Arial,sans-serif;color:#fff}
.chip{position:absolute;left:60px;right:60px;opacity:0;padding:20px 28px;border-radius:20px;background:rgba(8,12,20,.88);border-left:10px solid #FF8A1F;font:800 40px/1.15 Inter,Arial,sans-serif;color:#fff}
.chip b{display:block;font:700 26px "JetBrains Mono",monospace;letter-spacing:.16em;margin-bottom:6px}
.ph{position:absolute;opacity:0;border-radius:22px;overflow:hidden;border:5px solid #FF8A1F;box-shadow:0 18px 50px rgba(0,0,0,.7);background:#111}
.ph img{width:100%;height:100%;display:block}.pc{position:absolute;left:0;right:0;bottom:0;padding:40px 20px 12px;background:linear-gradient(180deg,transparent,rgba(0,0,0,.88));font:900 40px Inter,Arial,sans-serif;color:#fff}
.pc em{display:block;font-style:normal;font-weight:600;font-size:22px;color:#ddd;margin-top:4px}
#stats{position:absolute;left:50px;right:50px;top:250px;display:grid;grid-template-columns:repeat(4,1fr);gap:14px;opacity:0}
#stats div{padding:18px 8px;border-radius:18px;background:rgba(8,12,20,.88);border:2px solid #FF8A1F;text-align:center;font-family:Inter,Arial,sans-serif}
#stats b{display:block;font-weight:900;font-size:50px;color:#FF9B3D}#stats i{display:block;font-style:normal;font:700 22px "JetBrains Mono",monospace;letter-spacing:.12em;color:#fff;text-transform:uppercase}
#save{position:absolute;right:50px;top:860px;display:flex;flex-direction:column;align-items:flex-end;text-align:right;gap:6px;opacity:0;font-family:Inter,Arial,sans-serif;text-shadow:0 4px 0 #000}
#save b{font-weight:900;font-size:64px;line-height:1;color:#FFE03A}#save i{font-style:normal;font-weight:800;font-size:36px;color:#fff}
#indic{position:absolute;left:40px;right:40px;top:200px;text-align:center;opacity:0;font:600 22px "JetBrains Mono",monospace;color:rgba(255,255,255,.75);text-shadow:0 1px 4px #000}
#share{position:absolute;left:0;right:0;top:1060px;display:flex;flex-direction:column;align-items:center;gap:12px;opacity:0;font:900 40px Inter,Arial,sans-serif;color:#fff;text-shadow:0 3px 0 #000;white-space:nowrap}
#share svg{background:#FF8A1F;border-radius:50%;padding:16px;box-shadow:0 0 0 12px rgba(255,138,31,.3)}
#brand{position:absolute;left:0;right:0;top:150px;text-align:center;font:700 24px "JetBrains Mono",monospace;letter-spacing:.2em;color:rgba(255,255,255,.85);text-shadow:0 2px 6px #000}
#credit{position:absolute;left:40px;right:40px;bottom:90px;text-align:center;font:500 19px "JetBrains Mono",monospace;color:rgba(255,255,255,.65);text-shadow:0 1px 3px #000}
#cover{position:absolute;inset:0;opacity:0;overflow:hidden;background:radial-gradient(120% 80% at 70% 40%,#2B2016 0%,#1B140F 55%,#120d09 100%)}
#cvt{position:absolute;left:70px;right:70px;top:230px;font:900 150px/0.92 Inter,sans-serif;letter-spacing:-0.01em;color:#F3E7D3;text-shadow:0 8px 40px rgba(0,0,0,.6)}#cvt span{color:#FF9B3D}
#cvs{position:absolute;left:76px;top:560px;font:800 52px/1.1 Inter,sans-serif;color:#F3E7D3}
.cvtag{position:absolute;padding:8px 16px;border-radius:12px;background:rgba(40,26,12,.92);border:2px solid #E3A23B;font:800 28px Inter,sans-serif;color:#F3E7D3;white-space:nowrap}
#cvpill{position:absolute;left:76px;top:1560px;padding:12px 22px;border-radius:14px;background:rgba(60,38,14,.92);border:2px solid #E3A23B;font:800 40px Inter,sans-serif;color:#F3E7D3}"""
FONTS = '@font-face{font-family:"Instrument Serif";src:url(assets/fonts/instrument-serif-latin-400-normal.woff2)}'
open(f"{P}/index.html", "w").write(f"""<!doctype html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script><style>{FONTS}{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="30">
<svg id="world" viewBox="{vb(CALL, WALL * 1.25)}" preserveAspectRatio="xMidYMid slice">{"".join(S)}</svg>
{"".join(H)}{"".join(H2)}
<audio id="music" class="clip" src="assets/music_tune.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.8" data-fade-in="0.3" data-fade-out="2.5"></audio>
{"".join(SFX)}
</div><script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(J)}
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>""")
print("END", END, "pink pts", len(PINK), "pink len", round(PC[-1]), "orange len", round(OC[-1]), "stations", len(PS), len(OS))
