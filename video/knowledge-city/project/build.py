"""Knowledge City (Chittora, Diggi Malpura Road) — dreamy explainer reel. Text-led draft; Ashwil adds face (0–2 s) + voice later."""
import json, math
P = "proj"
TJ = json.load(open("tile.json")); Z, X0, Y0 = TJ["z"], TJ["x0"], TJ["y0"]
def wp(lat, lon):
    n = 256 * 2 ** Z
    return ((lon + 180) / 360 * n - X0 * 256, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n - Y0 * 256)
def vb(c, w): h = w * 1920 / 1080; return f"{c[0] - w / 2:.1f} {c[1] - h / 2:.1f} {w:.1f} {h:.1f}"
def pd(pl): return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pl)
S, H, J, SFX = [], [], [], []
def sfx(n, t, v=.3): SFX.append(f'<audio class="clip" src="assets/sfx/{n}.mp3" data-start="{t:.2f}" data-duration="2" data-track-index="{20 + len(SFX)}" data-volume="{v}"></audio>')
def cam(t, c, w, d=1.4, ease="power2.inOut"): J.append(f'tl.to("#world", {{attr:{{viewBox:"{vb(c, w)}"}}, duration:{d}, ease:"{ease}"}}, {t:.2f});')
def cap(i, html, a, b, top=1330):
    H.append(f'<div class="st" id="{i}" style="top:{top}px"><span class="bx">{html}</span></div>')
    J.append(f'tl.fromTo("#{i}", {{opacity:0, y:18, scale:.96}}, {{opacity:1, y:0, scale:1, duration:.25, ease:"back.out(2)"}}, {a:.2f}); tl.to("#{i}", {{opacity:0, duration:.15}}, {b - .15:.2f});')
def show(i, a, b, d=.35): J.append(f'tl.fromTo("#{i}", {{opacity:0}}, {{opacity:1, duration:{d}}}, {a:.2f}); tl.to("#{i}", {{opacity:0, duration:{d}}}, {b - d:.2f});')
Y, E = '<span class="y">', '</span>'; G, E2 = '<span class="g">', '</span>'

# ---------- geography ----------
KC = wp(26.6372, 75.7043)                     # Chittora (approx. scheme location)
SANG = wp(26.8146, 75.7731)
road = []
for e in json.load(open("diggi.json"))["elements"]:
    road += [(g["lat"], g["lon"]) for g in e["geometry"]]
road = sorted(set(road), key=lambda p: -p[0])
ROAD = [wp(*p) for p in road[::2]]
ROADX = [ROAD[-1], wp(26.70, 75.715), wp(26.655, 75.69), wp(26.60, 75.62), wp(26.577, 75.559)]   # indicative continuation towards Phagi
BG = 125                                      # ~1,800 bigha ≈ 4.5 km² ≈ 2.1 km square ≈ 125 px at z13 (illustrative)

S.append('<image href="assets/img/sat.jpg" x="0" y="0" width="2304" height="3072" preserveAspectRatio="none"/>')
S.append('<rect x="-3000" y="-3000" width="9000" height="9000" style="fill:#0a0d14;opacity:.30"/>')
S.append(f'<path id="road" pathLength="1" d="{pd(ROAD)}" style="fill:none;stroke:#FFD36B;stroke-width:6;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1;filter:drop-shadow(0 0 6px #FFB000)"/>')
S.append(f'<path id="roadx" d="{pd(ROADX)}" style="fill:none;stroke:#FFD36B;stroke-width:5;stroke-dasharray:12 10;opacity:0"/>')
S.append(f'<text id="lsang" x="{SANG[0] - 14:.1f}" y="{SANG[1]:.1f}" text-anchor="end" style="font:900 24px Inter;fill:#fff;paint-order:stroke;stroke:#000;stroke-width:6px;opacity:0">Sanganer · Airport</text>')
S.append(f'<text id="lroad" x="{ROAD[len(ROAD) // 2][0] - 16:.1f}" y="{ROAD[len(ROAD) // 2][1]:.1f}" text-anchor="end" style="font:900 22px Inter;fill:#FFD36B;paint-order:stroke;stroke:#000;stroke-width:6px;opacity:0">Diggi Malpura Rd · SH-12</text>')
# scheme area (illustrative) + glow
S.append(f'<rect id="area" x="{KC[0] - BG / 2:.1f}" y="{KC[1] - BG / 2:.1f}" width="{BG}" height="{BG}" rx="10" style="fill:#5CF08A;fill-opacity:.10;stroke:#5CF08A;stroke-width:3;stroke-dasharray:10 7;opacity:0"/>')
S.append(f'<circle id="pin" cx="{KC[0]:.1f}" cy="{KC[1]:.1f}" r="9" style="fill:#5CF08A;stroke:#fff;stroke-width:3;opacity:0"/>')
S.append(f'<circle id="pulse" cx="{KC[0]:.1f}" cy="{KC[1]:.1f}" r="9" style="fill:none;stroke:#5CF08A;stroke-width:3;opacity:0"/>')
# dream city: glowing blocks (deterministic layout) inside / around the scheme area
import random
rnd = random.Random(7)
blocks = []
for i in range(46):
    r = rnd.uniform(8, 120); a = rnd.uniform(0, 2 * math.pi)
    x, y = KC[0] + r * math.cos(a), KC[1] + r * math.sin(a) * .8
    w, h = rnd.uniform(10, 26), rnd.uniform(8, 20)
    blocks.append((x, y, w, h, r))
