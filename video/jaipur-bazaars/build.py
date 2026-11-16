"""Jaipur bazaars reel — Walled City (stylised) on satellite. Street lines approximate."""
import json, math, os
P = "proj"
LINES = [
    "Jaipur aaye aur galat bazaar chala gaya, toh paisa bhi zyada, aur cheez bhi wo nahi milegi. Yeh rahi list.",
    "Johari Bazaar: gold, kundan aur gems ki jewellery.",
    "Bapu Bazaar: kapde, Sanganeri print aur Jaipuri juttiyan.",
    "Nehru Bazaar: juttiyan aur sasta fabric.",
    "Tripolia Bazaar: brass aur lohe ka saamaan, aur bartan.",
    "Maniharon ka Rasta: lakh ki chudiyan.",
    "Chandpole aur Khajane Walon ka Rasta: marble ki murtiyan aur handicraft.",
    "Kishanpole Bazaar: bandhej aur leheriya.",
    "Chaura Rasta: kitaabein aur stationery.",
    "Aur thoda bahar, Sanganer aur Bagru: hand block print.",
    "Yeh saare bazaar 300 saal pehle plan kiye gaye the, har galli ek kaam ke liye. Isliye aaj bhi Walled City ki dukaanein Jaipur ki sabse keemti commercial property mein ginti hain.",
    "Aapka favourite bazaar kaunsa hai? Comment karo.",
]
VOICE = os.path.exists("rec/phrases.json")
if VOICE: PH = json.load(open("rec/phrases.json"))
else:
    PH = []; t = .3
    for l in LINES:
        d = len(l) / 15 + .15; PH.append({"s": round(t, 2), "e": round(t + d, 2), "t": l}); t += d + .3
N = len(PH)
def S(k): return PH[k]["s"]
def E(k): return PH[k]["e"]
def wt(k, w):
    t = PH[k]["t"]; i = t.lower().find(w.lower()); assert i >= 0, (k, w)
    return S(k) + (E(k) - S(k)) * i / len(t)
