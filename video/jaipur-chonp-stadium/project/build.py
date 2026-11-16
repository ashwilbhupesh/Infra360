"""Jaipur (Chonp) cricket stadium reel — Digital Banjaaraa. Text+music draft; uses rec/phrases.json when the voice arrives.
World = z13 web-mercator px from tile (5791, 3466) (same frame as the Ajmer episode, so India/Rajasthan layers line up)."""
import json, math, os
P = "proj"
ASP = json.load(open("aspects.json"))
LINES = [
    "Duniya ka teesra sabse bada cricket stadium, Jaipur mein. Par kaam ruka kyun?",
    "Chonp mein, 100 acre, 75 hazaar seats.",
    "Aage sirf Ahmedabad aur Melbourne.",
    "Vedanta ke 300 crore, baaki RCA ka.",
    "2022 mein neev, lekin 191 crore ke baad kaam ruka.",
    "Ab IIT Bombay jaanch kar rahi hai, RCA ka plan do saal.",
    "Banega toh hotels, restaurants, zameen ke daam, sab badlega.",
    "Kab tak banega? Comment karo.",
]
VOICE = os.path.exists("rec/phrases.json")
if VOICE: PH = json.load(open("rec/phrases.json"))
else:
    PH = []; t = .3
    for l in LINES:
        d = len(l) / 15 + .2; PH.append({"s": round(t, 2), "e": round(t + d, 2), "t": l}); t += d + .35
def S(k): return PH[k]["s"]
def E(k): return PH[k]["e"]
def wt(k, w):
    t = PH[k]["t"]; i = t.lower().find(w.lower()); assert i >= 0, (k, w)
    return S(k) + (E(k) - S(k)) * i / len(t)
END = round(E(7) + 1.3, 2)
def wp(lat, lon):
    n = 2 ** 13
    return (((lon + 180) / 360 * n) - 5791) * 256, (((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n) - 3466) * 256
SVG, H, J, SFX, CARDS = [], [], [], [], []
def vb(c, w): h = w * 1920 / 1080; return f"{c[0] - w / 2:.1f} {c[1] - h / 2:.1f} {w:.1f} {h:.1f}"
def sfx(n, t, v=.3): SFX.append(f'<audio id="sx{len(SFX)}" class="clip" src="assets/sfx/{n}.mp3" data-start="{t:.2f}" data-duration="2" data-track-index="{20 + len(SFX)}" data-volume="{v}"></audio>')
GOLD, PINK, CYAN, GRN, ORG = "#FFC42E", "#FF4FA3", "#3CDCFF", "#3CFF96", "#FF8A00"
CAMS = []
def cam(t, c, w, d=.9, e="power2.inOut"):
    J.append(f'tl.to("#world", {{attr:{{viewBox:"{vb(c, w)}"}}, duration:{d}, ease:"{e}"}}, {t:.2f});'); CAMS.append((t, d, c, w))
def scr(p, t):
    c, w = CAMS[0][2], CAMS[0][3]
    for t0, d, c1, w1 in sorted(CAMS, key=lambda q: q[0]):
        if t0 + d <= t + 1e-6: c, w = c1, w1
    h = w * 1920 / 1080
    return ((p[0] - (c[0] - w / 2)) / w * 1080, (p[1] - (c[1] - h / 2)) / h * 1920)
def pd(pts): return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)

# ---------- base ----------
BD = json.load(open("data/bounds.json"))
def pdr(rings): return " ".join("M" + " L".join(f"{wp(la, lo)[0]:.1f} {wp(la, lo)[1]:.1f}" for lo, la in r) + " Z" for r in rings)
def bbw(rings):
    pts = [wp(la, lo) for r in rings for lo, la in r]; xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)
def fitb(bb, top, bot, pad=1.12):
    x0, y0, x1, y1 = bb; w = max((x1 - x0) * pad, (y1 - y0) * pad * 1080 / (bot - top))
    return ((x0 + x1) / 2, (y0 + y1) / 2 - ((top + bot) / 2 - 960) * w / 1080), w
