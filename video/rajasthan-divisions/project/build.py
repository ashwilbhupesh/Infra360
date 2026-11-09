"""Rajasthan: 7 divisions, 41 districts (Digital Banjaaraa). Text + music version; timeline in T dict so it can be re-timed to a voice.
World = z7 web-mercator px from tile (88, 52)."""
import json, math
P = "proj"
def wp(lon, lat):
    n = 256 * 2 ** 7
    return ((lon + 180) / 360 * n - 88 * 256, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n - 52 * 256)
D = json.load(open("data/rajasthan_districts.geojson"))["features"]
DV = json.load(open("data/divisions.geojson"))["features"]
OUT = json.load(open("data/rajasthan_outline.geojson"))["features"][0]["geometry"]
ORDER = ["Jaipur", "Jodhpur", "Ajmer", "Udaipur", "Kota", "Bikaner", "Bharatpur"]
DCOL = {"Jaipur": "#F5A623", "Jodhpur": "#E8505B", "Ajmer": "#9B6BDF", "Udaipur": "#3CB878", "Kota": "#3D8BFF", "Bikaner": "#D9C04A", "Bharatpur": "#F06BB5"}
PAL = ["#F7B267", "#F79D84", "#F4845F", "#C3A6FF", "#9DE0AD", "#7EC8E3", "#FFD166", "#EF8FB8", "#B8E986"]
def rings(g):
    if g["type"] == "Polygon": return [g["coordinates"][0]]
    return [p[0] for p in g["coordinates"]]
def pd(g, step=1):
    return " ".join("M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in (wp(*c) for c in r[::step])) + " Z" for r in rings(g))
def bbox(gs):
    pts = [wp(*c) for g in gs for r in rings(g) for c in r]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)
def vb(c, w): h = w * 1920 / 1080; return f"{c[0] - w / 2:.2f} {c[1] - h / 2:.2f} {w:.2f} {h:.2f}"
def fit(gs, padw=1.25, top=430, bot=1330):
    x0, y0, x1, y1 = bbox(gs)
    w = max((x1 - x0) * padw, (y1 - y0) * 1.12 * 1080 / (bot - top))
    cy = (y0 + y1) / 2 - ((top + bot) / 2 - 960) * w / 1080
    return ((x0 + x1) / 2, cy), w
SVG, H, J, SFX = [], [], [], []
def sfx(n, t, v=.3): SFX.append(f'<audio id="sx{len(SFX)}" class="clip" src="assets/sfx/{n}.mp3" data-start="{t:.2f}" data-duration="2" data-track-index="{20 + len(SFX)}" data-volume="{v}"></audio>')
CAMS = []
def cam(t, c, w, d=1.0, e="power2.inOut"):
    J.append(f'tl.to("#world", {{attr:{{viewBox:"{vb(c, w)}"}}, duration:{d}, ease:"{e}"}}, {t:.2f});'); CAMS.append((t, d, c, w))
def scr(p, t):
    c, w = CAMS[0][2], CAMS[0][3]
    for t0, d, c1, w1 in sorted(CAMS, key=lambda q: q[0]):
        if t0 + d <= t + 1e-6: c, w = c1, w1
    h = w * 1920 / 1080
    return ((p[0] - (c[0] - w / 2)) / w * 1080, (p[1] - (c[1] - h / 2)) / h * 1920)

# ---------------- timeline (seconds) ----------------
T = {"hook": 0.0, "galat": 1.3, "count": 2.6, "divs": 5.6, "div_step": .75}
t = T["divs"] + 7 * T["div_step"] + .8
DT = {}
for dv in ORDER:
    n = sum(1 for f in D if f["properties"]["division"] == dv)
    DT[dv] = (t, n); t += 1.1 + n * .62 + .5
T["final"] = t; T["cta"] = t + 2.0; END = round(t + 6.0, 2)

