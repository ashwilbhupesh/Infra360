import sys, json, re, difflib
P, WJ = sys.argv[1], sys.argv[2]
VIDEO_END = 106.67
END = 110.2

# ---------- the master script (captions show exactly these words) ----------
SCRIPT = """If you’re buying land, please save these *10 tips* before you pay even a *token amount.*
One—verify the owner. Check the *seller’s identity* and have a property lawyer examine previous sale deeds and the *ownership chain.*
Two—check the land records. Verify the *revenue records* and *mutation entries*—the updates recording changes in ownership. Don’t rely only on *screenshots.*
Three—confirm the right to sell. Check for *co-owners,* *legal heirs* and *transfer restrictions.* Can this seller legally sell the entire property?
Four—check loans and disputes. Is the land *mortgaged?* Is there a *court case,* *stay order* or an existing *agreement to sell?*
Five—verify the permitted use. Whether you’re planning a *home,* *warehouse* or *resort,* check the *land-use permissions* and required *conversion approvals.*
Six—verify approvals directly. *‘JDA approved’* is a claim you should check. Verify the *patta* and approved layout with the Jaipur Development Authority or the relevant local authority.
Seven—measure the actual land. Get the *boundaries* and *area* surveyed, match them with the records, and confirm who physically possesses the property.
Eight—check legal access. A road reaching the plot doesn’t automatically mean you have a *legal right* to use it. Verify access rights and road width.
Nine—check restrictions and site risks. Look for *proposed roads,* *acquisition notices,* *drainage channels,* *flood risks,* *forest restrictions* and **high-voltage* power lines.*
Ten—calculate the full cost and document the deal. Include *stamp duty,* *registration,* *brokerage,* development costs and outstanding dues. Before paying a token, put *verification,* *refund* and possession terms *in writing.*
A good land purchase is one you can *legally own,* *use* and eventually *sell.*"""
REVIEW = {("this", "seller"): "Audio is ambiguous between “this seller” and “the seller” (≈29.1 s); script wording kept — please confirm."}

toks = []
for line in SCRIPT.split("\n"):
    on = False
    for raw in line.replace("—", "— ").split():
        st = raw.startswith("*") or raw.startswith("*‘"); en = "*" in raw[1:]
        if raw.startswith("*"): on = True
        toks.append({"t": raw.replace("*", ""), "em": on})
        if raw.rstrip(",.?”’").endswith("*") or (en and not raw.startswith("*")): on = False
        elif raw.startswith("*") and raw.count("*") == 2: on = False
def key(t):
    t = t.lower().replace("’", "").replace("‘", "").replace("'", "")
    t = re.sub(r"[^\w-]", "", t)
    return {"10": "ten", "one": "one"}.get(t, t)
heard = json.load(open(WJ))
H = []
for w in heard:
    for part in w["text"].replace("-", " - ").split():
        if part == "-": continue
        H.append({"k": key({"5.": "five", "6.": "six", "7.": "seven", "8.": "eight", "9.": "nine", "10.": "ten"}.get(part.lower(), part)), "s": w["start"]})
S_ = []
for i, t in enumerate(toks):
    for part in t["t"].replace("—", "").split("-"):
        S_.append((i, key(part)))
sm = difflib.SequenceMatcher(None, [k for _, k in S_], [h["k"] for h in H], autojunk=False)
tstart = {}
for tag, a0, a1, b0, b1 in sm.get_opcodes():
    if tag in ("equal", "replace") and (a1 - a0) == (b1 - b0):
        for k in range(a1 - a0):
            i = S_[a0 + k][0]
            tstart.setdefault(i, H[b0 + k]["s"])
# words the model missed: "Look" (audible at 79.78 s, verified)
for i, t in enumerate(toks):
    if i not in tstart:
        if t["t"] == "Look": tstart[i] = 79.78
missing = [toks[i]["t"] for i in range(len(toks)) if i not in tstart]
for i in range(len(toks)):
    if i not in tstart:  # interpolate between neighbours
        a = max(j for j in tstart if j < i); b = min(j for j in tstart if j > i)
        tstart[i] = tstart[a] + (tstart[b] - tstart[a]) * (i - a) / (b - a)
for i, t in enumerate(toks): t["s"] = round(tstart[i], 3)
# caption groups: <=32 chars, break at punctuation / dash, never across a pause > 0.55 s
def glen(g): return len(" ".join(w["t"] for w in g))
groups, cur = [], []
for i, w in enumerate(toks):
    cur.append(w); nxt = toks[i + 1] if i + 1 < len(toks) else None
    brk = nxt is None or glen(cur + [nxt]) > 32 or (w["t"][-1] in ".?" ) or (w["t"].endswith("—") and w["t"] not in ("One—","Two—","Three—","Four—","Five—","Six—","Seven—","Eight—","Nine—","Ten—")) or (w["t"][-1] == "," and glen(cur) >= 16) or (nxt and nxt["s"] - w["s"] > 1.3)
    if brk: groups.append(cur); cur = []
