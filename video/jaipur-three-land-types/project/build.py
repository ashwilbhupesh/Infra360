import sys, json, re
P, WJ = sys.argv[1], sys.argv[2]
VIDEO_END = 174.6
END = 178.6
exec(open(__file__.replace("build.py", "base_part.py")).read())  # BASE, INSERTS, rel(), scene()

# ---------- captions: Parakeet words (edited timeline), spellings checked against Whisper ----------
FIX = {"JD": "JDA", "GD": "JDA", "GOD": "JDA", "GDA": "JDA", "Patta,": "patta,", "Patta.": "patta.", "Ghana": "Gram", "Now": "Now"}
EM = {"three", "jda", "patta", "collector-approved", "municipality-approved", "gram", "panchayat", "credibility", "norms", "60:40", "40%", "60%",
      "facilities", "plots", "bank", "financing", "90%", "society", "pattas", "multiple", "chaos", "regularized", "few", "eligible",
      "agricultural", "true", "value", "years", "periphery", "acre", "square", "feet", "approved", "plot", "confidence", "resale", "comfortable",
      "cheaper", "camp", "converted", "long", "term", "expert", "jaipur"}
heard = json.load(open(WJ))
toks = []
i = 0
while i < len(heard):
    w = heard[i]; t = w["text"]; s = w["start"]
    nxt = heard[i + 1]["text"] if i + 1 < len(heard) else ""
    if t == "60" and nxt == "forty": t = "60:40"; i += 1
    elif t in ("forty", "sixty", "ninety") and nxt == "percent": t = {"forty": "40%", "sixty": "60%", "ninety": "90%"}[t]; i += 1
    elif t == "surrender" and 59 < s < 61: t = "surrendered"
    elif t == "the" and 60.5 < s < 60.6: t = "their"
    elif t == "term" and 62 < s < 62.2: t = "return"
    elif t == "the" and 61.9 < s < 62.0: t = None  # "in return of" (Whisper); Parakeet heard "in the term of"
    elif t == "will" and 67.2 < s < 67.3: t = "would"
    elif t == "The" and 83.8 < s < 83.9: t = "the"
    else: t = FIX.get(t, t)
    if t is not None:
        k = re.sub(r"[^\w:%-]", "", t.lower())
        toks.append({"t": t, "s": round(s, 3), "em": k in EM})
    i += 1
for k in range(1, len(toks)):
    if toks[k-1]["t"][-1] in ".?" and toks[k]["t"][0].islower(): toks[k]["t"] = toks[k]["t"][0].upper() + toks[k]["t"][1:]
def glen(g): return len(" ".join(w["t"] for w in g))
groups, cur = [], []
for i, w in enumerate(toks):
    cur.append(w); nxt = toks[i + 1] if i + 1 < len(toks) else None
    brk = nxt is None or glen(cur + [nxt]) > 30 or w["t"][-1] in ".?" or (w["t"][-1] == "," and glen(cur) >= 14) or (nxt and nxt["s"] - w["s"] > 1.3)
    if brk: groups.append(cur); cur = []
merged = []
for g in groups:
    if merged and len(g) == 1 and glen(merged[-1] + g) <= 36 and merged[-1][-1]["t"][-1] not in ".?": merged[-1] += g
    else: merged.append(g)
groups = merged
caps = []
for gi, g in enumerate(groups):
    nxt = groups[gi + 1][0]["s"] - 0.04 if gi + 1 < len(groups) else VIDEO_END
    last = g[-1]["s"] + max(0.35, 0.06 * len(g[-1]["t"]))
    caps.append((round(max(0.08, g[0]["s"] - 0.06), 2), round(min(nxt, last + 0.55), 2), g))
def ctext(g): return " ".join(w["t"] for w in g)
json.dump({"captions": [{"start": a, "end": b, "text": ctext(g)} for a, b, g in caps]}, open(f"{P}/../captions.json", "w"), indent=1, ensure_ascii=False)

