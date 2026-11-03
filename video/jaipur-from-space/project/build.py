"""Jaipur from space (text-led; voice to be added later): hook -> old photos -> satellite time-lapse -> 10 area wipes with rates -> what's next -> CTA -> credits."""
import json
P = "proj"
A = json.load(open("areas.json")); O = json.load(open("overlays.json"))
H, J, SFX = [], [], []
def sfx(n, t, v=.35): SFX.append(f'<audio class="clip" src="assets/sfx/{n}.mp3" data-start="{t:.2f}" data-duration="2" data-track-index="{20 + len(SFX)}" data-volume="{v}"></audio>')
def show(i, t, until, d=.35): J.append(f'tl.fromTo("#{i}", {{opacity:0}}, {{opacity:1, duration:{d}}}, {t:.2f}); tl.to("#{i}", {{opacity:0, duration:{d}}}, {until - d:.2f});')
def txt(i, html, t, until, top=1330, cls="st"):
    H.append(f'<div class="{cls}" id="{i}" style="top:{top}px"><span class="bx">{html}</span></div>')
    J.append(f'tl.fromTo("#{i}", {{opacity:0, y:20, scale:.95}}, {{opacity:1, y:0, scale:1, duration:.28, ease:"back.out(2)"}}, {t:.2f}); tl.to("#{i}", {{opacity:0, duration:.18}}, {until - .18:.2f});')
def full(i, src, t, until, z0=1.0, z1=1.08, x1=0, extra=""):
    H.append(f'<div class="full" id="{i}"><img src="assets/img/{src}" style="{extra}"/></div>')
    show(i, t, until, .35)
    J.append(f'tl.fromTo("#{i} img", {{scale:{z0}, x:0}}, {{scale:{z1}, x:{x1}, duration:{until - t:.2f}, ease:"none"}}, {t:.2f});')
def money(v): return f"₹{v / 100000:g} lakh" if v >= 100000 else f"₹{v:,}"
def mult(m): return f"~{round(m, -2) if m >= 1000 else round(m, -1):,.0f}×"
Y, E = '<span class="y">', '</span>'

# ---------- 0 · cover (whole city) ----------
H.append('<div id="cover"><svg width="1080" height="1920" style="position:absolute;inset:0"><defs><pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="rgba(243,231,211,.07)"/></pattern></defs><rect width="1080" height="1920" fill="url(#dots)"/></svg>'
         '<div id="cvt">JAIPUR<br/><span>1989 → 2024</span></div><div id="cvs">Land that cost ₹50 a gaj<br/>now costs ₹50,000+</div>'
         '<div id="cvimg"><img src="assets/img/city_1989.jpg"/><div id="cvb"><img src="assets/img/city_2025.jpg"/></div><i></i><b class="l">1989</b><b class="r">2024</b></div>'
         '<div id="cvpill">Real satellite · 10 areas · prices then &amp; now</div></div>')
J.append('tl.set("#cover", {opacity:1}, 0); tl.to("#cover", {opacity:0, duration:.25}, 0.55);')

# ---------- 1 · hook: the whole city ----------
full("h89", "city_1989.jpg", 0.5, 7.4, 1.0, 1.10)
H.append('<div class="full" id="h24"><img src="assets/img/city_2025.jpg"/></div><div id="hline"></div>')
J.append('tl.set("#h24", {opacity:1, clipPath:"inset(0 0 0 100%)"}, 0.5); tl.to("#h24", {clipPath:"inset(0 0 0 0%)", duration:1.3, ease:"power2.inOut"}, 3.6); tl.to("#h24", {opacity:0, duration:.35}, 7.05);')
J.append('tl.fromTo("#h24 img", {scale:1.0}, {scale:1.10, duration:6.9, ease:"none"}, 0.5);')
J.append('tl.set("#hline", {opacity:0, x:1080}, 0); tl.set("#hline", {opacity:1}, 3.6); tl.to("#hline", {x:0, duration:1.3, ease:"power2.inOut"}, 3.6); tl.to("#hline", {opacity:0, duration:.2}, 4.9);')
H.append('<div id="ss"><span><svg viewBox="0 0 24 24" width="38" height="38"><path d="M6 3h12v18l-6-4-6 4z" style="fill:#FFE03A"/></svg>SAVE this</span>'
         '<span><svg viewBox="0 0 24 24" width="38" height="38"><path d="M3 11l18-8-8 18-2-8z" style="fill:none;stroke:#fff;stroke-width:2.4;stroke-linejoin:round"/></svg>SHARE it</span></div>')
