"""Zameen kharidne se pehle 10 baatein (derived from the 1-crore reel) — was: Pehla 1 crore Jaipur mein kahan? — preference-based reel (zones are illustrative rings, not survey boundaries)."""
import json, math, os
P = "proj"
ASP = json.load(open("aspects.json"))
ORDER = [1, 3, 4, 7, 9, 6, 5, 2, 8, 10]
POS = {o: i + 1 for i, o in enumerate(ORDER)}
NUMW = ["Ek", "Do", "Teen", "Chaar", "Paanch", "Chhe", "Saat", "Aath", "Nau", "Das"]
BASE = ['jamabandi nikaalo. Apna Khata par dekho zameen sach mein bechne wale ke naam par hai ya nahi.', 'sauda power of attorney se ho raha hai? Check karo POA asli hai, maalik zinda hai, aur mukar toh nahi gaya.', 'zameen virasat ki hai toh saare waris ki sahmati lo, aur namantaran hua hai ya nahi dekho.', 'pichli saari registries ki chain dekho. Beech ka koi link missing nahi hona chahiye.', 'ek hi plot do logon ko bik jaata hai. Registration office se pata karo pehle koi registry toh nahi hui.', 'zameen par loan, girvi ya court case toh nahi, yeh confirm karo.', 'kagaz ka area site par naap ke milao, aur dekho kisi ka kabza toh nahi.', 'kheti ki zameen hai toh 90-A conversion, aur colony hai toh layout approval check karo.', 'plot tak pakka rasta hai? Aur master plan mein woh area residential hai ya nahi?', 'bada bayana cash mein mat do. Agreement likhit mein, aur payment bank se.']
LINES = ['Zameen kharidne se pehle in 10 baaton ka dhyaan zaroor rakhein, warna paisa phas sakta hai.'] + [f"{NUMW[i]}, {BASE[o - 1]}" for i, o in enumerate(ORDER)] + ['Main koi bhi plot suggest karne se pehle yeh sab khud check karta hoon. Jaipur mein zameen dhundh rahe ho? Comment karo Plot.']
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
END = round(E(11) + 1.3, 2)
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
PXKM = 256 * 2 ** 13 / 40075 / math.cos(math.radians(26.9))
CEN = wp(26.9124, 75.7873)
def km(b, d): return (CEN[0] + math.sin(math.radians(b)) * d * PXKM, CEN[1] - math.cos(math.radians(b)) * d * PXKM)
AGRI, FAR, NEAR = "#E0A040", "#3D8BFF", "#3CE65A"
def from11(p): return ((p[0] + 1450 * 256) * 4 - 5791 * 256, (p[1] + 860 * 256) * 4 - 3466 * 256)
def pdz(pts): return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
JZ = json.load(open("data/jda_zones_world.json"))
REG = [from11(p) for p in JZ["region"]]
NEWZ = ["15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25"]
ZN = {"15": "Shahpura", "16": "Chomu", "17": "Jalsoo", "18": "Jobner", "19": "Mozmabad", "20": "Dudu", "21": "Phagi", "22": "Madhorajpura", "23": "Chaksu", "24": "Bassi", "25": "Andhi"}
CB = json.load(open("data/jaipur_boundary.geojson"))["features"][0]["geometry"]["coordinates"][0]
CITY = [wp(la, lo) for lo, la in CB[::2]]
SVG.append(f'<defs><mask id="outside" maskUnits="userSpaceOnUse" x="-900000" y="-900000" width="2000000" height="2000000"><rect x="-900000" y="-900000" width="2000000" height="2000000" fill="#fff"/><path d="{pdz(REG)}" fill="#000"/></mask></defs>')
# agri: everything outside the JDA region (illustrative)
SVG.append(f'<rect id="zag" x="-900000" y="-900000" width="2000000" height="2000000" mask="url(#outside)" style="fill:{AGRI};opacity:0"/>')
# far: band just outside the JDA region edge (illustrative)
SVG.append(f'<path id="zfa" d="{pdz(REG)}" mask="url(#outside)" style="fill:none;stroke:{FAR};stroke-width:{18 * PXKM:.0f};stroke-linejoin:round;opacity:0"/>')
# near: the new JDA zones (2025)
for k in NEWZ:
    SVG.append(f'<path class="nz" id="nz{k}" d="{pdz([from11(p) for p in JZ["zones"][k]["poly"]])}" style="fill:{NEAR};fill-opacity:.45;stroke:#fff;stroke-width:2.5;vector-effect:non-scaling-stroke;opacity:0"/>')
SVG.append(f'<path id="jreg" d="{pdz(REG)}" style="fill:none;stroke:#fff;stroke-width:4;stroke-dasharray:14 10;vector-effect:non-scaling-stroke;opacity:0"/>')
SVG.append(f'<path id="zco" d="{pdz(CITY)}" style="fill:#fff;fill-opacity:0;stroke:#fff;stroke-width:4;vector-effect:non-scaling-stroke;stroke-linejoin:round;opacity:0"/>')
# highways (OSM NH lines) + state / city roads (approx.)
NH = json.load(open("data/nh_jaipur.json"))
def bearing(p): return math.degrees(math.atan2(-(p[1] - CEN[1]), p[0] - CEN[0]))
RD = {k: [] for k in ["nh48", "nh52", "nh21", "ring"]}
for f in NH:
    nm = (f["name"] or "").strip()
    for L in f["lines"]:
        pts = [wp(la, lo) for lo, la in L]
        mx = sum(p[0] for p in pts) / len(pts); my = sum(p[1] for p in pts) / len(pts)
        if math.hypot(mx - CEN[0], my - CEN[1]) / PXKM > 70: continue
        if nm == "NH 148C": RD["ring"].append(pts)
        elif nm.startswith("NH 48"): RD["nh48"].append(pts)
        elif nm == "NH 52": RD["nh52"].append(pts)
        elif nm == "NH 21": RD["nh21"].append(pts)
WPT = {"kalwar": [(26.948, 75.760), (26.975, 75.66), (26.972, 75.50), (26.972, 75.388)],
       "sirsi": [(26.928, 75.735), (26.948, 75.680), (26.962, 75.620), (26.975, 75.560)],
       "diggi": [(26.826, 75.790), (26.76, 75.735), (26.66, 75.65), (26.570, 75.563)]}
for k, v in WPT.items(): RD[k] = [smooth([wp(*p) for p in v], 8)]
RCOL = {"nh48": GOLD, "nh52": GOLD, "nh21": GOLD, "ring": "#3CE65A", "kalwar": "#FFFFFF", "sirsi": "#FFFFFF", "diggi": "#FFFFFF"}
for k, segs in RD.items():
    for pts in segs:
        d_ = pd(pts); w_ = 7 if k.startswith("nh") else 5
        SVG.append(f'<path class="r_{k} rr" d="{d_}" pathLength="1" style="fill:none;stroke:{RCOL[k]};stroke-width:{w_ * 3};stroke-opacity:.3;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>'
                   f'<path class="r_{k} rr" d="{d_}" pathLength="1" style="fill:none;stroke:{RCOL[k]};stroke-width:{w_};vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>')