FADE = '<div class="panel-fade"></div><div class="rep">Representative footage</div>'
ROWS = lambda cid, items, top, step=96: "".join(f'<div class="row" id="{cid}-r{k}" style="top:{top + k*step}px"><b>&#10003;</b>{n}</div>' for k, (n, _) in enumerate(items))
ROWJS = lambda cid, items, s: "\n".join(f'      IN("#{cid}-r{k}", {max(0.05, rel(t, s))}, {{ x: -20, y: 0 }}, {{ x: 0 }});' for k, (_, t) in enumerate(items))
def foot(cid, a, b, src, tag, t, amb=True):
    scene(cid, a, b, FADE + f'<div class="tag{" amb" if amb else ""}" style="left:96px;top:760px" id="{cid}-t">{tag}</div>', f'      IN("#{cid}-t", {max(0.1, rel(t, a))});', [(src, 0, round(b - a, 2))])
def card(cid, x, y, w, h, inner, amb=False):
    return (f'<div id="{cid}" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;border-radius:24px;'
            + ("border:3px solid #E3A23B;background:rgba(60,38,14,0.55)" if amb else "border:2px solid rgba(243,231,211,0.3);background:rgba(27,20,15,0.6)") + f'">{inner}</div>')

# ===== TYPE 01 — government-approved plots =====
s = 7.40
auth = [("JDA patta", 7.68), ("Collector-approved colony", 10.88), ("Municipality-approved", 13.12), ("Gram Panchayat-approved", 14.72)]
scene("a1", s, 16.45, '<div class="lbl" style="position:absolute;left:96px;top:240px;color:#E3A23B">Government-approved land</div>' + ROWS("a1", auth, 300, 110)
      + '<div class="note">Examples as spoken · verify the approving authority</div>', ROWJS("a1", auth, s))
s = 24.20
grid = "".join(f'<rect class="ln a2-p" x="{30+c*140}" y="{30+r*96}" width="124" height="80" rx="4"/>' for r in range(3) for c in range(6))
scene("a2", s, 36.95, f"""
      <div class="lbl" style="position:absolute;left:96px;top:240px;color:#E3A23B">60:40 layout</div>
      <svg style="position:absolute;left:96px;top:290px;width:888px;height:320px" viewBox="0 0 900 324">{grid}
        <rect id="a2-fac" x="20" y="20" width="860" height="296" rx="10" style="fill:none;stroke:#E3A23B;stroke-width:3;stroke-dasharray:12 10;opacity:0"/></svg>
      <div style="position:absolute;left:96px;right:96px;top:650px;height:64px;border-radius:14px;overflow:hidden;display:flex;border:1.5px solid rgba(243,231,211,0.25)">
        <div id="a2-b60" style="width:60%;background:#E3A23B;color:#1B140F;font-family:Inter,sans-serif;font-weight:800;font-size:34px;display:flex;align-items:center;padding-left:22px">60% plots for sale</div>
        <div id="a2-b40" style="width:40%;background:rgba(243,231,211,0.14);color:#F3E7D3;font-family:Inter,sans-serif;font-weight:800;font-size:34px;display:flex;align-items:center;padding-left:22px">40% facilities</div></div>
      <div class="lbl" id="a2-f" style="position:absolute;left:96px;top:740px">Roads · parks · amenities</div>
      <div class="note">Illustrative · verify current township policy</div>""",
      f"""      tl.fromTo('.a2-p', {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2, stagger: 0.02 }}, 0.1);
      IN("#a2-b40", {rel(29.8, s)}, {{ x: 20, y: 0 }}, {{ x: 0 }}); tl.to("#a2-fac", {{ opacity: 1, duration: 0.3 }}, {rel(29.8, s)}); IN("#a2-f", {rel(32.92, s)});
      IN("#a2-b60", {rel(33.96, s)}, {{ x: -20, y: 0 }}, {{ x: 0 }});""")