J.append('tl.fromTo("#ss", {opacity:0, y:-30}, {opacity:1, y:0, duration:.35, ease:"back.out(2)"}, 0.6); tl.to("#ss span", {scale:1.08, duration:.3, yoyo:true, repeat:3, stagger:.15}, 1.0); tl.to("#ss", {opacity:0, duration:.3}, 3.4);')
H.append('<div class="ytag" id="hy">JAIPUR · <span id="hyr">1989</span></div>')
J.append('tl.fromTo("#hy", {opacity:0}, {opacity:1, duration:.3}, 0.7); tl.call(()=>{document.getElementById("hyr").textContent="1989"}, null, 0.6); tl.call(()=>{document.getElementById("hyr").textContent="2024"}, null, 4.3); tl.to("#hy", {opacity:0, duration:.3}, 7.1);')
H.append('<div id="hprice"><b id="hp">₹50 – 300</b><i>PER GAJ · <span id="hpy">1990</span></i></div>')
J.append('tl.fromTo("#hprice", {opacity:0, scale:.6}, {opacity:1, scale:1, duration:.4, ease:"back.out(2)"}, 1.0); tl.to("#hprice", {opacity:0, duration:.3}, 5.6);')
J.append('tl.call(()=>{document.getElementById("hp").textContent="₹50 – 300"; document.getElementById("hpy").textContent="1990"}, null, 0.9);')
J.append('tl.call(()=>{document.getElementById("hp").textContent="₹40,000 – 1.5 lakh"; document.getElementById("hpy").textContent="TODAY"}, null, 4.3); tl.fromTo("#hp", {scale:1.4, color:"#fff"}, {scale:1, color:"#FFE03A", fontSize:"92px", duration:.5, ease:"back.out(2)"}, 4.3);')
txt("t0", f"In 1990, Jaipur land cost {Y}₹50–300 a gaj.{E}", 1.1, 3.8)
txt("t1", f"Today? {Y}Up to ~1,200× more.{E}", 4.3, 5.55)
# multiplier pins flash across the 2024 city
hp = ""
for k, (p, a) in enumerate(zip(O["pins"], A)):
    x = min(1000, max(60, p["xy"][0])); y = p["xy"][1]; m = mult(a["p1"] / a["p0"])
    hp += f'<div class="pin hpn" id="hq{k}" style="left:{x:.0f}px;top:{y:.0f}px"><i></i><b class="{"r" if x > 700 else ""}">{p["name"]} <span class="y">{m}</span></b></div>'
H.append(f'<div id="hpins">{hp}</div>')
J.append('tl.set("#hpins", {opacity:1}, 5.6); tl.to("#hpins", {opacity:0, duration:.3}, 7.1); tl.set("#hpins", {opacity:0}, 0);')
for k in range(len(A)): J.append(f'tl.fromTo("#hq{k}", {{opacity:0, scale:.3}}, {{opacity:1, scale:1, duration:.22, ease:"back.out(3)"}}, {5.65 + .14 * k:.2f});'); sfx("pop", 5.65 + .14 * k, .18)
sfx("impact-bass-1", 0.55, .5); sfx("riser", 2.6, .3); sfx("whoosh", 3.6, .35); sfx("ping", 4.3, .4)

# ---------- 2 · old photos ----------
H.append('<div class="bg" id="phbg"></div>'); show("phbg", 7.0, 17.5, .3)
PH = [("p_1890s.jpg", "1890s", "Jaipur · archive photo", 7.2, 9.4), ("p_bw.jpg", "OLD JAIPUR", "Image supplied", 9.4, 10.8), ("p_bazaar.jpg", "OLD JAIPUR", "Image supplied", 10.8, 12.2),
      ("p_2002.jpg", "2002", "Hawa Mahal · image supplied", 12.2, 13.5), ("p_2010.jpg", "~2010", "Ramganj Bazaar · image supplied", 13.5, 14.8),
      ("p_wtp.jpg", "~2010", "World Trade Park under construction · © Dr Hamid Raihan Ansari", 14.8, 16.0), ("p_today.jpg", "TODAY", "Image supplied", 16.0, 17.3)]
for k, (src, era, cr, t, u) in enumerate(PH):
    H.append(f'<div class="ph" id="ph{k}"><img src="assets/img/{src}"/><b>{era}</b><em>{cr}</em></div>')
    J.append(f'tl.fromTo("#ph{k}", {{opacity:0, scale:1.04}}, {{opacity:1, scale:1, duration:.3}}, {t:.2f}); tl.to("#ph{k}", {{opacity:0, duration:.25}}, {u:.2f}); tl.fromTo("#ph{k} img", {{scale:1}}, {{scale:1.08, duration:{u - t + .3:.2f}, ease:"none"}}, {t:.2f});')
    sfx("click-soft", t, .3)
txt("t2", f"How did Jaipur {Y}get here?{E}", 7.3, 10.8)
txt("t3", "Let's go back in time.", 10.8, 13.5)
txt("t4", f"From streets… to {Y}space.{E}", 13.5, 17.3)

# ---------- 3 · satellite time-lapse ----------
YRS = [("city_1989.jpg", "1989", "A small city, tucked against the hills."), ("city_2000.jpg", "2000", f"Mansarovar &amp; Vaishali {Y}spread west.{E}"),
       ("city_2010.jpg", "2010", f"The south {Y}fills in.{E}"), ("city_2025.jpg", "2024", f"Almost {Y}edge to edge.{E}")]
