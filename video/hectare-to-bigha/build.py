"""Hectare -> pakka / kaccha bigha + biswa. Rajasthan neon district map. Jamabandi is a SAMPLE."""
import json, os, math
P = "proj"
LINES = [
    "Jamabandi mein zameen hectare mein likhi hoti hai. Lekin Rajasthan mein bigha har jagah alag hota hai. Aaj dono tarah ka hisaab seekhiye.",
    "Rajasthan mein do tarah ke bigha chalte hain: pakka, yaani bada bigha, aur kaccha, yaani chhota bigha.",
    "Pakka bigha 165 foot guna 165 foot hota hai. Yaani 3,025 gaj, ya lagbhag 0.253 hectare.",
    "Kaccha bigha 132 foot guna 132 foot hota hai. Yaani 1,936 gaj, ya lagbhag 0.162 hectare.",
    "Aapke ilaake mein kaunsa bigha chalta hai? Pakka ya kaccha? Comment mein apna zila zaroor likhiye.",
    "Formula simple hai: hectare ko pakke ke liye 0.253 se, aur kacche ke liye 0.162 se bhaag dijiye. Jo poora number aaye wo bigha, aur dashamlav ko 20 se guna kariye, wo biswa.",
    "Ab example. Maan lijiye Jamabandi mein aapki zameen 2 hectare hai.",
    "Pakka bigha ke liye 2 ko 0.253 se bhaag dijiye: 7.9. Yaani 7 bigha poore.",
    "Bacha hua 0.9, isko 20 se guna kariye, kyunki ek bigha mein 20 biswa hote hain: 18 biswa. Yaani 7 bigha 18 biswa.",
    "Kaccha bigha ke liye 2 ko 0.162 se bhaag dijiye: 12.35. Yaani 12 bigha, aur 0.35 guna 20, lagbhag 7 biswa. Yaani 12 bigha 7 biswa.",
    "Dekha? Zameen wahi, lekin pakke mein 7 bigha aur kacche mein 12 bigha. Isliye sauda karne se pehle hamesha poochhiye, kaunsa bigha.",
    "Video save kar lijiye, aur gaon ke group mein share kariye.",
]
VOICE = os.path.exists("rec/phrases.json")
if VOICE: PH = json.load(open("rec/phrases.json"))
else:
    PH = []; t = .3
    for l in LINES:
        d = len(l) / 16 + .3 + (.6 if not PH else 0); PH.append({"s": round(t, 2), "e": round(t + d, 2), "t": l}); t += d + .3
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
END = round(E(11) + 1.0, 2)
H, J, SFX = [], [], []
def sfx(n, t, v=.3): SFX.append(f'<audio id="sx{len(SFX)}" class="clip" src="assets/sfx/{n}.mp3" data-start="{max(0, t):.2f}" data-duration="2" data-track-index="{20 + len(SFX)}" data-volume="{v}"></audio>')
def inn(sel, t, frm="opacity:0, y:40, scale:.95", ease="back.out(1.6)", d=.45):
    J.append(f'tl.set("{sel}", {{opacity:0}}, 0); tl.fromTo("{sel}", {{{frm}}}, {{opacity:1, x:0, y:0, scale:1, rotation:0, duration:{d}, ease:"{ease}", immediateRender:false}}, {t:.2f});')
def out(sel, t, d=.3): J.append(f'tl.to("{sel}", {{opacity:0, duration:{d}}}, {t - d:.2f});')
exec(open("fake.py").read())
def bgp(bid, img, t0, t1, op=.45, z0=1.0, z1=1.1, blur=0):
    H.append(f'<div class="bgp" id="{bid}"><img src="assets/img/{img}.jpg" style="{f"filter:blur({blur}px)" if blur else ""}"/></div>')
    J.append(f'tl.set("#{bid}", {{opacity:0}}, 0); tl.to("#{bid}", {{opacity:{op}, duration:.5}}, {max(0, t0):.2f}); tl.fromTo("#{bid} img", {{scale:{z0}}}, {{scale:{z1}, duration:{t1 - t0 + .5:.2f}, ease:"none", immediateRender:false}}, {max(0, t0):.2f}); tl.to("#{bid}", {{opacity:0, duration:.5}}, {t1 - .2:.2f});')

