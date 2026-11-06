import sys, json, re
P = sys.argv[1]
VIDEO_END = 107.12
END = 110.6

# ---------------- script, pinned to measured speech segments ----------------
SEGS = [
(0.33,2.89,"Zameen khareedne se pehle sirf *location* aur *rate* mat dekhiye."),
(3.55,4.86,"Yeh *10 checks* zaroor kijiye."),
(5.39,5.66,"Pehla—"),(6.01,6.60,"*maalik kaun* hai?"),
(7.46,8.34,"Seller ki *identity*,"),(8.64,9.47,"purani *registries*"),
(9.75,12.16,"aur *ownership ki poori chain* lawyer se *verify* karaiye."),
(12.64,13.15,"Doosra—"),(13.54,14.50,"zameen ke *records*."),
(15.00,17.86,"*Jamabandi*, yaani revenue record, aur *naamantaran*,"),
(18.12,20.83,"yaani records mein naam badalne ki entry, check kijiye."),
(21.14,23.07,"Sirf *online screenshot* par deal mat kijiye."),
(23.89,25.11,"Teesra— *bechne ka haq*."),(25.70,26.36,"*Joint owners*,"),(26.68,27.33,"*legal heirs*"),
(27.61,28.71,"aur *agricultural land*"),(29.02,30.66,"ki *transfer restrictions* check karaiye."),
(31.22,32.90,"Kya seller *akela* poori zameen bech sakta hai?"),
(33.36,33.78,"Chautha—"),(34.04,34.92,"*loan* aur *dispute*."),(35.22,36.14,"Zameen *girvi* toh nahi?"),
(36.63,37.07,"*Court case*,"),(37.34,39.26,"*stay order* ya pehle se *sale agreement* toh nahi?"),
(39.87,40.28,"Paanchva—"),(40.67,41.16,"*land use*."),(41.67,42.14,"Aap ghar,"),
(42.48,44.14,"warehouse ya resort banana chahte hain—"),(44.48,45.60,"kya us use ki *permission* hai?"),
(45.95,48.21,"Zaroori *conversion* aur *approvals* verify kijiye."),
(49.10,49.54,"Chhatha—"),(49.80,50.77,"approval ki *sachchai*."),(51.17,52.07,"‘JDA approved’"),(52.36,53.01,"sunna *kaafi nahi*."),
(53.77,56.77,"Jaipur Development Authority ya sambandhit authority se *patta*"),
(57.05,58.67,"aur *approved layout* verify kijiye."),
(59.27,60.74,"Saatva— *actual measurement*."),(61.28,63.30,"Survey aur *official demarcation* se *boundary*,"),
(63.69,64.78,"*area* aur *khasra number*—"),(65.16,67.40,"yaani land parcel ki pehchaan— *match* karaiye."),
(67.93,69.66,"*Kabza* kiske paas hai, yeh bhi dekhiye."),
(70.17,71.34,"Aathva— *legal raasta*."),(71.98,73.31,"Site tak gaadi pahunch rahi hai,"),
(73.69,75.97,"lekin kya us raaste se aane-jaane ka *legal haq* bhi hai?"),(76.48,78.08,"*Width* aur *records* check kijiye."),
(78.61,79.06,"Nauva—"),(79.42,80.52,"zameen par *restrictions*."),(81.03,81.83,"*Proposed road*,"),(82.18,83.00,"*acquisition*,"),
(83.28,83.83,"*naala*,"),(84.19,84.75,"*flood risk*,"),(85.20,87.40,"*forest restriction* ya *high-tension line* toh nahi?"),
(88.05,88.48,"Dasva—"),(89.18,90.28,"*total cost* aur *agreement*."),(90.75,93.44,"Registry, tax, brokerage, development,"),
(93.86,95.75,"bijli-paani aur *pending dues* jodiye."),(96.69,98.12,"*Token se pehle* verification,"),
(98.43,100.70,"refund aur possession ki shartein *likhit* mein rakhiye."),
(101.42,102.05,"Yaad rakhiye—"),(102.45,103.87,"zameen ka achha sauda wahi hai,"),(104.24,105.35,"jise aap *legally own*,"),
(105.62,107.0,"*use* aur aage *sell* kar sakein."),
]
# word-level times inside each segment, proportional to word length
words = []
for s, e, text in SEGS:
    on = False; toks = text.split(); lens = [len(re.sub(r"[^\w]", "", t)) + 2 for t in toks]; tot = sum(lens); t = s
    for tok, L in zip(toks, lens):
        st = tok.startswith("*"); en = tok.rstrip(",.?—’").endswith("*")
        if st: on = True
        words.append({"t": tok.replace("*", ""), "s": round(t, 3), "em": on, "seg": (s, e)})
        if en: on = False
        t += (e - s) * L / tot