T0, DT = 17.3, 2.5
for k, (src, yr, line) in enumerate(YRS):
    t = T0 + DT * k; u = T0 + DT * 4 + .2 if k == 3 else t + DT + .45
    H.append(f'<div class="full" id="c{k}"><img src="assets/img/{src}"/></div>')
    J.append(f'tl.fromTo("#c{k}", {{opacity:0}}, {{opacity:1, duration:{.4 if k == 0 else .9}}}, {t:.2f}); tl.to("#c{k}", {{opacity:0, duration:.4}}, {u:.2f});')
    txt(f"cy{k}", line, t + .2, (t + .5 + 1.0) if k == 3 else T0 + DT * (k + 1))
    sfx("whoosh-short", t, .3)
J.append(f'tl.fromTo(".full[id^=c] img", {{scale:1.0}}, {{scale:1.18, duration:{DT * 4 + .6:.2f}, ease:"none"}}, {T0:.2f});')
H.append('<div id="bigyr"><span id="byr">1989</span><em>JAIPUR FROM SPACE</em></div>')
J.append(f'tl.fromTo("#bigyr", {{opacity:0, y:-20}}, {{opacity:1, y:0, duration:.35}}, {T0:.2f}); tl.to("#bigyr", {{opacity:0, duration:.3}}, {T0 + DT * 4 + .2:.2f});')
for k, (src, yr, line) in enumerate(YRS): J.append(f'tl.call(()=>{{document.getElementById("byr").textContent="{yr}"}}, null, {T0 + DT * k + .45:.2f}); tl.fromTo("#byr", {{scale:1.25}}, {{scale:1, duration:.4, ease:"back.out(2)"}}, {T0 + DT * k + .45:.2f});')
TEND = T0 + DT * 4 + .2
pins = ""
for k, p in enumerate(O["pins"]):
    x = min(1000, max(60, p["xy"][0])); y = p["xy"][1]; right = x > 700
    pins += f'<div class="pin" id="pn{k}" style="left:{x:.0f}px;top:{y:.0f}px"><i></i><b class="{"r" if right else ""}">{p["name"]}</b></div>'
H.append(f'<div id="pins">{pins}</div>')
tp = T0 + DT * 3 + 1.6
J.append(f'tl.set("#pins", {{opacity:1}}, {tp:.2f}); tl.to("#pins", {{opacity:0, duration:.3}}, {TEND:.2f}); tl.fromTo("#pins", {{scale:{1 + .18 * (tp - T0) / (DT * 4 + .6):.3f}}}, {{scale:{1 + .18 * (TEND - T0) / (DT * 4 + .6):.3f}, duration:{TEND - tp:.2f}, ease:"none"}}, {tp:.2f}); tl.set("#pins", {{opacity:0}}, 0);')
for k in range(len(O["pins"])): J.append(f'tl.fromTo("#pn{k}", {{opacity:0, scale:.3}}, {{opacity:1, scale:1, duration:.25, ease:"back.out(3)"}}, {tp + .12 * k:.2f});'); 
sfx("click-soft", tp, .3)

# ---------- 4 · ten areas, wipe 1989 -> 2024 with rates ----------
TA, DA, DJ = TEND + .1, 2.45, 5.2
DUR = [DJ] + [DA] * (len(A) - 1); STARTS = [TA + sum(DUR[:k]) for k in range(len(A))]
txt("ta", f"Now zoom in. {Y}Same spot, 35 years apart.{E}", TEND - .3, TA + 1.5, top=1180)
for k, a in enumerate(A):
    t = STARTS[k]; d = DUR[k]; u = t + d + .25; W0 = 2.4 if k == 0 else .55
    H.append(f'<div class="full" id="b{k}"><img src="assets/img/a_{a["k"]}_1989.jpg"/></div><div class="full" id="n{k}"><img src="assets/img/a_{a["k"]}_2024.jpg"/></div>')
    J.append(f'tl.fromTo("#b{k}", {{opacity:0}}, {{opacity:1, duration:.25}}, {t:.2f}); tl.to("#b{k}", {{opacity:0, duration:.25}}, {u:.2f});')
    J.append(f'tl.set("#n{k}", {{opacity:1, clipPath:"inset(0 0 0 100%)"}}, {t:.2f}); tl.to("#n{k}", {{clipPath:"inset(0 0 0 0%)", duration:.9, ease:"power2.inOut"}}, {t + W0:.2f}); tl.to("#n{k}", {{opacity:0, duration:.25}}, {u:.2f}); tl.set("#n{k}", {{opacity:0}}, 0);')
    J.append(f'tl.fromTo(["#b{k} img","#n{k} img"], {{scale:1.0}}, {{scale:1.07, duration:{d + .3:.2f}, ease:"none"}}, {t:.2f});')
    J.append(f'tl.set("#aline", {{x:1080, opacity:1}}, {t + W0:.2f}); tl.to("#aline", {{x:0, duration:.9, ease:"power2.inOut"}}, {t + W0:.2f}); tl.set("#aline", {{opacity:0}}, {t + W0 + .91:.2f});')
    if k:
        J.append(f'tl.fromTo("#ring", {{opacity:0, scale:.4}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)"}}, {t + .15:.2f}); tl.to("#ring", {{opacity:0, duration:.2}}, {t + d - .1:.2f});')
    m = a["p1"] / a["p0"]
    H.append(f'<div class="atag" id="at{k}"><b>{a["name"]}</b><span>1989 <i>→</i> 2024</span></div>')
    txt(f"ap{k}", f'{money(a["p0"])} <span class="arr">→</span> {Y}{money(a["p1"])}{E}<small>per sq yd · approx.</small>', t + W0 + .1, t + d, top=1290, cls="st price")
    H.append(f'<div class="mult" id="am{k}"><span class="bx" style="padding:0 34px 8px">{mult(m)}</span></div>')
    show(f"at{k}", t, t + d, .2)
    J.append(f'tl.fromTo("#am{k}", {{opacity:0, scale:.5}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2.5)"}}, {t + W0 + .7:.2f}); tl.to("#am{k}", {{opacity:0, duration:.2}}, {t + d - .05:.2f});')
    sfx("whoosh-short", t + W0, .28); sfx("pop", t + W0 + .7, .25)
