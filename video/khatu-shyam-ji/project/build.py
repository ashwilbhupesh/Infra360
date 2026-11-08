"""Khatu Shyam Ji reel (text-led, no voice). World units = Web-Mercator px at zoom 11, origin tile (1448, 853)."""
import math, json
P = "proj"
OX, OY = 1448 * 256, 853 * 256
def wp(lat, lon):
    n = 256 * 2 ** 11
    return ((lon + 180) / 360 * n - OX, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n - OY)
PXKM = 256 * 2 ** 11 / 360 / (111.32 * math.cos(math.radians(27.4)))

G = {k: wp(*v) for k, v in {
    "khatu": (27.3637, 75.4029), "ringas": (27.3662, 75.5676), "jaipur": (26.9155, 75.8000), "chomu": (27.1727, 75.7204),
    "kotputli": (27.7072, 76.1996), "kishangarh": (26.5886, 74.8611), "renwal": (27.1504, 75.3565), "dudu": (26.6811, 75.2321),
    "salasar": (27.7258, 74.7243), "jeen": (27.4444, 75.2002), "sikar": (27.6094, 75.1399), "renwal2": (27.15, 75.36), "shahpura": (27.3900, 75.9600),
    "behror": (27.8900, 76.2800), "delhi": (28.6139, 77.2090), "gurgaon": (28.4595, 77.0266)}.items()}
END = 66.6
S, H, H2, J, SFX = [], [], [], [], []
def pd(pts, close=False): return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + (" Z" if close else "")
def smooth(pts, n=12):
    """Catmull-Rom through pts."""
    out = []
    P_ = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = P_[i - 1], P_[i], P_[i + 1], P_[i + 2]
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(pts[-1]); return out
def vb(c, w): h = w * 1920 / 1080; return f"{c[0] - w / 2:.1f} {c[1] - h / 2:.1f} {w:.1f} {h:.1f}"
CAMS = []
def cam(t, c, w, d=1.2, ease="power2.inOut"):
    J.append(f'tl.to("#world", {{attr:{{viewBox:"{vb(c, w)}"}}, duration:{d}, ease:"{ease}"}}, {t:.2f});'); CAMS.append((t, d, c, w))
def scr(p, t):
    c, w = CAMS[0][2], CAMS[0][3]
    for t0, d, c1, w1 in CAMS:
        if t0 + d <= t + 1e-6: c, w = c1, w1
    h = w * 1920 / 1080
    return ((p[0] - (c[0] - w / 2)) / w * 1080, (p[1] - (c[1] - h / 2)) / h * 1920)
def camw(t):
    w = CAMS[0][3]
    for t0, d, c1, w1 in CAMS:
        if t0 + d <= t + 1e-6: w = w1
    return w
def halo(i, p, t, until, at=None, rpx=110):
    r = rpx * camw(at if at is not None else t) / 1080
    S.append(f'<g id="{i}" style="opacity:0"><circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{r:.1f}" fill="url(#hg)"/>'
             f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{r * .5:.1f}" style="fill:none;stroke:#fff;stroke-width:{r * .045:.2f}"/>'
             f'<circle id="{i}r" cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{r * .5:.1f}" style="fill:none;stroke:#FFD54A;stroke-width:{r * .08:.2f}"/></g>')
    rep = max(0, int((until - t) / 0.9) - 1)
    J.append(f'tl.fromTo("#{i}", {{opacity:0, scale:.3, transformOrigin:"50% 50%"}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)"}}, {t:.2f});'
             f'tl.fromTo("#{i}r", {{attr:{{r:{r * .45:.1f}}}, opacity:1}}, {{attr:{{r:{r * 1.15:.1f}}}, opacity:0, duration:.9, ease:"power1.out", repeat:{rep}}}, {t:.2f});'
             f'tl.to("#{i}", {{opacity:0, duration:.25}}, {until - .25:.2f});')
def rail(i, pts, col, w, t, until, d=.5):
    dd = pd(pts)
    S.append(f'<g id="{i}" style="opacity:0"><path d="{dd}" style="fill:none;stroke:#111;stroke-width:{w * 3.4:.1f};stroke-opacity:.55;stroke-linecap:round"/>'
             f'<path d="{dd}" style="fill:none;stroke:#fff;stroke-width:{w * 2.6:.1f};stroke-dasharray:{w * .5:.1f} {w * 1.3:.1f}"/>'
             f'<path d="{dd}" style="fill:none;stroke:{col};stroke-width:{w:.1f};stroke-linecap:round"/></g>')
    J.append(f'tl.to("#{i}", {{opacity:1, duration:{d}}}, {t:.2f}); tl.to("#{i}", {{opacity:0, duration:.3}}, {until - .3:.2f});')
def railanim(i, pts, col, w, t, d, until):
    dd = pd(pts)
    S.append(f'<mask id="m{i}" maskUnits="userSpaceOnUse" x="-9000" y="-9000" width="30000" height="30000"><path id="mp{i}" d="{dd}" pathLength="1" style="fill:none;stroke:#fff;stroke-width:{w * 8:.1f};stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/></mask>')
    S.append(f'<g id="{i}" mask="url(#m{i})"><path d="{dd}" style="fill:none;stroke:{col};stroke-width:{w * 6:.1f};stroke-opacity:.35;stroke-linecap:round"/>'
             f'<path d="{dd}" style="fill:none;stroke:#111;stroke-width:{w * 3.4:.1f};stroke-opacity:.6"/>'
             f'<path d="{dd}" style="fill:none;stroke:#fff;stroke-width:{w * 2.6:.1f};stroke-dasharray:{w * .5:.1f} {w * 1.3:.1f}"/>'
             f'<path d="{dd}" style="fill:none;stroke:{col};stroke-width:{w:.1f};stroke-linecap:round"/></g>')
    L = [0.0]
    for a_, b_ in zip(pts, pts[1:]): L.append(L[-1] + math.hypot(b_[0] - a_[0], b_[1] - a_[1]))
    N = 40; samp = []
    for k in range(N + 1):
        tgt = L[-1] * k / N; j = max(1, next((m for m in range(1, len(L)) if L[m] >= tgt), len(L) - 1))
        f = (tgt - L[j - 1]) / max(1e-6, L[j] - L[j - 1]); a_, b_ = pts[j - 1], pts[j]
        samp.append((a_[0] + (b_[0] - a_[0]) * f, a_[1] + (b_[1] - a_[1]) * f, math.degrees(math.atan2(b_[1] - a_[1], b_[0] - a_[0]))))
    tw, th = w * 9, w * 3.6
    S.append(f'<g id="tr{i}" style="opacity:0" transform="translate({samp[0][0]:.1f},{samp[0][1]:.1f}) rotate({samp[0][2]:.1f})">'
             f'<circle r="{tw * .9:.1f}" fill="url(#hg)"/><rect x="{-tw / 2:.1f}" y="{-th / 2:.1f}" width="{tw:.1f}" height="{th:.1f}" rx="{th / 2:.1f}" style="fill:{col};stroke:#fff;stroke-width:{w * .5:.1f}"/>'
             f'<rect x="{tw * .18:.1f}" y="{-th * .28:.1f}" width="{tw * .2:.1f}" height="{th * .56:.1f}" rx="{th * .1:.1f}" style="fill:#fff"/></g>')
    J.append(f'tl.to("#mp{i}", {{strokeDashoffset:0, duration:{d}, ease:"none"}}, {t:.2f}); tl.to("#tr{i}", {{opacity:1, duration:.15}}, {t:.2f});')
    for k in range(1, N + 1):
        x, y, ang = samp[k]
        J.append(f'tl.to("#tr{i}", {{attr:{{transform:"translate({x:.1f},{y:.1f}) rotate({ang:.1f})"}}, duration:{d / N:.4f}, ease:"none"}}, {t + d * (k - 1) / N:.4f});')
    J.append(f'tl.to(["#{i}", "#tr{i}"], {{opacity:0, duration:.3}}, {until - .3:.2f});')
