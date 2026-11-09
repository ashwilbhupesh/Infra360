"""Jaipur 3-day itinerary reel (Digital Banjaaraa), synced to the Hindi voice. World = z15 web-mercator px from tile (23282, 13830)."""
import json, math
P = "proj"
ASP = json.load(open("aspects.json"))
PH = {p["k"]: p for p in json.load(open("rec/phrases.json"))}
def S(k): return PH[k]["s"]
def E(k): return PH[k]["e"]
END = round(E(58) + 1.2, 2)
def wp(lat, lon):
    n = 2 ** 15
    return (((lon + 180) / 360 * n) - 23282) * 256, (((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n) - 13830) * 256
SVG, H, J, SFX = [], [], [], []
def vb(c, w): h = w * 1920 / 1080; return f"{c[0] - w / 2:.1f} {c[1] - h / 2:.1f} {w:.1f} {h:.1f}"
def cam(t, c, w, d=.7, ease="power2.inOut"): J.append(f'tl.to("#world", {{attr:{{viewBox:"{vb(c, w)}"}}, duration:{d}, ease:"{ease}"}}, {t:.2f});')
def sfx(n, t, v=.3): SFX.append(f'<audio id="sx{len(SFX)}" class="clip" src="assets/sfx/{n}.mp3" data-start="{t:.2f}" data-duration="2" data-track-index="{20 + len(SFX)}" data-volume="{v}"></audio>')
DAYC = {1: "#FF4FA3", 2: "#FFC42E", 3: "#3CDCFF"}
Y = '<span class="y">'; Z = '</span>'

# ---------------- places ----------------
PL = {"hawa": (26.9239, 75.8267), "windview": (26.9236, 75.8262), "city": (26.9256, 75.8236), "jantar": (26.9248, 75.8247),
      "rawat": (26.9205, 75.7935), "johri": (26.9213, 75.8270), "johari": (26.9190, 75.8266), "lmb": (26.9203, 75.8262),
      "bapu": (26.9155, 75.8195), "amrapali": (26.9156, 75.8102), "lassi": (26.9163, 75.8036), "niros": (26.9158, 75.8063),
      "amer": (26.9855, 75.8513), "panna": (26.9877, 75.8567), "jal": (26.9535, 75.8462), "nahar": (26.9378, 75.8152),
      "galta": (26.9168, 75.8585), "birla": (26.8921, 75.8156), "patrika": (26.8418, 75.8043), "shop": (26.9070, 75.8050),
      "tapri": (26.9050, 75.8048), "albert": (26.9116, 75.8195), "chokhi": (26.7672, 75.8358)}
W = {k: wp(*v) for k, v in PL.items()}
DAYS = {1: ["hawa", "city", "jantar", "rawat", "johri", "bapu", "amrapali", "lassi", "niros"],
        2: ["amer", "panna", "jal", "nahar"],
        3: ["galta", "birla", "patrika", "shop", "albert", "chokhi"]}
SVG.append('<image href="assets/img/map13.jpg" x="-5632" y="-5632" width="13312" height="17408" preserveAspectRatio="none"/>')
SVG.append('<image href="assets/img/map.webp" x="0" y="0" width="2048" height="6656" preserveAspectRatio="none"/>')
for d, ks in DAYS.items():
    pts = " ".join(f"{W[k][0]:.1f},{W[k][1]:.1f}" for k in ks)
    SVG.append(f'<polyline id="route{d}" points="{pts}" pathLength="1" style="fill:none;stroke:{DAYC[d]};stroke-width:6;stroke-linejoin:round;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1;opacity:.9"/>')
    for k in ks:
        x, y = W[k]
        SVG.append(f'<g id="pin_{k}" style="opacity:0"><circle cx="{x:.1f}" cy="{y:.1f}" r="26" style="fill:{DAYC[d]};opacity:.25"/>'
                   f'<circle cx="{x:.1f}" cy="{y:.1f}" r="12" style="fill:{DAYC[d]};stroke:#fff;stroke-width:5"/></g>')
SVG.append('<circle id="ring" cx="0" cy="0" r="20" style="fill:none;stroke:#fff;stroke-width:5;opacity:0"/>')
def bbox(keys, pad=1.35):
    xs = [W[k][0] for k in keys]; ys = [W[k][1] for k in keys]
    c = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)
    w = max((max(xs) - min(xs)) * pad, (max(ys) - min(ys)) * pad * 1080 / 1920, 700)
    return c, w

