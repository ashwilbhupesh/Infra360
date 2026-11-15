"""SC/ST ki zameen — Rajasthan Tenancy Act 1955 Sec 42. Graphics-heavy reel. Jamabandi is a SAMPLE (names changed)."""
import json, os, math
P = "proj"
LINES = [
    "कई लोग SC/ST की सस्ती ज़मीन देखकर खुश हो जाते हैं, और गलत तरीकों से उसे अपनाने के चक्कर में अपने लाखों रुपए और समय गँवा देते हैं।",
    "क्योंकि SC/ST की ज़मीन आम तौर पर General या OBC के नाम हो ही नहीं सकती।",
    "इन परिवारों की ज़मीन सुरक्षित रखने के लिए राजस्थान काश्तकारी अधिनियम 1955 की धारा 42 कहती है: SC की ज़मीन सिर्फ़ SC को, और ST की ज़मीन सिर्फ़ ST को बेची, दी या वसीयत की जा सकती है।",
    "अगर कोई और इसे रजिस्ट्री करवा के भी खरीद ले, तो वो सौदा शून्य है, void, यानी सरकार की नज़र में उसकी कोई कीमत नहीं।",
    "ऐसी ज़मीन ना बेचने वाले की रहती है, क्योंकि उसने बेच दी, और ना खरीदने वाले की, क्योंकि खरीद गैरकानूनी है। खरीदार को बेदखल किया जा सकता है, और ज़मीन सरकार की, यानी राज रकबा, हो सकती है।",
    "हाई कोर्ट भी साफ़ कह चुका है: ऐसी ज़मीन पर सालों कब्ज़ा रखने से भी खरीदार मालिक नहीं बनता।",
    "कई लोग जुगाड़ करते हैं: किसी SC/ST रिश्तेदार के नाम करवा लेंगे, या पावर ऑफ़ अटॉर्नी ले लेंगे।",
    "लेकिन याद रखिए, जब तक आप कानूनी तौर पर खुद मालिक नहीं बनते, इन सब शॉर्टकट्स में आगे केस और मुकदमे होने की पूरी संभावना है। आपका पैसा, समय और एनर्जी, तीनों जा सकते हैं।",
    "इसलिए SC/ST की सस्ती ज़मीन देखकर खुश मत होइए। खरीदने से पहले जमाबंदी में खातेदार की जाति ज़रूर चेक कीजिए।",
    "ये वीडियो उस दोस्त को भेजिए जो सस्ती ज़मीन ढूँढ रहा है।",
]
VOICE = os.path.exists("rec/phrases.json")
if VOICE: PH = json.load(open("rec/phrases.json"))
else:
    PH = []; t = .3
    for l in LINES:
        d = len(l) / 14 + .3 + (.6 if not PH else 0); PH.append({"s": round(t, 2), "e": round(t + d, 2), "t": l}); t += d + .3
def S(k): return PH[k]["s"]
def E(k): return PH[k]["e"]
def wt(k, w):
    t = PH[k]["t"]; i = t.find(w); assert i >= 0, (k, w)
    if PH[k].get("parts"):
        off = 0
        for p in PH[k]["parts"]:
            if i < off + len(p["t"]) + 1: return p["s"] + (p["e"] - p["s"]) * (i - off) / len(p["t"])
            off += len(p["t"]) + 1
    return S(k) + (E(k) - S(k)) * i / len(t)
END = round(E(9) + 1.0, 2)
H, J, SFX = [], [], []
def sfx(n, t, v=.3): SFX.append(f'<audio id="sx{len(SFX)}" class="clip" src="assets/sfx/{n}.mp3" data-start="{max(0, t):.2f}" data-duration="2" data-track-index="{20 + len(SFX)}" data-volume="{v}"></audio>')
def inn(sel, t, frm="opacity:0, y:40, scale:.95", ease="back.out(1.6)", d=.45):
    J.append(f'tl.set("{sel}", {{opacity:0}}, 0); tl.fromTo("{sel}", {{{frm}}}, {{opacity:1, x:0, y:0, scale:1, rotation:0, duration:{d}, ease:"{ease}", immediateRender:false}}, {t:.2f});')
def out(sel, t, d=.3): J.append(f'tl.to("{sel}", {{opacity:0, duration:{d}}}, {t - d:.2f});')
exec(open("fake.py").read())

# ---------- background photos (always something moving) ----------
def bgp(bid, img, t0, t1, op=.55, z0=1.0, z1=1.12, blur=0):
    H.append(f'<div class="bgp" id="{bid}"><img src="assets/img/{img}.jpg" style="{f"filter:blur({blur}px) brightness(.85)" if blur else ""}"/></div>')
    J.append(f'tl.set("#{bid}", {{opacity:0}}, 0); tl.to("#{bid}", {{opacity:{op}, duration:.5}}, {max(0, t0):.2f}); tl.fromTo("#{bid} img", {{scale:{z0}}}, {{scale:{z1}, duration:{t1 - t0 + .5:.2f}, ease:"none", immediateRender:false}}, {max(0, t0):.2f}); tl.to("#{bid}", {{opacity:0, duration:.5}}, {t1 - .2:.2f});')