# caption groups: <= 34 chars, break after punctuation, never across a gap > 0.9 s
groups, cur = [], []
def glen(g): return len(" ".join(w["t"] for w in g))
for i, w in enumerate(words):
    nxt = words[i + 1] if i + 1 < len(words) else None
    cur.append(w)
    gap = (nxt["s"] - w["seg"][1]) if nxt and nxt["seg"] != w["seg"] else 0
    brk = (nxt is None or glen(cur + [nxt]) > 34 or gap > 0.9 or
           (w["t"][-1] in ",.?" and glen(cur) >= 14) or (nxt and nxt["seg"] != w["seg"] and w["t"][-1] in ".?"))
    if brk: groups.append(cur); cur = []
# fold one- or two-word tails back into the previous line when it still fits two lines
merged = []
for g in groups:
    if merged and len(g) <= 2 and glen(merged[-1] + g) <= 46 and g[0]["s"] - merged[-1][-1]["s"] < 1.6 and merged[-1][-1]["t"][-1] not in ".?":
        merged[-1] = merged[-1] + g
    else:
        merged.append(g)
groups = merged
caps = []
for gi, g in enumerate(groups):
    start = g[0]["s"] - 0.05
    end_speech = g[-1]["seg"][1]
    nxt = groups[gi + 1][0]["s"] - 0.05 if gi + 1 < len(groups) else VIDEO_END
    end = min(nxt, end_speech + 0.6)
    caps.append((round(max(0.1, start), 2), round(end, 2), g))
json.dump([{"start": a, "end": b, "text": " ".join(w["t"] for w in g)} for a, b, g in caps], open(f"{P}/../captions.json", "w"), indent=1, ensure_ascii=False)

# ---------------- design tokens ----------------
BASE = """
    @font-face { font-family: "Instrument Serif"; src: url("assets/fonts/instrument-serif-latin-400-normal.woff2") format("woff2"); font-style: normal; }
    @font-face { font-family: "Instrument Serif"; src: url("assets/fonts/instrument-serif-latin-400-italic.woff2") format("woff2"); font-style: italic; }
    #root { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
    .host { position: absolute; inset: 0; }
    .lbl { font-family: "JetBrains Mono", monospace; font-size: 30px; letter-spacing: 0.18em; text-transform: uppercase; color: #C9B79C; white-space: nowrap; }
    .ins { position: absolute; inset: 0; background: radial-gradient(110% 70% at 50% 28%, #33261C 0%, #1B140F 62%, #120D0A 100%); }
    .ins-grain { position: absolute; inset: 0; opacity: 0.05; background-image: radial-gradient(rgba(255,240,220,0.9) 1px, transparent 1px); background-size: 6px 6px; }
    .bug { position: absolute; left: 60px; top: 178px; font-family: "JetBrains Mono", monospace; font-size: 28px; letter-spacing: 0.24em; color: rgba(243,231,211,0.55); }
    .note { position: absolute; left: 60px; right: 200px; top: 905px; font-family: "JetBrains Mono", monospace; font-size: 28px; color: rgba(201,183,156,0.75); white-space: nowrap; }
    .stage { position: absolute; left: 60px; right: 60px; top: 250px; height: 640px; }
    .ln { fill: none; stroke: #F3E7D3; stroke-width: 4; stroke-linecap: round; stroke-linejoin: round; }
    .ln-a { fill: none; stroke: #E3A23B; stroke-width: 4; stroke-linecap: round; stroke-linejoin: round; }
    .draw { stroke-dasharray: 1; stroke-dashoffset: 1; }
    .tag { position: absolute; display: inline-flex; align-items: center; gap: 14px; padding: 14px 24px; border-radius: 16px; background: rgba(243,231,211,0.07); border: 1.5px solid rgba(243,231,211,0.22); font-family: "Inter", sans-serif; font-weight: 700; font-size: 40px; color: #F3E7D3; white-space: nowrap; }
    .tag.amb { border-color: #E3A23B; background: rgba(227,162,59,0.14); }
    .tag i { font-style: normal; display: inline-flex; width: 46px; height: 46px; border-radius: 50%; background: #E3A23B; color: #1B140F; align-items: center; justify-content: center; font-size: 30px; font-weight: 900; }
    .serif { font-family: "Instrument Serif", serif; color: #F3E7D3; }
"""

def insert(cid, dur, body, js):
    html = f"""<template>
  <style>{BASE}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920">
    <div id="{cid}-host" class="host clip" data-start="0" data-duration="{dur}">
      <div id="{cid}-bg" class="ins"><div class="ins-grain"></div><div class="bug">ASHWILLPOWER</div>{body}
      </div>
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      const IN = (sel, t, f, to) => tl.fromTo(sel, Object.assign({{ opacity: 0, y: 18 }}, f || {{}}), Object.assign({{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, to || {{}}), t);
      const DRAW = (sel, t, d) => tl.fromTo(sel, {{ strokeDashoffset: 1 }}, {{ strokeDashoffset: 0, duration: d || 0.8, ease: "power2.inOut" }}, t);
      tl.fromTo("#{cid}-bg", {{ opacity: 0, scale: 1.03 }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "power2.out" }}, 0);
{js}
      tl.to("#{cid}-bg", {{ opacity: 0, duration: 0.3, ease: "power2.in" }}, {dur - 0.3});
      window.__timelines["{cid}"] = tl;
    }})();
  </script>
</template>
"""
    open(f"{P}/compositions/{cid}.html", "w").write(html)