# ---------------- helpers ----------------
CARDS = []
def card(cid, img, t0, t1, time_, title, sub, day, tag=None, box=(900, 700)):
    a = ASP[img]; bw, bh = box
    w = bw; h = w / a
    if h > bh: h = bh; w = h * a
    cw = w + 28; top = 360 + (700 - h) / 2 * .6
    left = (1080 - cw) / 2
    tag_html = ""
    if tag:
        kind, name = tag
        col = {"CAFE": "#3CDCFF", "FOOD": "#FF9F43", "SHOP": "#FF4FA3", "DINNER": "#FFC42E"}[kind]
        tag_html = f'<div class="tag"><b style="background:{col}">{kind}</b>{name}</div>'
    H.append(f'<div class="card" id="{cid}" style="left:{left:.0f}px;top:{top:.0f}px;width:{cw:.0f}px">'
             + (f'<div class="tp" style="background:{DAYC[day]}">{time_}</div>' if time_ else '')
             + f'<img src="assets/img/{img}.jpg" style="width:{w:.0f}px;height:{h:.0f}px"/>'
             f'<div class="ct">{title}</div>' + (f'<div class="cs">{sub}</div>' if sub else '') + tag_html + '</div>')
    J.append(f'tl.fromTo("#{cid}", {{opacity:0, scale:.6, y:40}}, {{opacity:1, scale:1, y:0, duration:.32, ease:"back.out(1.7)"}}, {t0:.2f});'
             f'tl.to("#{cid}", {{opacity:0, scale:.85, y:30, duration:.18, ease:"power2.in"}}, {t1 - .18:.2f});')
    sfx("pop", t0, .22)
def fly(k, t, w=760, d=.55):
    c = (W[k][0], W[k][1] + w * 1920 / 1080 * .12)
    cam(t, c, w, d)
    x, y = W[k]
    J.append(f'tl.set("#pin_{k}", {{opacity:1}}, {t:.2f}); tl.fromTo("#ring", {{attr:{{cx:{x:.1f}, cy:{y:.1f}, r:16}}, opacity:1}}, {{attr:{{r:90}}, opacity:0, duration:.7, ease:"power1.out", immediateRender:false}}, {t + .3:.2f});')

# ---------------- 0 · OPENING collage ----------------
COL = ["p01", "p06", "p24", "p52", "p40", "p42", "p34", "p45", "p29", "p18", "p37", "p11"]
H.append('<div id="intro"><div id="grid">' + "".join(f'<div class="gi" id="g{i}"><img src="assets/img/{p}.jpg"/></div>' for i, p in enumerate(COL)) + '</div><div id="ishade"></div>'
         '<div id="ititle"><span class="k1">JAIPUR</span><span class="k2">3 DAYS</span><span class="k3">TIME-WISE ITINERARY</span></div>'
         '<div id="isave">SAVE THIS FOR YOUR TRIP</div></div>')
for i in range(len(COL)):
    J.append(f'tl.fromTo("#g{i}", {{opacity:0, scale:1.3}}, {{opacity:1, scale:1, duration:.35, ease:"power2.out"}}, {.82 + .04 * i:.2f});')
J.append('tl.fromTo("#grid", {scale:1.0}, {scale:1.12, duration:7.4, ease:"none"}, 0);')
J.append('tl.fromTo("#ititle .k1", {opacity:0, y:60}, {opacity:1, y:0, duration:.35, ease:"back.out(2)"}, .95);'
         'tl.fromTo("#ititle .k2", {opacity:0, scale:.5}, {opacity:1, scale:1, duration:.3, ease:"back.out(2)"}, 1.15);'
         'tl.fromTo("#ititle .k3", {opacity:0, y:30}, {opacity:1, y:0, duration:.3}, 1.3);')