# ---------------- world ----------------
SVG.append('<rect x="-5000" y="-5000" width="12000" height="12000" style="fill:#0a1418"/>')
SVG.append('<image href="assets/img/bm6.jpg" x="-1024" y="-1024" width="3072" height="3072" preserveAspectRatio="none"/>')
SVG.append('<image href="assets/img/bm7.jpg" x="0" y="0" width="1280" height="1024" preserveAspectRatio="none"/>')
SVG.append('<rect id="dim" x="-5000" y="-5000" width="12000" height="12000" style="fill:#000;opacity:.25"/>')
SVG.append(f'<path id="state" d="{pd(OUT)}" style="fill:#2E8BC0;fill-opacity:.82;stroke:#fff;stroke-width:1.6;stroke-linejoin:round"/>')
for i, f in enumerate(D):
    p = f["properties"]; did = "d" + str(i)
    f["_id"] = did
    SVG.append(f'<path id="{did}" d="{pd(f["geometry"])}" style="fill:{DCOL[p["division"]]};fill-opacity:0;stroke:#fff;stroke-width:.5;stroke-opacity:0;stroke-linejoin:round"/>')
for f in DV:
    dv = f["properties"]["division"]
    SVG.append(f'<path id="v{dv}" d="{pd(f["geometry"])}" style="fill:{DCOL[dv]};fill-opacity:0;stroke:#fff;stroke-width:1.4;stroke-linejoin:round;opacity:0"/>')
SVG.append(f'<path id="stateo" d="{pd(OUT)}" pathLength="1" style="fill:none;stroke:#fff;stroke-width:2.4;stroke-linejoin:round"/>')

ALLC, ALLW = fit([OUT], 1.1, 420, 1360)
J.append(f'tl.set("#world", {{attr:{{viewBox:"{vb(ALLC, ALLW * 1.35)}"}}}}, 0);'); CAMS.append((0, 0, ALLC, ALLW * 1.35))
cam(0.05, ALLC, ALLW, 2.4, "power2.out")

# ---------------- hook ----------------
H.append('<div id="hook"><b>RAJASTHAN MEIN<br/>KITNE DISTRICT?</b></div>')
J.append('tl.fromTo("#hook", {opacity:0, scale:1.4}, {opacity:1, scale:1, duration:.3, ease:"back.out(2)"}, .05); tl.to("#hook", {opacity:0, duration:.2}, 2.5);')
H.append('<div id="fifty"><span>50?</span><i></i><b>GALAT</b></div>')
J.append(f'tl.fromTo("#fifty span", {{opacity:0, scale:.5}}, {{opacity:1, scale:1, duration:.25, ease:"back.out(2)"}}, .7); tl.set("#fifty", {{opacity:1}}, .7);'
         f'tl.fromTo("#fifty i", {{scaleX:0}}, {{scaleX:1, duration:.2, ease:"power3.out"}}, {T["galat"]:.2f}); tl.fromTo("#fifty b", {{opacity:0, scale:2.2}}, {{opacity:1, scale:1, duration:.22, ease:"back.out(2.5)"}}, {T["galat"]:.2f});'
         f'tl.to("#fifty", {{x:"+=14", duration:.05, yoyo:true, repeat:5}}, {T["galat"] + .2:.2f}); tl.to("#fifty", {{opacity:0, duration:.2}}, {T["count"] - .1:.2f});')
sfx("impact-bass-1", .05, .45); sfx("pop", .7, .3); sfx("impact-bass-1", T["galat"], .5)

# ---------------- count ----------------
H.append('<div id="cnt"><div><b>41</b><span>DISTRICTS</span></div><div><b>7</b><span>DIVISIONS</span></div><em>After Dec 2024 · 9 districts &amp; 3 divisions cancelled</em></div>')
J.append(f'tl.fromTo("#cnt", {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:.3}}, {T["count"]:.2f}); tl.from("#cnt div", {{opacity:0, scale:.4, duration:.3, stagger:.3, ease:"back.out(2.2)"}}, {T["count"] + .1:.2f}); tl.to("#cnt", {{opacity:0, duration:.25}}, {T["divs"] - .1:.2f});')
sfx("pop", T["count"] + .1, .3); sfx("pop", T["count"] + .4, .3)