def sfx(name, t, vol=0.5):
    SFX.append(f'<audio class="clip" src="assets/sfx/{name}.mp3" data-start="{t:.2f}" data-duration="2" data-track-index="{20 + len(SFX)}" data-volume="{vol}"></audio>')
def inout(sel, t, until, frm="opacity:0, y:30, scale:.94", to="opacity:1, y:0, scale:1", d=.3, ease="back.out(2)", out="opacity:0, duration:.2"):
    J.append(f'tl.fromTo("{sel}", {{{frm}}}, {{{to}, duration:{d}, ease:"{ease}"}}, {t:.2f}); tl.to("{sel}", {{{out}}}, {until - .2:.2f});')
def story(i, html, t, until, top=1330):
    H2.append(f'<div class="st" id="{i}" style="top:{top}px"><div>{html}</div></div>'); inout(f"#{i}", t, until)
def chip(i, kick, text, t, until, y=230):
    H2.append(f'<div class="chip" id="{i}" style="top:{y}px"><b>{kick}</b>{text}</div>')
    inout(f"#{i}", t, until, frm="opacity:0, x:-50", to="opacity:1, x:0", d=.35, ease="power3.out")
def photo(i, src, cap, credit, t, until, x=60, y=420, w=960, h=760, fit="cover", rot=0, pos="50% 50%"):
    H2.append(f'<div class="ph" id="{i}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px"><img src="assets/img/{src}" style="object-fit:{fit};object-position:{pos}"/>'
              + (f'<div class="pc">{cap}<em>{credit}</em></div>' if cap or credit else '') + '</div>')
    J.append(f'tl.fromTo("#{i}", {{opacity:0, scale:.7, rotation:{rot - 3}}}, {{opacity:1, scale:1, rotation:{rot}, duration:.4, ease:"back.out(1.6)"}}, {t:.2f}); tl.to("#{i}", {{opacity:0, scale:.94, duration:.25}}, {until - .25:.2f});')
    sfx("pop", t, 0.3)
def label(i, p, text, t, until, at=None, cls="", dx=0, dy=0):
    x, y = scr(p, at if at is not None else t)
    H.append(f'<div class="lab {cls}" id="{i}" style="left:{x + dx:.0f}px;top:{y + dy:.0f}px">{text}</div>')
    inout(f"#{i}", t, until, frm="opacity:0, scale:.6", to="opacity:1, scale:1", d=.3)
def line(i, pts, color, width, t, d, until=None, dash=None, glow=True, op=1):
    dd = pd(pts)
    if glow: S.append(f'<path id="{i}g" d="{dd}" pathLength="1" style="fill:none;stroke:{color};stroke-width:{width * 3.2:.1f};stroke-opacity:.35;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1"/>')
    S.append(f'<path id="{i}" d="{dd}" pathLength="1" style="fill:none;stroke:{color};stroke-width:{width};stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1;opacity:{op}"/>')
    sel = f'["#{i}","#{i}g"]' if glow else f'"#{i}"'
    J.append(f'tl.to({sel}, {{strokeDashoffset:0, duration:{d}, ease:"power2.inOut"}}, {t:.2f});')
    if until: J.append(f'tl.to({sel}, {{opacity:0, duration:.4}}, {until:.2f});')
def dot(i, p, r, t, until, col="#FFD54A"):
    S.append(f'<circle id="{i}" cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{r}" style="fill:{col};stroke:#fff;stroke-width:{r / 3:.1f};opacity:0"/>')
    J.append(f'tl.to("#{i}", {{opacity:1, duration:.2}}, {t:.2f}); tl.to("#{i}", {{opacity:0, duration:.3}}, {until:.2f});')
Y = '<span class="y">'; E = '</span>'

# ---------- world ----------
S.append('<defs><radialGradient id="hg"><stop offset="0" stop-color="#FFD54A" stop-opacity=".7"/><stop offset=".5" stop-color="#FFD54A" stop-opacity=".3"/><stop offset="1" stop-color="#FFD54A" stop-opacity="0"/></radialGradient></defs>')
S.append('<rect x="-3000" y="-3000" width="11000" height="11000" style="fill:#0d1014"/>')
S.append('<image href="assets/img/s2_k11.jpg" x="0" y="0" width="4352" height="5120" preserveAspectRatio="none"/>')
S.append('<image id="hi" href="assets/img/s2_k13.jpg" x="1088" y="2048" width="576" height="512" preserveAspectRatio="none" style="opacity:0"/>')
S.append('<rect id="dim" x="-3000" y="-3000" width="11000" height="11000" style="fill:#000;opacity:.3"/>')
LINES_AT = len(S)

