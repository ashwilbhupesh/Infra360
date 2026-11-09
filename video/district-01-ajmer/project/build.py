"""Rajasthan Ke 41 Rang · Ep 01 Ajmer (Digital Banjaaraa). Itinerary-style night map + photo cards.
Timing: rec/phrases.json if present (voice), else estimated from text. World = z13 px from tile (5791, 3466)."""
import json, math, os
P = "proj"
ASP = json.load(open("aspects.json"))
LINES = [
    "Ek aisa district jahan Garib Nawaz ki Dargah bhi hai aur Brahma ji ka mandir bhi: yeh hai Ajmer.",
    "Rajasthan Board aur RPSC, dono ka headquarters Ajmer mein hi hai.",
    "Yahan hai Ajmer Sharif Dargah, Pushkar ka Brahma mandir, aur duniya bhar mein mashhoor Pushkar mela.",
    "Khaane mein zaroor try karo Ajmer ka sohan halwa, Pushkar ke malpue aur gulkand.",
    "Ghoomne ke liye hai Ana Sagar jheel, Adhai Din ka Jhonpra aur Soniji ki Nasiyan.",
    "Kishangarh ki Bani-Thani painting ko kehte hain Rajasthan ki Mona Lisa, aur Mayo College 1875 se chal raha hai.",
    "Shopping ke liye Pushkar ka bazaar, aur marble ke liye Kishangarh ki mandi.",
    "Aabadi lagbhag 26 lakh, district ki GDP 70 hazaar crore, aur per capita income lagbhag 2 lakh rupaye.",
    "Kotputli-Kishangarh expressway aa raha hai, Kishangarh mein airport hai, aur Ajmer Smart City bhi hai.",
    "Ajmer ko Chauhan raja Ajayaraja ne basaya tha, aur yeh Prithviraj Chauhan ki rajdhani rahi.",
    "Jaipur se sirf 135 km, NH-48 par.",
    "Aap Ajmer se ho? Comment karo. Next episode mein: Alwar.",
]
VOICE = os.path.exists("rec/phrases.json")
if VOICE:
    PH = json.load(open("rec/phrases.json"))
else:
    PH = []; t = .4
    for i, l in enumerate(LINES):
        d = len(l) / 13.5 + .2
        PH.append({"s": round(t, 2), "e": round(t + d, 2), "t": l}); t += d + (.55 if i else .45)
def S(k): return PH[k]["s"]
def E(k): return PH[k]["e"]
def wt(k, w):
    t = PH[k]["t"]; i = t.lower().find(w.lower())
    assert i >= 0, (k, w)
    return S(k) + (E(k) - S(k)) * i / len(t)
END = round(E(11) + 1.3, 2)