# ---------------- 7 divisions intro ----------------
H.append('<div class="tag" id="tagd">7 DIVISIONS</div>')
J.append(f'tl.fromTo("#tagd", {{opacity:0, x:-40}}, {{opacity:1, x:0, duration:.3}}, {T["divs"]:.2f}); tl.to("#tagd", {{opacity:0, duration:.2}}, {DT["Jaipur"][0] - .1:.2f});')
J.append(f'tl.to("#state", {{fillOpacity:.25, duration:.4}}, {T["divs"]:.2f});')
for i, dv in enumerate(ORDER):
    t = T["divs"] + T["div_step"] * i
    f = next(x for x in DV if x["properties"]["division"] == dv)
    x0, y0, x1, y1 = bbox([f["geometry"]]); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    lp = {"Jaipur": (cx, cy - (y1 - y0) * .05), "Kota": (cx + (x1 - x0) * .08, cy), "Udaipur": (cx - (x1 - x0) * .08, cy)}.get(dv, (cx, cy))
    J.append(f'tl.to("#v{dv}", {{opacity:1, fillOpacity:.85, duration:.25}}, {t:.2f});')
    x, y = scr(lp, t)
    H.append(f'<div class="dvl" id="dl{dv}" style="left:{x:.0f}px;top:{y:.0f}px">{dv.upper()}</div>')
    J.append(f'tl.fromTo("#dl{dv}", {{opacity:0, scale:.4}}, {{opacity:1, scale:1, duration:.25, ease:"back.out(2.4)"}}, {t:.2f}); tl.to("#dl{dv}", {{opacity:0, duration:.2}}, {DT["Jaipur"][0] - .1:.2f});')
    sfx("pop", t, .28)

# ---------------- each division ----------------
for dv in ORDER:
    t0, n = DT[dv]
    fs = [f for f in D if f["properties"]["division"] == dv]
    fv = next(x for x in DV if x["properties"]["division"] == dv)
    c, w = fit([fv["geometry"]])
    cam(t0, c, w, 1.0)
    J.append(f'tl.to(".dvx", {{opacity:0, duration:.2}}, {t0:.2f});')
    for o in ORDER: J.append(f'tl.to("#v{o}", {{fillOpacity:{.85 if o == dv else .18}, opacity:1, duration:.4}}, {t0:.2f});')
    H.append(f'<div class="head" id="h{dv}" style="border-color:{DCOL[dv]}"><b style="background:{DCOL[dv]}">{ORDER.index(dv) + 1}/7</b>{dv.upper()} DIVISION<span>{n} DISTRICTS</span></div>')
    tend = t0 + 1.1 + n * .62 + .45
    J.append(f'tl.fromTo("#h{dv}", {{opacity:0, x:-50}}, {{opacity:1, x:0, duration:.3, ease:"power3.out"}}, {t0:.2f}); tl.to("#h{dv}", {{opacity:0, duration:.2}}, {tend:.2f});')
    sfx("whoosh", t0 - .05, .3)
    J.append(f'tl.to("#v{dv}", {{fillOpacity:0, duration:.3}}, {t0 + 1.0:.2f});')
    order = sorted(fs, key=lambda f: (-f["properties"]["label"][1], f["properties"]["label"][0]))
    lst = ""
    for j, f in enumerate(order):
        p = f["properties"]; t = t0 + 1.1 + j * .62; did = f["_id"]
        col = PAL[(ORDER.index(dv) * 3 + j) % len(PAL)]
        J.append(f'tl.to("#{did}", {{fill:"{col}", fillOpacity:.95, strokeOpacity:1, duration:.25}}, {t:.2f}); tl.fromTo("#{did}", {{strokeWidth:2.2}}, {{strokeWidth:.5, duration:.5, immediateRender:false}}, {t:.2f});')
        lp = wp(*p["label"]); x, y = scr(lp, t0 + 1.05)
        nm = p["district"].replace("-", "-<br/>") if len(p["district"]) > 11 else p["district"]
        H.append(f'<div class="dsl dvx" id="dn{did}" style="left:{x:.0f}px;top:{y:.0f}px">{nm}' + ('<em>NEW 2023</em>' if p["new_2023"] else '') + '</div>')
        J.append(f'tl.fromTo("#dn{did}", {{opacity:0, scale:.3}}, {{opacity:1, scale:1, duration:.22, ease:"back.out(2.6)"}}, {t:.2f});')
        lst += f'<p id="li{did}"><b style="background:{col}">{j + 1}</b>{p["district"]}</p>'
        J.append(f'tl.fromTo("#li{did}", {{opacity:0, x:-30}}, {{opacity:1, x:0, duration:.2}}, {t:.2f});')
        sfx("pop", t, .22)
    H.append(f'<div class="lst" id="ls{dv}" style="border-color:{DCOL[dv]}">{lst}</div>')
    J.append(f'tl.set("#ls{dv}", {{opacity:1}}, {t0 + 1.0:.2f}); tl.to("#ls{dv}", {{opacity:0, duration:.2}}, {tend:.2f}); tl.to(".dvx", {{opacity:0, duration:.2}}, {tend:.2f});')