SVG.append('<rect x="-900000" y="-900000" width="2000000" height="2000000" style="fill:#0b1a2a"/>')
SVG.append('<image href="assets/img/bm4.jpg" x="-302848" y="-363008" width="786432" height="786432" preserveAspectRatio="none"/>')
SVG.append('<image href="assets/img/bm5.jpg" x="-171776" y="-166400" width="327680" height="393216" preserveAspectRatio="none"/>')
SVG.append('<image href="assets/img/bm7.webp" x="-40704" y="-35328" width="81920" height="65536" preserveAspectRatio="none"/>')
SVG.append('<image href="assets/img/jp11.webp" x="4352" y="-6656" width="7168" height="8192" preserveAspectRatio="none"/>')
SVG.append('<image href="assets/img/ch15.webp" x="7680" y="-3072" width="256" height="320" preserveAspectRatio="none"/>')
SVG.append(f'<path id="bind" d="{pdr(BD["india"])}" style="fill:#fff;fill-opacity:.06;stroke:#fff;stroke-width:3;vector-effect:non-scaling-stroke"/>')
SVG.append(f'<path id="braj" d="{pdr(BD["raj"])}" style="fill:{PINK};fill-opacity:0;stroke:{PINK};stroke-width:5;vector-effect:non-scaling-stroke;opacity:0"/>')
SVG.append(f'<path id="bjp" d="{pdr(BD["jaipur"])}" style="fill:{GOLD};fill-opacity:0;stroke:{GOLD};stroke-width:6;vector-effect:non-scaling-stroke;opacity:0"/>')
JPR = wp(26.9124, 75.7873); CHP = wp(27.1122, 75.8253)
ROUTE = [JPR, wp(26.99, 75.83), wp(27.06, 75.86), wp(27.10, 75.845), CHP]
SVG.append(f'<path id="rtg" d="{pd(ROUTE)}" pathLength="1" style="fill:none;stroke:{GOLD};stroke-width:16;stroke-opacity:.35;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>'
           f'<path id="rt" d="{pd(ROUTE)}" pathLength="1" style="fill:none;stroke:{GOLD};stroke-width:7;vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>')
for k, p, c in [("jpin", JPR, PINK), ("cpin", CHP, GRN)]:
    SVG.append(f'<g id="{k}" style="opacity:0"><circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="22" style="fill:{c};opacity:.3"/><circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="9" style="fill:{c};stroke:#fff;stroke-width:3"/></g>')
SVG.append(f'<circle id="ring" cx="{CHP[0]:.1f}" cy="{CHP[1]:.1f}" r="10" style="fill:none;stroke:#fff;stroke-width:3;vector-effect:non-scaling-stroke;opacity:0"/>')
SVG.append('<rect id="dim" x="-900000" y="-900000" width="2000000" height="2000000" style="fill:#000;opacity:.12"/>')

# ---------- helpers ----------
def card(cid, img, t0, t1, title, sub="", tag=None, top=380, maxw=900, maxh=640, rot=0, left=None, info=None):
    a = ASP[img]; w = maxw; h = w / a
    if h > maxh: h = maxh; w = h * a
    cw = max(w + 28, 760) if info else w + 28; lx = (1080 - cw) / 2 if left is None else left
    tg = f'<div class="tg" style="background:{tag[1]}">{tag[0]}</div>' if tag else ''
    H.append(f'<div class="card" id="{cid}" style="left:{lx:.0f}px;top:{top}px;width:{cw:.0f}px;rotate:{rot}deg">{tg}<img src="assets/img/{img}.jpg" style="width:{w:.0f}px;height:{h:.0f}px"/>'
             f'<div class="ct">{title}</div>' + (f'<div class="cs">{sub}</div>' if sub else '') + (f'<div class="ci">{info}</div>' if info else '') + '</div>')
    J.append(f'tl.fromTo("#{cid}", {{opacity:0, scale:.55, y:60}}, {{opacity:1, scale:1, y:0, duration:.32, ease:"back.out(1.7)"}}, {t0:.2f});'); CARDS.append([cid, t0, t1])
    sfx("pop", t0, .25)
