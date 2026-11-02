"""JDA zones reel (no voice): text-led story over the real satellite map with the official 2025 zone map fitted to it.
World units = Web-Mercator px at zoom 11, origin at tile (1450, 859)."""
import json, math, os
import numpy as np, cv2
P = "proj"
OX, OY = 1450 * 256, 859 * 256
def wp(lat, lon):
    n = 256 * 2 ** 11
    return ((lon + 180) / 360 * n - OX, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n - OY)

# ---- zone polygons: map pixels -> world (inverse of the highway-fitted affine merc->px) ----
A = np.array(json.load(open("affine_fit.json"))["merc2px"])          # [mx,my,1] @ A = [px,py]
M3 = np.eye(3); M3[:, :2] = A; Minv = np.linalg.inv(M3)
def px2w(x, y):
    m = np.array([x, y, 1.0]) @ Minv
    return (m[0] - OX, m[1] - OY)
ZP = json.load(open("zones_final_px.json"))
img = cv2.imread("supplied/zones_2025.jpg")
ZONES = {}
for k, v in ZP.items():
    poly = [px2w(*p) for p in v["poly"]]
    sx, sy = v["seed"]
    b, g, r = (int(c) for c in np.median(img[sy - 4:sy + 5, sx - 4:sx + 5].reshape(-1, 3), 0))
    a = np.array(poly); ctr = (float(a[:, 0].mean()), float(a[:, 1].mean()))
    ZONES[k] = {"poly": poly, "col": f"#{r:02x}{g:02x}{b:02x}", "ctr": ctr}
# region outline = union of zone masks
mask = np.zeros((1840, 1754), np.uint8)
for v in ZP.values(): cv2.fillPoly(mask, [np.array(v["poly"], np.int32)], 255)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
cs, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
REGION = [px2w(*p) for p in cv2.approxPolyDP(max(cs, key=cv2.contourArea), 1.5, True)[:, 0]]
ra = np.array(REGION); RC = (float((ra[:, 0].min() + ra[:, 0].max()) / 2), float((ra[:, 1].min() + ra[:, 1].max()) / 2))
RW = float(ra[:, 0].max() - ra[:, 0].min())
CORE = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "PRN N", "PRN S"]
ca = np.array([p for k in CORE for p in ZONES[k]["poly"]]); CC = (float(ca[:, 0].mean()), float(ca[:, 1].mean())); CWID = float(ca[:, 0].max() - ca[:, 0].min())

def pd(pts, close=True): return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + (" Z" if close else "")
def vb(c, w): h = w * 1920 / 1080; return f"{c[0] - w / 2:.1f} {c[1] - h / 2:.1f} {w:.1f} {h:.1f}"
S, H, J, SFX = [], [], [], []
VIEW = {"c": RC, "w": RW * 1.15}
CAMS = []
def cam(t, c, w, d=1.4, ease="power2.inOut"):
    J.append(f'tl.to("#world", {{attr:{{viewBox:"{vb(c, w)}"}}, duration:{d}, ease:"{ease}"}}, {t:.2f});'); CAMS.append((t, d, c, w))
def scr(p, t):
    c, w = RC, RW * 1.15
    for t0, d, c1, w1 in CAMS:
        if t0 + d <= t + 1e-6: c, w = c1, w1
    h = w * 1920 / 1080
    return ((p[0] - (c[0] - w / 2)) / w * 1080, (p[1] - (c[1] - h / 2)) / h * 1920)
def sfx(name, t, vol=0.5):
    SFX.append(f'<audio class="clip" src="assets/sfx/{name}.mp3" data-start="{t:.2f}" data-duration="2" data-track-index="{20 + len(SFX)}" data-volume="{vol}"></audio>')

# ---- world layers ----
S.append('<image href="assets/img/s2_z11.jpg" x="-512" y="-768" width="3328" height="4352" preserveAspectRatio="none"/>')
S.append('<image id="hi" href="assets/img/s2_z13.jpg" x="1024" y="1216" width="576" height="640" preserveAspectRatio="none" style="opacity:0"/>')
S.append('<rect id="dim" x="-2000" y="-2000" width="7000" height="7000" style="fill:#000;opacity:0.25"/>')
for k, z in ZONES.items():
    zid = "z" + k.replace(" ", "")
    S.append(f'<path id="{zid}" d="{pd(z["poly"])}" style="fill:{z["col"]};fill-opacity:.55;stroke:#fff;stroke-width:1.2;stroke-opacity:.9;opacity:0"/>')