# ---------- 0 HOOK: board ----------
bgp("b0", "board", 0, S(1), op=1, z0=1.0, z1=1.0)
H.append('<div id="sign"><div class="sa"><b>सस्ती ज़मीन</b><span>बिकाऊ &middot; ₹ आधे दाम</span></div><div class="sb"></div></div><div id="signt"><b>₹ लाखों फँसे</b><span>सावधान!</span></div>')
tf = wt(0, "गलत")
J.append(f'tl.set("#sign .sb", {{opacity:0}}, 0); tl.fromTo("#sign .sa", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.4, ease:"back.out(2)"}}, .2); tl.to("#sign .sa", {{rotationX:90, opacity:0, duration:.25}}, {tf:.2f}); tl.fromTo("#sign .sb", {{rotationX:-90, opacity:0}}, {{rotationX:0, opacity:1, duration:.3, immediateRender:false}}, {tf + .25:.2f}); tl.to("#sign, #signt", {{x:8, duration:.05, yoyo:true, repeat:7}}, {tf + .55:.2f}); tl.to("#sign, #signt", {{opacity:0, duration:.3}}, {S(1) - .3:.2f}); tl.set("#signt", {{opacity:0}}, 0); tl.fromTo("#signt", {{opacity:0, rotationX:-90}}, {{opacity:1, rotationX:0, duration:.3, immediateRender:false}}, {tf + .25:.2f});')
H.append('<div id="hook"><small>सावधान</small><b>SC/ST की सस्ती ज़मीन?</b></div>')
inn("#hook", .1, "opacity:0, y:-40"); out("#hook", S(1))
H.append('<div id="rain">' + "".join(f'<i style="left:{40 + (k * 131) % 1000}px;font-size:{60 + (k * 23) % 50}px">₹</i>' for k in range(14)) + '</div>')
J.append(f'tl.set("#rain", {{opacity:1}}, {wt(0, "लाखों") - .2:.2f}); tl.fromTo("#rain i", {{y:-150, opacity:0, rotation:-20}}, {{y:2100, opacity:1, rotation:30, duration:1.8, stagger:{{each:.09}}, ease:"power1.in", immediateRender:false}}, {wt(0, "लाखों") - .2:.2f}); tl.set("#rain", {{opacity:0}}, {S(1):.2f}); tl.set("#rain", {{opacity:0}}, 0);')
sfx("impact-bass-1", 0, .45); sfx("whoosh", tf + .2, .35); sfx("impact-bass-1", tf + .3, .4)

# 'sasti zameen dekhkar khush' -> daydream illustration
H.append('<div id="happy"><img src="assets/img/happy.jpg"/><span>प्रतीकात्मक चित्र</span></div>')
J.append(f'tl.set("#happy", {{opacity:0}}, 0); tl.fromTo("#happy", {{opacity:0, scale:.7, rotation:-5, y:60}}, {{opacity:1, scale:1, rotation:-2, y:0, duration:.4, ease:"back.out(1.8)", immediateRender:false}}, .95); tl.to("#happy", {{opacity:0, x:200, rotation:6, duration:.3}}, {wt(0, "गलत") - .2:.2f});')
sfx("pop", .95, .3)
# 'galat tareekon se apnane' -> illustration
H.append('<div id="grab"><img src="assets/img/grab.jpg"/><span>प्रतीकात्मक चित्र</span></div>')
tg_ = wt(0, "गलत") - .1
J.append(f'tl.set("#grab", {{opacity:0}}, 0); tl.fromTo("#grab", {{opacity:0, scale:.7, rotation:5}}, {{opacity:1, scale:1, rotation:2, duration:.35, ease:"back.out(1.8)", immediateRender:false}}, {tg_:.2f}); tl.to("#grab", {{opacity:0, x:-200, rotation:-6, duration:.3}}, {wt(0, "लाखों") - .2:.2f});')
sfx("whoosh", tg_, .3)
# 'lakhon rupaye gawa dete hain' -> loss image pop-up
H.append('<div id="loss"><img src="assets/img/loss.jpg"/><span>प्रतीकात्मक चित्र</span></div>')
tl_ = wt(0, "लाखों") - .15
J.append(f'tl.set("#loss", {{opacity:0}}, 0); tl.fromTo("#loss", {{opacity:0, scale:.6, rotation:-6, y:80}}, {{opacity:1, scale:1, rotation:-2, y:0, duration:.4, ease:"back.out(1.8)", immediateRender:false}}, {tl_:.2f}); tl.to("#loss", {{opacity:0, scale:.95, duration:.3}}, {S(1) - .25:.2f});')
sfx("whoosh", tl_, .3)
# ---------- 1 Jamabandi: jaati ----------
bgp("b1", "bg_fields", S(1) - .3, S(2) + .2, op=.4, blur=3)
H.append('<div class="doc" id="d1"><div class="im" id="d1i"><img src="assets/img/jama_real.jpg"/>' + fake_overlay(940 / 1082, hl=True) + '</div></div>')
inn("#d1", S(1) - .2, "opacity:0, y:120, rotation:-4"); out("#d1", S(2) + .1)
J.append(f'tl.set("#d1i", {{transformOrigin:"0 0"}}, 0); tl.to("#d1i", {{scale:1.4, x:-20, y:-290, duration:.8, ease:"power2.inOut"}}, {S(1) + .5:.2f}); tl.set(".hlb", {{opacity:0, scale:.7}}, 0);')
for i in range(3): J.append(f'tl.to("#hlb{i}", {{opacity:1, scale:1, duration:.25, ease:"back.out(2.5)"}}, {S(1) + 1.2 + i * .2:.2f});')
H.append('<div class="tagx" id="tg1">उदाहरण &middot; नाम बदले गए हैं</div>'); inn("#tg1", S(1) + .3, "opacity:0"); out("#tg1", S(2) + .1)
for j, (lab, kw) in enumerate([("General", "General"), ("OBC", "OBC")]):
    H.append(f'<div class="nox" id="nx{j}" style="left:{60 + j * 520}px"><b>{lab}</b><i>&#10005;</i></div>')
    inn(f"#nx{j}", wt(1, kw) - .1, "opacity:0, scale:2.2", "power4.out", .3); out(f"#nx{j}", S(2) + .1); sfx("impact-bass-1", wt(1, kw) - .05, .3)