def theme(i, txt, t, until):
    H.append(f'<div class="th" id="th{i}">{txt}</div>')
    J.append(f'tl.fromTo("#th{i}", {{opacity:0, x:-60}}, {{opacity:1, x:0, duration:.3, ease:"power3.out"}}, {t:.2f}); tl.to("#th{i}", {{opacity:0, duration:.2}}, {until - .2:.2f});')
    J.append(f'tl.fromTo("#flash", {{opacity:.4}}, {{opacity:0, duration:.25, immediateRender:false}}, {t:.2f});')
def pl(i, p, text, t, until, at, dy=-60, cls=""):
    x, y = scr(p, at); H.append(f'<div class="pl {cls}" id="{i}" style="left:{min(max(x, 200), 880):.0f}px;top:{y + dy:.0f}px">{text}</div>')
    J.append(f'tl.fromTo("#{i}", {{opacity:0, scale:.5}}, {{opacity:1, scale:1, duration:.25, ease:"back.out(2)"}}, {t:.2f}); tl.to("#{i}", {{opacity:0, duration:.2}}, {until - .2:.2f});')

# ---------- 0 HOOK: India -> Rajasthan -> Jaipur -> Chonp ----------
IND_C, IND_W = fitb(bbw(BD["india"]), 700, 1400, 1.08)
RAJ_C, RAJ_W = fitb(bbw(BD["raj"]), 720, 1380, 1.1)
JP_C, JP_W = fitb(bbw(BD["jaipur"]), 760, 1380, 1.15)
CH_C, CH_W = (CHP[0], CHP[1] - 40), 260
J.append(f'tl.set("#world", {{attr:{{viewBox:"{vb(IND_C, IND_W)}"}}}}, 0);')
J.append('const VB = document.getElementById("world"); function zoomTo(t, c0, w0, c1, w1, d){ const o = {z:0}; tl.to(o, {z:1, duration:d, ease:"power2.inOut", onUpdate:()=>{ const w = Math.exp(Math.log(w0) + (Math.log(w1) - Math.log(w0)) * o.z); const f = (w0 - w) / (w0 - w1); const cx = c0[0] + (c1[0] - c0[0]) * f, cy = c0[1] + (c1[1] - c0[1]) * f; const h = w * 1920 / 1080; VB.setAttribute("viewBox", (cx - w / 2) + " " + (cy - h / 2) + " " + w + " " + h); }}, t); }')
Z = [(.35, IND_C, IND_W, RAJ_C, RAJ_W, 1.0), (1.4, RAJ_C, RAJ_W, JP_C, JP_W, 1.0), (2.5, JP_C, JP_W, CH_C, CH_W, 1.3)]
for t, c0, w0, c1, w1, d in Z:
    J.append(f'zoomTo({t}, [{c0[0]:.1f},{c0[1]:.1f}], {w0:.1f}, [{c1[0]:.1f},{c1[1]:.1f}], {w1:.1f}, {d});'); CAMS.append((t, d, c1, w1))
CAMS.insert(0, (0, 0, IND_C, IND_W))
J.append('tl.to("#braj", {opacity:1, fillOpacity:.4, duration:.3}, .3); tl.to("#braj", {fillOpacity:.1, duration:.4}, 1.3); tl.to("#bjp", {opacity:1, fillOpacity:.45, duration:.3}, 1.5); tl.to("#bjp", {fillOpacity:.05, duration:.5}, 2.6);'
         'tl.to(["#braj", "#bind"], {opacity:0, duration:.4}, 2.4); tl.to("#bjp", {opacity:.5, duration:.4}, 3.6); tl.to("#cpin", {opacity:1, duration:.2}, 3.3); tl.fromTo("#ring", {attr:{r:6}, opacity:1}, {attr:{r:60}, opacity:0, duration:.8, repeat:2, immediateRender:false}, 3.4);')
