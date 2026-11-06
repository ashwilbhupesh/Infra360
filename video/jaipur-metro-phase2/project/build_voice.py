"""Jaipur Metro reel (text-led): dark satellite map, Pink Line (OSM) + Phase-2 Orange Line (indicative, via Tonk Rd / Sikar Rd) drawing on with stations."""
import json, math, os
import numpy as np
P = "projv"; Z = 13; OXT, OYT = 5816, 3455
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

# rebuild Pink Line as a clean ordered path through its stations (OSM way chain is fragmented)
PORDER = ["Mansarovar", "New Aatish Market", "Vivek Vihar", "Shyam Nagar", "Ram Nagar", "Civil Lines", "Railway Station", "Sindhi Camp", "Chandpole", "Choti Chaupar", "Badi Chaupar"]
PP = {n: p for n, sv, p in PS}
PINK = cat([PP[n] for n in PORDER], 14); PC = cum(PINK)
PS = [(n, nearest_s(PINK, PC, PP[n])[0], PP[n]) for n in PORDER]
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
    H.append(f'<div class="st" id="{i}"><span class="bx">{html}</span></div>')
    J.append(f'tl.fromTo("#{i}", {{opacity:0, y:22, scale:.94}}, {{opacity:1, y:0, scale:1, duration:.26, ease:"back.out(2)"}}, {t:.2f}); tl.to("#{i}", {{opacity:0, y:-10, duration:.16}}, {until - .16:.2f});')
def chip(i, kick, text, t, until, y=250, col="#FF8A1F"):
    H.append(f'<div class="chip" id="{i}" style="top:{y}px;border-left-color:{col}"><b style="color:{col}">{kick}</b>{text}</div>')
    J.append(f'tl.fromTo("#{i}", {{opacity:0, x:-40}}, {{opacity:1, x:0, duration:.35, ease:"power3.out"}}, {t:.2f}); tl.to("#{i}", {{opacity:0, duration:.25}}, {until - .25:.2f});')
def photo(i, src, cap, credit, t, until, x=60, y=420, w=960, h=600, fit="cover"):
    H.append(f'<div class="ph" id="{i}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px"><img src="assets/img/{src}" style="object-fit:{fit}"/><div class="pc">{cap}<em>{credit}</em></div></div>')
    J.append(f'tl.fromTo("#{i}", {{opacity:0, y:14}}, {{opacity:.96, y:0, duration:.5, ease:"power2.out"}}, {t:.2f}); tl.to("#{i}", {{opacity:0, duration:.35}}, {until - .35:.2f});')
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

# ---------------- timeline (synced to Ashwil's Hinglish voice) ----------------
END = 53.6
def scap(i, html, t, until, top=1330): story(i, html, t, until); J.append(f'tl.set("#{i}", {{top:{top}}}, 0);')
# ---- 0 · hook: 1 km ring around a station, then 36 pins rain over Jaipur
GN = [p for n, s, p in OS if n == "Gandhi Nagar"][0]
J.append(f'tl.set("#world", {{attr:{{viewBox:"{vb(GN, 420)}"}}}}, 0);')
S.append(f'<g id="hpin" style="opacity:0"><circle id="hring" cx="{GN[0]:.1f}" cy="{GN[1]:.1f}" r="59" style="fill:#FF8A1F;fill-opacity:.18;stroke:#FFB36B;stroke-width:3;stroke-dasharray:8 6"/>'
         f'<path d="M{GN[0]:.1f} {GN[1]:.1f} l-14 -30 a16 16 0 1 1 28 0 z" style="fill:#FF2D55;stroke:#fff;stroke-width:3"/>'
         f'<text x="{GN[0] + 64:.1f}" y="{GN[1] + 6:.1f}" style="font:900 22px Inter;fill:#fff;paint-order:stroke;stroke:#000;stroke-width:5px">1 km</text></g>')