# ---------------- final ----------------
cam(T["final"], ALLC, ALLW, 1.2)
for o in ORDER: J.append(f'tl.to("#v{o}", {{fillOpacity:0, duration:.3}}, {T["final"]:.2f});')
H.append('<div id="fin"><b>7</b> DIVISIONS · <b>41</b> DISTRICTS</div>')
J.append(f'tl.fromTo("#fin", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, {T["final"] + .4:.2f});')
H.append('<div id="cta"><b>AAPKA DISTRICT KAUNSA HAI?</b><span>COMMENT KARO</span></div>')
J.append(f'tl.fromTo("#cta", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:.35, ease:"back.out(2)"}}, {T["cta"]:.2f}); tl.to("#cta span", {{scale:1.08, duration:.4, yoyo:true, repeat:5}}, {T["cta"] + .5:.2f});')
sfx("impact-bass-1", T["final"], .4); sfx("sparkle", T["cta"], .3)

H.append('<div id="wm">DIGITAL BANJAARAA</div><div id="cred">Imagery: NASA Blue Marble · Boundaries: geoBoundaries (LGD); 2023 districts built from tehsils, approx.</div>')
CSS = """@font-face{font-family:Anton;src:url(assets/fonts/anton.woff2)}@font-face{font-family:Mont;font-weight:800;src:url(assets/fonts/mont800.woff2)}@font-face{font-family:Mont;font-weight:900;src:url(assets/fonts/mont900.woff2)}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#0a1418}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif}#world{position:absolute;inset:0;width:1080px;height:1920px}
#wm{position:absolute;left:0;right:0;top:200px;text-align:center;font:800 24px Mont;letter-spacing:.34em;color:rgba(255,255,255,.6);z-index:20}
#cred{position:absolute;left:40px;right:40px;top:1620px;text-align:center;font:800 18px Mont;color:rgba(255,255,255,.6);z-index:20}
#hook{position:absolute;left:0;right:0;top:300px;text-align:center;opacity:0;z-index:8}#hook b{display:inline-block;padding:18px 30px;border-radius:24px;background:rgba(8,12,16,.85);font:400 92px/1.02 Anton;color:#fff}
#fifty{position:absolute;left:0;right:0;top:900px;text-align:center;opacity:0;z-index:8}#fifty span{display:inline-block;font:400 260px/1 Anton;color:#fff;text-shadow:0 10px 40px #000}
#fifty i{position:absolute;left:330px;right:330px;top:120px;height:26px;background:#FF3246;transform:rotate(-12deg);transform-origin:0 50%}
#fifty b{display:block;margin-top:-10px;font:400 120px Anton;color:#FF3246;text-shadow:0 6px 24px #000}
#cnt{position:absolute;left:60px;right:60px;top:330px;opacity:0;display:flex;flex-wrap:wrap;justify-content:center;gap:20px;z-index:8}
#cnt div{flex:1;padding:20px 0;border-radius:24px;background:rgba(8,12,16,.88);text-align:center}#cnt b{display:block;font:400 170px/1 Anton;color:#FFC42E}#cnt span{font:900 36px Mont;color:#fff;letter-spacing:.12em}
#cnt em{width:100%;text-align:center;font-style:normal;font:800 26px Mont;color:#fff;text-shadow:0 2px 8px #000}
.tag{position:absolute;left:50px;top:262px;padding:10px 26px;border-radius:40px;background:#FFC42E;color:#111;font:400 50px/1 Anton;opacity:0;z-index:8}
.dvl{position:absolute;opacity:0;translate:-50% -50%;padding:6px 16px;border-radius:14px;background:rgba(8,12,16,.82);font:400 44px/1 Anton;color:#fff;letter-spacing:.03em;white-space:nowrap;z-index:6}
.head{position:absolute;left:50px;right:50px;top:255px;display:flex;align-items:center;gap:16px;padding:10px 22px 10px 10px;border-radius:40px;background:rgba(8,12,16,.9);border:3px solid;font:400 54px/1 Anton;color:#fff;opacity:0;z-index:8}
.head b{padding:8px 16px;border-radius:30px;color:#111;font:400 40px/1 Anton}.head span{margin-left:auto;font:900 26px Mont;letter-spacing:.08em;color:#ccd}
.dsl{position:absolute;opacity:0;translate:-50% -50%;text-align:center;font:900 30px/1.05 Mont;color:#111;text-shadow:0 0 6px rgba(255,255,255,.9),0 0 2px #fff;white-space:nowrap;z-index:5}
.dsl em{display:block;margin:4px auto 0;width:max-content;padding:2px 8px;border-radius:8px;background:#111;color:#FFC42E;font-style:normal;font:900 15px Mont;text-shadow:none;letter-spacing:.06em}
.lst{position:absolute;left:50px;right:50px;top:1360px;opacity:0;display:flex;flex-wrap:wrap;gap:10px 14px;padding:16px 18px;border-radius:24px;background:rgba(8,12,16,.88);border:3px solid;z-index:8}
.lst p{display:flex;align-items:center;gap:8px;font:900 30px Mont;color:#fff;opacity:0}.lst p b{width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font:900 20px Mont;color:#111}
#fin{position:absolute;left:0;right:0;top:300px;text-align:center;opacity:0;font:400 66px Anton;color:#fff;text-shadow:0 4px 20px #000;z-index:8}#fin b{color:#FFC42E;font-size:96px}
#cta{position:absolute;left:50px;right:50px;top:1380px;opacity:0;text-align:center;z-index:9}#cta b{display:block;padding:20px;border-radius:24px;background:#FFC42E;color:#111;font:400 64px/1.05 Anton}
#cta span{display:inline-block;margin-top:14px;padding:12px 30px;border-radius:30px;background:#FF3246;color:#fff;font:900 40px Mont}"""
open(f"{P}/index.html", "w").write(f"""<!doctype html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="30">
<svg id="world" viewBox="{vb(ALLC, ALLW * 1.35)}" preserveAspectRatio="xMidYMid slice">{"".join(SVG)}</svg>
{"".join(H)}
<audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.5" data-fade-out="1.5"></audio>
{"".join(SFX)}
</div><script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(J)}
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>""")
print("END", END, {k: round(v[0], 1) for k, v in DT.items()})