merged = []
for g in groups:
    if merged and len(g) == 1 and glen(merged[-1] + g) <= 40 and merged[-1][-1]["t"][-1] not in ".?—": merged[-1] += g
    else: merged.append(g)
groups = merged
caps = []
for gi, g in enumerate(groups):
    nxt = groups[gi + 1][0]["s"] - 0.04 if gi + 1 < len(groups) else VIDEO_END
    last = g[-1]["s"] + max(0.35, 0.06 * len(g[-1]["t"]))
    caps.append((round(max(0.08, g[0]["s"] - 0.06), 2), round(min(nxt, last + 0.55), 2), g))
flags = []
for a, b, g in caps:
    txt = " ".join(w["t"] for w in g)
    if "this seller" in txt: flags.append({"start": a, "end": b, "text": txt, "note": REVIEW[("this", "seller")]})
json.dump({"captions": [{"start": a, "end": b, "text": " ".join(w["t"] for w in g).replace("— ", "—")} for a, b, g in caps], "flags": flags, "unaligned_words": missing},
          open(f"{P}/../captions.json", "w"), indent=1, ensure_ascii=False)

# ---------- design ----------
BASE = """
    @font-face { font-family: "Instrument Serif"; src: url("assets/fonts/instrument-serif-latin-400-normal.woff2") format("woff2"); font-style: normal; }
    @font-face { font-family: "Instrument Serif"; src: url("assets/fonts/instrument-serif-latin-400-italic.woff2") format("woff2"); font-style: italic; }
    #root { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
    .host { position: absolute; inset: 0; }
    .ins { position: absolute; inset: 0; background: radial-gradient(110% 70% at 50% 28%, #33261C 0%, #1B140F 62%, #120D0A 100%); }
    .grain { position: absolute; inset: 0; opacity: 0.05; background-image: radial-gradient(rgba(255,240,220,0.9) 1px, transparent 1px); background-size: 6px 6px; }
    .bug { position: absolute; left: 96px; top: 190px; font-family: "JetBrains Mono", monospace; font-size: 28px; letter-spacing: 0.24em; color: rgba(243,231,211,0.6); z-index: 5; text-shadow: 0 1px 6px rgba(0,0,0,.6); }
    .panel { position: absolute; left: 0; top: 0; width: 1080px; height: 1100px; overflow: hidden; }
    .panel video { position: absolute; left: 0; top: 0; width: 1080px; height: 1100px; object-fit: cover; }
    .panel-fade { position: absolute; left: 0; right: 0; top: 840px; height: 262px; background: linear-gradient(180deg, rgba(18,13,10,0), #120D0A); }
    .rep { position: absolute; right: 96px; top: 960px; font-family: "JetBrains Mono", monospace; font-size: 28px; color: rgba(243,231,211,0.7); }
    .note { position: absolute; left: 96px; top: 960px; font-family: "JetBrains Mono", monospace; font-size: 28px; color: rgba(201,183,156,0.85); white-space: nowrap; }
    .ln { fill: none; stroke: #F3E7D3; stroke-width: 4; stroke-linecap: round; stroke-linejoin: round; }
    .ln-a { fill: none; stroke: #E3A23B; stroke-width: 4; stroke-linecap: round; stroke-linejoin: round; }
    .draw { stroke-dasharray: 1; stroke-dashoffset: 1; }
    .tag { position: absolute; display: inline-flex; align-items: center; gap: 14px; padding: 14px 24px; border-radius: 16px; background: rgba(27,20,15,0.86); border: 1.5px solid rgba(243,231,211,0.25); font-family: "Inter", sans-serif; font-weight: 700; font-size: 40px; color: #F3E7D3; white-space: nowrap; }
    .tag.amb { border-color: #E3A23B; background: rgba(60,38,14,0.9); }
    .tag i { font-style: normal; display: inline-flex; width: 46px; height: 46px; border-radius: 50%; background: #E3A23B; color: #1B140F; align-items: center; justify-content: center; font-size: 30px; font-weight: 900; }
    .serif { font-family: "Instrument Serif", serif; color: #F3E7D3; }
    .lbl { font-family: "JetBrains Mono", monospace; font-size: 30px; letter-spacing: 0.18em; text-transform: uppercase; color: #C9B79C; white-space: nowrap; }
    .row { position: absolute; left: 96px; right: 96px; height: 84px; display: flex; align-items: center; gap: 22px; border-bottom: 1px solid rgba(243,231,211,0.16); font-family: "Inter", sans-serif; font-weight: 700; font-size: 44px; color: #F3E7D3; }
    .row b { display: inline-flex; width: 50px; height: 50px; border-radius: 12px; border: 2px solid #E3A23B; align-items: center; justify-content: center; color: #E3A23B; font-size: 32px; }
"""
INSERTS = []
def rel(t, s): return round(t - s, 2)