J.append('tl.fromTo("#hpin", {opacity:0, y:-120}, {opacity:1, y:0, duration:.5, ease:"bounce.out"}, 0.5);')
J.append(f'tl.fromTo("#hring", {{attr:{{r:4}}}}, {{attr:{{r:59}}, duration:1.0, ease:"power2.out"}}, 0.9);')
J.append(f'tl.to("#hring", {{fillOpacity:.32, duration:.5, yoyo:true, repeat:5}}, 2.0); tl.to("#hpin", {{opacity:0, duration:.3}}, 5.3);')
for k, (nm, sv, p) in enumerate(OS):
    S.append(f'<g id="rp{k}" style="opacity:0"><path d="M{p[0]:.1f} {p[1]:.1f} l-9 -20 a11 11 0 1 1 18 0 z" style="fill:#FF8A1F;stroke:#fff;stroke-width:2.5"/></g>')
    J.append(f'tl.fromTo("#rp{k}", {{opacity:0, y:-160}}, {{opacity:1, y:0, duration:.45, ease:"bounce.out"}}, {6.1 + .07 * k:.2f}); tl.to("#rp{k}", {{opacity:0, duration:.3}}, 8.6);')
    if k % 3 == 0: sfx("pop", 6.1 + .07 * k, .18)
cam(5.3, CALL, WALL, 1.2, "power2.inOut")
H.append('<div id="ss"><span><svg viewBox="0 0 24 24" width="40" height="40"><path d="M6 3h12v18l-6-4-6 4z" style="fill:#FFE03A"/></svg>SAVE this map</span>'
         '<span><svg viewBox="0 0 24 24" width="40" height="40"><path d="M3 11l18-8-8 18-2-8z" style="fill:none;stroke:#fff;stroke-width:2.4;stroke-linejoin:round"/></svg>SHARE it</span></div>')
J.append('tl.fromTo("#ss", {opacity:0, y:-30}, {opacity:1, y:0, duration:.35, ease:"back.out(2)"}, 0.3); tl.to("#ss span", {scale:1.08, duration:.3, yoyo:true, repeat:3, stagger:.15}, 0.7); tl.to("#ss", {opacity:0, duration:.3}, 5.2);')
scap("h0", f"Metro station ke {Y}1 km ke andar{E} ki zameen", 0.6, 3.0)
scap("h1", f"aksar {Y}sabse pehle mehngi{E} hoti hai", 3.0, 5.3)
scap("h2", f"Jaipur mein {O_}36 naye stations{E2} aa rahe hain", 5.36, 7.6)
scap("h3", f"Dekhiye {Y}kahan{E}", 7.6, 8.75)
sfx("impact-bass-1", 0.5, .35); sfx("whoosh", 5.3, .3)
# ---- 8.75 · India map: Jaipur, 6th city with a metro
def ip(lat, lon, GX=40, GY=300, GW=1000): return (GX + (lon - 67.0) / 32.0 * GW, GY + (37.5 - lat) / 32.5 * 1293 * GW / 1200)
CITIES = [("Kolkata", 22.57, 88.36, "1984", 1), ("Delhi", 28.61, 77.21, "2002", 1), ("Bengaluru", 12.97, 77.59, "2011", 1), ("Gurugram", 28.46, 77.03, "2013", -1), ("Mumbai", 19.08, 72.88, "2014", 1), ("Jaipur", 26.92, 75.82, "2015", 1)]
ih = '<div id="india"><img src="assets/img/indiamap.png" style="position:absolute;left:40px;top:300px;width:1000px;opacity:.95"/>'
for k, (n, la, lo, yr, sd) in enumerate(CITIES):
    x, y = ip(la, lo); dy = -46 if n == "Gurugram" else (6 if n == "Delhi" else (14 if n == "Jaipur" else -20))
    ih += (f'<div class="ic{" jp" if n == "Jaipur" else ""}" id="ic{k}" style="left:{x:.0f}px;top:{y:.0f}px"><i></i>'
           f'<b style="{"left" if sd > 0 else "right"}:22px;top:{dy}px">{k + 1}. {n} <span>{yr}</span></b></div>')