SVG.append('<rect id="dim" x="-900000" y="-900000" width="2000000" height="2000000" style="fill:#000;opacity:0"/>')

# ---------- cameras ----------
def bbr(rings): return [wp(la, lo) for r in rings for lo, la in r]
IND_C, IND_W = fitb(bbr(BD["india"]), 640, 1420, 1.08)
RAJ_C, RAJ_W = fitb(bbr(BD["raj"]), 700, 1380, 1.1)
JP_C, JP_W = fitb(bbr(BD["jaipur"]), 700, 1380, 1.1)
def ccam(rkm, cy=1120): w = 2 * rkm * PXKM * 1.08; return (CEN[0], CEN[1] - (cy - 960) * w / 1080), w
def fitp(pts, top, bot, pad): return fitb(pts, top, bot, pad)
CITYC = fitp(CITY, 720, 1400, 1.2); REGC = fitp(REG, 500, 1420, 1.08); AGC = fitp(REG, 500, 1420, 1.5); MID = ccam(30); ROADC = ccam(38)
J.append(f'tl.set("#world", {{attr:{{viewBox:"{vb(RAJ_C, RAJ_W * 1.15)}"}}}}, 0);')
J.append('const VB = document.getElementById("world"); function setDots(w){ document.querySelectorAll(".dc").forEach(e=>e.setAttribute("r", w/90)); document.querySelectorAll(".dg").forEach(e=>e.setAttribute("r", w/40)); document.querySelectorAll(".mvc").forEach(e=>e.setAttribute("r", w/70)); document.querySelectorAll(".mvg").forEach(e=>e.setAttribute("r", w/26)); }'
         'function zoomTo(t, c0, w0, c1, w1, d){ const o = {z:0}; tl.to(o, {z:1, duration:d, ease:"power2.inOut", onUpdate:()=>{ const w = Math.exp(Math.log(w0) + (Math.log(w1) - Math.log(w0)) * o.z); const f = Math.abs(w0 - w1) < 1e-6 ? o.z : (w0 - w) / (w0 - w1); const cx = c0[0] + (c1[0] - c0[0]) * f, cy = c0[1] + (c1[1] - c0[1]) * f; const h = w * 1920 / 1080; VB.setAttribute("viewBox", (cx - w / 2) + " " + (cy - h / 2) + " " + w + " " + h); setDots(w); }}, t); }')
CAMS.append((0, 0, RAJ_C, RAJ_W * 1.15))
zoom(0, RAJ_C, RAJ_W, .5); zoom(1.0, JP_C, JP_W, .9); zoom(2.0, *CITYC, 1.0)
zoom(S(1) - .2, *AGC, .8); zoom(S(3) - .2, *REGC, .8); zoom(S(4) - .2, *ROADC, .8); zoom(S(6) - .3, *REGC, .8)
J.append('tl.set("#bind", {opacity:0}, 0); tl.to("#braj", {opacity:1, fillOpacity:.75, duration:.3}, .05); tl.to("#braj", {fillOpacity:.1, duration:.3}, 1.0);'
         'tl.to("#bjp", {opacity:1, fillOpacity:.6, duration:.3}, 1.0); tl.to("#bjp", {fillOpacity:0, opacity:.4, duration:.4}, 2.0); tl.to("#braj", {opacity:0, duration:.3}, 2.0); tl.to("#bjp", {opacity:0, duration:.3}, 3.0);')
sfx("whoosh", 1.0, .3); sfx("whoosh", 2.0, .3)

def lab(i, p, text, t, until, at, dx=0, dy=0, cls="", style=""):
    x, y = scr(p, at); H.append(f'<div class="ml {cls}" id="{i}" style="left:{min(max(x + dx, 60 + len(text) * 11), 1020 - len(text) * 11):.0f}px;top:{y + dy:.0f}px;opacity:0;{style}">{text}</div>')
    J.append(f'tl.fromTo("#{i}", {{opacity:0, scale:.5}}, {{opacity:1, scale:1, duration:.25, ease:"back.out(2)", immediateRender:false}}, {t:.2f}); tl.fromTo("#{i}", {{opacity:1}}, {{opacity:0, duration:.2, immediateRender:false}}, {until - .2:.2f});')

# ---------- BACKGROUND (no map) ----------
H.append('<div id="bg"><div id="grid"></div><div id="glow1"></div><div id="glow2"></div><div id="vig"></div></div>')
J.append(f'tl.fromTo("#grid", {{backgroundPosition:"0px 0px"}}, {{backgroundPosition:"0px 1200px", duration:{END:.2f}, ease:"none"}}, 0);'
         f'tl.fromTo("#glow1", {{x:-200, y:0}}, {{x:300, y:500, duration:{END:.2f}, ease:"sine.inOut"}}, 0); tl.fromTo("#glow2", {{x:200, y:0}}, {{x:-300, y:-400, duration:{END:.2f}, ease:"sine.inOut"}}, 0);')
# progress bar
H.append('<div id="prog">' + "".join(f'<i id="pg{i}"><b></b></i>' for i in range(1, 11)) + '</div>')
J.append(f'tl.fromTo("#prog", {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:.3}}, {S(1) - .2:.2f}); tl.to("#prog", {{opacity:0, duration:.3}}, {S(11) - .1:.2f});')
for i in range(1, 11):
    J.append(f'tl.fromTo("#pg{i} b", {{scaleX:0}}, {{scaleX:1, duration:{S(i + 1) - S(i):.2f}, ease:"none"}}, {S(i):.2f});')

