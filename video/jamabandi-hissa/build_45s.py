"""Jamabandi mein hissa — 45s screen-guide reel. Real Apna Khata/BhuNaksha screenshots (user's) + real Jamabandi with personal details blurred."""
import json, os
P = "proj"
LINES = [
    "Aap bhi Jamabandi mein apna hissa nikaalna seekh lijiye.",
    "Apne naam ke aage hissa dekhiye, jaise 1/6. Aur neeche kul area, 1.03 hectare.",
    "Hissa guna kul area: 1/6 guna 1.03, yaani 0.1717 hectare.",
    "Isko 11,960 se guna kariye, 2,053 gaj. Aur 3,025 se bhaag dijiye, lagbhag 0.68 bigha.",
    "Bigha ka maap apni tehsil mein confirm kar lijiye.",
    "Aur agar Jamabandi ki PDF nikaalni hai, to video aage dekhiye.",
    "Google par Apna Khata search kariye, aur pehli website kholiye.",
    "Neeche scroll karke Bhu Naksha par click kariye.",
    "Viewmap kholiye, aur zila, tehsil, gaon aur sheet number chuniye.",
    "Map par apna khasra dabaiye, aur Plot Info mein Nakal par click kariye.",
    "Show Report PDF dabaiye, aur aapki Jamabandi ki PDF taiyaar.",
    "Video save kar lijiye, aur jiski zameen bati hui hai unhe share kariye.",
]
VOICE = os.path.exists("rec/phrases.json")
if VOICE: PH = json.load(open("rec/phrases.json"))
else:
    PH = []; t = .3
    for l in LINES:
        d = len(l) / 16.5 + .2 + (.5 if not PH else 0); PH.append({"s": round(t, 2), "e": round(t + d, 2), "t": l}); t += d + .3
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

FW, FH, FX, FY = 940, 1160, 70, 250
IMG = {"s1": (576, 1240), "s2": (576, 1240), "s3": (576, 1240), "s4": (720, 1550), "s5": (720, 1550), "s6": (576, 1240), "s7": (720, 1550), "jama_real": (1082, 1530)}
def place(name, cx, cy, z):
    w, h = IMG[name]; k = FW / w; W, Hh = w * k * z, h * k * z
    tx = min(0, max(FW - W, FW / 2 - cx * k * z)); ty = min(0, max(FH - Hh, FH * .45 - cy * k * z))
    return tx, ty, z