ih += '<div id="inote">India map: Milenioscuro, CC BY 4.0 · Gurugram = Rapid Metro</div></div>'
H.append(ih)
J.append('tl.fromTo("#india", {opacity:0, scale:1.15}, {opacity:1, scale:1, duration:.5, ease:"power2.out"}, 8.7); tl.to("#india", {opacity:0, duration:.4}, 13.7);')
for k in range(6):
    t = 9.0 + .38 * k if k < 5 else 11.0
    J.append(f'tl.fromTo("#ic{k}", {{opacity:0, scale:.3}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(3)"}}, {t:.2f});'); sfx("click-soft" if k < 5 else "ping", t, .25)
J.append('tl.to("#ic5 i", {scale:1.6, duration:.35, yoyo:true, repeat:5}, 11.3);')
chip("c15", "3 JUNE 2015", "Jaipur Metro opens · Mansarovar → Chandpole", 11.6, 13.8, y=250, col="#FF5FA2")
scap("i0", f"Waise, Jaipur desh ka {Y}6th shehar{E} tha", 8.8, 11.4)
scap("i1", f"jahan metro chali — {Y}3 June 2015{E}", 11.4, 13.9)
# ---- 13.9 · Pink Line: Mansarovar -> Chandpole (2015) -> underground to Badi Chaupar (2020)
cam(13.5, PCEN, 760, 0.9)
sC = [s for n, s, p in PS if n == "Chandpole"][0]
J.append(f'tl.to(["#pink","#pinkglow"], {{strokeDashoffset:{1 - sC / PC[-1]:.4f}, duration:1.6, ease:"none"}}, 13.96);')
J.append(f'tl.to(["#pink","#pinkglow"], {{strokeDashoffset:0, duration:2.3, ease:"none"}}, 15.65);')
def ptime(sv): return 13.96 + 1.6 * sv / sC if sv <= sC else 15.65 + 2.3 * (sv - sC) / (PC[-1] - sC)
for k, (nm, sv, p) in enumerate(PS):
    t = ptime(sv); J.append(f'tl.fromTo("#ps{k}", {{opacity:0, scale:.4, transformOrigin:"{p[0]:.1f}px {p[1]:.1f}px"}}, {{opacity:1, scale:1, duration:.25, ease:"back.out(3)"}}, {t:.2f});'); sfx("click-soft", t, .2)
J.append('tl.set(["#pink","#pinkglow"], {strokeDasharray:"1"}, 0); tl.to("#pink", {strokeDasharray:".012 .008", duration:.01}, 15.65); tl.to("#pink", {strokeDasharray:"1", duration:.01}, 18.0);')
chip("c20", "2020 · UNDERGROUND", "Below the walled city → Choti &amp; Badi Chaupar", 15.65, 19.6, y=250, col="#FF5FA2")
scap("p0", f"{Y}Mansarovar{E} se {Y}Chandpole{E}", 13.96, 15.6)
scap("p1", f"2020 mein walled city ke {Y}neeche se — underground{E}", 15.6, 18.6)
scap("p2", f"{Y}Badi Chaupar{E} tak", 18.6, 19.9)
scap("p3", f"Aaj bhi — {Y}sirf ek line{E}", 19.9, 21.8)
J.append('tl.to("#pinkglow", {strokeOpacity:.8, strokeWidth:24, duration:.4, yoyo:true, repeat:3}, 20.0);')
photo("ptrain", "train.jpg", "Pink Line today", "Image supplied", 19.9, 21.8, x=690, y=1000, w=340, h=200)
# ---- 21.8 · Phase 2 approved
J.append('tl.to("[id^=ps] text", {opacity:0, duration:.3}, 21.7);')
cam(21.7, CALL, WALL, 1.4)
photo("pdd", "ddnews.jpg", "8 April 2026", "DD News · screenshot supplied", 21.9, 26.4, x=700, y=420, w=330, h=370)
chip("cfig", "PHASE 2 · ORANGE LINE", "Approved April 2026 · ₹13,037 crore · 41 km", 21.9, 26.6, y=250, col="#FF8A1F")
scap("o0", f"Ab aa rahi hai {O_}Metro Phase 2{E2}", 21.8, 23.85)
scap("o1", f"{O_}Orange Line{E2} — {Y}41 kilometre{E}", 23.85, 26.9)
sfx("whoosh", 21.8, .3)
# ---- 26.9 · Orange Line, keyed to the spoken names (south -> north)
KEYS = [(27.0, "Prahladpura"), (28.37, "India Gate · Sitapura"), (29.33, "Sanganer"), (30.05, "Durgapura"), (31.01, "Gandhi Nagar"), (32.05, "Rambagh Circle"),
        (32.93, "SMS Hospital"), (34.05, "Govt Hostel"), (35.73, "Pani Pech"), (36.6, "Ambabari")]