INSERTS = []
def add(cid, start, end, body, js):
    INSERTS.append((cid, start, round(end - start, 2)))
    insert(cid, round(end - start, 2), body, js)

def rel(t, s): return round(t - s, 2)
DOC = lambda x, y, w, h, cls="ln": f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>' + "".join(f'<path class="ln" style="stroke-width:3;opacity:.55" d="M{x+24} {y+44+k*30} H{x+w-24-(k%2)*40}"/>' for k in range(int((h-60)/30)))

# 1 ownership chain (8.5-11.9)
s = 8.5
add("i01", s, 12.25, f"""
        <svg class="stage" viewBox="0 0 960 640">
          <g id="i01-d1">{DOC(30,170,230,300)}</g><g id="i01-d2">{DOC(365,170,230,300)}</g><g id="i01-d3">{DOC(700,170,230,300)}</g>
          <path id="i01-c1" class="ln-a draw" pathLength="1" d="M262 320 H362"/><path id="i01-c2" class="ln-a draw" pathLength="1" d="M597 320 H697"/>
        </svg>
        <div class="tag" style="left:70px;top:740px" id="i01-t1">Seller ID</div>
        <div class="tag" style="left:395px;top:740px" id="i01-t2">Registries</div>
        <div class="tag" style="left:735px;top:740px" id="i01-t3">Chain</div>
        <div class="tag amb" style="left:60px;top:820px" id="i01-t4"><i>&#10003;</i>Lawyer se verify</div>""",
f"""      IN("#i01-d1", 0.05); IN("#i01-t1", 0.1);
      IN("#i01-d2", {rel(8.64,s)}); IN("#i01-t2", {rel(8.7,s)}); DRAW("#i01-c1", {rel(8.64,s)}, 0.4);
      IN("#i01-d3", {rel(10.2,s)}); IN("#i01-t3", {rel(10.3,s)}); DRAW("#i01-c2", {rel(10.2,s)}, 0.4);
      IN("#i01-t4", {rel(11.0,s)});""")

# 2 Jamabandi + Naamantaran (15.0-18.0)
s = 15.0
add("i02", s, 18.3, f"""
        <svg class="stage" viewBox="0 0 960 640"><g id="i02-d1">{DOC(40,90,360,440)}</g><g id="i02-d2">{DOC(560,90,360,440)}</g>
          <path id="i02-plus" class="ln-a" style="stroke-width:8" d="M480 280 V340 M450 310 H510"/></svg>
        <div id="i02-h1" class="serif" style="position:absolute;left:100px;top:790px;font-size:64px">Jamabandi</div>
        <div id="i02-s1" class="lbl" style="position:absolute;left:100px;top:860px">Revenue record</div>
        <div id="i02-h2" class="serif" style="position:absolute;left:620px;top:790px;font-size:64px">Naamantaran</div>
        <div id="i02-s2" class="lbl" style="position:absolute;left:620px;top:860px">Naam ki entry</div>""",
f"""      IN("#i02-d1", 0.05); IN("#i02-h1", 0.1); IN("#i02-s1", {rel(15.9,s)});
      IN("#i02-plus", {rel(16.6,s)}, {{ scale: 0.4 }}, {{ scale: 1 }});
      IN("#i02-d2", {rel(16.9,s)}); IN("#i02-h2", {rel(16.95,s)}); IN("#i02-s2", {rel(17.2,s)});""")

# 3 right to sell - ownership diagram (25.7-29.4)
s = 25.7
add("i03", s, 29.2, """
        <svg class="stage" viewBox="0 0 960 640">
          <rect id="i03-plot" class="ln-a" x="380" y="230" width="200" height="170" rx="6" style="fill:rgba(227,162,59,0.12)"/>
          <path id="i03-l1" class="ln draw" pathLength="1" d="M200 140 L380 260"/><path id="i03-l2" class="ln draw" pathLength="1" d="M760 140 L580 260"/><path id="i03-l3" class="ln draw" pathLength="1" d="M480 520 L480 400"/>
          <circle id="i03-n1" class="ln" cx="170" cy="120" r="44"/><circle id="i03-n2" class="ln" cx="790" cy="120" r="44"/><circle id="i03-n3" class="ln" cx="480" cy="560" r="40"/><text x="480" y="330" text-anchor="middle" style="font-family:Instrument Serif,serif;font-style:italic;font-size:46px;fill:#E3A23B">Plot</text>
        </svg>
        <div class="tag" style="left:60px;top:420px" id="i03-t1">Joint owner</div>
        <div class="tag" style="left:700px;top:420px" id="i03-t2">Joint owner</div>
        <div class="tag" style="left:600px;top:775px" id="i03-t3">Legal heirs</div>
        <div class="serif" id="i03-p" style="position:absolute;left:470px;top:555px;font-size:46px;font-style:italic;color:#E3A23B;display:none">Plot</div>
        <div class="tag amb" style="left:60px;top:875px;font-size:34px" id="i03-t4">Agricultural land &middot; transfer restrictions</div>""",
f"""      IN("#i03-plot", 0.05, {{ scale: 0.9 }}, {{ scale: 1 }});
      IN("#i03-n1", 0.05); IN("#i03-n2", 0.15); IN("#i03-t1", 0.1); IN("#i03-t2", 0.2); DRAW("#i03-l1", 0.1, 0.5); DRAW("#i03-l2", 0.2, 0.5);
      IN("#i03-n3", {rel(26.7,s)}); IN("#i03-t3", {rel(26.75,s)}); DRAW("#i03-l3", {rel(26.7,s)}, 0.5);
      IN("#i03-t4", {rel(27.7,s)});""")

