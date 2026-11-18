"""SkyDome Jaipur reel: procedural 3D dome on canvas + map scenes. Locations approximate."""
import json, os, math
P = "proj"
LINES = [
    "Duniya ka teesra sabse bada immersive dome ab Jaipur mein hai.",
    "Naam hai SkyDome, Delhi road par Kukas mein.",
    "60 meter chauda, 21 meter ooncha, andar 5,000 se zyada log.",
    "17 laser projectors se poora dome kabhi mahal, kabhi galaxy ban jaata hai.",
    "Shaadiyan, concerts, bade events, sab yahin.",
    "Aas-paas Fairmont, Leela, Le Meridien, Taj Amer.",
    "Delhi road par pehle stadium, ab SkyDome. Jahan events, wahan zameen ki demand. Aap jaoge? Comment karo.",
]
VOICE = os.path.exists("rec/phrases.json")
if VOICE: PH = json.load(open("rec/phrases.json"))
else:
    PH = []; t = .2
    for l in LINES:
        d = len(l) / 16 + .2 + (.4 if not PH else 0); PH.append({"s": round(t, 2), "e": round(t + d, 2), "t": l}); t += d + .25
def S(k): return PH[k]["s"]
def E(k): return PH[k]["e"]
def wt(k, w):
    t = PH[k]["t"]; i = t.lower().find(w.lower()); assert i >= 0, (k, w)
    if PH[k].get("parts"):
        off = 0
        for p in PH[k]["parts"]:
            if i < off + len(p["t"]) + 1: return p["s"] + (p["e"] - p["s"]) * (i - off) / len(p["t"])
            off += len(p["t"]) + 1
    return S(k) + (E(k) - S(k)) * i / len(t)
END = round(E(6) + 1.0, 2)
H, J, SFX = [], [], []
def sfx(n, t, v=.3): SFX.append(f'<audio id="sx{len(SFX)}" class="clip" src="assets/sfx/{n}.mp3" data-start="{max(0, t):.2f}" data-duration="2" data-track-index="{20 + len(SFX)}" data-volume="{v}"></audio>')
def inn(sel, t, frm="opacity:0, y:40, scale:.95", ease="back.out(1.6)", d=.4):
    J.append(f'tl.set("{sel}", {{opacity:0}}, 0); tl.fromTo("{sel}", {{{frm}}}, {{opacity:1, x:0, y:0, scale:1, rotation:0, duration:{d}, ease:"{ease}", immediateRender:false}}, {t:.2f});')
def out(sel, t, d=.3): J.append(f'tl.to("{sel}", {{opacity:0, duration:{d}}}, {t - d:.2f});')

# ---------- dome keyframes (time, value) ----------
MAP1 = (S(1) - .15, S(2) - .1)          # map scene 1
MAP2 = (S(5) - .15, END)                # map scene 2 (hotels + delhi road)
KF = {
    "alpha": [(0, 1), (MAP1[0], 1), (MAP1[0] + .3, 0), (MAP1[1] - .3, 0), (MAP1[1], 1), (MAP2[0], 1), (MAP2[0] + .3, 0)],
    "rise":  [(0, .05), (.7, 1)],
    "wire":  [(0, 1), (.9, 1), (1.5, 0), (S(2) + .2, 0), (S(2) + .5, 1), (E(2) - .3, 1), (E(2), 0)],
    "R":     [(0, 400), (S(1), 380), (S(2), 300), (S(3), 360), (S(4), 300), (S(5), 300)],
    "cy":    [(0, 1180), (S(2), 1180), (S(3), 1120), (S(4), 1250)],
    "pitch": [(0, .42), (S(1), .30), (S(2), .18), (S(3), .55), (S(4), .30)],
    "beams": [(0, .6), (1.2, 1), (S(1), 1), (S(2), .2), (S(3) - .2, .2), (S(3) + .2, 1), (S(4), 1), (S(5), .6)],
    "mode":  [(0, 1), (.9, 1), (1.6, 2), (2.6, 2), (3.2, 3), (S(1), 3), (S(2), 0), (wt(3, "mahal") - .2, 0), (wt(3, "mahal") + .2, 1), (wt(3, "galaxy") - .2, 1), (wt(3, "galaxy") + .2, 3), (S(4), 3), (S(4) + .6, 2), (E(4), 2)],
}
# modes: 0 white shell, 1 mahal (palace), 2 peacock, 3 galaxy