sfx("whoosh", .35, .3); sfx("whoosh", 1.4, .3); sfx("whoosh", 2.5, .35)
H.append('<div id="series">JAIPUR KA MEGA PROJECT</div>')
J.append(f'tl.fromTo("#series", {{opacity:0, y:-20}}, {{opacity:1, y:0, duration:.3}}, .1); tl.to("#series", {{opacity:0, duration:.3}}, {S(1) - .1:.2f});')
H.append('<div id="hook"><small>DUNIYA KA</small><b>3RD</b><span>SABSE BADA CRICKET STADIUM</span><i>JAIPUR MEIN</i></div>')
J.append(f'tl.fromTo("#hook", {{opacity:0, scale:1.4}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, .2); tl.from("#hook i", {{opacity:0, y:30, duration:.3}}, {wt(0, "Jaipur") - .1:.2f}); tl.to("#hook", {{opacity:0, duration:.2}}, {wt(0, "Par kaam") - .1:.2f});')
card("h1", "render", wt(0, "Par kaam") - .1, S(1) - .4, "KAAM RUKA KYUN?", "", ("?", PINK), top=420, maxw=900, maxh=520)
sfx("impact-bass-1", .2, .5); sfx("impact-bass-1", wt(0, "Par kaam"), .4)

# ---------- 1 LOCATION ----------
theme(1, "&#128205; KAHAN?", S(1), S(2))
LC_C, LC_W = fitb((JPR[0] - 60, CHP[1] - 40, JPR[0] + 220, JPR[1] + 40), 760, 1330, 1.25)
cam(S(1) - .2, LC_C, LC_W, 1.0)
J.append(f'tl.to("#bjp", {{opacity:0, duration:.3}}, {S(1):.2f}); tl.to("#jpin", {{opacity:1, duration:.2}}, {S(1) + .4:.2f}); tl.to(["#rt", "#rtg"], {{strokeDashoffset:0, duration:1.0, ease:"power2.out"}}, {S(1) + .5:.2f});')
pl("ljp", JPR, "JAIPUR", S(1) + .4, S(2), S(1) + 1)
pl("lch", CHP, "CHONP &middot; STADIUM SITE", S(1) + 1.4, S(2), S(1) + 1, cls="g")
pl("lkm", ROUTE[2], "~25 KM", S(1) + 1.0, S(2), S(1) + 1, dy=0, cls="y")
H.append('<div id="facts"><div><b>100</b><span>ACRE</span></div><div><b>75,000</b><span>SEATS</span></div></div>')
J.append(f'tl.fromTo("#facts", {{opacity:0}}, {{opacity:1, duration:.2}}, {wt(1, "100") - .1:.2f}); tl.from("#facts div", {{opacity:0, scale:.4, duration:.3, stagger:{wt(1, "75") - wt(1, "100"):.2f}, ease:"back.out(2.2)"}}, {wt(1, "100") - .1:.2f}); tl.to("#facts", {{opacity:0, duration:.2}}, {S(2) - .1:.2f});')
sfx("pop", wt(1, "100"), .3); sfx("pop", wt(1, "75"), .3)

# ---------- 2 COMPARISON ----------
theme(2, "&#127942; DUNIYA KE SABSE BADE", S(2), S(3))
J.append(f'tl.to("#dim", {{opacity:.65, duration:.3}}, {S(2) - .1:.2f}); tl.to("#dim", {{opacity:.12, duration:.3}}, {S(3):.2f});')
H.append('<div id="rank">'
         '<div class="rk" id="rk0"><img src="assets/img/modi.jpg"/><div><i>#1</i><b>NARENDRA MODI STADIUM</b><span>Ahmedabad &middot; 1,32,000</span><u style="width:100%"></u></div></div>'
         '<div class="rk" id="rk1"><img src="assets/img/mcg.jpg"/><div><i>#2</i><b>MELBOURNE CRICKET GROUND</b><span>Australia &middot; ~1,00,000</span><u style="width:76%"></u></div></div>'
         '<div class="rk hot" id="rk2"><img src="assets/img/render.jpg"/><div><i>#3</i><b>JAIPUR (CHONP)</b><span>Rajasthan &middot; 75,000 (planned)</span><u style="width:57%"></u></div></div></div>')