# ---------- 0 HOOK ----------
H.append('<div id="title"><small>ZAMEEN KHARIDNE SE PEHLE</small><b>IN 10 BAATON KA<br/>DHYAAN RAKHEIN</b></div>')
J.append(f'tl.fromTo("#title", {{opacity:0, scale:1.3}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, .1); tl.to("#title b", {{opacity:.55, duration:.06, yoyo:true, repeat:5}}, {wt(0, "10"):.2f}); tl.to("#title", {{opacity:0, y:-40, duration:.25}}, {S(1) - .15:.2f});')
sfx("impact-bass-1", .1, .45); sfx("impact-bass-1", wt(0, "10"), .4)
# hook illustration: a plot with pillars + sale board, then money gets locked
H.append('''<div id="hk"><svg viewBox="0 0 800 560" width="800" height="560">
<path id="hkplot" d="M120 300 L520 230 L700 330 L300 420 Z" pathLength="1" style="fill:rgba(255,196,46,.12);stroke:#FFC42E;stroke-width:6;stroke-dasharray:1;stroke-dashoffset:1"/>
<g class="pil"><rect x="112" y="270" width="16" height="34" fill="#fff"/><rect x="512" y="200" width="16" height="34" fill="#fff"/><rect x="692" y="300" width="16" height="34" fill="#fff"/><rect x="292" y="390" width="16" height="34" fill="#fff"/></g>
<g id="hkboard"><rect x="388" y="150" width="10" height="160" fill="#ddd"/><rect x="300" y="70" width="200" height="100" rx="10" fill="#fff"/><text x="400" y="115" text-anchor="middle" font-family="Anton" font-size="38" fill="#111">PLOT FOR</text><text x="400" y="155" text-anchor="middle" font-family="Anton" font-size="38" fill="#E53935">SALE</text></g>
<g id="hknotes"><g class="nt"><rect x="0" y="0" width="120" height="60" rx="6" fill="#7CB342"/><text x="60" y="42" text-anchor="middle" font-family="Anton" font-size="34" fill="#fff">&#8377;500</text></g>
<g class="nt"><rect x="0" y="0" width="120" height="60" rx="6" fill="#7CB342"/><text x="60" y="42" text-anchor="middle" font-family="Anton" font-size="34" fill="#fff">&#8377;500</text></g>
<g class="nt"><rect x="0" y="0" width="120" height="60" rx="6" fill="#7CB342"/><text x="60" y="42" text-anchor="middle" font-family="Anton" font-size="34" fill="#fff">&#8377;500</text></g></g>
<g id="hklock" transform="translate(560 380)"><path d="M30 50 V30 a40 40 0 0 1 80 0 V50" fill="none" stroke="#FFC42E" stroke-width="12"/><rect x="10" y="50" width="120" height="100" rx="14" fill="#E53935"/><circle cx="70" cy="95" r="12" fill="#fff"/><rect x="65" y="100" width="10" height="26" fill="#fff"/></g>
</svg></div>''')
J.append(f'tl.fromTo("#hk", {{opacity:0}}, {{opacity:1, duration:.2}}, .3); tl.to("#hkplot", {{strokeDashoffset:0, duration:.9, ease:"power2.inOut"}}, .35); tl.fromTo("#hk .pil rect", {{scaleY:0, transformOrigin:"50% 100%"}}, {{scaleY:1, duration:.25, stagger:.12, ease:"back.out(3)"}}, 1.0);'
         f'tl.fromTo("#hkboard", {{y:-300, opacity:0}}, {{y:0, opacity:1, duration:.45, ease:"bounce.out"}}, 1.4);'
         f'tl.set("#hklock", {{opacity:0}}, 0); tl.set("#hk .nt", {{opacity:0}}, 0);')
TP = wt(0, "paisa") - .3
for i, (x0, y0) in enumerate([(120, 120), (60, 230), (200, 180)]):
    J.append(f'tl.fromTo("#hk .nt:nth-child({i + 1})", {{opacity:1, x:{x0}, y:{y0}, rotation:{-15 + i * 12}}}, {{x:575, y:430, rotation:0, scale:.5, duration:.6, ease:"power2.in", immediateRender:false}}, {TP + i * .12:.2f}); tl.to("#hk .nt:nth-child({i + 1})", {{opacity:0, duration:.1}}, {TP + .6 + i * .12:.2f});')
J.append(f'tl.fromTo("#hklock", {{opacity:0, scale:.3, transformOrigin:"50% 50%"}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(3)", immediateRender:false}}, {TP + .5:.2f}); tl.to("#hklock", {{rotation:8, duration:.06, yoyo:true, repeat:7, transformOrigin:"50% 50%"}}, {TP + .9:.2f});')
H.append('<div id="warn">&#9888; PAISA PHAS SAKTA HAI</div>')
J.append(f'tl.fromTo("#warn", {{opacity:0, scale:2}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2.5)"}}, {wt(0, "paisa") + .3:.2f}); tl.to(["#warn", "#hk"], {{opacity:0, duration:.25}}, {S(1) - .15:.2f});')
sfx("whoosh-short", TP, .3); sfx("impact-bass-1", wt(0, "paisa") + .3, .45)

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
# ---------- POINT VISUALS ----------
OK = '<i class="ok">&#10004;</i>'; NO = '<i class="no">&#10006;</i>'
PERSON = '<svg viewBox="0 0 60 60" width="70" height="70"><circle cx="30" cy="20" r="13" fill="#111"/><path d="M6 58 a24 22 0 0 1 48 0 Z" fill="#111"/></svg>'
V = {}; X = {}   # vis html, extra-animation builder
V[1] = f'''<div class="match"><div class="mc">{PERSON}<small>BECHNE WALA</small><b>RAMESH</b></div><div class="eq">=</div><div class="mc rec"><svg viewBox="0 0 60 60" width="70" height="70"><rect x="10" y="4" width="40" height="52" rx="4" fill="#C62828"/><rect x="17" y="14" width="26" height="4" fill="#fff"/><rect x="17" y="24" width="26" height="4" fill="#fff"/><rect x="17" y="34" width="18" height="4" fill="#fff"/></svg><small>JAMABANDI MEIN</small><b>RAMESH</b></div></div><div class="verdict">NAAM MATCH {OK}</div><div class="mag"></div>'''
def x1(c, a, b): return [f'tl.fromTo("#{c} .mag", {{x:-300, y:-260, opacity:0}}, {{x:260, y:-260, opacity:1, duration:1.1, ease:"power1.inOut"}}, {a + .3:.2f}); tl.to("#{c} .mag", {{opacity:0, duration:.2}}, {a + 1.4:.2f});',
                         f'tl.fromTo("#{c} .eq", {{scale:0}}, {{scale:1, duration:.3, ease:"back.out(3)"}}, {a + 1.2:.2f});']