# ---------- 0 · HOOK (0–3.4) ----------
H2.append('<div id="hookbg" class="full"><img src="assets/img/shringar.jpg" style="object-position:50% 40%"/><div class="shade"></div></div>')
J.append('tl.fromTo("#hookbg img", {scale:1.25}, {scale:1.04, duration:3.6, ease:"power1.out"}, 0); tl.set("#hookbg", {opacity:1}, 0); tl.to("#hookbg", {opacity:0, duration:.2}, 3.3);')
H2.append('<div id="save"><span>🔖 SAVE</span><span>➤ SHARE</span></div>')
J.append('tl.fromTo("#save", {opacity:0, y:-20}, {opacity:1, y:0, duration:.3}, 0.05); tl.to("#save", {opacity:0, duration:.3}, 3.2);')
H2.append('<div id="hook"><b>KHATU SHYAM JI<br/>JAATE HO?</b></div>')
J.append('tl.fromTo("#hook", {opacity:0, scale:1.25}, {opacity:1, scale:1, duration:.3, ease:"back.out(2.2)"}, 0.02); tl.to("#hook", {opacity:0, duration:.2}, 3.2);')
story("s0", f"Agle 5 saal mein yeh jagah<br/>{Y}pehchaan nahi paoge{E}", 1.1, 3.4)
sfx("impact-bass-1", 0.02, 0.55); sfx("whoosh-short", 1.05, 0.35)
H2.append('<div class="tagimg" id="t0">Image supplied</div>'); inout("#t0", 0.3, 3.3, frm="opacity:0", to="opacity:1")

# ---------- 1 · SCALE (3.4–7.6) ----------
H2.append('<div id="crowdbg" class="full"><img src="assets/img/nishan.jpg"/><div class="shade"></div></div>')
J.append('tl.set("#crowdbg", {opacity:0}, 0); tl.to("#crowdbg", {opacity:1, duration:.15}, 3.3); tl.fromTo("#crowdbg img", {scale:1.05}, {scale:1.22, duration:4.4, ease:"none"}, 3.3); tl.to("#crowdbg", {opacity:0, duration:.3}, 7.45);')
H2.append('<div id="count"><small>HAR SAAL</small><span>LAKHON BHAKT</span><em>Sirf Lakkhi mele mein ~50 lakh</em></div>')
inout("#count", 3.45, 7.6, frm="opacity:0, scale:.6", to="opacity:1, scale:1")

story("s1", f"Aur ab yahan pahunchna hoga<br/>{Y}aur bhi aasaan{E}", 4.9, 7.6)
H2.append('<div class="tagimg" id="t1">~50 lakh during Lakkhi mela · Rajasthan Tourism via ThePrint · Image supplied</div>'); inout("#t1", 3.6, 7.5, frm="opacity:0", to="opacity:1")
sfx("riser", 3.4, 0.25); sfx("ping", 5.1, 0.35)

# ---------- 2 · MAP: Delhi & Jaipur (7.6–12.4) ----------
WIDE_C, WIDE_W = (wp(27.45, 75.92)[0] - 230, 2562), 1900
J.append(f'tl.set("#world", {{attr:{{viewBox:"{vb(WIDE_C, WIDE_W * 1.25)}"}}}}, 0);')
CAMS.append((0, 0, WIDE_C, WIDE_W * 1.25))
cam(7.5, WIDE_C, WIDE_W, 1.6, "power2.out")
DEL = smooth([G["delhi"], G["gurgaon"], G["behror"], G["kotputli"], G["shahpura"], G["chomu"], G["ringas"], G["khatu"]], 10)
line("rdel", DEL, "#FF5A36", 9, 7.8, 1.9, until=12.3)
JAI = smooth([G["jaipur"], G["chomu"], G["ringas"], G["khatu"]], 10)
line("rjai", JAI, "#4FC3F7", 9, 9.6, 1.1, until=12.3)
S.append(f'<circle id="kpin" cx="{G["khatu"][0]:.1f}" cy="{G["khatu"][1]:.1f}" r="16" style="fill:#FFD54A;stroke:#fff;stroke-width:6;opacity:0"/>')
S.append(f'<circle id="kring" cx="{G["khatu"][0]:.1f}" cy="{G["khatu"][1]:.1f}" r="16" style="fill:none;stroke:#FFD54A;stroke-width:6;opacity:0"/>')
J.append('tl.to("#kpin", {opacity:1, duration:.2}, 7.7); tl.fromTo("#kring", {attr:{r:16}, opacity:1}, {attr:{r:70}, opacity:0, duration:1, repeat:3}, 7.8);')
label("lk", G["khatu"], "🚩 KHATU SHYAM JI", 7.8, 12.4, at=9.2, cls="hot", dy=-70)
label("ldel", G["kotputli"], "DELHI ↗<br/><span class='y'>~300 km</span>", 8.6, 12.4, at=9.2, cls="big", dx=40, dy=-260)
label("ljai", G["jaipur"], "JAIPUR<br/><span class='c'>~80 km</span>", 10.0, 12.4, at=10.0, cls="big", dx=-190)
halo("hk1", G["khatu"], 7.8, 12.4, at=9.2); halo("hj1", G["jaipur"], 10.0, 12.4, at=10.0)
dot("djai", G["jaipur"], 12, 9.6, 12.3, "#4FC3F7")
story("s2", f"Delhi ho ya Jaipur —<br/>{Y}seedhi connectivity aa rahi hai{E}", 8.3, 12.4)
sfx("whoosh", 7.5, 0.35); sfx("click-soft", 10.0, 0.3)

# ---------- 3 · CM clipping (12.4–15.0) ----------
photo("pcm", "clip_cm.jpg", "", "", 12.4, 15.0, x=60, y=560, w=960, h=305, fit="cover")
H2.append('<div class="cred" id="ccm" style="top:880px">Bhaskar English · image supplied</div>'); inout("#ccm", 12.5, 15.0, frm="opacity:0", to="opacity:1")
story("s3", f"Aur ab yahan aa rahe hain<br/>{Y}4 bade projects{E}", 12.5, 15.0)
J.append('tl.to("#dim", {opacity:.65, duration:.4}, 12.3); tl.to("#dim", {opacity:.3, duration:.4}, 14.9);')
sfx("impact-bass-1", 12.4, 0.4)