# Jagatpura: the 150-gaj plot story (₹10,000 in 1990 -> ~₹1.17 crore today)
tj = STARTS[0]
H.append('<div id="plot"><svg viewBox="0 0 600 520" width="600" height="520">'
         '<rect x="120" y="70" width="300" height="400" rx="6" style="fill:rgba(255,224,58,.10);stroke:#FFE03A;stroke-width:6;stroke-dasharray:18 12"/>'
         '<line x1="120" y1="40" x2="420" y2="40" style="stroke:#fff;stroke-width:3"/><text x="270" y="28" text-anchor="middle" style="font:800 30px Inter;fill:#fff">30 ft</text>'
         '<line x1="455" y1="70" x2="455" y2="470" style="stroke:#fff;stroke-width:3"/><text x="470" y="278" style="font:800 30px Inter;fill:#fff">45 ft</text>'
         '<g id="house" style="opacity:0"><path d="M170 300 L270 210 L370 300 Z" style="fill:#FF8A1F"/><rect x="190" y="300" width="160" height="130" style="fill:#F3E7D3"/><rect x="250" y="355" width="40" height="75" style="fill:#8a5a2b"/><rect x="205" y="320" width="34" height="30" style="fill:#5aa9e6"/><rect x="301" y="320" width="34" height="30" style="fill:#5aa9e6"/></g>'
         '<text id="gaj" x="270" y="280" text-anchor="middle" style="font:900 64px Inter;fill:#FFE03A">150 GAJ</text>'
         '</svg><div id="tag"><b id="hm">₹10,000</b><i id="tagsub">PRICE · 1990</i></div></div>')
J.append(f'tl.fromTo("#plot", {{opacity:0, scale:.5, rotation:-6}}, {{opacity:1, scale:1, rotation:0, duration:.5, ease:"back.out(1.8)"}}, {tj + .5:.2f}); tl.to("#plot", {{opacity:0, scale:.9, duration:.3}}, {tj + DJ - 1.5:.2f});')
J.append(f'tl.fromTo("#plot rect:first-child", {{strokeDashoffset:0}}, {{strokeDashoffset:-120, duration:4, ease:"none"}}, {tj + .5:.2f});')
J.append(f'tl.to("#gaj", {{opacity:0, duration:.3}}, {tj + 2.6:.2f}); tl.fromTo("#house", {{opacity:0, scale:.2, transformOrigin:"270px 430px"}}, {{opacity:1, scale:1, duration:.6, ease:"back.out(2)"}}, {tj + 2.7:.2f});')
J.append(f'tl.fromTo("#tag", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:.35, ease:"back.out(2)"}}, {tj + .9:.2f});')
J.append(f'const hm={{v:10000}}; tl.to(hm, {{v:11700000, duration:1.3, ease:"power3.in", onUpdate:()=>{{const v=hm.v; document.getElementById("hm").textContent = v>=1e7 ? "₹"+(v/1e7).toFixed(2)+" crore" : v>=1e5 ? "₹"+(v/1e5).toFixed(1)+" lakh" : "₹"+Math.round(v).toLocaleString("en-IN")}}}}, {tj + 2.5:.2f});')
J.append(f'tl.call(()=>{{document.getElementById("tagsub").textContent="SAME PLOT · TODAY (APPROX.)"}}, null, {tj + 3.8:.2f}); tl.fromTo("#tag", {{scale:1}}, {{scale:1.15, duration:.25, yoyo:true, repeat:1}}, {tj + 3.8:.2f});')
H.append('<div id="notes">' + "".join(f'<i style="bottom:{k*18}px"></i>' for k in range(12)) + '</div>')
J.append(f'tl.fromTo("#notes", {{opacity:0}}, {{opacity:1, duration:.2}}, {tj + 2.5:.2f}); tl.from("#notes i", {{y:-500, opacity:0, duration:.35, stagger:.1, ease:"bounce.out"}}, {tj + 2.5:.2f}); tl.to("#notes", {{opacity:0, duration:.3}}, {tj + DJ - 1.5:.2f});')
txt("tj0", f"In 1990, {Y}₹10,000{E} bought a {Y}150-gaj plot{E} here.", tj + .5, tj + 2.4)
J.append(f'tl.set("#am0", {{top:1060}}, 0);')
H.append('<div id="ring"><i></i></div>')
J.append(f'tl.fromTo("#ring i", {{scale:1, opacity:.8}}, {{scale:1.5, opacity:0, duration:1, repeat:{int((sum(DUR)) // 1)}, ease:"power1.out"}}, {TA:.2f}); tl.set("#ring", {{opacity:0}}, 0);')
H.append('<div id="aline"></div><div class="yl" id="yl89">1989</div><div class="yl r" id="yl24">2024</div>')
TB = TA + sum(DUR)
show("yl89", TA, TB, .25); show("yl24", TA + .55, TB, .25)
FINE = "Approx. rates · 1990–95: historical estimates · 2026: indicative listing rates · multipliers are calculated estimates, not verified investment returns · past growth ≠ future returns · ₹100 in 1990 ≈ ₹1,000 today (inflation)"
H.append(f'<div id="fine">{FINE}</div><div id="fine2">{FINE}</div>')
show("fine", 4.3, 5.7, .3); show("fine2", TA, TB, .3)