blocks.sort(key=lambda b: b[4])
S.append('<g id="dream" style="opacity:0">' + "".join(
    f'<rect class="db" x="{x - w / 2:.1f}" y="{y - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="2" style="fill:#FFD98A;fill-opacity:.55;stroke:#FFF1C9;stroke-width:1.2;filter:drop-shadow(0 0 6px #FFC24A)"/>'
    for x, y, w, h, r in blocks) + "</g>")

import random as _r
rr = _r.Random(11); BL = []
LAND = [("UNIVERSITY", 0, -70, 50, 32, 34, "#c9b48a"), ("MEDICAL COLLEGE", 85, -10, 26, 26, 70, "#d8dde6"), ("IT INSTITUTE", -75, 20, 20, 20, 120, "#5d8fc9"),
        ("LIBRARY", 40, 75, 28, 28, 30, "#c9b48a"), ("CONVENTION CENTRE", -45, 95, 56, 32, 22, "#b89a6a")]
for nm, x, z, w, d, h, c in LAND: BL.append({"x": x, "z": z, "w": w, "d": d, "h": h, "c": c, "e": "#ffb84a", "ei": .35, "label": nm})
for i in range(70):
    r = rr.uniform(30, 150); a = rr.uniform(0, 6.283); x, z = r * math.cos(a), r * math.sin(a)
    if any(abs(x - b["x"]) < (b["w"] / 2 + 10) and abs(z - b["z"]) < (b["d"] / 2 + 10) for b in BL): continue
    BL.append({"x": round(x, 1), "z": round(z, 1), "w": round(rr.uniform(7, 13), 1), "d": round(rr.uniform(7, 13), 1), "h": round(rr.uniform(22, 95), 1),
               "c": rr.choice(["#3b4a63", "#4a5670", "#6b7f9e", "#2f3d55"]), "e": "#ffb040", "ei": round(rr.uniform(.15, .5), 2)})
BL.sort(key=lambda b: math.hypot(b["x"], b["z"]))
SPUR = [ROADX[1], (KC[0] - 20, KC[1] - 30), KC]
D3 = {"ov": [list(p) for p in ROAD[::3] + ROADX[1:]], "cc": list(wp(26.915, 75.805)), "road": [list(p) for p in ROAD[::3] + ROADX[:2]], "spur": [list(p) for p in SPUR], "kc": list(KC), "blocks": BL}
# ---------- 0–2.2 · face placeholder (Ashwil's face goes here) ----------
H.append('<video id="avatar" class="clip" src="assets/avatar.mp4" data-start="0" data-duration="__ENDN__" data-track-index="0" playsinline data-has-audio="true" data-volume="1" style="position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover"></video>')
J.append('tl.set("#avatar", {opacity:1}, 0); tl.to("#avatar", {opacity:0, scale:1.06, duration:.2}, 0.72);')
H.append('<div id="kt"><i>DIGGI MALPURA ROAD</i><b>KNOWLEDGE<br/>CITY</b></div>')
J.append('tl.fromTo("#kt", {opacity:0, scale:1.3}, {opacity:1, scale:1, duration:.3, ease:"back.out(2)"}, 0.05); tl.to("#kt", {opacity:0, duration:.2}, 0.75);')
cap("c0", f"{Y}Diggi Malpura Road{E} pe aa raha hai — {G}Knowledge City{E2}", 0.25, 2.0, top=1450)
cap("c0b", f"Jaipur ka {Y}agla bada sapna{E}", 2.0, 5.0)
sfx("impact-bass-1", .25, .35)

# ---------- 1.9–9.6 · 3D: fly down Diggi Malpura Road, a vertical city rises ----------
J.append(f'tl.set("#world", {{attr:{{viewBox:"{vb(((SANG[0] + KC[0]) / 2, (SANG[1] + KC[1]) / 2), 900)}"}}}}, 0);')
J.append('tl.set("#gl", {opacity:0}, 0); tl.to("#gl", {opacity:1, duration:.2}, 0.72); tl.to("#gl", {opacity:0, duration:.5}, 9.3);')
H.append('<div id="dtag"><b>10 SAAL BAAD?</b><i>imagination · not an official plan</i></div>'); show("dtag", 5.1, 7.6)