def screen(sid, name, t0, t1, targets, scroll=None, extra=""):
    """targets: list of (t, cx, cy, rx, ry, z, label)"""
    w, h = IMG[name]; k = FW / w
    svg = []
    for i, (t, cx, cy, rx, ry, z, lab) in enumerate(targets):
        s = k * z; ex, ey = cx + rx * .35, cy + ry * .98; sx, sy = ex + 80 / s, ey + 150 / s
        if sx > w - 20: sx, ex = ex - 80 / s, cx - rx * .35   # arrow from lower-left if too close to right edge
        svg.append(f'<ellipse class="ci" id="{sid}c{i}" cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" pathLength="1" style="stroke-width:{8 / s:.2f}"/>'
                   f'<g class="ar" id="{sid}a{i}"><line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey + 6 / s:.1f}" style="stroke-width:{9 / s:.2f}" marker-end="url(#ah)"/>'
                   f'<text x="{sx:.1f}" y="{sy + 34 / s:.1f}" style="font-size:{30 / s:.1f}px">{lab}</text></g>')
    if scroll:
        svg.append(f'<g class="ar" id="{sid}sc"><line x1="{w / 2}" y1="{h * .55}" x2="{w / 2}" y2="{h * .8}" style="stroke-width:{9 / k:.2f}" marker-end="url(#ah)"/><text x="{w / 2}" y="{h * .53}" text-anchor="middle" style="font-size:{34 / k:.1f}px">स्क्रॉल करें</text></g>')
    H.append(f'<div class="scr" id="{sid}"><div class="im" id="{sid}i" style="width:{w * k:.0f}px;height:{h * k:.0f}px"><img src="assets/img/{name}.jpg"/>{extra}'
             f'<svg viewBox="0 0 {w} {h}"><defs><marker id="ah" markerWidth="4" markerHeight="4" refX="2.2" refY="2" orient="auto"><path d="M0,0 L4,2 L0,4 Z" fill="#FFD23F"/></marker></defs>{"".join(svg)}</svg></div></div>')
    J.append(f'tl.set("#{sid}", {{opacity:0}}, 0); tl.set("#{sid} .ci", {{strokeDashoffset:1}}, 0); tl.set("#{sid} .ar", {{opacity:0}}, 0);'
             f'tl.fromTo("#{sid}", {{opacity:0, x:60}}, {{opacity:1, x:0, duration:.35, ease:"power3.out", immediateRender:false}}, {t0:.2f}); tl.to("#{sid}", {{opacity:0, x:-60, duration:.3}}, {t1 - .3:.2f});')
    J.append(f'tl.set("#{sid}i", {{x:0, y:0, scale:1, transformOrigin:"0 0"}}, 0);')
    if scroll:
        J.append(f'tl.fromTo("#{sid}sc", {{opacity:0}}, {{opacity:1, duration:.25, immediateRender:false}}, {scroll[0]:.2f}); tl.fromTo("#{sid}sc line", {{y:-20}}, {{y:20, duration:.4, yoyo:true, repeat:3, immediateRender:false}}, {scroll[0]:.2f});'
                 f'tl.to("#{sid}i", {{y:{FH - h * k:.0f}, duration:{scroll[1]:.2f}, ease:"power2.inOut"}}, {scroll[0] + .2:.2f});')
    for i, (t, cx, cy, rx, ry, z, lab) in enumerate(targets):
        tx, ty, zz = place(name, cx, cy, z)
        J.append(f'tl.to("#{sid}i", {{x:{tx:.0f}, y:{ty:.0f}, scale:{zz}, duration:.7, ease:"power2.inOut"}}, {t - .75:.2f});'
                 f'tl.to("#{sid}c{i}", {{strokeDashoffset:0, duration:.5, ease:"power2.out"}}, {t:.2f});'
                 f'tl.fromTo("#{sid}a{i}", {{opacity:0, scale:.6, svgOrigin:"{cx} {cy}"}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)", immediateRender:false}}, {t + .3:.2f});'
                 f'tl.to("#{sid}a{i} line", {{x:6, y:-8, duration:.35, yoyo:true, repeat:3}}, {t + .65:.2f});')
        if i > 0: J.append(f'tl.to("#{sid}c{i - 1}, #{sid}a{i - 1}", {{opacity:0, duration:.25}}, {t - .75:.2f});')
        sfx("click-soft", t, .3)
def step(i, num, text, t0, t1):
    H.append(f'<div class="stp" id="stp{i}"><i>{num}</i><b>{text}</b></div>')
    J.append(f'tl.set("#stp{i}", {{opacity:0}}, 0); tl.fromTo("#stp{i}", {{opacity:0, y:-20}}, {{opacity:1, y:0, duration:.3, immediateRender:false}}, {t0:.2f}); tl.to("#stp{i}", {{opacity:0, duration:.2}}, {t1 - .2:.2f});')

FAKE = [((80, 322, 240, 346), "सीता पुत्री मोहन"), ((80, 370, 224, 394), "गीता पुत्र मोहन"), ((80, 418, 232, 442), "रमेश पुत्र मोहन"),
        ((140, 124, 215, 150), "उदाहरणपुर"), ((150, 158, 225, 186), "नमूना"), ((150, 190, 215, 216), "नमूना"), ((118, 222, 215, 248), "उदाहरण")]