# ---------- map ----------
def wp(lat, lon):
    n = 2 ** 13
    return (((lon + 180) / 360 * n) - 5791) * 256, (((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n) - 3466) * 256
MX0, MY0 = 5376, -3072   # map image world origin; image px = world * .5
def mp(lat, lon): x, y = wp(lat, lon); return (x - MX0) * .5, (y - MY0) * .5
SKY = mp(27.031, 75.889); AMER = mp(26.9855, 75.8513); JPR = mp(26.9124, 75.7873); CHP = mp(27.1122, 75.8253)
DLR = [mp(*p) for p in [(26.9124, 75.7873), (26.99, 75.83), (27.03, 75.885), (27.06, 75.86), (27.10, 75.845), (27.13, 75.86)]]
HOT = [("ITC MEMENTOS", (27.034, 75.893)), ("FAIRMONT", (27.026, 75.897)), ("LE MERIDIEN", (27.044, 75.880)), ("THE LEELA", (26.995, 75.862)), ("TAJ AMER", (26.985, 75.870))]
def pd(pts): return "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
HOFF = {"ITC MEMENTOS": (-170, -10), "FAIRMONT": (190, 60), "LE MERIDIEN": (-60, -110), "THE LEELA": (-150, 0), "TAJ AMER": (140, 20)}
pins = "".join(f'<div class="hp cs" id="hp{i}" style="left:{mp(*ll)[0]:.0f}px;top:{mp(*ll)[1]:.0f}px"><i></i><b style="transform:translate({HOFF[n][0]}px,{HOFF[n][1]}px)">{n}</b></div>' for i, (n, ll) in enumerate(HOT))
H.append(f'''<div id="mapw"><div id="map" style="width:2304px;height:2048px"><img src="assets/img/map.jpg"/>
<svg viewBox="0 0 2304 2048"><path id="dlr" d="{pd(DLR)}" pathLength="1"/></svg>
<div class="mk cs" id="mjpr" style="left:{JPR[0]:.0f}px;top:{JPR[1]:.0f}px"><i></i><b>JAIPUR</b></div>
<div class="mk cs" id="mamer" style="left:{AMER[0]:.0f}px;top:{AMER[1]:.0f}px"><i></i><b>AMER FORT</b></div>
<div class="mk st cs" id="mchp" style="left:{CHP[0]:.0f}px;top:{CHP[1]:.0f}px"><i></i><b>STADIUM &middot; CHONP</b></div>
<div class="dpin cs" id="dpin" style="left:{SKY[0]:.0f}px;top:{SKY[1]:.0f}px"><div class="mini"></div><b>SKYDOME &middot; KUKAS</b></div>
{pins}<div class="rlab cs" id="rlab" style="left:{(DLR[1][0] + DLR[2][0]) / 2 - 40:.0f}px;top:{(DLR[1][1] + DLR[2][1]) / 2:.0f}px">DELHI ROAD &middot; NH-48</div></div></div>''')
def mxy(c, sc):
    x = min(0, max(1080 - 2304 * sc, 540 - c[0] * sc)); y = min(0, max(1920 - 2048 * sc, 860 - c[1] * sc)); return x, y
def mapcam(t, c, sc, d=1.0):
    x, y = mxy(c, sc)
    J.append(f'tl.to("#map", {{x:{x:.0f}, y:{y:.0f}, scale:{sc}, duration:{d}, ease:"power2.inOut", onUpdate:CS}}, {t:.2f});')
J.append('function CS(){ const k = 1 / gsap.getProperty("#map", "scale"); document.querySelectorAll("#map .cs").forEach(e => e.style.scale = k); }')
J.append(f'tl.set("#map", {{transformOrigin:"0 0", x:{mxy(JPR, 1.0)[0]:.0f}, y:{mxy(JPR, 1.0)[1]:.0f}, scale:1.0, onComplete:CS}}, 0); tl.set("#mapw", {{opacity:0}}, 0); tl.set("#dlr", {{strokeDashoffset:1}}, 0); tl.set(".mk, .dpin, .hp, #rlab", {{opacity:0}}, 0);')
# map scene 1
J.append(f'tl.to("#mapw", {{opacity:1, duration:.35}}, {MAP1[0]:.2f}); tl.to("#mapw", {{opacity:0, duration:.3}}, {MAP1[1] - .3:.2f});')
mapcam(MAP1[0] - .05, ((JPR[0] + SKY[0]) / 2, (JPR[1] + SKY[1]) / 2), 1.0, .01)
J.append(f'tl.to("#dlr", {{strokeDashoffset:0, duration:.9, ease:"power2.out"}}, {MAP1[0] + .1:.2f}); tl.to("#mjpr, #rlab", {{opacity:1, duration:.3}}, {MAP1[0] + .2:.2f});')
mapcam(wt(1, "Kukas") - .5, SKY, 1.9, .9)
J.append(f'tl.to("#mamer", {{opacity:1, duration:.3}}, {wt(1, "Kukas") - .1:.2f}); tl.fromTo("#dpin", {{opacity:0, scale:.3}}, {{opacity:1, scale:1, duration:.4, ease:"back.out(2.5)", immediateRender:false}}, {wt(1, "Kukas") + .1:.2f});')
sfx("whoosh", MAP1[0], .3); sfx("pop", wt(1, "Kukas") + .1, .35)
# map scene 2: hotels then delhi road + stadium
J.append(f'tl.to("#mapw", {{opacity:1, duration:.35}}, {MAP2[0]:.2f}); tl.set(".hp", {{opacity:0}}, {MAP2[0]:.2f}); tl.set("#dpin, #mamer", {{opacity:1}}, {MAP2[0]:.2f});')
mapcam(MAP2[0] - .05, (SKY[0] - 60, SKY[1] + 40), 2.2, .01)
for i, (n, ll) in enumerate(HOT):
    kw = {"ITC MEMENTOS": None, "FAIRMONT": "Fairmont", "LE MERIDIEN": "Meridien", "THE LEELA": "Leela", "TAJ AMER": "Taj"}[n]
    t_ = wt(5, kw) - .1 if kw else S(5) + .1
    J.append(f'tl.fromTo("#hp{i}", {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:.3, ease:"back.out(2.5)", immediateRender:false}}, {t_:.2f});'); sfx("click-soft", t_, .3)
J.append(f'tl.to(".hp", {{opacity:0, duration:.3}}, {S(6) - .1:.2f});')
mapcam(S(6) - .2, ((JPR[0] + SKY[0]) / 2 + 60, (JPR[1] + CHP[1]) / 2 + 200), 1.25, 1.0)
J.append(f'tl.fromTo("#mchp", {{opacity:0, scale:.4}}, {{opacity:1, scale:1, duration:.4, ease:"back.out(2.5)", immediateRender:false}}, {wt(6, "stadium") - .1:.2f}); tl.to("#dpin", {{scale:1.35, duration:.3, yoyo:true, repeat:3}}, {wt(6, "ab SkyDome") - .1:.2f});')
sfx("impact-bass-1", wt(6, "stadium"), .35); sfx("impact-bass-1", wt(6, "ab SkyDome"), .35)

# ---------- overlays ----------
H.append('<div id="hk1">DUNIYA KA <b>3RD</b> SABSE BADA</div><div id="hk2">IMMERSIVE DOME</div><div id="hk3">AB <b>JAIPUR</b> MEIN</div>')
J.append('tl.set("#hk1, #hk2, #hk3", {opacity:0}, 0);')
inn("#hk1", .05, "opacity:0, scale:1.6", "power4.out", .3); inn("#hk2", wt(0, "immersive") - .1, "opacity:0, y:30", "power3.out", .3); inn("#hk3", wt(0, "Jaipur") - .15, "opacity:0, scale:1.8", "power4.out", .3)
out("#hk1, #hk2, #hk3", S(1) + .05)
sfx("impact-bass-1", .05, .5); sfx("riser", .3, .25); sfx("impact-bass-1", wt(0, "Jaipur") - .1, .45)
# size
H.append('<svg id="dims" viewBox="0 0 1080 1920"><line id="dw" x1="240" y1="1290" x2="840" y2="1290"/><line id="dh" x1="900" y1="1290" x2="900" y2="1000"/></svg>'
         '<div class="dl" id="dlw" style="left:540px;top:1340px">60 METER</div><div class="dl" id="dlh" style="left:960px;top:1130px">21 M</div>'
         '<div id="cap"><b class="cn">0</b><span>+ MEHMAAN</span></div>')
J.append('tl.set("#dims line", {strokeDashoffset:1}, 0); tl.set("#dims, #dlw, #dlh, #cap", {opacity:0}, 0);')
J.append(f'tl.to("#dims", {{opacity:1, duration:.2}}, {S(2):.2f}); tl.to("#dw", {{strokeDashoffset:0, duration:.5}}, {wt(2, "60") - .1:.2f}); tl.to("#dh", {{strokeDashoffset:0, duration:.5}}, {wt(2, "21") - .1:.2f}); tl.to("#dims", {{opacity:0, duration:.3}}, {S(3) - .1:.2f});')
inn("#dlw", wt(2, "60") + .1, "opacity:0, y:20", "back.out(2)", .3); out("#dlw", S(3)); inn("#dlh", wt(2, "21") + .1, "opacity:0, x:20", "back.out(2)", .3); out("#dlh", S(3))
inn("#cap", wt(2, "5,000") - .2, "opacity:0, scale:.6", "back.out(2)", .35); out("#cap", S(3))
J.append(f'(function(){{ const el = document.querySelector("#cap .cn"); const o = {{v:0}}; tl.to(o, {{v:5000, duration:.8, ease:"power2.out", onUpdate:()=>{{ el.textContent = Math.round(o.v).toLocaleString("en-IN"); }}}}, {wt(2, "5,000") - .2:.2f}); }})();')
sfx("click-soft", wt(2, "60"), .3); sfx("click-soft", wt(2, "21"), .3); sfx("impact-bass-1", wt(2, "5,000"), .35)
# projectors
H.append('<div class="tag" id="t17"><b>17</b> LASER PROJECTORS &middot; 360&deg;</div><div class="ml" id="mm">MAHAL</div><div class="ml" id="mg">GALAXY</div>')
inn("#t17", S(3), "opacity:0, y:-30", "back.out(2)", .35); out("#t17", S(4))
inn("#mm", wt(3, "mahal") - .05, "opacity:0, scale:1.5", "power4.out", .3); out("#mm", wt(3, "galaxy") - .1)
inn("#mg", wt(3, "galaxy") - .05, "opacity:0, scale:1.5", "power4.out", .3); out("#mg", S(4))
sfx("whoosh", wt(3, "mahal"), .3); sfx("whoosh", wt(3, "galaxy"), .3)
# uses
for i, (txt, kw) in enumerate([("SHAADIYAN", "Shaadiyan"), ("CONCERTS", "concerts"), ("BADE EVENTS", "bade events")]):
    H.append(f'<div class="use" id="u{i}" style="top:{330 + i * 140}px">{txt}</div>')
    inn(f"#u{i}", wt(4, kw) - .1, "opacity:0, x:-200", "back.out(1.8)", .35); out(f"#u{i}", S(5)); sfx("pop", wt(4, kw), .3)
# end
H.append('<div id="eq"><span>STADIUM</span><i>+</i><span>SKYDOME</span></div><div id="dem">JAHAN EVENTS &rarr; WAHAN <b>ZAMEEN KI DEMAND</b></div><div id="cm">AAP JAOGE? <b>COMMENT KARO</b></div>')
inn("#eq", wt(6, "stadium") - .1, "opacity:0, y:-30", "back.out(2)", .35)
inn("#dem", wt(6, "Jahan") - .1, "opacity:0, y:30", "back.out(2)", .35)
inn("#cm", wt(6, "Aap") - .1, "opacity:0, scale:.8", "back.out(2)", .35)
J.append(f'tl.to("#cm b", {{scale:1.08, duration:.3, yoyo:true, repeat:5, display:"inline-block"}}, {wt(6, "Comment"):.2f});'); sfx("sparkle", wt(6, "Comment"), .3)

# ---------- captions ----------
HI = ["teesra sabse bada", "Jaipur", "SkyDome", "Kukas", "60 meter", "21 meter", "5,000", "17 laser", "mahal", "galaxy", "Shaadiyan", "concerts", "stadium", "zameen ki demand", "Comment"]
def hl(t):
    for h in sorted(HI, key=len, reverse=True):
        i = t.find(h)
        if i >= 0 and "<span" not in t[max(0, i - 25):i] and "span" not in t[i:i + len(h)]: t = t[:i] + '<span class="y">' + h + '</span>' + t[i + len(h):]
    return t
FLAT = [q for ph in PH for q in (ph.get("parts") or ([ph] if ph["e"] - ph["s"] >= .1 else []))]
ci = 0
for n, ph in enumerate(FLAT):
    words = ph["t"].split(); chunks = []; cur = ""
    for w_ in words:
        if cur and len(cur) + 1 + len(w_) > 22: chunks.append(cur); cur = w_
        else: cur = (cur + " " + w_).strip()
    chunks.append(cur)
    tot_ = sum(len(c) for c in chunks); t = ph["s"]; nx = FLAT[n + 1]["s"] if n + 1 < len(FLAT) else END
    for j, c in enumerate(chunks):
        d = (ph["e"] - ph["s"]) * len(c) / tot_
        a_ = max(.02, t if j else t - .04); b_ = (min(t + d + .25, nx - .08) if j == len(chunks) - 1 else t + d - .03)
        H.append(f'<div class="cp" id="cp{ci}"><div>{hl(c)}</div></div>')
        J.append(f'tl.fromTo("#cp{ci}", {{opacity:0, scale:.88}}, {{opacity:1, scale:1, duration:.1}}, {a_:.2f}); tl.to("#cp{ci}", {{opacity:0, duration:.04}}, {b_ - .04:.2f});')
        t += d; ci += 1
if os.path.exists(f"{P}/assets/face.mp4"):
    H.append('<video id="face" class="clip" src="assets/face.mp4" data-start="0" data-duration="1.0" data-track-index="2" muted playsinline></video>')
    J.append('tl.set("#face", {opacity:1}, 0); tl.to("#face", {opacity:0, scale:1.06, duration:.12}, .8);')
H.append('<div id="cred">3D dome: illustrative graphic &middot; facts: Outlook Traveller, TravTalk, OneIndia (Nov 2026) &middot; &ldquo;3rd largest&rdquo; as billed by SkyDome &middot; map locations approximate &middot; Imagery: Sentinel-2 (EOX)</div>')

DOME_JS = r"""
const CV = document.getElementById("dome"), CX = CV.getContext("2d"); const KF = __KF__;
function kv(name, t){ const k = KF[name]; if (t <= k[0][0]) return k[0][1]; for (let i = 1; i < k.length; i++){ if (t <= k[i][0]){ const a = k[i-1], b = k[i]; let u = (t - a[0]) / Math.max(1e-6, b[0] - a[0]); u = u < .5 ? 2*u*u : 1 - Math.pow(-2*u+2, 2)/2; return a[1] + (b[1] - a[1]) * u; } } return k[k.length-1][1]; }
function hash(a, b){ const s = Math.sin(a * 127.1 + b * 311.7) * 43758.5453; return s - Math.floor(s); }
const STARS = Array.from({length: 160}, (_, i) => [hash(i, 1) * 1080, hash(i, 2) * 1100, hash(i, 3)]);
function modeCol(m, lon, lat, t){
  if (m === 0){ const g = 200 + 40 * lat; return [g - 10, g, g + 25]; }
  if (m === 1){ // mahal: gold/red bands with arches + jali + rosette
    const L = lat / (Math.PI/2);
    if (L < .32){ const a = Math.sin(lon * 18); const arch = (a > .2 && L > .05 + .2 * (1 - a)) ? 1 : 0; return arch ? [250, 225, 170] : [175, 30, 45]; }
    if (L < .62){ const j = (Math.sin(lon * 40) * Math.sin(L * 60) > .3) ? 1 : 0; return j ? [235, 175, 40] : [120, 20, 60]; }
    const r = Math.sin((1 - L) * 40 + t * 2) > 0 ? 1 : 0; const sp = Math.sin(lon * 12) > .6 ? 1 : 0; return r ? (sp ? [30, 140, 160] : [240, 190, 60]) : [190, 40, 90];
  }
  if (m === 2){ // peacock swirls
    const h = Math.sin(lon * 6 + lat * 9 - t * 1.5), e = Math.sin(lon * 22 + lat * 14 + t);
    const gold = Math.max(0, e - .6) * 2.5;
    return [20 + 40 * (1 + h) + 200 * gold, 90 + 70 * (1 + h) / 2 + 120 * gold, 150 + 60 * (1 - h) / 2 - 60 * gold];
  }
  // galaxy
  const neb = Math.sin(lon * 3 + lat * 5 + t * .6) * Math.sin(lon * 5 - lat * 4);
  return [40 + 120 * Math.max(0, neb), 20 + 30 * Math.max(0, neb), 80 + 110 * (.5 + .5 * neb)];
}
function draw(t){
  CX.clearRect(0, 0, 1080, 1920);
  const A = kv("alpha", t); if (A <= .01) return;
  CX.globalAlpha = A;
  // sky
  const sg = CX.createLinearGradient(0, 0, 0, 1500); sg.addColorStop(0, "#05030f"); sg.addColorStop(.6, "#140a2a"); sg.addColorStop(1, "#2a1230"); CX.fillStyle = sg; CX.fillRect(0, 0, 1080, 1920);
  for (const s of STARS){ CX.fillStyle = `rgba(255,255,255,${.25 + .6 * Math.abs(Math.sin(t * 2 + s[2] * 9))})`; CX.fillRect(s[0], s[1], 2, 2); }
  const R = kv("R", t), cy = kv("cy", t), cx = 540, p = kv("pitch", t), rise = kv("rise", t), wire = kv("wire", t), beams = kv("beams", t), mv = kv("mode", t);
  const yaw = t * .35;
  // ground
  const gg = CX.createRadialGradient(cx, cy, 10, cx, cy, R * 2.2); gg.addColorStop(0, "rgba(255,140,60,.35)"); gg.addColorStop(1, "rgba(0,0,0,0)");
  CX.fillStyle = "#0b0712"; CX.fillRect(0, cy, 1080, 1920 - cy); CX.save(); CX.translate(cx, cy); CX.scale(1, Math.sin(p) + .05); CX.fillStyle = gg; CX.beginPath(); CX.arc(0, 0, R * 2.2, 0, Math.PI * 2); CX.fill(); CX.restore();
  // beams (behind)
  CX.globalCompositeOperation = "lighter";
  for (let i = 0; i < 17; i++){ const a = i / 17 * Math.PI * 2 + yaw * .3; const bx = cx + Math.cos(a) * R * 1.25, by = cy + Math.sin(a) * R * 1.25 * Math.sin(p);
    if (Math.sin(a) > 0) continue; const sw = Math.sin(t * 1.3 + i) * .35; const ex = bx + Math.sin(sw + (bx - cx) / 600) * 1400, ey = by - 1500;
    const bg = CX.createLinearGradient(bx, by, ex, ey); bg.addColorStop(0, `rgba(190,215,255,${.55 * beams})`); bg.addColorStop(1, "rgba(190,215,255,0)");
    CX.strokeStyle = bg; CX.lineWidth = 7; CX.beginPath(); CX.moveTo(bx, by); CX.lineTo(ex, ey); CX.stroke(); }
  CX.globalCompositeOperation = "source-over";
  // dome mesh
  const NL = 112, NA = 30, quads = [];
  const P3 = (lon, lat) => { const x = R * Math.cos(lat) * Math.cos(lon), z = R * Math.cos(lat) * Math.sin(lon), y = R * Math.sin(lat) * rise; const x1 = x * Math.cos(yaw) - z * Math.sin(yaw), z1 = x * Math.sin(yaw) + z * Math.cos(yaw); return [cx + x1, cy - y * Math.cos(p) + z1 * Math.sin(p), z1 * Math.cos(p) + y * Math.sin(p)]; };
  const m0 = Math.floor(mv), m1 = Math.min(3, m0 + 1), f = mv - m0;
  for (let i = 0; i < NL; i++) for (let j = 0; j < NA; j++){
    const l0 = i / NL * Math.PI * 2, l1 = (i + 1) / NL * Math.PI * 2, a0 = j / NA * Math.PI / 2, a1 = (j + 1) / NA * Math.PI / 2;
    const q = [P3(l0, a0), P3(l1, a0), P3(l1, a1), P3(l0, a1)]; const lc = (l0 + l1) / 2, ac = (a0 + a1) / 2;
    const nz = Math.cos(ac) * Math.sin(lc + 0) ; const d = (q[0][2] + q[1][2] + q[2][2] + q[3][2]) / 4;
    // normal depth (sphere normal = position dir)
    const nx = Math.cos(ac) * Math.cos(lc), nzz = Math.cos(ac) * Math.sin(lc), ny = Math.sin(ac);
    const nz1 = nx * Math.sin(yaw) + nzz * Math.cos(yaw); const nd = nz1 * Math.cos(p) + ny * Math.sin(p);
    if (nd < -0.02) continue;
    quads.push([d, q, lc - yaw * 0, ac, nd]);
  }
  quads.sort((a, b) => a[0] - b[0]);
  for (const [d, q, lc, ac, nd] of quads){
    const c0 = modeCol(m0, lc, ac, t), c1 = modeCol(m1, lc, ac, t); const sh = .55 + .45 * nd; const glow = 1 - wire;
    const c = [0,1,2].map(k => Math.min(255, (c0[k] * (1 - f) + c1[k] * f) * sh));
    CX.beginPath(); CX.moveTo(q[0][0], q[0][1]); for (let k = 1; k < 4; k++) CX.lineTo(q[k][0], q[k][1]); CX.closePath();
    if (glow > .01){ CX.fillStyle = `rgba(${c[0]|0},${c[1]|0},${c[2]|0},${glow})`; CX.fill(); CX.strokeStyle = CX.fillStyle; CX.lineWidth = 1.2; CX.stroke(); }
    if (wire > .01){ CX.strokeStyle = `rgba(150,230,255,${.85 * wire})`; CX.lineWidth = 1.6; CX.stroke(); }
  }
  // galaxy stars on dome
  const gw = m0 === 3 ? 1 - f : (m1 === 3 ? f : 0);
  if (gw > .02 && wire < .5){ CX.fillStyle = `rgba(255,255,255,${gw})`;
    for (let i = 0; i < 260; i++){ const lo = hash(i, 7) * Math.PI * 2, la = hash(i, 9) * 1.45; const nx = Math.cos(la) * Math.cos(lo), nzz = Math.cos(la) * Math.sin(lo), ny = Math.sin(la); const nz1 = nx * Math.sin(yaw) + nzz * Math.cos(yaw); if (nz1 * Math.cos(p) + ny * Math.sin(p) < 0) continue;
      const q = P3(lo, la); const sz = 1.5 + 2.5 * hash(i, 11) * (.6 + .4 * Math.sin(t * 3 + i)); CX.beginPath(); CX.arc(q[0], q[1], sz, 0, Math.PI * 2); CX.fill(); } }
  // rim light + entrance
  CX.globalCompositeOperation = "lighter"; CX.strokeStyle = "rgba(255,200,140,.35)"; CX.lineWidth = 5; CX.save(); CX.translate(cx, cy); CX.scale(1, Math.sin(p) + .02); CX.beginPath(); CX.arc(0, 0, R, 0, Math.PI); CX.stroke(); CX.restore(); CX.globalCompositeOperation = "source-over";
  const ew = R * .18, eh = R * .28 * rise; CX.fillStyle = "rgba(255,225,170,.9)"; CX.fillRect(cx - ew / 2, cy + R * Math.sin(p) - eh, ew, eh);
  CX.globalAlpha = 1;
}
"""

CSS = """@font-face{font-family:Anton;src:url(assets/fonts/anton.woff2)}@font-face{font-family:Mont;font-weight:700;src:url(assets/fonts/mont700.woff2)}@font-face{font-family:Mont;font-weight:800;src:url(assets/fonts/mont800.woff2)}@font-face{font-family:Mont;font-weight:900;src:url(assets/fonts/mont900.woff2)}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#05030f}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif;background:#05030f}
.y{color:#111;background:#FFC93C;border-radius:6px;padding:0 6px}
#face{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:40}
#dome{position:absolute;inset:0;z-index:2}
#mapw{position:absolute;inset:0;overflow:hidden;z-index:3;opacity:0;background:#05030f}#map{position:absolute;left:0;top:0}#map img{display:block;width:2304px;height:2048px;filter:saturate(1.1) brightness(.8)}
#map svg{position:absolute;inset:0;width:2304px;height:2048px}#dlr{fill:none;stroke:#FFC93C;stroke-width:14;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1;filter:drop-shadow(0 0 10px #FFC93C)}
.mk{position:absolute;translate:-50% -50%;transform-origin:50% 50%;display:flex;flex-direction:column;align-items:center;gap:6px}.mk i{width:20px;height:20px;border-radius:50%;background:#fff;border:4px solid #111}.mk b{padding:5px 14px;border-radius:6px;background:rgba(5,3,15,.9);color:#fff;font:900 26px Mont;letter-spacing:.06em;white-space:nowrap}
.mk.st b{background:#FFC93C;color:#111}
.dpin{position:absolute;width:0;height:0}.dpin .mini{position:absolute;left:-60px;top:-60px;width:120px;height:60px;border-radius:120px 120px 0 0;background:radial-gradient(circle at 50% 100%,#ff5aa8,#8a3cff 55%,#2a0a5a);box-shadow:0 0 40px #ff5aa8}.dpin b{position:absolute;left:0;top:-120px;translate:-50% -50%;padding:6px 16px;border-radius:8px;background:linear-gradient(90deg,#ff5aa8,#8a3cff);color:#fff;font:900 30px Mont;letter-spacing:.06em;white-space:nowrap}
.hp{position:absolute;width:0;height:0}.hp i{position:absolute;left:-12px;top:-12px;width:24px;height:24px;border-radius:50%;background:#FFC93C;border:4px solid #111}.hp b{position:absolute;left:0;top:0;translate:-50% -50%;padding:6px 14px;border-radius:8px;background:#fff;color:#111;font:900 30px Mont;white-space:nowrap;box-shadow:0 6px 18px rgba(0,0,0,.5)}
.rlab{position:absolute;rotate:28deg;padding:4px 12px;border-radius:6px;background:#FFC93C;color:#111;font:900 24px Mont;white-space:nowrap}
#hk1,#hk2,#hk3{position:absolute;left:0;right:0;text-align:center;z-index:10;text-shadow:0 6px 30px rgba(0,0,0,.8)}
#hk1{top:150px;font:800 54px Mont;color:#fff;letter-spacing:.04em}#hk1 b{font:400 86px Anton;color:#FFC93C}
#hk2{top:285px;font:400 120px/1 Anton;background:linear-gradient(180deg,#fff,#ffb3e0 60%,#b28cff);-webkit-background-clip:text;color:transparent}
#hk3{top:430px;font:800 56px Mont;color:#fff}#hk3 b{font:400 96px Anton;color:#FFC93C}
#dims{position:absolute;inset:0;width:1080px;height:1920px;z-index:6}#dims line{stroke:#fff;stroke-width:4;stroke-dasharray:1;stroke-dashoffset:1}#dims line{stroke-dasharray:1;}
.dl{position:absolute;translate:-50% -50%;z-index:7;padding:6px 18px;border-radius:8px;background:#FFC93C;color:#111;font:400 54px Anton}
#cap{position:absolute;left:0;right:0;top:260px;margin:0 auto;width:max-content;z-index:7;text-align:center;padding:16px 40px;border-radius:16px;background:rgba(5,3,15,.85);border:2px solid #ff5aa8}#cap b{font:400 120px/1 Anton;color:#fff}#cap span{display:block;font:900 32px Mont;color:#ffb3e0;letter-spacing:.1em}
.tag{position:absolute;left:0;right:0;top:200px;margin:0 auto;width:max-content;z-index:7;padding:12px 30px;border-radius:12px;background:rgba(5,3,15,.85);border:2px solid #b28cff;color:#fff;font:900 40px Mont}.tag b{font:400 70px Anton;color:#FFC93C}
.ml{position:absolute;left:0;right:0;top:340px;margin:0 auto;width:max-content;z-index:7;font:400 150px/1 Anton;color:#fff;letter-spacing:.05em;text-shadow:0 0 40px #ff5aa8,0 8px 30px #000}
.use{position:absolute;left:70px;z-index:7;padding:16px 34px;border-radius:14px;background:linear-gradient(90deg,#ff5aa8,#8a3cff);color:#fff;font:400 80px/1 Anton;letter-spacing:.04em;box-shadow:0 12px 40px rgba(0,0,0,.6)}
#eq{position:absolute;left:0;right:0;top:1040px;margin:0 auto;width:max-content;z-index:7;display:flex;gap:20px;align-items:center;padding:14px 30px;border-radius:14px;background:rgba(5,3,15,.9)}#eq span{font:400 70px Anton;color:#fff}#eq i{font:400 70px Anton;font-style:normal;color:#FFC93C}
#dem{position:absolute;left:50px;right:50px;top:1180px;z-index:7;text-align:center;padding:16px;border-radius:14px;background:rgba(5,3,15,.9);color:#fff;font:900 40px Mont}#dem b{color:#FFC93C}
#cm{position:absolute;left:0;right:0;top:1300px;margin:0 auto;width:max-content;z-index:7;color:#fff;font:900 46px Mont}#cm b{padding:6px 18px;border-radius:10px;background:#ff5aa8}
#cred{position:absolute;left:30px;right:30px;top:1700px;text-align:center;font:700 16px Mont;color:rgba(255,255,255,.55);z-index:20}
.cp{position:absolute;left:40px;right:40px;top:1480px;text-align:center;opacity:0;z-index:35}
.cp div{display:inline-block;padding:4px 20px 8px;border-radius:10px;background:#fff;font:900 60px/1.12 Mont;color:#111;box-shadow:0 8px 24px rgba(0,0,0,.45)}"""
audio = (f'<audio id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{END}" data-track-index="1" data-volume="1"></audio><audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.14" data-fade-out="1.5"></audio>' if VOICE
         else f'<audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.6" data-fade-out="1.5"></audio>')
html = f"""<!doctype html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="30">
<canvas id="dome" width="1080" height="1920"></canvas>
{"".join(H)}
{audio}
{"".join(SFX)}
</div><script>
{DOME_JS.replace("__KF__", json.dumps(KF))}
document.querySelectorAll("#dims line").forEach(l => l.setAttribute("pathLength", "1"));
const tl = gsap.timeline({{ paused: true }});
const DT = {{t:0}}; tl.to(DT, {{t:{END}, duration:{END}, ease:"none", onUpdate:()=>draw(DT.t)}}, 0); draw(0);
{chr(10).join(J)}
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>"""
open(f"{P}/index.html", "w").write(html)
print("END", END, [p["s"] for p in PH])