foot("a3", 39.70, 43.10, "calc", "Bank financing available", 39.94)
s = 43.10
scene("a4", s, 47.30, """
      <div class="lbl" style="position:absolute;left:96px;top:240px;color:#E3A23B">Example as stated</div>
      <div id="a4-n" class="serif" style="position:absolute;left:90px;top:290px;font-size:260px;line-height:1;color:#E3A23B">90%</div>
      <div id="a4-t" style="position:absolute;left:96px;top:580px;right:96px;font-family:Inter,sans-serif;font-weight:700;font-size:48px;line-height:1.2;color:#F3E7D3">of plot value, bank-financed (“up to”)</div>
      <div class="note">Actual loan depends on bank, loan size &amp; property</div>""",
      f'      IN("#a4-n", {rel(44.02, s)}, {{ scale: 0.94 }}, {{ scale: 1 }}); IN("#a4-t", {rel(44.82, s)});')

# ===== TYPE 02 — society pattas =====
foot("b1", 50.80, 54.37, "society", "Many housing societies", 51.58, amb=False)
foot("b2", 54.37, 57.77, "paper", "Earlier…", 54.56, amb=False)
s = 57.80
NODE = lambda i, x, y, w, t, sub, amb=False: card(i, x, y, w, 150, f'<div style="position:absolute;left:28px;top:22px" class="lbl">{sub}</div><div class="serif" style="position:absolute;left:28px;top:58px;font-size:60px;color:{"#E3A23B" if amb else "#F3E7D3"}">{t}</div>', amb)
scene("b3", s, 69.50, NODE("b3-n1", 96, 260, 888, "Agricultural land", "Landowners surrendered") +
      '<div id="b3-a1" class="serif" style="position:absolute;left:500px;top:420px;font-size:70px;color:#E3A23B">↓</div>' +
      NODE("b3-n2", 96, 510, 888, "Housing society", "…to a society, which issued", True) +
      '<div id="b3-a2" class="serif" style="position:absolute;left:500px;top:670px;font-size:70px;color:#E3A23B">↓</div>' +
      '<div class="tag amb" id="b3-n3" style="left:96px;top:770px">Society pattas</div>' +
      '<div class="tag" id="b3-j" style="left:520px;top:770px;font-size:32px">Like land → JDA → JDA patta</div><div class="note">Illustrative</div>',
      f"""      IN("#b3-n1", {rel(57.95, s)}); IN("#b3-a1", {rel(58.08, s)}); IN("#b3-n2", {rel(58.24, s)});
      IN("#b3-j", {rel(61.12, s)}); IN("#b3-a2", {rel(67.28, s)}); IN("#b3-n3", {rel(67.52, s)});""")
s = 76.00
docs = "".join(f'<g id="b4-d{k}" transform="translate({330 + k*70} {60 + k*40}) rotate({-8 + k*8})"><rect x="0" y="0" width="220" height="290" rx="10" style="fill:#1B140F;stroke:#F3E7D3;stroke-width:4"/>' +
               "".join(f'<path class="ln" style="stroke-width:3;opacity:.5" d="M24 {50+j*34} H{196-(j%2)*40}"/>' for j in range(6)) +
               f'<text x="24" y="270" style="font-family:JetBrains Mono,monospace;font-size:34px;fill:#E3A23B">PATTA {k+1}</text></g>' for k in range(3))
scene("b4", s, 82.45, f"""
      <svg data-layout-allow-overlap style="position:absolute;left:96px;top:240px;width:888px;height:480px" viewBox="0 0 900 486">
        <path class="ln-a" d="M30 420 L250 380 L300 470 L60 480 Z" style="fill:rgba(227,162,59,0.15)"/>
        <text x="60" y="360" style="font-family:Instrument Serif,serif;font-style:italic;font-size:44px;fill:#E3A23B">One plot</text>{docs}</svg>
      <div class="tag amb" id="b4-t" style="left:96px;top:770px">Multiple pattas · same land</div>
      <div class="note" style="left:auto;right:96px">Illustrative</div>""",
      f"""      IN("#b4-d0", {rel(76.68, s)}); IN("#b4-d1", {rel(77.08, s)}); IN("#b4-d2", {rel(77.48, s)}); IN("#b4-t", {rel(78.2, s)});""")
foot("b5", 93.70, 97.10, "mag", "Check: can it issue pattas today?", 94.1)