J.append(f'tl.fromTo("#rank", {{opacity:0}}, {{opacity:1, duration:.2}}, {S(2):.2f}); tl.to("#rank", {{opacity:0, duration:.2}}, {S(3) - .1:.2f});')
for i, t in enumerate([wt(2, "Ahmedabad"), wt(2, "Melbourne"), S(2) + .1]):
    J.append(f'tl.fromTo("#rk{i}", {{opacity:0, x:-80}}, {{opacity:1, x:0, duration:.3, ease:"back.out(2)"}}, {t - .1:.2f}); tl.from("#rk{i} u", {{scaleX:0, transformOrigin:"0 50%", duration:.6}}, {t:.2f});'); sfx("pop", t, .3)

# ---------- 3 NAME + MONEY ----------
theme(3, "&#128176; PAISA KAHAN SE?", S(3), S(4))
cam(S(3) - .2, (CHP[0], CHP[1] + 30), 170, .9)
card("n1", "render_aerial", S(3), wt(3, "Vedanta") - .1, "ANIL AGARWAL INTERNATIONAL CRICKET STADIUM", "Design render", ("NAAM", GOLD), maxh=560,
     info="Practice grounds, academy, aur 3,500+ gaadiyon ki parking ka plan.")
card("n2", "statesman", wt(3, "Vedanta") - .1, S(4) + .1, "VEDANTA (HZL) + RCA", "MoU &middot; 30 March 2023", ("&#8377;300 CR + RCA", GOLD), maxw=520, maxh=600,
     info="Hindustan Zinc ke &#8377;300 crore,<br/>baaki RCA. Kul lagat ~&#8377;400 crore (shuruaati anumaan).")

# ---------- 4 STALLED ----------
theme(4, "&#9888; KAAM RUKA", S(4), S(5))
card("s1", "foundation", S(4) + .05, wt(4, "lekin") + .2, "NEEV: 5 FEBRUARY 2022", "Shilanyas", ("2022", CYAN), info="Pehle phase mein 40,000 seats,<br/>doosre mein 35,000 aur.")
card("s2", "construction", wt(4, "lekin") + .2, S(5) + .2, "~&#8377;191 CR KHARCH, PHIR KAAM THAP", "Site ki tasveer", ("RUKA", "#FF4646"), info="Karib do saal tak nirmaan ruka raha<br/>(Times Now, ETV Bharat).")

# ---------- 5 2026 ----------
theme(5, "&#128295; AB KYA HO RAHA HAI?", S(5), S(6))
H.append('<div id="now"><p id="nw0"><b>2026</b>RCA ne jaanch committee banayi</p><p id="nw1"><b>IIT BOMBAY</b>Concrete, steel, foundation ki structural jaanch</p><p id="nw2"><b>TARGET</b>Agle 2 saal mein poora karna</p></div>')
J.append(f'tl.to("#dim", {{opacity:.55, duration:.3}}, {S(5) - .1:.2f}); tl.fromTo("#now", {{opacity:0}}, {{opacity:1, duration:.2}}, {S(5):.2f}); tl.to("#now", {{opacity:0, duration:.2}}, {S(6) - .1:.2f}); tl.to("#dim", {{opacity:.12, duration:.3}}, {S(6):.2f});')
for i, t in enumerate([S(5), wt(5, "IIT"), wt(5, "RCA ka plan")]):
    J.append(f'tl.fromTo("#nw{i}", {{opacity:0, x:-60}}, {{opacity:1, x:0, duration:.3, ease:"back.out(2)"}}, {t - .1:.2f});'); sfx("click-soft", t, .3)