ROWS = [(322, 238, 350, "1/2"), (370, 222, 336, "1/3"), (418, 230, 343, "1/6")]   # y0, hissa-x, caste-x, share  (1/2+1/3+1/6 = 1)
def fake_overlay(k, hl=False):
    o = []
    for (x0, y0, x1, y1), t in FAKE:
        o.append(f'<div class="fk" style="left:{x0 * k:.1f}px;top:{y0 * k:.1f}px;width:{(x1 - x0 + 4) * k:.1f}px;height:{(y1 - y0) * k:.1f}px;font-size:{19 * k:.1f}px">{t}</div>')
    for y0, hx, cs, sh in ROWS:
        o.append(f'<div class="fk" style="left:{(hx - 2) * k:.1f}px;top:{y0 * k:.1f}px;width:{(cs - 30 - hx + 2) * k:.1f}px;height:{24 * k:.1f}px;font-size:{19 * k:.1f}px">हिस्सा- {sh}</div>')
        o.append(f'<div class="fk" style="left:{(cs - 30) * k:.1f}px;top:{y0 * k:.1f}px;width:{217 * k:.1f}px;height:{24 * k:.1f}px;font-size:{19 * k:.1f}px">&nbsp;जाति- ----&nbsp;&nbsp;सा. देह खातेदार</div>')
        o.append(f'<div class="fk" style="left:{62 * k:.1f}px;top:{(y0 + 24) * k:.1f}px;width:{645 * k:.1f}px;height:{24 * k:.1f}px"></div>')
    o.append(f'<div class="fk" style="left:{55 * k:.1f}px;top:{466 * k:.1f}px;width:{670 * k:.1f}px;height:{148 * k:.1f}px"></div>')
    for b in [(160, 1215, 450, 1305), (500, 1215, 720, 1305), (110, 1360, 880, 1388), (150, 1428, 400, 1482)]:
        o.append(f'<div class="fk" style="left:{b[0] * k:.1f}px;top:{b[1] * k:.1f}px;width:{(b[2] - b[0]) * k:.1f}px;height:{(b[3] - b[1]) * k:.1f}px;font-size:{19 * k:.1f}px">------</div>')
    if hl:
        for i, (y0, hx, cs, sh) in enumerate(ROWS):
            o.append(f'<div class="hlb" id="hlb{i}" style="left:{(hx - 8) * k:.1f}px;top:{(y0 - 4) * k:.1f}px;width:{(cs - 30 - hx + 14) * k:.1f}px;height:{32 * k:.1f}px"></div>')
    o.append(f'<div class="wm" style="font-size:{150 * k:.0f}px">उदाहरण · SAMPLE</div>')
    return "".join(o)
# ---------- 0 hook ----------
H.append('<div id="hook"><small>आप भी सीख लीजिए</small><b>जमाबंदी में<br/>अपना हिस्सा निकालना</b><span>1/6 = कितनी ज़मीन?</span></div>')
J.append(f'tl.fromTo("#hook", {{opacity:0, scale:1.1}}, {{opacity:1, scale:1, duration:.45, ease:"power3.out"}}, 0); tl.to("#hook", {{opacity:0, y:-30, duration:.3}}, {S(1) - .3:.2f});')
H.append('<div class="scr" id="hd"><div class="im" id="hdi" style="width:940px"><img src="assets/img/jama_real.jpg"/>' + fake_overlay(940 / 1082, hl=True) + '</div></div>')
J.append(f'tl.fromTo("#hd", {{opacity:0, y:160, scale:.9}}, {{opacity:1, y:120, scale:1, duration:.5, ease:"power3.out"}}, .1); tl.to("#hd", {{opacity:0, duration:.3}}, {S(1) - .3:.2f});')
t12 = PH[0].get("hl", [1.0])[0]; J.append(f'tl.to("#hdi", {{scale:1.4, x:-60, y:-250, transformOrigin:"0 0", duration:.6, ease:"power2.inOut"}}, {t12 - .6:.2f}); tl.to("#hook", {{y:-150, scale:.82, duration:.5, ease:"power2.inOut"}}, {t12 - .6:.2f}); tl.set(".hlb", {{opacity:0, scale:.7}}, 0);')
for i, t_ in enumerate(PH[0].get("hl", [1.0, 1.75, 2.65])):
    J.append(f'tl.to("#hlb{i}", {{opacity:1, scale:1, duration:.25, ease:"back.out(2.5)"}}, {t_:.2f});'); sfx("pop", t_, .28)
sfx("impact-bass-1", 0, .4)

# ---------- 1 the jamabandi ----------
step(6, "&#9733;", "नाम के आगे <u>हिस्सा</u> &middot; नीचे <u>कुल क्षेत्रफल</u>", S(1) - .1, S(2))
screen("sc8", "jama_real", S(1) - .1, S(2) + .2, [(wt(1, "hissa"), 290, 430, 72, 20, 1.6, "हिस्सा 1/6"), (wt(1, "kul area"), 250, 1135, 75, 22, 1.6, "कुल 1.0300 हेक्टेयर")], extra=fake_overlay(940 / 1082))
H.append('<div class="tag" id="tagr">उदाहरण &middot; नाम बदले गए हैं</div>')
J.append(f'tl.set("#tagr", {{opacity:0}}, 0); tl.to("#tagr", {{opacity:1, duration:.3}}, {S(1) + .2:.2f}); tl.to("#tagr", {{opacity:0, duration:.2}}, {S(2):.2f});')
sfx("whoosh", S(1) - .1, .3)