# ---------- 2 Section 42 ----------
bgp("b2", "stamp", S(2) - .3, S(3) - .1, op=.3, blur=6)
H.append('<div class="law" id="law"><small>राजस्थान काश्तकारी अधिनियम, 1955</small><b>धारा 42</b>'
         '<div class="ln" id="ln0"><span class="c">SC</span><i>&rarr;</i><span class="c">SC</span><em class="ok">&#10003;</em></div>'
         '<div class="ln" id="ln1"><span class="c">ST</span><i>&rarr;</i><span class="c">ST</span><em class="ok">&#10003;</em></div>'
         '<div class="ln" id="ln2"><span class="c">SC/ST</span><i>&rarr;</i><span class="c g">General / OBC</span><em class="no">&#10005;</em></div>'
         '<div class="vb">बेचना &middot; दान &middot; वसीयत</div></div>')
H.append('<div id="book"><img src="assets/img/act_book.jpg"/></div>')
inn("#book", S(2) + .2, "opacity:0, y:120, rotation:-8, scale:.8"); out("#book", wt(2, "धारा") - .1)
sfx("whoosh", S(2) + .2, .3)
inn("#law", wt(2, "धारा") - .3, "opacity:0, y:60"); out("#law", S(3))
J.append(f'tl.fromTo("#law b", {{scale:1.8, opacity:0}}, {{scale:1, opacity:1, duration:.45, ease:"power4.out", immediateRender:false}}, {wt(2, "धारा") - .1:.2f}); tl.set("#law b", {{opacity:0}}, 0);')
for j, kw in enumerate(["SC की ज़मीन", "ST की ज़मीन", "बेची"]):
    inn(f"#ln{j}", wt(2, kw) - .1, "opacity:0, x:-80", "power3.out", .35); sfx("click-soft", wt(2, kw), .3)
inn("#law .vb", wt(2, "बेची") + .4, "opacity:0, y:20")
sfx("impact-bass-1", wt(2, "धारा"), .4)

# ---------- 3 VOID ----------
bgp("b3", "stamp", S(3) - .3, S(4) - .1, op=1, z0=1.12, z1=1.0)
H.append('<div class="lbl1" id="l3">रजिस्ट्री हो गई&hellip;</div>'); inn("#l3", S(3) + .1, "opacity:0, y:-30"); out("#l3", S(4))
H.append('<div id="void"><b>शून्य</b><span>VOID</span></div>')
tv = wt(3, "शून्य") - .1
J.append(f'tl.set("#void", {{opacity:0}}, 0); tl.fromTo("#void", {{opacity:0, scale:3.2, rotation:-25}}, {{opacity:1, scale:1, rotation:-12, duration:.28, ease:"power4.in", immediateRender:false}}, {tv:.2f}); tl.to("#root", {{x:10, duration:.04, yoyo:true, repeat:5}}, {tv + .28:.2f}); tl.to("#void", {{opacity:0, duration:.3}}, {S(4) - .1:.2f});')
H.append('<div class="pill" id="p3">सरकार की नज़र में कोई कीमत नहीं</div>'); inn("#p3", wt(3, "सरकार"), "opacity:0, y:30"); out("#p3", S(4))
sfx("impact-bass-1", tv + .25, .55)

# ---------- 4 neither seller nor buyer -> raj rakba ----------
bgp("b4", "bg_fields", S(4) - .3, S(5) - .1, op=.45, blur=2)
PIC = '<svg viewBox="0 0 100 100"><circle cx="50" cy="32" r="18" fill="currentColor"/><path d="M14 96c2-24 18-36 36-36s34 12 36 36z" fill="currentColor"/></svg>'
H.append(f'<div class="who" id="w0" style="left:60px"><div class="av">{PIC}</div><b>बेचने वाला</b><span>बेच दी</span><i>&#10005;</i></div>'
         f'<div class="who" id="w1" style="left:580px"><div class="av">{PIC}</div><b>खरीदने वाला</b><span>गैरकानूनी खरीद</span><i>&#10005;</i></div>')
inn("#w0", S(4) + .1, "opacity:0, x:-80"); inn("#w1", wt(4, "खरीदने") - .1, "opacity:0, x:80")
for j, kw in enumerate(["बेच दी", "गैरकानूनी"]):
    J.append(f'tl.set("#w{j} i", {{opacity:0}}, 0); tl.fromTo("#w{j} i", {{opacity:0, scale:2.5}}, {{opacity:1, scale:1, duration:.25, ease:"power4.in", immediateRender:false}}, {wt(4, kw) + .2:.2f});'); sfx("impact-bass-1", wt(4, kw) + .4, .3)