cap("c1", f"Socho… 10 saal baad — {Y}university, medical college, IT institute{E}…", 5.0, 7.6)
H.append('<div id="today"><b>AAJ — MAUKA HAI</b><i>early stage</i></div>'); show("today", 7.8, 9.6, .25)
cap("c2", f"Aaj? Aaj ek {Y}mauka hai — invest karne ka sahi samay{E}", 7.7, 12.83)
sfx("riser", 1.9, .3); sfx("whoosh", 2.0, .3); sfx("impact-bass-1", 5.0, .35); sfx("whoosh", 7.6, .3)
for k in range(8): sfx("pop", 5.1 + .25 * k, .15)

# ---------- 9.6–16 · where it is ----------
mid = ((SANG[0] + KC[0]) / 2, (SANG[1] + KC[1]) / 2)
cam(9.6, mid, 900, 1.2)
J.append('tl.to("#road", {strokeDashoffset:0, duration:1.6, ease:"power1.inOut"}, 10.4); tl.to("#roadx", {opacity:1, duration:.5}, 11.8);')
J.append('tl.to("#lsang", {opacity:1, duration:.3}, 10.3); tl.to("#lroad", {opacity:1, duration:.3}, 11.0);')
J.append('tl.fromTo("#pin", {opacity:0, attr:{r:30}}, {opacity:1, attr:{r:9}, duration:.4, ease:"back.out(2)"}, 12.6);')
J.append('tl.fromTo("#pulse", {opacity:.9, attr:{r:9}}, {opacity:0, attr:{r:60}, duration:1.2, repeat:12, ease:"power1.out"}, 12.8);')
H.append('<div class="lab" id="kclab"><b>KNOWLEDGE CITY</b><i>Chittora · approx. location</i></div>')
cam(13.6, (KC[0], KC[1] - 10), 520, 1.6)
show("kclab", 13.0, 13.9, .3)
cap("c4", f"JDA ki official scheme — {Y}Knowledge City South{E}", 13.6, 16.0)
sfx("whoosh-short", 9.6, .25); sfx("ping", 12.6, .3)

# ---------- 16–27.4 · the plan (as per reports) ----------
J.append('tl.fromTo("#area", {opacity:0, scale:.6, transformOrigin:"' + f'{KC[0]:.1f}px {KC[1]:.1f}px' + '"}, {opacity:1, scale:1, duration:.6, ease:"back.out(1.6)"}, 16.2);')
PLAN = ["UNIVERSITY", "IT INSTITUTE", "TECHNICAL INSTITUTES", "MEDICAL COLLEGE &amp; HOSPITAL", "INTERNATIONAL LIBRARY", "CONVENTION CENTRE"]
H.append('<div id="plan"><b>THE PLAN · AS PER JDA LAYOUT &amp; REPORTS</b>' + "".join(f'<div class="pi" id="pi{k}"><s>{k + 1}</s>{p}</div>' for k, p in enumerate(PLAN)) + '<em>~1,000 hectare · Dainik Bhaskar</em></div>')
show("plan", 19.3, 27.4)
for k in range(len(PLAN)):
    t = 19.4 + .9 * k
    J.append(f'tl.fromTo("#pi{k}", {{opacity:0, x:-40}}, {{opacity:1, x:0, duration:.35, ease:"back.out(2)"}}, {t:.2f});'); sfx("pop", t, .22)
J.append('tl.from("#plan em", {opacity:0, scale:.5, duration:.4, ease:"back.out(2)"}, 26.6);')

# photos for each planned facility (representative images)
PIMG = [("p_univ.jpg", "University", "Representative image"), ("p_it.jpg", "IT institute", "Representative image"), ("p_tech.jpg", "Technical institutes", "Representative image"),
        ("p_med.jpg", "Medical college &amp; hospital", "Representative image"), ("p_lib.jpg", "International library", "Representative image"), ("p_jecc.jpg", "Convention centre", "JECC, Jaipur · representative")]
for k, (src, nm, cr) in enumerate(PIMG):
    t = 19.4 + .9 * k
    H.append(f'<div class="pim" id="pim{k}"><img src="assets/img/{src}"/><div><b>{nm}</b><i>{cr}</i></div></div>')
    J.append(f'tl.fromTo("#pim{k}", {{opacity:0, scale:.85, y:30}}, {{opacity:1, scale:1, y:0, duration:.35, ease:"back.out(1.8)"}}, {t:.2f}); tl.to("#pim{k}", {{opacity:0, duration:.2}}, {(t + .9 if k < 5 else 27.3):.2f});')