# ===== TYPE 03 — agricultural land =====
foot("c1", 105.40, 108.80, "plots", "Agricultural land", 105.58)
foot("c2", 112.50, 115.90, "road", "Hold for years", 114.26)
s = 119.50
farms = "".join(f'<rect class="ln c3-f" x="{x}" y="{y}" width="70" height="56" rx="3" style="opacity:.6"/>' for x, y in [(80,80),(160,60),(700,70),(780,120),(90,380),(760,420),(170,450),(820,300),(60,240)])
scene("c3", s, 126.85, f"""
      <svg style="position:absolute;left:96px;top:240px;width:888px;height:510px" viewBox="0 0 900 516">{farms}
        <rect id="c3-p" x="700" y="230" width="90" height="70" rx="4" style="fill:rgba(227,162,59,0.25);stroke:#E3A23B;stroke-width:4"/>
        <text x="660" y="340" style="font-family:Inter,sans-serif;font-weight:700;font-size:34px;fill:#E3A23B">Your land</text>
        <circle id="c3-c" cx="400" cy="260" r="120" style="fill:rgba(243,231,211,0.10);stroke:#F3E7D3;stroke-width:4"/>
        <text x="400" y="272" text-anchor="middle" style="font-family:Instrument Serif,serif;font-size:56px;fill:#F3E7D3">City</text></svg>
      <div class="tag" id="c3-t1" style="left:96px;top:770px">City expands via the periphery</div>
      <div class="tag amb" id="c3-t2" style="left:96px;top:770px">Becomes part of the city</div>
      <div class="note" style="top:200px">Illustrative · not a forecast</div>""",
      f"""      tl.fromTo("#c3-c", {{ attr: {{ r: 120 }} }}, {{ attr: {{ r: 330 }}, duration: 4.6, ease: "power1.inOut" }}, {rel(120.6, s)});
      IN("#c3-t1", {rel(120.83, s)}); tl.to("#c3-t1", {{ opacity: 0, duration: 0.2 }}, {rel(124.35, s)}); IN("#c3-t2", {rel(124.6, s)});
      tl.to("#c3-p", {{ attr: {{ fill: "rgba(227,162,59,0.6)" }}, duration: 0.4 }}, {rel(125.3, s)});""")
s = 126.85
scene("c4", s, 133.30, card("c4-a", 96, 270, 888, 190, '<div style="position:absolute;left:32px;top:28px" class="lbl">Before conversion</div><div class="serif" style="position:absolute;left:32px;top:70px;font-size:84px;color:#F3E7D3">Price per acre</div>')
      + '<div id="c4-ar" class="serif" style="position:absolute;left:500px;top:470px;font-size:80px;color:#E3A23B">↓</div>'
      + card("c4-b", 96, 580, 888, 190, '<div style="position:absolute;left:32px;top:28px" class="lbl">After approval</div><div class="serif" style="position:absolute;left:32px;top:70px;font-size:84px;color:#E3A23B">Price per sq ft</div>', True)
      + '<div class="note">1 acre = 43,560 sq ft · illustrative, not a forecast</div>',
      f'      IN("#c4-a", {rel(129.15, s)}); IN("#c4-ar", {rel(130.27, s)}); IN("#c4-b", {rel(131.15, s)});')

# ===== MY ROADMAP =====
s = 135.20
STEP = lambda i, n, t, sub, y: f'<div id="{i}" style="position:absolute;left:96px;right:96px;top:{y}px;height:150px;border-radius:22px;border:2px solid rgba(243,231,211,0.3);background:rgba(27,20,15,0.65)"><div style="position:absolute;left:28px;top:26px;font-family:JetBrains Mono,monospace;font-size:44px;color:#E3A23B">{n}</div><div style="position:absolute;left:120px;top:24px;font-family:Inter,sans-serif;font-weight:800;font-size:44px;color:#F3E7D3">{t}</div><div id="{i}-s" style="position:absolute;left:120px;top:86px;font-family:Inter,sans-serif;font-weight:600;font-size:32px;color:#C9B79C">{sub}</div></div>'
scene("d1", s, 148.40, STEP("d1-1", "01", "Start with an approved plot", "Confidence · better resale value", 280) + STEP("d1-2", "02", "Then society patta / agri land", "Once you're comfortable", 460) + STEP("d1-3", "03", "Long term: agricultural land", "If you can hold", 640)
      + '<div class="lbl" style="position:absolute;left:96px;top:230px;color:#E3A23B">The roadmap</div>',
      f"""      IN("#d1-1", {rel(135.55, s)}); tl.fromTo("#d1-1-s", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {rel(137.63, s)});
      tl.to("#d1-1", {{ borderColor: "#E3A23B", duration: 0.3 }}, {rel(135.8, s)});
      IN("#d1-2", {rel(142.59, s)}); IN("#d1-3", {rel(146.51, s)}, {{ y: 16 }});""")