# ---------- Rajasthan neon map (shared) ----------
RM = json.load(open("rajmap.json")); MW, MH = RM["w"], RM["h"]
NEON = ["#2FA8FF"]
paths = "".join(f'<path class="dz" d="{d["d"]}" style="stroke:{NEON[0]};color:{NEON[0]}"/>' for i, d in enumerate(RM["ds"]))
qs = "".join(f'<text class="qm" x="{d["c"][0]}" y="{d["c"][1] + 14}" style="fill:{NEON[0]}">?</text>' for i, d in enumerate(RM["ds"]))
H.append(f'<div id="map"><svg viewBox="-10 -10 {MW + 20} {MH + 20}"><defs><filter id="ng" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
         f'<g filter="url(#ng)">{paths}</g><g class="qs">{qs}</g></svg></div>')
J.append('tl.set("#map", {opacity:0}, 0); tl.set("#map .dz", {strokeDashoffset:1}, 0); tl.set("#map .qm", {opacity:0, scale:.3, transformOrigin:"50% 50%"}, 0);')
def map_on(t0, t1, draw=True, qmarks=False, y=420, sc=1.0):
    J.append(f'tl.fromTo("#map", {{opacity:0, y:{y + 40}, scale:{sc}}}, {{opacity:1, y:{y}, scale:{sc}, duration:.4, immediateRender:false}}, {t0:.2f}); tl.to("#map", {{opacity:0, duration:.3}}, {t1 - .3:.2f});')
    if draw: J.append(f'tl.fromTo("#map .dz", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:1.0, stagger:{{each:.025, from:"random"}}, ease:"power2.out", immediateRender:false}}, {t0:.2f});')
    J.append(f'tl.fromTo("#map .dz", {{fillOpacity:0}}, {{fillOpacity:.08, duration:.6, immediateRender:false}}, {t0 + 1.0:.2f});')
    if qmarks:
        J.append(f'tl.fromTo("#map .qm", {{opacity:0, scale:.3}}, {{opacity:1, scale:1, duration:.3, stagger:{{each:.04, from:"random"}}, ease:"back.out(3)", immediateRender:false}}, {t0 + .6:.2f});  tl.to("#map .qm", {{opacity:0, duration:.2}}, {t1 - .4:.2f});')
    sfx("riser", t0, .25)

H.append('<div class="qt" id="qb">बड़ा बीघा ?</div><div class="qt" id="qc">छोटा बीघा ?</div>')
J.append('tl.set("#qb, #qc", {opacity:0}, 0);')
def qtags(ta, tb, t1):
    J.append(f'tl.fromTo("#qb", {{opacity:0, scale:1.6, rotation:-6}}, {{opacity:1, scale:1, rotation:-4, duration:.35, ease:"back.out(2.5)", immediateRender:false}}, {ta:.2f}); tl.fromTo("#qc", {{opacity:0, scale:1.6, rotation:6}}, {{opacity:1, scale:1, rotation:4, duration:.35, ease:"back.out(2.5)", immediateRender:false}}, {tb:.2f}); tl.to("#qb, #qc", {{opacity:0, duration:.3}}, {t1 - .3:.2f});')
    sfx("pop", ta, .3); sfx("pop", tb, .3)
# ---------- 0 hook ----------
bgp("b0", "bg_fields", 0, S(1) + .2, op=.45, blur=2)
H.append('<div class="doc" id="d0"><div class="im"><img src="assets/img/jama_real.jpg"/>' + fake_overlay(760 / 1082) + '</div><div class="hl" id="ha">1.0300 हेक्टेयर</div></div>')
inn("#d0", .15, "opacity:0, y:120, rotation:-4"); out("#d0", wt(0, "Lekin") + .1)
J.append(f'tl.set("#ha", {{opacity:0}}, 0); tl.fromTo("#ha", {{opacity:0, scale:1.8}}, {{opacity:1, scale:1, duration:.35, ease:"power4.out", immediateRender:false}}, {wt(0, "hectare") - .1:.2f});')
H.append('<div id="hook"><small>हेक्टेयर से</small><b>कितने बीघा?</b><span>पक्का &middot; कच्चा &middot; बिस्वा</span></div>')
inn("#hook", wt(0, "Lekin") - .1, "opacity:0, scale:1.4", "power4.out", .4); out("#hook", S(1))
J.append(f'tl.to("#hook b", {{scale:1.07, duration:.3, yoyo:true, repeat:3}}, {wt(0, "Aaj"):.2f});')
sfx("impact-bass-1", 0, .4); sfx("impact-bass-1", wt(0, "Lekin"), .4)

