"""Jamabandi mein hissa kaise nikaalein — animated explainer. Document shown is a SAMPLE with made-up names."""
import json, os
P = "proj"
LINES = [
    "Jamabandi mein 15-20 naam hote hain, aur har naam ke aage 158/3795 jaisa hissa likha hota hai. Isse apni zameen kaise nikaalein? 1 minute mein seekhiye.",
    "Pehle Apna Khata website par jaakar apna zila, tehsil aur gaon chuniye, aur khata number ya naam se Jamabandi ki nakal nikaaliye.",
    "Upar khatedaron ki list hogi. Apna naam dhoondhiye aur uske aage likha hissa dekhiye. Jaise yahan 158/3795.",
    "Ab neeche dekhiye, sab khasron ka total area, kul khasre ke aage hectare mein. Yahan 3.7950 hectare.",
    "Formula simple hai: hissa guna total area. 158 bhaag 3795, guna 3.7950, barabar 0.158 hectare. Yeh aapki zameen hai.",
    "Ab hectare ko gaj mein badaliye. 1 hectare mein lagbhag 11,960 gaj. To 0.158 guna 11,960, yaani lagbhag 1,890 gaj.",
    "Bigha ke liye 3,025 se bhaag dijiye. 1,890 bhaag 3,025, yaani lagbhag 0.62 bigha.",
    "Ek trick: agar hisse ka neeche wala number, total area hi ho bina point ke, jaise 3795 aur 3.7950, to upar wale number ko seedha 1,000 se bhaag de dijiye. 158 bhaag 1,000, yaani 0.158 hectare.",
    "Dhyaan rahe, bigha har ilaake mein alag hota hai. Jaipur ke aas-paas pakka bigha 3,025 gaj ka maana jaata hai, apne tehsil mein confirm kar lijiye.",
    "Is video ko save kar lijiye, aur jis dost ki zameen bati hui hai usse share kariye.",
]
VOICE = os.path.exists("rec/phrases.json")
if VOICE: PH = json.load(open("rec/phrases.json"))
else:
    PH = []; t = .3
    for l in LINES:
        d = len(l) / 15 + .4 + (.8 if not PH else 0); PH.append({"s": round(t, 2), "e": round(t + d, 2), "t": l}); t += d + .35
def S(k): return PH[k]["s"]
def E(k): return PH[k]["e"]
def wt(k, w):
    t = PH[k]["t"]; i = t.lower().find(w.lower()); assert i >= 0, (k, w)
    return S(k) + (E(k) - S(k)) * i / len(t)
END = round(E(9) + 1.2, 2)
H, J, SFX = [], [], []
def sfx(n, t, v=.3): SFX.append(f'<audio id="sx{len(SFX)}" class="clip" src="assets/sfx/{n}.mp3" data-start="{max(0, t):.2f}" data-duration="2" data-track-index="{20 + len(SFX)}" data-volume="{v}"></audio>')
def show(sel, t0, t1, frm="opacity:0, y:30", dur=.45, ease="power3.out"):
    J.append(f'tl.fromTo("{sel}", {{{frm}}}, {{opacity:1, x:0, y:0, scale:1, duration:{dur}, ease:"{ease}", immediateRender:false}}, {t0:.2f}); tl.fromTo("{sel}", {{opacity:1}}, {{opacity:0, duration:.3, immediateRender:false}}, {t1 - .3:.2f}); tl.set("{sel}", {{opacity:0}}, 0);')

# ---------- sample Jamabandi document ----------
NAMES = [("रामलाल पुत्र मोहनलाल", 237), ("श्यामलाल पुत्र मोहनलाल", 237), ("गोपाल पुत्र किशनलाल", 949), ("कमला पत्नी भैरूलाल", 13), ("नारायण पुत्र भैरूलाल", 290),
         ("सुरेश पुत्र रामेश्वर", 158), ("महेश पुत्र रामेश्वर", 158), ("दिनेश पुत्र रामेश्वर", 158), ("सीता पुत्री रामेश्वर", 316), ("भंवरलाल पुत्र गणपत", 158),
         ("मोहन पुत्र गणपत", 13), ("राधा पत्नी गणपत", 312), ("हरिराम पुत्र छोटूराम", 316), ("बजरंग पुत्र छोटूराम", 158)]