def wp(lat, lon):
    n = 2 ** 13
    return (((lon + 180) / 360 * n) - 5791) * 256, (((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n) - 3466) * 256
SVG, H, J, SFX = [], [], [], []
def vb(c, w): h = w * 1920 / 1080; return f"{c[0] - w / 2:.1f} {c[1] - h / 2:.1f} {w:.1f} {h:.1f}"
def cam(t, c, w, d=.7, e="power2.inOut"): J.append(f'tl.to("#world", {{attr:{{viewBox:"{vb(c, w)}"}}, duration:{d}, ease:"{e}"}}, {t:.2f});')
def sfx(n, t, v=.3): SFX.append(f'<audio id="sx{len(SFX)}" class="clip" src="assets/sfx/{n}.mp3" data-start="{t:.2f}" data-duration="2" data-track-index="{20 + len(SFX)}" data-volume="{v}"></audio>')
GOLD, PINK, CYAN, GRN = "#FFC42E", "#FF4FA3", "#3CDCFF", "#3CFF96"

PL = {"dargah": (26.4560, 74.6283, "Ajmer Sharif Dargah"), "brahma": (26.4876, 74.5513, "Brahma Mandir, Pushkar"), "mela": (26.4950, 74.5430, "Pushkar Mela ground"),
      "anasagar": (26.4705, 74.6290, "Ana Sagar"), "adhai": (26.4553, 74.6253, "Adhai Din ka Jhonpra"), "soniji": (26.4589, 74.6366, "Soniji ki Nasiyan"),
      "mayo": (26.4316, 74.6492, "Mayo College"), "kishangarh": (26.5880, 74.8580, "Kishangarh"), "mandi": (26.5770, 74.8570, "Marble Mandi"),
      "airport": (26.6010, 74.8140, "Kishangarh Airport"), "bazaar": (26.4885, 74.5535, "Pushkar Bazaar"), "ajmer": (26.4499, 74.6399, "Ajmer")}
W = {k: wp(v[0], v[1]) for k, v in PL.items()}
SVG.append('<rect x="-9000" y="-9000" width="25000" height="25000" style="fill:#c9b79a"/>')
SVG.append('<image href="assets/img/aj11.jpg" x="-2816" y="-2560" width="8192" height="7168" preserveAspectRatio="none"/>')
SVG.append('<image href="assets/img/aj13.webp" x="0" y="0" width="2560" height="2048" preserveAspectRatio="none"/>')
SVG.append('<image href="assets/img/aj15.webp" x="640" y="1024" width="448" height="640" preserveAspectRatio="none"/>')
WIDE_C = ((W["brahma"][0] + W["kishangarh"][0]) / 2, (W["mayo"][1] + W["kishangarh"][1]) / 2); WIDE_W = (W["kishangarh"][0] - W["brahma"][0]) * 1.35
CITY_C = (W["soniji"][0] - 6, W["adhai"][1]); CITY_W = 150
# expressway (indicative) arriving at Kishangarh from NE, NH-48 towards Jaipur
EXP = [(W["kishangarh"][0] + 520, W["kishangarh"][1] - 900), (W["kishangarh"][0] + 300, W["kishangarh"][1] - 450), (W["kishangarh"][0] + 120, W["kishangarh"][1] - 150), (W["kishangarh"][0] + 30, W["kishangarh"][1] - 20)]
NH = [W["ajmer"], ((W["ajmer"][0] + W["kishangarh"][0]) / 2, (W["ajmer"][1] + W["kishangarh"][1]) / 2 - 20), W["kishangarh"], (W["kishangarh"][0] + 700, W["kishangarh"][1] - 300)]
def pd(pts): return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
SVG.append(f'<path id="expg" d="{pd(EXP)}" pathLength="1" style="fill:none;stroke:#FF8A00;stroke-width:70;stroke-opacity:.35;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>'
           f'<path id="expb" d="{pd(EXP)}" pathLength="1" style="fill:none;stroke:#fff;stroke-width:34;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>'
           f'<path id="exp" d="{pd(EXP)}" pathLength="1" style="fill:none;stroke:#FF8A00;stroke-width:24;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>')
SVG.append(f'<path id="nh" d="{pd(NH)}" pathLength="1" style="fill:none;stroke:{GOLD};stroke-width:7;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>')
NUM = {}
for i, k in enumerate(["dargah", "brahma", "mela", "anasagar", "adhai", "soniji", "kishangarh", "mayo", "bazaar", "mandi", "airport"]):
    NUM[k] = i + 1
    x, y = W[k]; r = 9 if k in ("anasagar", "adhai", "soniji", "dargah", "mayo") else 16
    SVG.append(f'<g id="pin_{k}" style="opacity:0"><circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 2.2:.1f}" style="fill:{PINK};opacity:.3"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" style="fill:{PINK};stroke:#fff;stroke-width:{r / 3:.1f}"/></g>')
SVG.append('<circle id="ring" cx="0" cy="0" r="10" style="fill:none;stroke:#fff;stroke-width:4;opacity:0"/>')
CAMS = [(0, 0, WIDE_C, WIDE_W)]
J.append(f'tl.set("#world", {{attr:{{viewBox:"{vb(WIDE_C, WIDE_W)}"}}}}, 0);')
def fly(k, t, w):
    c = (W[k][0], W[k][1] + w * 1920 / 1080 * .22)
    cam(t, c, w, .6); CAMS.append((t, .6, c, w))
    x, y = W[k]
    J.append(f'tl.to("#pin_{k}", {{opacity:1, duration:.2}}, {t:.2f}); tl.fromTo("#ring", {{attr:{{cx:{x:.1f}, cy:{y:.1f}, r:{w / 60:.1f}}}, opacity:1}}, {{attr:{{r:{w / 9:.1f}}}, opacity:0, duration:.7, immediateRender:false}}, {t + .35:.2f});')
    sfx("whoosh-short", t, .25)
def scr(p, t):
    c, w = CAMS[0][2], CAMS[0][3]
    for t0, d, c1, w1 in sorted(CAMS, key=lambda q: q[0]):
        if t0 + d <= t + 1e-6: c, w = c1, w1
    h = w * 1920 / 1080
    return ((p[0] - (c[0] - w / 2)) / w * 1080, (p[1] - (c[1] - h / 2)) / h * 1920)
def label(i, k, t, until, text=None, dy=-48):
    x, y = scr(W[k], t + .7)
    H.append(f'<div class="pl" id="{i}" style="left:{min(max(x, 250), 830):.0f}px;top:{y + dy:.0f}px">' + (f'<b>{NUM[k]}</b>' if k in NUM else '') + f'{text or PL[k][2]}</div>')
    J.append(f'tl.fromTo("#{i}", {{opacity:0, scale:.5}}, {{opacity:1, scale:1, duration:.25, ease:"back.out(2)"}}, {t + .2:.2f}); tl.to("#{i}", {{opacity:0, duration:.2}}, {until - .2:.2f});')
def card(cid, img, t0, t1, title, sub="", tag=None, top=380, maxw=830, maxh=880, rot=0, left=None):
    a = ASP[img]
    if a > 1.2 and maxw == 830: maxw = 960
    w = maxw; h = w / a
    if h > maxh: h = maxh; w = h * a
    cw = w + 28; lx = (1080 - cw) / 2 if left is None else left
    tg = f'<div class="tg" style="background:{tag[1]}">{tag[0]}</div>' if tag else ''
    H.append(f'<div class="card" id="{cid}" style="left:{lx:.0f}px;top:{top}px;width:{cw:.0f}px;rotate:{rot}deg">{tg}<img src="assets/img/{img}.jpg" style="width:{w:.0f}px;height:{h:.0f}px"/>'
             f'<div class="ct">{title}</div>' + (f'<div class="cs">{sub}</div>' if sub else '') + '</div>')
    J.append(f'tl.fromTo("#{cid}", {{opacity:0, scale:.55, y:60}}, {{opacity:1, scale:1, y:0, duration:.32, ease:"back.out(1.7)"}}, {t0:.2f}); tl.to("#{cid}", {{opacity:0, scale:.85, y:30, duration:.18, ease:"power2.in"}}, {t1 - .18:.2f});')
    sfx("pop", t0, .25)
def theme(i, num, name, t, until):
    H.append(f'<div class="th" id="th{i}"><b>{num}</b>{name}</div>')
    J.append(f'tl.fromTo("#th{i}", {{opacity:0, x:-60}}, {{opacity:1, x:0, duration:.3, ease:"power3.out"}}, {t:.2f}); tl.to("#th{i}", {{opacity:0, duration:.2}}, {until - .2:.2f});')
    J.append(f'tl.fromTo("#flash", {{opacity:.4}}, {{opacity:0, duration:.25, immediateRender:false}}, {t:.2f});')

# ---------- 0 HOOK ----------
H.append('<div id="series">RAJASTHAN KE 41 RANG · EP 01/41</div>')
J.append(f'tl.fromTo("#series", {{opacity:0, y:-20}}, {{opacity:1, y:0, duration:.3}}, .1); tl.to("#series", {{opacity:0, duration:.3}}, {E(0) + .3:.2f});')
card("h1", "dargah", .15, S(1) - .05, "GARIB NAWAZ KI DARGAH", top=330, maxw=560, maxh=600, rot=-3, left=30)
card("h2", "brahma_temple", wt(0, "Brahma"), S(1) - .05, "BRAHMA JI KA MANDIR", top=560, maxw=470, maxh=640, rot=3, left=560)
H.append('<div id="big">AJMER</div>'); J.append(f'tl.fromTo("#big", {{opacity:0, scale:2.4}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, {wt(0, "yeh hai") + .2:.2f}); tl.to("#big", {{opacity:0, duration:.2}}, {S(1) - .05:.2f});')
sfx("impact-bass-1", .1, .45); sfx("impact-bass-1", wt(0, "yeh hai") + .2, .45)
J.append(f'tl.to("#dim", {{opacity:.65, duration:.2}}, 0); tl.to("#dim", {{opacity:.15, duration:.4}}, {S(2) - .2:.2f});')

# ---------- 1 ROCHAK ----------
theme(1, "01", "KYA AAPKO PATA HAI?", S(1), S(2))
H.append('<div id="hq"><div class="hb"><b>RAJASTHAN BOARD</b><span>(BSER)</span></div><i>+</i><div class="hb"><b>RPSC</b><span>Public Service Commission</span></div><em>DONO KA HEADQUARTERS</em><strong>AJMER</strong></div>')
J.append(f'tl.fromTo("#hq", {{opacity:0}}, {{opacity:1, duration:.2}}, {S(1):.2f}); tl.from("#hq .hb", {{opacity:0, scale:.5, duration:.3, stagger:{(wt(1, "RPSC") - S(1)):.2f}, ease:"back.out(2)"}}, {S(1):.2f});'
         f'tl.from("#hq em, #hq strong", {{opacity:0, y:30, duration:.3, stagger:.15}}, {wt(1, "headquarters") - .1:.2f}); tl.to("#hq", {{opacity:0, duration:.2}}, {S(2) - .1:.2f});')
sfx("pop", S(1), .3); sfx("pop", wt(1, "RPSC"), .3); sfx("impact-bass-1", wt(1, "headquarters"), .35)

# ---------- 2 AASTHA ----------
theme(2, "02", "AASTHA", S(2), S(3))
fly("dargah", S(2) - .3, 420); card("a1", "dargah", wt(2, "Ajmer Sharif"), wt(2, "Pushkar ka"), "AJMER SHARIF DARGAH", "Khwaja Garib Nawaz", ("AASTHA", PINK))
label("la1", "dargah", S(2) - .3, wt(2, "Pushkar ka"))
fly("brahma", wt(2, "Pushkar ka") - .3, 600); card("a2", "brahma_temple", wt(2, "Pushkar ka"), wt(2, "Pushkar mela") - .2, "BRAHMA MANDIR", "Pushkar", ("AASTHA", PINK))
label("la2", "brahma", wt(2, "Pushkar ka") - .3, S(3))
card("a3", "pushkar_mela", wt(2, "Pushkar mela") - .2, S(3) + .2, "PUSHKAR MELA", "Duniya bhar mein mashhoor", ("MELA", PINK))
J.append(f'tl.to("#pin_mela", {{opacity:1, duration:.2}}, {wt(2, "Pushkar mela") - .2:.2f});')

# ---------- 3 KHAANA ----------
theme(3, "03", "KHAANA", S(3), S(4))
for i, (img, nm, w_) in enumerate([("sohan_halwa", "SOHAN HALWA", "sohan"), ("malpua", "MALPUA", "malpue"), ("gulkand", "GULKAND", "gulkand")]):
    t0 = wt(3, w_) - .15; t1 = (wt(3, ["malpue", "gulkand"][i]) - .15) if i < 2 else S(4) + .1
    card(f"k{i}", img, t0, t1, nm, ["Ajmer", "Pushkar", "Pushkar ke gulab"][i], ("KHAANA", "#FF9F43"))
J.append(f'tl.to("#dim", {{opacity:.55, duration:.3}}, {S(3):.2f}); tl.to("#dim", {{opacity:.15, duration:.3}}, {S(4):.2f});')

# ---------- 4 GHOOMNA ----------
theme(4, "04", "GHOOMNE KI JAGAH", S(4), S(5))
fly("anasagar", S(4) - .2, CITY_W * 1.3)
card("g1", "ana_sagar_baradari", wt(4, "Ana Sagar"), wt(4, "Adhai"), "ANA SAGAR JHEEL", "Baradari, Ajmer", ("GHOOMNA", CYAN))
label("lg1", "anasagar", S(4) - .2, S(5) + .2)
J.append(f'tl.to(["#pin_adhai", "#pin_soniji"], {{opacity:1, duration:.2}}, {wt(4, "Adhai") - .2:.2f});')
label("lg2", "adhai", wt(4, "Adhai") - .5, S(5) + .2, dy=48); label("lg3", "soniji", wt(4, "Soniji") - .5, S(5) + .2)
card("g2", "adhai_din", wt(4, "Adhai"), wt(4, "Soniji"), "ADHAI DIN KA JHONPRA", "", ("GHOOMNA", CYAN))
card("g3", "soniji_nasiyan", wt(4, "Soniji"), S(5) + .2, "SONIJI KI NASIYAN", "Sone ka Jain mandir", ("GHOOMNA", CYAN))

# ---------- 5 MASHHOOR ----------
theme(5, "05", "MASHHOOR", S(5), S(6))
fly("kishangarh", S(5) - .3, 900)
card("m1", "bani_thani", S(5) + .1, wt(5, "Mayo") - .1, "BANI-THANI", "Rajasthan ki Mona Lisa · Kishangarh", ("MASHHOOR", GOLD), maxh=900)
fly("mayo", wt(5, "Mayo") - .4, 420)
card("m2", "mayo_college", wt(5, "Mayo") - .1, S(6) + .1, "MAYO COLLEGE", "1875 se", ("MASHHOOR", GOLD))
label("lm2", "mayo", wt(5, "Mayo") - .4, S(6), dy=60)

# ---------- 6 SHOPPING ----------
theme(6, "06", "SHOPPING", S(6), S(7))
fly("bazaar", S(6) - .3, 520)
card("s1", "pushkar_bazaar", wt(6, "Pushkar"), wt(6, "marble"), "PUSHKAR BAZAAR", "", ("SHOP", PINK))
label("ls1", "bazaar", S(6) - .3, wt(6, "marble"))
fly("mandi", wt(6, "marble") - .3, 700)
card("s2", "kishangarh_mandi", wt(6, "marble"), S(7) + .1, "KISHANGARH MARBLE MANDI", "Desh ki sabse badi marble mandiyon mein se ek", ("SHOP", PINK))
label("ls2", "mandi", wt(6, "marble") - .3, S(7))


# ---------- 7 NUMBERS ----------
theme(7, "07", "AJMER IN NUMBERS", S(7), S(8))
H.append('<div id="nums"><div class="nb" id="nb0"><i>&#128101;</i><div><b>~26 LAKH</b><span>AABADI · Census 2011</span></div></div>'
         '<div class="nb" id="nb1"><i>&#128200;</i><div><b>&#8377;70,283 CR</b><span>DISTRICT GDP · 2023-24</span></div></div>'
         '<div class="nb" id="nb2"><i>&#128176;</i><div><b>~&#8377;2 LAKH</b><span>PER CAPITA INCOME · saal ka</span></div></div>'
         '<em>Source: Census 2011 (before Beawar split) · DES Rajasthan, Economic Review 2024-25 · current prices</em></div>')
J.append(f'tl.to("#dim", {{opacity:.6, duration:.3}}, {S(7) - .1:.2f}); tl.fromTo("#nums", {{opacity:0}}, {{opacity:1, duration:.2}}, {S(7):.2f}); tl.to("#nums", {{opacity:0, duration:.2}}, {S(8) - .1:.2f}); tl.to("#dim", {{opacity:.15, duration:.3}}, {S(8):.2f});')
for i, w_ in enumerate(["Aabadi", "GDP", "per capita"]):
    t = wt(7, w_) - .1
    J.append(f'tl.fromTo("#nb{i}", {{opacity:0, x:-80}}, {{opacity:1, x:0, duration:.3, ease:"back.out(2)"}}, {t:.2f});'); sfx("pop", t, .3)

# ---------- 8 FUTURE ----------
theme(70, "08", "FUTURE", S(8), S(9))
W["expmid"] = EXP[1]; FW = (EXP[0][0] - W["ajmer"][0]) * 1.3; FC = ((W["ajmer"][0] + EXP[0][0]) / 2, (W["ajmer"][1] + EXP[0][1]) / 2 + FW * .12); cam(S(8) - .2, FC, FW, .9); CAMS.append((S(8) - .2, .9, FC, FW))
J.append(f'tl.to(["#exp", "#expb", "#expg"], {{strokeDashoffset:0, duration:1.2, ease:"power2.out"}}, {S(8) + .1:.2f}); tl.to("#expg", {{strokeOpacity:.6, duration:.35, yoyo:true, repeat:5}}, {S(8) + 1.3:.2f}); tl.to(["#exp", "#expb", "#expg"], {{opacity:.5, duration:.4}}, {S(10) + 1:.2f});')
label("lf1", "expmid", S(8) + .6, S(9), "Kotputli-Kishangarh<br/>Expressway", dy=-20)
J.append(f'tl.to("#pin_airport", {{opacity:1, duration:.2}}, {wt(8, "airport") - .3:.2f});'); label("lf2", "airport", wt(8, "airport") - .5, S(9), "&#9992; Kishangarh Airport")
J.append(f'tl.to(["#pin_dargah", "#pin_mayo"], {{opacity:1, duration:.2}}, {wt(8, "Smart City") - .3:.2f});'); label("lf3", "ajmer", wt(8, "Smart City") - .5, S(9), "AJMER · SMART CITY", dy=-70)
H.append('<div class="foot" id="ff">Expressway alignment indicative</div>'); J.append(f'tl.fromTo("#ff", {{opacity:0}}, {{opacity:1, duration:.2}}, {S(8):.2f}); tl.to("#ff", {{opacity:0, duration:.2}}, {S(9):.2f});')

# ---------- 8 ITIHAAS ----------
theme(8, "09", "ITIHAAS", S(9), S(10))
card("i1", "prithviraj_painting", wt(9, "Prithviraj") - .1, S(10) + .1, "PRITHVIRAJ CHAUHAN", "Ajmer ki rajdhani se raaj · painting", ("ITIHAAS", "#B98CFF"), maxh=900)
H.append('<div id="ajay"><b>AJAYAMERU</b> &rarr; <b>AJMER</b><span>Chauhan raja Ajayaraja ne basaya</span></div>')
J.append(f'tl.fromTo("#ajay", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.3}}, {S(9) + .1:.2f}); tl.to("#ajay", {{opacity:0, duration:.2}}, {wt(9, "Prithviraj") - .1:.2f});')
J.append(f'tl.to("#dim", {{opacity:.55, duration:.3}}, {S(9):.2f}); tl.to("#dim", {{opacity:.15, duration:.3}}, {S(10):.2f});')

# ---------- 9 CONNECT ----------
theme(9, "10", "CONNECTIVITY", S(10), S(11))
cam(S(10) - .2, WIDE_C, WIDE_W * 1.05, .9); CAMS.append((S(10) - .2, .9, WIDE_C, WIDE_W * 1.05))
J.append(f'tl.to("#nh", {{strokeDashoffset:0, duration:1.0, ease:"power2.out"}}, {S(10):.2f});')
H.append('<div id="jp">JAIPUR &rarr; <b>135 KM</b><span>NH-48</span></div>'); J.append(f'tl.fromTo("#jp", {{opacity:0, x:60}}, {{opacity:1, x:0, duration:.3, ease:"back.out(2)"}}, {S(10) + .2:.2f}); tl.to("#jp", {{opacity:0, duration:.2}}, {S(11):.2f});')
for k in ["dargah", "brahma", "anasagar", "soniji", "adhai", "kishangarh", "mayo", "bazaar", "mandi", "airport", "mela"]: J.append(f'tl.to("#pin_{k}", {{opacity:1, duration:.2}}, {S(10):.2f});')

# ---------- 10 CTA ----------
H.append('<div id="cta"><b>AAP AJMER SE HO?</b><span>COMMENT KARO</span><em>NEXT EPISODE: <i>ALWAR</i></em></div>')
J.append(f'tl.to("#dim", {{opacity:.55, duration:.3}}, {S(11):.2f}); tl.fromTo("#cta", {{opacity:0}}, {{opacity:1, duration:.2}}, {S(11):.2f}); tl.from("#cta b", {{opacity:0, scale:.6, duration:.3, ease:"back.out(2)"}}, {S(11):.2f});'
         f'tl.from("#cta span", {{opacity:0, y:30, duration:.3}}, {wt(11, "Comment"):.2f}); tl.from("#cta em", {{opacity:0, scale:.5, duration:.3, ease:"back.out(2)"}}, {wt(11, "Next"):.2f});')
sfx("sparkle", wt(11, "Next"), .3)

# ---------- captions ----------
HI = ["Garib Nawaz", "Dargah", "Brahma", "Ajmer", "Rajasthan Board", "RPSC", "headquarters", "Ajmer Sharif", "Pushkar", "Pushkar mela", "sohan halwa", "malpue", "gulkand",
      "Ana Sagar", "Adhai Din ka Jhonpra", "Soniji ki Nasiyan", "Bani-Thani", "Mona Lisa", "Mayo College", "1875", "bazaar", "Kishangarh", "marble", "expressway", "airport",
      "Smart City", "Ajayaraja", "Prithviraj Chauhan", "rajdhani", "135 km", "NH-48", "Comment", "Alwar"]
def hl(t):
    for h in sorted(HI, key=len, reverse=True):
        i = t.find(h)
        if i >= 0 and "<span" not in t[max(0, i - 25):i] and "span" not in t[i:i + len(h)]: t = t[:i] + '<span class="y">' + h + '</span>' + t[i + len(h):]
    return t
ci = 0
for n, ph in enumerate(PH):
    words = ph["t"].split(); chunks = []; cur = ""
    for w_ in words:
        if cur and len(cur) + 1 + len(w_) > 24: chunks.append(cur); cur = w_
        else: cur = (cur + " " + w_).strip()
    chunks.append(cur)
    tot = sum(len(c) for c in chunks); t = ph["s"]; nx = PH[n + 1]["s"] if n + 1 < len(PH) else END
    for j, c in enumerate(chunks):
        d = (ph["e"] - ph["s"]) * len(c) / tot
        a_ = max(.02, t if j else t - .04); b_ = (min(t + d + .25, nx - .08) if j == len(chunks) - 1 else t + d - .03)
        H.append(f'<div class="cp" id="cp{ci}"><div>{hl(c)}</div></div>')
        J.append(f'tl.fromTo("#cp{ci}", {{opacity:0, scale:.88}}, {{opacity:1, scale:1, duration:.1}}, {a_:.2f}); tl.to("#cp{ci}", {{opacity:0, duration:.04}}, {b_ - .04:.2f});')
        t += d; ci += 1
if os.path.exists(f"{P}/assets/face.mp4"):
    H.append('<video id="face" class="clip" src="assets/face.mp4" data-start="0" data-duration="1.8" data-track-index="2" muted playsinline></video>')
    J.append('tl.set("#face", {opacity:1}, 0); tl.to("#face", {opacity:0, scale:1.06, duration:.15}, 1.45);')
H.append('<div id="wm">DIGITAL BANJAARAA</div><div id="vig"></div><div id="flash"></div>')
SVG.append('<rect id="dim" x="-9000" y="-9000" width="25000" height="25000" style="fill:#000;opacity:.15"/>')
CSS = """@font-face{font-family:Anton;src:url(assets/fonts/anton.woff2)}@font-face{font-family:Mont;font-weight:700;src:url(assets/fonts/mont700.woff2)}@font-face{font-family:Mont;font-weight:800;src:url(assets/fonts/mont800.woff2)}@font-face{font-family:Mont;font-weight:900;src:url(assets/fonts/mont900.woff2)}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#07090d}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif}#world{position:absolute;inset:0;width:1080px;height:1920px}.y{color:#FFC42E}
#face{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:40}
#vig{position:absolute;inset:0;pointer-events:none;background:radial-gradient(80% 60% at 50% 45%,rgba(0,0,0,0) 50%,rgba(0,0,0,.6) 100%);z-index:2}#flash{position:absolute;inset:0;background:#fff;opacity:0;z-index:25;pointer-events:none}
#wm{position:absolute;left:0;right:0;top:190px;text-align:center;font:800 24px Mont;letter-spacing:.34em;color:rgba(255,255,255,.55);z-index:20}
#series{position:absolute;left:0;right:0;top:250px;margin:0 auto;width:max-content;padding:8px 22px;border-radius:30px;background:#FFC42E;color:#111;font:900 28px Mont;letter-spacing:.06em;opacity:0;z-index:12}
#big{position:absolute;left:0;right:0;top:1150px;text-align:center;opacity:0;font:400 230px/1 Anton;color:#FF4FA3;text-shadow:0 10px 40px rgba(0,0,0,.8);z-index:12}
.th{position:absolute;left:50px;top:250px;display:flex;align-items:center;gap:12px;padding:8px 22px 8px 8px;border-radius:40px;background:rgba(8,10,15,.9);border:2px solid #FFC42E;font:400 44px/1 Anton;color:#fff;letter-spacing:.04em;opacity:0;z-index:12}
.th b{padding:8px 14px;border-radius:30px;background:#FFC42E;color:#111;font:400 38px/1 Anton}
.card{position:absolute;opacity:0;padding:14px 14px 16px;border-radius:24px;background:#fff;box-shadow:0 30px 70px rgba(0,0,0,.7);z-index:8;text-align:center}
.card img{display:block;border-radius:14px;object-fit:cover}.ct{margin-top:10px;font:400 58px/1 Anton;color:#14161c;letter-spacing:.02em}.cs{margin-top:6px;font:700 28px Mont;color:#5b6070}
.tg{position:absolute;left:-12px;top:-22px;padding:8px 20px;border-radius:30px;font:900 28px Mont;color:#111;box-shadow:0 6px 16px rgba(0,0,0,.4);z-index:2}
.pl{position:absolute;opacity:0;translate:-50% -50%;text-align:center;line-height:1.1;display:flex;align-items:center;gap:10px;padding:6px 18px 6px 6px;border-radius:30px;background:rgba(8,10,15,.9);border:2px solid #FF4FA3;font:800 30px Mont;color:#fff;white-space:nowrap;z-index:6}
.pl b{width:38px;height:38px;border-radius:50%;background:#FF4FA3;color:#111;display:flex;align-items:center;justify-content:center;font:900 22px Mont}
#hq{position:absolute;left:60px;right:60px;top:400px;opacity:0;text-align:center;z-index:9}.hb{display:block;padding:24px;border-radius:26px;background:rgba(8,10,15,.92);border:3px solid #3CDCFF}
.hb b{display:block;font:400 92px/1 Anton;color:#fff}.hb span{display:block;margin-top:6px;font:800 30px Mont;color:#3CDCFF}#hq i{display:block;font:900 80px/1.2 Mont;color:#FFC42E;font-style:normal}
#hq em{display:block;margin-top:22px;font-style:normal;font:900 38px Mont;color:#fff;letter-spacing:.1em}#hq strong{display:block;font:400 180px/1 Anton;color:#FF4FA3}
#nums{position:absolute;left:50px;right:50px;top:400px;opacity:0;z-index:9}.nb{display:flex;align-items:center;gap:22px;margin-bottom:22px;padding:24px 28px;border-radius:26px;background:rgba(8,10,15,.92);border:3px solid #FFC42E}.nb i{font-style:normal;font-size:84px}.nb b{display:block;white-space:nowrap;font:400 92px/1 Anton;color:#FFC42E}.nb span{display:block;margin-top:6px;font:900 28px Mont;color:#fff;letter-spacing:.06em}#nums em{display:block;font-style:normal;font:700 21px Mont;color:rgba(255,255,255,.8);text-align:center}
#ajay{position:absolute;left:60px;right:60px;top:430px;opacity:0;text-align:center;padding:30px;border-radius:26px;background:rgba(8,10,15,.92);border:3px solid #B98CFF;font:400 96px/1.1 Anton;color:#fff;z-index:9}
#ajay b{color:#FFC42E;font-weight:400}#ajay span{display:block;margin-top:10px;font:800 34px Mont;color:#ddd}
#jp{position:absolute;right:50px;top:560px;opacity:0;padding:20px 28px;border-radius:24px;background:rgba(8,10,15,.92);border:3px solid #FFC42E;font:400 70px/1 Anton;color:#fff;z-index:9;text-align:right}#jp b{color:#FFC42E;font-weight:400}#jp span{display:block;font:900 30px Mont;color:#ccc;margin-top:6px}
#cta{position:absolute;left:50px;right:50px;top:440px;opacity:0;text-align:center;z-index:12}#cta b{display:block;padding:24px;border-radius:26px;background:#FFC42E;color:#111;font:400 96px/1 Anton}
#cta span{display:inline-block;margin-top:20px;padding:14px 34px;border-radius:30px;background:#FF4FA3;color:#111;font:900 44px Mont}#cta em{display:block;margin:26px auto 0;font-style:normal;font:900 40px Mont;color:#fff}#cta em i{font-style:normal;color:#FFC42E;font:400 80px Anton;display:block}
.foot{position:absolute;left:40px;right:40px;top:1600px;text-align:center;opacity:0;font:700 22px Mont;color:rgba(255,255,255,.7);z-index:6}
.cp{position:absolute;left:40px;right:130px;top:1420px;text-align:center;opacity:0;z-index:35}
.cp div{display:inline-block;font:900 60px/1.12 Mont;color:#fff;-webkit-text-stroke:7px #000;paint-order:stroke fill;text-shadow:0 6px 18px rgba(0,0,0,.8)}"""
audio = ('<audio id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{END}" data-track-index="1" data-volume="1"></audio>' if VOICE
         else f'<audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.55" data-fade-out="1.5"></audio>')
open(f"{P}/index.html", "w").write(f"""<!doctype html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="30">
<svg id="world" viewBox="{vb(WIDE_C, WIDE_W)}" preserveAspectRatio="xMidYMid slice">{"".join(SVG)}</svg>
{"".join(H)}
{audio.replace("{END}", str(END))}
{"".join(SFX)}
</div><script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(J)}
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>""")
print("END", END, "voice" if VOICE else "estimated", [p["s"] for p in PH])