def scene(cid, start, end, body, js, videos=()):
    dur = round(end - start, 2); INSERTS.append((cid, start, dur))
    vids = "".join(f'<div class="panel" id="{cid}-pw{k}"><video id="{cid}-v{k}" class="clip" src="assets/broll/{src}.mp4" data-start="{round(vs,2)}" data-duration="{round(vd,2)}" muted playsinline></video></div>' for k, (src, vs, vd) in enumerate(videos))
    html = f"""<template>
  <style>{BASE}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920">
    <div id="{cid}-host" class="host clip" data-start="0" data-duration="{dur}"><div id="{cid}-bg" class="ins"><div class="grain"></div></div></div>
    <div id="{cid}-vids">{vids}</div>
    <div id="{cid}-fg" class="host"><div class="bug">ASHWILLPOWER</div><div class="body" style="position:absolute;inset:0;transform:translateY(90px)">{body}</div></div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      const IN = (sel, t, f, to) => tl.fromTo(sel, Object.assign({{ opacity: 0, y: 16 }}, f || {{}}), Object.assign({{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, to || {{}}), t);
      const DRAW = (sel, t, d) => tl.fromTo(sel, {{ strokeDashoffset: 1 }}, {{ strokeDashoffset: 0, duration: d || 0.8, ease: "power2.inOut" }}, t);
      tl.fromTo(["#{cid}-bg", "#{cid}-vids", "#{cid}-fg"], {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3, ease: "power2.out" }}, 0);
      tl.fromTo("#{cid}-vids", {{ scale: 1.04 }}, {{ scale: 1.0, duration: {dur}, ease: "none" }}, 0);
{js}
      tl.to(["#{cid}-bg", "#{cid}-vids", "#{cid}-fg"], {{ opacity: 0, duration: 0.28, ease: "power2.in" }}, {round(dur - 0.28, 2)});
      window.__timelines["{cid}"] = tl;
    }})();
  </script>
</template>
"""
    open(f"{P}/compositions/{cid}.html", "w").write(html)

FADE = '<div class="panel-fade"></div><div class="rep">Representative footage</div>'
DOC = lambda x, y, w, h: f'<rect class="ln" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>' + "".join(f'<path class="ln" style="stroke-width:3;opacity:.5" d="M{x+24} {y+44+k*30} H{x+w-24-(k%2)*40}"/>' for k in range(int((h-60)/30)))

# CHECK 01 — owner: lawyer reviewing papers, then ownership chain graphic
s = 7.30
scene("c1a", s, 9.95, FADE + '<div class="tag amb" style="left:96px;top:760px" id="c1a-t">Seller identity</div>',
      f'      IN("#c1a-t", {rel(8.05, s)});', [("docs", 0, 2.65)])
s = 9.95
scene("c1b", s, 12.60, f"""
      <svg style="position:absolute;left:96px;top:300px;width:888px;height:388px" viewBox="0 0 960 420">
        <g id="c1b-d1">{DOC(20,40,230,300)}</g><g id="c1b-d2">{DOC(365,40,230,300)}</g><g id="c1b-d3">{DOC(710,40,230,300)}</g>
        <path id="c1b-a1" class="ln-a draw" pathLength="1" d="M252 190 H362"/><path id="c1b-a2" class="ln-a draw" pathLength="1" d="M597 190 H707"/></svg>
      <div class="lbl" style="position:absolute;left:80px;top:250px">Previous sale deeds</div>
      <div class="tag amb" style="left:96px;top:760px" id="c1b-t">Ownership chain</div>
      <div class="note">Illustrative</div>""",
      f"""      IN("#c1b-d1", 0.1); IN("#c1b-d2", {rel(10.8, s)}); DRAW("#c1b-a1", {rel(10.8, s)}, 0.4);
      IN("#c1b-d3", {rel(11.5, s)}); DRAW("#c1b-a2", {rel(11.5, s)}, 0.4); IN("#c1b-t", {rel(11.84, s)});""")