J.append(f'tl.fromTo("#isave", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, {S(2) + .4:.2f}); tl.to("#isave", {{scale:1.08, duration:.35, yoyo:true, repeat:3}}, {S(2) + .8:.2f});')
J.append(f'tl.to("#intro", {{opacity:0, duration:.35}}, {S(4) - .3:.2f});')
sfx("impact-bass-1", 0.02, .45); sfx("riser", 4.4, .2)
J.append(f'tl.set("#world", {{attr:{{viewBox:"{vb(bbox(DAYS[1])[0], bbox(DAYS[1])[1] * 1.6)}"}}}}, 0);')

# ---------------- day intros ----------------
TT = {1: [("9:00", "Hawa Mahal"), ("10:15", "City Palace"), ("12:15", "Jantar Mantar"), ("1:30", "Pyaaz kachori lunch"), ("3:00", "The Johri · Johari Bazaar"),
          ("4:00", "Bapu Bazaar"), ("7:00", "MI Road shopping"), ("8:30", "Dinner at Niros")],
      2: [("8:00", "Amer Fort"), ("11:00", "Panna Meena ka Kund"), ("12:00", "Jal Mahal"), ("1:00", "Lunch & rest"), ("4:30", "Nahargarh sunset")],
      3: [("7:30", "Galta Ji"), ("10:00", "Birla Mandir"), ("11:30", "Patrika Gate"), ("12:30", "Shopping · C-Scheme"), ("6:00", "Albert Hall"), ("7:30", "Chokhi Dhani")]}
SUBT = {1: "OLD CITY", 2: "FORTS", 3: "MANDIR + MODERN JAIPUR"}
DSTART = {1: S(4), 2: S(23), 3: S(32)}
DEND = {1: S(23), 2: S(32), 3: S(50)}
FIRST = {1: S(6), 2: S(25), 3: S(34)}
for d in (1, 2, 3):
    t0, t1 = DSTART[d], DEND[d]
    c, w = bbox(DAYS[d])
    if d > 1: J.append(f'tl.to("#world", {{attr:{{viewBox:"{vb(c, w * 1.25)}"}}, duration:.6, ease:"power2.inOut"}}, {t0 - .2:.2f});')
    cam(t0, c, w, 1.0, "power2.out")
    J.append(f'tl.to("#route{d}", {{strokeDashoffset:0, duration:1.1, ease:"power2.inOut"}}, {t0 + .1:.2f});')
    for i, k in enumerate(DAYS[d]): J.append(f'tl.to("#pin_{k}", {{opacity:1, duration:.15}}, {t0 + .15 + .1 * i:.2f});')
    if d > 1:
        for k in DAYS[d - 1]: J.append(f'tl.to("#pin_{k}", {{opacity:0, duration:.2}}, {t0 - .2:.2f});')
        J.append(f'tl.to("#route{d - 1}", {{opacity:0, duration:.2}}, {t0 - .2:.2f});')
    J.append(f'tl.to("#route{d}", {{opacity:.35, duration:.3}}, {FIRST[d] - .2:.2f});')
    H.append(f'<div class="daytab" id="dt{d}" style="background:{DAYC[d]}">DAY {d}<span>{SUBT[d]}</span></div>')
    J.append(f'tl.fromTo("#dt{d}", {{opacity:0, x:-60}}, {{opacity:1, x:0, duration:.3, ease:"power3.out"}}, {t0:.2f}); tl.to("#dt{d}", {{opacity:0, duration:.2}}, {t1 - .25:.2f});')
    rows = "".join(f'<p><b style="color:{DAYC[d]}">{a}</b>{b}</p>' for a, b in TT[d])
    H.append(f'<div class="tt" id="tt{d}" style="border-color:{DAYC[d]}"><h3>DAY {d} TIMETABLE</h3>{rows}</div>')
    J.append(f'tl.fromTo("#tt{d}", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:.3, ease:"power3.out"}}, {t0 + .15:.2f}); tl.from("#tt{d} p", {{opacity:0, x:-30, duration:.2, stagger:.06}}, {t0 + .3:.2f}); tl.to("#tt{d}", {{opacity:0, duration:.2}}, {FIRST[d] - .1:.2f});')
    sfx("whoosh", t0 - .1, .35)

# ---------------- stops ----------------
st = []
def stop(cid, k, img, t0, t1, time_, title, sub, day, tag=None, flyto=True, w=760):
    if flyto and k: fly(k, t0 - .35, w)
    card(cid, img, t0 + .05, t1, time_, title, sub, day, tag)