# ---------- 1 two types ----------
map_on(wt(0, "Lekin") - .2, S(2), draw=True, y=560, sc=.95)
qtags(wt(0, "alag") - .1, wt(0, "alag") + .35, S(1) + .1)
H.append('<div class="two" id="two"><div class="pk"><b>पक्का</b><span>बड़ा बीघा</span></div><i>vs</i><div class="kc"><b>कच्चा</b><span>छोटा बीघा</span></div></div>')
inn("#two .pk", wt(1, "pakka") - .1, "opacity:0, x:-80", "back.out(2)", .35); inn("#two .kc", wt(1, "kaccha") - .1, "opacity:0, x:80", "back.out(2)", .35)
J.append(f'tl.set("#two", {{opacity:1}}, 0); tl.set("#two i", {{opacity:0}}, 0); tl.to("#two i", {{opacity:1, duration:.2}}, {wt(1, "kaccha") + .2:.2f}); tl.to("#two", {{opacity:0, duration:.3}}, {S(2) - .3:.2f});')
H.append('<div class="t1" id="t1"><b>राजस्थान में 2 तरह के बीघा</b></div>'); inn("#t1", S(1), "opacity:0, y:-30"); out("#t1", S(2))
sfx("pop", wt(1, "pakka"), .3); sfx("pop", wt(1, "kaccha"), .3)

# ---------- 2-3 squares to scale ----------
SQ = 760 / 165   # px per ft
H.append(f'<div id="sq"><div class="pq" style="width:{165 * SQ:.0f}px;height:{165 * SQ:.0f}px"><em class="w">165 ft</em><em class="h">165 ft</em><div class="lab"><b>पक्का बीघा</b><span>3,025 गज &middot; &asymp; 0.253 हेक्टेयर</span></div></div>'
         f'<div class="kq" style="width:{132 * SQ:.0f}px;height:{132 * SQ:.0f}px"><em class="w">132 ft</em><em class="h">132 ft</em><div class="lab"><b>कच्चा बीघा</b><span>1,936 गज &middot; &asymp; 0.162 हेक्टेयर</span></div></div></div>')
bgp("b2", "bg_plots", S(2) - .3, S(4) - .1, op=.35)
J.append(f'tl.set("#sq", {{opacity:0}}, 0); tl.to("#sq", {{opacity:1, duration:.3}}, {S(2) - .1:.2f}); tl.to("#sq", {{opacity:0, duration:.3}}, {S(4) - .3:.2f});'
         f'tl.set("#sq .kq, #sq .lab, #sq em", {{opacity:0}}, 0);'
         f'tl.fromTo("#sq .pq", {{scale:0, transformOrigin:"0% 100%"}}, {{scale:1, duration:.7, ease:"power3.out", immediateRender:false}}, {wt(2, "165") - .1:.2f}); tl.to("#sq .pq em", {{opacity:1, duration:.3}}, {wt(2, "165") + .3:.2f}); tl.to("#sq .pq .lab", {{opacity:1, duration:.3}}, {wt(2, "3,025") - .2:.2f});'
         f'tl.to("#sq .pq .lab", {{opacity:0, duration:.2}}, {S(3) - .1:.2f}); tl.fromTo("#sq .kq", {{scale:0, transformOrigin:"0% 100%"}}, {{opacity:1, scale:1, duration:.7, ease:"power3.out", immediateRender:false}}, {wt(3, "132") - .1:.2f}); tl.to("#sq .kq em", {{opacity:1, duration:.3}}, {wt(3, "132") + .3:.2f}); tl.to("#sq .kq .lab", {{opacity:1, duration:.3}}, {wt(3, "1,936") - .2:.2f});')
