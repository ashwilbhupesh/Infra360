import sys, json, re
P, WJ, MAPJ = sys.argv[1], sys.argv[2], sys.argv[3]
CUT_A, CUT_B, GAP = 26.96, 33.38, 4.5          # removed source range; data card fills the gap
OFF = CUT_B - (CUT_A + GAP)                     # 2.42
SRC_END = 54.63
TALK_END = round(SRC_END - OFF, 2)              # 52.21
END = round(TALK_END + 7.5, 2)
def out(t): return round(t if t < CUT_A else t - OFF, 3)

# ---------- captions from the actual spoken words ----------
W = json.load(open(WJ))
fix = {"Prop": None, "Equity's": "PropEquity's", "2025.": "in 2025.", "fits.": "fits", "Your": "your", "6,000": "6,000", "8,000": "8,000"}
words = []
for w in W:
    if CUT_A <= w["start"] < CUT_B: continue
    t = w["text"]
    if t in fix:
        if fix[t] is None: continue
        t = fix[t]
    if t == "year." and words and words[-1]["t"] == "the": words.pop(); words.pop() if words and words[-1]["t"] == "in" else None; continue
    for part in t.split():
        words.append({"t": part, "s": out(w["start"])})
EM = {"buyers", "same", "property", "careful", "research,", "waits.", "budget", "less.", "hypothetical", "actual", "numbers.", "PropEquity's", "2024", "10,000", "homes", "39%", "6,000", "8,000",
      "starting", "early", "location,", "negotiate", "better,", "budget.", "postponing", "rising", "prices", "beyond", "rushing", "verification", "more.", "Jaipur,", "contact"}
def glen(g): return len(" ".join(w["t"] for w in g))
groups, cur = [], []
for i, w in enumerate(words):
    cur.append(w); nxt = words[i + 1] if i + 1 < len(words) else None
    if nxt is None or glen(cur + [nxt]) > 30 or w["t"][-1] in ".?" or (w["t"][-1] == "," and glen(cur) >= 14) or (nxt and nxt["s"] - w["s"] > 1.2):
        groups.append(cur); cur = []
merged = []
for g in groups:
    if merged and len(g) == 1 and glen(merged[-1] + g) <= 36 and merged[-1][-1]["t"][-1] not in ".?": merged[-1] += g
    else: merged.append(g)
groups = merged
caps = []
for gi, g in enumerate(groups):
    nxt = groups[gi + 1][0]["s"] - 0.04 if gi + 1 < len(groups) else TALK_END
    end = min(nxt, g[-1]["s"] + 0.9)
    if g[-1]["s"] < CUT_A <= end: end = CUT_A
    caps.append((round(max(0.1, g[0]["s"] - 0.06), 2), round(end, 2), g))
json.dump([{"start": a, "end": b, "text": " ".join(w["t"] for w in g)} for a, b, g in caps], open(f"{P}/../captions.json", "w"), indent=1, ensure_ascii=False)