NAMES.append(("कैलाश पुत्र छोटूराम", 3795 - sum(n for _, n in NAMES)))
HERO = 5
KH = [("18", "0.2530", "चाही-1"), ("23", "0.2530", "चाही-1"), ("24", "0.2530", "चाही-1"), ("25", "0.2530", "चाही-1"), ("31", "0.2480", "चाही-1"), ("...", "...", "..."), ("38/22", "0.0760", "गै.मु.बाड़ा")]
def lag(a):
    try: return "" if "गै" in a[2] else f"{float(a[1]) * 36:.2f}"
    except ValueError: return "..."
rows = "".join(f'<div class="nr{" hero" if i == HERO else ""}" id="nr{i}"><span class="nm">{i + 1}. {n}</span><span class="hs">हिस्सा- <b id="{"hhs" if i == HERO else ""}">{v}/3795</b></span><span class="kt">सा. देह खातेदार</span></div>' for i, (n, v) in enumerate(NAMES))
krows = "".join(f'<div class="kr"><span>{a}</span><span>{b}</span><span>{c}</span><span>{b}</span><span>{lag((a, b, c))}</span><span></span><span></span></div>' for a, b, c in KH)
H.append(f'''<div id="docwrap"><div id="doc">
<div class="top"><div class="seal">उदाहरण</div><b>जमाबन्दी (खेवट/खतौनी) (प्रतिलिपि )</b><div class="pp">प्रपत्र पी-26 (सी)<br/>(देखिये नियम 169 एच)<br/>पृष्ठ संख्या :- 1 of 2</div></div>
<div class="meta"><div><span>ग्राम का नाम :- उदाहरणपुर</span><span>पटवार हल्का :- नमूना</span><span>भू.अभि.नि.क्षेत्र :- नमूना</span><span>तहसील :- उदाहरण</span><span>जिला :- उदाहरण</span></div>
<div><span>अंतिम चौसला आधार संवत :- 2076 - 2079</span><span>भूमि धारक का नाम :- राज. सरकार</span><span>क्षेत्रफल की इकाई :- हैक्टेयर</span><span>खाता संख्या नया :- 39</span><span>खाता संख्या पुराना :- 32</span></div></div>
<div class="lab">काश्तकार का नाम :-</div>
<div id="nlist">{rows}</div>
<div class="kh"><div class="kr khd"><span>खसरा<br/>संख्या</span><span>क्षेत्रफल</span><span>भूमि<br/>वर्गीकरण</span><span></span><span>कृषक द्वारा<br/>संदत्त लगान</span><span>सिंचाई<br/>के साधन</span><span>टिप्पणी</span></div>{krows}
<div class="kr tot" id="tot"><span>कुल खसरे -16</span><span><b id="tval">3.7950</b></span><span></span><span></span><span>133.88</span><span></span><span></span></div></div>
<div class="foot"><b>आवेदक की सूचना :-</b><div class="fg"><span>आवेदक का नाम - ------</span><span>पता - ------</span><span>प्रतिलिपि सं. - XXXXX</span><span>नक़ल जारी करने का स्थान - ------</span></div>
<div class="qr">SAMPLE<br/>QR</div></div>
<div class="wm">SAMPLE</div></div>
<svg id="mark" viewBox="0 0 940 2600"><ellipse id="hcirc" cx="655" cy="0" rx="150" ry="34" pathLength="1"/><rect id="tbox" x="0" y="0" width="0" height="0" rx="10" pathLength="1"/></svg></div>''')
J.append('(function(){ const h = document.getElementById("nr' + str(HERO) + '"), b = document.getElementById("hhs"), t = document.getElementById("tot"), v = document.getElementById("tval"); const c = document.getElementById("hcirc"); c.setAttribute("cy", h.offsetTop + h.offsetHeight / 2); c.setAttribute("cx", b.offsetLeft + b.offsetWidth / 2); c.setAttribute("rx", b.offsetWidth / 2 + 26); const tb = document.getElementById("tbox"); tb.setAttribute("x", v.offsetLeft - 18); tb.setAttribute("y", t.offsetTop + 2); tb.setAttribute("width", v.offsetWidth + 36); tb.setAttribute("height", t.offsetHeight - 4); })();')
J.append('function DY(id, sc, frac){ const e = document.getElementById(id); const y = e.offsetTop + e.offsetHeight * (frac === undefined ? .5 : frac); return 760 - 260 - y * sc; }')
def docpos(t, el, sc, d=1.0, frac=.5):
    J.append(f'tl.to("#docwrap", {{y:() => DY("{el}", {sc}, {frac}), scale:{sc}, duration:{d}, ease:"power2.inOut"}}, {t:.2f});')