# CHECK 02 — records: document close-up, then revenue record + mutation entry graphic
s = 15.05
scene("c2a", s, 17.20, FADE + '<div class="tag amb" style="left:96px;top:760px" id="c2a-t">Revenue records</div>', f'      IN("#c2a-t", {rel(15.68, s)});', [("mag", 0, 2.15)])
s = 17.20
scene("c2b", s, 20.15, f"""
      <svg style="position:absolute;left:96px;top:300px;width:888px;height:388px" viewBox="0 0 960 420"><g id="c2b-d1">{DOC(20,20,380,380)}</g><g id="c2b-d2">{DOC(560,20,380,380)}</g>
        <path id="c2b-ar" class="ln-a draw" pathLength="1" d="M420 210 H540 M515 190 L540 210 L515 230"/></svg>
      <div class="serif" style="position:absolute;left:100px;top:740px;font-size:56px">Revenue record</div>
      <div class="serif" id="c2b-h2" style="position:absolute;left:640px;top:740px;font-size:56px;color:#E3A23B">Mutation entry</div>
      <div class="lbl" id="c2b-s" style="position:absolute;left:640px;top:810px">Ownership updates</div>
      <div class="note">Illustrative</div>""",
      f"""      IN("#c2b-d1", 0.05); DRAW("#c2b-ar", 0.3, 0.5); IN("#c2b-d2", 0.35); IN("#c2b-h2", 0.4); IN("#c2b-s", {rel(17.92, s)});""")

# CHECK 03 — right to sell: neutral signing, then co-ownership diagram
s = 24.90
scene("c3a", s, 26.55, FADE + '<div class="tag amb" style="left:96px;top:760px" id="c3a-t">Co-owners</div>', f'      IN("#c3a-t", {rel(25.44, s)});', [("sign1", 0, 1.65)])
s = 26.55
scene("c3b", s, 28.75, """
      <svg style="position:absolute;left:96px;top:260px;width:888px;height:481px" viewBox="0 0 960 520">
        <rect class="ln-a" x="380" y="200" width="200" height="150" rx="6" style="fill:rgba(227,162,59,0.12)"/>
        <text x="480" y="288" text-anchor="middle" style="font-family:Instrument Serif,serif;font-style:italic;font-size:44px;fill:#E3A23B">Land</text>
        <path class="ln" d="M180 120 L380 230 M780 120 L580 230"/><path id="c3b-l3" class="ln draw" pathLength="1" d="M480 470 L480 350"/>
        <circle class="ln" cx="150" cy="100" r="42"/><circle class="ln" cx="810" cy="100" r="42"/><circle id="c3b-n3" class="ln" cx="480" cy="480" r="36"/></svg>
      <div class="tag" style="left:96px;top:430px">Co-owner</div><div class="tag" style="left:740px;top:430px">Co-owner</div>
      <div class="tag" id="c3b-t1" style="left:560px;top:700px">Legal heirs</div>
      <div class="tag amb" id="c3b-t2" style="left:96px;top:800px">Transfer restrictions</div>
      <div class="note" style="left:auto;right:96px">Illustrative</div>""",
      f"""      IN("#c3b-t1", {rel(26.62, s)}); IN("#c3b-n3", {rel(26.62, s)}); DRAW("#c3b-l3", {rel(26.62, s)}, 0.4); IN("#c3b-t2", {rel(27.36, s)});""")

# CHECK 04 — loans & disputes: mortgage paperwork, scales of justice, checklist
s = 34.40
scene("c4a", s, 36.05, FADE + '<div class="tag amb" style="left:96px;top:760px" id="c4a-t">Mortgage?</div>', f'      IN("#c4a-t", {rel(35.12, s)});', [("mort", 0, 1.65)])
s = 36.05
items4 = [("Mortgage", 35.12), ("Court case", 36.48), ("Stay order", 37.36), ("Existing agreement to sell", 38.56)]
rows4 = "".join(f'<div class="row" id="c4b-r{k}" style="top:{620 + k*80}px;font-size:40px;left:120px;right:120px"><b>&#10003;</b>{n}</div>' for k, (n, _) in enumerate(items4))
scene("c4b", s, 39.95, FADE + '<div style="position:absolute;left:72px;right:72px;top:600px;height:360px;border-radius:24px;background:rgba(18,13,10,0.84)"></div>' + rows4,
      "\n".join(f'      IN("#c4b-r{k}", {max(0.05, rel(t, s))}, {{ x: -20, y: 0 }}, {{ x: 0 }});' for k, (_, t) in enumerate(items4)), [("statue", 0, 3.9)])