X[1] = x1
V[3] = f'''<svg class="tree" viewBox="0 0 900 520" width="900" height="520">
<path class="tl" d="M450 110 V180 M150 180 H750 M150 180 V240 M450 180 V240 M750 180 V240" pathLength="1" style="fill:none;stroke:#fff;stroke-width:6;stroke-dasharray:1;stroke-dashoffset:1"/>
<g class="nd n0"><rect x="320" y="30" width="260" height="80" rx="14" fill="#FFC42E"/><text x="450" y="82" text-anchor="middle" font-family="Mont" font-weight="900" font-size="34" fill="#111">PITA JI (late)</text></g>
<g class="nd n1"><rect x="40" y="240" width="220" height="80" rx="14" fill="#fff"/><text x="150" y="292" text-anchor="middle" font-family="Mont" font-weight="900" font-size="36" fill="#111">BETA</text></g>
<g class="nd n2"><rect x="340" y="240" width="220" height="80" rx="14" fill="#fff"/><text x="450" y="292" text-anchor="middle" font-family="Mont" font-weight="900" font-size="36" fill="#111">BETI</text></g>
<g class="nd n3"><rect x="640" y="240" width="220" height="80" rx="14" fill="#fff"/><text x="750" y="292" text-anchor="middle" font-family="Mont" font-weight="900" font-size="36" fill="#111">BETA</text></g>
<g class="sg s1"><circle cx="150" cy="370" r="30" fill="#19C25A"/><text x="150" y="383" text-anchor="middle" font-size="36" font-weight="900" fill="#fff">&#10004;</text></g>
<g class="sg s2"><circle cx="450" cy="370" r="30" fill="#E53935"/><text class="s2t" x="450" y="383" text-anchor="middle" font-size="36" font-weight="900" fill="#fff">?</text></g>
<g class="sg s3"><circle cx="750" cy="370" r="30" fill="#19C25A"/><text x="750" y="383" text-anchor="middle" font-size="36" font-weight="900" fill="#fff">&#10004;</text></g>
<g class="nm"><rect x="250" y="430" width="400" height="76" rx="38" fill="#19C25A"/><text x="450" y="481" text-anchor="middle" font-family="Mont" font-weight="900" font-size="34" fill="#fff">NAMANTARAN &#10004;</text></g></svg>
<div class="note">Beti bhi barabar ki waris hai</div>'''
def x3(c, a, b):
    return [f'tl.to("#{c} .tl", {{strokeDashoffset:0, duration:.7, ease:"power2.inOut"}}, {a + .2:.2f});',
            f'tl.fromTo("#{c} .nd", {{scale:0, transformOrigin:"50% 50%", transformBox:"fill-box"}}, {{scale:1, duration:.3, stagger:.15, ease:"back.out(2.5)"}}, {a + .1:.2f});',
            f'tl.fromTo("#{c} .sg", {{scale:0, transformOrigin:"50% 50%", transformBox:"fill-box"}}, {{scale:1, duration:.25, stagger:.2, ease:"back.out(3)"}}, {a + 1.0:.2f});',
            f'tl.to("#{c} .s2", {{scale:1.3, duration:.15, yoyo:true, repeat:3, transformOrigin:"50% 50%", transformBox:"fill-box"}}, {a + 1.8:.2f}); tl.to("#{c} .s2 circle", {{attr:{{fill:"#19C25A"}}, duration:.2}}, {a + 2.5:.2f}); tl.set("#{c} .s2t", {{textContent:"\\u2714"}}, {a + 2.5:.2f});',
            f'tl.fromTo("#{c} .nm", {{scale:0, transformOrigin:"50% 50%", transformBox:"fill-box"}}, {{scale:1, duration:.35, ease:"back.out(2.5)"}}, {a + 2.9:.2f});']
X[3] = x3
CH = ["MAALIK A", "MAALIK B", "????", "MAALIK C", "AAP"]
V[4] = '<div class="vchain">' + "".join(f'<div class="cn{" miss" if c == "????" else ""}{" you" if c == "AAP" else ""}">{c}</div>' + ('<div class="ca"></div>' if i < len(CH) - 1 else '') for i, c in enumerate(CH)) + '</div>'
def x4(c, a, b):
    return [f'tl.fromTo("#{c} .cn", {{x:-80, opacity:0}}, {{x:0, opacity:1, duration:.25, stagger:.22, ease:"back.out(2)"}}, {a + .1:.2f}); tl.fromTo("#{c} .ca", {{scaleY:0}}, {{scaleY:1, duration:.2, stagger:.22}}, {a + .25:.2f});',
            f'tl.to("#{c} .miss", {{scale:1.15, duration:.15, yoyo:true, repeat:5}}, {a + 1.4:.2f});']
X[4] = x4
V[7] = '''<svg class="naap" viewBox="0 0 900 600" width="900" height="600">
<rect class="pl" x="150" y="120" width="560" height="340" pathLength="1" style="fill:rgba(255,196,46,.12);stroke:#FFC42E;stroke-width:6;stroke-dasharray:1;stroke-dashoffset:1"/>
<g class="dim"><line x1="150" y1="500" x2="710" y2="500" stroke="#fff" stroke-width="4"/><line x1="150" y1="485" x2="150" y2="515" stroke="#fff" stroke-width="4"/><line x1="710" y1="485" x2="710" y2="515" stroke="#fff" stroke-width="4"/><text x="430" y="560" text-anchor="middle" font-family="Mont" font-weight="900" font-size="38" fill="#fff">KAGAZ: 200 GAJ</text></g>
<g class="tape"><rect x="120" y="60" width="70" height="70" rx="14" fill="#FFC42E"/><circle cx="155" cy="95" r="18" fill="#111"/><rect class="tb" x="190" y="86" width="0" height="18" fill="#FFD95A"/></g>
<g class="kb"><rect x="590" y="120" width="120" height="340" fill="url(#hatch)"/><rect x="590" y="120" width="120" height="340" fill="none" stroke="#E53935" stroke-width="6"/><text x="650" y="300" text-anchor="middle" font-family="Anton" font-size="44" fill="#fff" transform="rotate(-90 650 300)">KABZA!</text></g>
<g class="site"><rect x="210" y="20" width="440" height="70" rx="35" fill="#E53935"/><text x="430" y="68" text-anchor="middle" font-family="Mont" font-weight="900" font-size="36" fill="#fff">SITE PAR: SIRF 160 GAJ</text></g>
<defs><pattern id="hatch" width="20" height="20" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="20" height="20" fill="rgba(229,57,53,.35)"/><rect width="8" height="20" fill="rgba(229,57,53,.75)"/></pattern></defs></svg>
<div class="verdict">NAAP + SEEMANKAN KARWAO ''' + OK + '</div>'
def x7(c, a, b):
    return [f'tl.to("#{c} .pl", {{strokeDashoffset:0, duration:.8, ease:"power2.inOut"}}, {a + .1:.2f});',
            f'tl.fromTo("#{c} .tb", {{attr:{{width:0}}}}, {{attr:{{width:520}}, duration:.9, ease:"power2.out"}}, {a + .6:.2f}); tl.fromTo("#{c} .dim", {{opacity:0}}, {{opacity:1, duration:.3}}, {a + 1.3:.2f});',
            f'tl.fromTo("#{c} .kb", {{x:260, opacity:0}}, {{x:0, opacity:1, duration:.6, ease:"power3.out"}}, {wt(POS[7], "kabza") - .4:.2f}); tl.to("#{c} .tape", {{opacity:0, duration:.2}}, {wt(POS[7], "kabza") - .1:.2f}); tl.fromTo("#{c} .site", {{scale:0, transformOrigin:"50% 50%", transformBox:"fill-box"}}, {{scale:1, duration:.3, ease:"back.out(3)"}}, {wt(POS[7], "kabza") + .1:.2f});']