# Day 1
stop("c_hawa", "hawa", "p01", S(6), S(7), "9:00 AM", "HAWA MAHAL", "Palace of Winds", 1)
stop("c_wind", "windview", "p02", S(7), S(10), "", "HAWA MAHAL VIEW", "Chai on the rooftop opposite", 1, ("CAFE", "Wind View Cafe · Tattoo Cafe"), flyto=False)
stop("c_city", "city", "p06", S(10), S(11), "10:15 AM", "CITY PALACE", "", 1)
stop("c_bara", None, "p04", S(11), S(12), "", "INSIDE CITY PALACE", "", 1, ("CAFE", "Baradari · coffee"), flyto=False)
stop("c_jan", "jantar", "p11", S(12), S(13), "12:15 PM", "JANTAR MANTAR", "", 1)
stop("c_kach", "rawat", "p22", S(13), S(14), "1:30 PM", "PYAAZ KACHORI", "", 1, ("FOOD", "Rawat Mishthan Bhandar"))
stop("c_johri", "johri", "p56", S(15) - .2, S(16), "", "THE JOHRI", "Chai-nashta", 1, ("CAFE", "Johari Bazaar"))
stop("c_jew", "johari", "p70", S(16), S(17), "", "JOHARI BAZAAR", "Jewellery", 1, ("SHOP", "Jewellery lane"), flyto=False)
stop("c_lmb", "lmb", "p57", S(17), S(18), "", "LMB", "Mithai", 1, ("FOOD", "Laxmi Misthan Bhandar"), flyto=False)
stop("c_bapu", "bapu", "p18", S(18), S(19) + 1.0, "4:00 PM", "BAPU BAZAAR", "Mojari", 1, ("SHOP", "Mojari · Bandhej · Lac bangles"))
stop("c_bapu2", None, "p19", S(19) + 1.0, S(20), "", "BAPU BAZAAR", "Bandhej · Lac bangles", 1, flyto=False)
TL = S(21) + 1.55
stop("c_amra", "amrapali", "p71", S(20), TL, "7:00 PM", "AMRAPALI", "Silver jewellery · MI Road", 1, ("SHOP", "Amrapali"))
stop("c_lassi", "lassi", "p23", TL, S(22), "", "LASSIWALA", "MI Road", 1, ("FOOD", "Lassiwala"))
stop("c_niros", "niros", "p59", S(22), S(23), "8:30 PM", "NIROS", "Dinner since 1949", 1, ("DINNER", "Niros · MI Road"))
# Day 2
stop("c_amer", "amer", "p24", S(25), S(26), "8:00 AM", "AMER FORT", "", 2, w=900)
stop("c_1135", None, "p62", S(26), S(28), "", "1135 AD", "Royal lunch ya chai", 2, ("DINNER", "1135 AD · inside Amer"), flyto=False)
stop("c_panna", "panna", "p29", S(28), S(29), "11:00 AM", "PANNA MEENA KA KUND", "", 2)
stop("c_jal", "jal", "p52", S(29), S(30), "12:00 PM", "JAL MAHAL", "", 2, w=900)
T_PADAO = S(31) + 1.3; T_NIGHT = S(31) + 3.6
stop("c_nahar", "nahar", "p35", S(31), T_PADAO, "4:30 PM", "NAHARGARH", "Sunset", 2, w=900)
stop("c_padao", None, "p68", T_PADAO, T_NIGHT, "", "PADAO CAFE", "Sunset on Nahargarh", 2, ("CAFE", "Padao"), flyto=False)
stop("c_night", None, "p53", T_NIGHT, S(32), "", "JAIPUR AT NIGHT", "From Nahargarh", 2, flyto=False)
# Day 3
stop("c_galta", "galta", "p45", S(34), S(36), "7:30 AM", "GALTA JI", "", 3, w=900)
stop("c_birla", "birla", "p42", S(36), S(38), "10:00 AM", "BIRLA MANDIR", "", 3)
stop("c_patrika", "patrika", "p40", S(38), S(43), "11:30 AM", "PATRIKA GATE", "Photos", 3, w=900)
stop("c_gulab", "shop", "p74", S(43), S(45), "12:30 PM", "JAIPUR PRINT", "Gulab Chand Prints", 3, ("SHOP", "Anokhi · Gulab Chand"))
stop("c_blue", None, "p75", S(45), S(46), "", "BLUE POTTERY", "", 3, ("SHOP", "Blue pottery"), flyto=False)
stop("c_tapri", "tapri", "p64", S(46), S(48), "", "TAPRI CENTRAL", "Chai", 3, ("CAFE", "Tapri · opp. Central Park"))
stop("c_albert", "albert", "p34", S(48), S(49), "6:00 PM", "ALBERT HALL", "", 3)
T_FIRE = S(49) + 1.3
stop("c_chokhi", "chokhi", "p47", S(49), T_FIRE, "7:30 PM", "CHOKHI DHANI", "Rajasthani dinner", 3, ("DINNER", "Chokhi Dhani"), w=1100)
stop("c_fire", None, "p51", T_FIRE, S(50), "", "CHOKHI DHANI", "Folk dance & thali", 3, flyto=False)