out("#w0, #w1", wt(4, "बेदखल") - .2)
H.append('<div id="evict"><b>बेदखली</b><span>खरीदार को ज़मीन से हटाया जा सकता है</span></div>'); inn("#evict", wt(4, "बेदखल") - .2, "opacity:0, scale:.8"); out("#evict", wt(4, "राज रकबा") - .3)
H.append('<div id="raj"><div class="gv"><svg viewBox="0 0 120 100"><path d="M10 40 60 10 110 40z" fill="#FFD23F"/><rect x="18" y="44" width="84" height="6" fill="#FFD23F"/>' + "".join(f'<rect x="{24 + k * 18}" y="54" width="9" height="32" fill="#FFD23F"/>' for k in range(5)) + '<rect x="12" y="88" width="96" height="8" fill="#FFD23F"/></svg></div><b>राज रकबा</b><span>ज़मीन सरकार की हो सकती है</span></div>')
inn("#raj", wt(4, "राज रकबा") - .3, "opacity:0, y:60, scale:.9"); out("#raj", S(5))
sfx("whoosh", wt(4, "राज रकबा") - .3, .3)

# ---------- 5 High Court ----------
bgp("b5", "hc", S(5) - .3, S(6) - .1, op=.7, blur=0)
H.append('<div id="hc"><div class="cb" style="display:none"><svg viewBox="0 0 200 120"><path d="M20 44 100 8 180 44z" fill="#E8D6A8"/><rect x="28" y="48" width="144" height="8" fill="#E8D6A8"/>' + "".join(f'<rect x="{36 + k * 26}" y="60" width="14" height="44" fill="#E8D6A8"/>' for k in range(6)) + '<rect x="18" y="106" width="164" height="10" fill="#E8D6A8"/></svg></div>'
         '<small>राजस्थान हाई कोर्ट</small><div class="q">&ldquo;धारा 42 के खिलाफ़ खरीदी ज़मीन पर<br/>सालों के कब्ज़े से भी खातेदारी नहीं मिलती&rdquo;</div>'
         '<div class="eq"><span>सालों का कब्ज़ा</span><i>&ne;</i><span class="y">मालिकाना हक</span></div><em>सीता राम बनाम राजस्व मंडल (2012) &middot; 2025 में भी दोहराया</em></div>')
inn("#hc", S(5) - .1, "opacity:0, y:60"); out("#hc", S(6))
J.append(f'tl.set("#hc .eq", {{opacity:0}}, 0); tl.fromTo("#hc .eq", {{opacity:0, scale:.8}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)", immediateRender:false}}, {wt(5, "सालों") - .1:.2f});')
sfx("impact-bass-1", S(5), .4); sfx("click-soft", wt(5, "सालों"), .3)

# ---------- 6 jugaad ----------
bgp("b6", "cash", S(6) - .3, S(7) + .4, op=.85, z0=1.0, z1=1.15)
H.append('<div class="lbl1" id="l6">जुगाड़ &#128064;</div>'); inn("#l6", S(6), "opacity:0, y:-30"); out("#l6", wt(6, "रिश्तेदार") - .2)
for j, (t1_, t2_, kw) in enumerate([("रिश्तेदार के नाम", "SC/ST रिश्तेदार के नाम रजिस्ट्री", "रिश्तेदार"), ("पावर ऑफ़ अटॉर्नी", "&lsquo;सब कुछ मेरे ज़रिए होगा&rsquo;", "पावर")]):
    H.append(f'<div class="jg" id="jg{j}" style="top:{1130 + j * 170}px"><b>{t1_}</b><span>{t2_}</span><div class="ck"></div></div>')
    inn(f"#jg{j}", wt(6, kw) - .1, "opacity:0, x:-120", "back.out(1.6)", .4); sfx("pop", wt(6, kw), .3)


# family tree (रिश्तेदार) + PoA document
FT = ('<svg viewBox="0 0 900 520"><defs><marker id="fa" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#FFD23F"/></marker></defs>'
      '<g class="ftl" stroke="#cfd8e6" stroke-width="5" fill="none"><path d="M450 130 V200 H190 V260"/><path d="M450 200 H710 V260"/></g>'
      '<g class="fn n0"><rect x="300" y="30" width="300" height="100" rx="16" fill="#2b3a52" stroke="#cfd8e6" stroke-width="3"/><text x="450" y="74" text-anchor="middle" fill="#fff" font-size="34" font-weight="800">SC/ST खातेदार</text><text x="450" y="112" text-anchor="middle" fill="#FFD23F" font-size="26" font-weight="700">ज़मीन बेचने वाला</text></g>'
      '<g class="fn n1"><rect x="40" y="260" width="300" height="110" rx="16" fill="#1f4d2b" stroke="#2FD158" stroke-width="3"/><text x="190" y="306" text-anchor="middle" fill="#fff" font-size="32" font-weight="800">SC/ST रिश्तेदार</text><text x="190" y="346" text-anchor="middle" fill="#2FD158" font-size="26" font-weight="700">काग़ज़ में नाम</text></g>'
      '<g class="fn n2"><rect x="560" y="260" width="300" height="110" rx="16" fill="#5a1616" stroke="#FF6B6B" stroke-width="3"/><text x="710" y="306" text-anchor="middle" fill="#fff" font-size="32" font-weight="800">असली खरीदार</text><text x="710" y="346" text-anchor="middle" fill="#FFD23F" font-size="26" font-weight="700">पैसा आपका</text></g>'
      '<path class="fdl" d="M560 315 C470 430 410 430 340 330" stroke="#FFD23F" stroke-width="6" stroke-dasharray="14 10" fill="none" marker-end="url(#fa)"/>'
      '<text class="fq" x="450" y="470" text-anchor="middle" fill="#FFD23F" font-size="40" font-weight="900">नाम किसी का · पैसा आपका ?</text></svg>')