# counter badge 1-2-3-4
H2.append('<div id="badge">' + "".join(f'<i id="bn{k}" style="opacity:{1 if k == 1 else 0}">{k}</i>' for k in range(1, 5)) + '<span>/4</span></div>')
J.append('tl.fromTo("#badge", {opacity:0, scale:.5}, {opacity:1, scale:1, duration:.3, ease:"back.out(2)"}, 15.0); tl.to("#badge", {opacity:0, duration:.3}, 33.3);')
for k, t in [(2, 19.6), (3, 23.6), (4, 27.6)]:
    J.append(f'tl.set("#bn{k - 1}", {{opacity:0}}, {t:.2f}); tl.set("#bn{k}", {{opacity:1}}, {t:.2f}); tl.fromTo("#badge", {{scale:1.35}}, {{scale:1, duration:.35, ease:"back.out(3)", immediateRender:false}}, {t:.2f});')

# ---------- 4 · ① expressway (15.0–19.6) ----------
REG_C = (1455, 2668); cam(15.0, REG_C, 2500, 1.2)
EXP = smooth([G["kotputli"], wp(27.52, 75.86), wp(27.40, 75.50), G["renwal"], wp(26.85, 75.24), G["dudu"], G["kishangarh"]], 12)
line("rexp", EXP, "#FF8A00", 14, 15.5, 2.0, until=19.5)
for n, k in [("dko", "kotputli"), ("dki", "kishangarh")]: dot(n, G[k], 16, 15.4, 19.5, "#FF8A00")
J.append('tl.to("#kpin", {attr:{r:24}, duration:.3}, 15.0);')
label("lkot", G["kotputli"], "KOTPUTLI", 15.6, 19.6, at=16.3, dy=60, dx=-40)
label("lkis", G["kishangarh"], "KISHANGARH", 16.8, 19.6, at=16.3, dy=-60, dx=60)
label("lk2", G["khatu"], "🚩 KHATU SHYAM JI", 15.4, 19.6, at=16.3, cls="hot", dy=-60, dx=-60)
halo("hko", G["kotputli"], 15.6, 19.6, at=16.3); halo("hki", G["kishangarh"], 16.8, 19.6, at=16.3); halo("hk2", G["khatu"], 15.4, 19.6, at=16.3)
chip("c1", "① GREENFIELD EXPRESSWAY", f"Kotputli → Kishangarh<br/>{Y}Delhi side se seedha, tez safar{E}", 15.1, 19.6)
story("s4", f"Khatu area se hokar —<br/>{Y}naye investment zones{E}", 15.8, 19.6)
H2.append('<div class="cred" id="cexp" style="top:420px">Route indicative · not exact alignment</div>'); inout("#cexp", 15.6, 19.6, frm="opacity:0", to="opacity:1")
sfx("whoosh-short", 15.0, 0.35); sfx("riser", 15.4, 0.2)

# ---------- 5 · ② NH-52 (19.6–23.6) ----------
NH_C = (1640, 2700); cam(19.6, NH_C, 1050, 1.2)
J.append('tl.to("#kpin", {attr:{r:9}, duration:.3}, 19.6);')
NH = smooth([G["jaipur"], G["chomu"], G["ringas"]], 14)
line("rnh", NH, "#4FC3F7", 7, 20.0, 1.2)
J.append('tl.to(["#rnh","#rnhg"], {strokeWidth:"+=10", duration:.6, ease:"power2.out"}, 21.4); tl.to(["#rnh","#rnhg"], {opacity:0, duration:.4}, 23.5);')
for n, k in [("dj2", "jaipur"), ("dch", "chomu"), ("dri", "ringas")]: dot(n, G[k], 9, 20.0, 23.5, "#4FC3F7")
label("lj2", G["jaipur"], "JAIPUR", 20.0, 23.6, at=20.9, dy=50)
label("lch", G["chomu"], "CHOMU", 20.5, 23.6, at=20.9, dx=-120)
label("lri", G["ringas"], "RINGAS", 21.0, 23.6, at=20.9, dx=150)
halo("hj2", G["jaipur"], 20.0, 23.6, at=20.9); halo("hch", G["chomu"], 20.5, 23.6, at=20.9); halo("hri", G["ringas"], 21.0, 23.6, at=20.9)
label("l46", wp(27.10, 75.73), f"4 → {Y}6 LANE{E}", 21.4, 23.6, at=20.9, cls="big", dx=200)
chip("c2", "② NH-52 WIDENING", f"Jaipur → Ringas {Y}6-lane{E}<br/><small>Jaipur se Khatu — kam traffic, kam time</small>", 19.7, 23.6)
sfx("whoosh-short", 19.6, 0.35); sfx("click-soft", 21.4, 0.35)

# ---------- 6 · ③ ring road (23.6–27.6) ----------
K_C = G["khatu"]; cam(23.6, (K_C[0] + 10, K_C[1] + 10), 300, 1.3)
J.append('tl.to("#hi", {opacity:1, duration:.6}, 23.9); tl.to("#kpin", {attr:{r:7}, duration:.4}, 23.6);')
RR = [(K_C[0] + 4.2 * PXKM * math.cos(a) * (1 + .12 * math.sin(3 * a)), K_C[1] + 3.4 * PXKM * math.sin(a) * (1 + .1 * math.cos(2 * a))) for a in [i / 60 * 2 * math.pi for i in range(61)]]
line("rring", RR, "#FFD54A", 4, 24.4, 1.6, until=27.5)
label("lk3", G["khatu"], "KHATU", 24.0, 27.6, at=25.0, cls="hot sm", dy=-45)
halo("hk3", G["khatu"], 24.0, 27.6, at=25.0, rpx=130)
label("lring", (K_C[0], K_C[1] + 3.6 * PXKM), "RING ROAD", 25.2, 27.6, at=25.0, cls="", dy=40)
chip("c3", "③ KHATU RING ROAD", f"Mele ka {Y}jam khatam{E}", 23.7, 27.6)
story("s6", f"Mele mein bhi {Y}aasaan darshan{E}", 24.3, 27.6)
H2.append('<div class="cred" id="crr" style="top:1270px">Ring shown indicative · final alignment awaited</div>'); inout("#crr", 24.4, 27.6, frm="opacity:0", to="opacity:1")
sfx("whoosh", 23.6, 0.3); sfx("sparkle", 24.4, 0.3)