s = 148.40
scene("d2", s, 161.00, """
      <div class="lbl" style="position:absolute;left:96px;top:230px;color:#E3A23B">Society patta</div>
      <div class="tag" id="d2-t1" style="left:96px;top:290px">Typically cheaper than JDA plots</div>
      <div id="d2-f" style="position:absolute;left:96px;right:96px;top:420px;height:250px;border-radius:24px;border:3px solid #E3A23B;background:rgba(60,38,14,0.55)">
        <div class="lbl" style="position:absolute;left:32px;top:28px">If you get into a JDA camp</div>
        <div class="serif" id="d2-c1" style="position:absolute;left:32px;top:80px;font-size:66px;color:#F3E7D3">Society patta</div>
        <div class="serif" id="d2-c2" style="position:absolute;left:32px;top:156px;font-size:66px;color:#E3A23B">→ converted to JDA patta</div></div>
      <div class="tag amb" id="d2-t2" style="left:96px;top:720px">Potential capital appreciation</div>
      <div class="note">Eligibility varies · appreciation not guaranteed</div>""",
      f"""      IN("#d2-t1", {rel(149.47, s)}); IN("#d2-f", {rel(152.45, s)}); IN("#d2-c1", {rel(154.53, s)}); IN("#d2-c2", {rel(155.41, s)}, {{ x: -20, y: 0 }}, {{ x: 0 }});
      IN("#d2-t2", {rel(157.97, s)});""")
foot("e1", 168.80, 172.10, "docs", "Consult an expert first", 169.7)

# ---------- chrome ----------
SECT = [(6.88, "TYPE 01/03", "Government-approved plots"), (47.46, "TYPE 02/03", "Society pattas"), (104.70, "TYPE 03/03", "Agricultural land"),
        (132.59, "MY ROADMAP", "Where to start"), (167.14, "BEFORE YOU BUY", "Consult an expert")]
cards = [(f"hd-{k+1}", t, (SECT[k+1][0] if k + 1 < len(SECT) else VIDEO_END), c, h) for k, (t, c, h) in enumerate(SECT)]
CALL = [("co-0", 4.48, 6.80, "Three kinds of land"), ("co-1", 19.30, 23.95, "Higher credibility · built to norms"),
        ("co-2", 73.80, 76.00, "Less credible than government bodies"), ("co-3", 85.54, 91.60, "Regularised · only a few can still issue pattas"),
        ("co-4", 99.30, 104.20, "Verify the society's authority"), ("co-5", 116.58, 119.45, "Long-term · not guaranteed"),
        ("co-6", 163.62, 166.95, "Long term → agricultural land"), ("co-7", 172.10, VIDEO_END, "Call / WhatsApp 96721 19046")]
hd_html = "".join(f'<div id="{i}" class="hd"><div class="hd-c">{c}</div><div class="hd-h">{h}</div></div>' for i, _, _, c, h in cards)
co_html = "".join(f'<div id="{i}" class="co">{t}</div>' for i, _, _, t in CALL)
js = "".join(f"""
      tl.fromTo("#{i}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01 }}, {t});
      tl.fromTo("#{i} .hd-c", {{ opacity: 0, x: -14 }}, {{ opacity: 1, x: 0, duration: 0.35, ease: "power3.out" }}, {t});
      tl.fromTo("#{i} .hd-h", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, {t + 0.06});
      tl.to("#{i}", {{ opacity: 0, duration: 0.2, ease: "power2.in" }}, {round(e - 0.2, 2)});""" for i, t, e, _, _ in cards)
