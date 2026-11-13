"""Rajasthan upcoming industrial areas — 3D map tour. Pin positions approximate. Sources: RIICO MIS Jun-2026, RIICO DAP 2025, Rising Rajasthan brochure."""
import json, math, os, random
P = "proj"
LINES = [
    "Rajasthan mein pichhle do saal mein 30 se zyada naye industrial areas khule hain, aur aur bhi khulne wale hain. Jahan factory, wahan naukri, aur wahan ghar ki demand.",
    "Jaipur mein Kunjbiharipura, Bagru ke paas, auto aur heavy engineering ke liye. Bichoon, Phulera freight corridor ke paas. Hukkan-Nimodia, Jaipur-Kota highway par. Aur Tonk Road par naya Fintech Park, IT aur AI companies ke liye.",
    "Bhiwadi mein Salarpur, Honda, Hero aur Maruti ke paas.",
    "Jodhpur mein Boranada Extension aur Medical Device Park.",
    "Balotra mein Petro Zone, refinery ke bilkul paas.",
    "Bhilwara mein Rupaheli Textile Park, Chittorgarh mein glass aur ceramic ke liye Soniyana, Bikaner mein Gajner, aur Kota mein Gundi Fatehpur.",
    "Real estate ka funda simple hai: jahan industry, wahan naukri, aur jahan naukri, wahan ghar aur plot ki demand.",
    "Aapke zile mein kaunsa industrial area aa raha hai? Comment karo.",
]
VOICE = os.path.exists("rec/phrases.json")
if VOICE: PH = json.load(open("rec/phrases.json"))
else:
    PH = []; t = .3
    for l in LINES:
        d = len(l) / 15 + .15
        if not PH: d += 2.5     # hold the overview so viewers can screenshot
        PH.append({"s": round(t, 2), "e": round(t + d, 2), "t": l}); t += d + .3
def S(k): return PH[k]["s"]
def E(k): return PH[k]["e"]
def wt(k, w):
    t = PH[k]["t"]; i = t.lower().find(w.lower()); assert i >= 0, (k, w)
    return S(k) + (E(k) - S(k)) * i / len(t)