S.append(f'<path id="region" pathLength="1" d="{pd(REGION)}" style="fill:none;stroke:#FF2D95;stroke-width:5;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1"/>')
S.append(f'<path id="regionglow" d="{pd(REGION)}" style="fill:none;stroke:#FF2D95;stroke-width:16;stroke-opacity:.35;opacity:0"/>')
for k, z in ZONES.items():
    zid = "n" + k.replace(" ", "")
    fs = 9 if k in CORE else 22
    S.append(f'<text id="{zid}" x="{z["ctr"][0]:.1f}" y="{z["ctr"][1]:.1f}" text-anchor="middle" dominant-baseline="middle" style="font:900 {fs}px Inter,Arial,sans-serif;fill:#fff;paint-order:stroke;stroke:#000;stroke-width:{fs / 5:.1f};opacity:0">{k.replace("PRN ", "PRN-")}</text>')

# ---- HTML helpers ----
def story(i, html, t, until):
    H.append(f'<div class="st" id="{i}">{html}</div>')
    J.append(f'tl.fromTo("#{i}", {{opacity:0, y:24, scale:.94}}, {{opacity:1, y:0, scale:1, duration:.28, ease:"back.out(2)"}}, {t:.2f}); tl.to("#{i}", {{opacity:0, y:-12, duration:.18}}, {until - .18:.2f});')
def chip(i, kick, text, t, until, y=270):
    H.append(f'<div class="chip" id="{i}" style="top:{y}px"><b>{kick}</b>{text}</div>')
    J.append(f'tl.fromTo("#{i}", {{opacity:0, x:-40}}, {{opacity:1, x:0, duration:.35, ease:"power3.out"}}, {t:.2f}); tl.to("#{i}", {{opacity:0, duration:.25}}, {until - .25:.2f});')
def photo(i, src, cap, credit, t, until, x=60, y=330, w=960, h=640, fit="cover"):
    H.append(f'<div class="ph" id="{i}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px"><img src="assets/img/{src}" style="object-fit:{fit}"/><div class="pc">{cap}<em>{credit}</em></div></div>')
    J.append(f'tl.fromTo("#{i}", {{opacity:0, scale:.7, rotation:-2}}, {{opacity:1, scale:1, rotation:0, duration:.45, ease:"back.out(1.6)"}}, {t:.2f}); tl.to("#{i}", {{opacity:0, scale:.92, duration:.3}}, {until - .3:.2f});')
    sfx("pop", t, 0.35)
def label(i, p, text, t, until, at=None, cls=""):
    x, y = scr(p, at if at is not None else t + 1.5)
    H.append(f'<div class="lab {cls}" id="{i}" style="left:{x:.0f}px;top:{y:.0f}px">{text}</div>')
    J.append(f'tl.fromTo("#{i}", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, {t:.2f}); tl.to("#{i}", {{opacity:0, duration:.2}}, {until - .2:.2f});')
def zon(k, t, op=1, d=.3): J.append(f'tl.to("#z{k.replace(" ", "")}", {{opacity:{op}, duration:{d}}}, {t:.2f});')
def num(k, t, op=1, d=.3): J.append(f'tl.to("#n{k.replace(" ", "")}", {{opacity:{op}, duration:{d}}}, {t:.2f});')

Y = '<span class="y">'; E = '</span>'
ALL = list(ZONES)
OUTER = ["15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25"]

# B0 0–3.2 · hook
# ---- voice timeline (words.json from Ashwil's recording) ----
import re as _re
words = [{"t": w["text"], "s": w["start"]} for w in json.load(open("words.json"))]
END = round(words[-1]["s"] + 0.75, 2)
def cue(*seq, after=0.0):
    seq = [s.lower() for s in seq]
    for i, w in enumerate(words):
        if w["s"] < after: continue
        if all(i + k < len(words) and _re.sub(r"[^\w]", "", words[i + k]["t"].lower()).startswith(seq[k]) for k in range(len(seq))): return w["s"]
    raise KeyError(seq)