# ---------- 5 · what's next ----------
TN = TB + .1
H.append('<div class="full" id="reg"><img src="assets/img/region_2024.jpg"/>'
         '<svg width="1080" height="1920" viewBox="0 0 1080 1920" style="position:absolute;inset:0">'
         + "".join(f'<path class="rg" pathLength="1" d="M{" L".join(f"{x} {y}" for x, y in s)}" style="fill:none;stroke:#FFE03A;stroke-width:7;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>' for s in O["ring"])
         + "".join(f'<path class="pk" pathLength="1" d="M{" L".join(f"{x} {y}" for x, y in s)}" style="fill:none;stroke:#FF5FA2;stroke-width:9;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>' for s in O["pink"])
         + f'<path id="or" pathLength="1" d="M{" L".join(f"{x} {y}" for x, y in O["orange"])}" style="fill:none;stroke:#FF8A1F;stroke-width:11;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1"/>'
         + f'<path id="td" d="M{" L".join(f"{x} {y}" for x, y in O["todi"])}" style="fill:none;stroke:#FF8A1F;stroke-width:7;stroke-dasharray:14 12;opacity:0"/>'
         + '</svg></div>')
show("reg", TN, TN + 6.6, .5)
J.append(f'tl.fromTo("#reg img", {{scale:1.15}}, {{scale:1.0, duration:6.6, ease:"power1.out"}}, {TN:.2f});')
J.append(f'tl.to(".rg", {{strokeDashoffset:0, duration:1.4, ease:"power2.inOut"}}, {TN + 1.6:.2f}); tl.to(".pk", {{strokeDashoffset:0, duration:.9}}, {TN + 2.9:.2f}); tl.to("#or", {{strokeDashoffset:0, duration:1.3}}, {TN + 3.2:.2f}); tl.to("#td", {{opacity:1, duration:.4}}, {TN + 4.4:.2f});')
H.append('<div class="chip" id="proj"><b>PROJECTION · APPROVED &amp; ANNOUNCED PROJECTS</b>What\'s already planned</div>'); show("proj", TN + .2, TN + 6.6, .3)
txt("w0", f"So what's {Y}next?{E}", TN + .1, TN + 1.6)
txt("w1", f"{Y}Ring Road{E} pulling the city outward", TN + 1.6, TN + 3.1)
txt("w2", f"Metro Phase 2 {Y}approved{E}: Tonk Rd → Sikar Rd", TN + 3.1, TN + 4.9)
txt("w3", f"JDA region: {Y}~6,000 sq km{E}", TN + 4.9, TN + 6.6)
sfx("whoosh", TN, .3)

# ---------- 6 · CTA ----------
TC = TN + 6.6
full("cta", "region_2024.jpg", TC - .2, TC + 4.4, 1.0, 1.06, extra="filter:brightness(.45)")
txt("k0", f"Where's the {Y}next Jagatpura?{E}", TC, TC + 4.4, top=760, cls="st big")
txt("k1", "Comment your answer 👇", TC + .8, TC + 4.4, top=1060)
H.append('<div id="share"><span><svg viewBox="0 0 24 24" width="60" height="60"><path d="M6 3h12v18l-6-4-6 4z" style="fill:#FFE03A"/></svg>Save it · check back in 10 years</span>'
         '<span><svg viewBox="0 0 24 24" width="60" height="60"><path d="M3 11l18-8-8 18-2-8z" style="fill:none;stroke:#fff;stroke-width:2;stroke-linejoin:round"/></svg>Send to someone buying land</span></div>')