# ---------- 6 FUTURE ----------
theme(6, "&#128200; AAS-PAAS KYA BADLEGA?", S(6), S(7))
FC_C, FC_W = fitb((CHP[0] - 150, CHP[1] - 120, CHP[0] + 150, CHP[1] + 150), 760, 1330, 1.2)
cam(S(6) - .2, FC_C, FC_W, .9)
IC = [("&#127976;", "Hotels", (-95, -80), "hotels"), ("&#127869;", "Restaurants", (95, -80), "restaurants"), ("&#127968;", "Zameen ke daam", (0, 95), "zameen")]
for i, (ic, nm, (dx, dy), w_) in enumerate(IC):
    x, y = scr((CHP[0] + dx, CHP[1] + dy), S(6) + 1)
    H.append(f'<div class="wpin" id="wp{i}" style="left:{x:.0f}px;top:{y:.0f}px"><i>{ic}</i><b>{nm}</b></div>')
    t = wt(6, w_); J.append(f'tl.fromTo("#wp{i}", {{opacity:0, scale:.2, y:30}}, {{opacity:1, scale:1, y:0, duration:.3, ease:"back.out(2.5)"}}, {t:.2f}); tl.to("#wp{i}", {{opacity:0, duration:.2}}, {S(7) - .1:.2f});'); sfx("pop", t, .25)
J.append(f'tl.fromTo("#ring", {{attr:{{r:6}}, opacity:1}}, {{attr:{{r:120}}, opacity:0, duration:1, repeat:3, immediateRender:false}}, {S(6):.2f});')
pl("lnh", (CHP[0] + 60, CHP[1] + 30), "&#8594; DELHI HIGHWAY", S(6) + .3, S(7), S(6) + 1, dy=0, cls="y")

# ---------- 7 CTA ----------
H.append('<div id="cta"><b>KAB TAK TAIYAAR HOGA?</b><div class="opts"><span>2027</span><span>2028</span><span>2030+</span></div><em>COMMENT KARO</em></div>')
J.append(f'tl.to("#dim", {{opacity:.55, duration:.3}}, {S(7):.2f}); tl.fromTo("#cta", {{opacity:0}}, {{opacity:1, duration:.2}}, {S(7):.2f}); tl.from("#cta b", {{opacity:0, scale:.6, duration:.3, ease:"back.out(2)"}}, {S(7):.2f}); tl.from("#cta .opts span", {{opacity:0, y:30, duration:.25, stagger:.15}}, {S(7) + .5:.2f}); tl.from("#cta em", {{opacity:0, scale:.5, duration:.3, ease:"back.out(2)"}}, {wt(7, "Comment"):.2f});')
sfx("sparkle", wt(7, "Comment"), .3)

# card exits: hold until the next card arrives (never blank)
CARDS.sort(key=lambda c: c[1])
for i, (cid, t0, t1) in enumerate(CARDS):
    nxt = CARDS[i + 1][1] if i + 1 < len(CARDS) else END
    out = t1 if cid == 'h1' else max(t1, min(nxt + .3, t1 + .6))
    J.append(f'tl.set("#{cid}", {{zIndex:{10 + i}}}, 0); tl.to("#{cid}", {{opacity:0, scale:.9, duration:.2, ease:"power2.in"}}, {out - .2:.2f});')