END = round(E(N - 1) + 1.0, 2)
def wp(lat, lon):
    n = 2 ** 13
    return (((lon + 180) / 360 * n) - 5791) * 256, (((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n) - 3466) * 256
SVG, H, J, SFX, IN = [], [], [], [], []
def sfx(n, t, v=.3): SFX.append(f'<audio id="sx{len(SFX)}" class="clip" src="assets/sfx/{n}.mp3" data-start="{t:.2f}" data-duration="2" data-track-index="{20 + len(SFX)}" data-volume="{v}"></audio>')
def pd(pts, close=False): return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + (" Z" if close else "")
GOLD, CREAM, PINK = "#C9A24A", "#F3E6C8", "#E8908A"

C0 = wp(26.9225, 75.8235); CW = 130
CH = CW * 1920 / 1080
def vb(c, w): h = w * 1920 / 1080; return f"{c[0] - w / 2:.2f} {c[1] - h / 2:.2f} {w:.2f} {h:.2f}"
U = CW / 1080

# base: satellite (dim) + warm tint
SVG.append('<rect x="-900000" y="-900000" width="2000000" height="2000000" style="fill:#15110d"/>')
SVG.append('<image href="assets/img/jp14.webp" x="7040" y="-2176" width="1536" height="1792" preserveAspectRatio="none" style="opacity:.4"/>')
SVG.append('<rect x="-900000" y="-900000" width="2000000" height="2000000" style="fill:#2a1a10;opacity:.45"/>')
# walled city outline (approx)
WALL = [wp(*p) for p in [(26.9330, 75.8050), (26.9300, 75.8045), (26.9200, 75.8060), (26.9160, 75.8110), (26.9155, 75.8290), (26.9175, 75.8400), (26.9235, 75.8410), (26.9300, 75.8380), (26.9340, 75.8300), (26.9345, 75.8150)]]
SVG.append(f'<path id="wall" d="{pd(WALL, True)}" pathLength="1" style="fill:{PINK};fill-opacity:0;stroke:{PINK};stroke-width:{U * 5:.2f};stroke-dasharray:1;stroke-dashoffset:1;stroke-linejoin:round"/>')
# minor grid (chokri streets) for texture
for lon in (75.8135, 75.8165, 75.8235, 75.8300, 75.8345):
    SVG.append(f'<path class="grid" d="{pd([wp(26.9160, lon), wp(26.9300, lon)])}" style="stroke:#F3E6C8;stroke-width:1.5;stroke-opacity:.0;vector-effect:non-scaling-stroke"/>')
for lat in (26.9200, 26.9275):
    SVG.append(f'<path class="grid" d="{pd([wp(lat, 75.8080), wp(lat, 75.8380)])}" style="stroke:#F3E6C8;stroke-width:1.5;stroke-opacity:.0;vector-effect:non-scaling-stroke"/>')

BZ = {  # key: (label, points, line index, keyword)
    "johari": ("JOHARI BAZAAR", [(26.9240, 75.8277), (26.9200, 75.8274), (26.9160, 75.8270)], 1),
    "bapu": ("BAPU BAZAAR", [(26.9166, 75.8205), (26.9164, 75.8235), (26.9162, 75.8268)], 2),
    "nehru": ("NEHRU BAZAAR", [(26.9168, 75.8140), (26.9167, 75.8172), (26.9166, 75.8205)], 3),
    "tripolia": ("TRIPOLIA BAZAAR", [(26.9246, 75.8197), (26.9243, 75.8237), (26.9240, 75.8277)], 4),
    "manihar": ("MANIHARON KA RASTA", [(26.9243, 75.8252), (26.9222, 75.8251), (26.9205, 75.8250)], 5),
    "chandpole": ("CHANDPOLE BAZAAR", [(26.9262, 75.8085), (26.9254, 75.8140), (26.9246, 75.8197)], 6),
    "khajane": ("KHAJANE WALON KA RASTA", [(26.9254, 75.8128), (26.9235, 75.8127), (26.9215, 75.8126)], 6),
    "kishanpole": ("KISHANPOLE BAZAAR", [(26.9246, 75.8197), (26.9205, 75.8190), (26.9168, 75.8180)], 7),
    "chaura": ("CHAURA RASTA", [(26.9244, 75.8228), (26.9205, 75.8226), (26.9168, 75.8222)], 8),
}
BP = {}
for k, (lab, pts, li) in BZ.items():
    P_ = [wp(*p) for p in pts]; BP[k] = P_
    SVG.append(f'<path class="bzg" id="bg_{k}" d="{pd(P_)}" pathLength="1" style="fill:none;stroke:{GOLD};stroke-width:{U * 26:.2f};stroke-opacity:.35;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1;opacity:0"/>'
               f'<path class="bz" id="bz_{k}" d="{pd(P_)}" pathLength="1" style="fill:none;stroke:#F7E3A8;stroke-width:{U * 9:.2f};stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1;opacity:0;filter:drop-shadow(0 0 6px {GOLD})"/>')
HAWA = wp(26.9239, 75.8267)
SVG.append(f'<g id="hawa" style="opacity:0"><circle cx="{HAWA[0]:.2f}" cy="{HAWA[1]:.2f}" r="{U * 10:.2f}" style="fill:{PINK};stroke:#fff;stroke-width:3;vector-effect:non-scaling-stroke"/></g>')

# 3D-ish plane
def plane(t, rx, sc, x, y, d=1.0): J.append(f'tl.to("#plane", {{rotationX:{rx}, scale:{sc}, x:{x}, y:{y}, duration:{d}, ease:"power2.inOut"}}, {t:.2f});')
def scr(p):  # base screen coords of a world point (before plane transform)
    return ((p[0] - (C0[0] - CW / 2)) / CW * 1080, (p[1] - (C0[1] - CH / 2)) / CH * 1920)
J.append('tl.set("#plane", {rotationX:32, scale:1, x:0, y:0, transformOrigin:"50% 55%"}, 0);')

def lux(i, html, t, until, x, y, cls=""):
    H.append(f'<div class="lx {cls}" id="lx{i}" style="left:{x}px;top:{y}px">{html}</div>')
    J.append(f'tl.fromTo("#lx{i}", {{opacity:0, y:24, clipPath:"inset(0 100% 0 0)"}}, {{opacity:1, y:0, clipPath:"inset(0 0% 0 0)", duration:.45, ease:"power3.out"}}, {t:.2f}); tl.to("#lx{i}", {{opacity:0, y:-14, duration:.3}}, {until - .3:.2f});')
    sfx("click-soft", t, .3)

# ---------- 0 HOOK ----------
J.append('tl.fromTo("#plane", {rotationX:10, scale:.3}, {rotationX:32, scale:.48, y:80, duration:1.6, ease:"power3.out"}, 0);')
J.append(f'tl.to("#wall", {{strokeDashoffset:0, duration:1.4, ease:"power2.inOut"}}, .2); tl.to("#wall", {{fillOpacity:.12, duration:.6}}, 1.2); tl.to(".grid", {{strokeOpacity:.25, duration:.6, stagger:.05}}, 1.0);')
H.append('<div id="hook"><small>JAIPUR KE BAZAAR</small><b>KAHAN KYA<br/>MILTA HAI?</b><span>&#9888; galat bazaar = zyada paisa</span></div>')
J.append(f'tl.fromTo("#hook", {{opacity:0, scale:1.12}}, {{opacity:1, scale:1, duration:.45, ease:"power3.out"}}, 0); tl.fromTo("#hook span", {{opacity:0, y:16}}, {{opacity:1, y:0, duration:.35}}, {wt(0, "galat") - .1:.2f}); tl.to("#hook", {{opacity:0, y:-30, duration:.3}}, {S(1) - .2:.2f});')
lux(0, "WALLED CITY &middot; <b>PINK CITY</b>", 1.4, S(1) - .1, 250, 1300)
sfx("impact-bass-1", 0, .45); sfx("whoosh", .2, .3)

# ---------- bazaars ----------
ITEM = {
    "johari": ("&#128142;", "GOLD &middot; KUNDAN &middot; GEMS"),
    "bapu": ("&#129403;", "KAPDE &middot; SANGANERI PRINT &middot; JUTTI"),
    "nehru": ("&#128094;", "JUTTIYAN &middot; SASTA FABRIC"),
    "tripolia": ("&#127866;", "BRASS &middot; LOHA &middot; BARTAN"),
    "manihar": ("&#128141;", "LAKH KI CHUDIYAN"),
    "chandpole": ("&#128511;", "MARBLE MURTIYAN &middot; HANDICRAFT"),
    "kishanpole": ("&#127752;", "BANDHEJ &middot; LEHERIYA"),
    "chaura": ("&#128218;", "KITAABEIN &middot; STATIONERY"),
}
KW = {"johari": "Johari", "bapu": "Bapu", "nehru": "Nehru", "tripolia": "Tripolia", "manihar": "Maniharon", "chandpole": "Chandpole", "khajane": "Khajane", "kishanpole": "Kishanpole", "chaura": "Chaura"}
for k, (lab, pts, li) in BZ.items():
    t = wt(li, KW[k]) - .1
    mid = BP[k][1]; x, y = scr(mid)
    # focus the plane on this street
    sc = 1.25; rx = 34
    if k != "khajane": plane(t - .35, rx, sc, (540 - x) * sc, (980 - y) * sc, .7)
    J.append(f'tl.set(["#bg_{k}", "#bz_{k}"], {{opacity:1}}, {t:.2f}); tl.to(["#bg_{k}", "#bz_{k}"], {{strokeDashoffset:0, duration:.7, ease:"power2.out"}}, {t:.2f}); tl.to("#bg_{k}", {{strokeOpacity:.15, duration:.4}}, {S(li + 1) - .1:.2f}); tl.to("#bz_{k}", {{opacity:.55, duration:.4}}, {S(li + 1) - .1:.2f});')
    IN.append(f'<div class="bb" id="bl_{k}" style="left:{x:.0f}px;top:{y - 14:.0f}px"><span>{lab}</span></div>')
    J.append(f'tl.fromTo("#bl_{k}", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)", immediateRender:false}}, {t + .2:.2f}); tl.to("#bl_{k}", {{opacity:0, duration:.25}}, {S(li + 1) - .15:.2f});')
    sfx("whoosh-short", t, .25)
for li in range(1, 9):
    ks = [k for k, v in BZ.items() if v[2] == li and k in ITEM]
    if not ks: continue
    k = ks[0]; ic, txt = ITEM[k]; t = wt(li, ":") + .05 if ":" in PH[li]["t"] else S(li) + .6
    H.append(f'<div class="card" id="cd{li}"><i>{ic}</i><div><small>{BZ[k][0]}</small><b>{txt}</b></div></div>')
    J.append(f'tl.fromTo("#cd{li}", {{opacity:0, y:40, scale:.92}}, {{opacity:1, y:0, scale:1, duration:.45, ease:"power3.out"}}, {t:.2f}); tl.fromTo("#cd{li} i", {{scale:2.2, rotation:-20}}, {{scale:1, rotation:0, duration:.5, ease:"back.out(2.5)"}}, {t:.2f}); tl.to("#cd{li}", {{opacity:0, y:-20, duration:.25}}, {S(li + 1) - .15:.2f});')
    sfx("pop", t, .3)
J.append(f'tl.to("#hawa", {{opacity:1, duration:.3}}, {S(1) - .2:.2f}); tl.to("#hawa", {{opacity:0, duration:.3}}, {S(2):.2f});')
IN.append(f'<div class="bb sm" id="bl_hawa" style="left:{scr(HAWA)[0] + 70:.0f}px;top:{scr(HAWA)[1] - 10:.0f}px"><span>HAWA MAHAL</span></div>')
J.append(f'tl.fromTo("#bl_hawa", {{opacity:0}}, {{opacity:1, duration:.3, immediateRender:false}}, {S(1) + .4:.2f}); tl.to("#bl_hawa", {{opacity:0, duration:.25}}, {S(2) - .1:.2f});')

# ---------- 9 Sanganer / Bagru (inset map) ----------
H.append('''<div id="inset"><svg viewBox="0 0 900 640" width="900" height="640">
<rect width="900" height="640" fill="#1c1610"/>
<path d="M0 520 Q 300 470 900 560" fill="none" stroke="#3a2f22" stroke-width="20"/>
<g class="jp"><path d="M560 150 L700 140 L730 210 L690 260 L570 255 Z" fill="#E8908A" fill-opacity=".3" stroke="#E8908A" stroke-width="3"/><text x="640" y="125" text-anchor="middle" font-family="Mont" font-weight="700" font-size="28" letter-spacing="4" fill="#FFD3CF">JAIPUR WALLED CITY</text></g>
<path class="r1" d="M640 255 Q 630 380 600 470" fill="none" stroke="#C9A24A" stroke-width="6" stroke-dasharray="14 10"/>
<path class="r2" d="M600 470 Q 400 500 160 450" fill="none" stroke="#C9A24A" stroke-width="6" stroke-dasharray="14 10"/>
<g class="sn"><circle cx="600" cy="470" r="34" fill="#C9A24A" fill-opacity=".3" stroke="#C9A24A" stroke-width="4"/><circle cx="600" cy="470" r="12" fill="#F7E3A8"/><text x="600" y="545" text-anchor="middle" font-family="Anton" font-size="44" fill="#F7E3A8">SANGANER</text></g>
<g class="bg"><circle cx="160" cy="450" r="34" fill="#C9A24A" fill-opacity=".3" stroke="#C9A24A" stroke-width="4"/><circle cx="160" cy="450" r="12" fill="#F7E3A8"/><text x="160" y="525" text-anchor="middle" font-family="Anton" font-size="44" fill="#F7E3A8">BAGRU</text></g>
<text x="450" y="610" text-anchor="middle" font-family="Mont" font-weight="700" font-size="20" letter-spacing="4" fill="#888">SHEHAR KE BAHAR &middot; NOT TO SCALE</text></svg></div>''')
J.append(f'tl.fromTo("#inset", {{opacity:0, y:40, scale:.9}}, {{opacity:1, y:0, scale:1, duration:.45, ease:"power3.out"}}, {S(9) - .05:.2f}); tl.to("#inset", {{opacity:0, duration:.3}}, {S(10) - .1:.2f});'
         f'tl.set(["#inset .sn", "#inset .bg", "#inset .r1", "#inset .r2"], {{opacity:0}}, 0); tl.to(["#inset .r1", "#inset .sn"], {{opacity:1, duration:.3}}, {wt(9, "Sanganer") - .1:.2f}); tl.fromTo("#inset .sn", {{scale:0, transformOrigin:"600px 470px"}}, {{scale:1, duration:.35, ease:"back.out(2.5)", immediateRender:false}}, {wt(9, "Sanganer") - .1:.2f});'
         f'tl.to(["#inset .r2", "#inset .bg"], {{opacity:1, duration:.3}}, {wt(9, "Bagru") - .1:.2f}); tl.fromTo("#inset .bg", {{scale:0, transformOrigin:"160px 450px"}}, {{scale:1, duration:.35, ease:"back.out(2.5)", immediateRender:false}}, {wt(9, "Bagru") - .1:.2f});')
J.append(f'tl.to("#dim", {{opacity:.5, duration:.3}}, {S(9) - .1:.2f}); tl.to("#dim", {{opacity:0, duration:.3}}, {S(10):.2f});')
H.append('<div class="card" id="cd9" style="top:1040px"><i>&#127912;</i><div><small>SANGANER &middot; BAGRU</small><b>HAND BLOCK PRINT</b></div></div>')
J.append(f'tl.fromTo("#cd9", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:.45, ease:"power3.out"}}, {wt(9, "hand") - .2:.2f}); tl.to("#cd9", {{opacity:0, duration:.25}}, {S(10) - .15:.2f});')
sfx("whoosh", S(9) - .1, .3); sfx("pop", wt(9, "Sanganer"), .3); sfx("pop", wt(9, "Bagru"), .3)

# ---------- 10 real estate ----------
J.append(f'tl.to("#plane", {{scale:.5, rotationX:32, x:0, y:80, duration:1.1, ease:"power2.inOut"}}, {S(10) - .3:.2f});')
J.append(f'tl.to([".bz", ".bzg"], {{opacity:1, strokeOpacity:1, strokeDashoffset:0, duration:.5, stagger:.05}}, {wt(10, "har galli") - .2:.2f}); tl.to("#wall", {{fillOpacity:.25, duration:.6}}, {wt(10, "Walled") - .2:.2f}); tl.to(".grid", {{strokeOpacity:.6, duration:.5}}, {S(10) + .2:.2f});')
H.append('<div id="re"><small>300 SAAL PURANA PLAN</small><b>HAR GALLI,<br/>EK KAAM</b><span>WALLED CITY &middot; SABSE KEEMTI COMMERCIAL &#9650;</span></div>')
J.append(f'tl.fromTo("#re", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.45, ease:"power3.out"}}, {S(10):.2f}); tl.fromTo("#re span", {{opacity:0}}, {{opacity:1, duration:.4}}, {wt(10, "Isliye") - .1:.2f}); tl.to("#re", {{opacity:0, duration:.3}}, {S(11) - .1:.2f});')
sfx("riser", S(10), .3); sfx("sparkle", wt(10, "keemti"), .3)

# ---------- 11 CTA ----------
H.append('<div id="cta"><b>AAPKA FAVOURITE BAZAAR KAUNSA HAI?</b><span>COMMENT KARO</span></div>')
J.append(f'tl.to("#dim", {{opacity:.5, duration:.3}}, {S(11):.2f}); tl.fromTo("#cta", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.45, ease:"power3.out"}}, {S(11):.2f}); tl.to("#cta span", {{scale:1.06, duration:.4, yoyo:true, repeat:3}}, {wt(11, "Comment"):.2f});')
sfx("sparkle", wt(11, "Comment"), .3)

# ---------- captions ----------
HI = ["Johari Bazaar", "Bapu Bazaar", "Nehru Bazaar", "Tripolia Bazaar", "Maniharon ka Rasta", "Chandpole", "Khajane Walon ka Rasta", "Kishanpole Bazaar", "Chaura Rasta", "Sanganer", "Bagru",
      "galat bazaar", "300 saal", "keemti", "Comment"]
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
H.append('<div id="cred">Street lines approximate &middot; Imagery: Sentinel-2 (EOX)</div>')
J.append('tl.set(".bb", {xPercent:-50, yPercent:-100, rotationX:-32, transformOrigin:"50% 100%"}, 0);')

CSS = """@font-face{font-family:Anton;src:url(assets/fonts/anton.woff2)}@font-face{font-family:Mont;font-weight:700;src:url(assets/fonts/mont700.woff2)}@font-face{font-family:Mont;font-weight:800;src:url(assets/fonts/mont800.woff2)}@font-face{font-family:Mont;font-weight:900;src:url(assets/fonts/mont900.woff2)}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#0d0b09}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif}.y{color:#111;background:#F2B23E;border-radius:6px;padding:0 6px}
#stage{position:absolute;inset:0;perspective:1500px;perspective-origin:50% 26%;overflow:hidden;background:#15110d}#plane{position:absolute;inset:0;transform-style:preserve-3d}
#world{position:absolute;left:-4320px;top:-7680px;width:9720px;height:17280px}
.bb{position:absolute;white-space:nowrap;opacity:0}.bb span{display:inline-block;padding:6px 14px;border-radius:4px;background:linear-gradient(135deg,rgba(14,12,9,.95),rgba(34,27,18,.95));border:1.5px solid #C9A24A;color:#F7E3A8;font:700 26px Mont;letter-spacing:.14em}
.bb.sm span{font-size:20px;border-color:#E8908A;color:#FFD3CF}
#dim{position:absolute;inset:0;background:#000;opacity:0;z-index:5;pointer-events:none}
#face{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:40}
#cred{position:absolute;left:40px;right:40px;top:1650px;text-align:center;font:700 17px Mont;color:rgba(255,255,255,.6);z-index:20}
#hook{position:absolute;left:60px;right:60px;top:150px;z-index:16;text-align:center;padding:26px 20px;border-radius:8px;border:1.5px solid #C9A24A;background:linear-gradient(135deg,rgba(14,12,9,.93),rgba(34,27,18,.93))}
#hook small{display:block;font:700 30px Mont;letter-spacing:.3em;color:#E8908A}#hook b{display:block;margin-top:10px;font:400 110px/1 Anton;background:linear-gradient(180deg,#F7E3A8,#C9A24A);-webkit-background-clip:text;color:transparent}
#hook span{display:inline-block;margin-top:14px;padding:6px 18px;border-radius:4px;border:1.5px solid #E5484D;color:#FF9A9A;font:700 28px Mont;letter-spacing:.08em}
.lx{position:absolute;opacity:0;z-index:14;padding:16px 28px;border-radius:6px;background:linear-gradient(135deg,rgba(14,12,9,.93),rgba(34,27,18,.93));border:1.5px solid #C9A24A;color:#F3E6C8;font:700 30px/1.1 Mont;letter-spacing:.12em;white-space:nowrap}
.lx b{font:400 44px/1 Anton;letter-spacing:.04em;background:linear-gradient(180deg,#F7E3A8,#C9A24A);-webkit-background-clip:text;color:transparent}
.card{position:absolute;left:60px;right:60px;top:200px;opacity:0;z-index:15;display:flex;align-items:center;gap:26px;padding:26px 30px;border-radius:8px;border:1.5px solid #C9A24A;background:linear-gradient(135deg,rgba(14,12,9,.95),rgba(34,27,18,.95));box-shadow:0 24px 60px rgba(0,0,0,.6)}
.card i{font-style:normal;font-size:110px;line-height:1;filter:drop-shadow(0 6px 14px rgba(0,0,0,.6))}.card small{display:block;font:700 28px Mont;letter-spacing:.24em;color:#E8908A}
.card b{display:block;margin-top:8px;font:400 62px/1.05 Anton;background:linear-gradient(180deg,#F7E3A8,#C9A24A);-webkit-background-clip:text;color:transparent}
#inset{position:absolute;left:80px;top:300px;opacity:0;z-index:15;border-radius:8px;overflow:hidden;border:1.5px solid #C9A24A;box-shadow:0 30px 70px rgba(0,0,0,.7)}#inset svg{display:block}
#re{position:absolute;left:60px;right:60px;top:200px;opacity:0;z-index:15;text-align:center;padding:28px;border-radius:8px;border:1.5px solid #C9A24A;background:linear-gradient(135deg,rgba(14,12,9,.95),rgba(34,27,18,.95))}
#re small{font:700 28px Mont;letter-spacing:.3em;color:#E8908A}#re b{display:block;margin-top:10px;font:400 104px/1 Anton;background:linear-gradient(180deg,#F7E3A8,#C9A24A);-webkit-background-clip:text;color:transparent}
#re span{display:inline-block;margin-top:16px;padding:8px 20px;border-radius:4px;background:#3CE65A;color:#0d0d0d;font:800 26px Mont;letter-spacing:.08em}
#cta{position:absolute;left:60px;right:60px;top:420px;opacity:0;text-align:center;z-index:16}#cta b{display:block;padding:24px;border-radius:6px;background:linear-gradient(135deg,rgba(14,12,9,.95),rgba(34,27,18,.95));border:1.5px solid #C9A24A;color:#F3E6C8;font:400 80px/1.05 Anton}
#cta span{display:inline-block;margin-top:24px;padding:14px 34px;border-radius:4px;background:#C9A24A;color:#111;font:900 40px Mont;letter-spacing:.22em}
.cp{position:absolute;left:40px;right:40px;top:1440px;text-align:center;opacity:0;z-index:35}
.cp div{display:inline-block;padding:4px 20px 8px;border-radius:10px;background:#fff;font:900 60px/1.12 Mont;color:#111;box-shadow:0 8px 24px rgba(0,0,0,.45)}"""
audio = (f'<audio id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{END}" data-track-index="1" data-volume="1"></audio><audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.12" data-fade-out="1.5"></audio>' if VOICE
         else f'<audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.55" data-fade-out="1.5"></audio>')
open(f"{P}/index.html", "w").write(f"""<!doctype html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="30">
<div id="stage"><div id="plane"><svg id="world" viewBox="{vb(C0, CW * 9)}" preserveAspectRatio="xMidYMid slice">{"".join(SVG)}</svg>{"".join(IN)}</div></div><div id="dim"></div>
{"".join(H)}
{audio}
{"".join(SFX)}
</div><script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(J)}
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>""")
print("END", END, [p["s"] for p in PH])