SN = {n: sv for n, sv, p in OS}
KT = [t for t, n in KEYS]; KS = [SN[n] for t, n in KEYS]
def s_at(t):
    if t <= KT[0]: return KS[0]
    for (t0, s0), (t1, s1) in zip(zip(KT, KS), zip(KT[1:], KS[1:])):
        if t <= t1: return s0 + (s1 - s0) * (t - t0) / (t1 - t0)
    return KS[-1]
def t_at(sv):
    for (t0, s0), (t1, s1) in zip(zip(KT, KS), zip(KT[1:], KS[1:])):
        if sv <= s1: return t0 + (t1 - t0) * (sv - s0) / max(1e-6, s1 - s0)
    return KT[-1]
def head(t): sv = s_at(t); i = min(range(len(ORANGE)), key=lambda k: abs(OC[k] - sv)); return ORANGE[i]
J.append(f'tl.set(["#orange","#orglow"], {{strokeDashoffset:1}}, 0);')
J.append(f'tl.to(["#orange","#orglow"], {{strokeDashoffset:{1 - KS[0] / OC[-1]:.4f}, duration:.4}}, 26.6);')
for (t0, s0), (t1, s1) in zip(zip(KT, KS), zip(KT[1:], KS[1:])):
    J.append(f'tl.to(["#orange","#orglow"], {{strokeDashoffset:{1 - s1 / OC[-1]:.4f}, duration:{t1 - t0:.2f}, ease:"none"}}, {t0:.2f});')
J.append(f'tl.to(["#orange","#orglow"], {{strokeDashoffset:0, duration:.4}}, {KT[-1]:.2f});')
W = 720
hh = head(26.6); cam(26.0, (hh[0], hh[1] + 150), W, 0.9)
tt = 26.9
while tt < 37.0:
    t2 = min(37.0, tt + .5); h = head(min(37.0, t2 + .4)); J.append(f'tl.to("#world", {{attr:{{viewBox:"{vb((h[0], h[1] + 150), W)}"}}, duration:{t2 - tt:.2f}, ease:"none"}}, {tt:.2f});'); tt = t2
for k, (nm, sv, p) in enumerate(OS):
    t = t_at(sv) - .05
    J.append(f'tl.fromTo("#os{k}", {{opacity:0, scale:.4, transformOrigin:"{p[0]:.1f}px {p[1]:.1f}px"}}, {{opacity:1, scale:1, duration:.25, ease:"back.out(3)"}}, {t:.2f});'); sfx("click-soft", t, .2)
