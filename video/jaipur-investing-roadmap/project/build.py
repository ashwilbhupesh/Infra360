import sys, json, re
P, WJ = sys.argv[1], sys.argv[2]
VIDEO_END = 86.3
END = 90.3
exec(open(__file__.replace("build.py", "base_part.py")).read())  # BASE, INSERTS, rel(), scene()

# ---------- captions: Parakeet words, spelling fixed to the spoken words ----------
FIX = {"Kishangar": "Kishangarh", "Kishangar,": "Kishangarh–", "Bandikwi": "Bandikui", "preference.": "preference", "Is": "is",
       "Ashwill,": "Ashwil,", "Jaipur,": "Jaipur–"}
EM = {"trustworthy", "independent", "approved", "residential", "plots", "deals", "ownership", "farmhouses", "permitted", "legal", "access",
      "water", "maintenance", "agricultural", "eligibility", "exit", "nh48", "bandikui", "northern", "ring", "road", "kotputli", "alignment",
      "interchanges", "not", "guaranteed", "land", "flats", "long-term", "location", "growth", "negotiating", "power", "stuck", "opportunities",
      "verification", "ashwil", "96721", "19046"}
heard = json.load(open(WJ))
toks = []
for i, w in enumerate(heard):
    t = FIX.get(w["text"], w["text"])
    if t == "967-211-9046":
        toks.append({"t": "96721", "s": w["start"], "em": True}); toks.append({"t": "19046", "s": 82.9, "em": True}); continue
    k = re.sub(r"[^\w-]", "", t.lower())
    toks.append({"t": t, "s": round(w["start"], 3), "em": k in EM})
def glen(g): return len(" ".join(w["t"] for w in g))
groups, cur = [], []
for i, w in enumerate(toks):
    cur.append(w); nxt = toks[i + 1] if i + 1 < len(toks) else None
    brk = nxt is None or glen(cur + [nxt]) > 30 or w["t"][-1] in ".?" or (w["t"][-1] == "," and glen(cur) >= 14) or (nxt and nxt["s"] - w["s"] > 1.3)
    if w["t"].endswith("–") or w["t"] == "96721": brk = False
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
def ctext(g): return "".join(w["t"] + ("" if w["t"].endswith("–") or k == len(g) - 1 else " ") for k, w in enumerate(g))
flags = [{"start": a, "end": b, "text": ctext(g), "note": "Place name heard as “Chitroli” (≈46.0 s); spelling not verified — please confirm."} for a, b, g in caps if any("Chitroli" in w["t"] for w in g)]
json.dump({"captions": [{"start": a, "end": b, "text": ctext(g)} for a, b, g in caps], "flags": flags}, open(f"{P}/../captions.json", "w"), indent=1, ensure_ascii=False)

FADE = '<div class="panel-fade"></div><div class="rep">Representative footage</div>'
ROWS = lambda cid, items, top, step=96: "".join(f'<div class="row" id="{cid}-r{k}" style="top:{top + k*step}px"><b>&#10003;</b>{n}</div>' for k, (n, _) in enumerate(items))
ROWJS = lambda cid, items, s: "\n".join(f'      IN("#{cid}-r{k}", {max(0.05, rel(t, s))}, {{ x: -20, y: 0 }}, {{ x: 0 }});' for k, (_, t) in enumerate(items))

# HOOK — independent property lawyer
s = 4.45
scene("i0", s, 6.95, FADE + '<div class="tag amb" style="left:96px;top:760px" id="i0-t">Independent property lawyer</div>', f'      IN("#i0-t", {rel(4.96, s)});', [("docs", 0, 2.5)])

# STEP 01 — approved residential plots
s = 7.60
scene("p1a", s, 10.05, FADE + '<div class="tag amb" style="left:96px;top:760px" id="p1a-t">Learn the market first</div>', f'      IN("#p1a-t", 0.2);', [("plots", 0, 2.45)])
s = 10.05
plots = "".join(f'<rect class="ln p1b-p" x="{20+c*150}" y="{20+r*130}" width="134" height="114" rx="6"/>' for r in range(2) for c in range(6))
items1 = [("Compare actual deals", 10.08), ("Verify ownership", 11.52), ("What makes a location valuable", 13.04)]
scene("p1b", s, 14.75, f"""
      <svg style="position:absolute;left:96px;top:250px;width:888px;height:262px" viewBox="0 0 920 272">{plots}
        <rect id="p1b-hi" class="ln-a" x="320" y="150" width="134" height="114" rx="6" style="fill:rgba(227,162,59,0.18)"/></svg>
      <div class="lbl" style="position:absolute;left:96px;top:200px;color:#E3A23B">Approved residential plots</div>
      {ROWS("p1b", items1, 590)}<div class="note">Illustrative</div>""",
      "      tl.fromTo('.p1b-p', { opacity: 0 }, { opacity: 1, duration: 0.2, stagger: 0.03 }, 0.05);\n      IN('#p1b-hi', 0.5, { y: 0 });\n" + ROWJS("p1b", items1, s))