js += "".join(f"""
      tl.fromTo("#{i}", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, {a});
      tl.to("#{i}", {{ opacity: 0, duration: 0.2 }}, {round(b - 0.2, 2)});""" for i, a, b, _ in CALL)
open(f"{P}/compositions/chrome.html", "w").write(f"""<template>
  <style>{BASE}
    .hd {{ position: absolute; left: 96px; top: 1226px; max-width: 820px; padding: 14px 28px 16px 24px; border-radius: 18px; background: rgba(27,20,15,0.88); border-left: 6px solid #E3A23B; opacity: 0; }}
    .hd-c {{ font-family: "JetBrains Mono", monospace; font-size: 30px; letter-spacing: 0.2em; color: #E3A23B; }}
    .hd-h {{ font-family: "Inter", sans-serif; font-weight: 800; font-size: 52px; letter-spacing: 0.01em; line-height: 1.08; color: #F3E7D3; }}
    #op {{ position: absolute; left: 96px; right: 164px; top: 1226px; padding: 14px 28px 16px; border-radius: 20px; background: rgba(27,20,15,0.9); border-left: 6px solid #E3A23B; }}
    #op-a {{ font-family: "Inter", sans-serif; font-weight: 800; font-size: 54px; color: #F3E7D3; line-height: 1.05; }}
    #op-b {{ font-family: "Inter", sans-serif; font-weight: 900; font-size: 60px; color: #E3A23B; line-height: 1.05; }}
    #pg {{ position: absolute; left: 96px; right: 164px; top: 1196px; display: flex; gap: 10px; opacity: 0; }}
    #pg i {{ flex: 1; height: 7px; border-radius: 4px; background: rgba(27,20,15,0.55); box-shadow: 0 0 0 1px rgba(243,231,211,0.25); }}
    .co {{ position: absolute; left: 96px; top: 1118px; padding: 12px 22px; border-radius: 14px; background: rgba(60,38,14,0.92); border: 1.5px solid #E3A23B; font-family: "Inter", sans-serif; font-weight: 700; font-size: 38px; color: #F3E7D3; opacity: 0; white-space: nowrap; }}
  </style>
  <div id="root" data-composition-id="chrome" data-width="1080" data-height="1920">
    <div id="chrome-host" class="host clip" data-start="0" data-duration="{VIDEO_END}">
      <div id="op"><div id="op-a">JAIPUR REAL ESTATE</div><div id="op-b">3 KINDS OF LAND</div></div>
      <div id="pg">{"".join(f'<i id="pg-{k+1}"></i>' for k in range(len(SECT)))}</div>
      {hd_html}{co_html}
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#op", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, 0.12);
      tl.fromTo("#op-b", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35 }}, 0.5);
      tl.to("#op", {{ opacity: 0, y: -10, duration: 0.3, ease: "power2.in" }}, 6.55);
      tl.fromTo("#pg", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, 6.6);
      tl.to("#pg", {{ opacity: 0, duration: 0.3 }}, {VIDEO_END - 0.35});{"".join(f"""
      tl.fromTo("#pg-{k+1}", {{ backgroundColor: "rgba(27,20,15,0.55)" }}, {{ backgroundColor: "#E3A23B", duration: 0.3 }}, {t});""" for k, (t, _, _) in enumerate(SECT))}{js}
      window.__timelines["chrome"] = tl;
    }})();
  </script>
</template>
""")