# CHECK 05 — permitted use: agricultural land, then home / warehouse / resort tiles
s = 42.30
tiles = [("home", "Home", 43.36), ("wh", "Warehouse", 43.76), ("resort", "Resort", 44.64)]
tile_html = "".join(f'<div id="c5a-k{k}" style="position:absolute;left:{96 + k*302}px;top:600px;width:284px;height:300px;border-radius:20px;overflow:hidden;border:2px solid rgba(243,231,211,0.35)"><video id="c5a-tv{k}" class="clip" src="assets/broll/{src}.mp4" data-start="{rel(t, s) - 0.1}" data-duration="{rel(45.35, s) - rel(t, s) + 0.1}" muted playsinline style="position:absolute;left:-120px;top:0;width:560px;height:300px;object-fit:cover"></video><div style="position:absolute;left:0;right:0;bottom:0;padding:10px 16px;background:linear-gradient(180deg,rgba(18,13,10,0),rgba(18,13,10,.9));font-family:Inter,sans-serif;font-weight:800;font-size:38px;color:#F3E7D3">{n}</div></div>' for k, (src, n, t) in enumerate(tiles))
scene("c5a", s, 45.35, FADE + '<div class="tag" style="left:96px;top:300px" id="c5a-t0">Agricultural land</div>' + tile_html,
      "\n".join(f'      IN("#c5a-k{k}", {rel(t, s) - 0.1}, {{ scale: 0.94 }}, {{ scale: 1 }});' for k, (_, _, t) in enumerate(tiles)) + '\n      IN("#c5a-t0", 0.15);',
      [("field", 0, 3.05)])

# CHECK 06 — approvals checklist (original, no seals or stamps)
s = 54.00
plots = "".join(f'<rect class="ln c6-p" x="{20+c*88}" y="{20+r*110 + (40 if r>=2 else 0)}" width="78" height="100" rx="4"/>' for r in range(4) for c in range(5))
items6 = [("Patta", 54.56), ("Approved layout", 55.28), ("Authority verification", 56.16)]
rows6 = "".join(f'<div class="tag" id="c6-c{k}" style="left:540px;top:{330 + k*110}px;font-size:36px"><i>&#10003;</i>{n}</div>' for k, (n, _) in enumerate(items6))
scene("c6", s, 58.20, f"""
      <svg style="position:absolute;left:96px;top:300px;width:420px;height:504px" viewBox="0 0 460 540">{plots}<path class="ln-a" d="M10 255 H450" style="stroke-width:6"/></svg>{rows6}
      <div class="note">Illustrative layout · not an official document</div>""",
      "      tl.fromTo('#c6-host ~ #c6-fg .c6-p, .c6-p', { opacity: 0 }, { opacity: 1, duration: 0.2, stagger: 0.02 }, 0.05);\n" +
      "\n".join(f'      IN("#c6-c{k}", {max(0.05, rel(t, s))}, {{ x: -16, y: 0 }}, {{ x: 0 }});' for k, (_, t) in enumerate(items6)))

# CHECK 07 — boundary + area survey (illustrative; no surveyor footage available on Mixkit)
s = 61.85
scene("c7", s, 65.20, """
      <svg style="position:absolute;left:96px;top:260px;width:888px;height:555px" viewBox="0 0 960 600">
        <g id="c7-ts"><path class="ln" d="M100 560 L150 380 L200 560 M150 380 V340"/><rect class="ln-a" x="120" y="290" width="60" height="50" rx="6"/><path class="ln" d="M180 315 H220"/></g>
        <path id="c7-plot" class="ln-a draw" pathLength="1" style="fill:rgba(227,162,59,0.10)" d="M400 140 L860 100 L900 460 L440 510 Z"/>
        <g id="c7-pins"><rect class="ln" x="390" y="120" width="20" height="40"/><rect class="ln" x="850" y="80" width="20" height="40"/><rect class="ln" x="890" y="440" width="20" height="40"/><rect class="ln" x="430" y="490" width="20" height="40"/></g>
        <path class="ln" style="stroke-dasharray:10 12;opacity:.6" d="M220 315 L400 140"/></svg>
      <div class="tag" id="c7-t1" style="left:480px;top:420px">Boundaries</div>
      <div class="tag" id="c7-t2" style="left:540px;top:530px">Area</div>
      <div class="tag amb" id="c7-t3" style="left:96px;top:800px">Match with records</div>
      <div class="note" style="left:auto;right:96px">Illustrative</div>""",
      f"""      IN("#c7-ts", 0.05); DRAW("#c7-plot", 0.15, 1.0); IN("#c7-pins", {rel(62.32, s)});
      IN("#c7-t1", {rel(62.32, s)}); IN("#c7-t2", {rel(62.88, s)}); IN("#c7-t3", {rel(63.92, s)});""")

