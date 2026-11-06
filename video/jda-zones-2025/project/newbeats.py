# ---- voice timeline (words.json from Ashwil's recording) ----
import re as _re
words = [{"t": w["text"], "s": w["start"]} for w in json.load(open("words.json"))]
END = round(words[-1]["s"] + 0.75, 2)
def cue(*seq, after=0.0):
    seq = [s.lower() for s in seq]
    for i, w in enumerate(words):
        if w["s"] < after: continue
        if all(i + k < len(words) and _re.sub(r"[^\w]", "", words[i + k]["t"].lower()).startswith(seq[k]) for k in range(len(seq))): return w["s"]
    raise KeyError(seq)
K = {n: cue(*s) for n, s in {"oct": ("in", "october"), "before": ("before",), "now": ("now", "27"), "tf": ("twentyfive",), "add": ("add", "them"),
     "four": ("that", "is", "four"), "know": ("the", "jaipur", "you"), "z3": ("zone", "3"), "big": ("and", "the", "biggest"), "front": ("now", "look"),
     "all": ("all", "of", "this"), "stop": ("and", "it", "may"), "bhaskar": ("bhaskar",), "why": ("so", "why"), "one": ("1",), "two": ("2", "conversion"),
     "three": ("3", "rules"), "test": ("so", "quick"), "jag": ("jagatpura",), "vai": ("vaishali",), "man": ("mansarovar",), "tonk": ("tonk",),
     "which": ("which", "zone", "are"), "comment": ("comment",), "send": ("send", "this")}.items()}
FACE_END = K["oct"] - 0.15

# 0 · cover thumbnail (0–0.55), then face full-screen for the opening line
H2 = []
H2.append('<div id="cover"><div id="cvmap"></div><div id="cvtxt"><b>JAIPUR IS NOW<br/>BIGGER THAN <i class="y">GOA</i></b>'
          '<span>27 ZONES · 6,000 SQ KM</span></div><img id="cvme" src="assets/img/thumb_cut.png"/><div id="cvarrow">↓ is your plot inside?</div></div>')
J.append('tl.set("#cover", {opacity:1}, 0); tl.to("#cover", {opacity:0, duration:.25}, 0.55);')
J.append(f'tl.set("#world", {{attr:{{viewBox:"{vb(RC, RW * 1.6)}"}}}}, 0);')
J.append(f'tl.set("#maplayer", {{opacity:0}}, 0); tl.set("#maplayer", {{opacity:1}}, {FACE_END:.2f});')
J.append(f'tl.fromTo("#avatar", {{opacity:1, scale:1}}, {{opacity:0, scale:1.08, duration:.6, ease:"power2.in"}}, {FACE_END:.2f});')
H2.append('<div id="hook"><b>JAIPUR IS NOW<br/>BIGGER THAN <i class="y">GOA</i></b></div>')
J.append(f'tl.fromTo("#hook", {{opacity:0, scale:1.15}}, {{opacity:1, scale:1, duration:.4, ease:"back.out(2)"}}, 0.6); tl.to("#hook", {{opacity:0, duration:.3}}, {FACE_END - 0.3:.2f});')
sfx("impact-bass-1", 0.55, 0.5)

# B1 · office order: map comes alive
t0 = FACE_END
cam(t0, RC, RW * 1.15, 2.4, "power2.out")
J.append(f'tl.to("#region", {{strokeDashoffset:0, duration:1.6, ease:"power2.inOut"}}, {t0 + .1:.2f});')
for i, k in enumerate(ALL): zon(k, t0 + .4 + 0.04 * i, 1, .2)
for k in ALL: zon(k, t0 + 2.2, 0.15, .4)
chip("c1", "JDA OFFICE ORDER", "Dated 10 October 2025", t0 + .2, K["before"])
photo("pjda", "jda.jpg", "Jaipur Development Authority", "Image supplied", K["oct"] + 1.6, K["before"], x=60, y=430, w=960, h=620)
sfx("riser", t0, 0.25)

# B2 · before
photo("pold", "zones_old.jpg", "BEFORE · the old JDA zone map", "Image supplied", K["before"], K["now"], x=170, y=270, w=740, h=1000, fit="contain")
sfx("whoosh-short", K["before"] - .1, 0.4)

# B3 · now 27
H.append('<div id="count"><span id="cnum">14</span><em>ZONES</em></div>')
J.append(f'tl.fromTo("#count", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.35, ease:"back.out(2)"}}, {K["now"] - .1:.2f}); tl.to("#count", {{opacity:0, duration:.3}}, {K["add"] - .3:.2f});')
J.append(f'const cn={{v:14}}; tl.to(cn, {{v:27, duration:{K["now"] + 0.65 - K["now"]:.2f}, ease:"none", onUpdate:()=>{{document.getElementById("cnum").textContent=Math.round(cn.v)}}}}, {K["now"]:.2f});')
order = sorted(ALL, key=lambda k: math.hypot(ZONES[k]["ctr"][0] - CC[0], ZONES[k]["ctr"][1] - CC[1]))
for i, k in enumerate(order):
    t = K["now"] + 2.2 * i / len(order); zon(k, t, 1, .15); num(k, t, 1, .15)
    if i % 3 == 0: sfx("click-soft", t, 0.3)