# ---------- captions ----------
spans = [f'<div id="cp-{gi}" class="cp"><div class="cp-in">' + "".join(f'<span class="w{" em" if w["em"] else ""}">{w["t"]}</span>' + ("" if w["t"].endswith("–") or k == len(g) - 1 else " ") for k, w in enumerate(g)) + "</div></div>" for gi, (a, b, g) in enumerate(caps)]
data = [[a, b, [w["s"] for w in g]] for a, b, g in caps]
open(f"{P}/compositions/captions.html", "w").write("""<template>
  <style>
    #root { position: absolute; inset: 0; pointer-events: none; }
    .cp { position: absolute; left: 96px; width: 820px; top: 1426px; display: flex; justify-content: center; opacity: 0; }
    .cp-in { max-width: 820px; text-align: center; padding: 12px 24px 14px; border-radius: 18px; background: rgba(20,14,10,0.82);
      font-family: "Inter", sans-serif; font-weight: 700; font-size: 56px; line-height: 1.2; color: #FFF8EE; }
    .w { opacity: 0.6; }
    .w.em { color: #F5B04A; }
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
    """ + "\n    ".join(spans) + """
  </div>
  <script>
    (function () {
      const tl = gsap.timeline({ paused: true });
      const G = """ + json.dumps(data) + """;
      G.forEach(([open, close, starts], i) => {
        const g = document.getElementById("cp-" + i);
        const ws = g.querySelectorAll(".w");
        tl.fromTo(g, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.12, ease: "power2.out" }, open);
        ws.forEach((w, k) => tl.fromTo(w, { opacity: 0.6 }, { opacity: 1, duration: 0.08, ease: "none" }, starts[k]));
        tl.to(g, { opacity: 0, duration: 0.1 }, close - 0.1);
        tl.set(g, { opacity: 0, visibility: "hidden" }, close);
      });
      window.__timelines["captions"] = tl;
    })();
  </script>
</template>
""")

# ---------- closing card ----------
steps = ["Approved plot — start here", "Society patta / agricultural land", "Long term: agricultural land"]
lis = "".join(f'<div class="ec-i"><b>{k+1:02d}</b>{t}</div>' for k, t in enumerate(steps))
ED = round(END - VIDEO_END, 2)
open(f"{P}/compositions/endcard.html", "w").write(f"""<template>
  <style>{BASE}
    #ec-k {{ position: absolute; left: 96px; top: 330px; }}
    #ec-t {{ position: absolute; left: 96px; right: 96px; top: 400px; font-family: "Instrument Serif", serif; font-size: 112px; line-height: 1.0; color: #F3E7D3; }}
    #ec-s {{ position: absolute; left: 96px; top: 530px; font-family: "Instrument Serif", serif; font-style: italic; font-size: 64px; color: #E3A23B; }}
    #ec-l {{ position: absolute; left: 96px; right: 96px; top: 700px; display: flex; flex-direction: column; gap: 26px; }}
    .ec-i {{ font-family: "Inter", sans-serif; font-weight: 600; font-size: 40px; color: #F3E7D3; display: flex; gap: 18px; align-items: baseline; white-space: nowrap; }}
    .ec-i b {{ font-family: "JetBrains Mono", monospace; font-weight: 400; font-size: 30px; color: #E3A23B; }}
    #ec-c {{ position: absolute; left: 96px; right: 164px; top: 1040px; padding: 26px 32px; border-radius: 22px; background: rgba(60,38,14,0.7); border: 2px solid #E3A23B; }}
    #ec-c .lbl {{ color: #E3A23B; }}
    #ec-n {{ font-family: "Inter", sans-serif; font-weight: 800; font-size: 76px; color: #F3E7D3; letter-spacing: 0.02em; margin-top: 6px; }}
    #ec-b {{ position: absolute; left: 0; right: 0; top: 1420px; text-align: center; font-family: "JetBrains Mono", monospace; font-size: 34px; letter-spacing: 0.3em; color: #C9B79C; }}
  </style>
  <div id="root" data-composition-id="endcard" data-width="1080" data-height="1920">
    <div id="endcard-host" class="host clip" data-start="0" data-duration="{ED}">
      <div id="endcard-bg" class="ins"><div class="grain"></div>
        <div id="ec-k" class="lbl">Jaipur Real Estate</div>
        <div id="ec-t">Ashwil Bhupesh</div><div id="ec-s">Know the land type first.</div>
        <div id="ec-l">{lis}</div>
        <div id="ec-c"><div class="lbl">Call / WhatsApp</div><div id="ec-n">96721 19046</div></div>
        <div id="ec-b">ASHWILLPOWER</div>
      </div>
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#endcard-bg", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, ease: "power2.out" }}, 0);
      tl.fromTo(["#ec-k", "#ec-t"], {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, 0.2);
      tl.fromTo("#ec-s", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, 0.5);
      tl.fromTo(".ec-i", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.3, stagger: 0.08, ease: "power3.out" }}, 0.6);
      tl.fromTo("#ec-c", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, 0.9);
      tl.fromTo("#ec-b", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, 1.1);
      window.__timelines["endcard"] = tl;
    }})();
  </script>
</template>
""")