J.append(f'tl.fromTo("#share", {{opacity:0, y:20}}, {{opacity:1, y:0, duration:.4}}, {TC + 1.4:.2f}); tl.to("#share svg", {{scale:1.15, duration:.4, yoyo:true, repeat:3}}, {TC + 1.9:.2f}); tl.to("#share", {{opacity:0, duration:.3}}, {TC + 4.2:.2f});')
sfx("sparkle", TC + .1, .35)

# ---------- 7 · credits ----------
TK = TC + 4.4; END = round(TK + 4.6, 2)
H.append('<div id="credits"><b>CREDITS, SOURCES &amp; REFERENCES</b>'
         '<p>MagicBricks (2026 Residential Plot Trends) · Housing.com (Jaipur Property Rates) · Rajasthan Registration &amp; Stamps Department (DLC Rates) · Rajasthan GIS Portal · Kapil Raisinghani (historical land-price account)</p>'
         '<p>Satellite: Landsat 5 / 7 / 9 courtesy NASA/USGS · Contains modified Copernicus Sentinel-2 data (2024) · Map data © OpenStreetMap contributors</p>'
         '<b>DISCLAIMER</b><p>1990–1995 prices are historical estimates; 2026 prices are indicative market rates based on property listings. Appreciation multipliers are calculated estimates, not verified investment returns. Future section shows approved / announced projects only — not a prediction.</p>'
         '<i>ASHWILLPOWER · JAIPUR REAL ESTATE</i></div>')
J.append(f'tl.fromTo("#credits", {{opacity:0}}, {{opacity:1, duration:.4}}, {TK:.2f});')
H.append('<div id="brand">ASHWILLPOWER · JAIPUR REAL ESTATE</div>')
J.append(f'tl.set("#brand", {{opacity:0}}, 0); tl.to("#brand", {{opacity:1, duration:.3}}, 0.6); tl.to("#brand", {{opacity:0, duration:.3}}, {TK:.2f});')