# ---------- 7 · ④ rail (27.6–33.4) ----------
RA_C = wp(27.372, 75.485); cam(27.6, RA_C, 430, 1.1)
RL = smooth([G["ringas"], wp(27.372, 75.52), wp(27.369, 75.45), G["khatu"]], 12)
RX = smooth([G["jaipur"], G["chomu"], G["ringas"], G["sikar"]], 10)
rail("rx1", RX, "#9aa4b2", 3, 27.6, 30.6)
railanim("rn1", RL, "#FF2D95", 3.2, 28.0, 2.3, 30.6)
dot("dri2", G["ringas"], 6, 27.8, 30.5, "#FF2D95"); dot("dkh2", G["khatu"], 6, 27.8, 30.5, "#FF2D95")
label("lri2", G["ringas"], "RINGAS", 27.9, 30.6, at=28.7, dy=-45)
label("lkh4", G["khatu"], "KHATU", 27.9, 30.6, at=28.7, cls="hot sm", dy=-45)
halo("hri2", G["ringas"], 27.9, 30.5, at=28.7); halo("hk4", G["khatu"], 29.9, 30.5, at=28.7, rpx=140)
label("lrx", wp(27.43, 75.50), "Existing rail · Jaipur–Sikar", 28.0, 30.6, at=28.7, cls="sm", dy=-40)
label("lkm", wp(27.369, 75.485), f"{Y}PROPOSED RAIL LINE{E}", 28.6, 30.6, at=28.7, cls="big", dy=70)
chip("c4", "④ RINGAS–KHATU RAIL LINE", f"{Y}Train se seedha Khatu{E}<br/><small>Ringas–Khatu line sanctioned</small>", 27.7, 33.4)
photo("paaj", "aajtak_map.jpg", "Proposed rail alignment near Khatu", "Aaj Tak · image supplied", 30.5, 32.0, x=60, y=470, w=960, h=640)
photo("psun", "sundarpura.jpg", "", "", 31.9, 33.4, x=60, y=430, w=470, h=740)
H2.append('<div class="tagc" id="tsun" style="left:60px;top:1185px;width:470px">Concept image · not official design</div>'); inout("#tsun", 32.0, 33.4, frm="opacity:0", to="opacity:1")
photo("pie", "clip_ie.jpg", "", "", 32.1, 33.4, x=550, y=520, w=470, h=326, fit="cover", pos="50% 0%", rot=2)
H2.append('<div class="tagc" id="tie" style="left:550px;top:860px;width:470px">The Indian Express · image supplied</div>'); inout("#tie", 32.2, 33.4, frm="opacity:0", to="opacity:1")
story("s7", f"Naya {Y}Sundarpura station{E} — construction<br/>next year (Indian Express)", 30.6, 33.4)
J.append('tl.to("#dim", {opacity:.6, duration:.4}, 30.4);')
sfx("whoosh-short", 27.6, 0.35); sfx("riser", 28.0, 0.25)

# ---------- 8 · heritage (33.4–38.0) ----------
H2.append('<div id="herbg" class="full"><img src="assets/img/entrance.jpg"/><div class="shade"></div></div>')
J.append('tl.set("#herbg", {opacity:0}, 0); tl.to("#herbg", {opacity:1, duration:.25}, 33.3); tl.fromTo("#herbg img", {scale:1.02}, {scale:1.15, duration:4.8, ease:"none"}, 33.3); tl.to("#herbg", {opacity:0, duration:.3}, 37.9);')
H2.append('<div id="crore"><small>MANDIR KA KAYAKALP</small><span>HERITAGE LOOK</span><em>₹87.87 Cr · Swadesh Darshan 2.0</em></div>')
inout("#crore", 33.5, 38.0, frm="opacity:0, scale:.6", to="opacity:1, scale:1")

photo("psd", "clip_sd.jpg", "", "", 35.0, 38.0, x=60, y=840, w=960, h=296, fit="cover")
H2.append('<div class="cred" id="csd" style="top:1150px">Bhaskar English · image supplied</div>'); inout("#csd", 35.1, 38.0, frm="opacity:0", to="opacity:1")
story("s8", f"Behtar darshan → zyada bhakt<br/>→ {Y}zyada demand{E}", 35.6, 38.0)
sfx("impact-bass-1", 33.4, 0.4); sfx("sparkle", 34.7, 0.3)

# ---------- 9 · hub (38.0–43.6) ----------
H2.append('<div id="hotbg" class="full"><img src="assets/img/hotel.jpg" style="object-position:48% 50%"/><div class="shade"></div></div>')
J.append('tl.set("#hotbg", {opacity:0}, 0); tl.to("#hotbg", {opacity:1, duration:.25}, 37.9); tl.fromTo("#hotbg img", {scale:1.2}, {scale:1.05, duration:5.8, ease:"power1.out"}, 37.9); tl.to("#hotbg", {opacity:0, duration:.3}, 43.5);')
story("s9a", f"Lakhon log aate hain —<br/>par {Y}rukne ki jagah kitni hai?{E}", 38.1, 40.4)
TILES = [("🏨", "HOTELS"), ("🛕", "DHARAMSHALA"), ("🏡", "HOMESTAYS"), ("🍛", "RESTAURANTS")]
H2.append('<div id="tiles">' + "".join(f'<div class="tile" id="tl{i}"><i>{a}</i><b>{b}</b><u>kam pad jaate hain</u></div>' for i, (a, b) in enumerate(TILES)) + '</div>')
for i in range(4):
    J.append(f'tl.fromTo("#tl{i}", {{opacity:0, scale:.5}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, {38.5 + .3 * i:.2f});'); sfx("pop", 38.5 + .3 * i, .28)
J.append('tl.to("#tiles", {opacity:0, duration:.25}, 40.6);')
H2.append(f'<div id="hub"><small>KHATU SHYAM JI BAN RAHA HAI</small><b>PILGRIMAGE<br/>TOURISM<br/>HOTELS<br/>HOUSING</b><em>ka agla {Y}HUB{E}</em></div>')
J.append('tl.fromTo("#hub", {opacity:0}, {opacity:1, duration:.2}, 40.7); tl.from("#hub b", {opacity:0, y:40, duration:.5, ease:"power3.out"}, 40.75); tl.from("#hub em", {opacity:0, scale:.6, duration:.4, ease:"back.out(2)"}, 41.5); tl.to("#hub", {opacity:0, duration:.25}, 43.4);')
H2.append('<div class="tagimg" id="t9">Hotel in Khatu · image supplied</div>'); inout("#t9", 38.1, 43.5, frm="opacity:0", to="opacity:1")
sfx("whoosh", 37.9, 0.3); sfx("impact-bass-1", 40.7, 0.4)