# ---------- 2-3 formula ----------
def board(i, t0, t1, html):
    H.append(f'<div class="bd" id="bd{i}">{html}</div>')
    J.append(f'tl.set("#bd{i}", {{opacity:0}}, 0); tl.set("#bd{i} .tk", {{opacity:0}}, 0); tl.fromTo("#bd{i}", {{opacity:0, scale:.95}}, {{opacity:1, scale:1, duration:.35, ease:"power3.out", immediateRender:false}}, {t0:.2f}); tl.to("#bd{i}", {{opacity:0, y:-30, duration:.3}}, {t1 - .3:.2f});')
def tok(i, j, t):
    J.append(f'tl.fromTo("#bd{i} .t{j}", {{opacity:0, y:24, scale:.85}}, {{opacity:1, y:0, scale:1, duration:.35, ease:"back.out(2)", immediateRender:false}}, {t:.2f});'); sfx("click-soft", t, .25)
board(7, S(2) - .1, S(3), '<div class="tk t0 lbl">हिस्सा &times; कुल क्षेत्रफल</div><div class="row"><span class="tk t1 big">1/6</span><span class="tk t2 op">&times;</span><span class="tk t3 big">1.03</span></div>'
      '<div class="tk t4 op">=</div><div class="tk t5 res">0.1717 <small>हेक्टेयर</small></div>')
tok(7, 0, S(2) + .1); tok(7, 1, wt(2, "1/6 guna") - .1); tok(7, 2, wt(2, "guna 1.03") - .05); tok(7, 3, wt(2, "1.03 hectare") - .1); tok(7, 4, wt(2, "answer aata") - .1); tok(7, 5, wt(2, "answer aata") + .1)
sfx("impact-bass-1", wt(2, "answer aata") + .1, .35)
board(8, S(3) - .1, S(4), '<div class="tk t0 lbl">हेक्टेयर &rarr; गज &rarr; बीघा</div>'
      '<div class="ln tk t1"><span>0.1717</span><i>&times; 11,960 =</i><b>2,053 गज</b></div>'
      '<div class="ln tk t2"><span>2,053</span><i>&divide; 3,025 =</i><b class="g">0.68 बीघा</b></div>'
      '<em class="tk t3">1 हेक्टेयर &asymp; 11,960 गज &middot; 1 पक्का बीघा = 3,025 गज (इलाके के हिसाब से अलग हो सकता है)</em>')
tok(8, 0, S(3) + .1); tok(8, 1, wt(3, "11,960") - .1); tok(8, 2, wt(3, "3,025") - .1); tok(8, 3, wt(3, "0.68") - .1)
sfx("impact-bass-1", wt(3, "0.68"), .35)

# owner result: name + 0.68 bigha
H.append('<div id="own"><small>परिणाम</small><div class="or"><span class="nm">रमेश पुत्र मोहन</span><span class="hs">हिस्सा <span style="font:900 36px Mont">1/6</span></span></div><i>&darr;</i><b>0.68 बीघा</b><em>&asymp; 2,053 गज &middot; 0.1717 हेक्टेयर</em></div>')
to_ = wt(3, "Ab hamare paas") - .1
J.append(f'tl.set("#own", {{opacity:0}}, 0); tl.fromTo("#own", {{opacity:0, y:40, scale:.95}}, {{opacity:1, y:0, scale:1, duration:.4, ease:"back.out(1.6)", immediateRender:false}}, {to_:.2f}); tl.fromTo("#own b", {{scale:.6, opacity:0}}, {{scale:1, opacity:1, duration:.4, ease:"back.out(2.5)", immediateRender:false}}, {to_ + .35:.2f}); tl.to("#own", {{opacity:0, y:-20, duration:.3}}, {(PH[4]["fgap"][0] if "fgap" in PH[4] else S(4)) - .1:.2f});')
J.append(f'tl.to("#bd8", {{opacity:0, duration:.25}}, {to_ - .05:.2f});')
sfx("impact-bass-1", to_ + .35, .4)
# general formula card (in the inserted gap)
FG0, FG1 = PH[4]["fgap"] if "fgap" in PH[4] else (S(4) - .05, E(4) + .05)
H.append('<div id="fml"><small>सामान्य सूत्र</small><b>अपना हिस्सा निकालो</b>'
         '<div class="ch"><span>हिस्सा &times; कुल क्षेत्रफल</span><i>=</i><span class="g">हेक्टेयर</span></div>'
         '<div class="ch"><span class="g">हेक्टेयर</span><i>&times; 11,960 =</i><span class="g">गज</span></div>'
         '<div class="ch"><span class="g">गज</span><i>&divide; 3,025 =</i><span class="y">बीघा</span></div></div>')