H.append(f'<div id="ftree">{FT}</div>')
tr = wt(6, "रिश्तेदार") - .2
J.append(f'tl.set("#ftree", {{opacity:0}}, 0); tl.set("#ftree .fn, #ftree .ftl, #ftree .fdl, #ftree .fq", {{opacity:0}}, 0); tl.to("#ftree", {{opacity:1, duration:.25}}, {tr:.2f});'
         f'tl.fromTo("#ftree .n0", {{opacity:0, y:-20}}, {{opacity:1, y:0, duration:.3, immediateRender:false}}, {tr:.2f}); tl.to("#ftree .ftl", {{opacity:1, duration:.3}}, {tr + .25:.2f});'
         f'tl.fromTo("#ftree .n1", {{opacity:0, scale:.7, svgOrigin:"190 315"}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)", immediateRender:false}}, {tr + .45:.2f});'
         f'tl.fromTo("#ftree .n2", {{opacity:0, scale:.7, svgOrigin:"710 315"}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)", immediateRender:false}}, {tr + .7:.2f});'
         f'tl.to("#ftree .fdl", {{opacity:1, duration:.2}}, {tr + 1.0:.2f}); tl.fromTo("#ftree .fdl", {{strokeDashoffset:300}}, {{strokeDashoffset:0, duration:.8, immediateRender:false}}, {tr + 1.0:.2f}); tl.to("#ftree .fq", {{opacity:1, duration:.3}}, {tr + 1.3:.2f});'
         f'tl.to("#ftree", {{opacity:0, duration:.25}}, {wt(6, "पावर") - .3:.2f});')
sfx("pop", tr + .45, .25); sfx("pop", tr + .7, .25)
H.append('<div id="poa"><img src="assets/img/poa.jpg"/><span>प्रतीकात्मक चित्र</span></div>')
tp_ = wt(6, "पावर") - .2
J.append(f'tl.set("#poa", {{opacity:0}}, 0); tl.fromTo("#poa", {{opacity:0, y:140, rotation:6, scale:.85}}, {{opacity:1, y:0, rotation:-3, scale:1, duration:.45, ease:"back.out(1.6)", immediateRender:false}}, {tp_:.2f}); tl.to("#poa", {{rotation:6, y:"+=60", opacity:0, duration:.5, ease:"power2.in"}}, {wt(7, "केस") - .2:.2f});')
sfx("whoosh", tp_, .3)
# ---------- 7 litigation ----------
bgp("b7", "court", S(7) - .2, S(8) - .1, op=1, z0=1.12, z1=1.0)
tk = wt(7, "केस") - .2
J.append(f'tl.to("#jg0, #jg1", {{rotation:(i) => i ? 6 : -6, y:"+=40", opacity:0, duration:.5, ease:"power2.in"}}, {tk:.2f}); tl.set(".ck", {{opacity:0}}, 0); tl.to(".ck", {{opacity:1, duration:.1}}, {tk - .2:.2f});')
sfx("impact-bass-1", tk - .2, .4)
H.append('<div id="case"><b>केस &middot; मुकदमे</b><span>सालों तक</span></div>'); inn("#case", tk + .1, "opacity:0, scale:1.6", "power4.out", .3); out("#case", wt(7, "पैसे") - .2)
H.append('<div id="mt">' + "".join(f'<div class="m" id="m{j}"><b>{a}</b><div class="bar"><i></i></div></div>' for j, a in enumerate(["₹ पैसा", "&#8987; समय", "&#9889; एनर्जी"])) + '</div>')
for j, kw in enumerate(["पैसे", "समय,", "एनर्जी"]):
    inn(f"#m{j}", wt(7, kw) - .15, "opacity:0, x:-60", "power3.out", .3)
    J.append(f'tl.fromTo("#m{j} .bar i", {{scaleX:1}}, {{scaleX:.08, duration:1.2, ease:"power2.in", immediateRender:false}}, {wt(7, kw):.2f});')
    sfx("click-soft", wt(7, kw), .3)
out("#mt", S(8))

# ---------- 8 checklist ----------
bgp("b8", "bg_fields", S(8) - .3, S(9) + .1, op=.55)
H.append('<div id="chk"><small>खरीदने से पहले</small><b>ये ज़रूर चेक करें</b>'
         '<div class="it" id="it0"><i>&#10003;</i>जमाबंदी देखें</div><div class="it" id="it1"><i>&#10003;</i>खातेदार की <u>जाति</u> देखें</div><div class="it" id="it2"><i>&#10003;</i>SC/ST हो तो <u>धारा 42</u> याद रखें</div>'
         '<div class="no2">सस्ती ज़मीन &ne; सही सौदा</div></div>')
inn("#chk", S(8) - .1, "opacity:0, y:60"); out("#chk", S(9))
for j, kw in enumerate(["जमाबंदी", "जाति", "चेक"]):
    inn(f"#it{j}", wt(8, kw) - .1, "opacity:0, x:-60", "back.out(1.6)", .35); sfx("click-soft", wt(8, kw), .3)
inn("#chk .no2", S(8) + .3, "opacity:0, scale:.8")