# ---------------- tips ----------------
TS = S(50)
H.append('<div id="tips"><h2>QUICK TIPS</h2>'
         f'<div class="tr" id="tr1"><b>BEST TIME</b><span>October – March</span></div>'
         f'<div class="tr" id="tr2"><b>STAY</b><span>Central Jaipur</span></div>'
         f'<div class="tr" id="tr3"><b>MUST EAT</b><span>Khaana mat bhoolna</span></div>'
         '<div id="foods">' + "".join(f'<div class="fd" id="fd{i}"><img src="assets/img/{p}.jpg"/><i>{n}</i></div>' for i, (p, n) in enumerate([("p76", "Dal baati churma"), ("p77", "Ghewar"), ("p22", "Pyaaz kachori")])) + '</div></div>')
J.append(f'tl.to("#world", {{opacity:.25, duration:.4}}, {TS - .2:.2f}); tl.fromTo("#tips", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:.35}}, {TS:.2f}); tl.to("#tips", {{opacity:0, duration:.25}}, {S(58) - .2:.2f});')
for i, t in enumerate([S(50) + .1, S(51), S(53)]): J.append(f'tl.from("#tr{i + 1}", {{opacity:0, x:-50, duration:.3, ease:"power3.out"}}, {t:.2f});'); sfx("click-soft", t, .3)
for i, t in enumerate([S(54), S(55), S(55) + .8]): J.append(f'tl.from("#fd{i}", {{opacity:0, scale:.5, duration:.3, ease:"back.out(2)"}}, {t:.2f});'); sfx("pop", t, .25)
# ---------------- CTA ----------------
H.append('<div id="cta"><div class="b1">SAVE KARO</div><div class="b2">COMMENT KARO</div><div class="b3">AGLI CITY KAUNSI?</div></div>')
J.append(f'tl.fromTo("#cta", {{opacity:0}}, {{opacity:1, duration:.2}}, {S(58):.2f}); tl.from("#cta .b1", {{opacity:0, scale:.5, duration:.3, ease:"back.out(2)"}}, {S(58):.2f});'
         f'tl.from("#cta .b2", {{opacity:0, scale:.5, duration:.3, ease:"back.out(2)"}}, {S(58) + 1.2:.2f}); tl.from("#cta .b3", {{opacity:0, y:40, duration:.35, ease:"back.out(2)"}}, {S(58) + 2.0:.2f});'
         f'tl.to("#cta .b3", {{scale:1.07, duration:.4, yoyo:true, repeat:3}}, {S(58) + 2.5:.2f});')
J.append(f'tl.to("#world", {{attr:{{viewBox:"{vb(wp(26.905, 75.825), 5200)}"}}, duration:4, ease:"power1.inOut"}}, {TS:.2f});')
sfx("sparkle", S(58), .3); sfx("impact-bass-1", TS - .1, .3)

