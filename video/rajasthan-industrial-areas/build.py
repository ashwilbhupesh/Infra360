"""Rajasthan industrial areas — top-view satellite tour (Sentinel-2 cloudless, EOX). Industrial-area zones are indicative circles at approximate locations."""
import json, math, os
P = "proj"
LINES = [
    "Rajasthan mein pichhle do saal mein 30 se zyada naye industrial areas khule hain, aur aur bhi aa rahe hain. Chaliye north se south dekhte hain.",
    "Sabse upar, Bhiwadi mein Salarpur, Honda, Hero aur Maruti ke paas.",
    "Bikaner mein Gajner, ceramic industry ke liye.",
    "Jaipur mein Bichoon, Phulera freight corridor ke paas. Kunjbiharipura, Bagru ke paas, auto aur heavy engineering ke liye. Tonk Road par naya Fintech Park, airport ke bilkul paas. Aur Hukkan-Nimodia, Jaipur-Kota highway par.",
    "Jodhpur mein Boranada Extension aur Medical Device Park.",
    "Bhilwara mein Rupaheli Textile Park, jahan allotment shuru ho chuka hai.",
    "Balotra mein Petro Zone, refinery ke bilkul paas.",
    "Chittorgarh mein Soniyana, glass aur ceramic ke liye.",
    "Aur sabse neeche, Kota mein Gundi Fatehpur.",
    "Real estate ka funda simple hai: jahan industry, wahan naukri, aur jahan naukri, wahan ghar aur plot ki demand.",
    "Aapke zile mein kaunsa industrial area aa raha hai? Comment karo.",
]
VOICE = os.path.exists("rec/phrases.json")
# text preview: anchors.json (written by the previous build pass) pins each area keyword to the moment its zone lands
ANC = {} if VOICE or not os.path.exists("anchors.json") else json.load(open("anchors.json"))
if VOICE: PH = json.load(open("rec/phrases.json"))
else:
    PH = []; t = .3
    for n_, l in enumerate(LINES):
        d = len(l) / 15 + .15 + (1.0 if not PH else .6); e = t + d
        for key, ta in ANC.items():
            ln, kw = key.split("|")
            if int(ln) == n_ and kw == "__end": e = max(e, ta); continue
            if int(ln) == n_:
                ci = l.lower().find(kw.lower()); e = max(e, ta + (len(l) - ci) / 15 + .4)
        PH.append({"s": round(t, 2), "e": round(e, 2), "t": l}); t = e + .3
def S(k): return PH[k]["s"]
def E(k): return PH[k]["e"]
def tchar(k, ci):
    """time at character index ci of line k (piecewise linear through anchors)"""
    l = PH[k]["t"]; pts = [(0, S(k))]
    for key, ta in sorted(ANC.items(), key=lambda kv: kv[1]):
        ln, kw = key.split("|")
        if int(ln) == k:
            c = l.lower().find(kw.lower())
            if c > pts[-1][0] and ta > pts[-1][1]: pts.append((c, ta))
    pts.append((len(l), max(E(k), pts[-1][1] + .3)))
    for (c0, t0), (c1, t1) in zip(pts, pts[1:]):
        if ci <= c1: return t0 + (t1 - t0) * (ci - c0) / max(1, c1 - c0)
    return E(k)
def wt(k, w):
    i = PH[k]["t"].lower().find(w.lower()); assert i >= 0, (k, w)
    return tchar(k, i)