# STEP 02 — farmhouses
s = 17.10
scene("p2a", s, 19.85, FADE + '<div class="tag amb" style="left:96px;top:760px" id="p2a-t">Check permitted use</div>', f'      IN("#p2a-t", {rel(18.64, s)});', [("home", 0, 2.75)])
s = 19.85
items2 = [("Permitted use", 19.9), ("Legal access", 20.16), ("Water", 21.2), ("Maintenance costs", 21.68)]
scene("p2b", s, 23.35, '<div class="lbl" style="position:absolute;left:96px;top:240px;color:#E3A23B">Farmhouse checklist</div>' + ROWS("p2b", items2, 300, 110),
      ROWJS("p2b", items2, s))

# STEP 03 — agricultural land
s = 28.40
scene("p3a", s, 30.70, FADE + '<div class="tag amb" style="left:96px;top:760px" id="p3a-t">Deeper checks</div>', f'      IN("#p3a-t", {rel(29.44, s)});', [("field", 0, 2.3)])
s = 30.70
items3 = [("Ownership", 30.8), ("Purchase eligibility", 31.52), ("Land use", 33.12), ("Your eventual exit", 34.24)]
scene("p3b", s, 35.75, '<div class="lbl" style="position:absolute;left:96px;top:240px;color:#E3A23B">Agricultural land checklist</div>' + ROWS("p3b", items3, 300, 110),
      ROWJS("p3b", items3, s))

# WHERE TO RESEARCH — schematic corridor map (positions from town lat/long, 350 px per degree)
def xy(lat, lon): return round(100 + (lon - 74.75) * 440), round(70 + (27.80 - lat) * 440)
T = {"Jaipur": xy(26.92, 75.79), "Kishangarh": xy(26.59, 74.86), "Bandikui": xy(27.05, 76.57), "Kotputli": xy(27.70, 76.20), "Bagru": xy(26.81, 75.54)}
J, K, B, KO, BG = T["Jaipur"], T["Kishangarh"], T["Bandikui"], T["Kotputli"], T["Bagru"]
def town(cid, n, big=False, dx=18, dy=-18, anchor="start"):
    x, y = T[n]
    return (f'<g id="{cid}-tw-{n}"><circle cx="{x}" cy="{y}" r="{16 if big else 10}" style="fill:{"#E3A23B" if big else "#F3E7D3"}"/>'
            f'<text x="{x+dx}" y="{y+dy}" text-anchor="{anchor}" style="font-family:Inter,sans-serif;font-weight:{800 if big else 600};font-size:{40 if big else 32}px;fill:#F3E7D3">{n}</text></g>')
NH48 = f"M{J[0]} {J[1]} C {J[0]-90} {J[1]+50}, {K[0]+120} {K[1]-10}, {K[0]} {K[1]}"
BXP = f"M{J[0]+40} {J[1]-10} C {J[0]+140} {J[1]-40}, {B[0]-120} {B[1]+20}, {B[0]} {B[1]}"
NRR = f"M{BG[0]} {BG[1]} C {BG[0]-30} {BG[1]-120}, {J[0]-20} {J[1]-150}, {J[0]+90} {J[1]-60}"
KKX = f"M{K[0]} {K[1]} C {K[0]+60} {K[1]-240}, {KO[0]-260} {KO[1]+120}, {KO[0]} {KO[1]}"
def mapsvg(cid, extra=""):
    return (f'<svg style="position:absolute;left:96px;top:230px;width:888px;height:691px" viewBox="40 20 900 700">'
            f'<path id="{cid}-nh" class="ln-a draw" pathLength="1" style="stroke-width:9" d="{NH48}"/>'
            f'<path id="{cid}-bx" class="ln-a draw" pathLength="1" style="stroke-width:9" d="{BXP}"/>'
            f'<path id="{cid}-rr" class="ln draw" pathLength="1" style="stroke-width:7" d="{NRR}"/>{extra}'
            + town(cid, "Kishangarh", dx=-40, dy=56, anchor="start") + town(cid, "Bandikui", dx=10, dy=-28, anchor="end") + town(cid, "Kotputli", dx=0, dy=-26, anchor="middle")
            + town(cid, "Bagru", dx=-16, dy=-22, anchor="end") + town(cid, "Jaipur", True, dx=26, dy=54) + "</svg>")