END = round(E(7) + 1.0, 2)
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
    ("rup", "RUPAHELI TEXTILE PARK", (25.93, 74.62), "Bhilwara", "ALLOTMENT SHURU", "&#129525;", 5, "Rupaheli", "new"),
    ("son", "SONIYANA", (25.13, 74.52), "Chittorgarh", "GLASS &middot; CERAMIC", "&#129346;", 5, "Soniyana", "new"),
    ("gaj", "GAJNER", (27.95, 73.06), "Bikaner", "CERAMIC PARK", "&#127994;", 5, "Gajner", "new"),
    ("gun", "GUNDI FATEHPUR", (24.84, 75.95), "Kota", "STONE &middot; AGRO", "&#129704;", 5, "Gundi", "new"),
]
IP = {k: wp(*ll) for k, _, ll, *_ in IA}
for k, nm, ll, dist, tag, ic, li, kw, stt in IA:
    x, y = IP[k]; col = ORG if stt == "soon" else GOLD
    SVG.append(f'<g class="pin" id="pn_{k}"><circle class="halo" cx="{x:.0f}" cy="{y:.0f}" r="{U * 14:.0f}" style="fill:{col};fill-opacity:.25;stroke:{col};stroke-width:2;vector-effect:non-scaling-stroke"/>'
               f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{U * 9:.0f}" style="fill:#F7E3A8;stroke:#fff;stroke-width:2.5;vector-effect:non-scaling-stroke"/></g>')
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
    k = a[0]; t = .5 + i * .09
    J.append(f'tl.fromTo("#pn_{k}", {{opacity:0}}, {{opacity:1, duration:.2}}, {t:.2f}); tl.fromTo("#pn_{k} .halo", {{attr:{{r:{U * 6:.0f}}}}}, {{attr:{{r:{U * 14:.0f}}}, duration:.5, ease:"back.out(2)", immediateRender:false}}, {t:.2f});'
             f'tl.to("#fb_{k}", {{scaleY:1, rotationX:-90, duration:.4, ease:"back.out(2)"}}, {t:.2f}); tl.fromTo("#ov_{k}", {{opacity:0}}, {{opacity:1, duration:.25, immediateRender:false}}, {t + .1:.2f}); tl.to("#ov_{k}", {{opacity:0, duration:.25}}, {S(1) - .4:.2f});')
    sfx("click-soft", t, .15)
J.append(f'tl.to("#dmic", {{strokeDashoffset:0, duration:1.2, ease:"power2.inOut"}}, 1.2);')
H.append('<div id="hook"><small>RAJASTHAN KE</small><b>NAYE INDUSTRIAL AREAS</b><span>&#128278; SAVE KAR LO</span></div>')
J.append(f'tl.fromTo("#hook", {{opacity:0, scale:1.1}}, {{opacity:1, scale:1, duration:.4, ease:"power3.out"}}, 0); tl.fromTo("#hook span", {{opacity:0, scale:1.4}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)", immediateRender:false}}, 1.6); tl.to("#hook span", {{scale:1.08, duration:.35, yoyo:true, repeat:5}}, 2.0); tl.to("#hook", {{opacity:0, y:-30, duration:.3}}, {S(1) - .3:.2f});')
lux(0, "<b>30+</b> NAYE &middot; AUR AA RAHE HAIN", wt(0, "30") - .1, wt(0, "Jahan") - .1, 200, 1300)
H.append('<div id="flow"><span>FACTORY</span><i>&rarr;</i><span>NAUKRI</span><i>&rarr;</i><b>GHAR KI DEMAND</b></div>')
J.append(f'tl.fromTo("#flow", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.4, ease:"power3.out"}}, {wt(0, "Jahan") - .1:.2f}); tl.to("#flow", {{opacity:0, duration:.3}}, {S(1) - .3:.2f});')
sfx("impact-bass-1", 0, .45); sfx("riser", .5, .3)

# ---------- tour ----------
def card(k, t, until):
    a = [x for x in IA if x[0] == k][0]
    soon = '<em>COMING SOON</em>' if a[8] == "soon" else '<em class="n">NAYA</em>'
    H.append(f'<div class="card" id="cd_{k}"><i>{a[5]}</i><div><small>{a[3].upper()} {soon}</small><b>{a[1]}</b><span>{a[4]}</span></div></div>')
    J.append(f'tl.fromTo("#cd_{k}", {{opacity:0, x:-60}}, {{opacity:1, x:0, duration:.4, ease:"power3.out"}}, {t:.2f}); tl.fromTo("#cd_{k} i", {{scale:2, rotation:-15}}, {{scale:1, rotation:0, duration:.45, ease:"back.out(2.5)"}}, {t:.2f}); tl.to("#cd_{k}", {{opacity:0, x:40, duration:.25}}, {until - .25:.2f});')
    J.append(f'tl.fromTo("#pn_{k} .halo", {{attr:{{r:{U * 8:.0f}}}}}, {{attr:{{r:{U * 22:.0f}}}, duration:.8, repeat:2, ease:"power2.out", immediateRender:false}}, {t:.2f}); tl.fromTo("#ov_{k}", {{opacity:0}}, {{opacity:1, duration:.25, immediateRender:false}}, {t:.2f}); tl.to("#ov_{k}", {{opacity:0, duration:.25}}, {until - .2:.2f});')
    sfx("pop", t, .3)
STEPS = []   # (key, line)
for a in IA: STEPS.append((a[0], a[6]))
# line 1 Jaipur cluster: zoom into Jaipur, show 4 one by one
rx, sc, x, y = focus(wp(26.78, 75.6), 40, 4.2, 1050)
plane(S(1) - .3, rx, sc, x, y, 1.1); dist_on("Jaipur", S(1), S(2) - .1); sfx("whoosh", S(1) - .3, .3)
jk = [a for a in IA if a[6] == 1]
for i, a in enumerate(jk):
    t = wt(1, a[7]) - .1; nxt = wt(1, jk[i + 1][7]) - .1 if i + 1 < len(jk) else S(2)
    card(a[0], t, nxt)
for li in (2, 3, 4):
    for a in [x for x in IA if x[6] == li]:
        rx, sc, x, y = focus(IP[a[0]], 40, 3.2, 1050); plane(S(li) - .35, rx, sc, x, y, 1.0); sfx("whoosh", S(li) - .35, .3)
        dist_on(a[3], S(li), S(li + 1) - .1); card(a[0], S(li) + .2, S(li + 1))
J.append(f'tl.to("#dmic", {{strokeOpacity:.8, duration:.4}}, {S(2):.2f}); tl.to("#dmic", {{strokeOpacity:.35, duration:.4}}, {S(3):.2f});')
lk = [a for a in IA if a[6] == 5]
for i, a in enumerate(lk):
    t = wt(5, a[3]) - .25; nxt = wt(5, lk[i + 1][3]) - .25 if i + 1 < len(lk) else S(6)
    rx, sc, x, y = focus(IP[a[0]], 40, 3.0, 1050); plane(t - .3, rx, sc, x, y, .7); sfx("whoosh-short", t - .3, .25)
    dist_on(a[3], t, nxt - .1); card(a[0], t + .1, nxt)

# ---------- 6 real estate: back to overview, rings ----------
plane(S(6) - .3, *OV, 1.1)
for i, a in enumerate(IA):
    t = S(6) + .4 + i * .06
    J.append(f'tl.fromTo("#pn_{a[0]} .halo", {{attr:{{r:{U * 10:.0f}}}, fillOpacity:.35}}, {{attr:{{r:{U * 80:.0f}}}, fillOpacity:0, duration:1.1, repeat:2, ease:"power2.out", immediateRender:false}}, {t:.2f});')
H.append('<div id="flow2"><span>INDUSTRY</span><i>&rarr;</i><span>NAUKRI</span><i>&rarr;</i><b>GHAR &amp; PLOT KI DEMAND &#9650;</b></div>')
J.append(f'tl.fromTo("#flow2", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.4, ease:"power3.out"}}, {S(6):.2f}); tl.fromTo("#flow2 b", {{opacity:0, x:30}}, {{opacity:1, x:0, duration:.4, immediateRender:false}}, {wt(6, "ghar") - .1:.2f}); tl.to("#flow2", {{opacity:0, duration:.3}}, {S(7) - .1:.2f});')
sfx("riser", S(6), .3)

# ---------- 7 CTA ----------
H.append('<div id="cta"><b>AAPKE ZILE MEIN KAUNSA INDUSTRIAL AREA AA RAHA HAI?</b><span>COMMENT KARO</span></div>')
J.append(f'tl.to("#dim", {{opacity:.5, duration:.3}}, {S(7):.2f}); tl.fromTo("#cta", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.45, ease:"power3.out"}}, {S(7):.2f}); tl.to("#cta span", {{scale:1.06, duration:.4, yoyo:true, repeat:3}}, {wt(7, "Comment"):.2f});')
sfx("sparkle", wt(7, "Comment"), .3)

# ---------- captions ----------
HI = ["30 se zyada", "Kunjbiharipura", "Bichoon", "Hukkan-Nimodia", "Fintech Park", "Salarpur", "Boranada Extension", "Medical Device Park", "Petro Zone", "Rupaheli Textile Park", "Soniyana", "Gajner", "Gundi Fatehpur",
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
.cp{position:absolute;left:40px;right:40px;top:1440px;text-align:center;opacity:0;z-index:35}
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