K = {n: cue(*s) for n, s in {"oct": ("in", "october"), "before": ("before",), "now": ("now", "27"), "tf": ("twentyfive",), "add": ("add", "them"),
     "four": ("that", "is", "four"), "know": ("the", "jaipur", "you"), "z3": ("zone", "3"), "big": ("and", "the", "biggest"), "front": ("now", "look"),
     "all": ("all", "of", "this"), "stop": ("and", "it", "may"), "bhaskar": ("bhaskar",), "why": ("so", "why"), "one": ("1", "approval"), "two": ("2", "conversion"),
     "three": ("3", "rules"), "test": ("so", "quick"), "jag": ("jagatpura",), "vai": ("vaishali",), "man": ("mansarovar",), "tonk": ("tonk",),
     "which": ("which", "zone", "are"), "comment": ("comment",), "send": ("send", "this")}.items()}
FACE_END = K["oct"] - 0.15

# 0 · cover thumbnail (0–0.55), then face full-screen for the opening line
H2 = []
ra_ = np.array(REGION); bx0, by0 = ra_.min(0); bx1, by1 = ra_.max(0)
CVS = min(700 / (bx1 - bx0), 700 / (by1 - by0)); CVX, CVY = 1040 - (bx1 - bx0) * CVS, 760
def cvp(p): return (CVX + (p[0] - bx0) * CVS, CVY + (p[1] - by0) * CVS)
def cvd(pts): return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in map(cvp, pts)) + " Z"
cvsvg = "".join(f'<path d="{cvd(z["poly"])}" style="fill:{"rgba(243,231,211,.13)" if k in CORE else "none"};stroke:rgba(243,231,211,.28);stroke-width:1.5"/>' for k, z in ZONES.items())
cvsvg += f'<path d="{cvd(REGION)}" style="fill:rgba(245,176,74,.06);stroke:#F5B04A;stroke-width:7;stroke-linejoin:round;filter:url(#cvglow)"/>'
tags = ""
for k, lab, dx, dy in [("15", "SHAHPURA", -60, -30), ("16", "CHOMU", -150, -20), ("20", "DUDU", -40, -10), ("21", "PHAGI", -60, 10), ("23", "CHAKSU", -40, 30), ("24", "BASSI", -20, 0)]:
    x, y = cvp(ZONES[k]["ctr"]); cvsvg += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" style="fill:#F5B04A"/>'
    tags += f'<div class="cvtag" style="left:{min(900, max(40, x + dx)):.0f}px;top:{y + dy + 14:.0f}px">{lab}</div>'
x, y = cvp(CC); tags += f'<div class="cvtag hot" style="left:{x - 95:.0f}px;top:{y - 70:.0f}px">JAIPUR</div>'
H2.append('<div id="cover"><svg id="cvgrid" width="1080" height="1920"><defs><pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="rgba(243,231,211,.07)"/></pattern>'
          '<filter id="cvglow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
          f'<rect width="1080" height="1920" fill="url(#dots)"/>{cvsvg}</svg>'
          '<div id="cvt">JDA<br/><span>ZONES</span></div><div id="cvs">Jaipur, redrawn.<br/>now bigger than Goa</div>'
          f'{tags}<div id="cvpill">14 → 27 zones · 5,994 sq km</div></div>')
J.append('tl.set("#cover", {opacity:1}, 0); tl.to("#cover", {opacity:0, duration:.25}, 0.55);')
J.append(f'tl.set("#world", {{attr:{{viewBox:"{vb(RC, RW * 1.6)}"}}}}, 0);')
J.append(f'tl.set("#maplayer", {{opacity:0}}, 0); tl.set("#maplayer", {{opacity:1}}, {FACE_END:.2f});')
J.append(f'tl.fromTo("#avatar", {{opacity:1, scale:1}}, {{opacity:0, scale:1.08, duration:.6, ease:"power2.in"}}, {FACE_END:.2f});')
H2.append('<div id="hook"><b>JAIPUR IS NOW<br/>BIGGER THAN <i class="y">GOA</i></b></div>')
J.append(f'tl.fromTo("#hook", {{opacity:0, scale:1.15}}, {{opacity:1, scale:1, duration:.4, ease:"back.out(2)"}}, 0.6); tl.to("#hook", {{opacity:0, duration:.3}}, {FACE_END - 0.3:.2f});')
sfx("impact-bass-1", 0.55, 0.5)

# B1 · office order: map comes alive
t0 = FACE_END
cam(t0, RC, RW * 1.15, 2.4, "power2.out")
J.append(f'tl.to("#region", {{strokeDashoffset:0, duration:1.6, ease:"power2.inOut"}}, {t0 + .1:.2f});')
for i, k in enumerate(ALL): zon(k, t0 + .4 + 0.04 * i, 1, .2)
for k in ALL: zon(k, t0 + 2.2, 0.15, .4)
chip("c1", "JDA OFFICE ORDER", "Dated 10 October 2025", t0 + .2, K["before"])
photo("pjda", "jda.jpg", "Jaipur Development Authority", "Image supplied", K["oct"] + 1.6, K["before"], x=60, y=430, w=960, h=620)
sfx("riser", t0, 0.25)