s = 36.60
scene("m1", s, 46.70, mapsvg("m1") + """
      <div class="tag amb" id="m1-t1" style="left:96px;top:930px;font-size:34px">NH48 · Jaipur–Kishangarh</div>
      <div class="tag amb" id="m1-t2" style="left:96px;top:930px;font-size:34px">Jaipur–Bandikui Expressway</div>
      <div class="tag" id="m1-t3" style="left:96px;top:930px;font-size:34px">Proposed Northern Ring Road</div>
            <div class="note" style="top:200px">Schematic · not to scale · alignments indicative</div>""",
      f"""      ["Jaipur","Kishangarh","Bandikui","Kotputli","Bagru"].forEach((n, k) => IN("#m1-tw-" + n, 0.1 + k * 0.06, {{ y: 8 }}));
      DRAW("#m1-nh", {rel(36.96, s)}, 1.2); IN("#m1-t1", {rel(38.56, s)});
      tl.to("#m1-t1", {{ opacity: 0, duration: 0.2 }}, {rel(40.2, s)});
      tl.to("#m1-nh", {{ opacity: 0.45, duration: 0.3 }}, {rel(40.4, s)});
      DRAW("#m1-bx", {rel(41.44, s)}, 1.0); IN("#m1-t2", {rel(41.44, s)});
      tl.to("#m1-t2", {{ opacity: 0, duration: 0.2 }}, {rel(43.6, s)});
      tl.to("#m1-bx", {{ opacity: 0.45, duration: 0.3 }}, {rel(43.8, s)});
      DRAW("#m1-rr", {rel(44.0, s)}, 1.1); IN("#m1-t3", {rel(44.4, s)});""")
s = 48.20
scene("m2", s, 53.95, mapsvg("m2", f'<path id="m2-kk" class="ln-a draw" pathLength="1" style="stroke-width:9" d="{KKX}"/><path id="m2-kd" class="ln" style="stroke-width:3;stroke-dasharray:14 14;opacity:0" d="{KKX}"/>') + """
      <div class="tag amb" id="m2-t1" style="left:96px;top:930px;font-size:34px">Kishangarh–Kotputli Expressway · upcoming</div>
      <div class="tag" id="m2-t2" style="left:96px;top:930px;font-size:34px">Verify final alignment &amp; interchanges</div>
      <div class="note" style="top:200px">Schematic · not to scale · alignments indicative</div>""",
      f"""      tl.set(["#m2-nh", "#m2-bx", "#m2-rr"], {{ strokeDashoffset: 0, opacity: 0.4 }}, 0);
      DRAW("#m2-kk", {rel(48.72, s)}, 1.4); IN("#m2-t1", {rel(48.72, s)});
      tl.to("#m2-kk", {{ opacity: 0.35, duration: 0.4 }}, {rel(51.36, s)});
      tl.to("#m2-kd", {{ opacity: 1, duration: 0.4 }}, {rel(51.36, s)}); tl.to("#m2-t1", {{ opacity: 0, duration: 0.2 }}, {rel(51.16, s)}); IN("#m2-t2", {rel(51.36, s)});""")

# MY STRATEGY — land over flats (original comparison graphic)
s = 59.30
scene("st", s, 65.30, """
      <div id="st-l" style="position:absolute;left:96px;top:300px;width:420px;height:420px;border-radius:24px;border:3px solid #E3A23B;background:rgba(60,38,14,0.55)">
        <div class="serif" style="position:absolute;left:36px;top:40px;font-size:104px;color:#E3A23B">Land</div>
        <div id="st-l2" style="position:absolute;left:36px;top:210px;right:30px;font-family:Inter,sans-serif;font-weight:700;font-size:40px;line-height:1.2;color:#F3E7D3">Long-term location growth</div></div>
      <div id="st-f" style="position:absolute;left:564px;top:300px;width:420px;height:420px;border-radius:24px;border:2px solid rgba(243,231,211,0.3);background:rgba(27,20,15,0.6)">
        <div class="serif" style="position:absolute;left:36px;top:40px;font-size:104px;color:rgba(243,231,211,0.6)">Flats</div>
        <div id="st-f2" style="position:absolute;left:36px;top:210px;right:30px;font-family:Inter,sans-serif;font-weight:700;font-size:40px;line-height:1.2;color:rgba(243,231,211,0.6)">Rental income</div></div>
      <div class="lbl" style="position:absolute;left:96px;top:240px;color:#E3A23B">For this strategy</div>
      <div class="serif" id="st-gt" style="position:absolute;left:510px;top:450px;width:60px;text-align:center;font-size:90px;color:#E3A23B">&gt;</div>
      <div class="note">My preference · not advice for every investor</div>""",
      f"""      IN("#st-l", {rel(60.48, s)}, {{ x: -30, y: 0 }}, {{ x: 0 }}); IN("#st-f", {rel(60.96, s)}, {{ x: 30, y: 0 }}, {{ x: 0 }}); IN("#st-gt", {rel(61.2, s)});
      IN("#st-l2", {rel(62.32, s)}); IN("#st-f2", {rel(64.24, s)});""")