# captions
HI = ["teesra", "cricket stadium", "Jaipur", "kaam ruka", "25 km", "Chonp", "100 acre", "75 hazaar seats", "Ahmedabad", "Narendra Modi Stadium", "Melbourne Cricket Ground", "Anil Agarwal",
      "Vedanta", "300 crore", "RCA", "2022", "191 crore", "do saal", "2026", "IIT Bombay", "Delhi highway", "hotels", "restaurants", "zameen ke daam", "Comment"]
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
H.append('<div id="wm">DIGITAL BANJAARAA</div><div id="vig"></div><div id="flash"></div><div id="cred">Renders: RCA design (image supplied) &middot; Sources: The Statesman, Business Standard, Times Now, ETV Bharat &middot; Imagery: NASA Blue Marble, Sentinel-2 (EOX)</div>')
CSS = """@font-face{font-family:Anton;src:url(assets/fonts/anton.woff2)}@font-face{font-family:Mont;font-weight:700;src:url(assets/fonts/mont700.woff2)}@font-face{font-family:Mont;font-weight:800;src:url(assets/fonts/mont800.woff2)}@font-face{font-family:Mont;font-weight:900;src:url(assets/fonts/mont900.woff2)}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#07090d}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif}#world{position:absolute;inset:0;width:1080px;height:1920px}.y{color:#FFC42E}
#face{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:40}
#vig{position:absolute;inset:0;pointer-events:none;background:radial-gradient(80% 60% at 50% 45%,rgba(0,0,0,0) 50%,rgba(0,0,0,.6) 100%);z-index:2}#flash{position:absolute;inset:0;background:#fff;opacity:0;z-index:25;pointer-events:none}
#wm{position:absolute;left:0;right:0;top:190px;text-align:center;font:800 24px Mont;letter-spacing:.34em;color:rgba(255,255,255,.55);z-index:20}
#cred{position:absolute;left:40px;right:40px;top:1640px;text-align:center;font:700 17px Mont;color:rgba(255,255,255,.55);z-index:20}
#series{position:absolute;left:0;right:0;top:250px;margin:0 auto;width:max-content;padding:8px 22px;border-radius:30px;background:#FFC42E;color:#111;font:900 28px Mont;letter-spacing:.06em;opacity:0;z-index:12}
#hook{position:absolute;left:40px;right:40px;top:380px;text-align:center;opacity:0;z-index:12;padding:26px 10px;border-radius:30px;background:rgba(8,10,15,.86)}
#hook small{display:block;font:900 44px Mont;color:#fff;letter-spacing:.14em}#hook b{display:block;font:400 240px/1 Anton;color:#FFC42E}#hook span{display:block;font:400 66px/1.05 Anton;color:#fff}
#hook i{display:inline-block;margin-top:14px;padding:8px 30px;border-radius:40px;background:#FF4FA3;color:#111;font:400 64px/1.1 Anton;font-style:normal}
.th{position:absolute;left:50px;top:250px;padding:10px 24px;border-radius:40px;background:rgba(8,10,15,.9);border:2px solid #FFC42E;font:400 44px/1 Anton;color:#fff;letter-spacing:.03em;opacity:0;z-index:30}
.card{position:absolute;opacity:0;padding:14px 14px 16px;border-radius:24px;background:#fff;box-shadow:0 30px 70px rgba(0,0,0,.7);z-index:8;text-align:center}
.card img{display:block;margin:0 auto;border-radius:14px;object-fit:cover}.ct{margin-top:10px;font:400 50px/1.05 Anton;color:#14161c;letter-spacing:.02em}.cs{margin-top:6px;font:700 26px Mont;color:#5b6070}
.ci{margin:10px 6px 0;padding-top:10px;border-top:2px solid #e3e3e8;text-align:left;font:700 26px/1.32 Mont;color:#2a2d36}
.tg{position:absolute;left:-12px;top:-22px;padding:8px 20px;border-radius:30px;font:900 28px Mont;color:#111;box-shadow:0 6px 16px rgba(0,0,0,.4);z-index:2}
.pl{position:absolute;opacity:0;translate:-50% -50%;padding:8px 20px;border-radius:30px;background:rgba(8,10,15,.9);border:2px solid #FF4FA3;font:900 32px Mont;color:#fff;white-space:nowrap;z-index:6}.pl.g{border-color:#3CFF96;color:#3CFF96}.pl.y{border-color:#FFC42E;color:#FFC42E}
#facts{position:absolute;left:50px;right:50px;top:340px;opacity:0;display:flex;gap:20px;z-index:9}#facts div{flex:1;padding:16px;border-radius:24px;background:rgba(8,10,15,.9);border:3px solid #3CFF96;text-align:center}
#facts b{display:block;font:400 96px/1 Anton;color:#3CFF96}#facts span{font:900 30px Mont;color:#fff;letter-spacing:.14em}
#rank{position:absolute;left:40px;right:40px;top:350px;opacity:0;z-index:9}.rk{display:flex;gap:18px;align-items:center;margin-bottom:18px;padding:14px;border-radius:24px;background:rgba(8,10,15,.92);border:3px solid #555}
.rk.hot{border-color:#FFC42E;box-shadow:0 0 40px rgba(255,196,46,.4)}.rk img{width:300px;height:190px;object-fit:cover;border-radius:16px;flex:none}.rk div{flex:1}
.rk i{display:block;font:400 56px/1 Anton;color:#FFC42E;font-style:normal}.rk b{display:block;font:400 40px/1.05 Anton;color:#fff;margin-top:4px}.rk span{display:block;margin:6px 0 10px;font:800 26px Mont;color:#ccc}
.rk u{display:block;height:16px;border-radius:8px;background:#FFC42E;text-decoration:none}
#now{position:absolute;left:50px;right:50px;top:420px;opacity:0;z-index:9}#now p{display:flex;flex-direction:column;margin-bottom:20px;padding:22px 26px;border-radius:24px;background:rgba(8,10,15,.92);border:3px solid #3CDCFF;font:800 38px/1.25 Mont;color:#fff}
#now p b{font:400 64px/1 Anton;color:#3CDCFF;margin-bottom:6px}
.wpin{position:absolute;opacity:0;translate:-50% -50%;display:flex;flex-direction:column;align-items:center;z-index:6}.wpin i{font-style:normal;font-size:96px;line-height:1;filter:drop-shadow(0 6px 10px rgba(0,0,0,.7))}
.wpin b{margin-top:4px;padding:6px 16px;border-radius:18px;background:rgba(8,10,15,.88);border:2px solid #3CFF96;font:800 30px Mont;color:#fff;white-space:nowrap}
#cta{position:absolute;left:50px;right:50px;top:420px;opacity:0;text-align:center;z-index:12}#cta b{display:block;padding:24px;border-radius:26px;background:#FFC42E;color:#111;font:400 86px/1 Anton}
.opts{display:flex;justify-content:center;gap:20px;margin-top:26px}.opts span{padding:16px 34px;border-radius:24px;background:rgba(8,10,15,.9);border:3px solid #fff;font:400 64px/1 Anton;color:#fff}
#cta em{display:inline-block;margin-top:26px;padding:14px 34px;border-radius:30px;background:#FF4FA3;color:#111;font:900 44px Mont;font-style:normal}
.cp{position:absolute;left:40px;right:130px;top:1440px;text-align:center;opacity:0;z-index:35}
.cp div{display:inline-block;font:900 60px/1.12 Mont;color:#fff;-webkit-text-stroke:7px #000;paint-order:stroke fill;text-shadow:0 6px 18px rgba(0,0,0,.8)}"""
audio = (f'<audio id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{END}" data-track-index="1" data-volume="1"></audio>' if VOICE
         else f'<audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.55" data-fade-out="1.5"></audio>')
open(f"{P}/index.html", "w").write(f"""<!doctype html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="30">
<svg id="world" viewBox="{vb(IND_C, IND_W)}" preserveAspectRatio="xMidYMid slice">{"".join(SVG)}</svg>
{"".join(H)}
{audio}
{"".join(SFX)}
</div><script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(J)}
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>""")
print("END", END, [p["s"] for p in PH])