# ---------- 9 share ----------
bgp("b9", "board", S(9) - .3, END, op=.5, blur=4)
H.append('<div id="share"><b>दोस्त को भेजिए</b><span>जो सस्ती ज़मीन ढूँढ रहा है</span><div class="cta">&#10148; SHARE &middot; SAVE</div></div>')
inn("#share", S(9) - .1, "opacity:0, scale:.9")
J.append(f'tl.to("#share .cta", {{scale:1.07, duration:.35, yoyo:true, repeat:5}}, {S(9) + .6:.2f});'); sfx("sparkle", S(9) + .5, .3)

# ---------- captions (Hindi) ----------
HI = ["SC/ST", "सस्ती ज़मीन", "लाखों रुपए", "General", "OBC", "धारा 42", "शून्य", "void", "राज रकबा", "बेदखल", "हाई कोर्ट", "मालिक नहीं", "राज रकबा", "शॉर्टकट्स", "पावर ऑफ़ अटॉर्नी", "रिश्तेदार", "केस", "मुकदमे", "जाति", "जमाबंदी"]
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
        if cur and len(cur) + 1 + len(w_) > 20: chunks.append(cur); cur = w_
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
H.append('<div id="cred">राजस्थान काश्तकारी अधिनियम 1955, धारा 42 &middot; Rajasthan HC: Sita Ram v. Board of Revenue (2012) &middot; जमाबंदी उदाहरण, नाम बदले गए &middot; कई चित्र प्रतीकात्मक &middot; कानूनी सलाह नहीं</div>')