# B2 · before
photo("pold", "zones_old.jpg", "BEFORE · the old JDA zone map", "Image supplied", K["before"], K["now"], x=170, y=270, w=740, h=1000, fit="contain")
sfx("whoosh-short", K["before"] - .1, 0.4)

# B3 · now 27
H.append('<div id="count"><span id="cnum">14</span><em>ZONES</em></div>')
J.append(f'tl.fromTo("#count", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)"}}, {K["now"] - .1:.2f}); tl.to("#count", {{opacity:0, duration:.3}}, {K["add"] - .3:.2f});')
J.append(f'const cn={{v:14}}; tl.to(cn, {{v:27, duration:{K["now"] + 0.65 - K["now"]:.2f}, ease:"none", onUpdate:()=>{{document.getElementById("cnum").textContent=Math.round(cn.v)}}}}, {K["now"]:.2f});')
order = sorted(ALL, key=lambda k: math.hypot(ZONES[k]["ctr"][0] - CC[0], ZONES[k]["ctr"][1] - CC[1]))
for i, k in enumerate(order):
    t = K["now"] + 2.2 * i / len(order); zon(k, t, 1, .15); num(k, t, 1, .15)
    if i % 3 == 0: sfx("click-soft", t, 0.3)
J.append(f'tl.to(["#zPRNN", "#zPRNS"], {{fillOpacity:1, duration:.3, yoyo:true, repeat:5}}, {K["tf"] + 1.2:.2f});')

# B4 · 6000 sq km
J.append(f'tl.to("#regionglow", {{opacity:1, duration:.4, yoyo:true, repeat:5}}, {K["add"]:.2f});')
for k in ALL: num(k, K["add"] - .1, 0, .3)
H.append('<div id="bars"><b>AREA · SQ KM</b>'
         '<div class="br"><i>JDA region</i><s style="width:100%"></s><u>5,994</u></div>'
         '<div class="br"><i>Goa (state)</i><s style="width:61.8%"></s><u>3,702</u></div>'
         '<div class="br"><i>Delhi (NCT)</i><s style="width:24.8%"></s><u>1,484</u></div></div>')
J.append(f'tl.fromTo("#bars", {{opacity:0, y:-20}}, {{opacity:1, y:0, duration:.35}}, {K["add"] + .2:.2f}); tl.from("#bars s", {{scaleX:0, transformOrigin:"0 50%", duration:.8, stagger:.25, ease:"power3.out"}}, {K["add"] + .4:.2f}); tl.to("#bars", {{opacity:0, duration:.3}}, {K["four"] - .15:.2f});')
# true-scale overlays: Delhi ×4 and Goa, projected into this map (km → world px at Jaipur's latitude)
OUTL = json.load(open("outlines_km.json")); PXKM = 256 * 2 ** 11 / 360 / (111.32 * math.cos(math.radians(26.9)))
def shape(nm, at): return ["M" + " L".join(f"{at[0] + x * PXKM:.1f} {at[1] + y * PXKM:.1f}" for x, y in r) + " Z" for r in OUTL[nm]]
DOFF = [(-365, -390), (365, -390), (-365, 390), (365, 390)]
for i, (dx, dy) in enumerate(DOFF):
    at = (RC[0] + dx + 39, RC[1] + dy + 80 - 23)
    S.append(f'<path id="delhi{i}" d="{" ".join(shape("delhi", at))}" style="fill:#4FC3F7;fill-opacity:.45;stroke:#fff;stroke-width:5;opacity:0"/>')
    J.append(f'tl.fromTo("#delhi{i}", {{opacity:0}}, {{opacity:1, duration:.25}}, {K["four"] + .05 + .3 * i:.2f}); tl.to("#delhi{i}", {{opacity:0, duration:.3}}, {cue("bigger", after=K["four"]) - .1:.2f});')
    sfx("pop", K["four"] + .05 + .3 * i, .3)