J.append(f'tl.to(["#zPRNN", "#zPRNS"], {{fillOpacity:1, duration:.3, yoyo:true, repeat:5}}, {K["tf"] + 1.2:.2f});')

# B4 · 6000 sq km
J.append(f'tl.to("#regionglow", {{opacity:1, duration:.4, yoyo:true, repeat:5}}, {K["add"]:.2f});')
for k in ALL: num(k, K["add"] - .1, 0, .3)
H.append('<div id="bars"><b>AREA · SQ KM</b>'
         '<div class="br"><i>JDA region</i><s style="width:100%"></s><u>5,994</u></div>'
         '<div class="br"><i>Goa (state)</i><s style="width:61.8%"></s><u>3,702</u></div>'
         '<div class="br"><i>Delhi (NCT)</i><s style="width:24.8%"></s><u>1,484</u></div></div>')
J.append(f'tl.fromTo("#bars", {{opacity:0, y:-20}}, {{opacity:1, y:0, duration:.35}}, {K["add"] + .2:.2f}); tl.from("#bars s", {{scaleX:0, transformOrigin:"0 50%", duration:.8, stagger:.25, ease:"power3.out"}}, {K["add"] + .4:.2f}); tl.to("#bars", {{opacity:0, duration:.3}}, {K["know"] - .3:.2f});')
J.append(f'tl.to("#bars .br:nth-child(4)", {{scale:1.06, duration:.3, yoyo:true, repeat:3}}, {K["four"] + .4:.2f}); tl.to("#bars .br:nth-child(3)", {{scale:1.06, duration:.3, yoyo:true, repeat:3}}, {K["four"] + 2.0:.2f});')
sfx("whoosh", K["add"], 0.3)

# B5 · the core
cam(K["know"], CC, CWID * 1.9, 1.8)
J.append(f'tl.to("#hi", {{opacity:1, duration:.8}}, {K["know"] + .2:.2f});')
for k in ALL:
    if k not in CORE: zon(k, K["know"], 0.12, .5)
for k in CORE: zon(k, K["know"] + .3, .8, .4); num(k, K["know"] + 1.0, 1, .3)
J.append(f'tl.to("#z3", {{fillOpacity:1, duration:.35, yoyo:true, repeat:5}}, {K["z3"]:.2f});')
for k in CORE:
    if k != "3": zon(k, K["z3"], .3, .3)
label("l3", ZONES["3"]["ctr"], "ZONE 3 · 2 SQ KM", K["z3"], K["big"], at=K["know"] + 2, cls="big")
sfx("ping", K["z3"], 0.4)

# B6 · the giant
cam(K["big"], RC, RW * 1.15, 1.6)
J.append(f'tl.to("#hi", {{opacity:0, duration:.6}}, {K["big"]:.2f});')
for k in CORE: num(k, K["big"], 0, .2); zon(k, K["big"], .15, .4)
zon("13", K["big"] + .6, 1, .4); num("13", K["big"] + .6, 1, .3)
J.append(f'tl.to("#z13", {{fillOpacity:.9, duration:.4, yoyo:true, repeat:5}}, {K["big"] + 1.2:.2f});')
label("l13", ZONES["13"]["ctr"], "AMER &amp;<br/>JAMWARAMGARH<br/><span class='y'>596 SQ KM</span>", K["big"] + 1.6, K["front"], at=K["big"] + 2)
sfx("whoosh-short", K["big"], 0.35)

# B7 · the new frontier (zones light as each name is spoken)
zon("13", K["front"], .15, .4); num("13", K["front"], 0, .2)
NAMES = {"15": "Shahpura", "16": "Chomu", "17": "Jalsoo", "18": "Jobner", "19": "Mozmabad", "20": "Dudu", "21": "Phagi", "22": "Madhorajpura", "23": "Chaksu", "24": "Bassi · Toonga", "25": "Andhi"}
SPOKEN = {"15": "shahpura", "16": "chomu", "17": "jalsoo", "18": "jobner", "20": "dudu", "21": "phagi", "22": "madhorajpura", "23": "chaksu", "24": "bassi", "25": "andhi"}
TT = {k: cue(v) - .1 for k, v in SPOKEN.items()}; TT["19"] = TT["20"]
for k in OUTER:
    t = TT[k]
    zon(k, t, 1, .25); label(f"lo{k}", ZONES[k]["ctr"], f"{k} · {NAMES[k]}", t, K["stop"], at=K["front"] + 1.5, cls="sm")
    sfx("pop", t, 0.22)