# CHECK 08 — approach road, then visible road vs legal access diagram
s = 70.30
scene("c8a", s, 72.45, FADE + '<div class="tag" style="left:96px;top:760px" id="c8a-t">A road reaching the plot…</div>', f'      IN("#c8a-t", {rel(70.56, s)});', [("road", 0, 2.15)])
s = 72.45
scene("c8b", s, 74.45, """
      <svg style="position:absolute;left:96px;top:260px;width:888px;height:555px" viewBox="0 0 960 600">
        <path class="ln" style="stroke-width:26;opacity:.3" d="M0 560 H960"/><path class="ln" style="stroke-dasharray:22 16" d="M0 560 H960"/>
        <rect class="ln-a" x="640" y="60" width="260" height="190" rx="6" style="fill:rgba(227,162,59,0.12)"/>
        <rect class="ln" style="opacity:.4" x="300" y="60" width="300" height="400" rx="6"/>
        <path class="ln" style="opacity:.55" d="M170 548 C190 420 300 330 470 300 C560 285 600 250 640 230"/>
        <path id="c8b-legal" class="ln-a draw" pathLength="1" d="M780 548 V250"/></svg>
      <div class="serif" style="position:absolute;left:720px;top:400px;font-size:46px;font-style:italic;color:#E3A23B">Plot</div>
      <div class="tag" style="left:96px;top:300px;font-size:34px">Visible track</div>
      <div class="tag amb" id="c8b-t" style="left:560px;top:880px;font-size:34px">Legal access route</div>
      <div class="note">Illustrative</div>""",
      f'      DRAW("#c8b-legal", {rel(73.1, s)}, 0.7); IN("#c8b-t", {rel(73.12, s)});')

# CHECK 09 — restrictions & risks: footage + text tiles
s = 79.70
scene("c9a", s, 81.75, FADE + '<div class="tag amb" style="left:96px;top:760px" id="c9a-t">Proposed roads</div><div class="tag" style="left:96px;top:300px;font-size:34px" id="c9a-t2">Acquisition notices</div>',
      f'      IN("#c9a-t", {rel(80.24, s)}); IN("#c9a-t2", {rel(81.12, s)});', [("clear", 0, 2.05)])
s = 81.75
scene("c9b", s, 84.40, FADE + '<div class="tag" style="left:96px;top:300px;font-size:34px" id="c9b-t0">Drainage channels</div><div class="tag amb" style="left:96px;top:760px" id="c9b-t">Flood risks</div>',
      f'      IN("#c9b-t0", {rel(82.40, s)}); IN("#c9b-t", {rel(83.52, s)});', [("flood", 0, 2.65)])
s = 84.40
scene("c9c", s, 87.5, FADE + '<div class="tag" style="left:96px;top:300px;font-size:34px" id="c9c-t0">Forest restrictions</div><div class="tag amb" style="left:96px;top:760px" id="c9c-t">High-voltage power lines</div>',
      f'      IN("#c9c-t0", {rel(84.48, s)}); IN("#c9c-t", {rel(85.92, s)});', [("ht", 0, 3.1)])

# CHECK 10 — cost checklist, then written terms over neutral signing
s = 91.20
items10 = [("Stamp duty", 91.76), ("Registration", 92.72), ("Brokerage", 93.84), ("Development costs", 94.72), ("Outstanding dues", 96.0)]
rows10 = "".join(f'<div class="row" id="c10a-r{k}" style="top:{290 + k*96}px"><b>&#10003;</b>{n}</div>' for k, (n, _) in enumerate(items10))
scene("c10a", s, 96.95, rows10 + '<div class="lbl" style="position:absolute;left:96px;top:240px;color:#E3A23B">Full cost</div>',
      "\n".join(f'      IN("#c10a-r{k}", {max(0.05, rel(t, s))}, {{ x: -20, y: 0 }}, {{ x: 0 }});' for k, (_, t) in enumerate(items10)))
s = 98.60
items10b = [("Verification", 98.88), ("Refund", 100.0), ("Possession terms", 100.64)]
rows10b = "".join(f'<div class="tag" id="c10b-c{k}" style="left:96px;top:{300 + k*110}px;font-size:38px"><i>&#10003;</i>{n}</div>' for k, (n, _) in enumerate(items10b))
scene("c10b", s, 102.0, FADE + rows10b + '<div class="tag amb" style="left:96px;top:760px" id="c10b-w">In writing — before any token</div>',
      "\n".join(f'      IN("#c10b-c{k}", {max(0.05, rel(t, s))}, {{ x: -20, y: 0 }}, {{ x: 0 }});' for k, (_, t) in enumerate(items10b)) + f'\n      IN("#c10b-w", {rel(100.75, s)});',
      [("sign2", 0, 3.4)])

# ---------- chrome: hook title, counters + headings, on-avatar callouts ----------
CHECKS = [(5.20, "VERIFY THE OWNER"), (12.88, "CHECK LAND RECORDS"), (22.48, "CONFIRM THE RIGHT TO SELL"), (31.92, "CHECK LOANS & DISPUTES"),
          (40.00, "VERIFY PERMITTED USE"), (48.96, "VERIFY APPROVALS"), (60.00, "MEASURE & VERIFY POSSESSION"), (68.00, "CHECK LEGAL ACCESS"),
          (76.88, "CHECK RESTRICTIONS & RISKS"), (87.60, "CALCULATE COSTS & DOCUMENT TERMS")]