# WHY START NOW — research vs buying blindly, then broker / legal verification
s = 67.90
scene("w1", s, 72.95, """
      <div id="w1-a" style="position:absolute;left:96px;right:96px;top:300px;height:200px;border-radius:24px;border:3px solid #E3A23B;background:rgba(60,38,14,0.55)">
        <div style="position:absolute;left:36px;top:30px" class="lbl">Research</div>
        <div id="w1-a2" class="serif" style="position:absolute;left:36px;top:80px;font-size:84px;color:#E3A23B">→ Negotiating power</div></div>
      <div id="w1-b" style="position:absolute;left:96px;right:96px;top:560px;height:200px;border-radius:24px;border:2px solid rgba(243,231,211,0.3);background:rgba(27,20,15,0.6)">
        <div style="position:absolute;left:36px;top:30px" class="lbl">Buying blindly</div>
        <div id="w1-b2" class="serif" style="position:absolute;left:36px;top:80px;font-size:84px;color:#F3E7D3">→ Money stuck</div></div>""",
      f"""      IN("#w1-a", {rel(68.0, s)}); IN("#w1-a2", {rel(68.88, s)}, {{ x: -20, y: 0 }}, {{ x: 0 }});
      IN("#w1-b", {rel(70.24, s)}); IN("#w1-b2", {rel(71.68, s)}, {{ x: -20, y: 0 }}, {{ x: 0 }});""")
s = 73.10
scene("w2", s, 76.05, FADE + '<div class="tag amb" style="left:96px;top:760px" id="w2-t">Broker → finds opportunities</div>', f'      IN("#w2-t", {rel(73.44, s)});', [("buyers", 0, 2.95)])
s = 76.30
scene("w3", s, 79.25, FADE + '<div class="tag amb" style="left:96px;top:760px" id="w3-t">Legal verification → assesses them</div>', f'      IN("#w3-t", {rel(76.48, s)});', [("mag", 0, 2.95)])

# ---------- chrome ----------
SECT = [(6.72, "STEP 01/03", "Approved residential plots"), (16.48, "STEP 02/03", "Farmhouses"), (25.20, "STEP 03/03", "Agricultural land"),
        (35.44, "WHERE TO RESEARCH", "Growth corridors"), (58.32, "MY STRATEGY", "Land over flats"), (65.60, "WHY START NOW", "Compare verified properties"),
        (80.00, "CONTACT", "Ashwil Bhupesh")]
cards = [(f"hd-{k+1}", t, (SECT[k+1][0] if k + 1 < len(SECT) else VIDEO_END), c, h) for k, (t, c, h) in enumerate(SECT)]
CALL = [("co-0", 3.12, 4.45, "Trustworthy local broker"), ("co-2", 23.40, 25.05, "Look past the landscaping"),
        ("co-4", 54.16, 58.15, "Not guaranteed appreciation"), ("co-7", 81.44, VIDEO_END, "Call / WhatsApp 96721 19046")]
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
      <div id="op"><div id="op-a">JAIPUR REAL ESTATE</div><div id="op-b">WHERE TO START</div></div>
      <div id="pg">{"".join(f'<i id="pg-{k+1}"></i>' for k in range(len(SECT)))}</div>
      {hd_html}{co_html}
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#op", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, 0.12);
      tl.fromTo("#op-b", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35 }}, 0.5);
      tl.to("#op", {{ opacity: 0, y: -10, duration: 0.3, ease: "power2.in" }}, 6.4);
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
steps = ["Approved residential plots", "Farmhouses", "Agricultural land"]
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
        <div id="ec-t">Ashwil Bhupesh</div><div id="ec-s">Research first. Then buy.</div>
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
PUNCH = [(0, 1.0), (2.56, 1.04), (6.72, 1.0), (16.48, 1.05), (25.20, 1.0), (35.44, 1.05), (46.70, 1.0), (53.95, 1.05), (58.32, 1.0), (65.60, 1.05), (80.00, 1.0), (81.44, 1.06)]
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
    <div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="25">
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