CSS = """*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#07090d}
#root{position:relative;width:1080px;height:1920px;overflow:hidden}.y{color:#FFE03A}
.full{position:absolute;inset:0;opacity:0;overflow:hidden}.full img{width:100%;height:100%;object-fit:cover;display:block}
.bg{position:absolute;inset:0;opacity:0;background:radial-gradient(120% 80% at 50% 40%,#2B2016,#100c08)}
.st{position:absolute;left:50px;right:50px;text-align:center;opacity:0;font:900 68px/1.1 Inter,Arial,sans-serif;color:#fff;text-shadow:0 4px 0 #000,0 0 22px rgba(0,0,0,.95),0 0 4px #000}
.st.big{font-size:96px}.st.price{font-size:74px}.st.price small{display:block;margin-top:6px;font:700 26px "JetBrains Mono",monospace;letter-spacing:.12em;color:rgba(255,255,255,.85)}.st .arr{color:#FF9B3D}
#ss{position:absolute;left:0;right:0;top:250px;display:flex;justify-content:center;gap:22px;opacity:0}
#ss span{display:flex;align-items:center;gap:12px;padding:14px 24px;border-radius:40px;background:rgba(8,12,20,.85);border:2px solid rgba(255,255,255,.25);font:900 36px Inter,Arial,sans-serif;color:#fff}
.ytag{position:absolute;left:60px;top:1220px;opacity:0;padding:10px 20px;border-radius:12px;background:rgba(8,12,20,.8);font:800 30px "JetBrains Mono",monospace;letter-spacing:.12em;color:#fff}.ytag span{color:#FFE03A}
#hline,#aline{position:absolute;top:0;left:0;width:6px;height:1920px;background:#fff;box-shadow:0 0 24px #fff;opacity:0}
#hmoney{position:absolute;left:0;right:0;top:560px;text-align:center;opacity:0;font-family:Inter,Arial,sans-serif;text-shadow:0 6px 0 #000,0 0 30px rgba(0,0,0,.9)}
#hmoney b{display:block;font-weight:900;font-size:150px;color:#FFE03A;letter-spacing:-.02em}#hmoney i{display:block;font-style:normal;font:700 30px "JetBrains Mono",monospace;letter-spacing:.14em;color:#fff}
.ph{position:absolute;left:70px;right:70px;top:330px;height:900px;opacity:0;border-radius:24px;overflow:hidden;box-shadow:0 30px 80px rgba(0,0,0,.7)}
.ph img{width:100%;height:100%;object-fit:cover;display:block}.ph b{position:absolute;left:28px;top:24px;padding:8px 18px;border-radius:12px;background:#FFE03A;font:900 44px Inter,Arial,sans-serif;color:#111}
.ph em{position:absolute;left:0;right:0;bottom:0;padding:40px 24px 16px;background:linear-gradient(180deg,transparent,rgba(0,0,0,.85));font:600 24px Inter,Arial,sans-serif;font-style:normal;color:#eee}
#bigyr{position:absolute;left:0;right:0;top:250px;text-align:center;opacity:0;font-family:Inter,Arial,sans-serif;text-shadow:0 6px 0 #000,0 0 30px rgba(0,0,0,.9)}
#bigyr span{display:block;font-weight:900;font-size:190px;line-height:1;color:#fff}#bigyr em{display:block;font-style:normal;font:700 30px "JetBrains Mono",monospace;letter-spacing:.3em;color:#FFE03A}
.atag{position:absolute;left:0;right:0;top:250px;text-align:center;opacity:0;font-family:Inter,Arial,sans-serif;text-shadow:0 5px 0 #000,0 0 26px rgba(0,0,0,.95)}
.atag b{display:block;font-weight:900;font-size:92px;line-height:1;color:#fff}.atag span{display:inline-block;margin-top:14px;padding:8px 20px;border-radius:12px;background:rgba(8,12,20,.8);font:800 32px "JetBrains Mono",monospace;letter-spacing:.12em;color:#fff}.atag i{font-style:normal;color:#FF9B3D}
.mult{position:absolute;left:0;right:0;top:1060px;text-align:center;opacity:0;font:900 130px Inter,Arial,sans-serif;color:#FFE03A;text-shadow:0 6px 0 #000,0 0 30px rgba(0,0,0,.95)}
.yl{position:absolute;left:30px;top:440px;opacity:0;padding:6px 14px;border-radius:10px;background:rgba(8,12,20,.8);font:800 26px "JetBrains Mono",monospace;color:#fff}.yl.r{left:auto;right:30px;color:#FFE03A}
#fine,#fine2{position:absolute;left:50px;right:50px;top:1575px;text-align:center;opacity:0;font:500 20px/1.35 "JetBrains Mono",monospace;color:rgba(255,255,255,.8);text-shadow:0 1px 4px #000}
.chip{position:absolute;left:60px;right:60px;top:250px;opacity:0;padding:20px 28px;border-radius:20px;background:rgba(8,12,20,.88);border-left:10px solid #FFE03A;font:800 42px/1.15 Inter,Arial,sans-serif;color:#fff}
.chip b{display:block;font:700 24px "JetBrains Mono",monospace;letter-spacing:.14em;color:#FFE03A;margin-bottom:6px}
#share{position:absolute;left:60px;right:60px;top:1260px;display:flex;flex-direction:column;gap:22px;opacity:0}
#share span{display:flex;align-items:center;gap:20px;padding:18px 26px;border-radius:20px;background:rgba(8,12,20,.85);border:2px solid rgba(255,255,255,.2);font:900 40px Inter,Arial,sans-serif;color:#fff}
#credits{position:absolute;inset:0;opacity:0;background:#0b0d10;padding:300px 80px 0;font-family:Inter,Arial,sans-serif;color:#ddd}
#credits b{display:block;margin:34px 0 14px;font:700 28px "JetBrains Mono",monospace;letter-spacing:.16em;color:#FFE03A}#credits p{font-size:32px;line-height:1.45;margin-bottom:18px}
#credits i{display:block;margin-top:60px;font:700 26px "JetBrains Mono",monospace;letter-spacing:.2em;color:#fff;font-style:normal}
#brand{position:absolute;left:0;right:0;top:150px;text-align:center;font:700 24px "JetBrains Mono",monospace;letter-spacing:.2em;color:rgba(255,255,255,.85);text-shadow:0 2px 6px #000}
#hprice{position:absolute;left:0;right:0;top:420px;text-align:center;opacity:0;font-family:Inter,Arial,sans-serif;text-shadow:0 6px 0 #000,0 0 30px rgba(0,0,0,.95)}#hprice b{display:inline-block;font-weight:900;font-size:120px;color:#FFE03A;letter-spacing:-.02em}#hprice i{display:block;font-style:normal;font:800 30px "JetBrains Mono",monospace;letter-spacing:.16em;color:#fff}#hprice i span{color:#FFE03A}
#hpins{position:absolute;inset:0;opacity:0;transform:scale(1.09);transform-origin:540px 960px}#hpin{position:absolute;left:470px;top:1110px;opacity:0}#hpin i{position:absolute;left:-14px;top:-14px;width:28px;height:28px;border-radius:50%;background:#FF2D55;border:4px solid #fff;box-shadow:0 0 18px #FF2D55}
#hpin s{position:absolute;left:-30px;top:-30px;width:60px;height:60px;border-radius:50%;border:4px solid #FF2D55}#hpin b{position:absolute;left:26px;top:-22px;padding:6px 14px;border-radius:10px;background:#FF2D55;font:900 28px Inter;color:#fff;white-space:nowrap}
#plot{position:absolute;left:240px;top:470px;width:600px;opacity:0;padding:10px 0 0;border-radius:28px;background:rgba(8,12,20,.82);border:2px solid rgba(255,224,58,.5);box-shadow:0 20px 60px rgba(0,0,0,.6);transform-origin:50% 100%}
#plot svg{display:block;margin:0 auto}#tag{position:absolute;left:0;right:0;bottom:-110px;text-align:center;opacity:0}#tag b{display:inline-block;padding:10px 26px;border-radius:16px;background:#FFE03A;font:900 70px Inter;color:#111}
#tag i{display:block;margin-top:8px;font:800 24px "JetBrains Mono",monospace;font-style:normal;letter-spacing:.14em;color:#fff;text-shadow:0 2px 6px #000}
#notes{position:absolute;left:880px;top:900px;width:150px;height:240px;opacity:0}#notes i{position:absolute;left:0;width:150px;height:30px;border-radius:5px;background:linear-gradient(90deg,#7bbf72,#a7d99b 50%,#7bbf72);border:2px solid #3d7a36;box-shadow:0 3px 6px rgba(0,0,0,.4)}
#pins{position:absolute;inset:0;opacity:0;transform-origin:540px 960px}.pin{position:absolute;opacity:0}.pin i{position:absolute;left:-11px;top:-11px;width:22px;height:22px;border-radius:50%;background:#FFE03A;border:3px solid #111;box-shadow:0 0 14px #FFE03A}
.pin b{position:absolute;left:18px;top:-20px;padding:4px 12px;border-radius:9px;background:rgba(8,12,20,.88);border:2px solid #FFE03A;font:800 26px Inter;color:#fff;white-space:nowrap}.pin b.r{left:auto;right:18px}
#ring{position:absolute;left:340px;top:600px;width:400px;height:400px;opacity:0}#ring::before,#ring i{content:"";position:absolute;inset:0;border-radius:50%;border:5px solid #FFE03A;box-shadow:0 0 24px rgba(255,224,58,.6)}
.bx{display:inline-block;padding:14px 28px 16px;border-radius:24px;background:rgba(6,8,12,.62);box-shadow:0 8px 30px rgba(0,0,0,.35)}
.atag b{display:inline-block!important;padding:4px 30px 10px;border-radius:24px;background:rgba(6,8,12,.62)}
#hprice b,#bigyr span{padding:0 30px 6px;border-radius:28px;background:rgba(6,8,12,.55)}#bigyr span{display:inline-block!important}
#hprice i,#bigyr em{display:table!important;margin:8px auto 0;padding:6px 16px;border-radius:12px;background:rgba(6,8,12,.7)}
.mult{display:flex;justify-content:center}.mult{background:none}
#fine,#fine2{background:rgba(6,8,12,.7);padding:10px 16px;border-radius:14px}
#tag i{display:table!important;margin:8px auto 0;padding:5px 14px;border-radius:10px;background:rgba(6,8,12,.75)}
#cover{position:absolute;inset:0;opacity:0;overflow:hidden;background:radial-gradient(120% 80% at 70% 40%,#2B2016 0%,#1B140F 55%,#120d09 100%)}
#cvt{position:absolute;left:70px;right:70px;top:200px;font:900 140px/0.95 Inter,sans-serif;letter-spacing:-0.01em;color:#F3E7D3;text-shadow:0 8px 40px rgba(0,0,0,.6)}#cvt span{color:#F5B04A}
#cvs{position:absolute;left:76px;top:500px;font:800 52px/1.12 Inter,sans-serif;color:#F3E7D3}
#cvimg{position:absolute;left:76px;right:76px;top:680px;height:820px;border-radius:24px;overflow:hidden;border:3px solid #E3A23B;box-shadow:0 0 40px rgba(245,176,74,.35)}
#cvimg>img,#cvb img{position:absolute;inset:0;width:928px;height:820px;object-fit:cover}#cvb{position:absolute;inset:0;clip-path:inset(0 0 0 50%)}
#cvimg i{position:absolute;left:50%;top:0;bottom:0;width:5px;margin-left:-2px;background:#fff;box-shadow:0 0 16px #fff}
#cvimg b{position:absolute;top:18px;padding:6px 14px;border-radius:10px;background:rgba(27,20,15,.9);border:2px solid #E3A23B;font:800 30px Inter,sans-serif;color:#F3E7D3}#cvimg b.l{left:18px}#cvimg b.r{right:18px;background:#F5B04A;color:#1B140F}
#cvpill{position:absolute;left:76px;top:1560px;padding:12px 22px;border-radius:14px;background:rgba(60,38,14,.92);border:2px solid #E3A23B;font:800 40px Inter,sans-serif;color:#F3E7D3}"""
open(f"{P}/index.html", "w").write(f"""<!doctype html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="30">
{"".join(H)}
<audio id="music" class="clip" src="assets/music_tune.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.8" data-fade-in="0.3" data-fade-out="2.5"></audio>
{"".join(SFX)}
</div><script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(J)}
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>""")
print("END", END, "areas", TA, TB, "next", TN, "cta", TC, "credits", TK)