# ---------- 10 · temple triangle (43.6–48.6) ----------
J.append('tl.to("#hi", {opacity:0, duration:.1}, 43.0); tl.to("#dim", {opacity:.35, duration:.1}, 43.0);')
TR_C = (775, 2075); J.append(f'tl.set("#world", {{attr:{{viewBox:"{vb(TR_C, 1900)}"}}}}, 43.4);'); CAMS.append((43.4, 0, TR_C, 1900))
cam(43.6, TR_C, 1300, 1.4, "power2.out")
TRI = [G["khatu"], G["salasar"], G["jeen"], G["khatu"]]
line("rtri", TRI, "#FFD54A", 7, 44.2, 1.6)
J.append('tl.to("#kpin", {attr:{r:14}, duration:.2}, 43.5);')
for n, k in [("dsa", "salasar"), ("dje", "jeen")]: dot(n, G[k], 14, 44.0, 48.5, "#FFD54A")
for i, (n, k) in enumerate([("hkt", "khatu"), ("hsa", "salasar"), ("hje", "jeen")]): halo(n, G[k], 44.3 + .55 * i, 48.4, at=45.1, rpx=120)
H.append('<div id="tri">')
for nid, img, name, x, y in [("vk", "shringar.jpg", "KHATU SHYAM JI", 800, 860), ("vs", "salasar.jpg", "SALASAR BALAJI", 170, 420), ("vj", "jeen.jpg", "JEEN MATA", 460, 740)]:
    H.append(f'<div class="tv" id="{nid}" style="left:{x}px;top:{y}px"><img src="assets/img/{img}"/><b>{name}</b></div>')
H.append('</div>')
for i, nid in enumerate(["vk", "vs", "vj"]):
    J.append(f'tl.fromTo("#{nid}", {{opacity:0, scale:.4}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)"}}, {44.3 + .55 * i:.2f}); tl.to("#{nid}", {{opacity:0, duration:.25}}, 48.4);'); sfx("pop", 44.3 + .55 * i, .3)
chip("c10", "RAJASTHAN KA", f"{Y}TEMPLE TRIANGLE{E}", 43.7, 48.6)
story("s10", f"Sirf Khatu nahi — {Y}Salasar Balaji{E}<br/>+ {Y}Jeen Mata{E} = poora circuit", 45.6, 48.6)
H2.append('<div class="tagimg" id="t10">Temple images supplied</div>'); inout("#t10", 44.3, 48.5, frm="opacity:0", to="opacity:1")
sfx("whoosh", 43.5, 0.3)

# ---------- 10b · OPPORTUNITIES across the region (48.6–59.6) ----------
J.append('tl.to(["#rtri","#rtrig"], {opacity:0, duration:.3}, 48.5); tl.to("#dim", {opacity:.4, duration:.3}, 48.5); tl.to("#kpin", {opacity:0, duration:.2}, 48.5);')
OV_C, OV_W = (1355, 2560), 2650
cam(48.6, OV_C, OV_W, 1.3)
J.append('tl.to("#credit", {opacity:0, duration:.2}, 48.6); tl.to("#credit", {opacity:1, duration:.2}, 59.6);')
line("oexp", EXP, "#FF8A00", 16, 48.9, 1.2, until=59.4)
line("onh", NH, "#4FC3F7", 14, 49.2, .9, until=59.4)
rail("orx", RX, "#cfd6df", 9, 49.4, 59.6)
railanim("orn", RL, "#FF2D95", 9, 49.6, 1.6, 59.6)
H2.append('<div id="legend"><span><i style="background:#FF8A00"></i>Expressway</span><span><i style="background:#4FC3F7"></i>6-lane NH-52</span><span><i class="rl" style="background:#9aa4b2"></i>Rail</span><span><i class="rl" style="background:#FF2D95"></i>New rail</span></div>')
inout("#legend", 49.3, 59.6, frm="opacity:0", to="opacity:1")
chip("c11", "POORA REGION BADAL RAHA HAI", f"Jahan connectivity, {Y}wahan growth{E}", 48.7, 59.6)
OPP = [("khatu", "KHATU SHYAM JI", "Hotels · Dharamshala · Homestays", 0, -150),
       ("ringas", "RINGAS", "Rail junction + 6-lane<br/>Shops · Stays · Commercial", 120, 150),
       ("chomu", "CHOMU", "6-lane corridor<br/>Housing near Jaipur", 60, 150),
       ("renwal", "RENWAL · EXPRESSWAY BELT", "Warehousing · Logistics<br/>near interchanges", -40, 150),
       ("kishangarh", "KISHANGARH", "Marble hub + airport<br/>Logistics · Industry", 230, -40),
       ("kotputli", "KOTPUTLI", "NH-48 junction<br/>Logistics · Highway shops", -150, 160),
       ("salasar", "SALASAR · JEEN MATA", "Pilgrim stays · Food · Travel", 200, 150)]
T0, STEP = 50.0, 1.35
for i, (k, nm, txt, dx, dy) in enumerate(OPP):
    t = T0 + STEP * i; nxt = t + STEP + .05
    halo(f"ho{i}", G[k], t, nxt, at=t, rpx=150)
    if k == "salasar": halo("ho7", G["jeen"], t, nxt, at=t, rpx=150)
    x, y = scr(G[k], t); x = min(max(x + dx, 280), 800); y = y + dy
    H.append(f'<div class="opp" id="op{i}" style="left:{x:.0f}px;top:{y:.0f}px"><b>{nm}</b>{txt}</div>')
    inout(f"#op{i}", t + .05, nxt, frm="opacity:0, scale:.6", to="opacity:1, scale:1", d=.3)
    sx, sy = scr(G[k], t)
    odx = {"khatu": -80, "ringas": 60}.get(k, 0)
    if nxt < 59.0:
        H.append(f'<div class="oname" id="on{i}" style="left:{sx + odx:.0f}px;top:{sy + 40:.0f}px">{nm.split(" ·")[0]}</div>')
        inout(f"#on{i}", nxt - .05, 59.5, frm="opacity:0", to="opacity:1", d=.2)
    sfx("pop", t, .3)
H2.append('<div class="cred" id="copp" style="top:470px">Possibilities, not guaranteed returns · lines indicative</div>'); inout("#copp", 49.5, 59.6, frm="opacity:0", to="opacity:1")
sfx("whoosh", 48.6, 0.3); sfx("riser", 57.0, 0.2)