H.append('<div class="t1" id="t2"><b>पक्का / बड़ा बीघा</b></div>'); inn("#t2", S(2) - .1, "opacity:0, y:-30"); out("#t2", S(3))
H.append('<div class="t1" id="t3"><b>कच्चा / छोटा बीघा</b></div>'); inn("#t3", S(3) - .1, "opacity:0, y:-30"); out("#t3", S(4))
sfx("whoosh", wt(2, "165"), .3); sfx("whoosh", wt(3, "132"), .3)

# ---------- 4 comment: neon map + ? ----------
map_on(S(4) - .2, S(5), draw=True, qmarks=True, y=470, sc=1.0)
qtags(wt(4, "Pakka ya") - .1, wt(4, "kaccha?") - .1, S(5))
H.append('<div id="ask"><b>आपके ज़िले में कौनसा बीघा?</b><span>पक्का या कच्चा &middot; <u>कमेंट करें</u></span></div>')
inn("#ask", S(4) - .1, "opacity:0, y:-40", "back.out(1.6)", .4); out("#ask", S(5))
J.append(f'tl.to("#ask u", {{scale:1.12, duration:.3, yoyo:true, repeat:5, display:"inline-block"}}, {wt(4, "Comment"):.2f});')
sfx("sparkle", wt(4, "Comment"), .3)

# ---------- 5 general formula ----------
bgp("bF", "bg_plots", S(5) - .3, S(6) - .1, op=.3, blur=3)
H.append('<div id="fm"><small>सामान्य फ़ॉर्मूला</small>'
         '<div class="fr k0"><span>हेक्टेयर</span><i>&divide; 0.253</i><b>पक्का बीघा</b></div>'
         '<div class="fr k1"><span>हेक्टेयर</span><i>&divide; 0.162</i><b>कच्चा बीघा</b></div>'
         '<div class="fr k2"><span>पूरा अंक</span><i>=</i><b>बीघा</b></div>'
         '<div class="fr k3"><span>दशमलव</span><i>&times; 20</i><b>बिस्वा</b></div></div>')
inn("#fm", S(5) - .1, "opacity:0, y:50"); out("#fm", S(6))
for j, kw in enumerate(["pakke", "kacche", "poora", "dashamlav"]):
    J.append(f'tl.set("#fm .k{j}", {{opacity:0}}, 0); tl.fromTo("#fm .k{j}", {{opacity:0, x:-60}}, {{opacity:1, x:0, duration:.35, ease:"back.out(1.8)", immediateRender:false}}, {wt(5, kw) - .1:.2f});'); sfx("click-soft", wt(5, kw), .25)
# ---------- 5-8 calculation ----------
bgp("b5", "bg_fields", S(6) - .3, S(10) - .1, op=.3, blur=4)
H.append('<div id="g2"><small>मान लीजिए ज़मीन</small><b>2 हेक्टेयर</b></div>'); inn("#g2", S(6), "opacity:0, scale:1.5", "power4.out", .35); out("#g2", S(7))
def calc(i, t0, t1, rows, title, cls=""):
    H.append(f'<div class="calc {cls}" id="c{i}"><small>{title}</small>' + "".join(f'<div class="r tk k{j}">{r}</div>' for j, r in enumerate(rows)) + '</div>')
    J.append(f'tl.set("#c{i}", {{opacity:0}}, 0); tl.set("#c{i} .tk", {{opacity:0}}, 0); tl.fromTo("#c{i}", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:.35, immediateRender:false}}, {t0:.2f}); tl.to("#c{i}", {{opacity:0, duration:.3}}, {t1 - .3:.2f});')
def tk(i, j, t):
    J.append(f'tl.fromTo("#c{i} .k{j}", {{opacity:0, y:20, scale:.85}}, {{opacity:1, y:0, scale:1, duration:.3, ease:"back.out(2)", immediateRender:false}}, {t:.2f});'); sfx("click-soft", t, .25)