# 4 loan & disputes (35.2-38.9)
s = 35.4
add("i04", s, 38.9, f"""
        <svg class="stage" viewBox="0 0 960 640">
          <g id="i04-doc">{DOC(40,60,330,420)}<circle class="ln-a" cx="300" cy="420" r="38"/><path class="ln-a" d="M285 420 h30 M300 405 v30"/></g>
          <g id="i04-court"><path class="ln" d="M560 210 L740 120 L920 210 Z M580 230 H900 M600 250 V420 M680 250 V420 M760 250 V420 M840 250 V420 M570 440 H910 M550 470 H930"/></g>
        </svg>
        <div class="tag amb" style="left:60px;top:760px" id="i04-t0">Girvi / mortgage?</div>
        <div class="tag" style="left:560px;top:760px;font-size:34px" id="i04-t1">Court case?</div>
        <div class="tag" style="left:60px;top:840px;font-size:34px" id="i04-t2">Stay order?</div>
        <div class="tag" style="left:440px;top:840px;font-size:34px" id="i04-t3">Sale agreement?</div>""",
f"""      IN("#i04-doc", 0.05); IN("#i04-t0", 0.2);
      IN("#i04-court", {rel(36.5,s)}); IN("#i04-t1", {rel(36.63,s)});
      IN("#i04-t2", {rel(37.4,s)}); IN("#i04-t3", {rel(38.2,s)});""")

# 5 land use (41.5-45.5)
s = 41.5
add("i05", s, 45.8, """
        <svg class="stage" viewBox="0 0 960 640">
          <path id="i05-field" class="ln draw" pathLength="1" style="opacity:.6" d="M0 520 H960 M0 560 C200 545 400 575 960 550 M0 600 C300 585 600 615 960 595"/>
          <g id="i05-h"><path class="ln" d="M60 470 V330 L170 250 L280 330 V470 Z M140 470 V390 H200 V470"/></g>
          <g id="i05-w"><path class="ln" d="M360 470 V300 L500 240 L640 300 V470 Z M400 470 V370 H600 V470 M400 400 H600 M400 430 H600"/></g>
          <g id="i05-r"><path class="ln" d="M700 470 V360 H900 V470 M690 360 L800 290 L910 360 M730 470 V410 H770 V470 M820 400 H870 V430 H820 Z"/><path class="ln-a" d="M930 470 V330 M930 330 C900 300 880 330 870 340 M930 330 C960 300 975 330 985 340"/></g>
        </svg>
        <div class="tag" style="left:90px;top:760px" id="i05-t1">Ghar</div>
        <div class="tag" style="left:380px;top:760px" id="i05-t2">Warehouse</div>
        <div class="tag" style="left:740px;top:760px" id="i05-t3">Resort</div>
        <div class="tag amb" style="left:60px;top:840px" id="i05-t4">Us use ki permission?</div>""",
f"""      DRAW("#i05-field", 0.0, 0.8);
      IN("#i05-h", {rel(41.67,s)}); IN("#i05-t1", {rel(41.7,s)});
      IN("#i05-w", {rel(42.5,s)}); IN("#i05-t2", {rel(42.55,s)});
      IN("#i05-r", {rel(43.1,s)}); IN("#i05-t3", {rel(43.15,s)});
      IN("#i05-t4", {rel(44.5,s)});""")

# 6 layout + checklist (53.7-57.7) - original illustrative plan, no stamps
plots = "".join(f'<rect class="ln i06-p" x="{40+c*95}" y="{40+r*120 + (40 if r>=2 else 0)}" width="85" height="110" rx="4"/>' for r in range(4) for c in range(5))
s = 53.7
add("i06", s, 57.7, f"""
        <svg class="stage" viewBox="0 0 560 640" style="width:500px;height:571px;left:60px;top:280px">
          {plots}<path id="i06-road" class="ln-a" d="M30 280 H520" style="stroke-width:6"/>
        </svg>
        <div>
          <div class="tag" id="i06-c1" style="font-size:34px;left:590px;top:330px"><i>&#10003;</i>Patta</div>
          <div class="tag" id="i06-c2" style="font-size:34px;left:590px;top:430px"><i>&#10003;</i>Approved layout</div>
          <div class="tag" id="i06-c3" style="font-size:34px;left:590px;top:530px"><i>&#10003;</i>Authority se verify</div>
        </div>
        <div class="note" id="i06-n">Illustrative layout &middot; not an official document</div>""",
f"""      tl.fromTo("#i06-host .i06-p", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25, stagger: 0.03 }}, 0.05);
      IN("#i06-road", 0.5); IN("#i06-n", 0.3);
      IN("#i06-c1", {rel(56.3,s)}); IN("#i06-c2", {rel(57.2,s) - 0.1}); IN("#i06-c3", {rel(54.6,s)});""")