END = round(E(10) + 1.0, 2)
def wp(lat, lon):
    n = 2 ** 13
    return (((lon + 180) / 360 * n) - 5791) * 256, (((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n) - 3466) * 256
PXKM = 256 * 2 ** 13 / 40075 / math.cos(math.radians(26.5))
SVG, H, J, SFX = [], [], [], []
def sfx(n, t, v=.3): SFX.append(f'<audio id="sx{len(SFX)}" class="clip" src="assets/sfx/{n}.mp3" data-start="{t:.2f}" data-duration="2" data-track-index="{20 + len(SFX)}" data-volume="{v}"></audio>')
def pd(pts, close=False): return "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts) + (" Z" if close else "")
GOLD, ZONE, WAVE = "#C9A24A", "#FFB020", "#BFE6FA"
SKY = "#A8D8F0"
TM = json.load(open("tiles_meta.json"))

# industrial areas (north -> south): key, name, latlon, district, tag, status, line, keyword
IA = [
    ("sal", "SALARPUR", (28.10, 76.84), "Khairthal-Tijara", "HONDA &middot; HERO &middot; MARUTI KE PAAS", "new", 1, "Salarpur"),
    ("gaj", "GAJNER", (27.95, 73.10), "Bikaner", "CERAMIC PARK", "new", 2, "Gajner"),
    ("bich", "BICHOON", (26.80, 75.30), "Jaipur", "PHULERA FREIGHT CORRIDOR KE PAAS", "new", 3, "Bichoon"),
    ("kunj", "KUNJBIHARIPURA", (26.74, 75.53), "Jaipur", "AUTO &middot; HEAVY ENGINEERING", "new", 3, "Kunjbiharipura"),
    ("fin", "FINTECH PARK", (26.84, 75.80), "Jaipur", "TONK ROAD &middot; IT &middot; AI", "soon", 3, "Fintech"),
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
SVG.append('<defs><radialGradient id="fg"><stop offset=".55" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient><mask id="feather" maskContentUnits="objectBoundingBox"><rect width="1" height="1" fill="url(#fg)"/></mask><linearGradient id="lh"><stop offset="0" stop-color="#000"/><stop offset=".025" stop-color="#fff"/><stop offset=".975" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient><linearGradient id="lv" x2="0" y2="1"><stop offset="0" stop-color="#000"/><stop offset=".025" stop-color="#fff"/><stop offset=".975" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient><mask id="fh" maskContentUnits="objectBoundingBox"><rect width="1" height="1" fill="url(#lh)"/></mask><mask id="fv" maskContentUnits="objectBoundingBox"><rect width="1" height="1" fill="url(#lv)"/></mask></defs>')
SVG.append('<g id="base" style="filter:grayscale(0) brightness(1)">')
SVG.append('<image href="assets/img/bm4.jpg" x="-302848" y="-363008" width="786432" height="786432" preserveAspectRatio="none"/>')
SVG.append(f'<g mask="url(#fv)"><image mask="url(#fh)" href="assets/img/raj8.jpg" x="{r["x"]}" y="{r["y"]}" width="{r["w"]}" height="{r["h"]}" preserveAspectRatio="none" style="filter:saturate(1.05) brightness(.95)"/>')
SVG.append(f'<image href="assets/img/t_raj8.jpg" x="{r["x"]}" y="{r["y"]}" width="{r["w"]}" height="{r["h"]}" preserveAspectRatio="none" style="mix-blend-mode:multiply;opacity:.75"/></g>')
for a in IA:
    m = TM[a[0]]
    SVG.append(f'<g class="patch" id="pt_{a[0]}" style="opacity:0" mask="url(#feather)"><image href="assets/img/s_{a[0]}.jpg" x="{m["x"]}" y="{m["y"]}" width="{m["w"]}" height="{m["h"]}" preserveAspectRatio="none"/>')
    SVG.append(f'<image href="assets/img/t_{a[0]}.jpg" x="{m["x"]}" y="{m["y"]}" width="{m["w"]}" height="{m["h"]}" preserveAspectRatio="none" style="mix-blend-mode:multiply;opacity:.7"/></g>')
SVG.append('</g>')
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
    SVG.append(f'<path class="dz" id="dz_{nm.replace("-", "_")}" d="{gpath(DG[nm]["geometry"])}" style="fill:{SKY};fill-opacity:0;stroke:#fff;stroke-width:3;stroke-linejoin:round;vector-effect:non-scaling-stroke;opacity:0"/>')
# spotlight dim layer: dark everywhere except a hole around the active zone (hole moves via attr)
SVG.append('<defs><mask id="spot" maskUnits="userSpaceOnUse" x="-900000" y="-900000" width="2000000" height="2000000"><rect x="-900000" y="-900000" width="2000000" height="2000000" fill="#fff"/>'
           '<circle id="hole" cx="0" cy="0" r="1" fill="#000"/></mask>'
           '<radialGradient id="zg"><stop offset="0" stop-color="#FFB020" stop-opacity=".55"/><stop offset=".75" stop-color="#FFB020" stop-opacity=".35"/><stop offset="1" stop-color="#FFB020" stop-opacity="0"/></radialGradient>'
           '<filter id="gs"><feColorMatrix type="saturate" values=".15"/></filter></defs>')
SVG.append('<rect id="dimr" x="-900000" y="-900000" width="2000000" height="2000000" fill="#0b1a26" fill-opacity="0" mask="url(#spot)"/>')
ZR = 2.6 * PXKM   # indicative zone radius
for a in IA:
    x, y = IP[a[0]]; col = "#FF7A45" if a[5] == "soon" else ZONE
    SVG.append(f'<g class="zone" id="zn_{a[0]}" style="opacity:0"><circle cx="{x:.0f}" cy="{y:.0f}" r="{ZR:.0f}" fill="url(#zg)"/>'
               f'<circle class="zr" cx="{x:.0f}" cy="{y:.0f}" r="{ZR:.0f}" style="fill:none;stroke:{col};stroke-width:5;vector-effect:non-scaling-stroke;filter:drop-shadow(0 0 8px {col})"/></g>')
    for w in range(3):
        SVG.append(f'<circle class="wv wv_{a[0]}" cx="{x:.0f}" cy="{y:.0f}" r="10" style="fill:none;stroke:{WAVE};stroke-width:3;vector-effect:non-scaling-stroke;opacity:0"/>')
    SVG.append(f'<circle class="dot" id="dt_{a[0]}" cx="{x:.0f}" cy="{y:.0f}" r="10" style="fill:#fff;stroke:{WAVE};stroke-width:3;vector-effect:non-scaling-stroke;opacity:0"/>')

# ---------- camera: one continuous smooth flight (van Wijk zoom-pan), segments never overlap ----------
OV_C, OV_W = wp(26.6, 73.85), 58000
INIT = (OV_C, OV_W * 1.22)
CAMS = [(0, 0, INIT[0], INIT[1])]
def vwS(c0, w0, c1, w1, rho=1.3):
    d1 = math.hypot(c1[0] - c0[0], c1[1] - c0[1])
    if d1 < 1e-3: return abs(math.log(w1 / w0)) / rho
    b0 = (w1 * w1 - w0 * w0 + rho ** 4 * d1 * d1) / (2 * w0 * rho ** 2 * d1); b1 = (w1 * w1 - w0 * w0 - rho ** 4 * d1 * d1) / (2 * w1 * rho ** 2 * d1)
    r0 = math.log(math.sqrt(b0 * b0 + 1) - b0); r1 = math.log(math.sqrt(b1 * b1 + 1) - b1); return abs(r1 - r0) / rho
def zoom(t, c1, w1, d=None):
    """schedule a camera move; returns arrival time. start is pushed after the previous move ends."""
    t0p, dp, c0, w0 = CAMS[-1]; t = max(t, t0p + dp)
    if d is None: d = min(2.1, max(1.15, .85 + .32 * vwS(c0, w0, c1, w1)))
    CAMS.append((t, d, c1, w1)); return t + d
def cam_at(t):
    c, w = CAMS[0][2], CAMS[0][3]
    for t0, d, c1, w1 in CAMS:
        if t0 + d <= t + 1e-6: c, w = c1, w1
    return c, w
def scr(p, t):
    c, w = cam_at(t); h = w * 1920 / 1080
    return ((p[0] - (c[0] - w / 2)) / w * 1080, (p[1] - (c[1] - h / 2)) / h * 1920)
def vb(c, w): h = w * 1920 / 1080; return f"{c[0] - w / 2:.1f} {c[1] - h / 2:.1f} {w:.1f} {h:.1f}"
def cam_js():
    kf = ",".join(f"[{t:.3f},{d:.3f},{c[0]:.1f},{c[1]:.1f},{w:.1f}]" for t, d, c, w in CAMS[1:])
    return ('const VB = document.getElementById("world");'
     'function setW(w){ document.querySelectorAll(".dot").forEach(e=>e.setAttribute("r", w/150)); document.querySelectorAll(".tdot").forEach(e=>e.setAttribute("r", w/120)); }'
     'function vw(p0,p1){ const rho=1.3, ux0=p0[0], uy0=p0[1], w0=p0[2], w1=p1[2], dx=p1[0]-ux0, dy=p1[1]-uy0, d2=dx*dx+dy*dy;'
     ' if(d2<1e-6){ const S=Math.log(w1/w0); return u=>[ux0, uy0, w0*Math.exp(u*S)]; }'
     ' const d1=Math.sqrt(d2), b0=(w1*w1-w0*w0+rho**4*d2)/(2*w0*rho*rho*d1), b1=(w1*w1-w0*w0-rho**4*d2)/(2*w1*rho*rho*d1), r0=Math.log(Math.sqrt(b0*b0+1)-b0), r1=Math.log(Math.sqrt(b1*b1+1)-b1), S=(r1-r0)/rho;'
     ' return u=>{ const s=u*S, c0=Math.cosh(r0), q=w0/(rho*rho*d1)*(c0*Math.tanh(rho*s+r0)-Math.sinh(r0)); return [ux0+q*dx, uy0+q*dy, w0*c0/Math.cosh(rho*s+r0)]; }; }'
     f'const INIT=[{INIT[0][0]:.1f},{INIT[0][1]:.1f},{INIT[1]:.1f}]; const KF=[{kf}]; const SEG=[]; {{ let cur=INIT; KF.forEach(k=>{{ const e=[k[2],k[3],k[4]]; SEG.push({{t0:k[0], d:k[1], f:vw(cur,e), e:e}}); cur=e; }}); }}'
     'function camAt(t){ let st=INIT; for(const s of SEG){ if(t<s.t0) break; if(t<s.t0+s.d){ const u=(t-s.t0)/s.d, e=u<.5?4*u*u*u:1-Math.pow(-2*u+2,3)/2; return s.f(e);} st=s.e; } return st; }'
     f'const CO={{t:0}}; tl.to(CO, {{t:{END}, duration:{END}, ease:"none", onUpdate:()=>{{ const c=camAt(CO.t), w=c[2], h=w*1920/1080; VB.setAttribute("viewBox", (c[0]-w/2)+" "+(c[1]-h/2)+" "+w+" "+h); setW(w); }}}}, 0);')
zoom(0, OV_C, OV_W, 1.3)


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
    waves(k, t, S(1) - .4, OV_W / 22)
    off = {"bich": (-110, -30), "fin": (40, -64), "kunj": (40, 46), "hukk": (120, 6), "bor": (-70, -34), "pet": (-30, 24), "rup": (70, 34)}.get(k, (0, -34))
    lab(f"ol_{k}", (IP[k][0] + off[0] * OV_W / 1080, IP[k][1]), a[1], t + .1, S(1) - .5, 1.3, dy=off[1], cls="sm")
    sfx("click-soft", t, .12)
H.append('<div id="hook"><small>RAJASTHAN KE</small><b>NAYE INDUSTRIAL AREAS</b><span>&#128278; SAVE KAR LO</span></div>')
J.append(f'tl.fromTo("#hook", {{opacity:0, scale:1.1}}, {{opacity:1, scale:1, duration:.4, ease:"power3.out"}}, 0); tl.fromTo("#hook span", {{opacity:0, scale:1.4}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)", immediateRender:false}}, 1.3); tl.to("#hook span", {{scale:1.08, duration:.35, yoyo:true, repeat:5}}, 1.7); tl.to("#hook", {{opacity:0, y:-30, duration:.3}}, {S(1) - .8:.2f});')
H.append('<div id="ns"><b>NORTH</b><i></i><b>SOUTH</b></div>')
J.append(f'tl.fromTo("#ns", {{opacity:0}}, {{opacity:1, duration:.3}}, {wt(0, "Chaliye") - .1:.2f}); tl.fromTo("#ns i", {{scaleY:0}}, {{scaleY:1, duration:.8, ease:"power2.inOut"}}, {wt(0, "Chaliye"):.2f}); tl.to("#ns", {{opacity:0, duration:.3}}, {S(1) - .8:.2f});')
sfx("impact-bass-1", 0, .45); sfx("riser", .5, .3)

# ---------- tour (beat-scheduled: every stop holds >= MH s, overlays always leave before the camera moves) ----------
AW = 34 * PXKM   # camera width at an area (~34 km across)
MH, DH = 2.5, 1.2   # min hold at an area / at a district view
FIRST = {}
for a in IA: FIRST.setdefault(a[3], a[0])
def dbox(nm):
    g = DG[nm]["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    pts = [wp(la, lo) for poly in polys for rr in poly[:1] for lo, la in rr]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; return min(xs), min(ys), max(xs), max(ys)
def dview(nm):
    x0, y0, x1, y1 = dbox(nm); c = ((x0 + x1) / 2, (y0 + y1) / 2 + (y1 - y0) * .08)
    return c, max((x1 - x0) * 1.35, (y1 - y0) * 1.35 * 1080 / 1300)
def acam(k): return (IP[k][0], IP[k][1] + AW * .12), AW
# connectivity: nearest key station + airport (straight-line km)
ST_ = {"sal": ("REWARI JN", (28.196, 76.617)), "gaj": ("BIKANER JN", (28.012, 73.318)), "bich": ("PHULERA JN", (26.874, 75.243)), "kunj": ("JAIPUR JN", (26.920, 75.788)),
       "fin": ("DURGAPURA STN", (26.851, 75.785)), "hukk": ("CHAKSU STN", (26.604, 75.946)), "bor": ("JODHPUR JN", (26.284, 73.022)), "rup": ("GULABPURA STN", (25.904, 74.660)),
       "pet": ("BALOTRA JN", (25.836, 72.240)), "son": ("CHITTORGARH JN", (24.882, 74.640)), "gun": ("RAMGANJ MANDI JN", (24.648, 75.940))}
AIR = {"sal": ("DELHI AIRPORT", (28.556, 77.100)), "gaj": ("BIKANER AIRPORT", (28.071, 73.207)), "bich": ("JAIPUR AIRPORT", (26.824, 75.812)), "kunj": ("JAIPUR AIRPORT", (26.824, 75.812)),
       "fin": ("JAIPUR AIRPORT", (26.824, 75.812)), "hukk": ("JAIPUR AIRPORT", (26.824, 75.812)), "bor": ("JODHPUR AIRPORT", (26.251, 73.049)), "rup": ("KISHANGARH AIRPORT", (26.591, 74.812)),
       "pet": ("JODHPUR AIRPORT", (26.251, 73.049)), "son": ("UDAIPUR AIRPORT", (24.618, 73.896))}
IC = {"road": '<svg viewBox="0 0 24 24"><path d="M9 2 5 22M15 2l4 20" stroke="currentColor" stroke-width="2.4" fill="none"/><path d="M12 3v3M12 10v4M12 18v3" stroke="currentColor" stroke-width="2.4"/></svg>',
      "rail": '<svg viewBox="0 0 24 24"><rect x="5" y="2" width="14" height="15" rx="3" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="M5 10h14" stroke="currentColor" stroke-width="2"/><circle cx="9" cy="13.5" r="1.3" fill="currentColor"/><circle cx="15" cy="13.5" r="1.3" fill="currentColor"/><path d="M8 17l-3 5M16 17l3 5" stroke="currentColor" stroke-width="2.2"/></svg>',
      "air": '<svg viewBox="0 0 24 24"><path fill="currentColor" d="M21 15.5v-2l-8-5V3.5a1.5 1.5 0 0 0-3 0V8.5l-8 5v2l8-2.5V18l-2 1.5V21l3.5-1 3.5 1v-1.5L13 18v-5z" transform="translate(.5 0)"/></svg>'}
def card(a, t, until):
    k = a[0]; soon = '<em class="s">COMING SOON</em>' if a[5] == "soon" else '<em>NAYA</em>'
    ch = [f'<i>{IC["road"]}{REF[k][1][0][0]}</i>']
    if k in ST_: ch.append(f'<i>{IC["rail"]}{ST_[k][0]} &middot; ~{max(1, round(hav(a[2], ST_[k][1]))):.0f} KM</i>')
    if k in AIR: ch.append(f'<i>{IC["air"]}{AIR[k][0]} &middot; ~{max(1, round(hav(a[2], AIR[k][1]))):.0f} KM</i>')
    H.append(f'<div class="card" id="cd_{k}"><small>{a[3].upper()} ZILA {soon}</small><b>{a[1]}</b><span>{a[4]}</span><div class="conn">{"".join(ch)}</div></div>')
    J.append(f'tl.fromTo("#cd_{k}", {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:.35, ease:"power3.out", immediateRender:false}}, {t:.2f}); tl.fromTo("#cd_{k}", {{opacity:1}}, {{opacity:0, y:-20, duration:.25, immediateRender:false}}, {until - .25:.2f}); tl.set("#cd_{k}", {{opacity:0}}, 0);')
    J.append(f'tl.fromTo("#cd_{k} .conn i", {{opacity:0, y:10}}, {{opacity:1, y:0, duration:.3, stagger:.12, immediateRender:false}}, {t + .9:.2f});')

# key roads & towns for relative position (scheme-brochure style); road geometry is snapped to Natural Earth highways
REF = {
 "sal": ([("BHIWADI", (28.21, 76.86)), ("DHARUHERA", (28.21, 76.79)), ("TIJARA", (27.93, 76.86)), ("DELHI", (28.61, 77.21)), ("HONDA PLANT, TAPUKARA", (28.14, 76.90))], [("NH-48", [(28.45, 77.03), (28.21, 76.79), (27.95, 76.52)])]),
 "gaj": ([("BIKANER", (28.02, 73.31)), ("KOLAYAT", (27.84, 72.95))], [("NH-11", [(28.02, 73.31), (27.93, 73.10), (27.80, 72.92)])]),
 "bich": ([("PHULERA", (26.87, 75.24)), ("DUDU", (26.68, 75.24)), ("JAIPUR", (26.91, 75.79))], [("NH-48", [(26.91, 75.79), (26.81, 75.54), (26.68, 75.24)])]),
 "fin": ([("SITAPURA", (26.78, 75.85)), ("WALLED CITY", (26.92, 75.82))], [("TONK ROAD", [(26.93, 75.80), (26.86, 75.80), (26.76, 75.83)])]),
 "kunj": ([("BAGRU", (26.81, 75.54)), ("PHAGI", (26.57, 75.54))], [("NH-48", [(26.91, 75.79), (26.81, 75.54), (26.68, 75.24)])]),
 "hukk": ([("SITAPURA", (26.78, 75.85)), ("JAIPUR", (26.91, 75.79))], [("NH-52", [(26.91, 75.79), (26.79, 75.82), (26.60, 75.95), (26.42, 76.05)])]),
 "bor": ([("JODHPUR", (26.24, 73.02)), ("LUNI", (26.00, 73.00))], [("NH-62", [(26.24, 73.02), (26.10, 73.10), (25.90, 73.25)])]),
 "rup": ([("BHILWARA", (25.35, 74.63)), ("AJMER", (26.45, 74.64))], [("NH-48", [(25.35, 74.63), (25.90, 74.66), (26.20, 74.65)])]),
 "pet": ([("PACHPADRA REFINERY", (25.95, 72.27))], [("NH-25", [(25.75, 72.05), (25.83, 72.24), (25.95, 72.45)])]),
 "son": ([("HAMIRGARH", (25.18, 74.63)), ("BHILWARA", (25.35, 74.63))], [("NH-48", [(25.35, 74.63), (25.13, 74.63), (24.88, 74.62)])]),
 "gun": ([("KOTA", (25.18, 75.83)), ("MORAK", (24.80, 75.98))], [("NH-52", [(25.18, 75.83), (24.95, 75.92), (24.65, 76.05)])]),
}
for k in REF:   # stations / airports join the map labels (deduped)
    tw = REF[k][0]
    if k in ST_: tw.append((ST_[k][0], ST_[k][1], "rail"))
    if k in AIR and not any(t[0] == AIR[k][0] for t in tw): tw.append((AIR[k][0], AIR[k][1], "air"))
LM = {"pet": ("PACHPADRA REFINERY", "lm_refinery", "HPCL Rajasthan Refinery, Pachpadra"), "fin": ("JAIPUR AIRPORT", "lm_airport", "Jaipur International Airport"),
      "bor": ("JODHPUR", "lm_mehrangarh", "Jodhpur &middot; Mehrangarh"), "gaj": ("BIKANER", "lm_junagarh", "Bikaner &middot; Junagarh Fort")}
def hav(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    return 6371 * 2 * math.asin(math.sqrt(math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2))
NE = json.load(open("data/ne_raj.json"))
def clip(lines, box):
    runs = []
    for l in lines:
        pts = [wp(p[1], p[0]) for p in l]; cur = []
        for i, p in enumerate(pts):
            if box[0] < p[0] < box[2] and box[1] < p[1] < box[3]:
                if not cur and i > 0: cur.append(pts[i - 1])
                cur.append(p)
            elif cur: cur.append(p); runs.append(cur); cur = []
        if len(cur) > 1: runs.append(cur)
    return runs
def dps(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / max(1e-9, dx * dx + dy * dy)))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)
RG = {}
for k, (towns, roads) in REF.items():
    x, y = IP[k]; box = (x - AW * .95, y - AW * 1.7, x + AW * .95, y + AW * 1.7)
    rails = [r for f in NE["ne_10m_railroads"] for r in clip(f["l"], box)]
    rds = [(f["p"]["type"], clip(f["l"], box)) for f in NE["ne_10m_roads"]]; rds = [(ty, rr) for ty, rr in rds if rr]
    # match each named road to the closest Natural Earth highway (mean distance of samples < 4 km)
    named = []
    for rn, rp in roads:
        P_ = [wp(*q) for q in rp]; samp = []
        for u, v in zip(P_, P_[1:]):
            n = max(1, int(math.hypot(v[0] - u[0], v[1] - u[1]) / (2 * PXKM)))
            samp += [(u[0] + (v[0] - u[0]) * i / n, u[1] + (v[1] - u[1]) * i / n) for i in range(n)]
        samp = [s for s in samp if box[0] < s[0] < box[2] and box[1] < s[1] < box[3]] or samp
        best = None
        for ty, rr in rds:
            m = sum(min(dps(s, a_, b_) for r_ in rr for a_, b_ in zip(r_, r_[1:])) for s in samp) / len(samp)
            if best is None or m < best[0]: best = (m, rr)
        named.append((rn, best[1] if best and best[0] < 4 * PXKM else None))
    RG[k] = named
    g = []
    for r_ in rails:
        g.append(f'<path d="{pd(r_)}" style="fill:none;stroke:#141414;stroke-width:8;stroke-linejoin:round;vector-effect:non-scaling-stroke"/><path d="{pd(r_)}" style="fill:none;stroke:#f4f4f4;stroke-width:4;stroke-dasharray:12 10;vector-effect:non-scaling-stroke"/>')
    for ty, rr in rds:
        sw = 8 if ty == "Major Highway" else 5
        for r_ in rr:
            g.append(f'<path d="{pd(r_)}" style="fill:none;stroke:#000;stroke-opacity:.55;stroke-width:{sw + 6};stroke-linecap:round;stroke-linejoin:round;vector-effect:non-scaling-stroke"/>'
                     f'<path class="rd" d="{pd(r_)}" pathLength="1" style="fill:none;stroke:#FFC42E;stroke-width:{sw};stroke-linecap:round;stroke-linejoin:round;vector-effect:non-scaling-stroke;stroke-dasharray:1;stroke-dashoffset:1"/>')
    for t_ in towns:
        p = wp(*t_[1]); col = {"rail": "#f4f4f4", "air": "#7FD3FF"}.get(t_[2] if len(t_) > 2 else "", "#fff")
        g.append(f'<circle class="tdot" cx="{p[0]:.0f}" cy="{p[1]:.0f}" r="1" style="fill:{col};stroke:#111;stroke-width:3;vector-effect:non-scaling-stroke"/>')
    SVG.append(f'<g class="refg" id="ref_{k}" style="opacity:0">{"".join(g)}</g>')
def ref_labels(a, tz, until):
    """screen-space labels for roads/towns with collision avoidance; off-screen towns -> edge arrows"""
    k = a[0]; towns, roads = REF[k]; placed = []
    zx, zy = scr(IP[k], tz); placed.append((zx - 210, zy - 150, zx + 210, zy + 120)); placed.append((0, 0, 1080, 470))
    def free(x0, y0, x1, y1):
        return all(x1 < a0 or x0 > a1 or y1 < b0 or y0 > b1 for a0, b0, a1, b1 in placed)
    out = []
    for rn, rr in RG[k]:
        if not rr: continue
        cands = []
        for r_ in rr:
            for i_ in range(len(r_) - 1):
                for f_ in (.5,):
                    q = (r_[i_][0] + (r_[i_ + 1][0] - r_[i_][0]) * f_, r_[i_][1] + (r_[i_ + 1][1] - r_[i_][1]) * f_)
                    x, y = scr(q, tz); cands.append((abs(math.hypot(x - zx, y - zy) - 330), x, y))
        for _, x, y in sorted(cands):
            w_ = len(rn) * 17 + 24; box = (x - w_ / 2, y - 22, x + w_ / 2, y + 22)
            if 60 < x - w_ / 2 and x + w_ / 2 < 1020 and 490 < y < 1380 and free(*box):
                placed.append(box); out.append(f'<div class="rl road" style="left:{x:.0f}px;top:{y:.0f}px">{rn}</div>'); break
    for t_ in towns:
        tn, ll = t_[0], t_[1]; kind = t_[2] if len(t_) > 2 else ""
        x, y = scr(wp(*ll), tz); km = hav(a[2], ll); txt = f"{IC[kind] if kind else ''}{tn} &middot; ~{max(1, round(km)):.0f} KM"
        w_ = len(tn) * 15 + 110 + (30 if kind else 0)
        if 80 < x < 1000 and 490 < y < 1370:
            for dy in (-34, 34, -70, 70):
                box = (x - w_ / 2, y + dy - 20, x + w_ / 2, y + dy + 20)
                if free(*box): placed.append(box); out.append(f'<div class="rl town {kind}" style="left:{min(max(x, w_ / 2 + 20), 1060 - w_ / 2):.0f}px;top:{y + dy:.0f}px">{txt}</div>'); break
        else:
            ang = math.atan2(y - zy, x - zx); ex = zx + math.cos(ang) * 2000; ey = zy + math.sin(ang) * 2000
            fx0, fy0, fx1, fy1 = 70, 510, 1010, 1360
            sc_ = min([v for v in [((fx1 - zx) / (ex - zx) if ex > zx else (fx0 - zx) / (ex - zx) if ex < zx else 9e9), ((fy1 - zy) / (ey - zy) if ey > zy else (fy0 - zy) / (ey - zy) if ey < zy else 9e9)] if v > 0])
            px, py = zx + (ex - zx) * sc_, zy + (ey - zy) * sc_
            deg = math.degrees(ang)
            for tries in range(8):
                box = (px - w_ / 2 - 30, py - 22, px + w_ / 2 + 30, py + 22)
                if free(*box): break
                py += 50 if py < 1300 else -50
            placed.append(box)
            px = min(max(px, w_ / 2 + 50), 1030 - w_ / 2)
            out.append(f'<div class="rl edge {kind}" style="left:{px:.0f}px;top:{py:.0f}px"><b style="transform:rotate({deg:.0f}deg)">&#10148;</b>{txt}</div>')
    if k in LM:
        tn, img, cap = LM[k]; ll = [t_[1] for t_ in towns if t_[0] == tn][0]; km = hav(a[2], ll)
        x, y = scr(wp(*ll), tz); side = "r" if x < 540 else "l"
        out.append(f'<div class="lmk {side}"><img src="assets/img/{img}.jpg"/><div><b>{cap}</b><span>~{max(1, round(km)):.0f} KM DOOR</span></div></div>')
    H.append(f'<div class="rls" id="rls_{k}">' + "".join(out) + '</div>')
    fo = until - .3
    J.append(f'tl.to("#ref_{k}", {{opacity:1, duration:.4}}, {tz - .1:.2f}); tl.to("#ref_{k} .rd", {{strokeDashoffset:0, duration:.9, ease:"power2.out"}}, {tz:.2f}); tl.fromTo("#ref_{k}", {{opacity:1}}, {{opacity:0, duration:.5, immediateRender:false}}, {fo:.2f});'
             f'tl.fromTo("#rls_{k} .lmk", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.4, ease:"back.out(2)", immediateRender:false}}, {tz + .9:.2f}); tl.fromTo("#rls_{k} .lmk", {{opacity:1}}, {{opacity:0, duration:.25, immediateRender:false}}, {fo:.2f}); tl.set("#rls_{k} .lmk", {{opacity:0}}, 0);'
             f'tl.fromTo("#rls_{k} .rl", {{opacity:0, y:12}}, {{opacity:1, y:0, duration:.3, stagger:.08, ease:"power2.out", immediateRender:false}}, {tz + .3:.2f}); tl.fromTo("#rls_{k} .rl", {{opacity:1}}, {{opacity:0, duration:.25, immediateRender:false}}, {fo:.2f}); tl.set("#rls_{k} .rl", {{opacity:0}}, 0);')

def district_on(nm, t0, arr, t_leave):
    dn = nm.replace("-", "_"); ks = [a for a in IA if a[3] == nm]; c, w = dview(nm)
    J.append(f'tl.to("#dz_{dn}", {{opacity:1, duration:.5}}, {t0 + .3:.2f}); tl.to("#dz_{dn}", {{fillOpacity:.55, duration:.7}}, {arr - .5:.2f}); tl.to("#dz_{dn}", {{fillOpacity:.18, duration:.6}}, {t_leave:.2f});')
    lo, la = DG[nm]["properties"]["label"]; lp = (c[0], wp(la, lo)[1]); fs = min(w / 8.5, w * .78 / (len(nm) * .52))
    names = " &#183; ".join(a[1] for a in ks)
    SVG.append(f'<g class="dname" id="dn_{dn}" style="opacity:0"><text x="{lp[0]:.0f}" y="{lp[1]:.0f}" text-anchor="middle" font-family="Anton" font-size="{fs:.0f}" letter-spacing="{fs * .05:.0f}" fill="#fff" stroke="#0b2a3a" stroke-width="{fs * .06:.0f}" paint-order="stroke" style="filter:drop-shadow(0 0 {fs * .1:.0f}px rgba(0,0,0,.5))">{nm.upper()}</text>'
               f'<text x="{lp[0]:.0f}" y="{lp[1] + fs * .55:.0f}" text-anchor="middle" font-family="Mont" font-weight="800" font-size="{min(fs * .22, w * .82 / (len(names.replace(" &#183; ", " . ")) * .78)):.0f}" letter-spacing="{fs * .02:.1f}" fill="#0b2a3a">{names}</text></g>')
    J.append(f'tl.fromTo("#dn_{dn}", {{opacity:0, y:{fs * .2:.0f}}}, {{opacity:1, y:0, duration:.5, ease:"power3.out", immediateRender:false}}, {arr - .4:.2f}); tl.fromTo("#dn_{dn}", {{opacity:1}}, {{opacity:0, duration:.4, immediateRender:false}}, {t_leave:.2f});')
    for i, a in enumerate(ks):
        waves(a[0], arr - .2 + i * .12, t_leave + .3, w / 14)
    sfx("whoosh", t0, .3); sfx("impact-bass-1", arr - .3, .3)

# ---- schedule beats ----
sched = []; tcur = S(1) - .7
for i, a in enumerate(IA):
    k = a[0]
    if FIRST[a[3]] == k:
        c, w = dview(a[3]); t0 = max(S(a[6]) - 1.1, tcur)
        arr = zoom(t0, c, w); t0 = CAMS[-1][0]
        sched.append(("d", a[3], t0, arr)); tcur = arr + DH
        ta = max(wt(a[6], a[7]) - .3, tcur)
    else:
        ta = max(wt(a[6], a[7]) - 1.0, tcur)
    c, w = acam(k); arr = zoom(ta, c, w); ta = CAMS[-1][0]
    sched.append(("a", k, ta, arr)); tcur = arr + MH
T_OUT = max(S(9) - .4, tcur)
if not VOICE:
    json.dump({f"{x[6]}|{x[7]}": round(t0_ + (.3 if FIRST[x[3]] == x[0] else 1.0), 2) for x in IA for kd, kk, t0_, arr_ in sched if kd == "a" and kk == x[0]} | {"8|__end": round(T_OUT + .1, 2)}, open("anchors.json", "w"))
for j, (kind, key, t0, arr) in enumerate(sched):
    nb = sched[j + 1][2] if j + 1 < len(sched) else T_OUT
    if kind == "d":
        nm = key; last_a = max(jj for jj, b in enumerate(sched) if b[0] == "a" and [x for x in IA if x[0] == b[1]][0][3] == nm)
        lv = sched[last_a + 1][2] if last_a + 1 < len(sched) else T_OUT
        district_on(nm, t0, arr, nb)
        J.append(f'tl.fromTo("#dz_{nm.replace("-", "_")}", {{opacity:1}}, {{opacity:0, duration:.6, immediateRender:false}}, {lv:.2f});')
        continue
    a = [x for x in IA if x[0] == key][0]; k = key
    lag = arr - wt(a[6], a[7])
    if lag > .6: print("WARN visual lags speech", k, round(lag, 2))
    J.append(f'tl.to("#pt_{k}", {{opacity:1, duration:.6}}, {arr - .55:.2f}); tl.fromTo("#pt_{k}", {{opacity:1}}, {{opacity:0, duration:.6, immediateRender:false}}, {nb + .1:.2f});')
    hx, hy = IP[k]
    J.append(f'tl.set("#hole", {{attr:{{cx:{hx:.0f}, cy:{hy:.0f}, r:{ZR * 1.6:.0f}}}}}, {t0 + .2:.2f}); tl.to("#dimr", {{attr:{{"fill-opacity":.5}}, duration:.6}}, {arr - .3:.2f}); tl.to("#dimr", {{attr:{{"fill-opacity":0}}, duration:.4}}, {nb - .3:.2f});')
    J.append(f'tl.to("#zn_{k}", {{opacity:1, duration:.35}}, {arr - .1:.2f}); tl.fromTo("#zn_{k} .zr", {{attr:{{r:{ZR * .3:.0f}}}}}, {{attr:{{r:{ZR:.0f}}}, duration:.6, ease:"back.out(1.8)", immediateRender:false}}, {arr - .1:.2f}); tl.fromTo("#zn_{k}", {{opacity:1}}, {{opacity:0, duration:.4, immediateRender:false}}, {nb - .3:.2f});')
    J.append(f'tl.fromTo("#zn_{k} .zr", {{strokeWidth:5}}, {{strokeWidth:12, duration:.45, yoyo:true, repeat:3, immediateRender:false}}, {arr + .5:.2f});')
    waves(k, arr, nb - .3, ZR * 2.4)
    lab(f"zl_{k}", IP[k], a[1], arr + .1, nb, arr, dy=-int(ZR / AW * 1080) - 40, cls="big" + (" soon" if a[5] == "soon" else ""))
    card(a, t0 + .3, nb)
    sfx("whoosh", t0, .25); sfx("impact-bass-1", arr, .3)
    ref_labels(a, arr, nb)

J.append(f'tl.to("#base", {{filter:"grayscale(0.2) brightness(0.88)", duration:.8}}, {S(1) - .6:.2f}); tl.to("#base", {{filter:"grayscale(0) brightness(1)", duration:.8}}, {T_OUT:.2f});')
# ---------- 9 real estate: back to top view, all zones glow ----------
zoom(T_OUT, OV_C, OV_W)
for i, a in enumerate(IA):
    waves(a[0], CAMS[-1][0] + CAMS[-1][1] - .3 + i * .05, S(10) - .1, OV_W / 18)
H.append('<div id="flow"><span>INDUSTRY</span><i>&rarr;</i><span>NAUKRI</span><i>&rarr;</i><b>GHAR &amp; PLOT KI DEMAND &#9650;</b></div>')
J.append(f'tl.fromTo("#flow", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.4, ease:"power3.out"}}, {CAMS[-1][0] + CAMS[-1][1] - .2:.2f}); tl.fromTo("#flow b", {{opacity:0, x:30}}, {{opacity:1, x:0, duration:.4, immediateRender:false}}, {max(wt(9, "ghar") - .1, CAMS[-1][0] + CAMS[-1][1] + .3):.2f}); tl.to("#flow", {{opacity:0, duration:.3}}, {S(10) - .1:.2f});')
sfx("riser", S(9), .3)

# ---------- 10 CTA ----------
H.append('<div id="cta"><b>AAPKE ZILE MEIN KAUNSA INDUSTRIAL AREA AA RAHA HAI?</b><span>COMMENT KARO</span></div>')
J.append(f'tl.to("#dim", {{opacity:.5, duration:.3}}, {S(10):.2f}); tl.fromTo("#cta", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.45, ease:"power3.out"}}, {S(10):.2f}); tl.to("#cta span", {{scale:1.06, duration:.4, yoyo:true, repeat:3}}, {wt(10, "Comment"):.2f});')
sfx("sparkle", wt(10, "Comment"), .3)

J.insert(0, cam_js())
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
    nx = PH[n + 1]["s"] if n + 1 < len(PH) else END; pos = 0
    for j, c in enumerate(chunks):
        st_, en_ = tchar(n, pos), tchar(n, pos + len(c)); pos += len(c) + 1
        a_ = max(.02, st_ if j else st_ - .04); b_ = (min(en_ + .25, nx - .08) if j == len(chunks) - 1 else en_ - .03)
        H.append(f'<div class="cp" id="cp{ci}"><div>{hl(c)}</div></div>')
        J.append(f'tl.fromTo("#cp{ci}", {{opacity:0, scale:.88}}, {{opacity:1, scale:1, duration:.1}}, {a_:.2f}); tl.to("#cp{ci}", {{opacity:0, duration:.04}}, {b_ - .04:.2f});')
        ci += 1
if os.path.exists(f"{P}/assets/face.mp4"):
    H.append('<video id="face" class="clip" src="assets/face.mp4" data-start="0" data-duration="1.0" data-track-index="2" muted playsinline></video>')
    J.append('tl.set("#face", {opacity:1}, 0); tl.to("#face", {opacity:0, scale:1.06, duration:.12}, .8);')
H.append('<div id="cred">Sources: RIICO MIS (June 2026), RIICO DAP 2025, Rising Rajasthan &middot; zones indicative, locations &amp; distances approximate (straight-line) &middot; roads/rail: Natural Earth &middot; Imagery: Sentinel-2 cloudless (EOX) &middot; photos: Wikimedia Commons (CC BY-SA)</div>')

CSS = """@font-face{font-family:Anton;src:url(assets/fonts/anton.woff2)}@font-face{font-family:Mont;font-weight:700;src:url(assets/fonts/mont700.woff2)}@font-face{font-family:Mont;font-weight:800;src:url(assets/fonts/mont800.woff2)}@font-face{font-family:Mont;font-weight:900;src:url(assets/fonts/mont900.woff2)}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#0c0b0a}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif}.y{color:#111;background:#F2B23E;border-radius:6px;padding:0 6px}
#world{position:absolute;inset:0;width:1080px;height:1920px}
#dim{position:absolute;inset:0;background:#000;opacity:0;z-index:5;pointer-events:none}
#face{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:40}
#cred{position:absolute;left:40px;right:40px;top:1660px;text-align:center;font:700 17px Mont;color:rgba(255,255,255,.7);z-index:20;text-shadow:0 2px 6px #000}
.ml{position:absolute;opacity:0;translate:-50% -50%;white-space:nowrap;z-index:8}
.ml.sm{padding:4px 10px;border-radius:4px;background:rgba(10,10,12,.85);border:1px solid #3FE0FF;color:#fff;font:800 20px Mont;letter-spacing:.06em}
.ml.big{padding:10px 24px;border-radius:4px;background:#FFB020;color:#111;font:400 54px/1 Anton;letter-spacing:.04em;box-shadow:0 10px 30px rgba(0,0,0,.55)}
.ml.big.soon{background:#FF7A45;color:#111}
#hook{position:absolute;left:50px;right:50px;top:110px;z-index:16;text-align:center;padding:22px 20px;border-radius:8px;border:1.5px solid #C9A24A;background:linear-gradient(135deg,rgba(14,12,9,.9),rgba(34,27,18,.9))}
#hook small{display:block;font:700 30px Mont;letter-spacing:.3em;color:#F3E6C8}#hook b{display:block;margin-top:8px;font:400 92px/1 Anton;background:linear-gradient(180deg,#F7E3A8,#C9A24A);-webkit-background-clip:text;color:transparent}
#hook span{display:inline-block;margin-top:14px;padding:8px 22px;border-radius:4px;background:#C9A24A;color:#111;font:900 30px Mont;letter-spacing:.14em}
#ns{position:absolute;right:40px;top:520px;opacity:0;z-index:12;display:flex;flex-direction:column;align-items:center;gap:8px}#ns b{padding:6px 14px;border-radius:4px;background:rgba(10,10,12,.85);border:1px solid #3FE0FF;color:#3FE0FF;font:800 22px Mont;letter-spacing:.2em}
#ns i{width:8px;height:300px;border-radius:4px;background:linear-gradient(#3FE0FF,#FF3DCB);transform-origin:50% 0}
.card{position:absolute;left:50px;right:50px;top:120px;opacity:0;z-index:15;text-align:center;padding:20px 24px;border-radius:8px;border:1.5px solid #C9A24A;background:linear-gradient(135deg,rgba(14,12,9,.92),rgba(34,27,18,.92))}
.card small{display:inline-flex;align-items:center;gap:12px;font:700 26px Mont;letter-spacing:.22em;color:#F3E6C8}.card em{font-style:normal;padding:3px 10px;border-radius:3px;background:#3CE65A;color:#111;font:900 20px Mont;letter-spacing:.1em}.card em.s{background:#FF9A3C}
.card b{display:block;margin-top:8px;font:400 76px/1 Anton;background:linear-gradient(180deg,#F7E3A8,#C9A24A);-webkit-background-clip:text;color:transparent}.card span{display:block;margin-top:8px;font:800 28px Mont;letter-spacing:.1em;color:#A8D8F0}
.card .conn{display:flex;flex-wrap:wrap;justify-content:center;gap:10px;margin-top:14px}.card .conn i{display:inline-flex;align-items:center;gap:8px;padding:6px 14px;border-radius:30px;border:1px solid rgba(201,162,74,.7);background:rgba(255,255,255,.06);font:800 21px Mont;font-style:normal;color:#F3E6C8;letter-spacing:.04em}
.card .conn svg,.rl svg{width:24px;height:24px;flex:none;color:#FFC42E}.rl.town.rail svg,.rl.edge.rail svg{color:#111}.rl.edge svg{color:#FFC42E}.rl.town.air svg{color:#0a6fb0}
.rl.town{display:flex;align-items:center;gap:6px}.rls{position:absolute;inset:0;z-index:9;pointer-events:none}.rl{position:absolute;translate:-50% -50%;white-space:nowrap;opacity:0}
.rl.road{padding:4px 12px;border-radius:4px;background:#FFC42E;color:#111;font:900 24px Mont;letter-spacing:.06em;box-shadow:0 4px 12px rgba(0,0,0,.6)}
.rl.town{padding:5px 12px;border-radius:4px;background:rgba(255,255,255,.95);color:#111;font:800 22px Mont;letter-spacing:.04em;box-shadow:0 4px 12px rgba(0,0,0,.6)}
.rl.edge{display:flex;align-items:center;gap:8px;padding:6px 14px;border-radius:30px;background:rgba(10,10,12,.88);border:1.5px solid #fff;color:#fff;font:800 22px Mont;letter-spacing:.04em}.rl.edge b{font-style:normal;color:#FFC42E;font-size:24px;display:inline-block}.rl.edge.rail svg{color:#fff}
.lmk{position:absolute;top:1080px;width:420px;opacity:0;padding:8px 8px 10px;border-radius:8px;background:rgba(10,10,12,.92);border:2px solid #fff;box-shadow:0 18px 40px rgba(0,0,0,.7)}.lmk.l{left:40px}.lmk.r{right:40px}
.lmk img{display:block;width:100%;height:230px;object-fit:cover;border-radius:4px}.lmk b{display:block;margin-top:8px;font:800 22px Mont;color:#fff}.lmk span{display:block;margin-top:2px;font:900 20px Mont;color:#FFC42E;letter-spacing:.08em}
.dist{position:absolute;left:0;right:0;top:300px;margin:0 auto;width:max-content;max-width:980px;opacity:0;z-index:15;text-align:center;padding:18px 30px;border-radius:8px;background:rgba(10,10,12,.88);border:2px solid #FFD36B}
.dist b{display:block;font:400 92px/1 Anton;color:#FFD36B;letter-spacing:.03em}.dist span{display:block;margin-top:10px;font:800 26px/1.35 Mont;color:#fff;letter-spacing:.06em}
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