calc(1, S(7) - .1, S(9), ['2 <i>&divide;</i> 0.253 <i>=</i> <b>7.9</b>', '<span class="g">7 बीघा</span> पूरे', '0.9 <i>&times;</i> 20 <i>=</i> <b>18 बिस्वा</b>', '<span class="res">7 बीघा 18 बिस्वा</span>'], "पक्का बीघा", "pk")
tk(1, 0, wt(7, "0.253") - .1); tk(1, 1, wt(7, "7 bigha") - .1); tk(1, 2, wt(8, "20 se") - .1); tk(1, 3, wt(8, "Yaani") - .1)
H.append('<div class="note" id="n20">1 बीघा = 20 बिस्वा</div>'); inn("#n20", wt(8, "ek bigha") - .1, "opacity:0, scale:1.4", "power4.out", .3); out("#n20", S(9))
calc(2, S(9) - .1, S(10), ['2 <i>&divide;</i> 0.162 <i>=</i> <b>12.35</b>', '<span class="g">12 बीघा</span> पूरे', '0.35 <i>&times;</i> 20 <i>&asymp;</i> <b>7 बिस्वा</b>', '<span class="res">12 बीघा 7 बिस्वा</span>'], "कच्चा बीघा", "kc")
tk(2, 0, wt(9, "0.162") - .1); tk(2, 1, wt(9, "12 bigha") - .1); tk(2, 2, wt(9, "0.35") - .1); tk(2, 3, wt(9, "Yaani 12") - .1)
sfx("impact-bass-1", wt(8, "Yaani"), .35); sfx("impact-bass-1", wt(9, "Yaani 12"), .35)

# ---------- 9 comparison ----------
bgp("b9", "bg_plots", S(10) - .3, S(11) + .1, op=.4)
H.append('<div id="cmp"><small>ज़मीन वही &middot; 2 हेक्टेयर</small><div class="cc"><div class="pk"><b>7</b><span>बीघा 18 बिस्वा</span><em>पक्का</em></div><i>=</i><div class="kc"><b>12</b><span>बीघा 7 बिस्वा</span><em>कच्चा</em></div></div><div class="ask2">सौदे से पहले पूछिए: <u>कौनसा बीघा?</u></div></div>')
inn("#cmp", S(10) - .1, "opacity:0, y:60"); out("#cmp", S(11))
J.append(f'tl.set("#cmp .ask2", {{opacity:0}}, 0); tl.fromTo("#cmp .ask2", {{opacity:0, scale:.8}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)", immediateRender:false}}, {wt(10, "Isliye") - .1:.2f});')
sfx("impact-bass-1", S(10), .35)

# ---------- 10 save ----------
H.append('<div id="save"><small>सेव कर लो</small><b>हेक्टेयर &rarr; बीघा</b><div class="ch"><span>हेक्टेयर</span><i>&divide; 0.253 =</i><span class="g">पक्का बीघा</span></div><div class="ch"><span>हेक्टेयर</span><i>&divide; 0.162 =</i><span class="y">कच्चा बीघा</span></div><div class="ch"><span>दशमलव</span><i>&times; 20 =</i><span class="g">बिस्वा</span></div><div class="cta">गाँव के ग्रुप में शेयर करें</div></div>')
inn("#save", S(11) - .1, "opacity:0, y:40")
J.append(f'tl.fromTo("#save .ch", {{opacity:0, x:-40}}, {{opacity:1, x:0, duration:.3, stagger:.2, immediateRender:false}}, {S(11) + .2:.2f}); tl.to("#save .cta", {{scale:1.06, duration:.35, yoyo:true, repeat:5}}, {wt(11, "share"):.2f});')
sfx("sparkle", wt(11, "share"), .3)

# ---------- captions ----------
HI = ["hectare", "bigha", "pakka", "kaccha", "biswa", "165 foot", "132 foot", "3,025 gaj", "1,936 gaj", "0.253", "0.162", "7 bigha 18 biswa", "12 bigha 7 biswa", "Comment", "kaunsa bigha"]
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
H.append('<div id="cred">पक्का बीघा 165&times;165 ft = 27,225 sq ft &asymp; 0.2529 ha &middot; कच्चा बीघा 132&times;132 ft = 17,424 sq ft &asymp; 0.1619 ha &middot; 1 बीघा = 20 बिस्वा &middot; गणना लगभग; स्थानीय माप तहसील से पुष्टि करें</div>')