for k in ALL: zon(k, K["four"], .12, .3)
label("ldelhi", (RC[0], RC[1] + 80), "<span class='y'>4×</span> DELHI", K["four"] + 1.0, cue("bigger", after=K["four"]) - .05, at=K["four"], cls="big2")
S.append(f'<path id="goa" d="{" ".join(shape("goa", (RC[0] - 129, RC[1] + 152)))}" style="fill:#FF9F43;fill-opacity:.5;stroke:#fff;stroke-width:5;opacity:0"/>')
TG = cue("bigger", after=K["four"])
J.append(f'tl.fromTo("#goa", {{opacity:0}}, {{opacity:1, duration:.35}}, {TG:.2f}); tl.to("#goa", {{opacity:0, duration:.3}}, {K["know"] - .1:.2f});')
label("lgoa", (RC[0], RC[1] + 60), "GOA<br/><span class='y'>3,702 sq km</span>", TG + .3, K["know"] - .05, at=TG, cls="big2")
sfx("whoosh-short", TG, .35)
sfx("whoosh", K["add"], 0.3)

# B5 · the core
cam(K["know"], CC, CWID * 1.9, 1.8)
J.append(f'tl.to("#hi", {{opacity:1, duration:.8}}, {K["know"] + .2:.2f});')
for k in ALL:
    if k not in CORE: zon(k, K["know"], 0.12, .5)
for k in CORE: zon(k, K["know"] + .3, .45, .4); num(k, K["know"] + 1.0, 1, .3)
T19 = cue("1", "to", "9"); TPRN = cue("plus", "prithviraj", after=T19)
for i, k in enumerate(["1", "2", "3", "4", "5", "6", "7", "8", "9"]):
    t = T19 - .1 + 0.11 * i
    J.append(f'tl.to("#z{k}", {{fill:"#FFE03A", fillOpacity:.85, stroke:"#FFE03A", strokeWidth:3, duration:.18}}, {t:.2f}); tl.to("#z{k}", {{fill:"{ZONES[k]["col"]}", fillOpacity:.55, stroke:"#fff", strokeWidth:1.2, duration:.4}}, {t + .9:.2f});')
    sfx("click-soft", t, .3)
J.append(f'tl.to(["#zPRNN", "#zPRNS"], {{fillOpacity:.9, fill:"#FFE03A", stroke:"#FFE03A", strokeWidth:3, duration:.2, yoyo:true, repeat:3}}, {TPRN + .2:.2f});')
J.append(f'tl.to("#z3", {{fillOpacity:1, duration:.35, yoyo:true, repeat:5}}, {K["z3"]:.2f});')
for k in CORE:
    if k != "3": zon(k, K["z3"], .3, .3)
label("l3", ZONES["3"]["ctr"], "ZONE 3 · 2 SQ KM", K["z3"], K["big"], at=K["know"] + 2, cls="big")
sfx("ping", K["z3"], 0.4)

# B6 · the giant
cam(K["big"], RC, RW * 1.15, 1.6)
J.append(f'tl.to("#hi", {{opacity:0, duration:.6}}, {K["big"]:.2f});')
for k in CORE: num(k, K["big"], 0, .2); zon(k, K["big"], .15, .4)
zon("13", K["big"] + .6, 1, .4); num("13", K["big"] + .6, 1, .3)
J.append(f'tl.to("#z13", {{fillOpacity:.9, duration:.4, yoyo:true, repeat:5}}, {K["big"] + 1.2:.2f});')
label("l13", ZONES["13"]["ctr"], "AMER &amp;<br/>JAMWARAMGARH<br/><span class='y'>596 SQ KM</span>", K["big"] + 1.6, K["front"], at=K["big"] + 2)
sfx("whoosh-short", K["big"], 0.35)

# B7 · the new frontier (zones light as each name is spoken)
zon("13", K["front"], .15, .4); num("13", K["front"], 0, .2)
NAMES = {"15": "Shahpura", "16": "Chomu", "17": "Jalsoo", "18": "Jobner", "19": "Mozmabad", "20": "Dudu", "21": "Phagi", "22": "Madhorajpura", "23": "Chaksu", "24": "Bassi · Toonga", "25": "Andhi"}
SPOKEN = {"15": "shahpura", "16": "chomu", "17": "jalsoo", "18": "jobner", "20": "dudu", "21": "phagi", "22": "madhorajpura", "23": "chaksu", "24": "bassi", "25": "andhi"}
TT = {k: cue(v) - .1 for k, v in SPOKEN.items()}; TT["19"] = TT["20"]
for k in OUTER:
    t = TT[k]
    zon(k, t, 1, .25); label(f"lo{k}", ZONES[k]["ctr"], f"{k} · {NAMES[k]}", t, K["stop"], at=K["front"] + 1.5, cls="sm")
    sfx("pop", t, 0.22)