# 3D-city section: quick photo flashes as the towers rise
for k, (src, nm, t0, t1) in enumerate([("p_univ.jpg", "University", 5.2, 6.0), ("p_med.jpg", "Medical college", 6.0, 6.8), ("p_it.jpg", "IT institute", 6.8, 7.6)]):
    H.append(f'<div class="pfl" id="pfl{k}"><img src="assets/img/{src}"/><b>{nm}</b><i>Representative image</i></div>')
    J.append(f'tl.fromTo("#pfl{k}", {{opacity:0, x:40}}, {{opacity:1, x:0, duration:.25}}, {t0:.2f}); tl.to("#pfl{k}", {{opacity:0, duration:.2}}, {t1:.2f});')

# official proof: JDA layout + Dainik Bhaskar (23 Jan 2026)
H.append('<div class="doc" id="djda"><img src="assets/img/jda_layout.jpg"/><i>JDA · Knowledge City South – Chittora · layout plan (supplied)</i></div>')
J.append('tl.fromTo("#djda", {opacity:0, scale:.8, rotation:-3}, {opacity:1, scale:1, rotation:0, duration:.45, ease:"back.out(1.6)"}, 13.9); tl.fromTo("#djda img", {scale:1}, {scale:1.25, x:-30, y:20, duration:2.0, ease:"power1.inOut"}, 14.2); tl.to("#djda", {opacity:0, duration:.25}, 16.0);')
H.append('<div class="doc tall" id="dbh"><img src="assets/img/bhaskar.jpg"/><i>Dainik Bhaskar, Jaipur · 23 January 2026</i></div>')
J.append('tl.fromTo("#dbh", {opacity:0, scale:.8, rotation:3}, {opacity:1, scale:1, rotation:0, duration:.45, ease:"back.out(1.6)"}, 16.1); tl.fromTo("#dbh img", {scale:1, y:0}, {scale:1.3, y:120, x:0, duration:2.4, ease:"power1.inOut"}, 16.6); tl.to("#dbh", {opacity:0, duration:.25}, 19.3);')
H.append('<div id="stamp">OFFICIAL</div>')
J.append('tl.fromTo("#stamp", {opacity:0, scale:2.2, rotation:-18}, {opacity:1, scale:1, rotation:-12, duration:.3, ease:"power3.in"}, 14.6); tl.to("#stamp", {opacity:0, duration:.2}, 19.2);')
sfx("pop", 13.9, .3); sfx("impact-bass-1", 14.6, .3); sfx("whoosh-short", 16.1, .3)
cap("c5", f"January 2026 mein JDA ne kabza {Y}RSRDC ko saunp diya{E} — project ko mili gati, lagbhag {Y}1,000 hectare{E}", 16.1, 19.3)
cap("c6", f"Plan suniye — {Y}university, IT institute, technical institute, medical college, international library, convention centre{E}", 19.3, 24.83)
cap("c6b", f"Aur {Y}desh-videsh{E} ke bade sansthano ko bhi yahan aamantrit kiya gaya hai", 24.83, 27.4)

# ---------- 27.4–47.6 · it has happened before ----------
def ip(lat, lon, GX=40, GY=300, GW=1000): return (GX + (lon - 67.0) / 32.0 * GW, GY + (37.5 - lat) / 32.5 * 1293 * GW / 1200)
CIT = [("Greater Noida", 28.47, 77.50, "Knowledge Park", 1), ("Sonipat", 28.99, 77.02, "Education City", -1), ("Mohali", 30.70, 76.72, "Knowledge City", 1), ]
ih = '<div id="india"><img src="assets/img/indiamap.png" style="position:absolute;left:40px;top:300px;width:1000px;opacity:.95"/>'
for k, (n, la, lo, sub, sd) in enumerate(CIT):
    x, y = ip(la, lo); dy = {"Greater Noida": 10, "Sonipat": -40, "Mohali": -30}[n]
    ih += f'<div class="ic" id="ic{k}" style="left:{x:.0f}px;top:{y:.0f}px"><i></i><b style="{"left" if sd > 0 else "right"}:22px;top:{dy}px">{n} <span>{sub}</span></b></div>'
jx, jy = ip(26.92, 75.82)
ih += f'<div class="ic jp" id="icj" style="left:{jx:.0f}px;top:{jy:.0f}px"><i></i><b style="right:26px;top:-20px">Jaipur?</b></div>'
ih += '<div id="inote">India map: Milenioscuro, CC BY 4.0</div></div>'
H.append(ih)
show("india", 27.4, 47.8, .4)
STORY = [("Greater Noida — Knowledge Park", "Pehle khet the. Aaj wahan bahut saare colleges aur universities khul gayi hain.", 30.0, 34.5, "u_gn.jpg", "Galgotias University, Greater Noida · image supplied"),
         ("Sonipat — Education City", "Ashoka, OP Jindal jaisi universities ne chhote sheher ko national map pe jagah de di.", 34.5, 39.0, "u_so.jpg", "Sonipat · image supplied"),
         ("Mohali — Knowledge City", "IISER jaise research institutes ke aas-paas naye sectors develop ho gaye.", 39.0, 43.5, "u_mo.jpg", "IISER Mohali · image supplied")]
