"""Rajasthan industrial areas — top-view satellite tour (Sentinel-2 cloudless, EOX). Industrial-area zones are indicative circles at approximate locations."""
import json, math, os
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
        d = len(l) / 15 + .15 + (1.0 if not PH else .6)
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
PXKM = 256 * 2 ** 13 / 40075 / math.cos(math.radians(26.5))
SVG, H, J, SFX = [], [], [], []
def sfx(n, t, v=.3): SFX.append(f'<audio id="sx{len(SFX)}" class="clip" src="assets/sfx/{n}.mp3" data-start="{t:.2f}" data-duration="2" data-track-index="{20 + len(SFX)}" data-volume="{v}"></audio>')
def pd(pts, close=False): return "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts) + (" Z" if close else "")
GOLD, ZONE, WAVE = "#C9A24A", "#FF3DCB", "#3FE0FF"
TM = json.load(open("tiles_meta.json"))

# industrial areas (north -> south): key, name, latlon, district, tag, status, line, keyword
IA = [
    ("sal", "SALARPUR", (28.10, 76.84), "Khairthal-Tijara", "HONDA &middot; HERO &middot; MARUTI KE PAAS", "new", 1, "Salarpur"),
    ("gaj", "GAJNER", (27.95, 73.10), "Bikaner", "CERAMIC PARK", "new", 2, "Gajner"),
    ("bich", "BICHOON", (26.80, 75.30), "Jaipur", "PHULERA FREIGHT CORRIDOR KE PAAS", "new", 3, "Bichoon"),
    ("fin", "FINTECH PARK", (26.84, 75.80), "Jaipur", "TONK ROAD &middot; IT &middot; AI", "soon", 3, "Fintech"),
    ("kunj", "KUNJBIHARIPURA", (26.74, 75.53), "Jaipur", "AUTO &middot; HEAVY ENGINEERING", "new", 3, "Kunjbiharipura"),
    ("hukk", "HUKKAN-NIMODIA", (26.63, 75.88), "Jaipur", "JAIPUR&ndash;KOTA NH-52", "new", 3, "Hukkan"),
    ("bor", "BORANADA + MEDTECH PARK", (26.15, 73.07), "Jodhpur", "MEDICAL DEVICES &middot; THAR DRY PORT", "new", 4, "Boranada"),
    ("rup", "RUPAHELI TEXTILE PARK", (25.98, 74.50), "Bhilwara", "ALLOTMENT SHURU", "new", 5, "Rupaheli"),
    ("pet", "PETRO ZONE", (25.88, 72.30), "Balotra", "REFINERY KE PAAS", "soon", 6, "Petro"),
    ("son", "SONIYANA", (25.13, 74.58), "Chittorgarh", "GLASS &middot; CERAMIC", "new", 7, "Soniyana"),
    ("gun", "GUNDI FATEHPUR", (24.82, 75.95), "Kota", "STONE &middot; AGRO", "new", 8, "Gundi"),
]
IP = {a[0]: wp(*a[2]) for a in IA}

# ---------- layers ----------
r = TM["raj"]
SVG.append('<rect x="-900000" y="-900000" width="2000000" height="2000000" fill="#0c0b0a"/>')
SVG.append('<image href="assets/img/bm4.jpg" x="-302848" y="-363008" width="786432" height="786432" preserveAspectRatio="none"/>')
SVG.append(f'<image href="assets/img/raj8.jpg" x="{r["x"]}" y="{r["y"]}" width="{r["w"]}" height="{r["h"]}" preserveAspectRatio="none" style="filter:saturate(1.2) brightness(.92)"/>')
SVG.append(f'<image href="assets/img/t_raj8.jpg" x="{r["x"]}" y="{r["y"]}" width="{r["w"]}" height="{r["h"]}" preserveAspectRatio="none" style="mix-blend-mode:multiply;opacity:.75"/>')
for a in IA:
    m = TM[a[0]]
    SVG.append(f'<image href="assets/img/s_{a[0]}.jpg" x="{m["x"]}" y="{m["y"]}" width="{m["w"]}" height="{m["h"]}" preserveAspectRatio="none"/>')
    SVG.append(f'<image href="assets/img/t_{a[0]}.jpg" x="{m["x"]}" y="{m["y"]}" width="{m["w"]}" height="{m["h"]}" preserveAspectRatio="none" style="mix-blend-mode:multiply;opacity:.7"/>')