J.append('tl.to("#todi", {opacity:1, duration:.5}, 36.8); tl.to("#todil", {opacity:1, duration:.4}, 37.1);')
J.append('tl.to("[id^=ps] text", {opacity:1, duration:.3}, 33.6); tl.to("[id^=ps] text", {opacity:0, duration:.3}, 35.6);')
J.append(f'tl.fromTo("#xring", {{opacity:0, attr:{{r:10}}}}, {{opacity:1, attr:{{r:26}}, duration:.45, yoyo:true, repeat:5}}, 34.0);')
scap("r0", f"{O_}Prahladpura{E2} se shuru…", 26.9, 28.3)
scap("r1", f"{O_}Tonk Road{E2}… {Y}Airport{E}…", 28.3, 30.0)
scap("r2", f"{O_}Durgapura{E2}… {O_}Gandhi Nagar{E2}…", 30.0, 32.0)
scap("r3", f"{O_}Rambagh{E2}… {Y}SMS Hospital{E}…", 32.0, 34.0)
scap("r4", f"{Y}Pink Line{E} se milti hai…", 34.0, 35.7)
scap("r5", f"aur {O_}Sikar Road{E2} pe {O_}Todi Mod{E2} tak", 35.7, 37.8)
photo("pair", "airport.jpg", "Jaipur International Airport", "Image supplied", 29.2, 30.9, x=50, y=420, w=330, h=215)
photo("pram", "rambagh.jpg", "Rambagh Palace · by Rambagh Circle", "Image supplied", 31.95, 32.95, x=50, y=420, w=330, h=215)
photo("psms", "sms.jpg", "SMS Hospital", "Image supplied", 32.85, 34.0, x=50, y=420, w=330, h=215)
H.append('<div id="indic">Phase 2 route &amp; stations: indicative, based on published route maps · key stations shown</div>')
J.append('tl.fromTo("#indic", {opacity:0}, {opacity:1, duration:.4}, 26.9); tl.to("#indic", {opacity:0, duration:.4}, 47.4);')
# ---- 37.8 · the warning: 1 km vs "near metro" 3 km
cam(37.6, (CALL[0], CALL[1] + 60), WALL * 0.85, 1.4)
J.append('tl.to("[id^=os] text, [id^=ps] text", {opacity:0, duration:.3}, 37.6);')
for k in range(len(OS)): J.append(f'tl.fromTo("#ring{k}", {{opacity:0, attr:{{r:10}}}}, {{opacity:1, attr:{{r:58}}, duration:.5, ease:"back.out(1.6)"}}, {38.0 + 0.04 * k:.2f}); tl.to("#ring{k}", {{opacity:.35, duration:.3}}, 40.0);')
GP = [p for n, s, p in OS if n == "Durgapura"][0]
S.append(f'<g id="km3" style="opacity:0"><circle cx="{GP[0]:.1f}" cy="{GP[1]:.1f}" r="177" style="fill:#FF2D55;fill-opacity:.10;stroke:#FF2D55;stroke-width:4;stroke-dasharray:14 10"/>'
         f'<text x="{GP[0] + 182:.1f}" y="{GP[1] - 6:.1f}" style="font:900 30px Inter;fill:#FF6B86;paint-order:stroke;stroke:#000;stroke-width:6px">3 km</text>'
         f'<text x="{GP[0] + 66:.1f}" y="{GP[1] + 8:.1f}" style="font:900 24px Inter;fill:#FFB36B;paint-order:stroke;stroke:#000;stroke-width:5px">1 km</text></g>')