# ---------- 0 hook ----------
H.append('<div id="hook"><small>JAMABANDI MEIN</small><b>APNA HISSA<br/>KAISE NIKAALEIN?</b><span>158/3795 = KITNI ZAMEEN?</span></div>')
J.append(f'tl.fromTo("#hook", {{opacity:0, scale:1.12}}, {{opacity:1, scale:1, duration:.45, ease:"power3.out"}}, 0); tl.fromTo("#hook span", {{opacity:0, y:14}}, {{opacity:1, y:0, duration:.35, immediateRender:false}}, {wt(0, "158") - .1:.2f}); tl.to("#hook", {{opacity:0, y:-30, duration:.3}}, {S(1) - .3:.2f});')
J.append(f'tl.set("#docwrap", {{transformOrigin:"50% 0%", y:520, scale:.5, rotation:-4, opacity:0}}, 0); tl.to("#docwrap", {{opacity:1, y:330, rotation:-2, duration:.9, ease:"power3.out"}}, .25);')
J.append(f'tl.to("#docwrap", {{y:300, rotation:0, duration:{S(1) - 1.2:.2f}, ease:"none"}}, 1.15); tl.to("#docwrap", {{opacity:0, y:420, duration:.4}}, {S(1) - .2:.2f});')
J.append(f'tl.fromTo(".nr .hs b", {{color:"#1c1a16"}}, {{color:"#C2410C", duration:.2, stagger:.05, yoyo:true, repeat:1, immediateRender:false}}, {wt(0, "hissa") - .2:.2f});')
sfx("impact-bass-1", 0, .45); sfx("whoosh", .25, .3)

# ---------- 1 Apna Khata steps ----------
H.append('<div id="steps"><small>STEP 1 &middot; NAKAL NIKAALO</small>'
         '<div class="st" id="st1"><i>1</i><div><b>APNA KHATA WEBSITE</b><span>Rajasthan bhu-abhilekh portal</span></div></div>'
         '<div class="st" id="st2"><i>2</i><div><b>ZILA &rarr; TEHSIL &rarr; GAON</b><span>apna gaon chuno</span></div></div>'
         '<div class="st" id="st3"><i>3</i><div><b>KHATA NO. / NAAM</b><span>Jamabandi ki nakal</span></div></div></div>')
J.append(f'tl.fromTo("#steps", {{opacity:0}}, {{opacity:1, duration:.3}}, {S(1) - .1:.2f}); tl.to("#steps", {{opacity:0, duration:.3}}, {S(2) - .3:.2f}); tl.set(".st", {{opacity:0}}, 0);')
for k, kw in [(1, "Apna Khata"), (2, "zila"), (3, "khata number")]:
    J.append(f'tl.fromTo("#st{k}", {{opacity:0, x:-60}}, {{opacity:1, x:0, duration:.4, ease:"back.out(1.6)", immediateRender:false}}, {wt(1, kw) - .15:.2f});'); sfx("click-soft", wt(1, kw) - .1, .3)

# ---------- 2 find your name + hissa ----------
J.append(f'tl.set("#docwrap", {{y:420, scale:.62, rotation:0}}, {S(2) - .4:.2f}); tl.to("#docwrap", {{opacity:1, duration:.4}}, {S(2) - .35:.2f});')
docpos(S(2) - .3, "nr3", .66, .6)
docpos(wt(2, "Apna naam") - .2, "nr5", 1.0, 1.0)
J.append(f'tl.fromTo("#nr{HERO}", {{backgroundColor:"rgba(255,214,0,0)"}}, {{backgroundColor:"rgba(255,214,0,.55)", duration:.45, immediateRender:false}}, {wt(2, "Apna naam") + .6:.2f});')
J.append(f'tl.fromTo("#hcirc", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:.6, ease:"power2.out", immediateRender:false}}, {wt(2, "hissa") - .1:.2f}); tl.set("#hcirc", {{strokeDashoffset:1}}, 0);')
H.append('<div class="call" id="c_hissa"><small>AAPKA HISSA</small><b>158 / 3795</b></div>')
show("#c_hissa", wt(2, "Jaise"), S(3) + .4, "opacity:0, y:40, scale:.9")
sfx("pop", wt(2, "Apna naam") + .6, .3); sfx("click-soft", wt(2, "hissa"), .3); sfx("impact-bass-1", wt(2, "Jaise"), .35)