cards = [(f"hd-{k+1}", t, (CHECKS[k+1][0] if k + 1 < 10 else 102.05), f"CHECK {k+1:02d}/10", h) for k, (t, h) in enumerate(CHECKS)]
CALL = [("co-5", 45.40, 48.70, "Land use + Conversion approvals"), ("co-6", 51.55, 53.95, "JDA = Jaipur Development Authority"),
        ("co-7", 65.25, 67.75, "Who physically possesses it?"), ("co-8", 74.45, 76.65, "Access rights + Road width")]
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
    .hd {{ position: absolute; left: 96px; top: 1160px; max-width: 820px; padding: 14px 28px 16px 24px; border-radius: 18px; background: rgba(27,20,15,0.88); border-left: 6px solid #E3A23B; opacity: 0; }}
    .hd-c {{ font-family: "JetBrains Mono", monospace; font-size: 30px; letter-spacing: 0.2em; color: #E3A23B; }}
    .hd-h {{ font-family: "Inter", sans-serif; font-weight: 800; font-size: 52px; letter-spacing: 0.01em; line-height: 1.08; color: #F3E7D3; }}
    #op {{ position: absolute; left: 96px; right: 164px; top: 1160px; padding: 14px 28px 16px; border-radius: 20px; background: rgba(27,20,15,0.9); border-left: 6px solid #E3A23B; }}
    #op-a {{ font-family: "Inter", sans-serif; font-weight: 800; font-size: 54px; color: #F3E7D3; line-height: 1.05; }}
    #op-b {{ font-family: "Inter", sans-serif; font-weight: 900; font-size: 60px; color: #E3A23B; line-height: 1.05; }}
    #pg {{ position: absolute; left: 96px; right: 164px; top: 1118px; display: flex; gap: 10px; opacity: 0; }}
    #pg i {{ flex: 1; height: 6px; border-radius: 3px; background: rgba(243,231,211,0.18); }}
    .co {{ position: absolute; left: 96px; top: 1565px; padding: 12px 22px; border-radius: 14px; background: rgba(60,38,14,0.92); border: 1.5px solid #E3A23B; font-family: "Inter", sans-serif; font-weight: 700; font-size: 38px; color: #F3E7D3; opacity: 0; white-space: nowrap; }}
  </style>
  <div id="root" data-composition-id="chrome" data-width="1080" data-height="1920">
    <div id="chrome-host" class="host clip" data-start="0" data-duration="{VIDEO_END}">
      <div id="op"><div id="op-a">BUYING LAND?</div><div id="op-b">SAVE THESE 10 CHECKS</div></div>
      <div id="pg">{"".join(f'<i id="pg-{k+1}"></i>' for k in range(10))}</div>
      {hd_html}{co_html}<div id="hd-end" class="hd"><div class="hd-c">THE BOTTOM LINE</div><div class="hd-h">Legally own · use · sell</div></div>
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#op", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, 0.12);
      tl.fromTo("#op-b", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35 }}, 0.4);
      tl.to("#op", {{ opacity: 0, y: -10, duration: 0.3, ease: "power2.in" }}, 4.75);
      tl.fromTo("#pg", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, 5.1);
      tl.fromTo("#hd-end", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, 102.24);
      tl.to("#hd-end", {{ opacity: 0, duration: 0.2 }}, {VIDEO_END - 0.22});
      tl.to("#pg", {{ opacity: 0, duration: 0.3 }}, 102.0);{"".join(f"""
      tl.fromTo("#pg-{k+1}", {{ backgroundColor: "rgba(243,231,211,0.18)" }}, {{ backgroundColor: "#E3A23B", duration: 0.3 }}, {t});""" for k, (t, _) in enumerate(CHECKS))}{js}
      window.__timelines["chrome"] = tl;
    }})();
  </script>
</template>
""")

# ---------- captions ----------
spans = [f'<div id="cp-{gi}" class="cp"><div class="cp-in">' + "".join(f'<span class="w{" em" if w["em"] else ""}">{w["t"]}</span>' + ("" if w["t"].endswith("—") or k == len(g) - 1 else " ") for k, w in enumerate(g)) + "</div></div>" for gi, (a, b, g) in enumerate(caps)]
data = [[a, b, [w["s"] for w in g]] for a, b, g in caps]
open(f"{P}/compositions/captions.html", "w").write("""<template>
  <style>
    #root { position: absolute; inset: 0; pointer-events: none; }
    .cp { position: absolute; left: 96px; width: 820px; top: 1375px; display: flex; justify-content: center; opacity: 0; }
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
items = ["Verify the owner", "Check land records", "Confirm right to sell", "Loans & disputes", "Permitted use", "Verify approvals", "Measure & possession", "Legal access", "Restrictions & risks", "Costs & written terms"]
lis = "".join(f'<div class="ec-i"><b>{k+1:02d}</b>{t}</div>' for k, t in enumerate(items))
ED = round(END - VIDEO_END, 2)
open(f"{P}/compositions/endcard.html", "w").write(f"""<template>
  <style>{BASE}
    #ec-t {{ position: absolute; left: 96px; right: 96px; top: 380px; font-family: "Instrument Serif", serif; font-size: 104px; line-height: 1.02; color: #F3E7D3; }}
    #ec-t em {{ color: #E3A23B; }}
    #ec-l {{ position: absolute; left: 96px; right: 96px; top: 790px; display: grid; grid-template-columns: 1fr 1fr; gap: 44px 26px; }}
    .ec-i {{ font-family: "Inter", sans-serif; font-weight: 600; font-size: 36px; color: #F3E7D3; display: flex; gap: 14px; align-items: baseline; white-space: nowrap; }}
    .ec-i b {{ font-family: "JetBrains Mono", monospace; font-weight: 400; font-size: 28px; color: #E3A23B; }}
    #ec-b {{ position: absolute; left: 0; right: 0; top: 1420px; text-align: center; font-family: "JetBrains Mono", monospace; font-size: 34px; letter-spacing: 0.3em; color: #C9B79C; }}
  </style>
  <div id="root" data-composition-id="endcard" data-width="1080" data-height="1920">
    <div id="endcard-host" class="host clip" data-start="0" data-duration="{ED}">
      <div id="endcard-bg" class="ins"><div class="grain"></div>
        <div id="ec-t">Save this checklist <em>before your next site visit.</em></div>
        <div id="ec-l">{lis}</div><div id="ec-b">ASHWILLPOWER</div>
      </div>
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#endcard-bg", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, ease: "power2.out" }}, 0);
      tl.fromTo("#ec-t", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, 0.2);
      tl.fromTo(".ec-i", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.3, stagger: 0.05, ease: "power3.out" }}, 0.45);
      tl.fromTo("#ec-b", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, 0.8);
      window.__timelines["endcard"] = tl;
    }})();
  </script>
</template>
""")

# ---------- root ----------
hosts = "\n".join(f'      <div id="{c}" class="scene" style="z-index: 4" data-composition-id="{c}" data-composition-src="compositions/{c}.html" data-start="{s}" data-duration="{d}" data-track-index="{1 + k % 2}" data-track-kind="graphics" data-width="1080" data-height="1920"></div>' for k, (c, s, d) in enumerate(INSERTS))
sfx = [f'      <audio id="sfx-chk-{k+1}" class="clip" src="assets/sfx/click-soft.mp3" data-start="{t}" data-duration="0.36" data-track-index="{11 + k % 2}" data-volume="0.32"></audio>' for k, (t, _) in enumerate(CHECKS)]
sfx.append(f'      <audio id="sfx-end" class="clip" src="assets/sfx/chime.mp3" data-start="{VIDEO_END}" data-duration="2.2" data-track-index="13" data-volume="0.16" data-fade-out="0.8"></audio>')
PUNCH = [(0, 1.0), (5.20, 1.05), (12.88, 1.0), (22.48, 1.05), (31.92, 1.0), (40.00, 1.05), (48.96, 1.0), (60.00, 1.05), (68.00, 1.0), (76.88, 1.05), (87.60, 1.0), (102.24, 1.06)]
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
      #lower {{ position: absolute; left: 0; right: 0; top: 1040px; bottom: 0; background: linear-gradient(180deg, rgba(18,13,10,0) 0px, rgba(18,13,10,0.92) 60px, #1A130E 120px, #120D0A 100%); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="25">
      <div id="ground"></div>
      <div id="cam" style="z-index: 1">
        <video id="avatar" class="clip" src="assets/avatar.mp4" data-start="0" data-duration="{VIDEO_END}" data-track-index="0" playsinline data-has-audio="true" data-volume="1"></video>
      </div>
      <div id="lower" style="z-index: 2"></div>
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
json.dump({"inserts": INSERTS, "checks": CHECKS, "punch": PUNCH, "callouts": CALL}, open(f"{P}/../plan.json", "w"), indent=1)
tot = sum(d for _, _, d in INSERTS)
print("inserts", len(INSERTS), "seconds", round(tot, 1), f"{100*tot/VIDEO_END:.1f}%", "| caption groups", len(caps), "| unaligned:", missing)
for a, b, g in caps: print(f"{a:6.2f}-{b:6.2f} [{glen(g):2d}] " + " ".join(("*" + w["t"] + "*") if w["em"] else w["t"] for w in g))
