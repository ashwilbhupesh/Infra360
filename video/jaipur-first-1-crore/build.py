"""Pehla 1 crore Jaipur mein kahan? — preference-based reel (zones are illustrative rings, not survey boundaries)."""
import json, math, os
P = "proj"
ASP = json.load(open("aspects.json"))
LINES = [
    "Jaipur mein apna pehla 1 crore kahan lagaye? Jawab aapki risk aur holding par depend karta hai.",
    "High risk aur lambi holding? Agriculture land. Sasta milta hai, par conversion aur approval ka risk hai.",
    "Low risk aur lambi holding? Shehar se door JDA approved plots. Shehar jis taraf badh raha hai, wahan dekho.",
    "Low risk aur kam holding? Shehar ke paas, naye JDA zones mein plots. Infra aa raha hai, aur resale aasaan hai.",
    "Commercial chahiye? National highway, state highway ya city ke main road par plot lo. Frontage hi asli value hai.",
    "Kuch bhi lo, patta, approval aur RERA zaroor check karo.",
    "Aapki preference kya hai? Comment karo Crore.",
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
END = round(E(6) + 1.3, 2)
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

# ---------- 0 HOOK ----------
H.append('<div id="title"><small>JAIPUR MEIN APNA PEHLA</small><b>&#8377;1 CRORE<br/>KAHAN LAGAYE?</b></div>')
J.append(f'tl.fromTo("#title", {{opacity:0, scale:1.3}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, .2); tl.to("#title b", {{opacity:.55, duration:.06, yoyo:true, repeat:5}}, {wt(0, "1 crore"):.2f}); tl.to("#title", {{opacity:0, duration:.2}}, {S(1) - .1:.2f});')
sfx("impact-bass-1", .2, .45); sfx("impact-bass-1", wt(0, "1 crore"), .4)
H.append('<div id="ask"><span class="r">RISK?</span><span class="h">HOLDING?</span></div>')
J.append(f'tl.fromTo("#ask .r", {{opacity:0, scale:2}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2.5)"}}, {wt(0, "risk") - .05:.2f}); tl.fromTo("#ask .h", {{opacity:0, scale:2}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2.5)"}}, {wt(0, "holding") - .05:.2f}); tl.to("#ask", {{opacity:0, duration:.2}}, {S(1) - .1:.2f});')
sfx("pop", wt(0, "risk") - .05, .3); sfx("pop", wt(0, "holding") - .05, .3)
J.append(f'tl.to("#zco", {{opacity:1, fillOpacity:.22, duration:.4}}, 2.8); tl.to("#zco", {{fillOpacity:.08, duration:.4}}, {S(1):.2f});')
lab("lcity", CEN, "SHEHAR &middot; NAGAR NIGAM", 2.9, S(1) - .1, 3.1)
H.append('<div class="ml mlab" id="mr">RAJASTHAN</div><div class="ml mlab" id="mj">JAIPUR</div>')
for k, t_ in [("mr", .2), ("mj", 1.25)]:
    J.append(f'tl.fromTo("#{k}", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.25}}, {t_:.2f}); tl.to("#{k}", {{opacity:0, duration:.15}}, {t_ + .6:.2f});')

# ---------- preference cards ----------
def pref(k, cid, risk, hold, title, col, sub, t1):
    rc = {"HIGH": "#E53935", "LOW": "#19C25A"}.get(risk, "#C98A00")
    hp = f'<span style="background:#2b2f3a">HOLDING: {hold}</span>' if hold else ''
    H.append(f'<div class="pref" id="{cid}"><div class="tags"><span style="background:{rc}">{"RISK: " + risk if risk in ("HIGH", "LOW") else risk}</span>{hp}</div><b style="color:{col}">{title}</b><p>{sub}</p></div>')
    t0 = S(k) - .05
    J.append(f'tl.fromTo("#{cid}", {{opacity:0, y:-40}}, {{opacity:1, y:0, duration:.3, ease:"back.out(2)"}}, {t0:.2f}); tl.fromTo("#{cid} .tags span", {{opacity:0, scale:1.8}}, {{opacity:1, scale:1, duration:.25, stagger:.25, ease:"back.out(2.5)"}}, {t0 + .1:.2f});'
             f'tl.fromTo("#{cid} b", {{opacity:0, scale:1.6}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2.2)"}}, {t0 + .75:.2f}); tl.fromTo("#{cid} p", {{opacity:0}}, {{opacity:1, duration:.3}}, {t0 + 1.2:.2f}); tl.to("#{cid}", {{opacity:0, duration:.2}}, {t1 - .15:.2f});')
    sfx("pop", t0 + .1, .3); sfx("pop", t0 + .35, .25); sfx("impact-bass-1", t0 + .75, .35)
pref(1, "p1", "HIGH", "LAMBI", "AGRICULTURE LAND", AGRI, "Sasta &middot; par conversion / approval ka risk", S(2))
J.append(f'tl.to("#jreg", {{opacity:1, duration:.4}}, {S(1) + .2:.2f}); tl.to("#zag", {{opacity:.42, duration:.6}}, {S(1) + .5:.2f}); tl.to("#zag", {{opacity:.25, duration:.35, yoyo:true, repeat:3}}, {S(1) + 1.2:.2f}); tl.to("#zag", {{opacity:0, duration:.3}}, {S(2) - .1:.2f});')
sfx("whoosh-short", S(1) + .5, .3)
lab("l1", wp(27.30, 75.45), "KHETI KI ZAMEEN", S(1) + .9, S(2), S(1) + .9, style=f"background:{AGRI}")
lab("lj1", wp(26.72, 75.80), "JDA REGION", S(1) + .5, S(2), S(1) + .9, style="font-size:28px")
pref(2, "p2", "LOW", "LAMBI", "SHEHAR SE DOOR PLOTS", FAR, "JDA approved &middot; growth ki direction dekho", S(3))
J.append(f'tl.to("#zfa", {{opacity:.5, duration:.6}}, {S(2) + .3:.2f}); tl.to("#zfa", {{opacity:.3, duration:.35, yoyo:true, repeat:3}}, {S(2) + 1:.2f}); tl.to("#zfa", {{opacity:0, duration:.3}}, {S(3) - .1:.2f});')
sfx("whoosh-short", S(2) + .3, .3)
lab("l2", wp(27.33, 75.45), "DOOR KE PLOTS", S(2) + .9, S(3), S(2) + .9, style=f"background:{FAR};color:#fff")
for i, b in enumerate((300, 120, 210)):
    a0, a1 = km(b, 14), km(b, 46)
    SVG.append(f'<path id="ga{i}" d="{pd([a0, a1])}" pathLength="1" marker-end="url(#ah)" style="fill:none;stroke:#fff;stroke-width:6;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1;opacity:0"/>')
    J.append(f'tl.set("#ga{i}", {{opacity:.9}}, {wt(2, "badh") + i * .15:.2f}); tl.to("#ga{i}", {{strokeDashoffset:0, duration:.6, ease:"power2.out"}}, {wt(2, "badh") + i * .15:.2f}); tl.to("#ga{i}", {{opacity:0, duration:.2}}, {S(3) - .2:.2f});')
SVG.insert(0, '<defs><marker id="ah" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#fff"/></marker></defs>')
pref(3, "p3", "LOW", "KAM", "SHEHAR KE PAAS PLOTS", NEAR, "Naye JDA zones &middot; infra aa raha hai", S(4))
step = 1.6 / len(NEWZ)
for i, k in enumerate(NEWZ):
    t = S(3) + .4 + step * i
    J.append(f'tl.fromTo("#nz{k}", {{opacity:0}}, {{opacity:1, duration:.2, immediateRender:false}}, {t:.2f}); tl.fromTo("#nz{k}", {{fillOpacity:.85}}, {{fillOpacity:.45, duration:.5, immediateRender:false}}, {t + .2:.2f});')
    sfx("click-soft", t, .15)
    c_ = from11(JZ["zones"][k]["ctr"]); lab(f"lz{k}", c_, ZN[k], t + .05, S(4), S(3) + 1, style="font-size:24px;padding:3px 10px")
H.append('<div id="newz">NAYE JDA ZONES &middot; 2025</div>')
J.append(f'tl.fromTo("#newz", {{opacity:0, y:20}}, {{opacity:1, y:0, duration:.3}}, {S(3) + .4:.2f}); tl.to("#newz", {{opacity:0, duration:.2}}, {S(4) - .1:.2f});')
J.append(f'tl.to(".nz", {{opacity:.15, duration:.3}}, {S(4):.2f}); tl.to("#jreg", {{opacity:.3, duration:.3}}, {S(4):.2f});')
pref(4, "p4", "COMMERCIAL", "", "MAIN ROAD PLOTS", GOLD, "Commercial &middot; frontage = value", S(5))
pref(4, "p4", "COMMERCIAL", "", "MAIN ROAD PLOTS", GOLD, "NH &middot; State Highway &middot; City main roads", S(5))
for i, k in enumerate(["nh48", "nh52", "nh21", "ring", "kalwar", "sirsi", "diggi"]):
    J.append(f'tl.to(".r_{k}", {{strokeDashoffset:0, duration:.7, ease:"power2.out"}}, {S(4) + .3 + i * .2:.2f});')
sfx("whoosh", S(4) + .3, .3)
RL = [("NH 48", (27.10, 75.97), "y"), ("NH 48", (26.78, 75.55), "y"), ("NH 52", (27.13, 75.70), "y"), ("NH 21", (26.95, 76.08), "y"),
      ("RING ROAD", (26.78, 75.70), "g"), ("STATE / CITY ROADS", (27.02, 75.48), "w")]
for i, (nm, ll, c_) in enumerate(RL):
    st = {"y": "", "g": "background:#3CE65A", "w": "background:#fff"}[c_]
    lab(f"rl{i}", wp(*ll), nm, S(4) + .7 + i * .2, S(5), S(4) + .8, cls="y" if c_ == "y" else "", style=st + ";font-size:28px")
J.append(f'tl.to(".rr", {{opacity:.25, duration:.3}}, {S(5):.2f});')

# ---------- 5 CHECKLIST ----------
H.append('<div id="chk"><b>KHARIDNE SE PEHLE</b><ul><li>&#10004; PATTA</li><li>&#10004; JDA / APPROVAL</li><li>&#10004; RERA</li></ul></div>')
J.append(f'tl.fromTo("#chk", {{opacity:0, scale:.7}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, {S(5) - .05:.2f}); tl.to("#chk", {{opacity:0, duration:.2}}, {S(6) - .1:.2f});')
for w_, i in (("patta", 0), ("approval", 1), ("RERA", 2)):
    J.append(f'tl.fromTo("#chk li:nth-child({i + 1})", {{opacity:0, x:-60}}, {{opacity:1, x:0, duration:.25, ease:"back.out(2)"}}, {wt(5, w_) - .05:.2f});'); sfx("click-soft", wt(5, w_) - .05, .4)

# ---------- 6 CTA ----------
J.append(f'tl.to(".nz", {{opacity:.8, duration:.4}}, {S(6):.2f});')
H.append('<div id="cta"><b>AAPKI PREFERENCE KYA HAI?</b><span>COMMENT &ldquo;CRORE&rdquo;</span></div>')
J.append(f'tl.to("#dim", {{opacity:.45, duration:.3}}, {S(6):.2f}); tl.fromTo("#cta", {{opacity:0, scale:.8}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)"}}, {S(6):.2f}); tl.to("#cta span", {{scale:1.08, duration:.4, yoyo:true, repeat:3}}, {wt(6, "Comment"):.2f});')
sfx("sparkle", wt(6, "Comment"), .3)


# captions
HI = ["1 crore", "risk", "holding", "High risk", "Low risk", "Agriculture land", "JDA approved", "Shehar se door", "Shehar ke paas", "naye JDA zones", "National highway", "state highway", "main road", "Commercial", "Main road", "frontage", "patta", "approval", "RERA", "Crore"]
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
H.append('<div id="cred">City boundary: Jaipur Nagar Nigam &middot; JDA zones: 2025 zone map (approx.) &middot; highways: OSM &middot; agri / door bands illustrative &middot; Educational, not financial advice &middot; Imagery: Sentinel-2 (EOX), NASA Blue Marble</div>')
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