CSS = """@font-face{font-family:Deva;font-weight:100 900;src:url(assets/fonts/notodeva.woff2)}@font-face{font-family:DevaH;font-weight:100 900;src:url(assets/fonts/deva800.woff2)}@font-face{font-family:Anton;src:url(assets/fonts/anton.woff2)}@font-face{font-family:Mont;font-weight:700;src:url(assets/fonts/mont700.woff2)}@font-face{font-family:Mont;font-weight:800;src:url(assets/fonts/mont800.woff2)}@font-face{font-family:Mont;font-weight:900;src:url(assets/fonts/mont900.woff2)}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#070a12}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mont,Deva,sans-serif;background:radial-gradient(120% 80% at 50% 35%,#141b2e 0%,#070a12 70%)}
.y{color:#fff;background:#2FA8FF;border-radius:6px;padding:0 6px}
#face{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:40}
#cred{position:absolute;left:30px;right:30px;top:1700px;text-align:center;font:600 17px Deva;color:rgba(255,255,255,.55);z-index:20}
.bgp{position:absolute;inset:0;overflow:hidden;z-index:1;opacity:0}.bgp img{width:100%;height:100%;object-fit:cover}.bgp:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(7,10,18,.6),rgba(7,10,18,.25) 45%,rgba(7,10,18,.7))}
.doc{position:absolute;left:160px;top:520px;width:760px;height:760px;overflow:hidden;border-radius:14px;background:#fff;box-shadow:0 30px 80px rgba(0,0,0,.7);z-index:5}.doc .im{position:absolute;left:0;top:-80px;width:760px}.doc img{display:block;width:100%}
.doc .hl{position:absolute;left:150px;top:610px;padding:10px 26px;border-radius:10px;background:#fff;border:4px solid #2FA8FF;font:900 52px Mont,Deva;color:#111;box-shadow:0 10px 30px rgba(0,0,0,.4)}
.fk{position:absolute;background:#fff;color:#111;font-family:Deva,sans-serif;font-weight:500;line-height:1.25;white-space:nowrap;overflow:hidden;padding-left:2px}.hlb{display:none}
.wm{position:absolute;left:50%;top:42%;translate:-50% -50%;rotate:-28deg;white-space:nowrap;font-family:Deva,Mont;font-weight:900;color:rgba(200,30,30,.13);pointer-events:none}
#hook{position:absolute;left:60px;right:60px;top:140px;z-index:16;text-align:center;padding:40px 20px;border-radius:18px;border:3px solid #2FA8FF;background:rgba(7,10,18,.94);box-shadow:0 0 40px rgba(47,168,255,.35)}#hook small{display:block;font:800 40px Deva;color:#9fd4ff}#hook b{display:block;margin-top:8px;font:900 140px/1.05 DevaH;color:#fff;text-shadow:0 0 24px rgba(47,168,255,.6)}#hook span{display:inline-block;margin-top:16px;padding:8px 24px;border-radius:8px;background:#2FA8FF;color:#fff;font:900 40px Deva}
#map{position:absolute;left:70px;top:0;width:940px;z-index:6;opacity:0}#map svg{display:block;width:100%;overflow:visible}
#map .dz{fill:currentColor;fill-opacity:0;stroke-width:2.6;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1}#map .dz{vector-effect:non-scaling-stroke}#map path{pathLength:1}
#map .qm{font:900 44px Mont;text-anchor:middle;filter:drop-shadow(0 0 6px currentColor)}
.t1{position:absolute;left:0;right:0;top:160px;margin:0 auto;width:max-content;padding:14px 34px;border-radius:14px;background:rgba(7,10,18,.92);border:2px solid #2FA8FF;z-index:15;box-shadow:0 0 30px rgba(47,168,255,.3)}.t1 b{font:900 62px DevaH;color:#fff}
.two{position:absolute;left:60px;right:60px;top:1260px;z-index:15;display:flex;justify-content:center;align-items:center;gap:26px}.two>div{padding:24px 34px;border-radius:16px;text-align:center}.two .pk{background:#0c2a4a;border:3px solid #2FA8FF}.two .kc{background:#0a1a30;border:3px solid #9fd4ff}
.two b{display:block;font:900 84px/1 DevaH;color:#fff}.two span{display:block;margin-top:8px;font:800 34px Deva;color:#cfd8e6}.two i{font:400 64px Anton;font-style:normal;color:#2FA8FF}
#sq{position:absolute;left:160px;top:380px;width:760px;height:760px;z-index:7}#sq .pq,#sq .kq{position:absolute;left:0;bottom:0}#sq .pq{border:6px solid #2FA8FF;background:rgba(47,168,255,.14);box-shadow:0 0 30px rgba(47,168,255,.45)}#sq .kq{border:6px solid #fff;background:rgba(255,255,255,.18);box-shadow:0 0 30px rgba(255,255,255,.45)}
#sq em{position:absolute;font:900 38px Mont;font-style:normal;color:#fff;text-shadow:0 2px 8px #000}#sq .pq em.w{left:50%;top:-58px;translate:-50% 0}#sq .pq em.h{right:-150px;top:50%;translate:0 -50%}#sq .kq em.w{left:50%;bottom:16px;translate:-50% 0;color:#111;text-shadow:none}#sq .kq em.h{right:16px;top:50%;translate:0 -50%;color:#111;text-shadow:none}
#sq .lab{position:absolute;left:-100px;right:-100px;top:calc(100% + 26px);text-align:center}#sq .kq .lab{top:auto;bottom:calc(100% + 30px)}#sq .lab b{display:block;font:900 64px DevaH;color:#fff}#sq .lab span{display:inline-block;margin-top:8px;padding:6px 18px;border-radius:8px;background:rgba(7,10,18,.9);font:800 36px Deva;color:#9fd4ff}
#ask{position:absolute;left:50px;right:50px;top:150px;z-index:15;text-align:center;padding:26px 20px;border-radius:18px;background:rgba(7,10,18,.94);border:3px solid #2FA8FF;box-shadow:0 0 40px rgba(47,168,255,.4)}#ask b{display:block;font:900 70px/1.1 DevaH;color:#fff}#ask span{display:block;margin-top:12px;font:800 42px Deva;color:#cfd8e6}#ask u{text-decoration:none;padding:2px 14px;border-radius:8px;background:#2FA8FF;color:#fff}
#g2{position:absolute;left:0;right:0;top:600px;margin:0 auto;width:max-content;z-index:15;text-align:center;padding:40px 60px;border-radius:20px;background:rgba(7,10,18,.94);border:3px solid #2FA8FF}#g2 small{display:block;font:800 40px Deva;color:#9fd4ff}#g2 b{display:block;margin-top:10px;font:900 150px/1 DevaH;color:#fff}
.calc{position:absolute;left:60px;right:60px;top:260px;z-index:15;padding:40px 40px;border-radius:20px;background:rgba(7,10,18,.95)}.calc.pk{border:3px solid #2FA8FF;box-shadow:0 0 40px rgba(47,168,255,.3)}.calc.kc{border:3px solid #9fd4ff;box-shadow:0 0 40px rgba(47,168,255,.3)}
.calc small{display:block;text-align:center;font:900 54px DevaH;color:#fff}.calc .r{margin-top:34px;text-align:center;font:400 84px/1.1 Anton,DevaH;color:#e8edf5}.calc .r i{font-style:normal;color:#2FA8FF}.calc .r b{font-weight:400;color:#7cc8ff}.calc .g{color:#fff}
.calc .res{display:inline-block;padding:10px 30px;border-radius:14px;background:#2FA8FF;color:#fff;font:900 74px DevaH}.calc.kc .res{background:#fff;color:#0a1a30}
.note{position:absolute;left:0;right:0;top:1240px;margin:0 auto;width:max-content;z-index:16;padding:14px 34px;border-radius:12px;background:#2FA8FF;color:#fff;font:900 54px DevaH;box-shadow:0 0 30px rgba(47,168,255,.5)}
#cmp{position:absolute;left:50px;right:50px;top:330px;z-index:15;text-align:center;padding:40px 30px;border-radius:20px;background:rgba(7,10,18,.95);border:3px solid #2FA8FF}#cmp small{display:block;font:800 44px Deva;color:#9fd4ff}
#cmp .cc{display:flex;justify-content:center;align-items:center;gap:24px;margin-top:30px}#cmp .cc>div{padding:26px 30px;border-radius:16px}#cmp .pk{background:#0c2a4a;border:3px solid #2FA8FF}#cmp .kc{background:#0a1a30;border:3px solid #9fd4ff}
#cmp .cc b{display:block;font:400 150px/1 Anton;color:#fff}#cmp .cc span{display:block;font:800 34px Deva;color:#e8edf5}#cmp .cc em{display:block;margin-top:10px;font:900 44px DevaH;font-style:normal;color:#7cc8ff}#cmp .cc i{font:400 90px Anton;font-style:normal;color:#2FA8FF}
#cmp .ask2{margin-top:34px;font:900 50px DevaH;color:#fff}#cmp .ask2 u{text-decoration:none;color:#2FA8FF}
#save{position:absolute;left:60px;right:60px;top:300px;z-index:16;text-align:center;padding:40px 30px;border-radius:20px;background:rgba(7,10,18,.95);border:3px solid #2FA8FF}#save>small{display:block;font:800 36px Deva;color:#9fd4ff}#save>b{display:block;margin-top:10px;font:900 80px DevaH;color:#fff}
#save .ch{display:flex;justify-content:center;align-items:center;gap:16px;margin-top:30px;font:900 50px DevaH;color:#e8edf5}#save .ch i{font-style:normal;font-family:Anton;font-weight:400;color:#2FA8FF}#save .ch .g{padding:4px 16px;border-radius:8px;background:#2FA8FF;color:#fff}#save .ch .y{padding:4px 16px;border-radius:8px;background:#fff;color:#0a1a30}
#save .cta{display:inline-block;margin-top:40px;padding:14px 34px;border-radius:10px;background:#2FA8FF;color:#fff;font:900 40px Deva}
#fm{position:absolute;left:60px;right:60px;top:280px;z-index:15;padding:40px 40px;border-radius:20px;background:rgba(7,10,18,.95);border:3px solid #2FA8FF;box-shadow:0 0 40px rgba(47,168,255,.3)}#fm small{display:block;text-align:center;font:900 54px DevaH;color:#9fd4ff}
#fm .fr{display:flex;justify-content:center;align-items:center;gap:18px;margin-top:34px;font:900 56px DevaH;color:#fff}#fm .fr i{font-style:normal;font-family:Anton;font-weight:400;font-size:60px;color:#2FA8FF}#fm .fr b{padding:4px 18px;border-radius:10px;background:#2FA8FF;color:#fff;font-weight:900}
.qt{position:absolute;z-index:17;padding:12px 28px;border-radius:14px;background:rgba(7,10,18,.94);border:3px solid #2FA8FF;color:#fff;font:900 62px DevaH;box-shadow:0 0 30px rgba(47,168,255,.55)}#qb{left:60px;top:1210px}#qc{right:60px;top:1330px}
.cp{position:absolute;left:40px;right:40px;top:1480px;text-align:center;opacity:0;z-index:35}
.cp div{display:inline-block;padding:4px 20px 8px;border-radius:10px;background:#fff;font:900 60px/1.12 Mont;color:#111;box-shadow:0 8px 24px rgba(0,0,0,.45)}"""
audio = (f'<audio id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{END}" data-track-index="1" data-volume="1"></audio><audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.14" data-fade-out="1.5"></audio>' if VOICE
         else f'<audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.6" data-fade-out="1.5"></audio>')
html = f"""<!doctype html><html lang="hi"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="30">
{"".join(H)}
{audio}
{"".join(SFX)}
</div><script>
document.querySelectorAll("#map .dz").forEach(p => p.setAttribute("pathLength", "1"));
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(J)}
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>"""
open(f"{P}/index.html", "w").write(html)
print("END", END, [p["s"] for p in PH])