X[7] = x7
V[9] = '''<svg class="rasta" viewBox="0 0 900 520" width="900" height="520">
<rect x="0" y="330" width="900" height="150" fill="#3a3d45"/><line class="ln" x1="0" y1="405" x2="900" y2="405" stroke="#fff" stroke-width="6" stroke-dasharray="40 30"/>
<rect class="pl" x="300" y="60" width="300" height="250" rx="6" style="fill:rgba(60,230,90,.18);stroke:#3CE65A;stroke-width:6"/><text x="450" y="200" text-anchor="middle" font-family="Anton" font-size="56" fill="#fff">PLOT</text>
<g class="wd"><line x1="820" y1="335" x2="820" y2="475" stroke="#FFC42E" stroke-width="6"/><path d="M805 350 L820 330 L835 350 M805 460 L820 480 L835 460" fill="none" stroke="#FFC42E" stroke-width="6"/><rect x="640" y="372" width="160" height="66" rx="12" fill="#FFC42E"/><text x="720" y="417" text-anchor="middle" font-family="Anton" font-size="38" fill="#111">? FT</text></g>
</svg><div class="zones"><span class="zr">RESIDENTIAL ''' + OK + '</span><span class="zg">GREEN / ECO ZONE ' + NO + '</span></div>'
def x9(c, a, b):
    return [f'tl.fromTo("#{c} .ln", {{strokeDashoffset:0}}, {{strokeDashoffset:-280, duration:2, ease:"none"}}, {a:.2f});',
            f'tl.fromTo("#{c} .wd", {{opacity:0, scale:.5, transformOrigin:"50% 50%", transformBox:"fill-box"}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2.5)"}}, {a + .5:.2f});',
            f'tl.fromTo("#{c} .zones span", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.3, stagger:.25, ease:"back.out(2)"}}, {wt(POS[9], "master") :.2f});']
X[9] = x9
V[6] = '<div class="title-doc"><div class="dh">ZAMEEN KA TITLE</div><div class="stp s1">GIRVI</div><div class="stp s2">BANK LOAN</div><div class="stp s3">COURT STAY</div><div class="clr">CLEAR TITLE ' + OK + '</div></div>'
def x6(c, a, b):
    out = []
    for i, w in enumerate(["loan", "girvi", "court case"]):
        t = max(a + .2 + i * .35, wt(POS[6], w) - .1)
        out.append(f'tl.fromTo("#{c} .s{i + 1}", {{opacity:0, scale:2.5, rotation:-25}}, {{opacity:1, scale:1, rotation:{-12 + i * 8}, duration:.22, ease:"power4.in", immediateRender:false}}, {t:.2f});'); sfx("impact-bass-1", t + .2, .25)
    out.append(f'tl.to("#{c} .stp", {{opacity:.15, duration:.3}}, {wt(POS[6], "confirm") - .2:.2f}); tl.fromTo("#{c} .clr", {{opacity:0, scale:2}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2.5)", immediateRender:false}}, {wt(POS[6], "confirm"):.2f});')
    return out
X[6] = x6
V[5] = '''<svg class="dbl" viewBox="0 0 900 460" width="900" height="460">
<rect x="330" y="40" width="240" height="180" rx="10" style="fill:rgba(255,196,46,.18);stroke:#FFC42E;stroke-width:6;stroke-dasharray:18 12"/><text x="450" y="148" text-anchor="middle" font-family="Anton" font-size="56" fill="#fff">PLOT</text>
<g class="b1"><circle cx="120" cy="120" r="34" fill="#fff"/><path d="M70 220 a50 50 0 0 1 100 0 Z" fill="#fff"/><rect x="40" y="250" width="170" height="60" rx="10" fill="#fff"/><text x="125" y="291" text-anchor="middle" font-family="Mont" font-weight="900" font-size="26" fill="#111">REGISTRY 1</text></g>
<g class="b2"><circle cx="780" cy="120" r="34" fill="#FFB4B4"/><path d="M730 220 a50 50 0 0 1 100 0 Z" fill="#FFB4B4"/><rect x="690" y="250" width="170" height="60" rx="10" fill="#FFB4B4"/><text x="775" y="291" text-anchor="middle" font-family="Mont" font-weight="900" font-size="26" fill="#111">REGISTRY 2</text></g>
<g class="bang"><circle cx="450" cy="340" r="60" fill="#E53935"/><text x="450" y="365" text-anchor="middle" font-family="Anton" font-size="70" fill="#fff">!</text></g></svg>
<div class="verdict">PEHLE SE REGISTRY? CHECK ''' + OK + '</div>'
def x5(c, a, b):
    return [f'tl.fromTo("#{c} .b1", {{x:-300, opacity:0}}, {{x:0, opacity:1, duration:.5, ease:"power3.out"}}, {a + .1:.2f}); tl.fromTo("#{c} .b2", {{x:300, opacity:0}}, {{x:0, opacity:1, duration:.5, ease:"power3.out"}}, {a + .5:.2f});',
            f'tl.fromTo("#{c} .bang", {{scale:0, transformOrigin:"50% 50%", transformBox:"fill-box"}}, {{scale:1, duration:.3, ease:"back.out(3)"}}, {a + 1.0:.2f}); tl.to("#{c} .bang", {{scale:1.15, duration:.15, yoyo:true, repeat:5, transformOrigin:"50% 50%", transformBox:"fill-box"}}, {a + 1.3:.2f});']
X[5] = x5
V[2] = f'''<div class="doc"><div class="dh">POWER OF ATTORNEY</div><div class="dr"><span>POA asli hai?</span>{OK}</div><div class="dr"><span>Maalik zinda hai?</span><svg class="hb" viewBox="0 0 200 50" width="200" height="50"><polyline points="0,25 50,25 65,5 80,45 95,25 200,25" pathLength="1" style="fill:none;stroke:#19C25A;stroke-width:5;stroke-dasharray:1;stroke-dashoffset:1"/></svg></div><div class="dr"><span>Radd (cancel) toh nahi?</span>{OK}</div></div>'''
def x2(c, a, b): return [f'tl.to("#{c} .hb polyline", {{strokeDashoffset:0, duration:.8, ease:"none", repeat:2}}, {wt(POS[2], "zinda") - .3:.2f});']
X[2] = x2
V[8] = '''<svg class="conv" viewBox="0 0 900 520" width="900" height="520">
<g class="fld">''' + "".join(f'<rect x="{80 + i * 92}" y="40" width="80" height="380" rx="6" fill="{"#4CAF50" if i % 2 else "#7CB342"}"/>' for i in range(8)) + '''</g>
<g class="col">''' + "".join(f'<rect x="{80 + (i % 5) * 150}" y="{40 + (i // 5) * 130}" width="130" height="110" rx="6" fill="#fff" stroke="#FFC42E" stroke-width="4"/>' for i in range(15)) + '''</g>
<g class="st1"><rect x="120" y="440" width="300" height="70" rx="35" fill="#19C25A"/><text x="270" y="488" text-anchor="middle" font-family="Mont" font-weight="900" font-size="32" fill="#fff">90-A &#10004;</text></g>
<g class="st2"><rect x="460" y="440" width="340" height="70" rx="35" fill="#19C25A"/><text x="630" y="488" text-anchor="middle" font-family="Mont" font-weight="900" font-size="32" fill="#fff">LAYOUT &#10004;</text></g></svg>'''
def x8(c, a, b):
    return [f'tl.fromTo("#{c} .fld", {{opacity:1}}, {{opacity:0, duration:.4}}, {a + .8:.2f}); tl.fromTo("#{c} .col rect", {{opacity:0, scale:0, transformOrigin:"50% 50%", transformBox:"fill-box"}}, {{opacity:1, scale:1, duration:.2, stagger:.04, ease:"back.out(2)"}}, {a + .9:.2f});',
            f'tl.fromTo("#{c} .st1", {{scale:0, transformOrigin:"50% 50%", transformBox:"fill-box"}}, {{scale:1, duration:.3, ease:"back.out(3)"}}, {a + .6:.2f}); tl.fromTo("#{c} .st2", {{scale:0, transformOrigin:"50% 50%", transformBox:"fill-box"}}, {{scale:1, duration:.3, ease:"back.out(3)"}}, {a + 1.6:.2f});']