J.append(f'tl.to("#z24", {{fillOpacity:1, duration:.3, yoyo:true, repeat:1}}, {cue("toonga") - .1:.2f});')
J.append(f'tl.to("#regionglow", {{opacity:1, duration:.35, yoyo:true, repeat:3}}, {K["all"]:.2f});')

# B8 · may grow again
for k in OUTER: zon(k, K["stop"], .3, .4)
photo("pnews", "news.jpg", "Master Plan 2047 report", "Dainik Bhaskar · image supplied", K["stop"] + .3, K["why"], x=140, y=270, w=800, h=1060, fit="contain")
J.append(f'tl.to("#pnews img", {{scale:1.9, x:90, y:-330, duration:1.2, ease:"power2.inOut"}}, {K["bhaskar"] + .8:.2f});')

# B9 · why it matters
J.append(f'tl.to("#dim", {{opacity:.6, duration:.5}}, {K["why"]:.2f});')
sfx("impact-bass-1", K["why"], 0.4)
chip("w1", "① APPROVAL", "Check the scheme's approval — roads, layout &amp; patta", K["one"], K["two"])
photo("pscheme", "scheme.jpg", "An approved scheme layout", "Image supplied · branding cropped", K["one"] + .3, cue("patta") - .2, x=190, y=470, w=700, h=780)
photo("psite", "siteplan.jpg", "JDA site plan · approved scheme", "Riyasat Town, Chaksu · Zone 14 · image supplied", cue("patta") - .1, K["two"], x=170, y=440, w=740, h=1000, fit="contain")
chip("w2", "② CONVERSION", "Farm land needs 90-A conversion before you can build", K["two"], K["three"])
photo("p90a", "ninety_a.jpg", "Why 90-A matters", "Image supplied", cue("90a") - .3, K["three"], x=210, y=440, w=660, h=880)
chip("w3", "③ RULES", "Setbacks, FAR &amp; height depend on your zone &amp; the master plan", K["three"], K["test"])
for t in (K["one"], K["two"], K["three"]): sfx("whoosh-short", t, 0.3)

# B10 · quiz
J.append(f'tl.to("#dim", {{opacity:.25, duration:.5}}, {K["test"]:.2f});')
QUIZ = [("jagatpura.jpg", "Jagatpura", "Image supplied", "jag"), ("vaishali.jpg", "Vaishali Nagar", "Image supplied", "vai"),
        ("mansarovar.jpg", "Mansarovar", "Pacific Jaipur · rendering · image supplied", "man"), ("tonk.jpg", "Tonk Road", "Image supplied", "tonk")]
nxt = [K["vai"], K["man"], K["tonk"], K["comment"]]
for i, (src, nm, cr, key) in enumerate(QUIZ):
    photo(f"q{i}", src, f"{nm} → <span class='y'>Zone ?</span>", cr, K[key] - .15, nxt[i] - .1, x=90, y=330, w=900, h=900)

# B11 · CTA
H2.append('<div id="share"><svg viewBox="0 0 24 24" width="84" height="84"><path d="M3 11l18-8-8 18-2-8z" style="fill:none;stroke:#fff;stroke-width:2;stroke-linejoin:round"/></svg><span>Send to someone buying a plot</span></div>')
J.append(f'tl.fromTo("#share", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.4, ease:"back.out(2)"}}, {K["send"]:.2f}); tl.fromTo("#share svg", {{scale:1}}, {{scale:1.18, duration:.45, yoyo:true, repeat:5}}, {K["send"] + .5:.2f});')
chip("ccta", "COMMENT BELOW", "Your area → I'll tell you your zone", K["comment"], END + .3)
for k in ALL: zon(k, K["comment"], .6, .6)
sfx("sparkle", K["comment"], 0.35)

# captions (verbatim, bottom)
EMW = {"goa", "goa.", "october", "2025,", "14", "27.", "twenty-five", "prithviraj", "6000", "four", "delhi,", "3", "2", "13,", "frontier", "jda", "2047,", "272",
       "approval.", "conversion.", "rules.", "90-a", "jda-approved", "zone", "zones", "jaipur.", "comment"}
