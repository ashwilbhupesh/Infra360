"""Rajasthan Ke 41 Rang · Ep 01 Ajmer (Digital Banjaaraa). Itinerary-style night map + photo cards.
Timing: rec/phrases.json if present (voice), else estimated from text. World = z13 px from tile (5791, 3466)."""
import json, math, os
P = "proj"
ASP = json.load(open("aspects.json"))
LINES = [
    "Aayiye Ajmer ko jaante hain. Iski aabadi lagbhag 26 lakh hai, yaani Botswana desh se bhi zyada, aur economy 70 hazaar crore ki, yaani Maldives desh se bhi badi.",
    "Yahan hai Ajmer Sharif Dargah, Pushkar ka Brahma mandir, aur duniya bhar mein mashhoor Pushkar mela.",
    "Ghoomne ke liye hai Ana Sagar jheel, Adhai Din ka Jhonpra aur Soniji ki Nasiyan.",
    "Khaane mein zaroor try karo Ajmer ka sohan halwa, Pushkar ke malpue aur gulkand.",
    "Kishangarh ki Bani-Thani painting ko kehte hain Rajasthan ki Mona Lisa, aur Mayo College 1875 se chal raha hai.",
    "Har district ki aisi jaankari ke liye, Digital Banjaaraa ko follow karo.",
    "Aur Rajasthan Board aur RPSC, dono ka headquarters Ajmer mein hi hai.",
    "Shopping ke liye Pushkar ka bazaar, aur marble ke liye Kishangarh ki mandi.",
    "Kotputli-Kishangarh expressway aa raha hai, Kishangarh mein airport hai, aur Ajmer Smart City bhi hai.",
    "Ajmer ko Chauhan raja Ajayaraja ne basaya tha, aur yeh Prithviraj Chauhan ki rajdhani rahi.",
    "Jaipur se sirf 135 km, NH-48 par.",
    "Aap Ajmer se ho? Comment karo Ajmer. Next episode mein: Alwar.",
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
CARDS = []
def vb(c, w): h = w * 1920 / 1080; return f"{c[0] - w / 2:.1f} {c[1] - h / 2:.1f} {w:.1f} {h:.1f}"
def cam(t, c, w, d=.7, e="power2.inOut"): J.append(f'tl.to("#world", {{attr:{{viewBox:"{vb(c, w)}"}}, duration:{d}, ease:"{e}"}}, {t:.2f});')
def sfx(n, t, v=.3): SFX.append(f'<audio id="sx{len(SFX)}" class="clip" src="assets/sfx/{n}.mp3" data-start="{t:.2f}" data-duration="2" data-track-index="{20 + len(SFX)}" data-volume="{v}"></audio>')
GOLD, PINK, CYAN, GRN = "#FFC42E", "#FF4FA3", "#3CDCFF", "#3CFF96"

PL = {"dargah": (26.4560, 74.6283, "Ajmer Sharif Dargah"), "brahma": (26.4876, 74.5513, "Brahma Mandir, Pushkar"), "mela": (26.4950, 74.5430, "Pushkar Mela ground"),
      "anasagar": (26.4705, 74.6290, "Ana Sagar"), "adhai": (26.4553, 74.6253, "Adhai Din ka Jhonpra"), "soniji": (26.4589, 74.6366, "Soniji ki Nasiyan"),
      "mayo": (26.4316, 74.6492, "Mayo College"), "kishangarh": (26.5880, 74.8580, "Kishangarh"), "mandi": (26.5770, 74.8570, "Marble Mandi"),
      "airport": (26.6010, 74.8140, "Kishangarh Airport"), "bazaar": (26.4885, 74.5535, "Pushkar Bazaar"), "ajmer": (26.4499, 74.6399, "Ajmer")}
W = {k: wp(v[0], v[1]) for k, v in PL.items()}
SVG.append('<rect x="-900000" y="-900000" width="2000000" height="2000000" style="fill:#141414"/>')
SVG.append('<image href="assets/img/bm4.jpg" x="-302848" y="-363008" width="786432" height="786432" preserveAspectRatio="none" style="filter:grayscale(1) brightness(.62) contrast(1.15)"/>')
SVG.append('<image href="assets/img/bm5.jpg" x="-171776" y="-166400" width="327680" height="393216" preserveAspectRatio="none" style="filter:grayscale(1) brightness(.62) contrast(1.15)"/>')
SVG.append('<image href="assets/img/bm7.webp" x="-40704" y="-35328" width="81920" height="65536" preserveAspectRatio="none" style="filter:grayscale(1) brightness(.62) contrast(1.15)"/>')
SVG.append('<image href="assets/img/aj11.webp" x="-3840" y="-4608" width="11264" height="13312" preserveAspectRatio="none"/>')
SVG.append('<image id="ajgrey" href="assets/img/aj11.webp" x="-3840" y="-4608" width="11264" height="13312" preserveAspectRatio="none" style="filter:grayscale(1) brightness(.62) contrast(1.15)"/>')
SVG.append('<image href="assets/img/aj13.webp" x="0" y="0" width="2560" height="2048" preserveAspectRatio="none"/>')
SVG.append('<image class="ajg" href="assets/img/aj13.webp" x="0" y="0" width="2560" height="2048" preserveAspectRatio="none" style="filter:grayscale(1) brightness(.62) contrast(1.15)"/>')
SVG.append('<image href="assets/img/aj15.webp" x="640" y="1024" width="448" height="640" preserveAspectRatio="none"/>')
SVG.append('<image class="ajg" href="assets/img/aj15.webp" x="640" y="1024" width="448" height="640" preserveAspectRatio="none" style="filter:grayscale(1) brightness(.62) contrast(1.15)"/>')
WIDE_C = ((W["brahma"][0] + W["kishangarh"][0]) / 2, (W["mayo"][1] + W["kishangarh"][1]) / 2); WIDE_W = (W["kishangarh"][0] - W["brahma"][0]) * 1.35
CITY_C = (W["soniji"][0] - 6, W["adhai"][1]); CITY_W = 150
# expressway (indicative) arriving at Kishangarh from NE, NH-48 towards Jaipur
EXP = [(W["kishangarh"][0] + 520, W["kishangarh"][1] - 900), (W["kishangarh"][0] + 300, W["kishangarh"][1] - 450), (W["kishangarh"][0] + 120, W["kishangarh"][1] - 150), (W["kishangarh"][0] + 30, W["kishangarh"][1] - 20)]
NH = [W["ajmer"], ((W["ajmer"][0] + W["kishangarh"][0]) / 2, (W["ajmer"][1] + W["kishangarh"][1]) / 2 - 20), W["kishangarh"], (W["kishangarh"][0] + 700, W["kishangarh"][1] - 300)]
BD = json.load(open("data/bounds.json"))
def pdr(rings): return " ".join("M" + " L".join(f"{wp(la, lo)[0]:.1f} {wp(la, lo)[1]:.1f}" for lo, la in r) + " Z" for r in rings)
RD = json.load(open("/home/user/work/rajdiv/data/rajasthan_districts.geojson"))["features"]
def rr(g): return [g["coordinates"][0]] if g["type"] == "Polygon" else [p_[0] for p_ in g["coordinates"]]
SVG.append(f'<path id="bind" d="{pdr(BD["india"])}" style="fill:#9A4E1C;fill-opacity:.88;stroke:#fff;stroke-width:3;vector-effect:non-scaling-stroke;stroke-linejoin:round"/>')
SVG.append(f'<path id="braj" d="{pdr(BD["raj"])}" style="fill:#0E2470;fill-opacity:0;stroke:#fff;stroke-width:4;vector-effect:non-scaling-stroke;stroke-linejoin:round;opacity:0"/>')
SVG.append('<g id="bdist" style="opacity:0">' + "".join(f'<path d="{pdr([[c for c in r[::2]] for r in rr(f["geometry"])])}" style="fill:none;stroke:#fff;stroke-width:1.2;stroke-opacity:.7;vector-effect:non-scaling-stroke"/>' for f in RD) + '</g>')
SVG.append(f'<path id="bout" d="M-900000 -900000 H1100000 V1100000 H-900000 Z {pdr(BD["ajmer"])}" style="fill:#000;fill-rule:evenodd;opacity:0"/>')
SVG.append(f'<path id="baj" d="{pdr(BD["ajmer"])}" style="fill:#FFC42E;fill-opacity:0;stroke:#fff;stroke-width:4;vector-effect:non-scaling-stroke;stroke-linejoin:round;opacity:0"/>')
def bbw(rings):
    pts = [wp(la, lo) for r in rings for lo, la in r]; xs = [p_[0] for p_ in pts]; ys = [p_[1] for p_ in pts]
    return min(xs), min(ys), max(xs), max(ys)
def fitb(bb, top, bot, pad=1.12):
    x0, y0, x1, y1 = bb
    w = max((x1 - x0) * pad, (y1 - y0) * pad * 1080 / (bot - top))
    return ((x0 + x1) / 2, (y0 + y1) / 2 - ((top + bot) / 2 - 960) * w / 1080), w
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
def card(cid, img, t0, t1, title, sub="", tag=None, top=380, maxw=830, maxh=880, rot=0, left=None, info=None):
    if info and maxh == 880: maxh = 600 if ASP[(img if isinstance(img, str) else img[0])] < 1 else 640
    imgs = img if isinstance(img, list) else [img]
    a = ASP[imgs[0]]
    if a > 1.2 and maxw == 830: maxw = 960
    w = maxw; h = w / a
    if h > maxh: h = maxh; w = h * a
    cw = max(w + 28, 760) if info else w + 28; lx = (1080 - cw) / 2 if left is None else left
    tg = f'<div class="tg" style="background:{tag[1]}">{tag[0]}</div>' if tag else ''
    stack = "".join(f'<div class="lyr" id="{cid}_{i}" style="width:{w:.0f}px;height:{h:.0f}px;{"opacity:0;" if i else ""}">' + (f'<img class="bgb" src="assets/img/{im}.jpg"/>' if i else '')
                    + f'<img class="fg" src="assets/img/{im}.jpg" style="object-fit:{"contain" if i else "cover"}"/></div>' for i, im in enumerate(imgs))
    dots = ('<div class="dts">' + "".join(f'<i id="{cid}_d{i}" style="opacity:{1 if i == 0 else .35}"></i>' for i in range(len(imgs))) + '</div>') if len(imgs) > 1 else ''
    H.append(f'<div class="card" id="{cid}" style="left:{lx:.0f}px;top:{top}px;width:{cw:.0f}px;rotate:{rot}deg">{tg}<div class="stk" style="width:{w:.0f}px;height:{h:.0f}px">{stack}{dots}</div>'
             f'<div class="ct">{title}</div>' + (f'<div class="cs">{sub}</div>' if sub else '') + (f'<div class="ci">{info}</div>' if info else '') + '</div>')
    J.append(f'tl.fromTo("#{cid}", {{opacity:0, scale:.55, y:60}}, {{opacity:1, scale:1, y:0, duration:.32, ease:"back.out(1.7)"}}, {t0:.2f});'); CARDS.append([cid, t0, t1])
    step = (t1 - t0 - .2) / len(imgs)
    for i in range(1, len(imgs)):
        t = t0 + step * i
        J.append(f'tl.fromTo("#{cid}_{i}", {{opacity:0, scale:1.06}}, {{opacity:1, scale:1, duration:.22, immediateRender:false}}, {t:.2f}); tl.set("#{cid}_d{i - 1}", {{opacity:.35}}, {t:.2f}); tl.set("#{cid}_d{i}", {{opacity:1}}, {t:.2f});')
    sfx("pop", t0, .25)
def theme(i, num, name, t, until):
    H.append(f'<div class="th" id="th{i}"><b>{num}</b>{name}</div>')
    J.append(f'tl.fromTo("#th{i}", {{opacity:0, x:-60}}, {{opacity:1, x:0, duration:.3, ease:"power3.out"}}, {t:.2f}); tl.to("#th{i}", {{opacity:0, duration:.2}}, {until - .2:.2f});')
    J.append(f'tl.fromTo("#flash", {{opacity:.4}}, {{opacity:0, duration:.25, immediateRender:false}}, {t:.2f});')

# ---------- 0 HOOK + India -> Rajasthan -> Ajmer ----------
IND_C, IND_W = fitb(bbw(BD["india"]), 700, 1400, 1.08)
RAJ_C, RAJ_W = fitb(bbw(BD["raj"]), 720, 1380, 1.1)
AJD_C, AJD_W = fitb(bbw(BD["ajmer"]), 800, 1390, 1.15)
AJD_C = (AJD_C[0] + AJD_W * .2, AJD_C[1])
J.append(f'tl.set("#world", {{attr:{{viewBox:"{vb((IND_C[0], IND_C[1] - IND_W * .25), IND_W * 2.6)}"}}}}, 0);')
J.append('const VB = document.getElementById("world"); function zoomTo(t, c0, w0, c1, w1, d){ const o = {z:0}; tl.to(o, {z:1, duration:d, ease:"power2.inOut", onUpdate:()=>{ const w = Math.exp(Math.log(w0) + (Math.log(w1) - Math.log(w0)) * o.z); const f = (w0 - w) / (w0 - w1); const cx = c0[0] + (c1[0] - c0[0]) * f, cy = c0[1] + (c1[1] - c0[1]) * f; const h = w * 1920 / 1080; VB.setAttribute("viewBox", (cx - w / 2) + " " + (cy - h / 2) + " " + w + " " + h); }}, t); }')
TZ0 = 0.0; TZ1 = 1.05; TZ2 = 2.45
J.append(f'zoomTo(0, [{IND_C[0]:.1f},{IND_C[1] - IND_W * .25:.1f}], {IND_W * 2.6:.1f}, [{IND_C[0]:.1f},{IND_C[1]:.1f}], {IND_W:.1f}, 1.0);')
J.append(f'zoomTo({TZ1}, [{IND_C[0]:.1f},{IND_C[1]:.1f}], {IND_W:.1f}, [{RAJ_C[0]:.1f},{RAJ_C[1]:.1f}], {RAJ_W:.1f}, 1.2);')
J.append(f'zoomTo({TZ2:.2f}, [{RAJ_C[0]:.1f},{RAJ_C[1]:.1f}], {RAJ_W:.1f}, [{AJD_C[0]:.1f},{AJD_C[1]:.1f}], {AJD_W:.1f}, 1.4);')
CAMS[:] = [(0, 1.0, IND_C, IND_W), (TZ1, 1.2, RAJ_C, RAJ_W), (TZ2, 1.4, AJD_C, AJD_W)]
J.append(f'tl.to("#bout", {{opacity:.55, duration:.6}}, {TZ2 + 1.0:.2f}); tl.to("#bout", {{opacity:.25, duration:.5}}, {S(1) - .3:.2f}); tl.to("#bout", {{opacity:0, duration:.5}}, {S(2):.2f});')
J.append(f'tl.fromTo("#bind", {{fillOpacity:0}}, {{fillOpacity:.88, duration:.5}}, .3); tl.to("#bind", {{fillOpacity:0, duration:.5}}, {TZ1 + .2:.2f});'
         f'tl.to("#braj", {{opacity:1, fillOpacity:.92, duration:.4}}, {TZ1 + .2:.2f}); tl.to("#bdist", {{opacity:1, duration:.4}}, {TZ1 + .8:.2f});'
         f'tl.to("#baj", {{opacity:1, fillOpacity:.95, duration:.3}}, {TZ1 + 1.1:.2f}); tl.to("#baj", {{fillOpacity:.7, duration:.35, yoyo:true, repeat:3}}, {TZ1 + 1.4:.2f});'
         f'tl.to(["#braj", "#bdist", "#bind"], {{opacity:0, duration:.5}}, {TZ2 + 1.2:.2f}); tl.to("#baj", {{fillOpacity:.5, duration:.5}}, {TZ2 + 1.3:.2f}); tl.to("#baj", {{fillOpacity:0, opacity:.7, duration:.5}}, {S(1) - .2:.2f}); tl.to(["#ajgrey", ".ajg"], {{opacity:0, duration:.6}}, {S(1) - .3:.2f});')
H.append('<div class="mlab" id="ml_ind">INDIA</div><div class="mlab pk" id="ml_raj">RAJASTHAN</div><div class="mlab yl" id="ml_aj">AJMER</div>')
x, y = scr(((bbw(BD["india"])[0] + bbw(BD["india"])[2]) / 2, (bbw(BD["india"])[1] + bbw(BD["india"])[3]) / 2), 1.05)
J.append(f'tl.set("#ml_ind", {{left:{x:.0f}, top:{y + 120:.0f}}}, 0); tl.fromTo("#ml_ind", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.3}}, .6); tl.to("#ml_ind", {{opacity:0, duration:.2}}, {TZ1:.2f});')
bx = bbw(BD["raj"]); x, y = scr(((bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2), TZ1 + 1.3)
J.append(f'tl.set("#ml_raj", {{left:{x:.0f}, top:{y:.0f}}}, 0); tl.fromTo("#ml_raj", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.3}}, {TZ1 + .5:.2f}); tl.to("#ml_raj", {{opacity:0, duration:.2}}, {TZ1 + 1.0:.2f});')
bx = bbw(BD["ajmer"]); x, y = scr(((bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2), TZ1 + 1.2)
J.append(f'tl.set("#ml_aj", {{left:{x:.0f}, top:{y:.0f}}}, 0); tl.fromTo("#ml_aj", {{opacity:0, scale:.5}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2.5)"}}, {TZ1 + 1.1:.2f}); tl.to("#ml_aj", {{opacity:0, duration:.2}}, {TZ2:.2f});')
sfx("whoosh", 0, .45); sfx("whoosh", TZ1, .35); sfx("pop", TZ1 + 1.1, .35); sfx("whoosh", TZ2, .35)
H.append('<div id="clouds"><img id="cl0" src="assets/img/cloud0.png"/><img id="cl1" src="assets/img/cloud1.png"/></div>')
J.append('tl.fromTo("#cl0", {scale:1, y:0, opacity:1}, {scale:2.4, y:500, opacity:0, duration:1.5, ease:"power2.in"}, 0); tl.fromTo("#cl1", {scale:1, y:0, opacity:1}, {scale:2.6, y:-600, opacity:0, duration:1.3, ease:"power2.in"}, 0);')
H.append('<div id="series">RAJASTHAN KE 41 RANG · EP 01/41</div>')
J.append(f'tl.fromTo("#series", {{opacity:0, y:-20}}, {{opacity:1, y:0, duration:.3}}, .1); tl.to("#series", {{opacity:0, duration:.3}}, {TZ2 + 1.2:.2f});')
sfx("impact-bass-1", .05, .45)


# ---------- FOLLOW ----------
H.append('<div id="follow"><div class="fhead"><div class="fav">DB</div><div class="fst"><p><b>ep 01</b><span>episodes</span></p><p><b>41</b><span>districts</span></p><p><b>&#9733;</b><span>daily</span></p></div></div>'
         '<div class="fname">Digital Banjaaraa</div><div class="fbio">Rajasthan real estate, maps se samjho<br/>Har district, ek-ek karke</div><div class="fbtn"><span id="fb1">Follow</span><span id="fb2">Following &#10003;</span></div></div>')
J.append(f'tl.to("#dim", {{opacity:.6, duration:.3}}, {S(5) - .1:.2f}); tl.fromTo("#follow", {{opacity:0, scale:.6, y:80}}, {{opacity:1, scale:1, y:0, duration:.4, ease:"back.out(1.8)"}}, {S(5):.2f});'
         f'tl.set("#fb1", {{display:"none"}}, {wt(5, "follow") + .2:.2f}); tl.set("#fb2", {{display:"inline"}}, {wt(5, "follow") + .2:.2f}); tl.fromTo(".fbtn", {{scale:.85}}, {{scale:1, duration:.3, ease:"back.out(3)", immediateRender:false}}, {wt(5, "follow") + .2:.2f});'
         f'tl.to("#follow", {{opacity:0, scale:.9, duration:.2}}, {S(6) - .15:.2f}); tl.to("#dim", {{opacity:.12, duration:.3}}, {S(6):.2f});')
sfx("pop", S(5), .35); sfx("click-soft", wt(5, "follow") + .2, .5)

# ---------- 1 ROCHAK ----------
theme(1, "05", "KYA AAPKO PATA HAI?", S(6), S(7))
card("r1", "board", S(6) + .05, wt(6, "RPSC") - .05, "RAJASTHAN BOARD (BSER)", "Board of Secondary Education", ("HQ: AJMER", CYAN), info="1957 se. Rajasthan ke lakhon students ki<br/>10th-12th pariksha yahin se hoti hai.")
card("r2", "rpsc", wt(6, "RPSC"), S(7) + .05, "RPSC", "Rajasthan Public Service Commission", ("HQ: AJMER", CYAN), info="RAS jaisi sarkari bhartiyon ki pariksha.<br/>Har naukri aspirant ka sapna yahin se.")
H.append('<div id="hqb">DONO KA HEADQUARTERS: <b>AJMER</b></div>')
J.append(f'tl.fromTo("#hqb", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.3, ease:"back.out(2)"}}, {wt(6, "headquarters") - .1:.2f}); tl.to("#hqb", {{opacity:0, duration:.2}}, {S(7) - .1:.2f});')
sfx("pop", S(6), .3); sfx("pop", wt(6, "RPSC"), .3); sfx("impact-bass-1", wt(6, "headquarters"), .35)

# ---------- 2 AASTHA ----------
theme(2, "01", "AASTHA", S(1), S(2))
fly("dargah", S(1) - .3, 420); card("a1", "dargah", S(1) + .25, wt(1, "Pushkar ka"), "AJMER SHARIF DARGAH", "Khwaja Garib Nawaz", ("AASTHA", PINK), info="Sufi sant Khwaja Moinuddin Chishti ki dargah.<br/>Har saal Urs mein lakhon zaayreen aate hain, har dharm ke log.")
label("la1", "dargah", S(1) - .3, wt(1, "Pushkar ka"))
fly("brahma", wt(1, "Pushkar ka") - .3, 600); card("a2", ["brahma_temple", "pushkar_ghat1", "pushkar_ghat2"], wt(1, "Pushkar ka"), wt(1, "Pushkar mela") - .2, "BRAHMA MANDIR", "Pushkar · ghaat aur pavitra jheel", ("AASTHA", PINK), info="Duniya ke gine-chune Brahma mandiron mein se ek.<br/>Pushkar jheel ke kinare 52 ghaat.")
label("la2", "brahma", wt(1, "Pushkar ka") - .3, S(2))
card("a3", "pushkar_mela", wt(1, "Pushkar mela") - .2, S(2) + .2, "PUSHKAR MELA", "Duniya bhar mein mashhoor", ("MELA", PINK), info="Kartik mahine (Oct-Nov) mein, Kartik Purnima tak.<br/>Duniya ke sabse bade camel fairs mein se ek.")
J.append(f'tl.to("#pin_mela", {{opacity:1, duration:.2}}, {wt(1, "Pushkar mela") - .2:.2f});')

# ---------- 3 KHAANA ----------
theme(3, "03", "KHAANA", S(3), S(4))
for i, (img, nm, w_) in enumerate([("sohan_halwa", "SOHAN HALWA", "sohan"), ("malpua", "MALPUA", "malpue"), ("gulkand", "GULKAND", "gulkand")]):
    t0 = wt(3, w_) - .15; t1 = (wt(3, ["malpue", "gulkand"][i]) - .15) if i < 2 else S(4) + .1
    card(f"k{i}", img, t0, t1, nm, ["Ajmer", "Pushkar", "Pushkar ke gulab"][i], ("KHAANA", "#FF9F43"), info=["Ghee, chini aur dry fruits se bani<br/>Ajmer ki pehchaan wali mithai.", "Ghee mein tale, chashni mein doobe<br/>Pushkar ke mashhoor malpue.", "Pushkar ke desi gulab ki pattiyon<br/>aur chini se bana gulkand."][i])
J.append(f'tl.to("#dim", {{opacity:.55, duration:.3}}, {S(3):.2f}); tl.to("#dim", {{opacity:.15, duration:.3}}, {S(4):.2f});')

# ---------- 4 GHOOMNA ----------
theme(4, "02", "GHOOMNE KI JAGAH", S(2), S(3))
fly("anasagar", S(2) - .2, CITY_W * 1.3)
card("g1", ["ana_sagar_baradari", "ana_sagar"], wt(2, "Ana Sagar"), wt(2, "Adhai"), "ANA SAGAR JHEEL", "Baradari, Ajmer", ("GHOOMNA", CYAN), info="Prithviraj Chauhan ke dada Arnoraja ne banwayi (12vi sadi).<br/>Kinare ki marble baradari Shah Jahan ne banwayi.")
label("lg1", "anasagar", S(2) - .2, S(3) + .2)
J.append(f'tl.to(["#pin_adhai", "#pin_soniji"], {{opacity:1, duration:.2}}, {wt(2, "Adhai") - .2:.2f});')
label("lg2", "adhai", wt(2, "Adhai") - .5, S(3) + .2, dy=48); label("lg3", "soniji", wt(2, "Soniji") - .5, S(3) + .2)
card("g2", "adhai_din", wt(2, "Adhai"), wt(2, "Soniji"), "ADHAI DIN KA JHONPRA", "", ("GHOOMNA", CYAN), info="1199 mein Qutb-ud-din Aibak ne banwaya.<br/>Kahani hai ki yeh dhai din mein bana, isliye yeh naam.")
card("g3", "soniji_nasiyan", wt(2, "Soniji"), S(3) + .2, "SONIJI KI NASIYAN", "Sone ka Jain mandir", ("GHOOMNA", CYAN), info="1865 mein bana Digambar Jain mandir.<br/>Andar 'Swarna Nagari': sone ki parat chadhi lakdi se bani Jain duniya.")

# ---------- 5 MASHHOOR ----------
theme(5, "04", "MASHHOOR", S(4), S(6))
fly("kishangarh", S(4) - .3, 900)
card("m1", "bani_thani", S(4) + .1, wt(4, "Mayo") - .1, "BANI-THANI", "Rajasthan ki Mona Lisa · Kishangarh", ("MASHHOOR", GOLD), maxh=600, info="Kishangarh shaili, chitrakar Nihal Chand (lagbhag 1750).<br/>1973 mein is par India Post ka stamp bhi aaya.")
fly("mayo", wt(4, "Mayo") - .4, 420)
card("m2", "mayo_college", wt(4, "Mayo") - .1, S(6) + .1, "MAYO COLLEGE", "1875 se", ("MASHHOOR", GOLD), info="Lord Mayo ke naam par, 1875 mein shuru.<br/>Desh ke sabse purane boarding schools mein se ek.")
label("lm2", "mayo", wt(4, "Mayo") - .4, S(6), dy=60)

# ---------- 6 SHOPPING ----------
theme(6, "06", "SHOPPING", S(7), S(8))
fly("bazaar", S(7) - .3, 520)
card("s1", "pushkar_bazaar", wt(7, "Pushkar"), wt(7, "marble"), "PUSHKAR BAZAAR", "", ("SHOP", PINK), info="Kadhai wale bags, kapde, chandi ke gehne<br/>aur rang-birangi Rajasthani cheezein.")
label("ls1", "bazaar", S(7) - .3, wt(7, "marble"))
fly("mandi", wt(7, "marble") - .3, 700)
card("s2", ["kishangarh_mandi", "marble_quarry"], wt(7, "marble"), S(8) + .1, "KISHANGARH MARBLE MANDI", "Desh ki sabse badi marble mandiyon mein se ek", ("SHOP", PINK), info="Desh bhar se builders yahan marble lene aate hain.<br/>Saath mein granite aur stone ka bada kaarobaar.")
label("ls2", "mandi", wt(7, "marble") - .3, S(8))


# ---------- NUMBERS (inside hook) ----------
TN0 = max(wt(0, "aabadi") - .1, TZ2 + 1.3)
theme(7, "&#9733;", "AJMER IN NUMBERS", TN0, S(1))
H.append('<div id="nums"><div class="nb" id="nb0"><i>&#128101;</i><div><b>~26 LAKH</b><span>AABADI &middot; Botswana desh (23.6 lakh) se bhi zyada</span></div></div>'
         '<div class="nb" id="nb1"><i>&#128200;</i><div><b>&#8377;70,283 CR</b><span>ECONOMY &middot; Maldives ($6.6 bn) se bhi badi</span></div></div>'
         '<div class="nb" id="nb2"><i>&#128176;</i><div><b>~&#8377;2 LAKH</b><span>PER CAPITA INCOME &middot; saal ka</span></div></div>'
         '<em>Census 2011 (before Beawar split) · DES Rajasthan Economic Review 2024-25 (GDDP 2023-24) · Botswana census 2022 · Maldives GDP 2023</em></div>')
J.append(f'tl.fromTo("#nums", {{opacity:0}}, {{opacity:1, duration:.2}}, {TN0:.2f}); tl.to("#nums", {{opacity:0, duration:.2}}, {S(1) - .1:.2f});')
for i_, t in enumerate([TN0, max(wt(0, "economy") - .1, TN0 + .8), E(0) - .3]):
    J.append(f'tl.fromTo("#nb{i_}", {{opacity:0, x:-80}}, {{opacity:1, x:0, duration:.3, ease:"back.out(2)"}}, {t:.2f});'); sfx("pop", t, .3)
# country comparison panels (shape filled with flag)
CT = json.load(open("data/countries.json"))
def cpanel(cid, name, flag_svg, t0, t1, box_w, box_h, label, sub, col):
    g = CT[name]; polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
    xs = [c[0] for p_ in polys for c in p_[0]]; ys = [c[1] for p_ in polys for c in p_[0]]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys); k = min(box_w / (x1 - x0), box_h / (y1 - y0))
    ox = (box_w - (x1 - x0) * k) / 2; oy = (box_h - (y1 - y0) * k) / 2
    d = " ".join("M" + " L".join(f"{ox + (c[0] - x0) * k:.1f} {oy + (y1 - c[1]) * k:.1f}" for c in p_[0]) + " Z" for p_ in polys)
    fw, fh = (x1 - x0) * k, (y1 - y0) * k; s_ = max(fw / 3, fh / 2); FW, FH = 3 * s_, 2 * s_
    fx, fy = ox + (fw - FW) / 2, oy + (fh - FH) / 2
    H.append(f'<div class="cpan" id="{cid}" style="border-color:{col}"><svg width="{box_w}" height="{box_h}" style="overflow:visible"><defs><clipPath id="{cid}c"><path d="{d}"/></clipPath>'
             f'<filter id="{cid}g" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="7"/></filter></defs>'
             f'<path d="{d}" style="fill:none;stroke:{col};stroke-width:14;stroke-linejoin:round;opacity:.6" filter="url(#{cid}g)"/>'
             f'<g clip-path="url(#{cid}c)"><g transform="translate({fx:.1f},{fy:.1f}) scale({FW / 300:.4f},{FH / 200:.4f})">{flag_svg}</g></g>'
             f'<path d="{d}" style="fill:none;stroke:#fff;stroke-width:4;stroke-linejoin:round"/></svg>'
             f'<svg class="fchip" width="96" height="64" viewBox="0 0 300 200">{flag_svg}</svg>'
             f'<b>{label}</b><span>{sub}</span></div>')
    J.append(f'tl.fromTo("#{cid}", {{opacity:0, scale:.4, rotation:-6}}, {{opacity:1, scale:1, rotation:0, duration:.4, ease:"back.out(2)"}}, {t0:.2f}); tl.to("#{cid}", {{opacity:0, scale:.8, duration:.2}}, {t1 - .2:.2f});')
    sfx("pop", t0, .35)
BW_FLAG = '<rect width="300" height="200" fill="#75AADB"/><rect y="75" width="300" height="50" fill="#fff"/><rect y="83.3" width="300" height="33.3" fill="#000"/>'
MV_FLAG = '<rect width="300" height="200" fill="#D21034"/><rect x="50" y="50" width="200" height="100" fill="#007E3A"/><circle cx="160" cy="100" r="33" fill="#fff"/><circle cx="173" cy="100" r="28" fill="#007E3A"/>'
TB = wt(0, "Botswana") - .15; TM = wt(0, "Maldives") - .15
cpanel("cbw", "Botswana", BW_FLAG, TB, max(TM, TB + 1.4), 380, 380, "BOTSWANA", "23.6 lakh log &middot; Ajmer se kam!", "#75AADB")
cpanel("cmv", "Maldives", MV_FLAG, TM, S(1) - .05, 380, 380, "MALDIVES", "Economy ~$6.6 bn &middot; Ajmer se chhoti!", "#D21034")
J.append(f'tl.to("#nb0 span", {{color:"#FFC42E", duration:.2}}, {wt(0, "Botswana") - .1:.2f}); tl.to("#nb1 span", {{color:"#FFC42E", duration:.2}}, {wt(0, "Maldives") - .1:.2f});')

# ---------- 8 FUTURE ----------
theme(70, "07", "FUTURE", S(8), S(9))
W["expmid"] = EXP[1]; FW = (EXP[0][0] - W["ajmer"][0]) * 1.3; FC = ((W["ajmer"][0] + EXP[0][0]) / 2, (W["ajmer"][1] + EXP[0][1]) / 2 + FW * .12); cam(S(8) - .2, FC, FW, .9); CAMS.append((S(8) - .2, .9, FC, FW))
J.append(f'tl.to(["#exp", "#expb", "#expg"], {{strokeDashoffset:0, duration:1.2, ease:"power2.out"}}, {S(8) + .1:.2f}); tl.to("#expg", {{strokeOpacity:.6, duration:.35, yoyo:true, repeat:5}}, {S(8) + 1.3:.2f}); tl.to(["#exp", "#expb", "#expg"], {{opacity:.5, duration:.4}}, {S(10) + 1:.2f});')
label("lf1", "expmid", S(8) + .6, S(9), "Kotputli-Kishangarh<br/>Expressway", dy=-20)
J.append(f'tl.to("#pin_airport", {{opacity:1, duration:.2}}, {wt(8, "airport") - .3:.2f});')
card("fair", "airport", wt(8, "airport") - .1, wt(8, "Smart City") - .2, "KISHANGARH AIRPORT", "", ("FUTURE", "#FF8A00"), top=420, maxw=640, maxh=520, info="October 2017 se shuru.<br/>Ajmer, Pushkar aur Kishangarh ka hawai rasta."); label("lf2", "airport", wt(8, "airport") - .5, S(9), "&#9992; Kishangarh Airport")
J.append(f'tl.to(["#pin_dargah", "#pin_mayo"], {{opacity:1, duration:.2}}, {wt(8, "Smart City") - .3:.2f});'); label("lf3", "ajmer", wt(8, "Smart City") - .5, S(9), "AJMER · SMART CITY", dy=-70)
H.append('<div class="foot" id="ff">Expressway alignment indicative</div>'); J.append(f'tl.fromTo("#ff", {{opacity:0}}, {{opacity:1, duration:.2}}, {S(8):.2f}); tl.to("#ff", {{opacity:0, duration:.2}}, {S(9):.2f});')

# ---------- 8 ITIHAAS ----------
theme(8, "08", "ITIHAAS", S(9), S(10))
card("i1", "prithviraj_painting", wt(9, "Prithviraj") - .1, S(10) + .1, "PRITHVIRAJ CHAUHAN", "Ajmer ki rajdhani se raaj · painting", ("ITIHAAS", "#B98CFF"), maxh=600, info="12vi sadi ke Chauhan raja, rajdhani Ajmer.<br/>Tarain ke yuddh (1191, 1192) ke liye mashhoor.")
H.append('<div id="ajay"><b>AJAYAMERU</b> &rarr; <b>AJMER</b><span>Chauhan raja Ajayaraja ne basaya</span></div>')
J.append(f'tl.fromTo("#ajay", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.3}}, {S(9) + .1:.2f}); tl.to("#ajay", {{opacity:0, duration:.2}}, {wt(9, "Prithviraj") - .1:.2f});')
J.append(f'tl.to("#dim", {{opacity:.55, duration:.3}}, {S(9):.2f}); tl.to("#dim", {{opacity:.15, duration:.3}}, {S(10):.2f});')

# ---------- 9 CONNECT ----------
theme(9, "09", "CONNECTIVITY", S(10), S(11))
JPR = wp(26.9124, 75.7873); DUDU = wp(26.6811, 75.2321)
NH2 = [W["ajmer"], W["kishangarh"], DUDU, JPR]
SVG.append(f'<path id="nh2g" d="{pd(NH2)}" pathLength="1" style="fill:none;stroke:{GOLD};stroke-width:14;stroke-opacity:.35;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>'
           f'<path id="nh2" d="{pd(NH2)}" pathLength="1" style="fill:none;stroke:{GOLD};stroke-width:6;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>'
           f'<g id="jpin" style="opacity:0"><circle cx="{JPR[0]:.1f}" cy="{JPR[1]:.1f}" r="60" style="fill:{PINK};opacity:.3"/><circle cx="{JPR[0]:.1f}" cy="{JPR[1]:.1f}" r="26" style="fill:{PINK};stroke:#fff;stroke-width:9"/></g>')
CC_C, CC_W = fitb((W["brahma"][0], min(JPR[1], W["kishangarh"][1]), JPR[0], W["mayo"][1]), 760, 1340, 1.3)
cam(S(10) - .2, CC_C, CC_W, 1.1); CAMS.append((S(10) - .2, 1.1, CC_C, CC_W))
J.append(f'tl.to(["#nh2", "#nh2g"], {{strokeDashoffset:0, duration:1.2, ease:"power2.out"}}, {S(10) + .4:.2f}); tl.to("#jpin", {{opacity:1, duration:.3}}, {S(10) + 1.4:.2f}); tl.to("#bout", {{opacity:0, duration:.1}}, {S(10):.2f});')
x, y = scr(JPR, S(10) + 1.2); H.append(f'<div class="pl" id="ljp" style="left:{min(x, 900):.0f}px;top:{y - 60:.0f}px">JAIPUR</div>')
J.append(f'tl.fromTo("#ljp", {{opacity:0, scale:.5}}, {{opacity:1, scale:1, duration:.25, ease:"back.out(2)"}}, {S(10) + 1.4:.2f}); tl.to("#ljp", {{opacity:0, duration:.2}}, {S(11) - .1:.2f});')
x, y = scr(W["ajmer"], S(10) + 1.2); H.append(f'<div class="pl" id="lajc" style="left:{max(x, 160):.0f}px;top:{y + 60:.0f}px">AJMER</div>')
J.append(f'tl.fromTo("#lajc", {{opacity:0, scale:.5}}, {{opacity:1, scale:1, duration:.25, ease:"back.out(2)"}}, {S(10) + .3:.2f}); tl.to("#lajc", {{opacity:0, duration:.2}}, {S(11) - .1:.2f});')
H.append('<div id="jp">JAIPUR &rarr; <b>135 KM</b><span>NH-48</span></div>'); J.append(f'tl.fromTo("#jp", {{opacity:0, x:60}}, {{opacity:1, x:0, duration:.3, ease:"back.out(2)"}}, {S(10) + .2:.2f}); tl.to("#jp", {{opacity:0, duration:.2}}, {S(11):.2f});')
sfx("whoosh", S(10) - .2, .3)

# ---------- 10 CTA ----------
H.append('<div id="cta"><b>AAP AJMER SE HO?</b><span>COMMENT &ldquo;AJMER&rdquo;</span><em>NEXT EPISODE: <i>ALWAR</i></em></div>')
J.append(f'tl.to("#dim", {{opacity:.55, duration:.3}}, {S(11):.2f}); tl.fromTo("#cta", {{opacity:0}}, {{opacity:1, duration:.2}}, {S(11):.2f}); tl.from("#cta b", {{opacity:0, scale:.6, duration:.3, ease:"back.out(2)"}}, {S(11):.2f});'
         f'tl.from("#cta span", {{opacity:0, y:30, duration:.3}}, {wt(11, "Comment"):.2f}); tl.from("#cta em", {{opacity:0, scale:.5, duration:.3, ease:"back.out(2)"}}, {wt(11, "Next"):.2f});')
sfx("sparkle", wt(11, "Next"), .3)


# ---- card exits: each photo stays until the next one arrives (capped at map moments)
CAPS_T = sorted([S(8), S(10), S(11), S(9) + .2])
CARDS.sort(key=lambda c: c[1])
for i, (cid, t0, t1) in enumerate(CARDS):
    nxt = CARDS[i + 1][1] if i + 1 < len(CARDS) else END
    cap = min([c for c in CAPS_T if c > t0 + .3] + [END])
    out = max(t1, min(nxt + .3, cap))
    J.append(f'tl.set("#{cid}", {{zIndex:{10 + i}}}, 0); tl.to("#{cid}", {{opacity:0, scale:.9, duration:.2, ease:"power2.in"}}, {out - .2:.2f});')

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
SVG.append('<rect id="dim" x="-900000" y="-900000" width="2000000" height="2000000" style="fill:#000;opacity:.12"/>')
CSS = """@font-face{font-family:Anton;src:url(assets/fonts/anton.woff2)}@font-face{font-family:Mont;font-weight:700;src:url(assets/fonts/mont700.woff2)}@font-face{font-family:Mont;font-weight:800;src:url(assets/fonts/mont800.woff2)}@font-face{font-family:Mont;font-weight:900;src:url(assets/fonts/mont900.woff2)}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#07090d}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif}#world{position:absolute;inset:0;width:1080px;height:1920px}.y{color:#FFC42E}
#face{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:40}
#vig{position:absolute;inset:0;pointer-events:none;background:radial-gradient(80% 60% at 50% 45%,rgba(0,0,0,0) 50%,rgba(0,0,0,.6) 100%);z-index:2}#flash{position:absolute;inset:0;background:#fff;opacity:0;z-index:25;pointer-events:none}
#wm{position:absolute;left:0;right:0;top:190px;text-align:center;font:800 24px Mont;letter-spacing:.34em;color:rgba(255,255,255,.55);z-index:20}
#series{position:absolute;left:0;right:0;top:250px;margin:0 auto;width:max-content;padding:8px 22px;border-radius:30px;background:#FFC42E;color:#111;font:900 28px Mont;letter-spacing:.06em;opacity:0;z-index:12}
#big{position:absolute;left:0;right:0;top:420px;text-align:center;opacity:0;font:400 230px/1 Anton;color:#FF4FA3;text-shadow:0 10px 40px rgba(0,0,0,.8);z-index:12}
.th{position:absolute;left:50px;top:250px;display:flex;align-items:center;gap:12px;padding:8px 22px 8px 8px;border-radius:40px;background:rgba(8,10,15,.9);border:2px solid #FFC42E;font:400 44px/1 Anton;color:#fff;letter-spacing:.04em;opacity:0;z-index:12}
.th b{padding:8px 14px;border-radius:30px;background:#FFC42E;color:#111;font:400 38px/1 Anton}
.card{position:absolute;opacity:0;padding:14px 14px 16px;border-radius:24px;background:#fff;box-shadow:0 30px 70px rgba(0,0,0,.7);z-index:8;text-align:center}
.stk{position:relative;margin:0 auto;border-radius:14px;overflow:hidden;background:#111}.lyr{position:absolute;left:0;top:0;overflow:hidden}.lyr img{position:absolute;inset:0;width:100%;height:100%;display:block}.lyr .bgb{object-fit:cover;filter:blur(22px) brightness(.55);transform:scale(1.15)}.dts{position:absolute;right:14px;top:14px;display:flex;gap:7px;padding:7px 9px;border-radius:20px;background:rgba(0,0,0,.55)}.dts i{width:12px;height:12px;border-radius:50%;background:#fff}.ct{margin-top:10px;font:400 58px/1 Anton;color:#14161c;letter-spacing:.02em}.cs{margin-top:6px;font:700 28px Mont;color:#5b6070}
.ci{margin:10px 6px 0;padding-top:10px;border-top:2px solid #e3e3e8;text-align:left;font:700 26px/1.32 Mont;color:#2a2d36}.ci b{color:#c2185b}
.tg{position:absolute;left:-12px;top:-22px;padding:8px 20px;border-radius:30px;font:900 28px Mont;color:#111;box-shadow:0 6px 16px rgba(0,0,0,.4);z-index:2}
.pl{position:absolute;opacity:0;translate:-50% -50%;text-align:center;line-height:1.1;display:flex;align-items:center;gap:10px;padding:6px 18px 6px 6px;border-radius:30px;background:rgba(8,10,15,.9);border:2px solid #FF4FA3;font:800 30px Mont;color:#fff;white-space:nowrap;z-index:6}
.pl b{width:38px;height:38px;border-radius:50%;background:#FF4FA3;color:#111;display:flex;align-items:center;justify-content:center;font:900 22px Mont}
#hq{position:absolute;left:60px;right:60px;top:400px;opacity:0;text-align:center;z-index:9}.hb{display:flex;align-items:center;gap:20px;text-align:left;padding:16px;border-radius:26px;background:rgba(8,10,15,.92);border:3px solid #3CDCFF}
.hb b{display:block;font:400 92px/1 Anton;color:#fff}.hb span{display:block;margin-top:6px;font:800 30px Mont;color:#3CDCFF}.hb img{width:330px;height:220px;object-fit:cover;border-radius:16px;flex:none}.hb b{font-size:70px!important}#hq i{display:block;font:900 70px/1.1 Mont;color:#FFC42E;font-style:normal}
#hq em{display:block;margin-top:22px;font-style:normal;font:900 38px Mont;color:#fff;letter-spacing:.1em}#hq strong{display:block;font:400 180px/1 Anton;color:#FF4FA3}
#nums{position:absolute;left:50px;right:50px;top:340px;opacity:0;z-index:9}.nb{display:flex;align-items:center;gap:22px;margin-bottom:14px;padding:14px 26px;border-radius:26px;background:rgba(8,10,15,.92);border:3px solid #FFC42E}.nb i{font-style:normal;font-size:64px}.nb b{display:block;white-space:nowrap;font:400 74px/1 Anton;color:#FFC42E}.nb span{display:block;margin-top:6px;font:900 28px Mont;color:#fff;letter-spacing:.06em}#nums em{position:absolute;left:0;right:0;top:1265px;display:block;font-style:normal;font:700 21px Mont;color:rgba(255,255,255,.8);text-align:center}
.mlab{position:absolute;opacity:0;translate:-50% -50%;padding:8px 22px;border-radius:6px;background:#fff;font:700 50px/1 Mont;color:#111;box-shadow:0 6px 18px rgba(0,0,0,.5);letter-spacing:.06em;z-index:6}.mlab.pk{color:#111}.mlab.yl{color:#111;background:#fff}
#ov{position:absolute;inset:0;opacity:0;z-index:7}#ovlist{position:absolute;left:50px;right:50px;top:330px;padding:14px 22px;border-radius:24px;background:rgba(8,10,15,.88);border:3px solid #FF4FA3;display:grid;grid-template-columns:1fr 1fr;gap:4px 14px}#ovlist p{display:flex;align-items:center;gap:10px;height:50px;font:800 27px Mont;color:#fff;white-space:nowrap}#ovlist p b{width:36px;height:36px;flex:none;border-radius:50%;background:#FF4FA3;color:#111;display:flex;align-items:center;justify-content:center;font:900 20px Mont}
#hqb{position:absolute;left:40px;right:40px;top:1300px;opacity:0;text-align:center;padding:14px;border-radius:22px;background:#FF4FA3;font:900 40px Mont;color:#111;z-index:12}#hqb b{font:400 54px Anton}
.cpan{position:absolute;right:30px;top:860px;width:450px;opacity:0;padding:22px 20px 18px;border-radius:28px;background:rgba(8,10,15,.88);border:4px solid;z-index:9;text-align:center;display:flex;flex-direction:column;align-items:center}.fchip{position:absolute;left:18px;top:18px;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,.6)}.cpan b{display:block;margin-top:8px;font:400 60px/1 Anton;color:#fff;letter-spacing:.04em}.cpan span{display:block;margin-top:6px;font:900 24px Mont;color:#FFC42E}
#clouds{position:absolute;inset:0;z-index:15;pointer-events:none;overflow:hidden}#clouds img{position:absolute;left:-260px;top:-240px;width:1600px;height:2400px}
#follow{position:absolute;left:60px;right:60px;top:560px;opacity:0;z-index:30;padding:30px;border-radius:30px;background:#16181d;box-shadow:0 30px 80px rgba(0,0,0,.7);color:#fff;font-family:Mont}
.fhead{display:flex;align-items:center;gap:30px}.fav{width:170px;height:170px;border-radius:50%;flex:none;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#FF4FA3,#FFC42E);font:400 70px Anton;color:#111;box-shadow:0 0 0 6px #16181d,0 0 0 10px #FF4FA3}
.fst{display:flex;flex:1;justify-content:space-around}.fst p{text-align:center}.fst b{display:block;font:900 40px Mont}.fst span{font:700 26px Mont;color:#bbb}
.fname{margin-top:22px;font:900 40px Mont}.fbio{margin-top:8px;font:700 30px/1.35 Mont;color:#ddd}.fbtn{margin-top:24px;padding:18px;border-radius:16px;background:#0095F6;text-align:center;font:900 38px Mont}.fbtn #fb2{display:none}
#ajay{position:absolute;left:60px;right:60px;top:430px;opacity:0;text-align:center;padding:30px;border-radius:26px;background:rgba(8,10,15,.92);border:3px solid #B98CFF;font:400 96px/1.1 Anton;color:#fff;z-index:9}
#ajay b{color:#FFC42E;font-weight:400}#ajay span{display:block;margin-top:10px;font:800 34px Mont;color:#ddd}
#jp{position:absolute;right:50px;top:560px;opacity:0;padding:20px 28px;border-radius:24px;background:rgba(8,10,15,.92);border:3px solid #FFC42E;font:400 70px/1 Anton;color:#fff;z-index:9;text-align:right}#jp b{color:#FFC42E;font-weight:400}#jp span{display:block;font:900 30px Mont;color:#ccc;margin-top:6px}
#cta{position:absolute;left:50px;right:50px;top:440px;opacity:0;text-align:center;z-index:12}#cta b{display:block;padding:24px;border-radius:26px;background:#FFC42E;color:#111;font:400 96px/1 Anton}
#cta span{display:inline-block;margin-top:20px;padding:14px 34px;border-radius:30px;background:#FF4FA3;color:#111;font:900 44px Mont}#cta em{display:block;margin:26px auto 0;font-style:normal;font:900 40px Mont;color:#fff}#cta em i{font-style:normal;color:#FFC42E;font:400 80px Anton;display:block}
.foot{position:absolute;left:40px;right:40px;top:1600px;text-align:center;opacity:0;font:700 22px Mont;color:rgba(255,255,255,.7);z-index:6}
.cp{position:absolute;left:40px;right:130px;top:1420px;text-align:center;opacity:0;z-index:35}
.cp div{display:inline-block;padding:4px 20px 8px;border-radius:10px;background:#fff;font:900 62px/1.12 Mont;color:#111;box-shadow:0 8px 24px rgba(0,0,0,.45)}.cp .y{color:#111;background:#FFC42E;border-radius:6px;padding:0 6px}"""
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