CSS = """@font-face{font-family:Deva;font-weight:100 900;src:url(assets/fonts/notodeva.woff2)}@font-face{font-family:DevaH;font-weight:100 900;src:url(assets/fonts/deva800.woff2)}@font-face{font-family:Anton;src:url(assets/fonts/anton.woff2)}@font-face{font-family:Mont;font-weight:700;src:url(assets/fonts/mont700.woff2)}@font-face{font-family:Mont;font-weight:800;src:url(assets/fonts/mont800.woff2)}@font-face{font-family:Mont;font-weight:900;src:url(assets/fonts/mont900.woff2)}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#0b0f17}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Mont,Deva,sans-serif;background:radial-gradient(120% 80% at 50% 30%,#18202e 0%,#0b0f17 65%,#06080c 100%)}
.y{color:#111;background:#FFD23F;border-radius:6px;padding:0 6px}
#face{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:40}
#cred{position:absolute;left:30px;right:30px;top:1700px;text-align:center;font:600 17px Deva;color:rgba(255,255,255,.6);z-index:20}
.bgp{position:absolute;inset:0;overflow:hidden;z-index:1;opacity:0}.bgp img{width:100%;height:100%;object-fit:cover}.bgp:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(8,11,17,.35),rgba(8,11,17,.05) 40%,rgba(8,11,17,.55))}
#sign{position:absolute;left:392px;top:546px;width:566px;height:302px;z-index:6;perspective:900px;mix-blend-mode:multiply}#sign>div{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
#sign .sa b{font:900 82px/1 DevaH;color:#B3161C}#sign .sa span{margin-top:14px;font:800 40px Deva;color:#222}
#sign .sb{background:#B3161C}#signt{position:absolute;left:392px;top:546px;width:566px;height:302px;z-index:7;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;opacity:0;transform-origin:50% 50%}#signt b{font:900 86px/1 DevaH;color:#fff;text-shadow:0 2px 0 rgba(0,0,0,.25)}#signt span{margin-top:12px;font:800 40px Deva;color:#FFD23F}#sign .sb b{font:900 86px/1 DevaH;color:#fff}#sign .sb span{margin-top:12px;font:800 40px Deva;color:#FFD23F}
#hook{position:absolute;left:60px;right:60px;top:110px;z-index:16;text-align:center;padding:22px 20px;border-radius:14px;border:2px solid #FFD23F;background:rgba(11,15,23,.9)}#hook small{display:block;font:800 32px Deva;color:#FF6B6B}#hook b{display:block;margin-top:6px;font:900 78px/1.1 DevaH;color:#fff}
#happy{position:absolute;left:0;right:0;margin:0 auto;width:540px;top:870px;z-index:12;padding:8px;border-radius:10px;background:#fff;box-shadow:0 40px 90px rgba(0,0,0,.75)}#happy img{display:block;width:100%;border-radius:6px}#happy span{position:absolute;right:16px;bottom:16px;padding:3px 10px;border-radius:4px;background:rgba(0,0,0,.6);color:#fff;font:700 18px Deva}
#grab{position:absolute;left:0;right:0;margin:0 auto;width:590px;top:880px;z-index:12;padding:8px;border-radius:10px;background:#fff;box-shadow:0 40px 90px rgba(0,0,0,.75)}#grab img{display:block;width:100%;border-radius:6px}#grab b{position:absolute;left:24px;top:24px;padding:6px 18px;border-radius:8px;background:#C81E1E;color:#fff;font:900 46px DevaH}#grab span{position:absolute;right:16px;bottom:16px;padding:3px 10px;border-radius:4px;background:rgba(0,0,0,.6);color:#fff;font:700 18px Deva}
#loss{position:absolute;left:0;right:0;margin:0 auto;width:780px;top:890px;z-index:12;padding:8px;border-radius:10px;background:#fff;box-shadow:0 40px 90px rgba(0,0,0,.75)}#loss img{display:block;width:100%;border-radius:6px}#loss span{position:absolute;right:16px;bottom:16px;padding:3px 10px;border-radius:4px;background:rgba(0,0,0,.6);color:#fff;font:700 18px Deva}
#rain{position:absolute;inset:0;z-index:7;pointer-events:none;opacity:0}#rain i{position:absolute;top:0;font-style:normal;font-weight:900;color:#2FD158;text-shadow:0 4px 12px rgba(0,0,0,.6)}
.doc{position:absolute;left:70px;top:330px;width:940px;height:1060px;overflow:hidden;border-radius:16px;background:#fff;box-shadow:0 30px 80px rgba(0,0,0,.7);z-index:5}.doc .im{position:absolute;left:0;top:0;width:940px}.doc img{display:block;width:100%}
.fk{position:absolute;background:#fff;color:#111;font-family:Deva,sans-serif;font-weight:500;line-height:1.25;white-space:nowrap;overflow:hidden;padding-left:2px}
.hlb{position:absolute;border:4px solid #E8262B;border-radius:8px;background:rgba(255,210,63,.35);box-shadow:0 0 14px rgba(232,38,43,.5);opacity:0}
.wm{position:absolute;left:50%;top:42%;translate:-50% -50%;rotate:-28deg;white-space:nowrap;font-family:Deva,Mont;font-weight:900;color:rgba(200,30,30,.13);pointer-events:none}
.tagx{position:absolute;left:0;right:0;top:1340px;margin:0 auto;width:max-content;padding:6px 16px;border-radius:6px;background:rgba(10,14,22,.9);border:1px solid #FFD23F;color:#FFD23F;font:800 22px Deva;z-index:12}
.nox{position:absolute;top:1130px;width:440px;height:150px;border-radius:16px;background:#C81E1E;border:4px solid #fff;display:flex;align-items:center;justify-content:center;gap:20px;z-index:14;box-shadow:0 20px 50px rgba(0,0,0,.6);rotate:-6deg}.nox b{font:400 76px Anton;color:#fff}.nox i{font:900 90px Mont;font-style:normal;color:#fff}
#book{position:absolute;left:0;right:0;top:330px;margin:0 auto;width:640px;z-index:15;padding:10px;border-radius:10px;background:#fff;box-shadow:0 40px 90px rgba(0,0,0,.75);rotate:-3deg}#book img{display:block;width:100%;border-radius:4px}
.law{position:absolute;left:60px;right:60px;top:240px;z-index:15;text-align:center;padding:40px 30px;border-radius:18px;border:3px solid #C9A24A;background:linear-gradient(160deg,rgba(18,15,10,.97),rgba(38,30,19,.97));box-shadow:0 30px 70px rgba(0,0,0,.6)}
.law small{display:block;font:800 32px Deva;color:#E8D6A8}.law>b{display:block;margin:10px 0 18px;font:900 140px/1 DevaH;color:#FFD23F}
.law .ln{display:flex;justify-content:center;align-items:center;gap:20px;margin-top:22px}.law .c{padding:8px 24px;border-radius:10px;background:#2b3a52;color:#fff;font:400 58px Anton,DevaH}.law .c.g{background:#5a2222}.law i{font:900 56px Mont;font-style:normal;color:#C9A24A}
.law em{font:900 64px Mont;font-style:normal}.law .ok{color:#2FD158}.law .no{color:#FF4B4B}.law .vb{margin-top:30px;font:800 36px Deva;color:#E8D6A8}
.lbl1{position:absolute;left:0;right:0;top:220px;margin:0 auto;width:max-content;padding:14px 34px;border-radius:12px;background:rgba(11,15,23,.92);border:2px solid #FFD23F;color:#fff;font:900 60px DevaH;z-index:15}
#void{position:absolute;left:150px;top:660px;width:780px;height:420px;border:16px solid #D7261E;border-radius:24px;display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:16;background:rgba(215,38,30,.08);box-shadow:0 0 50px rgba(215,38,30,.5)}#void b{font:900 170px/1 DevaH;color:#D7261E}#void span{font:400 110px/1 Anton;letter-spacing:.2em;color:#D7261E}
.pill{position:absolute;left:0;right:0;top:1220px;margin:0 auto;width:max-content;padding:14px 30px;border-radius:40px;background:#fff;color:#111;font:800 42px Deva;z-index:16;box-shadow:0 10px 30px rgba(0,0,0,.5)}
.who{position:absolute;top:360px;width:440px;padding:40px 20px;border-radius:18px;background:rgba(11,15,23,.92);border:2px solid #cfd8e6;text-align:center;z-index:15}.who .av{width:180px;height:180px;margin:0 auto;color:#cfd8e6}.who b{display:block;margin-top:16px;font:900 58px DevaH;color:#fff}.who span{display:block;margin-top:8px;font:700 32px Deva;color:#cfd8e6}
.who i{position:absolute;left:0;right:0;top:10px;height:240px;display:flex;align-items:center;justify-content:center;font:900 230px/1 Mont;font-style:normal;color:#E8262B;text-shadow:0 0 30px rgba(0,0,0,.6)}
#evict{position:absolute;left:90px;right:90px;top:520px;z-index:15;text-align:center;padding:50px 30px;border-radius:18px;background:#5a1616;border:3px solid #FF6B6B}#evict b{display:block;font:900 120px/1 DevaH;color:#fff}#evict span{display:block;margin-top:18px;font:700 38px Deva;color:#ffd7d7}
#raj{position:absolute;left:90px;right:90px;top:420px;z-index:15;text-align:center;padding:40px 30px;border-radius:18px;background:rgba(11,15,23,.94);border:3px solid #FFD23F}#raj .gv{width:300px;margin:0 auto}#raj b{display:block;margin-top:20px;font:900 130px/1 DevaH;color:#FFD23F}#raj span{display:block;margin-top:16px;font:700 40px Deva;color:#fff}
#hc{position:absolute;left:60px;right:60px;top:820px;z-index:15;text-align:center;padding:36px 30px;border-radius:18px;background:linear-gradient(160deg,rgba(18,15,10,.96),rgba(38,30,19,.96));border:3px solid #C9A24A}#hc .cb{width:360px;margin:0 auto}#hc small{display:block;margin-top:14px;font:900 50px DevaH;color:#E8D6A8}
#hc .q{margin-top:22px;font:700 38px/1.4 Deva;color:#fff}#hc .eq{display:flex;justify-content:center;align-items:center;gap:20px;margin-top:30px}#hc .eq span{padding:10px 22px;border-radius:10px;background:#2b3a52;color:#fff;font:900 46px DevaH}#hc .eq span.y{background:#FFD23F;color:#111}#hc .eq i{font:900 80px Mont;font-style:normal;color:#FF6B6B}
#hc em{display:block;margin-top:26px;font:600 24px Deva;font-style:normal;color:#cfd8e6}
.jg{position:absolute;left:90px;right:90px;z-index:15;padding:14px 30px;border-radius:18px;background:rgba(11,15,23,.93);border:3px solid #FFD23F;overflow:hidden}.jg b{display:block;font:900 52px/1.1 DevaH;color:#FFD23F}.jg span{display:none;color:#fff}
.jg .ck{position:absolute;inset:0;opacity:0;background:linear-gradient(115deg,transparent 46%,#E8262B 47%,#E8262B 49%,transparent 50%),linear-gradient(65deg,transparent 60%,#E8262B 61%,#E8262B 62.5%,transparent 63%)}
#ftree{position:absolute;left:90px;right:90px;top:330px;z-index:15;padding:20px;border-radius:18px;background:rgba(11,15,23,.93);border:3px solid #FFD23F}#ftree svg{display:block;width:100%;font-family:Deva}
#poa{position:absolute;left:0;right:0;top:250px;margin:0 auto;width:470px;z-index:15;padding:8px;border-radius:8px;background:#fff;box-shadow:0 40px 90px rgba(0,0,0,.75)}#poa img{display:block;width:100%}#poa span{position:absolute;right:12px;bottom:12px;padding:3px 10px;border-radius:4px;background:rgba(0,0,0,.6);color:#fff;font:700 18px Deva}
#case{position:absolute;left:120px;right:120px;top:300px;z-index:15;text-align:center;padding:30px;border-radius:18px;background:#5a1616;border:3px solid #FF6B6B}#case b{display:block;font:900 110px/1.05 DevaH;color:#fff}#case span{display:block;margin-top:10px;font:800 44px Deva;color:#FFD23F}
#mt{position:absolute;left:90px;right:90px;top:340px;z-index:15}.m{margin-top:34px;padding:26px 30px;border-radius:16px;background:rgba(11,15,23,.93);border:2px solid #cfd8e6}.m b{display:block;font:900 60px DevaH;color:#fff}.m .bar{margin-top:16px;height:34px;border-radius:17px;background:rgba(255,255,255,.12);overflow:hidden}.m .bar i{display:block;height:100%;background:linear-gradient(90deg,#E8262B,#FF8A3D);transform-origin:0 50%}
#chk{position:absolute;left:60px;right:60px;top:240px;z-index:15;padding:40px 40px;border-radius:18px;background:rgba(11,15,23,.94);border:3px solid #2FD158}#chk small{display:block;text-align:center;font:800 34px Deva;color:#2FD158}#chk>b{display:block;text-align:center;margin-top:6px;font:900 76px/1.1 DevaH;color:#fff}
#chk .it{display:flex;align-items:center;gap:22px;margin-top:34px;font:800 52px Deva;color:#fff}#chk .it i{flex:none;width:76px;height:76px;border-radius:50%;background:#2FD158;color:#062411;display:flex;align-items:center;justify-content:center;font:900 46px Mont;font-style:normal}#chk u{text-decoration:none;color:#FFD23F}
#chk .no2{margin-top:40px;text-align:center;padding:14px;border-radius:12px;background:#5a1616;color:#fff;font:900 50px DevaH}
#share{position:absolute;left:80px;right:80px;top:500px;z-index:16;text-align:center;padding:50px 30px;border-radius:18px;background:rgba(11,15,23,.94);border:3px solid #FFD23F}#share b{display:block;font:900 96px/1.1 DevaH;color:#fff}#share span{display:block;margin-top:16px;font:700 44px Deva;color:#cfd8e6}#share .cta{display:inline-block;margin-top:36px;padding:16px 40px;border-radius:10px;background:#FFD23F;color:#111;font:900 44px Mont}
.cp{position:absolute;left:40px;right:40px;top:1480px;text-align:center;opacity:0;z-index:35}
.cp div{display:inline-block;padding:6px 22px 10px;border-radius:10px;background:#fff;font:800 58px/1.25 Deva;color:#111;box-shadow:0 8px 24px rgba(0,0,0,.45)}"""
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