# 7 survey & boundary (61.2-65.0)
s = 61.2
add("i07", s, 65.5, """
        <svg class="stage" viewBox="0 0 960 640">
          <g id="i07-ts"><path class="ln" d="M120 560 L170 380 L220 560 M170 380 V340"/><rect class="ln-a" x="140" y="290" width="60" height="50" rx="6"/><path class="ln" d="M200 315 H240"/></g>
          <path id="i07-plot" class="ln-a draw" pathLength="1" style="fill:rgba(227,162,59,0.10)" d="M420 160 L860 120 L900 470 L460 520 Z"/>
          <g id="i07-pins"><rect class="ln" x="410" y="140" width="20" height="40"/><rect class="ln" x="850" y="100" width="20" height="40"/><rect class="ln" x="890" y="450" width="20" height="40"/><rect class="ln" x="450" y="500" width="20" height="40"/></g>
          <path id="i07-sight" class="ln" style="stroke-dasharray:10 12;opacity:.6" d="M240 315 L420 160"/>
        </svg>
        <div class="tag" style="left:500px;top:300px" id="i07-t1">Boundary</div>
        <div class="tag" style="left:560px;top:420px" id="i07-t2">Area</div>
        <div class="tag amb" style="left:60px;top:840px" id="i07-t3">Khasra no. match karaiye</div>""",
f"""      IN("#i07-ts", 0.05); IN("#i07-sight", 0.4);
      DRAW("#i07-plot", 0.3, 1.2); IN("#i07-pins", {rel(62.8,s)});
      IN("#i07-t1", {rel(62.9,s)}); IN("#i07-t2", {rel(63.7,s)}); IN("#i07-t3", {rel(63.75,s)});""")

# 8 legal access (71.9-75.9)
s = 71.9
add("i08", s, 76.1, """
        <svg class="stage" viewBox="0 0 960 640">
          <path class="ln" style="stroke-width:28;opacity:.35" d="M0 560 H960"/><path class="ln" style="stroke-dasharray:24 18" d="M0 560 H960"/>
          <rect id="i08-plot" class="ln-a" x="620" y="70" width="270" height="200" rx="6" style="fill:rgba(227,162,59,0.12)"/>
          <rect class="ln" style="opacity:.4" x="300" y="70" width="260" height="400" rx="6"/>
          <path id="i08-path" class="ln-a draw" pathLength="1" style="stroke-dasharray:1" d="M180 546 C190 420 300 330 470 300 C560 285 600 260 640 240"/>
          <g id="i08-w"><path class="ln" d="M120 470 L235 470 M120 455 V485 M235 455 V485"/></g>
        </svg>
        <div class="serif" style="position:absolute;left:700px;top:395px;font-size:52px;font-style:italic;color:#E3A23B" id="i08-p">Plot</div>
        <div class="tag" style="left:700px;top:845px" id="i08-t1">Main road</div>
        <div class="tag amb" style="left:60px;top:300px" id="i08-t2">Legal haq ka raasta?</div>
        <div class="tag" style="left:60px;top:845px" id="i08-t3">Width?</div>""",
f"""      IN("#i08-plot", 0.05); IN("#i08-p", 0.1); IN("#i08-t1", 0.2);
      DRAW("#i08-path", 0.4, 1.4);
      IN("#i08-t2", {rel(74.1,s)}); IN("#i08-w", {rel(75.3,s) - 0.4}); IN("#i08-t3", {rel(75.3,s) - 0.35});""")

# 9 restrictions grid (81.0-84.9)
s = 81.15
tiles = [("Proposed road", 81.03, '<path class="ln" d="M40 120 L90 20 M140 120 L110 20 M88 110 V95 M93 70 V55 M98 35 V25"/>'),
         ("Acquisition", 82.18, '<path class="ln" d="M30 110 V40 H150 V110 Z"/><path class="ln-a" d="M30 40 L150 110 M150 40 L30 110"/>'),
         ("Naala", 83.28, '<path class="ln" d="M20 60 C50 40 70 80 100 60 C130 40 150 80 170 60 M20 95 C50 75 70 115 100 95 C130 75 150 115 170 95"/>'),
         ("Flood risk", 84.19, '<path class="ln" d="M90 15 C60 60 45 80 45 95 A45 45 0 0 0 135 95 C135 80 120 60 90 15 Z"/><path class="ln-a" d="M20 125 H160"/>')]