# ---------- 3 total area ----------
docpos(S(3) - .1, "tot", .95, 1.1, -1.5)
J.append(f'tl.fromTo("#tbox", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:.6, ease:"power2.out", immediateRender:false}}, {wt(3, "kul khasre") - .1:.2f}); tl.set("#tbox", {{strokeDashoffset:1}}, 0);')
J.append(f'tl.fromTo("#tot", {{backgroundColor:"rgba(255,214,0,0)"}}, {{backgroundColor:"rgba(255,214,0,.45)", duration:.4, immediateRender:false}}, {wt(3, "kul khasre"):.2f});')
H.append('<div class="call" id="c_tot"><small>KUL AREA</small><b>3.7950 HECTARE</b></div>')
show("#c_tot", wt(3, "Yahan") - .1, S(4) + .2, "opacity:0, y:40, scale:.9")
J.append(f'tl.to("#docwrap", {{opacity:0, y:"+=80", duration:.4}}, {S(4) - .3:.2f});')
sfx("whoosh", S(3) - .1, .3); sfx("impact-bass-1", wt(3, "Yahan"), .35)

# ---------- formula boards ----------
def board(i, t0, t1, rows_html, note=""):
    H.append(f'<div class="bd" id="bd{i}">{rows_html}{f"<em>{note}</em>" if note else ""}</div>')
    J.append(f'tl.fromTo("#bd{i}", {{opacity:0, scale:.94}}, {{opacity:1, scale:1, duration:.4, ease:"power3.out", immediateRender:false}}, {t0:.2f}); tl.to("#bd{i}", {{opacity:0, y:-30, duration:.3}}, {t1 - .3:.2f}); tl.set("#bd{i}", {{opacity:0}}, 0); tl.set("#bd{i} .tk", {{opacity:0}}, 0);')
def tok(i, j, t):
    J.append(f'tl.fromTo("#bd{i} .t{j}", {{opacity:0, y:30, scale:.8}}, {{opacity:1, y:0, scale:1, duration:.4, ease:"back.out(2)", immediateRender:false}}, {t:.2f});'); sfx("click-soft", t, .28)
H.append('<div id="ftitle">FORMULA</div>')
J.append(f'tl.fromTo("#ftitle", {{opacity:0, y:-20}}, {{opacity:1, y:0, duration:.4}}, {S(4) - .1:.2f}); tl.to("#ftitle", {{opacity:0, duration:.3}}, {S(8) - .3:.2f});')
# 4 hissa x area
board(4, S(4) - .1, S(5), '<div class="tk t0 lbl">HISSA &times; TOTAL AREA</div><div class="tk t1 big">158 / 3795</div><div class="tk t2 op">&times;</div><div class="tk t3 big">3.7950 <small>HA</small></div><div class="tk t4 op">=</div><div class="tk t5 res">0.158 <small>HECTARE</small></div>')
tok(4, 0, S(4) + .3); tok(4, 1, wt(4, "158 bhaag") - .1); tok(4, 2, wt(4, "guna 3.7950") - .1); tok(4, 3, wt(4, "guna 3.7950") + .1); tok(4, 4, wt(4, "barabar") - .1); tok(4, 5, wt(4, "barabar") + .1)
sfx("impact-bass-1", wt(4, "barabar") + .1, .4)
# 5 to gaj
board(5, S(5) - .1, S(6), '<div class="tk t0 lbl">HECTARE &rarr; GAJ</div><div class="tk t1 big">0.158 <small>HA</small></div><div class="tk t2 op">&times;</div><div class="tk t3 big">11,960</div><div class="tk t4 op">=</div><div class="tk t5 res">&asymp; 1,890 <small>GAJ</small></div>',
      "1 hectare &asymp; 11,960 gaj (sq. yard)")
tok(5, 0, S(5) + .2); tok(5, 3, wt(5, "11,960") - .1); tok(5, 1, wt(5, "0.158") - .1); tok(5, 2, wt(5, "0.158")); tok(5, 4, wt(5, "yaani") - .1); tok(5, 5, wt(5, "yaani") + .1)
sfx("impact-bass-1", wt(5, "yaani") + .1, .4)
# 6 to bigha
board(6, S(6) - .1, S(7), '<div class="tk t0 lbl">GAJ &rarr; BIGHA</div><div class="tk t1 big">1,890 <small>GAJ</small></div><div class="tk t2 op">&divide;</div><div class="tk t3 big">3,025</div><div class="tk t4 op">=</div><div class="tk t5 res">&asymp; 0.62 <small>BIGHA</small></div>',
      "1 pakka bigha = 3,025 gaj (Jaipur ke aas-paas)")
