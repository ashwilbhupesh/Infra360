import json, sys
V = sys.argv[1]
W = json.load(open(f"{V}/talk_words.json"))
fix = {"CG": None, "payment.": "CGPA,", "Class": "class", "NTSC": "NTSE", "ID": "IIT", "top.": "top", "this": "the", "India.": "India,", "Make": "make", "Jaipur": "Jaipur,", "98,": "98.", "Currently,": "Currently", "sector.": "sector."}
words = []
for w in W:
    t = w["text"]
    if t in fix:
        if fix[t] is None: continue
        t = fix[t]
    words.append({"t": t, "s": w["start"], "e": w["end"]})
# hide where big type restates the line
HIDE = (49.95, 52.75)
words = [w for w in words if not (HIDE[0] <= w["s"] < HIDE[1])]
groups, cur = [], []
for i, w in enumerate(words):
    cur.append(w)
    nxt = words[i+1] if i+1 < len(words) else None
    gap = (nxt["s"] - w["s"]) if nxt else 9
    if (w["t"][-1] in ".,?" and len(cur) >= 2) or len(cur) >= 5 or gap > 0.55 or not nxt:
        groups.append(cur); cur = []
merged = []
for g in groups:
    if merged and (len(g) == 1 or len(merged[-1]) == 1) and len(merged[-1]) + len(g) <= 6 and g[0]["s"] - merged[-1][-1]["s"] < 0.9:
        merged[-1] = merged[-1] + g
    else:
        merged.append(g)
groups = merged
spans = []; data = []
for gi, g in enumerate(groups):
    open_t = max(0.12, g[0]["s"] - 0.06)
    nxt = groups[gi+1][0]["s"] - 0.06 if gi+1 < len(groups) else 61.4
    close = min(nxt, g[-1]["s"] + 0.95)
    if HIDE[0] - 0.1 < close and g[-1]["s"] < HIDE[0]: close = min(close, HIDE[0])
    spans.append(f'<div id="cp-{gi}" class="cp">' + "".join(f'<span class="w">{w["t"]}</span>' for w in g) + '</div>')
    data.append([round(open_t,2), round(close,2), [round(w["s"],2) for w in g]])
html = """<template>
  <style>
    #root { position: absolute; inset: 0; pointer-events: none; }
    .cp { position: absolute; left: 0; right: 0; bottom: 610px; display: flex; flex-wrap: wrap; justify-content: center; gap: 0 14px; padding: 0 110px; opacity: 0;
      font-family: "Inter", sans-serif; font-weight: 600; font-size: 50px; line-height: 1.18; letter-spacing: -0.005em; text-align: center; }
    .cp .w { color: #f2ede4; opacity: 0.38; text-shadow: 0 2px 14px rgba(0,0,0,0.75), 0 0 2px rgba(0,0,0,0.6); }
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
        tl.fromTo(g, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.14, ease: "power3.out" }, open);
        ws.forEach((w, k) => tl.fromTo(w, { opacity: 0.38 }, { opacity: 1, duration: 0.1, ease: "none" }, starts[k]));
        tl.to(g, { opacity: 0, duration: 0.08, ease: "power2.in" }, close - 0.08);
        tl.set(g, { opacity: 0, visibility: "hidden" }, close);
      });
      window.__timelines["captions"] = tl;
    })();
  </script>
</template>
"""
open(f"{V}/proj/compositions/captions.html", "w").write(html)
for g in groups: print(round(g[0]["s"],2), " ".join(w["t"] for w in g))