X[8] = x8
V[10] = '''<svg class="pay" viewBox="0 0 900 560" width="900" height="560">
<g class="cash"><rect x="60" y="40" width="300" height="150" rx="12" fill="#7CB342"/><rect x="80" y="60" width="260" height="110" rx="8" fill="none" stroke="#fff" stroke-width="4"/><text x="210" y="135" text-anchor="middle" font-family="Anton" font-size="60" fill="#fff">&#8377; CASH</text><line class="x1" x1="40" y1="20" x2="380" y2="210" stroke="#E53935" stroke-width="16" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/></g>
<g class="bank"><path d="M560 70 L700 20 L840 70 Z" fill="#fff"/><rect x="575" y="80" width="250" height="16" fill="#fff"/><rect x="590" y="100" width="22" height="70" fill="#fff"/><rect x="650" y="100" width="22" height="70" fill="#fff"/><rect x="710" y="100" width="22" height="70" fill="#fff"/><rect x="770" y="100" width="22" height="70" fill="#fff"/><rect x="570" y="172" width="260" height="18" fill="#fff"/><text x="700" y="240" text-anchor="middle" font-family="Mont" font-weight="900" font-size="34" fill="#19C25A">BANK SE &#10004;</text></g>
<g class="agr"><rect x="250" y="290" width="400" height="250" rx="12" fill="#FFF8E7"/><text x="450" y="345" text-anchor="middle" font-family="Anton" font-size="40" fill="#111">LIKHIT AGREEMENT</text><rect x="290" y="370" width="320" height="8" fill="#ccc"/><rect x="290" y="395" width="280" height="8" fill="#ccc"/><rect x="290" y="420" width="300" height="8" fill="#ccc"/>
<path class="sig" d="M300 500 q20 -40 40 0 t40 0 q15 -30 30 -5 t50 5 l60 -10" pathLength="1" style="fill:none;stroke:#1e40af;stroke-width:5;stroke-dasharray:1;stroke-dashoffset:1"/></g></svg>'''
def x10(c, a, b):
    return [f'tl.to("#{c} .x1", {{attr:{{"stroke-dashoffset":0}}, duration:.3}}, {wt(POS[10], "cash") + .1:.2f});',
            f'tl.fromTo("#{c} .bank", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.3, ease:"back.out(2)", immediateRender:false}}, {wt(POS[10], "bank") - .3:.2f}); tl.fromTo("#{c} .agr", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:.3, ease:"back.out(2)", immediateRender:false}}, {wt(POS[10], "Agreement") - .1:.2f});',
            f'tl.to("#{c} .sig", {{strokeDashoffset:0, duration:.7, ease:"power1.inOut"}}, {wt(POS[10], "Agreement") + .3:.2f});']
X[10] = x10

PTS = {1: ("ASLI MAALIK", "Jamabandi &middot; Apna Khata", "naam"), 2: ("POWER OF ATTORNEY", "POA se sauda? Double check", "mukar"), 3: ("VIRASAT", "Saare waris + namantaran", "sahmati"),
       4: ("REGISTRY CHAIN", "Koi link missing nahi", "missing"), 5: ("DOUBLE SALE", "Ek plot, do kharidaar?", "Registration"), 6: ("LOAN / CASE", "Zameen saaf honi chahiye", "confirm"),
       7: ("NAAP AUR KABZA", "Kagaz = Site?", "naap"), 8: ("CONVERSION + APPROVAL", "90-A &middot; layout plan", "90-A"), 9: ("RASTA + MASTER PLAN", "Pakka rasta &middot; residential use", "rasta"),
       10: ("PAYMENT", "Likhit agreement &middot; bank se payment", "Agreement")}
PHOTOS = {1: [("jamabandi", "JAMABANDI", "Prati-lipi &middot; details blurred")], 4: [("stamp", "PURANI REGISTRIES", "Har kagaz ki chain")],
          9: [("jdamap", "MASTER PLAN", "JDA &middot; Land utilization, Jaipur region")], 5: [("subreg", "REGISTRATION OFFICE", "Up-panjiyak karyalaya")],
          8: [("farm", "KHETI KI ZAMEEN", "Conversion ke bina colony = risk"), ("layout", "LAYOUT APPROVAL", "Approved scheme &middot; RERA no. check karo")]}
for k, o in enumerate(ORDER, 1):
    title, sub, kw = PTS[o]; cid = f"pt{o}"; t0 = S(k) - .05; t1 = S(k + 1)
    VS = t0 + .35
    if o in PHOTOS:
        ph = PHOTOS[o]; mid = t0 + (t1 - t0) * (.45 if len(ph) == 1 else .6); seg = (mid - t0 - .3) / len(ph)
        for j, (img, ttl, sb) in enumerate(ph):
            a_ = t0 + .3 + seg * j; card(f"ph{o}{j}", img, a_, a_ + seg + .15, ttl, sb, top=590, maxw=880, maxh=680)
        VS = mid + .1
    H.append(f'<div class="pt" id="{cid}"><div class="num">{k}<small>/10</small></div><b>{title}</b><p>{sub}</p><div class="vis" style="opacity:0">{V[o]}</div></div>')
    J.append(f'tl.fromTo("#{cid}", {{opacity:0, x:120}}, {{opacity:1, x:0, duration:.3, ease:"power3.out"}}, {t0:.2f}); tl.fromTo("#{cid} .num", {{scale:2.2, rotation:-12}}, {{scale:1, rotation:0, duration:.35, ease:"back.out(2.5)"}}, {t0:.2f});'
             f'tl.fromTo("#{cid} .vis", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:.3, ease:"back.out(1.6)", immediateRender:false}}, {VS:.2f});'
             f'tl.to("#{cid}", {{opacity:0, x:-120, duration:.22, ease:"power2.in"}}, {t1 - .2:.2f});')
    J.extend(X[o](cid, VS, t1))
    tk = max(VS + .5, wt(k, kw) - .05)
    J.append(f'tl.fromTo("#{cid} .ok", {{opacity:0, scale:3}}, {{opacity:1, scale:1, duration:.25, stagger:.15, ease:"back.out(3)", immediateRender:false}}, {tk:.2f}); tl.fromTo("#{cid} .no", {{opacity:0, scale:3}}, {{opacity:1, scale:1, duration:.25, stagger:.15, ease:"back.out(3)", immediateRender:false}}, {tk:.2f});')
    J.append(f'tl.set("#{cid} .ok, #{cid} .no", {{opacity:0}}, 0);')
    sfx("whoosh-short", t0, .3); sfx("pop", t0 + .05, .3); sfx("pop", VS, .25); sfx("click-soft", tk, .45)