tok(6, 0, S(6) + .2); tok(6, 2, wt(6, "3,025") - .2); tok(6, 3, wt(6, "3,025")); tok(6, 1, wt(6, "1,890") - .1); tok(6, 4, wt(6, "yaani") - .1); tok(6, 5, wt(6, "yaani") + .1)
sfx("impact-bass-1", wt(6, "yaani") + .1, .4)
# 7 trick
H.append('<div class="bd trick" id="bd7"><div class="tk t0 lbl">&#9733; SHORTCUT TRICK</div>'
         '<div class="tk t1 pair"><span>158 / <u>3795</u></span><span class="vs">&harr;</span><span><u>3.7950</u> HA</span></div>'
         '<div class="tk t2 note2">neeche wala number = total area (bina point)?</div>'
         '<div class="tk t3 big">158 &divide; 1,000</div><div class="tk t4 op">=</div><div class="tk t5 res">0.158 <small>HECTARE</small></div>'
         '<em>Sirf tab, jab dono number same hon</em></div>')
J.append(f'tl.fromTo("#bd7", {{opacity:0, scale:.94}}, {{opacity:1, scale:1, duration:.4, ease:"power3.out", immediateRender:false}}, {S(7) - .1:.2f}); tl.to("#bd7", {{opacity:0, y:-30, duration:.3}}, {S(8) - .3:.2f}); tl.set("#bd7", {{opacity:0}}, 0); tl.set("#bd7 .tk", {{opacity:0}}, 0);')
tok(7, 0, S(7) + .2); tok(7, 1, wt(7, "jaise 3795") - .1); tok(7, 2, wt(7, "neeche wala") - .1); tok(7, 3, wt(7, "1,000 se") - .2); tok(7, 4, wt(7, "yaani") - .1); tok(7, 5, wt(7, "yaani") + .1)
J.append(f'tl.fromTo("#bd7 u", {{backgroundColor:"rgba(255,214,0,0)"}}, {{backgroundColor:"rgba(255,214,0,.6)", duration:.3, yoyo:true, repeat:3, immediateRender:false}}, {wt(7, "jaise 3795") + .3:.2f});')
sfx("sparkle", S(7), .3)
# 8 caution
H.append('<div class="bd warn" id="bd8"><div class="tk t0 ic">&#9888;</div><div class="tk t1 wt">BIGHA HAR ILAAKE<br/>MEIN ALAG HOTA HAI</div>'
         '<div class="tk t2 wl">Jaipur ke aas-paas: <b>1 pakka bigha &asymp; 3,025 gaj</b></div><div class="tk t3 wl">Apni tehsil / patwari se <b>confirm</b> karein</div></div>')
J.append(f'tl.fromTo("#bd8", {{opacity:0, scale:.94}}, {{opacity:1, scale:1, duration:.4, ease:"power3.out", immediateRender:false}}, {S(8) - .1:.2f}); tl.to("#bd8", {{opacity:0, duration:.3}}, {S(9) - .3:.2f}); tl.set("#bd8", {{opacity:0}}, 0); tl.set("#bd8 .tk", {{opacity:0}}, 0);')
tok(8, 0, S(8)); tok(8, 1, S(8) + .2); tok(8, 2, wt(8, "Jaipur") - .1); tok(8, 3, wt(8, "confirm") - .3)
# 9 save card
H.append('<div id="save"><small>SAVE KAR LO</small><b>APNA HISSA NIKAALNE KA FORMULA</b>'
         '<div class="ch"><span>HISSA &times; TOTAL AREA</span><i>=</i><span class="g">HECTARE</span></div>'
         '<div class="ch"><span class="g">HECTARE</span><i>&times; 11,960 =</i><span class="g">GAJ</span></div>'
         '<div class="ch"><span class="g">GAJ</span><i>&divide; 3,025 =</i><span class="y">BIGHA</span></div>'
         '<div class="cta">&#128278; SAVE &nbsp;&middot;&nbsp; SHARE KARO</div></div>')