J.append(f'tl.set("#fml", {{opacity:0}}, 0); tl.fromTo("#fml", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:.4, ease:"power3.out", immediateRender:false}}, {FG0:.2f}); tl.fromTo("#fml .ch", {{opacity:0, x:-40}}, {{opacity:1, x:0, duration:.3, stagger:.35, immediateRender:false}}, {FG0 + .3:.2f}); tl.to("#fml", {{opacity:0, y:-20, duration:.3}}, {FG1 + .05:.2f});')
sfx("whoosh", FG0, .3); sfx("click-soft", FG0 + .3, .25); sfx("click-soft", FG0 + .65, .25); sfx("click-soft", FG0 + 1.0, .25)
# ---------- 5 bridge ----------
H.append('<div id="bridge"><small>अब अगला भाग</small><b>जमाबंदी की PDF<br/>कैसे निकालें?</b><span>वीडियो आगे देखिए &darr;</span></div>')
J.append(f'tl.set("#bridge", {{opacity:0}}, 0); tl.fromTo("#bridge", {{opacity:0, scale:.92}}, {{opacity:1, scale:1, duration:.4, ease:"back.out(1.6)", immediateRender:false}}, {S(5) - .1:.2f}); tl.to("#bridge span", {{y:12, duration:.35, yoyo:true, repeat:3}}, {wt(5, "aage"):.2f}); tl.to("#bridge", {{opacity:0, duration:.3}}, {S(6) - .3:.2f});')
sfx("riser", S(5) - .3, .3); sfx("whoosh", S(6) - .2, .3)

# ---------- 6..10 navigation ----------
step(1, "1", "Google पर <u>अपना खाता</u> सर्च करें", S(6) - .1, S(7))
screen("sc1", "s1", S(6) - .1, S(7), [(wt(6, "website") - .1, 130, 450, 135, 40, 1.35, "क्लिक करें")])
step(2, "2", "नीचे स्क्रॉल &rarr; <u>भू नक्शा</u>", S(7) - .1, S(8))
mid = S(7) + (E(7) - S(7)) * .45
screen("sc2", "s2", S(7) - .1, mid + .3, [], scroll=(S(7) + .2, .9))
screen("sc3", "s3", mid, S(8), [(wt(7, "Bhu Naksha") + .1, 288, 771, 295, 50, 1.0, "क्लिक करें")])
step(3, "3", "<u>Viewmap</u> &rarr; जिला, तहसील, गाँव, शीट", S(8) - .1, S(9))
m3 = wt(8, "aur zila")
screen("sc4", "s4", S(8) - .1, m3 + .3, [(wt(8, "Viewmap") + .5, 95, 160, 62, 26, 1.9, "क्लिक करें")])
screen("sc5", "s5", m3, S(9), [(m3 + .45, 235, 638, 190, 120, 1.3, "चुनें")])
step(4, "4", "अपना <u>खसरा</u> दबाएँ &rarr; <u>नकल</u>", S(9) - .1, S(10))
screen("sc6", "s6", S(9) - .1, S(10), [(wt(9, "khasra"), 230, 710, 150, 95, 1.0, "दबाएँ"), (wt(9, "Nakal") + .1, 242, 1122, 55, 22, 1.35, "क्लिक करें")])
step(5, "5", "<u>Show Report PDF</u> &rarr; जमाबंदी PDF", S(10) - .1, S(11))
m10 = wt(10, "aur aapki")
screen("sc7", "s7", S(10) - .1, m10 + .3, [(wt(10, "Show") + .5, 45, 291, 50, 17, 2.3, "क्लिक करें")])
screen("sc9", "jama_real", m10, S(11), [], extra=fake_overlay(940 / 1082))
H.append('<div class="tag" id="tagp">&#128196; जमाबंदी PDF &middot; उदाहरण</div>')
J.append(f'tl.set("#tagp", {{opacity:0}}, 0); tl.to("#tagp", {{opacity:1, duration:.3}}, {m10 + .2:.2f}); tl.to("#tagp", {{opacity:0, duration:.2}}, {S(11) - .2:.2f}); tl.to("#sc9i", {{y:-260, duration:{S(11) - m10:.2f}, ease:"none"}}, {m10:.2f});')
sfx("pop", m10, .3)