# ---------------- captions ----------------
HI = ["Jaipur", "3 din", "save", "Day 1", "Day 2", "Day 3", "Hawa Mahal", "Wind View Cafe", "best view", "Tattoo Cafe", "City Palace", "Baradari", "Jantar Mantar",
      "Rawat", "pyaaz kachori", "The Johri", "Johari Bazaar", "LMB", "Bapu Bazaar", "lac ki chudiyan", "MI Road", "Amrapali", "Lassiwala", "Niros", "forts", "Amer Fort",
      "1135 AD", "Panna Meena ka Kund", "Jal Mahal", "Nahargarh", "Padao Cafe", "sunset", "Galta Ji", "Birla Mandir", "Patrika Gate", "shopping", "Anokhi", "Gulabji",
      "blue pottery", "Tapri Central", "Albert Hall", "Chokhi Dhani", "October", "March", "Central Jaipur", "dal baati churma", "ghewar", "agli city"]
def hl(t):
    for h in sorted(HI, key=len, reverse=True):
        i = t.find(h)
        if i >= 0 and '"y"' not in t[max(0, i - 20):i]: t = t[:i] + Y + h + Z + t[i + len(h):]
    return t
ci = 0; MJ = []
keys = sorted(PH)
for n, k in enumerate(keys):
    ph = PH[k]; words = ph["t"].split(); chunks = []; cur = ""
    for w_ in words:
        if cur and len(cur) + 1 + len(w_) > 26: chunks.append(cur); cur = w_
        else: cur = (cur + " " + w_).strip()
    chunks.append(cur)
    tot = sum(len(c) for c in chunks); t = ph["s"]
    nxt = PH[keys[n + 1]]["s"] if n + 1 < len(keys) else END
    for j, c in enumerate(chunks):
        d = (ph["e"] - ph["s"]) * len(c) / tot
        a = max(.02, t if j else t - .04); b = (min(t + d + .25, nxt - .08) if j == len(chunks) - 1 else t + d - .03)
        H.append(f'<div class="cp" id="cp{ci}"><div>{hl(c)}</div></div>')
        J.append(f'tl.fromTo("#cp{ci}", {{opacity:0, scale:.9}}, {{opacity:1, scale:1, duration:.1}}, {a:.2f}); tl.set("#cp{ci}", {{opacity:0}}, {b:.2f});')
        t += d; ci += 1