# ---------- root ----------
hosts = "\n".join(f'      <div id="{c}" class="scene" style="z-index: 4" data-composition-id="{c}" data-composition-src="compositions/{c}.html" data-start="{s}" data-duration="{d}" data-track-index="{1 + k % 2}" data-track-kind="graphics" data-width="1080" data-height="1920"></div>' for k, (c, s, d) in enumerate(INSERTS))
sfx = [f'      <audio id="sfx-sec-{k+1}" class="clip" src="assets/sfx/click-soft.mp3" data-start="{t}" data-duration="0.36" data-track-index="{11 + k % 2}" data-volume="0.32"></audio>' for k, (t, _, _) in enumerate(SECT)]
sfx.append(f'      <audio id="sfx-end" class="clip" src="assets/sfx/chime.mp3" data-start="{VIDEO_END}" data-duration="2.2" data-track-index="13" data-volume="0.16" data-fade-out="0.8"></audio>')
PUNCH = [(0, 1.0), (6.88, 1.05), (16.4, 1.0), (47.46, 1.05), (54.37, 1.0), (72.63, 1.06), (82.4, 1.0), (91.6, 1.05), (104.7, 1.0), (116.0, 1.05), (119.5, 1.0), (132.59, 1.0), (161.0, 1.05), (167.14, 1.0), (172.1, 1.06)]
open(f"{P}/index.html", "w").write(f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #120D0A; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; }}
      #ground {{ position: absolute; inset: 0; background: #120D0A; }}
      #cam {{ position: absolute; inset: 0; transform-origin: 50% 30%; }}
      #avatar {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      .scene {{ position: absolute; inset: 0; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="30">
      <div id="ground"></div>
      <div id="cam" style="z-index: 1">
        <video id="avatar" class="clip" src="assets/avatar.mp4" data-start="0" data-duration="{VIDEO_END}" data-track-index="0" playsinline data-has-audio="true" data-volume="1"></video>
      </div>
{hosts}
      <div id="chrome" class="scene" style="z-index: 6" data-composition-id="chrome" data-composition-src="compositions/chrome.html" data-start="0" data-duration="{VIDEO_END}" data-track-index="3" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="captions" class="scene" style="z-index: 7" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{VIDEO_END}" data-track-index="4" data-track-kind="captions" data-width="1080" data-height="1920"></div>
      <div id="endcard" class="scene" style="z-index: 9" data-composition-id="endcard" data-composition-src="compositions/endcard.html" data-start="{VIDEO_END}" data-duration="{ED}" data-track-index="5" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.55" data-fade-in="1.0" data-fade-out="2.0"></audio>
{chr(10).join(sfx)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {json.dumps(PUNCH)}.forEach(([t, s]) => tl.set("#cam", {{ scale: s }}, t));
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
""")
json.dump({"inserts": INSERTS, "sections": SECT, "punch": PUNCH, "callouts": CALL}, open(f"{P}/../plan.json", "w"), indent=1)
tot = sum(d for _, _, d in INSERTS)
print("inserts", len(INSERTS), "seconds", round(tot, 1), f"{100*tot/VIDEO_END:.1f}%", "| caption groups", len(caps))
for a, b, g in caps: print(f"{a:6.2f}-{b:6.2f} [{glen(g):2d}] " + " ".join(("*" + w["t"] + "*") if w["em"] else w["t"] for w in g))