for k, (t1, t2, a, b, img, cr) in enumerate(STORY):
    J.append(f'tl.fromTo("#ic{k}", {{opacity:0, scale:.3}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(3)"}}, {a - .1:.2f}); tl.to("#ic{k} i", {{scale:1.5, duration:.3, yoyo:true, repeat:3}}, {a + .2:.2f});')
    H.append(f'<div class="card" id="cd{k}"><b>{t1}</b><p>{t2}</p></div>'); show(f"cd{k}", a, b, .25)
    H.append(f'<div class="cimg" id="ci{k}"><img src="assets/img/{img}"/><i>{cr}</i></div>')
    J.append(f'tl.fromTo("#ci{k}", {{opacity:0, scale:.85, y:30}}, {{opacity:1, scale:1, y:0, duration:.4, ease:"back.out(1.6)"}}, {a + .1:.2f}); tl.to("#ci{k}", {{opacity:0, duration:.25}}, {b - .1:.2f});')
    sfx("click-soft", a, .25)
J.append('tl.fromTo("#icj", {opacity:0, scale:.3}, {opacity:1, scale:1, duration:.4, ease:"back.out(3)"}, 45.6); tl.to("#icj i", {scale:1.6, duration:.35, yoyo:true, repeat:3}, 45.9);')
cap("c7", f"Yeh idea naya nahi hai — India ke kuch shehron ne yahi kiya, {Y}aur dekhiye kya hua{E}", 27.5, 30.0)

# ---------- 47.6–59.5 · imagine Jaipur ----------
J.append('tl.to("#gl", {opacity:1, duration:.6}, 47.5); tl.to("#gl", {opacity:0, duration:.6}, 59.3);')
J.append('tl.to("#area", {opacity:0, duration:.4}, 47.6); tl.to(["#pin","#pulse"], {opacity:0, duration:.3}, 47.6);')
DEM = [("HOSTELS", -1, 0), ("PG", 1, 0), ("CAFES", -1, 1), ("SHOPS", 1, 1), ("HOMES", -1, 2), ("RENTALS", 1, 2)]
H.append('<div id="dem">' + "".join(f'<div class="dm" id="dm{k}" style="{"left" if s < 0 else "right"}:60px;top:{640 + 150 * r}px">{t}</div>' for k, (t, s, r) in enumerate(DEM)) + '</div>')
for k in range(len(DEM)):
    t = 53.0 + .45 * k; J.append(f'tl.fromTo("#dm{k}", {{opacity:0, scale:.5}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2.5)"}}, {t:.2f}); tl.to("#dm{k}", {{opacity:0, duration:.3}}, 56.0);'); sfx("pop", t, .18)
H.append('<div id="dtag2"><b>IMAGINE JAIPUR</b><i>imagination · not an official plan</i></div>'); show("dtag2", 48.0, 59.5)
cap("c8", f"Ab socho Jaipur mein… {Y}sab ek hi belt mein{E}", 47.7, 50.8)
cap("c9", f"Hazaron students, doctors, teachers — unhe chahiye {Y}ghar, hostel, PG, cafe, shops{E}", 50.8, 56.0)
H.append('<div id="quote">Jahan <span class="g">knowledge</span> aata hai —<br/>wahan sheher apne aap<br/>ban jaata hai.</div>')
J.append('tl.fromTo("#quote", {opacity:0, scale:.9}, {opacity:1, scale:1, duration:.5, ease:"power2.out"}, 56.0); tl.to("#quote", {opacity:0, duration:.3}, 59.4);')
sfx("sparkle", 56.0, .3)

# ---------- 59.5–66 · reality check ----------

cam(59.4, (KC[0], KC[1]), 560, 1.0)
J.append('tl.to(["#pin","#area"], {opacity:1, duration:.4}, 60.0);')
H.append('<div id="chk"><b>ABHI EARLY STAGE · PEHLE CHECK KARO</b><div>✓ Official map</div><div>✓ Approval</div><div>✓ Patta &amp; conversion</div></div>')
show("chk", 60.2, 66.0)
J.append('tl.from("#chk div", {opacity:0, x:-30, duration:.3, stagger:.5}, 61.2);')
cap("c10", f"Par yaad rakhna — {Y}abhi yeh early stage hai{E}", 59.5, 61.6)
cap("c11", f"Plot lene se pehle scheme ka {Y}official map, JDA approval aur patta{E} zaroor check karo", 61.6, 66.0)