def glen(g): return len(" ".join(w["t"] for w in g))
groups, cur = [], []
for i, w in enumerate(words):
    cur.append(w); nx = words[i + 1] if i + 1 < len(words) else None
    if nx is None or glen(cur + [nx]) > 22 or w["t"][-1] in ".?!" or (w["t"][-1] == "," and glen(cur) >= 10) or (nx["s"] - w["s"] > 1.0):
        groups.append(cur); cur = []
CAPS = []
for gi, g in enumerate(groups):
    nx = groups[gi + 1][0]["s"] - 0.03 if gi + 1 < len(groups) else END
    a, b = round(max(0.6, g[0]["s"] - 0.05), 2), round(min(nx, g[-1]["s"] + 0.8), 2)
    CAPS.append((a, b, " ".join(w["t"] for w in g)))
    H2.append(f'<div class="cp" id="cp{gi}">' + " ".join(f'<span class="{"y" if w["t"].lower() in EMW else ""}">{w["t"]}</span>' for w in g) + '</div>')
    J.append(f'tl.fromTo("#cp{gi}", {{opacity:0, scale:.92}}, {{opacity:1, scale:1, duration:.12}}, {a}); tl.to("#cp{gi}", {{opacity:0, duration:.06}}, {b - .06:.2f});')
json.dump([{"start": a, "end": b, "text": t} for a, b, t in CAPS], open("captions.json", "w"), indent=0)

H.append('<div id="brand">ASHWILLPOWER · JAIPUR REAL ESTATE</div>')
H.append('<div id="credit">Satellite: Sentinel-2 cloudless 2016 by EOX (CC BY 4.0) · Zones: JDA office order 10.10.2025 map, fitted to OSM highways (approx.)</div>')