# ---------- 11 save card ----------
H.append('<div id="save"><small>सेव कर लो</small><b>अपना हिस्सा निकालो</b>'
         '<div class="ch"><span>हिस्सा &times; कुल क्षेत्रफल</span><i>=</i><span class="g">हेक्टेयर</span></div>'
         '<div class="ch"><span class="g">हेक्टेयर</span><i>&times; 11,960 =</i><span class="g">गज</span></div>'
         '<div class="ch"><span class="g">गज</span><i>&divide; 3,025 =</i><span class="y">बीघा</span></div>'
         '<div class="wr">PDF: अपना खाता &rarr; भू नक्शा &rarr; नकल &rarr; Show Report PDF</div></div>')
J.append(f'tl.set("#save", {{opacity:0}}, 0); tl.fromTo("#save", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:.45, ease:"power3.out", immediateRender:false}}, {S(11) - .1:.2f}); tl.fromTo("#save .ch", {{opacity:0, x:-40}}, {{opacity:1, x:0, duration:.3, stagger:.2, immediateRender:false}}, {S(11) + .2:.2f});')
sfx("sparkle", wt(11, "share"), .3)

# ---------- captions ----------
HI = ["Apna Khata", "Bhu Naksha", "Viewmap", "khasra", "Nakal", "Show Report PDF", "PDF", "hissa", "1/6", "1.03 hectare", "0.1717 hectare", "11,960", "2,053 gaj", "3,025", "0.68 bigha", "save"]
def hl(t):
    for h in sorted(HI, key=len, reverse=True):
        i = t.find(h)
        if i >= 0 and "<span" not in t[max(0, i - 25):i] and "span" not in t[i:i + len(h)]: t = t[:i] + '<span class="y">' + h + '</span>' + t[i + len(h):]
    return t
ci = 0
FLAT = [q for ph in PH for q in (ph.get("parts") or ([ph] if ph["e"] - ph["s"] >= .1 else []))]
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
H.append('<div id="cred">Screens: apnakhata.rajasthan.gov.in &middot; bhunaksha.rajasthan.gov.in &middot; Jamabandi: udaharan, naam badle gaye hain &middot; 1 ha = 11,959.9 sq. yd</div>')