cells = "".join(f'<div class="i09-c" id="i09-c{k}" style="position:absolute;left:{60 + (k%2)*490}px;top:{250 + (k//2)*290}px;width:470px;height:260px;border-radius:24px;border:1.5px solid rgba(243,231,211,0.22);background:rgba(243,231,211,0.05)"><svg viewBox="0 0 180 140" style="position:absolute;left:30px;top:40px;width:180px;height:140px">{svg}</svg><div style="position:absolute;left:230px;top:96px;font-family:Inter,sans-serif;font-weight:800;font-size:42px;color:#F3E7D3">{name}</div></div>' for k, (name, t, svg) in enumerate(tiles))
add("i09", s, 84.9, cells, "\n".join(f'      IN("#i09-c{k}", {max(0.05, rel(t, s))});' for k, (_, t, _) in enumerate(tiles)))

# 10 HT line + forest (85.15-87.55)
s = 85.15
add("i10", s, 87.55, """
        <svg class="stage" viewBox="0 0 960 640">
          <g id="i10-tw"><path class="ln" d="M180 560 L240 120 L300 560 M200 420 H280 M215 300 H265 M140 180 H340 M160 240 H320"/><path class="ln" d="M660 560 L720 120 L780 560 M680 420 H760 M695 300 H745 M620 180 H820 M640 240 H800"/></g>
          <path id="i10-w" class="ln-a draw" pathLength="1" d="M0 200 C120 230 140 230 160 182 C400 260 560 260 640 182 C760 230 860 240 960 210"/>
          <g id="i10-f"><path class="ln" style="opacity:.7" d="M420 560 L460 470 L500 560 Z M480 560 L530 450 L580 560 Z M550 560 L590 480 L630 560 Z"/></g>
        </svg>
        <div class="tag amb" style="left:60px;top:845px;font-size:36px" id="i10-t1">High-tension line</div>
        <div class="tag" style="left:520px;top:845px;font-size:36px" id="i10-t2">Forest restriction</div>""",
f"""      IN("#i10-f", 0.05); IN("#i10-t2", 0.1);
      IN("#i10-tw", {rel(86.2,s)}); DRAW("#i10-w", {rel(86.3,s)}, 0.7); IN("#i10-t1", {rel(86.3,s)});""")

# 11 total cost (91.0-95.0)
s = 91.3
rows = [("Registry", 90.75), ("Tax", 91.5), ("Brokerage", 92.0), ("Development", 92.8), ("Bijli-paani", 93.9), ("Pending dues", 94.6)]
rr = "".join(f'<div class="i11-r" id="i11-r{k}" style="position:absolute;left:60px;right:60px;top:{250 + k*84}px;height:72px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid rgba(243,231,211,0.16);font-family:Inter,sans-serif;font-weight:700;font-size:42px;color:#F3E7D3"><span>+ {n}</span><span style="font-family:JetBrains Mono,monospace;font-weight:400;font-size:32px;color:#C9B79C">&#8377; ______</span></div>' for k, (n, _) in enumerate(rows))
add("i11", s, 95.0, rr + '<div id="i11-tot" style="position:absolute;left:60px;right:60px;top:770px;display:flex;justify-content:space-between;align-items:center;padding:18px 26px;border-radius:18px;background:rgba(227,162,59,0.16);border:2px solid #E3A23B;font-family:Inter,sans-serif;font-weight:900;font-size:48px;color:#F3E7D3"><span>Total cost</span><span style="color:#E3A23B">= rate + sab kharche</span></div>',
    "\n".join(f'      IN("#i11-r{k}", {max(0.05, rel(t, s))}, {{ x: -20, y: 0 }}, {{ x: 0 }});' for k, (_, t) in enumerate(rows)) + f'\n      IN("#i11-tot", {rel(94.85,s) - 0.5});')

# 12 written agreement (98.4-100.8)
s = 98.4
add("i12", s, 100.8, f"""
        <svg class="stage" viewBox="0 0 960 640"><g id="i12-doc">{DOC(220,30,520,560)}</g><path id="i12-sig" class="ln-a draw" pathLength="1" d="M290 540 C330 500 360 560 400 520 C430 490 450 545 490 515 L560 515"/></svg>
        <div>
          <div class="tag" id="i12-c1" style="font-size:36px;left:330px;top:400px;background:rgba(27,20,15,0.92)"><i>&#10003;</i>Verification</div>
          <div class="tag" id="i12-c2" style="font-size:36px;left:330px;top:500px;background:rgba(27,20,15,0.92)"><i>&#10003;</i>Refund terms</div>
          <div class="tag" id="i12-c3" style="font-size:36px;left:330px;top:600px;background:rgba(27,20,15,0.92)"><i>&#10003;</i>Possession date</div>
        </div>""",
f"""      IN("#i12-doc", 0.05); IN("#i12-c1", 0.1); IN("#i12-c2", {rel(98.45,s)+0.15}); IN("#i12-c3", {rel(99.1,s)});
      DRAW("#i12-sig", {rel(99.7,s)}, 0.7);""")

# ---------------- chrome: opening title, counter + heading, conclusion ----------------
CHECKS = [(5.39, "Asli maalik kaun?"), (12.64, "Records verify karein"), (23.89, "Bechne ka haq"), (33.36, "Loan ya dispute?"),
          (39.87, "Use ki permission?"), (49.10, "Patta + approved layout"), (59.27, "Boundary aur kabza"), (70.17, "Legal raasta"),
          (78.61, "Restrictions check karein"), (88.05, "Total cost + written terms")]