CSS = """*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#0b0d10}
#root{position:relative;width:1080px;height:1920px;overflow:hidden}#avatar{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover}#maplayer{position:absolute;inset:0}.cp{position:absolute;left:50px;right:50px;top:1500px;text-align:center;opacity:0;font:900 72px/1.08 Inter,Arial,sans-serif;color:#fff;text-shadow:0 4px 0 #000,0 0 18px rgba(0,0,0,.95),0 0 4px #000}#cover{position:absolute;inset:0;opacity:0;overflow:hidden;background:radial-gradient(120% 80% at 70% 35%,#2B2016 0%,#1B140F 55%,#120d09 100%)}#cvgrid{position:absolute;inset:0}#cvt{position:absolute;left:70px;right:70px;top:250px;font:900 170px/0.92 Inter,sans-serif;letter-spacing:-0.01em;color:#F3E7D3;text-shadow:0 8px 40px rgba(0,0,0,.6)}#cvt span{color:#F5B04A}#cvs{position:absolute;left:76px;right:70px;top:620px;font:800 52px/1.1 Inter,sans-serif;color:#F3E7D3}.cvtag{position:absolute;padding:8px 16px;border-radius:12px;background:rgba(40,26,12,.92);border:2px solid #E3A23B;font:800 30px Inter,sans-serif;color:#F3E7D3;white-space:nowrap}.cvtag.hot{background:#F5B04A;color:#1B140F;border-color:#F5B04A;font-size:34px}#cvpill{position:absolute;left:76px;top:1560px;padding:12px 22px;border-radius:14px;background:rgba(60,38,14,.92);border:2px solid #E3A23B;font:800 40px Inter,sans-serif;color:#F3E7D3}#world{position:absolute;inset:0;width:1080px;height:1920px}
.y{color:#FFE03A}
.st{position:absolute;left:50px;right:50px;top:1470px;text-align:center;opacity:0;font:900 74px/1.08 Inter,Arial,sans-serif;color:#fff;text-shadow:0 4px 0 #000,0 0 20px rgba(0,0,0,.95),0 0 4px #000}
#hook{position:absolute;left:0;right:0;top:250px;text-align:center;opacity:0;font-family:Inter,Arial,sans-serif;text-shadow:0 5px 0 #000,0 0 26px rgba(0,0,0,.9)}
#hook i{font-style:normal}#hook b{display:block;font-weight:900;font-size:104px;line-height:.98;color:#fff}#hook span{display:block;margin-top:16px;font-weight:800;font-size:46px;color:#fff}
.chip{position:absolute;left:60px;right:60px;opacity:0;padding:20px 28px;border-radius:20px;background:rgba(10,12,16,.86);border-left:10px solid #FFE03A;font:800 42px/1.15 Inter,Arial,sans-serif;color:#fff}
.chip b{display:block;font:700 26px "JetBrains Mono",monospace;letter-spacing:.16em;color:#FFE03A;margin-bottom:6px}
.ph{position:absolute;opacity:0;border-radius:22px;overflow:hidden;border:5px solid #FFE03A;box-shadow:0 18px 50px rgba(0,0,0,.7);background:#111}
.ph img{width:100%;height:100%;display:block}.pc{position:absolute;left:0;right:0;bottom:0;padding:40px 20px 12px;background:linear-gradient(180deg,transparent,rgba(0,0,0,.88));font:900 46px Inter,Arial,sans-serif;color:#fff}
.pc em{display:block;font-style:normal;font-weight:600;font-size:22px;color:#ddd;margin-top:4px}
.lab{position:absolute;opacity:0;transform-origin:50% 50%;translate:-50% -50%;font:900 38px/1.05 Inter,Arial,sans-serif;color:#fff;text-align:center;white-space:nowrap;text-shadow:0 3px 0 #000,0 0 14px rgba(0,0,0,.95)}
.lab.big2{font-size:66px;line-height:1}.lab.big{font-size:64px;color:#FFE03A;translate:-50% -170%}.lab.sm{font-size:30px}
#count{position:absolute;left:0;right:0;top:250px;text-align:center;opacity:0;font-family:Inter,Arial,sans-serif;text-shadow:0 6px 0 #000,0 0 30px rgba(0,0,0,.9)}
#count span{display:block;font-weight:900;font-size:230px;line-height:1;color:#FFE03A}#count em{display:block;font-style:normal;font:700 40px "JetBrains Mono",monospace;letter-spacing:.3em;color:#fff}
#bars{position:absolute;left:60px;right:60px;top:250px;opacity:0;padding:26px 30px;border-radius:22px;background:rgba(10,12,16,.88);font-family:Inter,Arial,sans-serif;color:#fff}
#bars>b{display:block;font:700 26px "JetBrains Mono",monospace;letter-spacing:.16em;color:#FFE03A;margin-bottom:14px}
.br{display:grid;grid-template-columns:240px 1fr 150px;align-items:center;gap:16px;margin:12px 0}.br i{font-style:normal;font-weight:800;font-size:34px}
.br s{display:block;height:40px;border-radius:8px;background:#FF2D95}.br:nth-child(3) s,.br:nth-child(4) s{background:#8a94a6}.br u{text-decoration:none;font-weight:900;font-size:40px;text-align:right}
#share{position:absolute;left:0;right:0;top:1180px;display:flex;flex-direction:column;align-items:center;gap:12px;opacity:0;font:900 42px Inter,Arial,sans-serif;color:#fff;text-shadow:0 3px 0 #000}
#share svg{background:#FFB000;border-radius:50%;padding:16px;box-shadow:0 0 0 12px rgba(255,176,0,.3)}
#brand{position:absolute;left:0;right:0;top:150px;text-align:center;font:700 24px "JetBrains Mono",monospace;letter-spacing:.2em;color:rgba(255,255,255,.85);text-shadow:0 2px 6px #000}
#credit{position:absolute;left:40px;right:40px;bottom:90px;text-align:center;font:500 19px "JetBrains Mono",monospace;color:rgba(255,255,255,.72);text-shadow:0 1px 3px #000}"""
FONTS = '@font-face{font-family:"Instrument Serif";src:url(assets/fonts/instrument-serif-latin-400-normal.woff2)}@font-face{font-family:"Instrument Serif";font-style:italic;src:url(assets/fonts/instrument-serif-latin-400-italic.woff2)}'
open(f"{P}/index.html", "w").write(f"""<!doctype html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script><style>{FONTS}{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="30">
<video id="avatar" class="clip" src="assets/avatar.mp4" data-start="0" data-duration="{END}" data-track-index="0" playsinline data-has-audio="true" data-volume="1"></video>
<div id="maplayer"><svg id="world" viewBox="{vb(RC, RW * 1.6)}" preserveAspectRatio="xMidYMid slice">{"".join(S)}</svg>
{"".join(H)}</div>
{"".join(H2)}
<audio id="music" class="clip" src="assets/music_tune.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.22" data-fade-in="0.5" data-fade-out="2.0"></audio>
{"".join(SFX)}
</div><script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(J)}
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>""")
STORY = [("s0", 0.4, 3.2)]
print("END", END, "zones", len(ZONES), "RW", round(RW), "core w", round(CWID))