CSS = """@font-face{font-family:Deva;font-weight:100 900;src:url(assets/fonts/notodeva.woff2)}@font-face{font-family:DevaH;font-weight:100 900;src:url(assets/fonts/deva800.woff2)}@font-face{font-family:Anton;src:url(assets/fonts/anton.woff2)}@font-face{font-family:Mont;font-weight:700;src:url(assets/fonts/mont700.woff2)}@font-face{font-family:Mont;font-weight:800;src:url(assets/fonts/mont800.woff2)}@font-face{font-family:Mont;font-weight:900;src:url(assets/fonts/mont900.woff2)}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#0b0f17}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif;background:radial-gradient(120% 80% at 50% 30%,#18202e 0%,#0b0f17 65%,#06080c 100%)}
.y{color:#111;background:#FFD23F;border-radius:6px;padding:0 6px}
#face{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:40}
#cred{position:absolute;left:40px;right:40px;top:1700px;text-align:center;font:700 17px Mont,Deva;color:rgba(255,255,255,.55);z-index:20}
.scr{position:absolute;left:70px;top:250px;width:940px;height:1160px;overflow:hidden;border-radius:18px;border:3px solid #2b3a52;background:#fff;box-shadow:0 30px 80px rgba(0,0,0,.65);opacity:0;z-index:5}
#hd{background:transparent;border:none;box-shadow:none}
.im{position:absolute;left:0;top:0}.im img{display:block;width:100%;height:auto}.im svg{position:absolute;left:0;top:0;width:100%;height:100%;overflow:visible}
.fk{position:absolute;background:#fff;color:#111;font-family:Deva,sans-serif;font-weight:500;line-height:1.25;white-space:nowrap;overflow:hidden;padding-left:2px}
.hlb{position:absolute;border:4px solid #E8262B;border-radius:8px;background:rgba(255,210,63,.35);box-shadow:0 0 14px rgba(232,38,43,.5);opacity:0}
.wm{position:absolute;left:50%;top:42%;translate:-50% -50%;rotate:-28deg;white-space:nowrap;font-family:Deva,Mont;font-weight:900;color:rgba(200,30,30,.13);pointer-events:none}
.ci{fill:none;stroke:#E8262B;stroke-dasharray:1;stroke-dashoffset:1;stroke-linecap:round;filter:drop-shadow(0 0 3px rgba(232,38,43,.6))}
.ar line{stroke:#FFD23F;stroke-linecap:round}.ar text{fill:#111;font-family:Mont,Deva;font-weight:900;paint-order:stroke;stroke:#FFD23F;stroke-width:.35em;stroke-linejoin:round}
.stp{position:absolute;left:70px;right:70px;top:120px;height:100px;display:flex;align-items:center;gap:20px;padding:0 26px;border-radius:14px;background:#141c29;border:2px solid #FFD23F;opacity:0;z-index:15}
.stp i{flex:none;width:66px;height:66px;border-radius:50%;background:#FFD23F;color:#111;display:flex;align-items:center;justify-content:center;font:400 44px Anton,DevaH;font-style:normal}
.stp b{font:800 34px/1.15 Mont,Deva;color:#fff}.stp u{text-decoration:none;color:#FFD23F}
.tag{letter-spacing:.02em !important;position:absolute;left:0;right:0;top:1360px;margin:0 auto;width:max-content;padding:6px 16px;border-radius:6px;background:rgba(10,14,22,.9);border:1px solid #FFD23F;color:#FFD23F;font:800 20px Mont,Deva;letter-spacing:.1em;opacity:0;z-index:12}
#hook{position:absolute;left:60px;right:60px;top:300px;z-index:16;text-align:center;padding:30px 20px 28px;border-radius:14px;border:2px solid #FFD23F;background:rgba(11,15,23,.94)}
#hook small{letter-spacing:.02em !important;display:block;font:800 30px Mont,Deva;letter-spacing:.3em;color:#cfd8e6}#hook b{display:block;margin-top:8px;font:400 96px/1.02 Anton,DevaH;color:#fff}
#hook span{display:inline-block;margin-top:18px;padding:8px 22px;border-radius:6px;background:#FFD23F;color:#111;font:900 30px Mont,Deva;letter-spacing:.1em}
.bd{position:absolute;left:60px;right:60px;top:300px;z-index:15;text-align:center;padding:42px 30px;border-radius:16px;border:2px solid #FFD23F;background:#121a27;box-shadow:0 30px 70px rgba(0,0,0,.6)}
.bd .lbl{letter-spacing:.02em !important;font:800 32px Mont,Deva;letter-spacing:.16em;color:#cfd8e6}.bd .row{display:flex;justify-content:center;align-items:center;gap:30px;margin-top:26px}.bd .big{font:400 140px/1 Anton,DevaH;color:#fff}.bd .op{font:400 90px/1 Anton,DevaH;color:#FFD23F}
.bd .res{display:inline-block;margin-top:16px;padding:14px 34px;border-radius:12px;background:#2FD158;color:#062411;font:400 120px/1 Anton,DevaH}.bd .res small{font-size:.42em}
.bd .ln{display:flex;justify-content:center;align-items:center;gap:18px;margin-top:40px;font:400 76px/1 Anton,DevaH;color:#fff}.bd .ln i{font-style:normal;color:#FFD23F;font-size:60px}.bd .ln b{font-weight:400;padding:6px 16px;border-radius:10px;background:#fff;color:#111}.bd .ln b.g{background:#2FD158;color:#062411}
.bd em{display:block;margin-top:40px;font:700 28px Mont,Deva;font-style:normal;color:#cfd8e6}
#save{position:absolute;left:60px;right:60px;top:260px;z-index:16;text-align:center;padding:40px 30px;border-radius:16px;border:2px solid #FFD23F;background:#121a27}
#save>small{letter-spacing:.02em !important;display:block;font:800 30px Mont,Deva;letter-spacing:.3em;color:#FFD23F}#save>b{display:block;margin-top:10px;font:400 76px/1.05 Anton,DevaH;color:#fff}
#save .ch{display:flex;justify-content:center;align-items:center;gap:16px;margin-top:34px;font:400 52px Anton,DevaH;color:#e8edf5}#save .ch i{font-style:normal;color:#FFD23F}#save .ch .g{padding:4px 16px;border-radius:8px;background:#2FD158;color:#062411}#save .ch .y{padding:4px 16px;border-radius:8px;background:#FFD23F;color:#111}
#save .wr{margin-top:40px;font:800 28px/1.35 Mont,Deva;color:#FFD23F}
#bridge{position:absolute;left:60px;right:60px;top:420px;z-index:16;text-align:center;padding:40px 24px;border-radius:16px;border:2px solid #FFD23F;background:#121a27}
#bridge small{letter-spacing:.02em !important;display:block;font:800 28px Mont,Deva;letter-spacing:.3em;color:#cfd8e6}#bridge b{display:block;margin-top:12px;font:400 92px/1.04 Anton,DevaH;color:#fff}#bridge span{display:inline-block;margin-top:24px;padding:10px 26px;border-radius:8px;background:#FFD23F;color:#111;font:900 36px Mont,Deva;letter-spacing:.08em}
.bd .ic{font:400 120px/1 Mont,Deva;color:#FFD23F}.bd .wt{margin-top:10px;font:400 96px/1.02 Anton,DevaH;color:#fff}
#fml{position:absolute;left:60px;right:60px;top:300px;z-index:16;text-align:center;padding:40px 30px;border-radius:16px;border:2px solid #FFD23F;background:#121a27}
#fml>small{display:block;font:800 32px Mont,Deva;color:#FFD23F}#fml>b{display:block;margin-top:10px;font:400 76px/1.1 Anton,DevaH;color:#fff}
#fml .ch{display:flex;justify-content:center;align-items:center;gap:16px;margin-top:34px;font:400 52px Anton,DevaH;color:#e8edf5}#fml .ch i{font-style:normal;color:#FFD23F}#fml .ch .g{padding:4px 16px;border-radius:8px;background:#2FD158;color:#062411}#fml .ch .y{padding:4px 16px;border-radius:8px;background:#FFD23F;color:#111}
#own{position:absolute;left:90px;right:90px;top:360px;z-index:16;text-align:center;padding:36px 30px;border-radius:18px;border:3px solid #2FD158;background:#121a27;box-shadow:0 30px 70px rgba(0,0,0,.6)}
#own small{letter-spacing:.02em !important;display:block;font:800 28px Mont,Deva;letter-spacing:.3em;color:#2FD158}#own .or{display:flex;justify-content:center;align-items:center;gap:22px;margin-top:22px}#own .nm{font:800 60px Deva;color:#fff}#own .hs{padding:6px 16px;border-radius:8px;background:#FFD23F;color:#111;font:800 36px Deva}
#own i{display:block;margin-top:12px;font:400 70px/1 Mont,Deva;font-style:normal;color:#FFD23F}#own b{display:inline-block;margin-top:10px;padding:14px 40px;border-radius:14px;background:#2FD158;color:#062411;font:400 150px/1 Anton,DevaH}#own em{display:block;margin-top:20px;font:700 30px Mont,Deva;font-style:normal;color:#cfd8e6}
.cp{position:absolute;left:40px;right:40px;top:1480px;text-align:center;opacity:0;z-index:35}
.cp div{display:inline-block;padding:4px 20px 8px;border-radius:10px;background:#fff;font:900 60px/1.12 Mont,Deva;color:#111;box-shadow:0 8px 24px rgba(0,0,0,.45)}"""
audio = (f'<audio id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{END}" data-track-index="1" data-volume="1"></audio><audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.14" data-fade-out="1.5"></audio>' if VOICE
         else f'<audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.6" data-fade-out="1.5"></audio>')
open(f"{P}/index.html", "w").write(f"""<!doctype html><html lang="hi"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="30">
{"".join(H)}
{audio}
{"".join(SFX)}
</div><script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(J)}
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>""")
print("END", END, [p["s"] for p in PH])