cards = []
for k, (t, h) in enumerate(CHECKS):
    end = CHECKS[k + 1][0] if k + 1 < len(CHECKS) else 101.25
    cards.append((f"hd-{k+1}", t, end, f"CHECK {k+1:02d}/10", h))
hd_html = "".join(f'<div id="{i}" class="hd"><div class="hd-c">{c}</div><div class="hd-h">{h}</div></div>' for i, _, _, c, h in cards)
hd_js = "".join(f"""
      tl.fromTo("#{i} .hd-c", {{ opacity: 0, x: -14 }}, {{ opacity: 1, x: 0, duration: 0.35, ease: "power3.out" }}, {t});
      tl.fromTo("#{i} .hd-h", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, {t + 0.06});
      tl.fromTo("#{i}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.01 }}, {t});
      tl.to("#{i}", {{ opacity: 0, duration: 0.2, ease: "power2.in" }}, {end - 0.2});""" for i, t, end, _, _ in cards)
open(f"{P}/compositions/chrome.html", "w").write(f"""<template>
  <style>{BASE}
    .hd {{ position: absolute; left: 60px; top: 965px; padding: 14px 28px 16px 24px; border-radius: 18px; background: rgba(27,20,15,0.86); border-left: 6px solid #E3A23B; opacity: 0; }}
    .hd-c {{ font-family: "JetBrains Mono", monospace; font-size: 30px; letter-spacing: 0.2em; color: #E3A23B; }}
    .hd-h {{ font-family: "Instrument Serif", serif; font-size: 62px; line-height: 1.05; color: #F3E7D3; white-space: nowrap; }}
    #op {{ position: absolute; left: 60px; right: 180px; top: 958px; padding: 12px 28px 14px; border-radius: 22px; background: rgba(27,20,15,0.88); border-left: 6px solid #E3A23B; }}
    #op-a {{ font-family: "Instrument Serif", serif; font-style: italic; font-size: 50px; color: #F3E7D3; line-height: 1.05; }}
    #op-b {{ font-family: "Inter", sans-serif; font-weight: 800; font-size: 56px; color: #E3A23B; letter-spacing: -0.01em; line-height: 1.05; }}
    #op-k {{ font-family: "JetBrains Mono", monospace; font-size: 28px; letter-spacing: 0.24em; color: #C9B79C; margin-bottom: 8px; }}
    #cl {{ position: absolute; left: 60px; top: 965px; padding: 14px 28px 16px 24px; border-radius: 18px; background: rgba(27,20,15,0.86); border-left: 6px solid #E3A23B; }}
  </style>
  <div id="root" data-composition-id="chrome" data-width="1080" data-height="1920">
    <div id="chrome-host" class="host clip" data-start="0" data-duration="{VIDEO_END}">
      <div id="op"><div id="op-a">Zameen khareedne se pehle:</div><div id="op-b">10 zaroori checks</div></div>
      {hd_html}
      <div id="cl" class="hd"><div class="hd-c">YAAD RAKHIYE</div><div class="hd-h">Own &middot; use &middot; sell</div></div>
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#op", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, 0.15);
      tl.fromTo("#op-b", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, 0.45);
      tl.to("#op", {{ opacity: 0, y: -10, duration: 0.3, ease: "power2.in" }}, 5.05);{hd_js}
      tl.fromTo("#cl", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, 101.42);
      tl.to("#cl", {{ opacity: 0, duration: 0.2 }}, {VIDEO_END - 0.25});
      window.__timelines["chrome"] = tl;
    }})();
  </script>
</template>
""")

# ---------------- captions ----------------
spans = []
for gi, (a, b, g) in enumerate(caps):
    spans.append(f'<div id="cp-{gi}" class="cp"><div class="cp-in">' + " ".join(f'<span class="w{" em" if w["em"] else ""}">{w["t"]}</span>' for w in g) + "</div></div>")
data = [[a, b, [w["s"] for w in g]] for a, b, g in caps]
open(f"{P}/compositions/captions.html", "w").write("""<template>
  <style>
    #root { position: absolute; inset: 0; pointer-events: none; }
    .cp { position: absolute; left: 60px; width: 860px; top: 1135px; display: flex; justify-content: center; opacity: 0; }
    .cp-in { max-width: 860px; text-align: center; padding: 12px 24px 14px; border-radius: 18px; background: rgba(27,20,15,0.74);
      font-family: "Inter", sans-serif; font-weight: 700; font-size: 50px; line-height: 1.22; color: #F8F1E6; }
    .w { opacity: 0.55; }
    .w.em { color: #F0AE45; }
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
        ws.forEach((w, k) => tl.fromTo(w, { opacity: 0.55 }, { opacity: 1, duration: 0.08, ease: "none" }, starts[k]));
        tl.to(g, { opacity: 0, duration: 0.1 }, close - 0.1);
        tl.set(g, { opacity: 0, visibility: "hidden" }, close);
      });
      window.__timelines["captions"] = tl;
    })();
  </script>
</template>
""")