H.append('<div id="wm">DIGITAL BANJAARAA</div><div id="vig"></div>')
H.append('<video id="face" class="clip" src="assets/face.mp4" data-start="0" data-duration="1.2" data-track-index="2" muted playsinline></video>')
J.append('tl.set("#face", {opacity:1}, 0); tl.to("#face", {opacity:0, scale:1.06, duration:.15}, .85);')
CSS = """@font-face{font-family:Anton;src:url(assets/fonts/anton.woff2)}@font-face{font-family:Mont;font-weight:700;src:url(assets/fonts/mont700.woff2)}
@font-face{font-family:Mont;font-weight:800;src:url(assets/fonts/mont800.woff2)}@font-face{font-family:Mont;font-weight:900;src:url(assets/fonts/mont900.woff2)}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#07090d}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif}#world{position:absolute;inset:0;width:1080px;height:1920px}
.y{color:#FFC42E}
#face{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:30}#vig{position:absolute;inset:0;pointer-events:none;background:radial-gradient(80% 60% at 50% 45%,rgba(0,0,0,0) 50%,rgba(0,0,0,.6) 100%)}
#wm{position:absolute;left:0;right:0;top:190px;text-align:center;font:800 26px Mont;letter-spacing:.32em;color:rgba(255,255,255,.5);z-index:20}
#intro{position:absolute;inset:0;z-index:10;background:#07090d;overflow:hidden}
#grid{position:absolute;left:-60px;top:-40px;width:1200px;height:2000px;display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(4,1fr);gap:10px;transform:rotate(-4deg)}
.gi{overflow:hidden;border-radius:16px}.gi img{width:100%;height:100%;object-fit:cover;display:block}
#ishade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(7,9,13,.35) 0%,rgba(7,9,13,.82) 32%,rgba(7,9,13,.82) 62%,rgba(7,9,13,.35) 100%)}
#ititle{position:absolute;left:0;right:0;top:560px;text-align:center;color:#fff}
#ititle span{display:block}#ititle .k1{font:400 230px/1 Anton;letter-spacing:.04em;color:#FF4FA3;text-shadow:0 8px 40px rgba(0,0,0,.7)}
#ititle .k2{font:400 150px/1.05 Anton;color:#fff}#ititle .k3{margin-top:14px;font:900 44px Mont;letter-spacing:.14em;color:#FFC42E}
#isave{position:absolute;left:0;right:0;top:1200px;margin:0 auto;width:640px;text-align:center;padding:18px 0;border-radius:60px;background:#FFC42E;color:#111;font:900 38px Mont;letter-spacing:.05em;opacity:0}
.daytab{position:absolute;left:50px;top:250px;padding:12px 26px;border-radius:40px;font:400 54px/1 Anton;color:#111;opacity:0;z-index:5;display:flex;align-items:center;gap:16px}
.daytab span{font:900 26px Mont;letter-spacing:.1em}
.tt{position:absolute;left:50px;right:50px;top:350px;padding:26px 30px 18px;border-radius:26px;background:rgba(8,10,15,.88);border:3px solid;opacity:0;z-index:4}
.tt h3{font:400 44px Anton;color:#fff;letter-spacing:.05em;margin-bottom:10px}.tt p{font:800 36px/1.5 Mont;color:#fff}.tt p b{display:inline-block;width:150px;font-weight:900}
.card{position:absolute;opacity:0;padding:14px 14px 18px;border-radius:24px;background:#fff;box-shadow:0 30px 70px rgba(0,0,0,.7);z-index:6;text-align:center}
.card img{display:block;border-radius:14px;margin:0 auto}
.tp{position:absolute;left:-14px;top:-26px;padding:10px 22px;border-radius:30px;font:900 36px Mont;color:#111;box-shadow:0 6px 16px rgba(0,0,0,.4)}
.ct{margin-top:12px;font:400 64px/1 Anton;color:#14161c;letter-spacing:.02em}.cs{margin-top:6px;font:700 30px Mont;color:#5b6070}
.tag{position:absolute;left:50%;bottom:-38px;transform:translateX(-50%);white-space:nowrap;display:flex;align-items:center;gap:12px;padding:8px 22px 8px 8px;border-radius:40px;background:#14161c;color:#fff;font:800 32px Mont;box-shadow:0 8px 20px rgba(0,0,0,.5)}
.tag b{padding:6px 14px;border-radius:30px;color:#111;font:900 24px Mont;letter-spacing:.08em}
.cp{position:absolute;left:40px;right:130px;top:1370px;text-align:center;opacity:0;z-index:15}
.cp div{display:inline-block;font:900 62px/1.12 Mont;color:#fff;-webkit-text-stroke:7px #000;paint-order:stroke fill;text-shadow:0 6px 18px rgba(0,0,0,.8)}
#tips{position:absolute;left:50px;right:50px;top:330px;opacity:0;padding:30px 34px;border-radius:28px;background:rgba(8,10,15,.92);border:3px solid #FFC42E;z-index:8}
#tips h2{font:400 70px Anton;color:#FFC42E;margin-bottom:10px}.tr{display:flex;align-items:baseline;gap:20px;margin:12px 0}
.tr b{width:250px;font:900 34px Mont;color:#FFC42E;letter-spacing:.06em}.tr span{font:800 46px Mont;color:#fff}
#foods{display:flex;gap:16px;margin-top:20px}.fd{flex:1;border-radius:18px;overflow:hidden;background:#fff;padding:8px}.fd img{width:100%;height:240px;object-fit:cover;border-radius:12px;display:block}
.fd i{display:block;font-style:normal;font:900 26px Mont;color:#14161c;text-align:center;padding:8px 0 2px}
#cta{position:absolute;left:0;right:0;top:470px;opacity:0;text-align:center;z-index:9}
#cta div{margin:0 auto 26px;width:820px;padding:26px 0;border-radius:30px;font:400 92px/1 Anton;letter-spacing:.03em}
#cta .b1{background:#FFC42E;color:#111}#cta .b2{background:#FF4FA3;color:#111}#cta .b3{background:#fff;color:#111;font-size:76px}"""
open(f"{P}/index.html", "w").write(f"""<!doctype html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="30">
<svg id="world" viewBox="{vb(bbox(DAYS[1])[0], 3000)}" preserveAspectRatio="xMidYMid slice">{"".join(SVG)}</svg>
{"".join(H)}
<audio id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{END}" data-track-index="1" data-volume="1"></audio>
{"".join(SFX)}
</div><script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(J)}
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>""")
print("END", END, "captions", ci)