ST = json.load(open("data/states.json"))
def ring(rs): return " ".join(pd([wp(la, lo) for lo, la in rr], True) for rr in rs)
RAJ = ring(ST["Rajasthan"])
# outside Rajasthan dimmed
SVG.append(f'<path d="M-900000 -900000 H1100000 V1100000 H-900000 Z {RAJ}" fill="#000" fill-opacity=".55" fill-rule="evenodd"/>')
SVG.append(f'<path id="raj" d="{RAJ}" style="fill:none;stroke:{GOLD};stroke-width:4;vector-effect:non-scaling-stroke"/>')
DG = {f["properties"]["district"]: f for f in json.load(open("data/rajasthan_districts.geojson"))["features"]}
def gpath(g):
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    return " ".join(pd([wp(la, lo) for lo, la in rr], True) for poly in polys for rr in poly[:1])
for nm in sorted({a[3] for a in IA}):
    SVG.append(f'<path class="dz" id="dz_{nm.replace("-", "_")}" d="{gpath(DG[nm]["geometry"])}" style="fill:none;stroke:#FFD36B;stroke-width:3;stroke-dasharray:14 9;vector-effect:non-scaling-stroke;opacity:0"/>')
# spotlight dim layer: dark everywhere except a hole around the active zone (hole moves via attr)
SVG.append('<defs><mask id="spot" maskUnits="userSpaceOnUse" x="-900000" y="-900000" width="2000000" height="2000000"><rect x="-900000" y="-900000" width="2000000" height="2000000" fill="#fff"/>'
           '<circle id="hole" cx="0" cy="0" r="1" fill="#000"/></mask>'
           '<radialGradient id="zg"><stop offset="0" stop-color="#FF3DCB" stop-opacity=".55"/><stop offset=".75" stop-color="#FF3DCB" stop-opacity=".35"/><stop offset="1" stop-color="#FF3DCB" stop-opacity="0"/></radialGradient>'
           '<filter id="gs"><feColorMatrix type="saturate" values=".15"/></filter></defs>')
SVG.append('<rect id="dimr" x="-900000" y="-900000" width="2000000" height="2000000" fill="#0b1220" fill-opacity="0" mask="url(#spot)"/>')
ZR = 2.6 * PXKM   # indicative zone radius
for a in IA:
    x, y = IP[a[0]]; col = "#FF9A3C" if a[5] == "soon" else ZONE
    SVG.append(f'<g class="zone" id="zn_{a[0]}" style="opacity:0"><circle cx="{x:.0f}" cy="{y:.0f}" r="{ZR:.0f}" fill="url(#zg)"/>'
               f'<circle class="zr" cx="{x:.0f}" cy="{y:.0f}" r="{ZR:.0f}" style="fill:none;stroke:{col};stroke-width:5;vector-effect:non-scaling-stroke;filter:drop-shadow(0 0 8px {col})"/></g>')
    for w in range(3):
        SVG.append(f'<circle class="wv wv_{a[0]}" cx="{x:.0f}" cy="{y:.0f}" r="10" style="fill:none;stroke:{WAVE};stroke-width:3;vector-effect:non-scaling-stroke;opacity:0"/>')
    SVG.append(f'<circle class="dot" id="dt_{a[0]}" cx="{x:.0f}" cy="{y:.0f}" r="10" style="fill:#fff;stroke:{WAVE};stroke-width:3;vector-effect:non-scaling-stroke;opacity:0"/>')

# ---------- camera ----------
OV_C, OV_W = wp(26.6, 73.85), 58000
CAMS = [(0, 0, OV_C, OV_W)]
J.append('const VB = document.getElementById("world"); const DOTS = () => document.querySelectorAll(".dot"); let CW = 1;'
         'function setW(w){ CW = w; document.querySelectorAll(".dot").forEach(e=>e.setAttribute("r", w/150)); }'
         'function zoomTo(t, c0, w0, c1, w1, d){ const o = {z:0}; tl.to(o, {z:1, duration:d, ease:"power2.inOut", onUpdate:()=>{ const w = Math.exp(Math.log(w0) + (Math.log(w1) - Math.log(w0)) * o.z); const f = Math.abs(w0 - w1) < 1e-6 ? o.z : (w0 - w) / (w0 - w1); const cx = c0[0] + (c1[0] - c0[0]) * f, cy = c0[1] + (c1[1] - c0[1]) * f; const h = w * 1920 / 1080; VB.setAttribute("viewBox", (cx - w / 2) + " " + (cy - h / 2) + " " + w + " " + h); setW(w); }}, t); }')