# ---------------- closing card ----------------
items = ["Asli maalik", "Jamabandi + naamantaran", "Bechne ka haq", "Loan / dispute", "Land use permission", "Patta + approved layout", "Boundary + kabza", "Legal raasta", "Restrictions", "Total cost + likhit shartein"]
lis = "".join(f'<div class="ec-i" id="ec-i{k}"><b>{k+1:02d}</b>{t}</div>' for k, t in enumerate(items))
ED = round(END - VIDEO_END, 2)
open(f"{P}/compositions/endcard.html", "w").write(f"""<template>
  <style>{BASE}
    #ec-t {{ position: absolute; left: 70px; right: 70px; top: 250px; font-family: "Instrument Serif", serif; font-size: 92px; line-height: 1.02; color: #F3E7D3; }}
    #ec-t em {{ color: #E3A23B; }}
    #ec-l {{ position: absolute; left: 70px; right: 70px; top: 560px; display: grid; grid-template-columns: 1fr 1fr; gap: 18px 26px; }}
    .ec-i {{ font-family: "Inter", sans-serif; font-weight: 600; font-size: 34px; color: #F3E7D3; display: flex; gap: 14px; align-items: baseline; white-space: nowrap; }}
    .ec-i b {{ font-family: "JetBrains Mono", monospace; font-weight: 400; font-size: 28px; color: #E3A23B; }}
    #ec-b {{ position: absolute; left: 0; right: 0; top: 1060px; text-align: center; font-family: "JetBrains Mono", monospace; font-size: 34px; letter-spacing: 0.3em; color: #C9B79C; }}
  </style>
  <div id="root" data-composition-id="endcard" data-width="1080" data-height="1920">
    <div id="endcard-host" class="host clip" data-start="0" data-duration="{ED}">
      <div id="endcard-bg" class="ins"><div class="ins-grain"></div>
        <div id="ec-t">Save this checklist <em>before your next site visit.</em></div>
        <div id="ec-l">{lis}</div>
        <div id="ec-b">ASHWILLPOWER</div>
      </div>
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#endcard-bg", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, ease: "power2.out" }}, 0);
      tl.fromTo("#ec-t", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, 0.2);
      tl.fromTo(".ec-i", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.3, stagger: 0.05, ease: "power3.out" }}, 0.5);
      tl.fromTo("#ec-b", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, 0.9);
      window.__timelines["endcard"] = tl;
    }})();
  </script>
</template>
""")

# ---------------- root ----------------
hosts = "\n".join(f'      <div id="{c}" class="scene" style="z-index: 4" data-composition-id="{c}" data-composition-src="compositions/{c}.html" data-start="{s}" data-duration="{d}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>' for c, s, d in INSERTS)
sfx = []
for k, (t, _) in enumerate(CHECKS):
    sfx.append(f'      <audio id="sfx-chk-{k+1}" class="clip" src="assets/sfx/click-soft.mp3" data-start="{t}" data-duration="0.36" data-track-index="{11 + k % 2}" data-volume="0.35"></audio>')
sfx.append(f'      <audio id="sfx-end" class="clip" src="assets/sfx/chime.mp3" data-start="{VIDEO_END}" data-duration="2.2" data-track-index="13" data-volume="0.18" data-fade-out="0.8"></audio>')
PUNCH = [(0, 1.0), (5.39, 1.05), (12.64, 1.0), (23.89, 1.05), (33.36, 1.0), (39.87, 1.05), (49.10, 1.0), (59.27, 1.05), (70.17, 1.0), (78.61, 1.05), (88.05, 1.0), (101.42, 1.06)]
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
      #cam {{ position: absolute; inset: 0; transform-origin: 50% 38%; }}
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
      <div id="chrome" class="scene" style="z-index: 6" data-composition-id="chrome" data-composition-src="compositions/chrome.html" data-start="0" data-duration="{VIDEO_END}" data-track-index="2" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
      <div id="captions" class="scene" style="z-index: 7" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{VIDEO_END}" data-track-index="3" data-track-kind="captions" data-width="1080" data-height="1920"></div>
      <div id="endcard" class="scene" style="z-index: 9" data-composition-id="endcard" data-composition-src="compositions/endcard.html" data-start="{VIDEO_END}" data-duration="{ED}" data-track-index="4" data-track-kind="graphics" data-width="1080" data-height="1920"></div>
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
json.dump({"inserts": INSERTS, "checks": CHECKS, "punch": PUNCH}, open(f"{P}/../plan.json", "w"), indent=1)
tot = sum(d for _, _, d in INSERTS)
print("inserts", len(INSERTS), "b-roll seconds", round(tot, 1), "share", round(100 * tot / VIDEO_END, 1), "%", "caption groups", len(caps))
for a, b, g in caps: print(f"{a:6.2f}-{b:6.2f} [{len(' '.join(w['t'] for w in g)):2d}] " + " ".join(("*" + w["t"] + "*") if w["em"] else w["t"] for w in g))