J.append(f'tl.fromTo("#save", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:.5, ease:"power3.out"}}, {S(9) - .1:.2f}); tl.fromTo("#save .ch", {{opacity:0, x:-40}}, {{opacity:1, x:0, duration:.35, stagger:.25, immediateRender:false}}, {S(9) + .3:.2f}); tl.to("#save .cta", {{scale:1.07, duration:.35, yoyo:true, repeat:5}}, {wt(9, "share"):.2f});')
sfx("riser", S(9) - .4, .3); sfx("sparkle", wt(9, "share"), .3)

# ---------- captions ----------
HI = ["Jamabandi", "hissa", "158/3795", "Apna Khata", "kul khasre", "3.7950 hectare", "hissa guna total area", "0.158 hectare", "11,960", "1,890 gaj", "3,025", "0.62 bigha", "1,000", "save"]
def hl(t):
    for h in sorted(HI, key=len, reverse=True):
        i = t.find(h)
        if i >= 0 and "<span" not in t[max(0, i - 25):i] and "span" not in t[i:i + len(h)]: t = t[:i] + '<span class="y">' + h + '</span>' + t[i + len(h):]
    return t
ci = 0
for n, ph in enumerate(PH):
    if ph["e"] - ph["s"] < .1: continue
    words = ph["t"].split(); chunks = []; cur = ""
    for w_ in words:
        if cur and len(cur) + 1 + len(w_) > 22: chunks.append(cur); cur = w_
        else: cur = (cur + " " + w_).strip()
    chunks.append(cur)
    tot_ = sum(len(c) for c in chunks); t = ph["s"]; nx = PH[n + 1]["s"] if n + 1 < len(PH) else END
    for j, c in enumerate(chunks):
        d = (ph["e"] - ph["s"]) * len(c) / tot_
        a_ = max(.02, t if j else t - .04); b_ = (min(t + d + .25, nx - .08) if j == len(chunks) - 1 else t + d - .03)
        H.append(f'<div class="cp" id="cp{ci}"><div>{hl(c)}</div></div>')
        J.append(f'tl.fromTo("#cp{ci}", {{opacity:0, scale:.88}}, {{opacity:1, scale:1, duration:.1}}, {a_:.2f}); tl.to("#cp{ci}", {{opacity:0, duration:.04}}, {b_ - .04:.2f});')
        t += d; ci += 1
if os.path.exists(f"{P}/assets/face.mp4"):
    H.append('<video id="face" class="clip" src="assets/face.mp4" data-start="0" data-duration="1.0" data-track-index="2" muted playsinline></video>')
    J.append('tl.set("#face", {opacity:1}, 0); tl.to("#face", {opacity:0, scale:1.06, duration:.12}, .8);')
H.append('<div id="cred">Sample document &middot; names made up &middot; 1 hectare = 11,959.9 sq. yard &middot; bigha ka maap ilaake ke hisaab se alag ho sakta hai</div>')