def zoom(t, c1, w1, d=1.0):
    c0, w0 = CAMS[-1][2], CAMS[-1][3]
    J.append(f'zoomTo({t:.2f}, [{c0[0]:.1f},{c0[1]:.1f}], {w0:.1f}, [{c1[0]:.1f},{c1[1]:.1f}], {w1:.1f}, {d});'); CAMS.append((t, d, c1, w1))
def cam_at(t):
    c, w = CAMS[0][2], CAMS[0][3]
    for t0, d, c1, w1 in CAMS:
        if t0 + d <= t + 1e-6: c, w = c1, w1
    return c, w
def scr(p, t):
    c, w = cam_at(t); h = w * 1920 / 1080
    return ((p[0] - (c[0] - w / 2)) / w * 1080, (p[1] - (c[1] - h / 2)) / h * 1920)
def vb(c, w): h = w * 1920 / 1080; return f"{c[0] - w / 2:.1f} {c[1] - h / 2:.1f} {w:.1f} {h:.1f}"
J.append(f'tl.set("#world", {{attr:{{viewBox:"{vb(OV_C, OV_W * 1.25)}"}}}}, 0); setW({OV_W});')
zoom(0, OV_C, OV_W, 1.2)

def lab(i, p, text, t, until, at, dy=-70, cls=""):
    x, y = scr(p, at); x = min(max(x, 40 + len(text) * 11), 1040 - len(text) * 11)
    H.append(f'<div class="ml {cls}" id="{i}" style="left:{x:.0f}px;top:{y + dy:.0f}px">{text}</div>')
    J.append(f'tl.fromTo("#{i}", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)", immediateRender:false}}, {t:.2f}); tl.to("#{i}", {{opacity:0, duration:.2}}, {until - .2:.2f});')
J.append('tl.set(".ml", {opacity:0}, 0);')
def waves(k, t0, t1, big=1.0):
    # repeating expanding rings (radius in world units relative to camera at the time)
    for w in range(3):
        J.append(f'tl.fromTo(".wv_{k}:nth-of-type(n)", {{}}, {{}}, 0);'.replace('tl.fromTo(".wv_' + k + ':nth-of-type(n)", {}, {}, 0);', ''))
    n = max(1, int((t1 - t0) / 1.5))
    J.append(f'(function(){{ const els = document.querySelectorAll(".wv_{k}"); els.forEach((e, i) => {{ tl.fromTo(e, {{attr:{{r:0}}, opacity:.95}}, {{attr:{{r:{big}}}, opacity:0, duration:1.5, ease:"power1.out", repeat:{n - 1}, immediateRender:false}}, {t0:.2f} + i * .5); tl.set(e, {{opacity:0}}, {t1:.2f}); }}); }})();')

# ---------- 0 OVERVIEW: top view + wave pins ----------
for i, a in enumerate(IA):
    k = a[0]; t = .5 + i * .07
    J.append(f'tl.fromTo("#dt_{k}", {{opacity:0}}, {{opacity:1, duration:.2}}, {t:.2f});')
    waves(k, t, S(1) - .2, OV_W / 22)
    off = {"bich": (-110, -30), "fin": (40, -64), "kunj": (40, 46), "hukk": (120, 6), "bor": (-70, -34), "pet": (-30, 24), "rup": (70, 34)}.get(k, (0, -34))
    lab(f"ol_{k}", (IP[k][0] + off[0] * OV_W / 1080, IP[k][1]), a[1], t + .1, S(1) - .1, 1.3, dy=off[1], cls="sm")
    sfx("click-soft", t, .12)