# ---------- 11 · smart check (59.6–62.6) ----------
J.append('tl.to("#dim", {opacity:.8, duration:.4}, 59.5);')
H2.append(f'<div id="chk"><small>PLOT LENE SE PEHLE CHECK KARO</small>'
          f'<p id="k1">✓ Expressway {Y}interchange{E} kitni door hai</p><p id="k2">✓ Layout ka {Y}approval{E}</p><p id="k3">✓ {Y}Patta{E} &amp; land conversion</p></div>')
J.append('tl.fromTo("#chk", {opacity:0, y:30}, {opacity:1, y:0, duration:.3}, 59.6); tl.to("#chk", {opacity:0, duration:.25}, 62.5);')
for i in range(3): J.append(f'tl.from("#k{i + 1}", {{opacity:0, x:-60, duration:.3, ease:"power3.out"}}, {59.9 + .45 * i:.2f});'); sfx("click-soft", 59.9 + .45 * i, .35)

# ---------- 12 · CTA (62.6–END) ----------
H2.append('<div id="ctabg" class="full"><img src="assets/img/shringar.jpg" style="object-position:50% 38%"/><div class="shade"></div></div>')
J.append(f'tl.set("#ctabg", {{opacity:0}}, 0); tl.to("#ctabg", {{opacity:1, duration:.3}}, 62.5); tl.fromTo("#ctabg img", {{scale:1.0}}, {{scale:1.12, duration:{END - 62.5:.1f}, ease:"none"}}, 62.5);')
H2.append(f'<div id="cta"><small>Aap kitni baar Khatu gaye ho?</small><b>Comment karo<br/>{Y}JAI SHREE SHYAM{E} 🙏</b></div>')
J.append('tl.fromTo("#cta", {opacity:0, scale:.8}, {opacity:1, scale:1, duration:.4, ease:"back.out(2)"}, 62.7); tl.fromTo("#cta b", {scale:1}, {scale:1.05, duration:.5, yoyo:true, repeat:5}, 63.3);')
H2.append('<div id="share"><svg viewBox="0 0 24 24" width="76" height="76"><path d="M3 11l18-8-8 18-2-8z" style="fill:none;stroke:#fff;stroke-width:2;stroke-linejoin:round"/></svg><span>Bhejo usko jo har Ekadashi<br/>Khatu jaata hai</span></div>')
J.append('tl.fromTo("#share", {opacity:0, y:30}, {opacity:1, y:0, duration:.35, ease:"back.out(2)"}, 63.6); tl.fromTo("#share svg", {scale:1}, {scale:1.15, duration:.45, yoyo:true, repeat:5}, 64.0);')
sfx("sparkle", 62.7, 0.35); sfx("impact-bass-1", 62.6, 0.35)

H2.append('<div id="brand">ASHWILLPOWER · JAIPUR REAL ESTATE</div>')
H.append('<div id="credit">Satellite: Sentinel-2 cloudless 2016 by EOX (CC BY 4.0) · routes indicative</div>')

