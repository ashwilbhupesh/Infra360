import json, sys, re
OUT = sys.argv[1]; WJ = sys.argv[2]
anchors = json.load(open(WJ))
# Hinglish script by phrase: (start, end, text). Keywords in *asterisks* get the accent colour.
phrases = [
 (0.24, 2.55, "Rajasthan ka *warehousing* sector"),
 (2.62, 5.0, "manufacturing, trade aur distribution ke beech ek *important link* hai."),
 (5.6, 7.87, "Modern warehouse ka role *storage se aage* hai —"),
 (8.1, 10.19, "*inventory management*, *order processing*"),
 (10.3, 11.6, "aur *timely dispatch* tak."),
 (12.0, 13.2, "*Knight Frank India*"),
 (13.3, 15.5, "ki report par published coverage ke mutabik,"),
 (15.9, 18.98, "Jaipur mein *2025* ke warehousing transactions"),
 (19.3, 21.24, "*13.1 lakh sq ft* rahe —"),
 (21.6, 23.16, "*24%* ki annual growth."),
 (23.7, 27.66, "Manufacturing companies ne leasing activity mein *35%* contribution diya."),
 (28.25, 30.22, "Rajasthan ki *5-state connectivity*"),
 (30.4, 32.44, "aur *Logistics Policy 2025*"),
 (32.5, 34.66, "is sector ke development ko support karti hai."),
 (35.0, 37.9, "Lekin developer ke liye opportunity ko successful project"),
 (38.0, 40.52, "mein convert karna *execution* par depend karta hai."),
 (40.95, 42.7, "*Location* ke saath *truck movement*,"),
 (42.8, 44.0, "*floor load capacity* —"),
 (44.1, 46.26, "yaani floor kitna weight sambhal sakta hai —"),
 (46.55, 48.3, "*clear height* aur *fire safety*"),
 (48.35, 51.2, "tenant ki operational requirements se *match* karna zaroori hai."),
 (51.5, 53.24, "Revenue *lease* se aa sakta hai,"),
 (53.4, 55.26, "ya *storage aur handling services* se."),
 (55.85, 59.0, "Successful warehousing project ki shuruaat construction se pehle,"),
 (59.35, 61.48, "*customer ki demand* samajhne se hoti hai."),
 (61.85, 63.4, "Main hoon *Ashwil*,"),
]
# full-screen cutaway windows: captions drop to the lower band there
FS = [(5.3, 11.7), (15.45, 23.25), (27.6, 34.75), (40.45, 48.2), (55.2, 61.6)]
groups = []
for s, e, text in phrases:
    toks = [t for t in text.replace(' —', '').split()]
    # snap the first word to the nearest model anchor at or after the phrase start
    a = [w["start"] for w in anchors if s - 0.15 <= w["start"] <= s + 0.6]
    s0 = a[0] if a else s
    lens = [len(re.sub(r"\W", "", t)) + 2 for t in toks]; tot = sum(lens); t = s0
    words = []
    for tok, L in zip(toks, lens):
        d = (e - s0) * L / tot; words.append((tok, round(t, 2))); t += d
    # 2-4 words per group, breaking after punctuation
    pg, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        if len(cur) >= 4 or w[0][-1] in ",.":
            pg.append(cur); cur = []
    if cur: pg.append(cur)
    merged = []
    for g in pg:
        if merged and (len(g) == 1 or len(merged[-1]) == 1) and len(merged[-1]) + len(g) <= 5:
            merged[-1] = merged[-1] + g
        else:
            merged.append(g)
    if len(merged) > 1 and len(merged[0]) == 1:
        merged[1] = merged[0] + merged[1]; merged = merged[1:]
    groups.extend(merged)
spans, data = [], []
for gi, g in enumerate(groups):
    op = max(0.1, g[0][1] - 0.05)
    nxt = groups[gi + 1][0][1] - 0.05 if gi + 1 < len(groups) else 64.3
    cl = min(nxt, g[-1][1] + 1.1)
    fs = any(a <= g[0][1] < b for a, b in FS)
    ws = []
    for tok, _ in g:
        em = tok.startswith("*") or tok.endswith("*") or tok.rstrip(",.—").endswith("*")
        clean = tok.replace("*", "")
        ws.append(f'<span class="w{" em" if em else ""}">{clean}</span>')
    # keyword spans across words: mark words between an opening and closing asterisk
    spans.append(f'<div id="cp-{gi}" class="cp{" low" if fs else ""}">' + "".join(ws) + "</div>")
    data.append([round(op, 2), round(cl, 2), [t for _, t in g]])
# propagate multi-word *keywords*
html_spans = []
inside = False
for sp in spans:
    parts = re.split(r'(<span class="w[^"]*">[^<]*</span>)', sp)
    out = []
    for p in parts:
        m = re.match(r'<span class="w([^"]*)">([^<]*)</span>', p)
        if not m: out.append(p); continue
        out.append(p)
    html_spans.append("".join(out))
# recompute emphasis from the raw script so multi-word keywords colour every word
flat = []
for s, e, text in phrases:
    on = False
    for tok in text.replace(' —', '').split():
        st = tok.startswith("*"); en = tok.rstrip(",.—").endswith("*")
        if st: on = True
        flat.append(on)
        if en: on = False
k = 0; final = []
for sp in html_spans:
    def rep(m):
        global k
        cls = " em" if flat[k] else ""; k += 1
        return f'<span class="w{cls}">{m.group(2)}</span>'
    final.append(re.sub(r'<span class="w([^"]*)">([^<]*)</span>', rep, sp))
html = """<template>
  <style>
    #root { position: absolute; inset: 0; pointer-events: none; }
    .cp { position: absolute; left: 0; right: 0; bottom: 1050px; display: flex; flex-wrap: wrap; justify-content: center; gap: 0 18px; padding: 0 80px; opacity: 0;
      font-family: "Inter", sans-serif; font-weight: 900; font-size: 62px; line-height: 1.12; letter-spacing: -0.01em; text-align: center; }
    .cp.low { bottom: 640px; }
    .cp .w { color: #fff; -webkit-text-stroke: 8px rgba(8,10,16,0.92); paint-order: stroke fill; text-shadow: 0 6px 22px rgba(0,0,0,0.55); }
    .cp .w.em { color: #F5A524; }
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
    """ + "\n    ".join(final) + """
  </div>
  <script>
    (function () {
      const tl = gsap.timeline({ paused: true });
      const G = """ + json.dumps(data) + """;
      G.forEach(([open, close, starts], i) => {
        const g = document.getElementById("cp-" + i);
        const ws = g.querySelectorAll(".w");
        tl.fromTo(g, { opacity: 0 }, { opacity: 1, duration: 0.06 }, open);
        ws.forEach((w, k) => tl.fromTo(w, { opacity: 0, y: 14, scale: 0.92 }, { opacity: 1, y: 0, scale: 1, duration: 0.16, ease: "back.out(2)" }, starts[k]));
        tl.to(g, { opacity: 0, duration: 0.06 }, close - 0.06);
        tl.set(g, { opacity: 0, visibility: "hidden" }, close);
      });
      window.__timelines["captions"] = tl;
    })();
  </script>
</template>
"""
open(OUT, "w").write(html)
for g, d in zip(groups, data): print(d[0], " ".join(t for t, _ in g))