H.append('<div id="hook"><small>RAJASTHAN KE</small><b>NAYE INDUSTRIAL AREAS</b><span>&#128278; SAVE KAR LO</span></div>')
J.append(f'tl.fromTo("#hook", {{opacity:0, scale:1.1}}, {{opacity:1, scale:1, duration:.4, ease:"power3.out"}}, 0); tl.fromTo("#hook span", {{opacity:0, scale:1.4}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)", immediateRender:false}}, 1.3); tl.to("#hook span", {{scale:1.08, duration:.35, yoyo:true, repeat:5}}, 1.7); tl.to("#hook", {{opacity:0, y:-30, duration:.3}}, {S(1) - .3:.2f});')
H.append('<div id="ns"><b>NORTH</b><i></i><b>SOUTH</b></div>')
J.append(f'tl.fromTo("#ns", {{opacity:0}}, {{opacity:1, duration:.3}}, {wt(0, "Chaliye") - .1:.2f}); tl.fromTo("#ns i", {{scaleY:0}}, {{scaleY:1, duration:.8, ease:"power2.inOut"}}, {wt(0, "Chaliye"):.2f}); tl.to("#ns", {{opacity:0, duration:.3}}, {S(1) - .2:.2f});')
sfx("impact-bass-1", 0, .45); sfx("riser", .5, .3)

# ---------- tour ----------
AW = 34 * PXKM   # camera width at an area (~34 km across)
def area_time(a):
    return wt(a[6], a[7]) - .2 if a[6] == 3 else S(a[6]) + .05
def card(a, t, until):
    k = a[0]; soon = '<em class="s">COMING SOON</em>' if a[5] == "soon" else '<em>NAYA</em>'
    H.append(f'<div class="card" id="cd_{k}"><small>{a[3].upper()} ZILA {soon}</small><b>{a[1]}</b><span>{a[4]}</span></div>')
    J.append(f'tl.fromTo("#cd_{k}", {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:.35, ease:"power3.out"}}, {t:.2f}); tl.to("#cd_{k}", {{opacity:0, y:-20, duration:.2}}, {until - .2:.2f});')
prev = None
for i, a in enumerate(IA):
    k = a[0]; t = area_time(a); nxt = area_time(IA[i + 1]) if i + 1 < len(IA) else S(9) - .1
    c = (IP[k][0], IP[k][1] + AW * .12)   # keep the zone slightly above centre (captions sit low)
    if prev is None:
        zoom(t - .9, c, AW, 1.2)
    else:
        d = math.hypot(c[0] - CAMS[-1][2][0], c[1] - CAMS[-1][2][1])
        if d > AW * 2.5:
            mid = ((c[0] + CAMS[-1][2][0]) / 2, (c[1] + CAMS[-1][2][1]) / 2)
            zoom(t - 1.0, mid, max(d * 1.5, AW * 3), .55); zoom(t - .45, c, AW, .6)
        else:
            zoom(t - .6, c, AW, .7)
    tz = CAMS[-1][0] + CAMS[-1][1]
    sfx("whoosh", t - .8, .3)
    # spotlight hole + zone + district outline
    hx, hy = IP[k]
    J.append(f'tl.set("#hole", {{attr:{{cx:{hx:.0f}, cy:{hy:.0f}, r:{ZR * 1.6:.0f}}}}}, {t - .3:.2f}); tl.to("#dimr", {{attr:{{"fill-opacity":.55}}, duration:.5}}, {tz - .2:.2f});')
    J.append(f'tl.to("#zn_{k}", {{opacity:1, duration:.35}}, {tz:.2f}); tl.fromTo("#zn_{k} .zr", {{attr:{{r:{ZR * .3:.0f}}}}}, {{attr:{{r:{ZR:.0f}}}, duration:.6, ease:"back.out(1.8)", immediateRender:false}}, {tz:.2f}); tl.to("#zn_{k}", {{opacity:0, duration:.3}}, {nxt - .5:.2f});')
    J.append(f'tl.fromTo("#zn_{k} .zr", {{strokeWidth:5}}, {{strokeWidth:12, duration:.45, yoyo:true, repeat:3, immediateRender:false}}, {tz + .6:.2f});')
    J.append(f'tl.to("#dimr", {{attr:{{"fill-opacity":0}}, duration:.3}}, {nxt - .5:.2f});')
    dn = a[3].replace("-", "_")
    if prev is None or prev[3] != a[3]:
        last = max(j for j, b in enumerate(IA) if b[3] == a[3]); endd = area_time(IA[last + 1]) if last + 1 < len(IA) else S(9) - .1
        J.append(f'tl.to("#dz_{dn}", {{opacity:1, duration:.4}}, {t - .6:.2f}); tl.to("#dz_{dn}", {{opacity:0, duration:.3}}, {endd - .5:.2f});')
    waves(k, tz, nxt - .5, ZR * 2.4)
    lab(f"zl_{k}", IP[k], a[1], tz + .2, nxt - .3, tz, dy=-int(ZR / AW * 1080) - 40, cls="big" + (" soon" if a[5] == "soon" else ""))
    card(a, t, nxt)
    sfx("impact-bass-1", tz, .3)
    prev = a