CSS = """*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#0d1014}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Inter,Arial,sans-serif}
#maplayer{position:absolute;inset:0}#world{position:absolute;inset:0;width:1080px;height:1920px}
.y{color:#FFD54A}.c{color:#4FC3F7}
.full{position:absolute;inset:0;opacity:0;overflow:hidden}.full img{width:100%;height:100%;object-fit:cover;display:block}
.full .shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.55) 0%,rgba(0,0,0,.05) 30%,rgba(0,0,0,.1) 55%,rgba(0,0,0,.75) 100%)}
#save{position:absolute;left:0;right:0;top:150px;display:flex;justify-content:center;gap:18px;opacity:0}
#save span{padding:10px 24px;border-radius:40px;background:rgba(0,0,0,.6);border:2px solid rgba(255,255,255,.7);font:800 30px Inter,sans-serif;color:#fff;letter-spacing:.06em}
#hook{position:absolute;left:30px;right:30px;top:250px;text-align:center;opacity:0}
#hook b{display:inline-block;padding:20px 30px;border-radius:26px;background:rgba(0,0,0,.62);font-weight:900;font-size:108px;line-height:1;color:#fff;text-shadow:0 4px 0 #000}
.st{position:absolute;left:40px;right:40px;text-align:center;opacity:0}
.st div{display:inline-block;padding:18px 28px;border-radius:24px;background:rgba(8,10,14,.78);font:900 56px/1.14 Inter,Arial,sans-serif;color:#fff}
.chip{position:absolute;left:50px;right:50px;opacity:0;padding:20px 28px;border-radius:22px;background:rgba(8,10,14,.86);border-left:12px solid #FFD54A;font:900 48px/1.12 Inter,Arial,sans-serif;color:#fff}
.chip small{display:block;font:700 30px Inter,sans-serif;color:#ccc;margin-top:6px}.chip b{display:block;font:800 28px "JetBrains Mono",monospace;letter-spacing:.12em;color:#FFD54A;margin-bottom:8px}
.ph{position:absolute;opacity:0;border-radius:22px;overflow:hidden;border:5px solid #FFD54A;box-shadow:0 18px 50px rgba(0,0,0,.7);background:#fff}
.ph img{width:100%;height:100%;display:block}.pc{position:absolute;left:0;right:0;bottom:0;padding:40px 20px 12px;background:linear-gradient(180deg,transparent,rgba(0,0,0,.9));font:900 42px Inter,Arial,sans-serif;color:#fff}
.pc em{display:block;font-style:normal;font-weight:600;font-size:22px;color:#ddd;margin-top:4px}
.lab{position:absolute;opacity:0;translate:-50% -50%;padding:8px 18px;border-radius:14px;background:rgba(8,10,14,.8);font:900 36px/1.08 Inter,Arial,sans-serif;color:#fff;text-align:center;white-space:nowrap}
.lab.big{font-size:52px}.lab.hot{background:#FFD54A;color:#111;font-size:40px}.lab.hot.sm{font-size:32px}.lab.sm{font-size:30px}
#count{position:absolute;left:40px;right:40px;top:300px;text-align:center;opacity:0;padding:26px 0 30px;border-radius:30px;background:rgba(8,10,14,.72)}
#count small{display:block;font:800 34px "JetBrains Mono",monospace;letter-spacing:.14em;color:#fff}
#count span{display:block;font-weight:900;font-size:112px;line-height:1.05;color:#FFD54A}#count em{display:block;font-style:normal;font:800 40px Inter,sans-serif;color:#fff}
#crore{position:absolute;left:40px;right:40px;top:300px;text-align:center;opacity:0;padding:26px 0 30px;border-radius:30px;background:rgba(8,10,14,.75)}
#crore small{display:block;font:800 34px "JetBrains Mono",monospace;letter-spacing:.14em;color:#fff}#crore span{display:block;font-weight:900;font-size:112px;line-height:1.05;color:#FFD54A}
#crore i{font-style:normal}#crore em{display:block;font-style:normal;font:800 36px Inter,sans-serif;color:#fff}
#badge{position:absolute;right:50px;top:1130px;opacity:0;width:150px;height:150px;border-radius:50%;background:#FFD54A;display:flex;align-items:center;justify-content:center;font:900 76px Inter,sans-serif;color:#111;box-shadow:0 10px 30px rgba(0,0,0,.6)}
#badge i{font-style:normal;position:absolute;left:0;width:96px;text-align:right}#badge{justify-content:flex-end;padding-right:22px}#badge span{font-size:40px;opacity:.7}
.cred,.tagimg{position:absolute;left:40px;right:40px;text-align:center;opacity:0;font:600 22px "JetBrains Mono",monospace;color:rgba(255,255,255,.88);text-shadow:0 1px 4px #000}
.tagimg{top:1270px}.tagc{position:absolute;opacity:0;text-align:center;font:700 22px "JetBrains Mono",monospace;color:#fff;background:rgba(0,0,0,.7);padding:6px;border-radius:10px}
#tiles{position:absolute;left:50px;right:50px;top:560px;display:grid;grid-template-columns:1fr 1fr;gap:24px}
.tile{opacity:0;padding:26px 18px;border-radius:24px;background:rgba(8,10,14,.82);border:3px solid #FFD54A;text-align:center;color:#fff}
.tile i{display:block;font-style:normal;font-size:84px}.tile b{display:block;font:900 44px Inter,sans-serif;margin-top:6px}.tile u{display:block;text-decoration:none;font:700 26px Inter,sans-serif;color:#FF8A80;margin-top:6px}
#hub{position:absolute;left:50px;right:50px;top:330px;opacity:0;text-align:center;padding:34px 20px;border-radius:30px;background:rgba(8,10,14,.82)}
#hub small{display:block;font:800 32px "JetBrains Mono",monospace;letter-spacing:.1em;color:#fff}#hub b{display:block;font:900 108px/1.02 Inter,sans-serif;color:#fff;margin:16px 0}
#hub em{display:block;font-style:normal;font:900 80px Inter,sans-serif;color:#fff}
.tv{position:absolute;opacity:0;width:240px;border-radius:22px;overflow:hidden;border:5px solid #FFD54A;background:#111;box-shadow:0 14px 40px rgba(0,0,0,.7)}
.tv img{width:100%;height:220px;object-fit:cover;display:block}.tv b{display:block;padding:10px 6px;text-align:center;font:900 24px Inter,sans-serif;color:#111;background:#FFD54A}
#chk{position:absolute;left:50px;right:50px;top:520px;opacity:0;padding:34px 34px;border-radius:30px;background:rgba(8,10,14,.9);border:3px solid #FFD54A}
#chk small{display:block;font:800 32px "JetBrains Mono",monospace;letter-spacing:.08em;color:#FFD54A;margin-bottom:18px}#chk p{font:900 54px/1.2 Inter,sans-serif;color:#fff;margin:16px 0}
#cta{position:absolute;left:40px;right:40px;top:330px;opacity:0;text-align:center;padding:30px 20px;border-radius:30px;background:rgba(8,10,14,.75)}
#cta small{display:block;font:800 48px Inter,sans-serif;color:#fff}#cta b{display:block;margin-top:14px;font:900 80px/1.08 Inter,sans-serif;color:#fff}
#share{position:absolute;left:0;right:0;top:1120px;display:flex;flex-direction:column;align-items:center;gap:14px;opacity:0}
#share span{display:block;padding:14px 26px;border-radius:22px;background:rgba(8,10,14,.78);text-align:center;font:900 46px/1.12 Inter,sans-serif;color:#fff}
#share svg{background:#FF8A00;border-radius:50%;padding:16px;box-shadow:0 0 0 12px rgba(255,138,0,.3)}
.opp{position:absolute;opacity:0;translate:-50% -50%;padding:14px 22px;border-radius:18px;background:rgba(8,10,14,.9);border:3px solid #FFD54A;font:800 32px/1.18 Inter,sans-serif;color:#fff;text-align:center;white-space:nowrap;box-shadow:0 10px 30px rgba(0,0,0,.6)}
.opp b{display:block;font:900 34px Inter,sans-serif;color:#FFD54A;margin-bottom:4px}
.oname{position:absolute;opacity:0;translate:-50% 0;padding:4px 10px;border-radius:8px;background:rgba(8,10,14,.75);font:800 22px Inter,sans-serif;color:#fff;white-space:nowrap}
#legend{position:absolute;left:40px;right:40px;top:400px;display:flex;flex-wrap:wrap;justify-content:center;gap:10px 22px;opacity:0;font:700 26px Inter,sans-serif;color:#fff}
#legend span{display:flex;align-items:center;gap:8px;padding:6px 14px;border-radius:12px;background:rgba(8,10,14,.75)}#legend i{display:inline-block;width:36px;height:8px;border-radius:4px}#legend i.rl{height:6px;outline:3px dashed #fff;outline-offset:2px}
#brand{position:absolute;left:0;right:0;top:96px;text-align:center;font:700 22px "JetBrains Mono",monospace;letter-spacing:.2em;color:rgba(255,255,255,.8);text-shadow:0 2px 6px #000}
#credit{position:absolute;left:40px;right:40px;top:1300px;text-align:center;font:500 18px "JetBrains Mono",monospace;color:rgba(255,255,255,.6);text-shadow:0 1px 3px #000}"""
S = S[:LINES_AT] + S[LINES_AT:]
open(f"{P}/index.html", "w").write(f"""<!doctype html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="30">
<div id="maplayer"><svg id="world" viewBox="{vb(WIDE_C, WIDE_W * 1.25)}" preserveAspectRatio="xMidYMid slice">{"".join(S)}</svg>
{"".join(H)}</div>
{"".join(H2)}
<audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.55" data-fade-out="1.5"></audio>
{"".join(SFX)}
</div><script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(J)}
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>""")
print("END", END, {k: (round(v[0]), round(v[1])) for k, v in G.items()})