J.append(f'tl.to("#z24", {{fillOpacity:1, duration:.3, yoyo:true, repeat:1}}, {cue("toonga") - .1:.2f});')
J.append(f'tl.to("#regionglow", {{opacity:1, duration:.35, yoyo:true, repeat:3}}, {K["all"]:.2f});')

# B8 · may grow again
for k in OUTER: zon(k, K["stop"], .3, .4)
photo("pnews", "news.jpg", "Master Plan 2047 report", "Dainik Bhaskar · image supplied", K["stop"] + .3, K["why"], x=140, y=270, w=800, h=1060, fit="contain")
J.append(f'tl.to("#pnews img", {{scale:1.9, x:-60, y:330, duration:1.2, ease:"power2.inOut"}}, {K["bhaskar"] + .8:.2f});')

# B9 · why it matters
J.append(f'tl.to("#dim", {{opacity:.6, duration:.5}}, {K["why"]:.2f});')
sfx("impact-bass-1", K["why"], 0.4)
chip("w1", "① APPROVAL", "Check the scheme's approval — roads, layout &amp; patta", K["one"], K["two"])
photo("pscheme", "scheme.jpg", "An approved scheme layout", "Image supplied · branding cropped", K["one"] + .3, K["two"], x=190, y=470, w=700, h=780)
chip("w2", "② CONVERSION", "Farm land needs 90-A conversion before you can build", K["two"], K["three"])
chip("w3", "③ RULES", "Setbacks, FAR &amp; height depend on your zone &amp; the master plan", K["three"], K["test"])
for t in (K["one"], K["two"], K["three"]): sfx("whoosh-short", t, 0.3)

# B10 · quiz
J.append(f'tl.to("#dim", {{opacity:.25, duration:.5}}, {K["test"]:.2f});')
QUIZ = [("jagatpura.jpg", "Jagatpura", "Image supplied", "jag"), ("vaishali.jpg", "Vaishali Nagar", "Image supplied", "vai"),
        ("mansarovar.jpg", "Mansarovar", "Pacific Jaipur · rendering · image supplied", "man"), ("tonk.jpg", "Tonk Road", "Image supplied", "tonk")]
nxt = [K["vai"], K["man"], K["tonk"], K["comment"]]
for i, (src, nm, cr, key) in enumerate(QUIZ):
    photo(f"q{i}", src, f"{nm} → <span class='y'>Zone ?</span>", cr, K[key] - .15, nxt[i] - .1, x=90, y=330, w=900, h=900)

# B11 · CTA
H2.append('<div id="share"><svg viewBox="0 0 24 24" width="84" height="84"><path d="M3 11l18-8-8 18-2-8z" style="fill:none;stroke:#fff;stroke-width:2;stroke-linejoin:round"/></svg><span>Send to someone buying a plot</span></div>')
J.append(f'tl.fromTo("#share", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.4, ease:"back.out(2)"}}, {K["send"]:.2f}); tl.fromTo("#share svg", {{scale:1}}, {{scale:1.18, duration:.45, yoyo:true, repeat:5}}, {K["send"] + .5:.2f});')
chip("ccta", "COMMENT BELOW", "Your area → I'll tell you your zone", K["comment"], END + .3)
for k in ALL: zon(k, K["comment"], .6, .6)
sfx("sparkle", K["comment"], 0.35)

# captions (verbatim, bottom)
EMW = {"goa", "goa.", "october", "2025,", "14", "27.", "twenty-five", "prithviraj", "6000", "four", "delhi,", "3", "2", "13,", "frontier", "jda", "2047,", "272",
       "approval.", "conversion.", "rules.", "90-a", "jda-approved", "zone", "zones", "jaipur.", "comment"}
def glen(g): return len(" ".join(w["t"] for w in g))
groups, cur = [], []
for i, w in enumerate(words):
    cur.append(w); nx = words[i + 1] if i + 1 < len(words) else None
    if nx is None or glen(cur + [nx]) > 22 or w["t"][-1] in ".?!" or (w["t"][-1] == "," and glen(cur) >= 10) or (nx["s"] - w["s"] > 1.0):
        groups.append(cur); cur = []
CAPS = []
for gi, g in enumerate(groups):
    nx = groups[gi + 1][0]["s"] - 0.03 if gi + 1 < len(groups) else END
    a, b = round(max(0.6, g[0]["s"] - 0.05), 2), round(min(nx, g[-1]["s"] + 0.8), 2)
    CAPS.append((a, b, " ".join(w["t"] for w in g)))
    H2.append(f'<div class="cp" id="cp{gi}">' + " ".join(f'<span class="{"y" if w["t"].lower() in EMW else ""}">{w["t"]}</span>' for w in g) + '</div>')
    J.append(f'tl.fromTo("#cp{gi}", {{opacity:0, scale:.92}}, {{opacity:1, scale:1, duration:.12}}, {a}); tl.to("#cp{gi}", {{opacity:0, duration:.06}}, {b - .06:.2f});')
json.dump([{"start": a, "end": b, "text": t} for a, b, t in CAPS], open("captions.json", "w"), indent=0)