J.append('tl.fromTo("#km3", {opacity:0, scale:.3, transformOrigin:"' + f'{GP[0]:.1f}px {GP[1]:.1f}px' + '"}, {opacity:1, scale:1, duration:.6, ease:"back.out(1.6)"}, 40.0); tl.to("#km3", {opacity:0, duration:.3}, 46.9);')
chip("w0", "DHYAN RAKHNA", "Rings = ~1 km walk · red = what “near metro” ads can mean", 38.0, 46.9, y=250, col="#FFE03A")
H.append('<div id="t2031"><b>~2031</b><i>TARGET</i></div>')
J.append('tl.fromTo("#t2031", {opacity:0, scale:.6}, {opacity:1, scale:1, duration:.35, ease:"back.out(2)"}, 44.8); tl.to("#t2031", {opacity:0, duration:.3}, 46.9);')
scap("w1", f"Par {Y}dhyan rakhna{E}", 37.8, 39.4)
scap("w2", f"Ad mein “metro ke paas” ka matlab — {Y}3 km{E} bhi ho sakta hai", 39.4, 43.0)
scap("w3", f"{Y}Actual station{E} check karein", 43.0, 44.75)
scap("w4", f"Aur timeline — {Y}2031 ke aas-paas{E}", 44.75, 47.5)
photo("pcon", "construction.jpg", "Metro piling work", "Image supplied", 44.75, 47.0, x=50, y=1000, w=250, h=310)
sfx("whoosh-short", 37.6, .3)
# ---- 47.5 · save + share
cam(47.2, (CALL[0] + 120, CALL[1] - 40), WALL * 1.14, 1.0)
J.append('tl.to("[id^=os] text:not(.dense), [id^=ps] text:not(.dense)", {opacity:1, duration:.4}, 47.6);')
H.append('<div id="save"><svg viewBox="0 0 24 24" width="64" height="64"><path d="M6 3h12v18l-6-4-6 4z" style="fill:#FFE03A"/></svg><b>SAVE THIS MAP</b><i>you will need it</i></div>')
J.append('tl.fromTo("#save", {opacity:0, scale:.6}, {opacity:1, scale:1, duration:.4, ease:"back.out(2)"}, 47.6); tl.to("#save svg", {scale:1.2, duration:.35, yoyo:true, repeat:3}, 48.0); tl.to("#save", {opacity:0, duration:.3}, 48.9);')
scap("s0", f"Is map ko {Y}save{E} karo", 47.6, 48.85)
scap("s1", f"aur apne doston ko {Y}share{E} karo — jinka ghar metro line ke paas hai", 48.85, END + .2)
S.append('<rect id="ctadim" x="-3000" y="-3000" width="9000" height="9000" style="fill:#05080d;opacity:0"/>')
J.append('tl.to("#ctadim", {opacity:.5, duration:.5}, 48.9);')
H.append('<div id="share"><svg viewBox="0 0 24 24" width="84" height="84"><path d="M3 11l18-8-8 18-2-8z" style="fill:none;stroke:#fff;stroke-width:2;stroke-linejoin:round"/></svg><span>Send to a friend near the metro line</span></div>')
J.append('tl.fromTo("#share", {opacity:0, scale:.6}, {opacity:1, scale:1, duration:.4, ease:"back.out(2)"}, 49.0); tl.fromTo("#share svg", {scale:1}, {scale:1.18, duration:.45, yoyo:true, repeat:5}, 49.4);')
sfx("sparkle", 47.6, .3)
H.append('<div id="brand">ASHWILLPOWER · JAIPUR REAL ESTATE</div>')
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
J.append('tl.set("#cover", {opacity:0}, 0);')