# ---------- 9 real estate: back to top view, all zones glow ----------
zoom(S(9) - .5, OV_C, OV_W, 1.2)
for i, a in enumerate(IA):
    waves(a[0], S(9) + .5 + i * .05, S(10) - .1, OV_W / 18)
H.append('<div id="flow"><span>INDUSTRY</span><i>&rarr;</i><span>NAUKRI</span><i>&rarr;</i><b>GHAR &amp; PLOT KI DEMAND &#9650;</b></div>')
J.append(f'tl.fromTo("#flow", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.4, ease:"power3.out"}}, {S(9) + .3:.2f}); tl.fromTo("#flow b", {{opacity:0, x:30}}, {{opacity:1, x:0, duration:.4, immediateRender:false}}, {wt(9, "ghar") - .1:.2f}); tl.to("#flow", {{opacity:0, duration:.3}}, {S(10) - .1:.2f});')
sfx("riser", S(9), .3)

# ---------- 10 CTA ----------
H.append('<div id="cta"><b>AAPKE ZILE MEIN KAUNSA INDUSTRIAL AREA AA RAHA HAI?</b><span>COMMENT KARO</span></div>')
J.append(f'tl.to("#dim", {{opacity:.5, duration:.3}}, {S(10):.2f}); tl.fromTo("#cta", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.45, ease:"power3.out"}}, {S(10):.2f}); tl.to("#cta span", {{scale:1.06, duration:.4, yoyo:true, repeat:3}}, {wt(10, "Comment"):.2f});')
sfx("sparkle", wt(10, "Comment"), .3)

# ---------- captions ----------
HI = ["30 se zyada", "north se south", "Salarpur", "Gajner", "Bichoon", "Fintech Park", "Kunjbiharipura", "Hukkan-Nimodia", "Boranada Extension", "Medical Device Park", "Rupaheli Textile Park", "Petro Zone", "Soniyana", "Gundi Fatehpur", "Comment"]
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
H.append('<div id="cred">Sources: RIICO MIS (June 2026), RIICO DAP 2025, Rising Rajasthan &middot; zones indicative, locations approximate &middot; Imagery: Sentinel-2 cloudless (EOX)</div>')