CSS = """@font-face{font-family:Anton;src:url(assets/fonts/anton.woff2)}@font-face{font-family:Mont;font-weight:700;src:url(assets/fonts/mont700.woff2)}@font-face{font-family:Mont;font-weight:800;src:url(assets/fonts/mont800.woff2)}@font-face{font-family:Mont;font-weight:900;src:url(assets/fonts/mont900.woff2)}
@font-face{font-family:Deva;font-weight:100 900;src:url(assets/fonts/notodeva.woff2);unicode-range:U+0900-097F,U+1CD0-1CF9,U+200C-200D,U+20A8,U+20B9,U+25CC,U+A830-A839,U+A8E0-A8FF}@font-face{font-family:Deva;font-weight:100 900;src:url(assets/fonts/notolatin.woff2);unicode-range:U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD}@font-face{font-family:Tiro;src:url(assets/fonts/tiro.woff2)}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#0f0d0a}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif;background:radial-gradient(120% 80% at 50% 30%,#2a2216 0%,#120f0b 60%,#0a0907 100%)}
#root:before{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(201,162,74,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(201,162,74,.06) 1px,transparent 1px);background-size:60px 60px}
.y{color:#111;background:#F2B23E;border-radius:6px;padding:0 6px}
#face{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:40}
#cred{position:absolute;left:40px;right:40px;top:1690px;text-align:center;font:700 18px Mont;color:rgba(255,255,255,.6);z-index:20}
#docwrap{position:absolute;left:70px;top:260px;width:940px;opacity:0;z-index:5}
#doc{position:relative;width:940px;padding:34px 36px 40px;background:#fff;border-radius:4px;box-shadow:0 40px 90px rgba(0,0,0,.7);color:#111;font-family:Deva,Mont,sans-serif;overflow:hidden}
#doc .top{position:relative;display:flex;align-items:center;height:110px}#doc .seal{flex:none;width:84px;height:84px;border-radius:50%;border:4px double #8a7a5a;display:flex;align-items:center;justify-content:center;font:700 17px Deva;color:#8a7a5a}
#doc .top>b{flex:1;text-align:center;font:800 35px Deva;padding-right:120px}#doc .pp{position:absolute;right:0;top:0;text-align:right;font:500 17px/1.35 Deva}
#doc .meta{display:grid;grid-template-columns:1fr 1.35fr;column-gap:20px;margin-top:12px;font:500 21px Deva}#doc .meta div{display:flex;flex-direction:column;gap:6px}
#doc .lab{margin-top:14px;height:40px;font:800 23px Deva}
#nlist .nr{display:flex;align-items:center;height:50px;font:500 23px Deva;border-radius:4px;padding:0 6px 0 18px}#nlist .nm{width:330px;flex:none}#nlist .hs{width:250px;flex:none}#nlist .hs b{font:700 23px Deva,Mont}#nlist .kt{color:#222}
#doc .kh{margin-top:26px;border-top:2px solid #111}#doc .kr{display:grid;grid-template-columns:160px 115px 130px 105px 130px 100px 1fr;align-items:center;height:54px;font:500 21px Deva;padding:0 4px;border-radius:4px}
#doc .khd{height:76px;font:800 19px/1.2 Deva;border-bottom:2px solid #111}#doc .tot{height:64px;border-top:2px solid #111;border-bottom:2px solid #111;font:800 23px Deva}#doc .tot b{font:800 25px Deva,Mont}
#doc .foot{position:relative;margin-top:24px;font:500 20px Deva}#doc .foot>b{font:800 22px Deva}#doc .fg{display:grid;grid-template-columns:1fr 1fr;row-gap:8px;margin-top:10px;padding-right:150px}
#doc .qr{position:absolute;right:0;top:0;width:120px;height:120px;border:3px solid #111;background:repeating-linear-gradient(45deg,#ddd 0 6px,#fff 6px 12px);display:flex;align-items:center;justify-content:center;text-align:center;font:900 16px Mont}
#doc .wm{position:absolute;left:50%;top:45%;translate:-50% -50%;rotate:-30deg;font:900 170px Mont;letter-spacing:.1em;color:rgba(180,38,26,.07);pointer-events:none}
#mark{position:absolute;left:0;top:0;width:940px;height:2600px;pointer-events:none;overflow:visible}#mark ellipse,#mark rect{fill:none;stroke:#D7261E;stroke-width:6;stroke-dasharray:1;stroke-dashoffset:1}
#hook{position:absolute;left:60px;right:60px;top:110px;z-index:16;text-align:center;padding:26px 20px 24px;border-radius:10px;border:1.5px solid #C9A24A;background:linear-gradient(135deg,rgba(14,12,9,.94),rgba(34,27,18,.94))}
#hook small{display:block;font:800 30px Mont;letter-spacing:.3em;color:#F3E6C8}#hook b{display:block;margin-top:8px;font:400 96px/1.02 Anton;background:linear-gradient(180deg,#F7E3A8,#C9A24A);-webkit-background-clip:text;color:transparent}
#hook span{display:inline-block;margin-top:16px;padding:8px 22px;border-radius:6px;background:#F2B23E;color:#111;font:900 34px Mont}
#steps{position:absolute;left:70px;right:70px;top:300px;z-index:16;opacity:0}#steps>small{display:block;text-align:center;font:800 28px Mont;letter-spacing:.24em;color:#C9A24A;margin-bottom:30px}
.st{display:flex;align-items:center;gap:26px;margin-top:26px;padding:26px 30px;border-radius:12px;border:1.5px solid rgba(201,162,74,.7);background:linear-gradient(135deg,rgba(20,17,12,.95),rgba(40,32,20,.95))}
.st i{flex:none;width:86px;height:86px;border-radius:50%;background:#C9A24A;color:#111;display:flex;align-items:center;justify-content:center;font:400 54px Anton;font-style:normal}
.st b{display:block;font:400 52px/1.05 Anton;color:#F7E3A8;letter-spacing:.02em}.st span{display:block;margin-top:6px;font:700 26px Mont;color:#E9DFC8}
.call{position:absolute;left:0;right:0;top:1180px;margin:0 auto;width:max-content;opacity:0;z-index:15;text-align:center;padding:18px 40px;border-radius:12px;border:2px solid #F2B23E;background:rgba(14,12,9,.95);box-shadow:0 20px 50px rgba(0,0,0,.6)}
.call small{display:block;font:800 26px Mont;letter-spacing:.24em;color:#F3E6C8}.call b{display:block;margin-top:6px;font:400 88px/1 Anton;color:#F2B23E}
#ftitle{position:absolute;left:0;right:0;top:150px;text-align:center;opacity:0;z-index:14;font:800 30px Mont;letter-spacing:.5em;color:#C9A24A}
.bd{position:absolute;left:60px;right:60px;top:240px;opacity:0;z-index:15;text-align:center;padding:40px 30px 36px;border-radius:16px;border:1.5px solid #C9A24A;background:linear-gradient(160deg,rgba(18,15,10,.96),rgba(38,30,19,.96));box-shadow:0 30px 70px rgba(0,0,0,.6)}
.bd .lbl{font:800 32px Mont;letter-spacing:.18em;color:#F3E6C8}.bd .big{margin-top:24px;font:400 120px/1 Anton;color:#F7E3A8}.bd .big small,.bd .res small{font-size:.45em;letter-spacing:.06em}
.bd .op{margin-top:14px;font:400 84px/1 Anton;color:#C9A24A}.bd .res{display:inline-block;margin-top:18px;padding:14px 34px;border-radius:12px;background:linear-gradient(180deg,#3CE65A,#22B541);color:#0b2410;font:400 120px/1 Anton}
.bd em{display:block;margin-top:26px;font:700 28px Mont;font-style:normal;color:#E9DFC8}
.trick .pair{display:flex;justify-content:center;align-items:center;gap:26px;margin-top:22px;font:400 86px/1.1 Anton;color:#F7E3A8}.trick .pair .vs{color:#C9A24A}.trick u{text-decoration:none;border-radius:8px;padding:0 6px}
.trick .note2{margin-top:16px;font:800 30px Mont;color:#F2B23E}.trick .big{font-size:100px}
.warn{border-color:#F2B23E}.warn .ic{font:400 140px/1 Mont;color:#F2B23E}.warn .wt{margin-top:10px;font:400 96px/1.02 Anton;color:#F7E3A8}.warn .wl{margin-top:28px;font:700 34px/1.3 Mont;color:#E9DFC8}.warn .wl b{color:#F2B23E}
#save{position:absolute;left:60px;right:60px;top:220px;opacity:0;z-index:16;text-align:center;padding:36px 30px;border-radius:16px;border:2px solid #C9A24A;background:linear-gradient(160deg,rgba(18,15,10,.97),rgba(38,30,19,.97))}
#save>small{display:block;font:800 30px Mont;letter-spacing:.3em;color:#F2B23E}#save>b{display:block;margin-top:10px;font:400 66px/1.05 Anton;color:#F7E3A8}
#save .ch{display:flex;justify-content:center;align-items:center;gap:16px;margin-top:30px;font:400 50px Anton;color:#F3E6C8}#save .ch i{font-style:normal;color:#C9A24A}#save .ch .g{padding:4px 16px;border-radius:8px;background:#3CE65A;color:#0b2410}#save .ch .y{padding:4px 16px;border-radius:8px;background:#F2B23E;color:#111}
#save .cta{display:inline-block;margin-top:40px;padding:14px 36px;border-radius:8px;background:#C9A24A;color:#111;font:900 40px Mont;letter-spacing:.12em}
.cp{position:absolute;left:40px;right:40px;top:1470px;text-align:center;opacity:0;z-index:35}
.cp div{display:inline-block;padding:4px 20px 8px;border-radius:10px;background:#fff;font:900 60px/1.12 Mont;color:#111;box-shadow:0 8px 24px rgba(0,0,0,.45)}"""
audio = (f'<audio id="voice" class="clip" src="assets/voice.wav" data-start="0" data-duration="{END}" data-track-index="1" data-volume="1"></audio><audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.12" data-fade-out="1.5"></audio>' if VOICE
         else f'<audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.5" data-fade-out="1.5"></audio>')
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