# ---------- 66–73 · CTA ----------
END = 73.0
cap("c12", f"Kya Jaipur ka Knowledge City {G}agla Greater Noida{E2} banega?", 66.0, 69.6)
cap("c13", f"Comment kijiye — {Y}reel save kariye aur share kariye{E}", 69.6, END + .2)
H.append('<div id="share"><span><svg viewBox="0 0 24 24" width="52" height="52"><path d="M6 3h12v18l-6-4-6 4z" style="fill:#FFE03A"/></svg>Save it</span><span><svg viewBox="0 0 24 24" width="52" height="52"><path d="M3 11l18-8-8 18-2-8z" style="fill:none;stroke:#fff;stroke-width:2;stroke-linejoin:round"/></svg>Send it</span></div>')
J.append('tl.fromTo("#share", {opacity:0, y:20}, {opacity:1, y:0, duration:.4}, 69.8); tl.to("#share svg", {scale:1.15, duration:.4, yoyo:true, repeat:5}, 70.2);')
H.append('<div id="brand">ASHWILLPOWER · JAIPUR REAL ESTATE</div>')
H.append('<div id="credit">Satellite: Sentinel-2 cloudless 2016 by EOX (CC BY 4.0) · Map data © OpenStreetMap · plan details as per media reports</div>')
J.append('tl.set("#credit", {opacity:0}, 0); tl.to("#credit", {opacity:1, duration:.3}, 2.3);')

ANCH = [(0, 0), (2.0, 2.9), (5.0, 5.5), (7.6, 9.0), (9.6, 12.0), (13.6, 14.6), (16.05, 17.25), (19.3, 23.77), (27.4, 34.85), (30.0, 39.4), (34.5, 45.6), (39.0, 52.3), (43.5, 58.6), (47.6, 59.7), (56.0, 68.9), (59.45, 72.0), (66.0, 80.9), (73.0, 87.4)]
def o2n(t):
    for (a0, b0), (a1, b1) in zip(ANCH, ANCH[1:]):
        if t <= a1: return b0 + (b1 - b0) * (t - a0) / (a1 - a0)
    return ANCH[-1][1] + t - ANCH[-1][0]