CSS = """@font-face{font-family:Anton;src:url(assets/fonts/anton.woff2)}@font-face{font-family:Mont;font-weight:700;src:url(assets/fonts/mont700.woff2)}@font-face{font-family:Mont;font-weight:800;src:url(assets/fonts/mont800.woff2)}@font-face{font-family:Mont;font-weight:900;src:url(assets/fonts/mont900.woff2)}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#0c0b0a}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif}.y{color:#111;background:#F2B23E;border-radius:6px;padding:0 6px}
#world{position:absolute;inset:0;width:1080px;height:1920px}
#dim{position:absolute;inset:0;background:#000;opacity:0;z-index:5;pointer-events:none}
#face{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:40}
#cred{position:absolute;left:40px;right:40px;top:1660px;text-align:center;font:700 17px Mont;color:rgba(255,255,255,.7);z-index:20;text-shadow:0 2px 6px #000}
.ml{position:absolute;opacity:0;translate:-50% -50%;white-space:nowrap;z-index:8}
.ml.sm{padding:4px 10px;border-radius:4px;background:rgba(10,10,12,.85);border:1px solid #3FE0FF;color:#fff;font:800 20px Mont;letter-spacing:.06em}
.ml.big{padding:12px 26px;border-radius:6px;background:#FF3DCB;color:#fff;font:400 58px/1 Anton;letter-spacing:.03em;box-shadow:0 0 30px rgba(255,61,203,.8),0 10px 30px rgba(0,0,0,.6)}
.ml.big.soon{background:#FF9A3C;color:#111;box-shadow:0 0 30px rgba(255,154,60,.8),0 10px 30px rgba(0,0,0,.6)}
#hook{position:absolute;left:50px;right:50px;top:110px;z-index:16;text-align:center;padding:22px 20px;border-radius:8px;border:1.5px solid #C9A24A;background:linear-gradient(135deg,rgba(14,12,9,.9),rgba(34,27,18,.9))}
#hook small{display:block;font:700 30px Mont;letter-spacing:.3em;color:#F3E6C8}#hook b{display:block;margin-top:8px;font:400 92px/1 Anton;background:linear-gradient(180deg,#F7E3A8,#C9A24A);-webkit-background-clip:text;color:transparent}
#hook span{display:inline-block;margin-top:14px;padding:8px 22px;border-radius:4px;background:#C9A24A;color:#111;font:900 30px Mont;letter-spacing:.14em}
#ns{position:absolute;right:40px;top:520px;opacity:0;z-index:12;display:flex;flex-direction:column;align-items:center;gap:8px}#ns b{padding:6px 14px;border-radius:4px;background:rgba(10,10,12,.85);border:1px solid #3FE0FF;color:#3FE0FF;font:800 22px Mont;letter-spacing:.2em}
#ns i{width:8px;height:300px;border-radius:4px;background:linear-gradient(#3FE0FF,#FF3DCB);transform-origin:50% 0}
.card{position:absolute;left:50px;right:50px;top:120px;opacity:0;z-index:15;text-align:center;padding:20px 24px;border-radius:8px;border:1.5px solid #C9A24A;background:linear-gradient(135deg,rgba(14,12,9,.92),rgba(34,27,18,.92))}
.card small{display:inline-flex;align-items:center;gap:12px;font:700 26px Mont;letter-spacing:.22em;color:#F3E6C8}.card em{font-style:normal;padding:3px 10px;border-radius:3px;background:#3CE65A;color:#111;font:900 20px Mont;letter-spacing:.1em}.card em.s{background:#FF9A3C}
.card b{display:block;margin-top:8px;font:400 76px/1 Anton;background:linear-gradient(180deg,#F7E3A8,#C9A24A);-webkit-background-clip:text;color:transparent}.card span{display:block;margin-top:8px;font:800 28px Mont;letter-spacing:.1em;color:#FF8BE3}
#flow{position:absolute;left:0;right:0;top:140px;margin:0 auto;width:max-content;opacity:0;z-index:15;display:flex;align-items:center;gap:14px;padding:16px 26px;border-radius:6px;border:1.5px solid #C9A24A;background:linear-gradient(135deg,rgba(14,12,9,.95),rgba(34,27,18,.95))}
#flow span{font:400 40px Anton;color:#F3E6C8}#flow i{font:300 40px Mont;color:#C9A24A;font-style:normal}#flow b{font:400 40px Anton;color:#3CE65A}
#cta{position:absolute;left:60px;right:60px;top:420px;opacity:0;text-align:center;z-index:16}#cta b{display:block;padding:24px;border-radius:6px;background:linear-gradient(135deg,rgba(14,12,9,.95),rgba(34,27,18,.95));border:1.5px solid #C9A24A;color:#F3E6C8;font:400 72px/1.05 Anton}
#cta span{display:inline-block;margin-top:24px;padding:14px 34px;border-radius:4px;background:#C9A24A;color:#111;font:900 40px Mont;letter-spacing:.22em}
.cp{position:absolute;left:40px;right:40px;top:1470px;text-align:center;opacity:0;z-index:35}
.cp div{display:inline-block;padding:4px 20px 8px;border-radius:10px;background:#fff;font:900 60px/1.12 Mont;color:#111;box-shadow:0 8px 24px rgba(0,0,0,.45)}"""
audio = (f'<audio id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{END}" data-track-index="1" data-volume="1"></audio><audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.12" data-fade-out="1.5"></audio>' if VOICE
         else f'<audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.55" data-fade-out="1.5"></audio>')
open(f"{P}/index.html", "w").write(f"""<!doctype html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="30">
<svg id="world" viewBox="{vb(OV_C, OV_W)}" preserveAspectRatio="xMidYMid slice">{"".join(SVG)}</svg><div id="dim"></div>
{"".join(H)}
{audio}
{"".join(SFX)}
</div><script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(J)}
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>""")
print("END", END, [p["s"] for p in PH])