# ---------- shared design ----------
BASE = """
    @font-face { font-family: "Instrument Serif"; src: url("assets/fonts/instrument-serif-latin-400-normal.woff2") format("woff2"); font-style: normal; }
    @font-face { font-family: "Instrument Serif"; src: url("assets/fonts/instrument-serif-latin-400-italic.woff2") format("woff2"); font-style: italic; }
    #root { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
    .host { position: absolute; inset: 0; }
    .ins { position: absolute; inset: 0; background: radial-gradient(110% 70% at 50% 28%, #33261C 0%, #1B140F 62%, #120D0A 100%); }
    .grain { position: absolute; inset: 0; opacity: 0.05; background-image: radial-gradient(rgba(255,240,220,0.9) 1px, transparent 1px); background-size: 6px 6px; }
    .panel { position: absolute; left: 0; top: 0; width: 1080px; height: 1100px; overflow: hidden; }
    .panel video { position: absolute; left: 0; top: 0; width: 1080px; height: 1100px; object-fit: cover; }
    .fade { position: absolute; left: 0; right: 0; top: 840px; height: 262px; background: linear-gradient(180deg, rgba(18,13,10,0), #120D0A); }
    .rep { position: absolute; right: 164px; top: 1050px; font-family: "JetBrains Mono", monospace; font-size: 28px; color: rgba(243,231,211,0.7); }
    .chip { position: absolute; display: inline-flex; align-items: center; gap: 14px; padding: 12px 22px; border-radius: 14px; background: rgba(27,20,15,0.86); border: 1.5px solid rgba(243,231,211,0.25);
      font-family: "Inter", sans-serif; font-weight: 700; font-size: 38px; color: #F3E7D3; white-space: nowrap; }
    .chip.amb { border-color: #E3A23B; background: rgba(60,38,14,0.92); }
    .chip i { font-style: normal; display: inline-flex; width: 44px; height: 44px; border-radius: 50%; background: #E3A23B; color: #1B140F; align-items: center; justify-content: center; font-size: 28px; font-weight: 900; }
    .mono { font-family: "JetBrains Mono", monospace; font-size: 28px; letter-spacing: 0.14em; color: #E3A23B; text-transform: uppercase; white-space: nowrap; }
    .label { position: absolute; left: 96px; top: 190px; padding: 10px 18px; border-radius: 10px; background: rgba(27,20,15,0.86); border: 1.5px solid #E3A23B; font-family: "JetBrains Mono", monospace; font-size: 28px; letter-spacing: 0.16em; color: #F3E7D3; text-transform: uppercase; }
    .serif { font-family: "Instrument Serif", serif; color: #F3E7D3; }
"""
SCENES = []
def scene(cid, start, end, body, js, videos=(), bg=True, z=4):
    dur = round(end - start, 2); SCENES.append((cid, start, dur, z))
    vids = "".join(f'<div class="panel"><video id="{cid}-v{k}" class="clip" src="assets/broll/{src}.mp4" data-start="{vs}" data-duration="{vd}" muted playsinline></video></div>' for k, (src, vs, vd) in enumerate(videos))
    bgh = f'<div id="{cid}-host" class="host clip" data-start="0" data-duration="{dur}"><div id="{cid}-bg" class="{"ins" if bg else "host"}">{"<div class=grain></div>" if bg else ""}</div></div>'
    html = f"""<template>
  <style>{BASE}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920">
    {bgh}
    <div id="{cid}-vids">{vids}</div>
    <div id="{cid}-fg" class="host">{body}</div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      const IN = (sel, t, f, to) => tl.fromTo(sel, Object.assign({{ opacity: 0, y: 16 }}, f || {{}}), Object.assign({{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, to || {{}}), t);
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
def r(t, s): return round(t - s, 2)

paths = json.load(open(MAPJ)); rj = paths["rj"]
JX, JY = 27.16 + (75.79 - 69.48) / 8.79 * 183.76, 173.07 + (30.20 - 26.91) / 7.15 * 167.53

# 1 · STORY — two buyers (illustrative)
s = 3.40
scene("s1", s, 6.45, f"""
    <div class="label">Illustrative scenario</div>
    <div style="position:absolute;left:96px;right:164px;top:300px;height:520px;border-radius:26px;overflow:hidden;border:2px solid rgba(243,231,211,0.25)" id="s1-a">
      <video id="s1-av" class="clip" src="assets/broll/buyers.mp4" data-start="0" data-duration="3.05" muted playsinline style="position:absolute;left:-60px;top:-200px;width:1080px;height:1100px;object-fit:cover"></video>
      <div style="position:absolute;left:0;right:0;bottom:0;height:200px;background:linear-gradient(180deg,rgba(18,13,10,0),rgba(18,13,10,.92))"></div>
      <div class="chip amb" style="left:24px;bottom:24px"><i>A</i>Researches, then buys</div></div>
    <div class="chip" id="s1-b" style="left:96px;top:860px;font-size:40px"><i>B</i>Waits</div>
    <svg style="position:absolute;left:700px;top:840px;width:160px;height:140px" viewBox="20 165 200 185"><path d="{rj}" fill="#E3A23B" opacity="0.9"/><circle cx="{JX:.1f}" cy="{JY:.1f}" r="7" fill="#fff"/></svg>
    <div class="mono" style="position:absolute;left:640px;top:985px;font-size:28px;color:#F3E7D3">JAIPUR</div>""",
      f'      IN("#s1-a", 0.05, {{ scale: 0.97 }}, {{ scale: 1 }}); IN("#s1-b", {r(5.4, s)});')

# 2 · STORY — same budget, buys less (illustrative)
s = 6.45
scene("s2", s, 10.45, """
    <div class="label">Illustrative scenario</div>
    <div class="mono" style="position:absolute;left:96px;top:320px">Same budget</div>
    <div style="position:absolute;left:96px;right:164px;top:370px;height:22px;border-radius:11px;background:#E3A23B" id="s2-bar"></div>
    <svg style="position:absolute;left:96px;top:450px;width:820px;height:520px" viewBox="0 0 820 520">
      <g id="s2-big"><path d="M60 500 V260 L250 120 L440 260 V500 Z" fill="rgba(227,162,59,0.14)" stroke="#F3E7D3" stroke-width="5" stroke-linejoin="round"/><path d="M200 500 V380 H300 V500" fill="none" stroke="#F3E7D3" stroke-width="5"/></g>
      <g id="s2-small"><path d="M560 500 V370 L670 290 L780 370 V500 Z" fill="rgba(227,162,59,0.22)" stroke="#E3A23B" stroke-width="5" stroke-linejoin="round"/><path d="M645 500 V430 H700 V500" fill="none" stroke="#E3A23B" stroke-width="5"/></g>
      <text x="250" y="80" text-anchor="middle" style="font-family:Inter,sans-serif;font-weight:800;font-size:40px;fill:#F3E7D3">Then</text>
      <text id="s2-later" x="670" y="250" text-anchor="middle" style="font-family:Inter,sans-serif;font-weight:800;font-size:40px;fill:#E3A23B">Years later</text>
    </svg>""",
      f"""      tl.fromTo("#s2-bar", {{ scaleX: 0, transformOrigin: "0 50%" }}, {{ scaleX: 1, duration: 0.6, ease: "power3.out" }}, 0.1);
      IN("#s2-big", 0.2); IN("#s2-later", {r(7.0, s)}); IN("#s2-small", {r(9.6, s)}, {{ scale: 0.6, transformOrigin: "670px 500px" }}, {{ scale: 1 }});""")

# 2b · JAIPUR establishing (user-supplied photo)
s = 14.40
scene("jp", s, 17.45, """
    <img src="assets/img/hawa_bg.jpg" style="position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover" alt="">
    <div id="jp-f" style="position:absolute;left:96px;top:330px;width:888px;border-radius:24px;overflow:hidden;box-shadow:0 30px 70px rgba(0,0,0,.55);border:2px solid rgba(243,231,211,.35)">
      <img id="jp-i" src="assets/img/hawa.jpg" style="display:block;width:888px;height:auto" alt="Hawa Mahal, Jaipur"></div>
    <div class="chip amb" id="jp-t" style="left:96px;top:880px;font-size:44px">Jaipur</div>
    <div class="mono" id="jp-s" style="position:absolute;left:96px;top:980px;color:#F3E7D3">Source: PropEquity · calendar year 2024</div>""",
      """      IN("#jp-f", 0.05, { scale: 0.96 }, { scale: 1 }); tl.fromTo("#jp-i", { scale: 1.0 }, { scale: 1.06, duration: 3.05, ease: "none" }, 0);
      IN("#jp-t", 0.5); IN("#jp-s", 0.45);""")

# 3 · DATA — gap card: average home sold (shown without narration)
s = CUT_A
scene("s3", s, CUT_A + GAP, """
    <div class="mono" style="position:absolute;left:96px;top:300px">Average home sold · Jaipur</div>
    <div style="position:absolute;left:96px;top:370px;display:flex;align-items:baseline;gap:26px">
      <div id="s3-a" class="serif" style="font-size:150px;line-height:1">₹59 lakh</div></div>
    <div id="s3-ar" style="position:absolute;left:96px;top:560px;font-family:Inter,sans-serif;font-weight:800;font-size:64px;color:#E3A23B">→ approx.</div>
    <div id="s3-b" class="serif" style="position:absolute;left:96px;top:650px;font-size:170px;line-height:1;color:#E3A23B">₹78 lakh</div>
    <div class="mono" style="position:absolute;left:96px;top:850px;color:#C9B79C">2023 → 2024</div>
    <div id="s3-n" style="position:absolute;left:96px;right:164px;top:930px;font-family:Inter,sans-serif;font-weight:600;font-size:32px;line-height:1.3;color:#C9B79C">Average transaction value reflects the mix of homes sold; not individual property appreciation.</div>""",
      """      IN("#s3-a", 0.15); IN("#s3-ar", 0.6); IN("#s3-b", 0.8, { scale: 0.92 }, { scale: 1 }); IN("#s3-n", 0.5);""")

# 4 · BENEFITS — residential development footage + checklist
s = out(36.0) - 0.30
items = [("Right location", out(36.48)), ("Better negotiation", out(37.36)), ("Property that fits your budget", out(39.04))]
rows = "".join(f'<div class="chip" id="s4-c{k}" style="left:96px;top:{720 + k*100}px"><i>&#10003;</i>{n}</div>' for k, (n, _) in enumerate(items))
scene("s4", s, out(41.1), '<div class="fade"></div><div class="rep">Representative footage</div><div class="mono" style="position:absolute;left:96px;top:660px">Starting early gives you</div>' + rows,
      "\n".join(f'      IN("#s4-c{k}", {max(0.1, r(t, s))}, {{ x: -18, y: 0 }}, {{ x: 0 }});' for k, (_, t) in enumerate(items)), [("dev", 0, round(out(41.1) - (out(36.0) - 0.30), 2))])

# 5 · RISKS — rising prices / rushing without verification
s = out(43.2)
scene("s5", s, out(46.95), '<div class="fade"></div><div class="rep">Representative footage</div><div class="chip amb" id="s5-t" style="left:96px;top:820px;font-size:36px">Rising prices may push it beyond budget</div>',
      f'      IN("#s5-t", {r(out(43.6), s)});', [("build", 0, round(out(46.95) - out(43.2), 2))])
s = out(47.45)
scene("s6", s, out(50.65), '<div class="fade"></div><div class="rep">Representative footage</div><div class="chip amb" id="s6-t" style="left:96px;top:820px;font-size:36px">Rushing without verification costs more</div>',
      f'      IN("#s6-t", {r(out(48.56), s)});', [("mag", 0, round(out(50.65) - out(47.45), 2))])

# ---------- overlays on the speaker (lower half only) ----------
stats = [("s-1", "10,695", "homes sold in 2024", 17.6), ("s-2", "+5%", "home sales", 18.6), ("s-3", "+39%", "total sales value", 23.1), ("s-4", "₹6,019 cr → ₹8,388 cr", "total sales value", 24.5)]
tiles = "".join(f'<div class="st" id="{i}" style="left:{96 + (k%2)*420}px;top:{1110 + (k//2)*170}px"><b>{v}</b><span>{l}</span></div>' for k, (i, v, l, _) in enumerate(stats))
open(f"{P}/compositions/over.html", "w").write(f"""<template>
  <style>{BASE}
    .st {{ position: absolute; width: 400px; height: 150px; padding: 18px 22px; border-radius: 20px; background: rgba(27,20,15,0.88); border: 1.5px solid rgba(227,162,59,0.6); opacity: 0; }}
    .st b {{ display: block; font-family: "Inter", sans-serif; font-weight: 900; font-size: 54px; color: #F5B04A; line-height: 1.05; white-space: nowrap; }}
    .st span {{ font-family: "Inter", sans-serif; font-weight: 600; font-size: 30px; color: #F3E7D3; }}
    #s-4 b {{ font-size: 40px; padding-top: 8px; }}
    #src {{ position: absolute; left: 96px; top: 1050px; padding: 8px 16px; border-radius: 10px; background: rgba(27,20,15,0.86); font-family: "JetBrains Mono", monospace; font-size: 28px; color: #F3E7D3; opacity: 0; white-space: nowrap; }}
    .ov {{ position: absolute; left: 96px; opacity: 0; }}
  </style>
  <div id="root" data-composition-id="over" data-width="1080" data-height="1920">
    <div id="over-host" class="host clip" data-start="0" data-duration="{TALK_END}">
      <div id="hook" class="ov" style="top:1150px"><div class="chip amb" style="position:relative;font-size:40px">Two buyers. Same property. Jaipur.</div></div>
      <div id="hyp" class="ov" style="top:1150px"><div class="chip" style="position:relative">A hypothetical story → <span style="color:#F5B04A">&nbsp;the actual numbers</span></div></div>
      <div id="src">Source: PropEquity, calendar year 2024</div>
      {tiles}
      <div id="cta" class="ov" style="top:1120px;right:164px"><div style="padding:22px 28px;border-radius:22px;background:rgba(60,38,14,0.94);border:2px solid #E3A23B">
        <div class="mono" style="font-size:28px">Planning to buy in Jaipur?</div>
        <div style="font-family:Inter,sans-serif;font-weight:800;font-size:46px;color:#F3E7D3;line-height:1.1;margin-top:6px">Start comparing verified options today.</div></div></div>
      <div id="risk1" class="ov" style="top:1150px"><div class="chip" style="position:relative;font-size:36px"><i>!</i>Postponing without tracking the market</div></div>
      <div id="contact" class="ov" style="top:1150px"><div class="chip amb" style="position:relative;font-size:40px">Ashwil Bhupesh · Jaipur Real Estate</div></div>
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      const SHOW = (sel, a, b) => {{ tl.fromTo(sel, {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, a); tl.to(sel, {{ opacity: 0, duration: 0.25 }}, b - 0.25); }};
      SHOW("#hook", 0.5, 3.35);
      SHOW("#hyp", {out(10.9)}, {out(14.3)});
      SHOW("#src", 17.45, {CUT_A});
{"".join(f'      tl.fromTo("#{i}", {{ opacity: 0, y: 16, scale: 0.96 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "power3.out" }}, {t}); tl.to("#{i}", {{ opacity: 0, duration: 0.25 }}, {CUT_A - 0.25});' + chr(10) for i, _, _, t in stats)}
      SHOW("#cta", {CUT_A + GAP + 0.05}, {round(out(36.0) - 0.30, 2)});
      SHOW("#risk1", {out(41.2)}, {out(43.2)});
      SHOW("#contact", {out(51.6)}, {TALK_END});
      window.__timelines["over"] = tl;
    }})();
  </script>
</template>
""")

# ---------- captions (lower half, below the overlays) ----------
spans = [f'<div id="cp-{gi}" class="cp"><div class="cp-in">' + " ".join(f'<span class="w{" em" if w["t"] in EM else ""}">{w["t"]}</span>' for w in g) + "</div></div>" for gi, (a, b, g) in enumerate(caps)]
data = [[a, b, [w["s"] for w in g]] for a, b, g in caps]
open(f"{P}/compositions/captions.html", "w").write("""<template>
  <style>
    #root { position: absolute; inset: 0; pointer-events: none; }
    .cp { position: absolute; left: 96px; width: 820px; top: 1460px; display: flex; justify-content: center; opacity: 0; }
    .cp-in { max-width: 820px; text-align: center; padding: 12px 24px 14px; border-radius: 18px; background: rgba(20,14,10,0.82);
      font-family: "Inter", sans-serif; font-weight: 700; font-size: 54px; line-height: 1.2; color: #FFF8EE; }
    .w { opacity: 0.6; } .w.em { color: #F5B04A; }
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
    """ + "\n    ".join(spans) + """
  </div>
  <script>
    (function () {
      const tl = gsap.timeline({ paused: true });
      const G = """ + json.dumps(data) + """;
      G.forEach(([open, close, starts], i) => {
        const g = document.getElementById("cp-" + i); const ws = g.querySelectorAll(".w");
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

# ---------- contact card ----------
CD = round(END - TALK_END, 2)
open(f"{P}/compositions/card.html", "w").write(f"""<template>
  <style>{BASE}
    #cd-k {{ position: absolute; left: 96px; top: 1000px; }}
    #cd-n {{ position: absolute; left: 96px; right: 164px; top: 1050px; font-family: "Instrument Serif", serif; font-size: 132px; line-height: 1; color: #F3E7D3; }}
    #cd-r {{ position: absolute; left: 96px; top: 1195px; font-family: "Inter", sans-serif; font-weight: 700; font-size: 46px; color: #E3A23B; letter-spacing: 0.02em; }}
    #cd-l {{ position: absolute; left: 96px; width: 300px; top: 1285px; height: 2px; background: #E3A23B; transform-origin: 0 50%; }}
    #cd-c {{ position: absolute; left: 96px; top: 1320px; font-family: "JetBrains Mono", monospace; font-size: 30px; letter-spacing: 0.16em; color: #C9B79C; }}
    #cd-p {{ position: absolute; left: 96px; top: 1365px; font-family: "Inter", sans-serif; font-weight: 800; font-size: 76px; color: #F3E7D3; letter-spacing: 0.01em; }}
  </style>
  <div id="root" data-composition-id="card" data-width="1080" data-height="1920">
    <div id="card-host" class="host clip" data-start="0" data-duration="{CD}">
      <div class="ins"><img src="assets/img/amer_bg.jpg" style="position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover" alt=""><div class="grain"></div>
        <div id="cd-f" style="position:absolute;left:96px;top:250px;width:888px;border-radius:24px;overflow:hidden;box-shadow:0 30px 70px rgba(0,0,0,.55);border:2px solid rgba(243,231,211,.35)"><img id="cd-i" src="assets/img/amer.jpg" style="display:block;width:888px;height:auto" alt="Amer Fort, Jaipur"></div>
        <div id="cd-k" class="mono">Explore property in Jaipur</div>
        <div id="cd-n">Ashwil Bhupesh</div>
        <div id="cd-r">Jaipur Real Estate</div>
        <div id="cd-l"></div>
        <div id="cd-c">CALL / WHATSAPP</div>
        <div id="cd-p">96721 19046</div>
      </div>
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#card-host .ins", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5 }}, 0);
      tl.fromTo("#cd-f", {{ opacity: 0, scale: 0.97 }}, {{ opacity: 1, scale: 1, duration: 0.6, ease: "power3.out" }}, 0.15);
      tl.fromTo("#cd-i", {{ scale: 1 }}, {{ scale: 1.05, duration: {CD}, ease: "none" }}, 0);
      ["#cd-k", "#cd-n", "#cd-r", "#cd-c", "#cd-p"].forEach((s, i) => tl.fromTo(s, {{ opacity: 0, y: 18 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, 0.3 + i * 0.15));
      tl.fromTo("#cd-l", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.6, ease: "power3.out" }}, 0.7);
      window.__timelines["card"] = tl;
    }})();
  </script>
</template>
""")

# ---------- root ----------
hosts = "\n".join(f'      <div id="{c}" class="scene" style="z-index: {z}" data-composition-id="{c}" data-composition-src="compositions/{c}.html" data-start="{s}" data-duration="{d}" data-track-index="{1 + k % 2}" data-track-kind="graphics" data-width="1080" data-height="1920"></div>' for k, (c, s, d, z) in enumerate(SCENES))
clicks = [17.6, 18.6, 23.1, 24.5, CUT_A + 0.2]
sfx = "\n".join(f'      <audio id="sfx-{k}" class="clip" src="assets/sfx/click-soft.mp3" data-start="{t}" data-duration="0.36" data-track-index="{11 + k % 2}" data-volume="0.3"></audio>' for k, t in enumerate(clicks))
PUNCH = [(0, 1.0), (3.4, 1.0), (10.45, 1.06), (17.45, 1.0), (CUT_A + GAP, 1.05), (out(41.1), 1.0), (out(46.95), 1.05), (out(50.65), 1.0)]
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
      .talk {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      .scene {{ position: absolute; inset: 0; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="30">
      <div id="ground"></div>
      <div id="cam" style="z-index: 1">
        <video id="talk-a" class="talk clip" src="assets/talk.mp4" data-start="0" data-duration="{CUT_A}" data-track-index="0" playsinline data-has-audio="true" data-volume="1"></video>
        <video id="talk-b" class="talk clip" src="assets/talk.mp4" data-start="{CUT_A + GAP}" data-media-start="{CUT_B}" data-duration="{round(SRC_END - CUT_B, 2)}" data-track-index="0" playsinline data-has-audio="true" data-volume="1"></video>
      </div>
{hosts}
      <div id="over" class="scene" style="z-index: 6" data-composition-id="over" data-composition-src="compositions/over.html" data-start="0" data-duration="{TALK_END}" data-track-index="3" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="captions" class="scene" style="z-index: 7" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{TALK_END}" data-track-index="4" data-track-kind="captions" data-width="1080" data-height="1920"></div>
      <div id="card" class="scene" style="z-index: 9" data-composition-id="card" data-composition-src="compositions/card.html" data-start="{TALK_END}" data-duration="{CD}" data-track-index="5" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.6" data-fade-in="1.0" data-fade-out="2.0"></audio>
{sfx}
      <audio id="sfx-end" class="clip" src="assets/sfx/chime.mp3" data-start="{TALK_END + 0.3}" data-duration="2.2" data-track-index="13" data-volume="0.15" data-fade-out="0.8"></audio>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {json.dumps(PUNCH)}.forEach(([t, s]) => tl.set("#cam", {{ scale: s }}, t));
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
""")
json.dump({"scenes": SCENES, "talk_end": TALK_END, "end": END, "cut": [CUT_A, CUT_B], "gap": GAP, "punch": PUNCH}, open(f"{P}/../plan.json", "w"), indent=1)
print("END", END, "| scenes", [(c, s, d) for c, s, d, _ in SCENES])
for a, b, g in caps: print(f"{a:6.2f}-{b:6.2f} " + " ".join(w["t"] for w in g))