# ---------- CTA ----------
card("phme", "me", S(11) - .05, wt(11, "Jaipur") + .1, "&#10004; MAIN YEH SAB KHUD CHECK KARTA HOON", "Ashwil Bhupesh &middot; site par", top=300, maxw=760, maxh=900)
H.append('<div id="cta"><b>JAIPUR MEIN ZAMEEN DHUNDH RAHE HO?</b><span>COMMENT &ldquo;PLOT&rdquo;</span></div>')
J.append(f'tl.fromTo("#cta", {{opacity:0, scale:.8}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)"}}, {wt(11, "Jaipur"):.2f}); tl.to("#cta span", {{scale:1.08, duration:.4, yoyo:true, repeat:3}}, {wt(11, "Comment"):.2f});')
card("phig", "insta", wt(11, "Comment") - .4, END + 1, "FOLLOW @ASHWILLPOWER", "", top=800, maxw=620, maxh=540)
sfx("sparkle", S(11), .3); sfx("sparkle", wt(11, "Comment"), .3)

# captions
HI = ["10 baaton", "paisa phas", "jamabandi", "Apna Khata", "power of attorney", "POA", "virasat", "waris", "namantaran", "registries ki chain", "missing", "do logon", "Registration office", "loan", "girvi", "court case", "naap", "kabza", "90-A conversion", "layout approval", "pakka rasta", "master plan", "residential", "cash", "likhit", "bank", "Plot"]
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
H.append('<div id="cred">Educational only &middot; legal verification ke liye vakeel se bhi salah lein</div>')
CSS = """@font-face{font-family:Anton;src:url(assets/fonts/anton.woff2)}@font-face{font-family:Mont;font-weight:700;src:url(assets/fonts/mont700.woff2)}@font-face{font-family:Mont;font-weight:800;src:url(assets/fonts/mont800.woff2)}@font-face{font-family:Mont;font-weight:900;src:url(assets/fonts/mont900.woff2)}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#1b1b1d}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif}#world{position:absolute;inset:0;width:1080px;height:1920px}.y{color:#111;background:#FFC42E;border-radius:6px;padding:0 6px}
#face{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:40}
#clouds{position:absolute;inset:0;z-index:15;pointer-events:none;overflow:hidden}#clouds img{position:absolute;left:-260px;top:-240px;width:1600px;height:2400px}
#cred{position:absolute;left:40px;right:40px;top:1650px;text-align:center;font:700 17px Mont;color:rgba(255,255,255,.6);z-index:20}
#rate{position:absolute;left:0;right:0;top:640px;text-align:center;opacity:0;z-index:16}#rate b{display:inline-block;padding:12px 30px;border-radius:14px;background:#19C25A;color:#fff;font:400 78px/1 Anton;box-shadow:0 8px 30px rgba(0,0,0,.6)}
#ask{position:absolute;left:0;right:0;top:690px;text-align:center;z-index:16;display:flex;gap:24px;justify-content:center}#ask span{opacity:0;padding:12px 28px;border-radius:14px;font:400 72px/1 Anton;color:#fff;box-shadow:0 8px 30px rgba(0,0,0,.6)}#ask .r{background:#E53935}#ask .h{background:#3D8BFF}
.pref{position:absolute;left:50px;right:50px;top:250px;opacity:0;text-align:center;z-index:12}.pref .tags{display:flex;gap:16px;justify-content:center}.pref .tags span{padding:10px 22px;border-radius:30px;font:900 32px Mont;color:#fff;box-shadow:0 6px 16px rgba(0,0,0,.5)}
.pref b{display:block;margin-top:18px;font:400 112px/1 Anton;font-weight:400;text-shadow:0 0 26px rgba(0,0,0,.6),0 6px 24px #000}.pref p{display:inline-block;margin-top:14px;padding:8px 22px;border-radius:10px;background:#fff;color:#111;font:900 32px Mont}
#newz{position:absolute;left:0;right:0;top:1330px;margin:0 auto;width:max-content;opacity:0;padding:8px 22px;border-radius:12px;background:#111;color:#3CE65A;font:900 32px Mont;z-index:9}
#chk{position:absolute;left:110px;right:110px;top:330px;opacity:0;padding:34px 40px;border-radius:28px;background:#fff;z-index:12;box-shadow:0 30px 70px rgba(0,0,0,.7)}#chk b{display:block;text-align:center;font:400 76px/1 Anton;color:#111;font-weight:400}#chk ul{list-style:none;margin-top:22px}#chk li{opacity:0;margin-top:14px;font:900 52px Mont;color:#0E8A3A}
#warn{position:absolute;left:0;right:0;top:1250px;margin:0 auto;width:max-content;opacity:0;padding:14px 30px;border-radius:14px;background:#E53935;color:#fff;font:400 64px/1 Anton;box-shadow:0 8px 30px rgba(0,0,0,.6);z-index:16}
.pt{position:absolute;left:60px;right:60px;top:230px;opacity:0;text-align:center;z-index:12}
.pt .num{display:inline-block;padding:6px 26px;border-radius:16px;background:#FFC42E;color:#111;font:400 84px/1 Anton}.pt .num small{font-size:40px;opacity:.6}
.pt > b{display:block;margin-top:16px;font:400 100px/1 Anton;font-weight:400;color:#fff;text-shadow:0 6px 24px #000}.pt p{display:inline-block;margin-top:14px;padding:8px 22px;border-radius:10px;background:#fff;color:#111;font:900 34px Mont}
.vis{margin-top:50px;display:flex;flex-direction:column;align-items:center;gap:18px}
.ok,.no{display:inline-block;margin-left:10px;width:46px;height:46px;line-height:46px;border-radius:50%;font:900 30px Mont;font-style:normal;color:#fff;text-align:center;vertical-align:middle}.ok{background:#19C25A}.no{background:#E53935}
.doc{width:780px;padding:26px 34px;border-radius:20px;background:#FFF8E7;box-shadow:0 20px 50px rgba(0,0,0,.6);text-align:left;border-top:14px solid #C62828}.dh{font:400 56px/1 Anton;color:#111;text-align:center;margin-bottom:14px;letter-spacing:.04em}
.dr{display:flex;justify-content:space-between;align-items:center;padding:12px 0;border-top:2px dashed #c9b98f;font:900 38px Mont;color:#222}.dr b{color:#C62828}
.tree{display:flex;flex-direction:column;align-items:center}.tn{padding:14px 24px;border-radius:14px;background:#fff;font:900 34px Mont;color:#111;box-shadow:0 10px 30px rgba(0,0,0,.5)}.tn.top{background:#FFC42E}.tl{width:6px;height:40px;background:#fff}
.trow{display:flex;gap:16px;border-top:6px solid #fff;padding-top:26px}.tn.nm{margin-top:30px;background:#19C25A;color:#fff}
.chain{display:flex;align-items:center;gap:8px}.chain span{padding:14px 12px;border-radius:14px;background:#fff;font:900 30px Mont;color:#111;box-shadow:0 10px 30px rgba(0,0,0,.5)}.chain b{font:900 34px Mont;color:#FFC42E}.chain .you{background:#FFC42E}
.dbl{position:relative;width:820px;height:420px}.dbl .plot{position:absolute;left:290px;top:20px;width:240px;height:200px;line-height:200px;border:6px dashed #FFC42E;border-radius:14px;background:rgba(255,196,46,.25);font:400 60px Anton;color:#fff}
.dbl .by{position:absolute;top:280px;padding:16px 24px;border-radius:14px;background:#fff;font:900 34px Mont;color:#111}.dbl .b1{left:20px}.dbl .b2{right:0;background:#FFE1E1}
.chips{display:flex;gap:12px}.chips span{padding:14px 16px;border-radius:14px;background:#fff;font:900 30px Mont;color:#111}.clear{padding:16px 40px;border-radius:16px;background:#19C25A;color:#fff;font:400 70px/1 Anton}
.naap{display:flex;flex-direction:column;align-items:center;gap:20px}.naap .pl{width:560px;height:300px;border:6px solid #fff;border-radius:10px;background:rgba(255,255,255,.12);display:flex;align-items:center;justify-content:center}.naap .w{font:900 40px Mont;font-style:normal;color:#FFC42E}
.cmp{display:flex;align-items:center;gap:16px}.cmp span{padding:14px 24px;border-radius:14px;background:#fff;font:900 38px Mont;color:#111}.cmp b{font:400 70px Anton;color:#fff}.kb{padding:12px 24px;border-radius:14px;background:#FFE1E1;font:900 36px Mont;color:#111}
.stamps{display:flex;flex-direction:column;gap:22px;align-items:center}.stamps span{padding:18px 30px;border-radius:16px;background:#fff;font:900 42px Mont;color:#111;box-shadow:0 12px 30px rgba(0,0,0,.6)}
.pay{display:flex;flex-direction:column;gap:20px;align-items:center}.pay div{padding:18px 30px;border-radius:16px;font:900 44px Mont;color:#111;background:#fff}.pay .cash{background:#FFE1E1;text-decoration:line-through;text-decoration-thickness:5px;text-decoration-color:#E53935}
#trust{position:absolute;left:0;right:0;top:600px;margin:0 auto;width:max-content;opacity:0;padding:16px 30px;border-radius:16px;background:#19C25A;color:#fff;font:900 40px Mont;z-index:13}
#world{display:none}
#bg{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 30%,#1d2340 0%,#0c0f1c 70%);overflow:hidden}
#grid{position:absolute;inset:-200px;background-image:linear-gradient(rgba(255,255,255,.06) 2px,transparent 2px),linear-gradient(90deg,rgba(255,255,255,.06) 2px,transparent 2px);background-size:120px 120px;transform:perspective(900px) rotateX(35deg);transform-origin:50% 100%}
#glow1,#glow2{position:absolute;width:900px;height:900px;border-radius:50%;filter:blur(120px);opacity:.35}#glow1{left:-200px;top:200px;background:#FFC42E}#glow2{right:-300px;top:900px;background:#3D8BFF}
#vig{position:absolute;inset:0;background:radial-gradient(ellipse at center,transparent 50%,rgba(0,0,0,.65) 100%)}
#prog{position:absolute;left:60px;right:60px;top:120px;display:flex;gap:10px;opacity:0;z-index:20}#prog i{flex:1;height:14px;border-radius:7px;background:rgba(255,255,255,.18);overflow:hidden}#prog b{display:block;height:100%;background:#FFC42E;transform-origin:0 50%}
#hk{position:absolute;left:140px;top:600px;transform:scale(1.15);transform-origin:50% 0;opacity:0;z-index:9}
.match{display:flex;align-items:center;gap:26px}.mc{width:330px;padding:24px 16px;border-radius:22px;background:#fff;text-align:center;box-shadow:0 20px 50px rgba(0,0,0,.6)}.mc small{display:block;margin-top:8px;font:900 26px Mont;color:#666}.mc b{display:block;font:400 64px/1.1 Anton;color:#111}.mc.rec{background:#FFF8E7}
.eq{font:400 110px/1 Anton;color:#FFC42E}.verdict{margin-top:30px;padding:16px 34px;border-radius:40px;background:#fff;font:900 40px Mont;color:#111;display:inline-block}
.mag{position:absolute;left:50%;top:50%;width:150px;height:150px;border-radius:50%;border:14px solid #FFC42E;background:rgba(255,255,255,.15);opacity:0}.mag:after{content:"";position:absolute;right:-60px;bottom:-40px;width:80px;height:22px;background:#FFC42E;transform:rotate(40deg);border-radius:10px}
.vis{position:relative}.note{margin-top:10px;padding:10px 24px;border-radius:12px;background:#FFC42E;font:900 32px Mont;color:#111;display:inline-block}
.vchain{display:flex;flex-direction:column;align-items:center}.cn{width:420px;padding:18px;border-radius:18px;background:#fff;font:400 54px/1 Anton;color:#111;box-shadow:0 14px 34px rgba(0,0,0,.5)}.cn.miss{background:#E53935;color:#fff}.cn.you{background:#FFC42E}.ca{width:8px;height:34px;background:#FFC42E;transform-origin:50% 0}
.zones{margin-top:20px;display:flex;flex-direction:column;gap:16px;align-items:center}.zones span{padding:14px 28px;border-radius:16px;font:900 38px Mont;color:#111}.zr{background:#fff}.zg{background:#FFE1E1}
.title-doc{position:relative;width:820px;height:640px;border-radius:24px;background:#FFF8E7;border-top:16px solid #C62828;box-shadow:0 30px 70px rgba(0,0,0,.7)}.title-doc .dh{margin-top:26px}
.stp{position:absolute;padding:14px 30px;border:8px solid #E53935;border-radius:14px;font:400 72px/1 Anton;color:#E53935;opacity:0;background:rgba(255,255,255,.6)}.s1{left:70px;top:130px}.s2{left:300px;top:270px}.s3{left:120px;top:420px}
.clr{position:absolute;left:0;right:0;margin:0 auto;width:max-content;top:250px;padding:20px 40px;border-radius:20px;background:#19C25A;color:#fff;font:400 84px/1 Anton;opacity:0}.clr .ok{background:#fff;color:#19C25A}
#title{position:absolute;left:0;right:0;top:280px;text-align:center;opacity:0;z-index:16}#title small{display:inline-block;padding:8px 22px;border-radius:10px;background:#fff;color:#111;font:900 34px Mont}
#title b{display:block;margin-top:14px;font:400 112px/1 Anton;color:#FFC42E;text-shadow:0 0 30px rgba(255,196,46,.6),0 6px 30px #000;font-weight:400}
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