ENDN = 87.6
import re as _re
SFX = [_re.sub(r'data-start="([\d.]+)"', lambda m: f'data-start="{o2n(float(m.group(1))):.2f}"', x) for x in SFX]
H = [x.replace("__ENDN__", str(ENDN)) for x in H]
WARP = "const master = gsap.timeline({ paused: true });\n" + "\n".join(f"master.fromTo(tl, {{time:{a0}}}, {{time:{a1}, duration:{b1 - b0:.3f}, ease:'none', immediateRender:false}}, {b0});" for (a0, b0), (a1, b1) in zip(ANCH, ANCH[1:])) + f"\nmaster.set({{}}, {{}}, {ENDN});"
CSS = """*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#070b12}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;background:linear-gradient(180deg,#05070c 0%,#1d1630 20%,#4a2a3a 28%,#0b0f17 44%)}
#world{position:absolute;inset:0;width:1080px;height:1920px}.y{color:#FFD36B}.g{color:#5CF08A}
.st{position:absolute;left:50px;right:50px;text-align:center;opacity:0}.st .bx{display:inline-block;padding:12px 26px 14px;border-radius:22px;background:rgba(6,8,12,.64);font:900 60px/1.12 Inter,Arial,sans-serif;color:#fff;text-shadow:0 4px 0 #000}
#face{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:radial-gradient(70% 50% at 50% 40%,#2b3446,#0b0d12);opacity:0}
#face div{border:4px dashed rgba(255,255,255,.35);border-radius:30px;padding:60px 80px;text-align:center;font-family:Inter}#face b{display:block;font-size:72px;color:#fff;letter-spacing:.06em}#face i{display:block;font-style:normal;font-size:34px;color:#9fb0c4}
#kt{position:absolute;left:0;right:0;top:200px;text-align:center;opacity:0;font-family:Inter;text-shadow:0 6px 0 #000,0 0 30px rgba(0,0,0,.8)}#kt i{display:block;font-style:normal;font:800 34px "JetBrains Mono",monospace;letter-spacing:.3em;color:#FFD36B}#kt b{display:block;font-weight:900;font-size:120px;line-height:.95;color:#5CF08A}
#rtag{position:absolute;left:0;right:0;top:300px;text-align:center;opacity:0;font-family:Inter}#rtag b{display:inline-block;padding:8px 24px;border-radius:16px;background:#FFD36B;font-weight:900;font-size:60px;color:#1a1200;box-shadow:0 0 30px rgba(255,200,80,.6)}#rtag i{display:table;margin:10px auto 0;padding:6px 16px;border-radius:12px;background:rgba(6,8,12,.75);font:700 26px \"JetBrains Mono\",monospace;font-style:normal;color:#fff}\n#rlab{position:absolute;left:0;top:0;transform:translate(0,-50%);opacity:0;white-space:nowrap;padding:8px 18px;border-radius:14px;background:#FFD36B;box-shadow:0 0 30px rgba(255,200,80,.7);font-family:Inter}#rlab b{display:block;font-weight:900;font-size:40px;color:#1a1200}#rlab i{display:block;font:800 22px "JetBrains Mono",monospace;font-style:normal;color:#5a3d00}\n.ovl{position:absolute;left:0;top:0;transform:translate(-50%,-140%);opacity:0;white-space:nowrap;padding:8px 18px;border-radius:14px;font:900 40px Inter;color:#111;background:#FFD36B;box-shadow:0 0 30px rgba(255,200,80,.7)}#ovj{background:#fff;font-size:52px}#ovk{background:#5CF08A}\n.l3{position:absolute;left:0;top:0;transform:translate(-50%,-100%);opacity:0;white-space:nowrap;padding:6px 14px;border-radius:12px;background:rgba(6,8,12,.82);border:2px solid #FFD98A;font:900 28px Inter;color:#FFD98A}\n#dtag,#dtag2,#today{position:absolute;left:0;right:0;top:300px;text-align:center;opacity:0;font-family:Inter}#dtag b,#dtag2 b,#today b{display:inline-block;padding:8px 26px;border-radius:18px;background:rgba(6,8,12,.7);font-weight:900;font-size:72px;color:#FFD98A;text-shadow:0 0 24px rgba(255,194,74,.7)}
#dtag i,#dtag2 i,#today i{display:table;margin:10px auto 0;padding:6px 16px;border-radius:12px;background:rgba(6,8,12,.75);font:700 26px "JetBrains Mono",monospace;font-style:normal;color:#fff}#today b{color:#fff;text-shadow:none}
.lab{position:absolute;left:0;right:0;top:850px;text-align:center;opacity:0;font-family:Inter}.lab b{display:inline-block;padding:10px 24px;border-radius:16px;background:#5CF08A;font-weight:900;font-size:50px;color:#06210f}.lab i{display:table;margin:8px auto 0;padding:5px 14px;border-radius:10px;background:rgba(6,8,12,.8);font:700 24px "JetBrains Mono",monospace;font-style:normal;color:#fff}
.pim{position:absolute;left:150px;right:150px;top:820px;height:470px;opacity:0;border-radius:22px;overflow:hidden;border:3px solid #5CF08A;box-shadow:0 20px 50px rgba(0,0,0,.7);background:#111}.pim img{width:100%;height:100%;object-fit:cover}
.pim div{position:absolute;left:0;right:0;bottom:0;padding:30px 18px 10px;background:linear-gradient(180deg,transparent,rgba(0,0,0,.85));font-family:Inter}.pim b{display:block;font-weight:900;font-size:40px;color:#fff}.pim i{display:block;font-style:normal;font-size:20px;color:#ddd}
.pfl{position:absolute;right:40px;top:470px;width:360px;height:250px;opacity:0;border-radius:18px;overflow:hidden;border:3px solid #FFD98A;box-shadow:0 14px 40px rgba(0,0,0,.7)}.pfl img{width:100%;height:100%;object-fit:cover}.pfl b{position:absolute;left:12px;bottom:26px;font:900 30px Inter;color:#fff;text-shadow:0 2px 6px #000}.pfl i{position:absolute;left:12px;bottom:6px;font:600 16px Inter;font-style:normal;color:#eee;text-shadow:0 2px 4px #000}
.doc{position:absolute;left:90px;right:90px;top:300px;height:820px;opacity:0;border-radius:18px;overflow:hidden;background:#fff;border:4px solid #FFD36B;box-shadow:0 24px 60px rgba(0,0,0,.75)}.doc img{width:100%;height:100%;object-fit:contain;transform-origin:50% 30%}.doc.tall{left:170px;right:170px;height:900px}
.doc i{position:absolute;left:0;right:0;bottom:0;padding:10px 14px;background:rgba(6,8,12,.88);font:700 22px Inter;font-style:normal;color:#FFD36B}
#stamp{position:absolute;right:70px;top:250px;opacity:0;padding:10px 22px;border:6px solid #e5262f;border-radius:14px;font:900 56px Inter;letter-spacing:.08em;color:#e5262f;background:rgba(255,255,255,.85)}
#plan{position:absolute;left:60px;right:60px;top:250px;opacity:0;padding:24px 28px;border-radius:24px;background:rgba(6,10,14,.86);border:2px solid #5CF08A;font-family:Inter}#plan>b{display:block;font:800 26px "JetBrains Mono",monospace;letter-spacing:.14em;color:#5CF08A;margin-bottom:10px}
.pi{display:flex;align-items:center;gap:16px;padding:9px 0;font-weight:900;font-size:40px;color:#fff;opacity:0}.pi s{text-decoration:none;display:inline-flex;align-items:center;justify-content:center;width:52px;height:52px;border-radius:50%;background:#5CF08A;color:#06210f;font-size:30px}
#plan em{display:block;margin-top:12px;font-style:normal;font-weight:900;font-size:44px;color:#FFD36B}
#india{position:absolute;inset:0;opacity:0;background:radial-gradient(120% 80% at 50% 45%,#16202e,#070b12)}
.ic{position:absolute;opacity:0}.ic i{position:absolute;left:-13px;top:-13px;width:26px;height:26px;border-radius:50%;background:#5CF08A;border:4px solid #fff;box-shadow:0 0 18px #5CF08A}
.ic b{position:absolute;white-space:nowrap;padding:6px 14px;border-radius:12px;background:rgba(6,8,12,.86);font:900 30px Inter;color:#fff}.ic b span{display:block;font-size:22px;color:#9ff7bd}
.ic.jp i{width:40px;height:40px;left:-20px;top:-20px;background:#FFD36B;box-shadow:0 0 30px #FFD36B}.ic.jp b{font-size:46px;background:#FFD36B;color:#111}
#inote{position:absolute;right:50px;top:1640px;font:500 20px "JetBrains Mono",monospace;color:rgba(255,255,255,.7)}
.cimg{position:absolute;left:110px;right:110px;top:720px;height:410px;opacity:0;border-radius:22px;overflow:hidden;border:3px solid #5CF08A;box-shadow:0 20px 50px rgba(0,0,0,.7)}.cimg img{width:100%;height:100%;object-fit:cover}.cimg i{position:absolute;left:0;right:0;bottom:0;padding:22px 14px 8px;background:linear-gradient(180deg,transparent,rgba(0,0,0,.85));font:600 20px Inter;font-style:normal;color:#eee}
.card{position:absolute;left:60px;right:60px;top:1160px;opacity:0;padding:20px 26px;border-radius:22px;background:rgba(6,10,14,.9);border-left:10px solid #5CF08A;font-family:Inter}.card b{display:block;font-weight:900;font-size:44px;color:#5CF08A}.card p{margin-top:6px;font-weight:700;font-size:34px;line-height:1.25;color:#fff}
.dm{position:absolute;opacity:0;padding:12px 26px;border-radius:40px;background:rgba(6,8,12,.82);border:3px solid #FFD98A;font:900 40px Inter;color:#FFD98A;box-shadow:0 0 24px rgba(255,194,74,.5)}
#quote{position:absolute;left:60px;right:60px;top:560px;text-align:center;opacity:0;padding:30px;border-radius:30px;background:rgba(6,8,12,.6);font:900 72px/1.15 Inter;color:#fff;text-shadow:0 4px 0 #000}
#chk{position:absolute;left:60px;right:60px;top:250px;opacity:0;padding:24px 28px;border-radius:24px;background:rgba(6,10,14,.88);border:2px solid #FFD36B;font-family:Inter}#chk b{display:block;font:800 26px "JetBrains Mono",monospace;letter-spacing:.12em;color:#FFD36B;margin-bottom:10px}#chk div{font-weight:900;font-size:46px;color:#fff;padding:6px 0}
#share{position:absolute;left:0;right:0;top:1060px;display:flex;justify-content:center;gap:30px;opacity:0}#share span{display:flex;align-items:center;gap:14px;padding:16px 28px;border-radius:40px;background:rgba(8,12,20,.86);border:2px solid rgba(255,255,255,.25);font:900 42px Inter;color:#fff}
#brand{position:absolute;left:0;right:0;top:150px;text-align:center;font:700 24px "JetBrains Mono",monospace;letter-spacing:.2em;color:rgba(255,255,255,.85);text-shadow:0 2px 6px #000}
#credit{position:absolute;left:40px;right:40px;bottom:90px;text-align:center;font:500 19px "JetBrains Mono",monospace;color:rgba(255,255,255,.65);text-shadow:0 1px 3px #000}"""
open(f"{P}/index.html", "w").write(f"""<!doctype html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{ENDN}" data-width="1080" data-height="1920" data-fps="30">
<svg id="world" viewBox="{vb(KC, 520)}" preserveAspectRatio="xMidYMid slice">{"".join(S)}</svg>\n<canvas id="gl" width="1080" height="1920" style="position:absolute;inset:0;width:1080px;height:1920px;opacity:0"></canvas><div id="l3"></div>
{"".join(H)}
<audio id="music" class="clip" src="assets/music_tune.mp3" data-start="0" data-duration="{ENDN}" data-track-index="10" data-volume="0.13" data-fade-in="0.5" data-fade-out="2.5"></audio>
{"".join(SFX)}
</div><script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(J)}
{WARP}
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = master;
</script>__JS3__</body></html>""".replace("__JS3__", open("js3.js").read().replace("__D3__", json.dumps(D3)).replace("__ANCH__", json.dumps(ANCH))))
print("ok", END, len(ROAD))