CSS = """*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#070b12}
#root{position:relative;width:1080px;height:1920px;overflow:hidden}#world{position:absolute;inset:0;width:1080px;height:1920px}
.y{color:#FFE03A}.o{color:#FF9B3D}
.st{position:absolute;left:50px;right:50px;top:1330px;text-align:center;opacity:0;font:900 70px/1.08 Inter,Arial,sans-serif;color:#fff;text-shadow:0 4px 0 #000,0 0 20px rgba(0,0,0,.95),0 0 4px #000}
#hook{position:absolute;left:0;right:0;top:400px;text-align:center;opacity:0;font-family:Inter,Arial,sans-serif;text-shadow:0 6px 0 #000,0 0 30px rgba(0,0,0,.9)}
#hook b{display:block;font-weight:900;font-size:130px;line-height:.95;color:#fff;letter-spacing:-.01em}#hook em{display:block;margin-bottom:14px;font-style:normal;font:800 46px "JetBrains Mono",monospace;color:#FFE03A;letter-spacing:.2em}
#ss{position:absolute;left:0;right:0;top:250px;display:flex;justify-content:center;gap:22px;opacity:0}
#ss span{display:flex;align-items:center;gap:12px;padding:14px 24px;border-radius:40px;background:rgba(8,12,20,.85);border:2px solid rgba(255,255,255,.25);font:900 36px Inter,Arial,sans-serif;color:#fff}
.chip{position:absolute;left:60px;right:60px;opacity:0;padding:20px 28px;border-radius:20px;background:rgba(8,12,20,.88);border-left:10px solid #FF8A1F;font:800 40px/1.15 Inter,Arial,sans-serif;color:#fff}
.chip b{display:block;font:700 26px "JetBrains Mono",monospace;letter-spacing:.16em;margin-bottom:6px}
.ph{position:absolute;opacity:0;border-radius:16px;overflow:hidden;border:2px solid rgba(255,255,255,.55);box-shadow:0 18px 50px rgba(0,0,0,.7);background:#111}
.ph img{width:100%;height:100%;display:block}.pc{position:absolute;left:0;right:0;bottom:0;padding:26px 12px 8px;background:linear-gradient(180deg,transparent,rgba(0,0,0,.88));font:800 26px Inter,Arial,sans-serif;color:#fff}
.pc em{display:block;font-style:normal;font-weight:600;font-size:17px;color:#ddd;margin-top:4px}
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
#india{position:absolute;inset:0;opacity:0;background:radial-gradient(120% 80% at 50% 45%,#16202e,#070b12)}
.ic{position:absolute;opacity:0}.ic i{position:absolute;left:-13px;top:-13px;width:26px;height:26px;border-radius:50%;background:#FF5FA2;border:4px solid #fff;box-shadow:0 0 18px #FF5FA2}
.ic b{position:absolute;white-space:nowrap;padding:6px 14px;border-radius:12px;background:rgba(6,8,12,.86);font:900 32px Inter;color:#fff}.ic b span{color:#FF9FC6}
.ic.jp i{width:40px;height:40px;left:-20px;top:-20px;background:#FFE03A;box-shadow:0 0 30px #FFE03A}.ic.jp b{font-size:48px;background:#FFE03A;color:#111}.ic.jp b span{color:#7a3b00}
#inote{position:absolute;right:50px;top:1640px;font:500 20px "JetBrains Mono",monospace;color:rgba(255,255,255,.7)}
#t2031{position:absolute;right:60px;top:430px;opacity:0;padding:14px 22px;border-radius:18px;background:rgba(8,12,20,.88);border:2px solid #FF8A1F;text-align:center;font-family:Inter}#t2031 b{display:block;font-weight:900;font-size:64px;color:#FF9B3D}#t2031 i{display:block;font:700 22px "JetBrains Mono",monospace;font-style:normal;letter-spacing:.14em;color:#fff}
.st .bx{background:rgba(6,8,12,.62);padding:12px 24px 14px;border-radius:22px;display:inline-block;font-size:62px}
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
<video id="avatar" class="clip" src="assets/avatar.mp4" data-start="0" data-duration="{END}" data-track-index="0" playsinline data-has-audio="true" data-volume="1" style="position:absolute;left:0;top:0;width:2px;height:2px;opacity:0"></video>
<audio id="music" class="clip" src="assets/music_tune.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.13" data-fade-in="0.3" data-fade-out="2.5"></audio>
{"".join(SFX)}
</div><script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(J)}
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>""")
print("END", END, "pink pts", len(PINK), "pink len", round(PC[-1]), "orange len", round(OC[-1]), "stations", len(PS), len(OS))
