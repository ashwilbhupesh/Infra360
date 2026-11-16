import sys, json, re
P, WJ = sys.argv[1], sys.argv[2]
VIDEO_END = 101.7
END = 105.7
exec(open(__file__.replace("build.py", "base_part.py")).read())  # BASE, INSERTS, rel(), scene()

# ---------- captions: Parakeet words (1:1 timing), numbers written as spoken ----------
NUM = {"1.": "One.", "2.": "Two.", "3.": "Three.", "4.": "Four.", "5.": "Five.", "6.": "Six.", "7.": "Seven.", "8.": "Eight.", "9.": "Nine.", "10.": "Ten."}
EM = {"broker", "10", "local", "market", "valuable", "price", "sense", "opportunities", "doors", "time", "negotiate", "red", "flags", "early",
      "legal", "technical", "full", "cost", "budget", "purpose", "goal", "coordinate", "moving", "honest", "second", "opinion",
      "transparent", "fees", "right", "decision", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"}
heard = json.load(open(WJ))
toks = []
for w in heard:
    t = NUM.get(w["text"], w["text"])
    k = re.sub(r"[^\w-]", "", t.lower())
    toks.append({"t": t, "s": round(w["start"], 3), "em": k in EM, "num": w["text"] in NUM})
def glen(g): return len(" ".join(w["t"] for w in g))
groups, cur = [], []
for i, w in enumerate(toks):
    cur.append(w); nxt = toks[i + 1] if i + 1 < len(toks) else None
    brk = nxt is None or glen(cur + [nxt]) > 30 or w["t"][-1] in ".?" or (w["t"][-1] == "," and glen(cur) >= 14) or (nxt and nxt["s"] - w["s"] > 1.3)
    if brk: groups.append(cur); cur = []
merged = []
for g in groups:
    if merged and len(g) == 1 and not g[0]["num"] and glen(merged[-1] + g) <= 36 and merged[-1][-1]["t"][-1] not in ".?": merged[-1] += g
    else: merged.append(g)
groups = merged
caps = []
for gi, g in enumerate(groups):
    nxt = groups[gi + 1][0]["s"] - 0.04 if gi + 1 < len(groups) else VIDEO_END
    last = g[-1]["s"] + max(0.35, 0.06 * len(g[-1]["t"]))
    caps.append((round(max(0.08, g[0]["s"] - 0.06), 2), round(min(nxt, last + 0.55), 2), g))
json.dump({"captions": [{"start": a, "end": b, "text": " ".join(w["t"] for w in g)} for a, b, g in caps]}, open(f"{P}/../captions.json", "w"), indent=1, ensure_ascii=False)

FADE = '<div class="panel-fade"></div><div class="rep">Representative footage</div>'
ROWS = lambda cid, items, top, step=96, mark="&#10003;": "".join(f'<div class="row" id="{cid}-r{k}" style="top:{top + k*step}px"><b>{mark}</b>{n}</div>' for k, (n, _) in enumerate(items))
ROWJS = lambda cid, items, s: "\n".join(f'      IN("#{cid}-r{k}", {max(0.05, rel(t, s))}, {{ x: -20, y: 0 }}, {{ x: 0 }});' for k, (_, t) in enumerate(items))
LBL = lambda t: f'<div class="lbl" style="position:absolute;left:96px;top:240px;color:#E3A23B">{t}</div>'
def foot(cid, a, b, src, tag, t, amb=True, extra="", js=""):
    scene(cid, a, b, FADE + extra + f'<div class="tag{" amb" if amb else ""}" style="left:96px;top:760px" id="{cid}-t">{tag}</div>', f'      IN("#{cid}-t", {max(0.1, rel(t, a))});' + js, [(src, 0, round(b - a, 2))])
def card(cid, x, y, w, h, inner, amb=False):
    return (f'<div id="{cid}" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;border-radius:24px;'
            + ("border:3px solid #E3A23B;background:rgba(60,38,14,0.55)" if amb else "border:2px solid rgba(243,231,211,0.3);background:rgba(27,20,15,0.6)") + f'">{inner}</div>')
def big(cid, x, y, w, h, lbl, txt, amb=False, size=64):
    return card(cid, x, y, w, h, f'<div style="position:absolute;left:30px;top:26px" class="lbl">{lbl}</div><div class="serif" style="position:absolute;left:30px;top:66px;right:24px;font-size:{size}px;line-height:1.05;color:{"#E3A23B" if amb else "#F3E7D3"}">{txt}</div>', amb)

# 01 — local market
foot("r1", 8.20, 11.60, "city", "Neighbourhood → exact street", 8.56, amb=False)
# 02 — price
s = 16.50
scene("r2", s, 21.00, big("r2-a", 96, 270, 888, 200, "Anyone can", "quote a number") +
      '<div id="r2-ar" class="serif" style="position:absolute;left:500px;top:480px;font-size:80px;color:#E3A23B">↓</div>' +
      big("r2-b", 96, 590, 888, 200, "An expert helps you judge", "does it make sense?", True),
      f'      IN("#r2-a", {rel(16.64, s)}); IN("#r2-ar", {rel(18.2, s)}); IN("#r2-b", {rel(18.52, s)});')
# 03 — opportunities: listing app vs broker network (original diagram)
s = 23.90
nodes = [(620, 120), (820, 90), (900, 260), (780, 400), (600, 330), (860, 470)]
net = "".join(f'<path class="ln" style="opacity:.55" d="M720 280 L{x} {y}"/><circle class="ln r3-n" cx="{x}" cy="{y}" r="22" style="fill:#1B140F"/>' for x, y in nodes)
scene("r3", s, 28.48, f"""
      {LBL("Not every property is listed")}
      <svg style="position:absolute;left:96px;top:290px;width:888px;height:500px" viewBox="0 0 960 540">
        <g id="r3-app"><rect class="ln" x="40" y="60" width="300" height="440" rx="34"/><path class="ln" style="stroke-width:3;opacity:.5" d="M80 130 H300 M80 190 H300 M80 250 H260 M80 310 H300"/>
          <text x="190" y="440" text-anchor="middle" style="font-family:Inter,sans-serif;font-weight:700;font-size:34px;fill:#C9B79C">Listing app</text></g>
        <g id="r3-net">{net}<circle cx="720" cy="280" r="46" style="fill:#E3A23B"/>
          <text x="720" y="292" text-anchor="middle" style="font-family:Inter,sans-serif;font-weight:800;font-size:30px;fill:#1B140F">Broker</text></g></svg>
      <div class="tag amb" id="r3-t" style="left:96px;top:760px">A network opens more doors</div>
      <div class="note" style="left:auto;right:96px">Illustrative</div>""",
      f'      IN("#r3-app", {rel(24.36, s)}); IN("#r3-net", {rel(26.36, s)}); IN("#r3-t", {rel(26.2, s)});')
# 04 — time saved
s = 30.40
it4 = [("Irrelevant calls", 30.6), ("Unsuitable properties", 32.2), ("Wasted site visits", 33.56)]
scene("r4", s, 34.95, LBL("Fewer…") + ROWS("r4", it4, 300, 110, "&#8722;"), ROWJS("r4", it4, s))
# 05 — negotiation beyond price
s = 37.50
it5 = [("Payment schedule", 37.66), ("Possession date", 38.70), ("What's included", 39.90), ("Final amount", 42.30)]
scene("r5", s, 43.10, LBL("Negotiate all of it") + ROWS("r5", it5, 300, 110), ROWJS("r5", it5, s))
# 06 — red flags
foot("r6", 46.10, 49.30, "mag", "Flag concerns early", 47.66)
s = 49.30
scene("r6b", s, 52.45, big("r6b-a", 96, 270, 888, 190, "Broker spots a concern", "→ bring in an expert", True, 60) +
      '<div class="tag" id="r6b-l" style="left:96px;top:520px">Legal expert</div><div class="tag" id="r6b-t" style="left:470px;top:520px">Technical expert</div>',
      f'      IN("#r6b-a", 0.05); IN("#r6b-l", {rel(50.46, s)}); IN("#r6b-t", {rel(51.26, s)});')
# 07 — full cost (illustrative stack, no amounts)
s = 55.30
scene("r7", s, 61.95, f"""
      {LBL("Your real budget")}
      <div id="r7-q" style="position:absolute;left:96px;right:96px;top:300px;height:150px;border-radius:18px;background:#E3A23B;color:#1B140F;font-family:Inter,sans-serif;font-weight:800;font-size:44px;display:flex;align-items:center;padding-left:32px">Quoted price</div>
      <div id="r7-c" style="position:absolute;left:96px;right:96px;top:470px;height:110px;border-radius:18px;background:rgba(243,231,211,0.16);border:1.5px solid rgba(243,231,211,0.3);color:#F3E7D3;font-family:Inter,sans-serif;font-weight:700;font-size:40px;display:flex;align-items:center;padding-left:32px">+ Applicable charges</div>
      <div id="r7-e" style="position:absolute;left:96px;right:96px;top:600px;height:110px;border-radius:18px;background:rgba(243,231,211,0.10);border:1.5px solid rgba(243,231,211,0.3);color:#F3E7D3;font-family:Inter,sans-serif;font-weight:700;font-size:40px;display:flex;align-items:center;padding-left:32px">+ Additional expenses</div>
      <div class="note">Illustrative · amounts vary by property</div>""",
      f'      IN("#r7-q", {rel(55.64, s)}); IN("#r7-c", {rel(59.32, s)}); IN("#r7-e", {rel(60.68, s)});')
# 08 — purpose tiles
s = 64.60
tiles = [("home", "Home", 64.76), ("rental", "Rental income", 65.80), ("plots", "Future investment", 67.32)]
tile_html = "".join(f'<div id="r8-k{k}" style="position:absolute;left:{96 + k*302}px;top:330px;width:284px;height:420px;border-radius:20px;overflow:hidden;border:2px solid rgba(243,231,211,0.35)"><video id="r8-tv{k}" class="clip" src="assets/broll/{src}.mp4" data-start="0" data-duration="{rel(70.0, s)}" muted playsinline style="position:absolute;left:-200px;top:0;width:690px;height:420px;object-fit:cover"></video><div style="position:absolute;left:0;right:0;bottom:0;padding:12px 16px;background:linear-gradient(180deg,rgba(18,13,10,0),rgba(18,13,10,.92));font-family:Inter,sans-serif;font-weight:800;font-size:34px;line-height:1.1;color:#F3E7D3">{n}</div></div>' for k, (src, n, t) in enumerate(tiles))
scene("r8", s, 70.00, LBL("Different goals → different choices") + tile_html + '<div class="rep">Representative footage</div>',
      "\n".join(f'      IN("#r8-k{k}", {round(max(0.05, rel(t, s) - 0.1), 2)}, {{ scale: 0.94 }}, {{ scale: 1 }});' for k, (_, _, t) in enumerate(tiles)))
# 09 — coordination hub
s = 75.60
hub = [("Site visits", 75.98, 120, 120), ("Sellers", 77.66, 700, 110), ("Banks", 78.22, 130, 440), ("Lawyers", 78.78, 690, 450)]
spokes = "".join(f'<path id="r9-l{k}" class="ln-a draw" pathLength="1" d="M480 290 L{x + 90} {y + 30}"/>' for k, (_, _, x, y) in enumerate(hub))
scene("r9", s, 81.45, f"""
      {LBL("One point of coordination")}
      <svg style="position:absolute;left:96px;top:290px;width:888px;height:500px" viewBox="0 0 960 540">{spokes}<circle cx="480" cy="290" r="70" style="fill:#E3A23B"/>
        <text x="480" y="302" text-anchor="middle" style="font-family:Inter,sans-serif;font-weight:800;font-size:34px;fill:#1B140F">Broker</text></svg>"""
      + "".join(f'<div class="tag" id="r9-t{k}" style="left:{96 + round(x * 0.925)}px;top:{290 + round(y * 0.925)}px;font-size:34px">{n}</div>' for k, (n, _, x, y) in enumerate(hub))
      + '<div class="note">Illustrative</div>',
      "\n".join(f'      DRAW("#r9-l{k}", {rel(t, s)}, 0.4); IN("#r9-t{k}", {rel(t, s)});' for k, (_, t, _, _) in enumerate(hub)))
# 10 — honest second opinion
foot("r10", 84.70, 87.90, "buyers", "Won't push every property", 85.18)
# How to choose
s = 90.10
itc = [("Local knowledge", 91.10), ("Transparent fees", 92.06), ("Confidence to give honest advice", 93.66)]
scene("ch", s, 95.95, LBL("Choose a broker with") + ROWS("ch", itc, 300, 110), ROWJS("ch", itc, s))

# ---------- chrome ----------
SECT = [(6.00, "REASON 01/10", "Local market knowledge"), (14.08, "REASON 02/10", "Price assessment"), (21.16, "REASON 03/10", "Hidden opportunities"),
        (28.52, "REASON 04/10", "Time saved"), (35.10, "REASON 05/10", "Negotiation beyond price"), (43.26, "REASON 06/10", "Spotting red flags"),
        (52.60, "REASON 07/10", "The full cost"), (62.20, "REASON 08/10", "Your purpose"), (73.34, "REASON 09/10", "Coordinating the process"),
        (81.82, "REASON 10/10", "An honest second opinion"), (90.22, "HOW TO CHOOSE", "The right broker"), (96.14, "THE BOTTOM LINE", "Make the right decision")]
cards = [(f"hd-{k+1}", t, (SECT[k+1][0] if k + 1 < len(SECT) else VIDEO_END), c, h) for k, (t, c, h) in enumerate(SECT)]
CALL = [("co-1", 11.60, 13.95, "Knows what makes it valuable"), ("co-10", 87.90, 90.05, "Says when a deal doesn't suit you"),
        ("co-12", 98.06, 101.6, "Not just finding a property")]
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
    #op-b {{ font-family: "Inter", sans-serif; font-weight: 900; font-size: 52px; color: #E3A23B; line-height: 1.05; }}
    #pg {{ position: absolute; left: 96px; right: 164px; top: 1196px; display: flex; gap: 10px; opacity: 0; }}
    #pg i {{ flex: 1; height: 7px; border-radius: 4px; background: rgba(27,20,15,0.55); box-shadow: 0 0 0 1px rgba(243,231,211,0.25); }}
    .co {{ position: absolute; left: 96px; top: 1118px; padding: 12px 22px; border-radius: 14px; background: rgba(60,38,14,0.92); border: 1.5px solid #E3A23B; font-family: "Inter", sans-serif; font-weight: 700; font-size: 38px; color: #F3E7D3; opacity: 0; white-space: nowrap; }}
  </style>
  <div id="root" data-composition-id="chrome" data-width="1080" data-height="1920">
    <div id="chrome-host" class="host clip" data-start="0" data-duration="{VIDEO_END}">
      <div id="op"><div id="op-a">SKIPPING A BROKER?</div><div id="op-b">10 REASONS TO HAVE ONE</div></div>
      <div id="pg">{"".join(f'<i id="pg-{k+1}"></i>' for k in range(10))}</div>
      {hd_html}{co_html}
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#op", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, 0.12);
      tl.fromTo("#op-b", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35 }}, 0.5);
      tl.to("#op", {{ opacity: 0, y: -10, duration: 0.3, ease: "power2.in" }}, 5.62);
      tl.fromTo("#pg", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, 6.0);
      tl.to("#pg", {{ opacity: 0, duration: 0.3 }}, 89.95);{"".join(f"""
      tl.fromTo("#pg-{k+1}", {{ backgroundColor: "rgba(27,20,15,0.55)" }}, {{ backgroundColor: "#E3A23B", duration: 0.3 }}, {t});""" for k, (t, _, _) in enumerate(SECT[:10]))}{js}
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
steps = ["Local market", "Price assessment", "Hidden opportunities", "Time saved", "Negotiation", "Red flags", "Full cost", "Your purpose", "Coordination", "Honest opinion"]
lis = "".join(f'<div class="ec-i"><b>{k+1:02d}</b>{t}</div>' for k, t in enumerate(steps))
ED = round(END - VIDEO_END, 2)
open(f"{P}/compositions/endcard.html", "w").write(f"""<template>
  <style>{BASE}
    #ec-k {{ position: absolute; left: 96px; top: 330px; }}
    #ec-t {{ position: absolute; left: 96px; right: 96px; top: 400px; font-family: "Instrument Serif", serif; font-size: 112px; line-height: 1.0; color: #F3E7D3; }}
    #ec-s {{ position: absolute; left: 96px; top: 530px; font-family: "Instrument Serif", serif; font-style: italic; font-size: 64px; color: #E3A23B; }}
    #ec-l {{ position: absolute; left: 96px; right: 96px; top: 680px; display: grid; grid-template-columns: 1fr 1fr; gap: 22px 24px; }}
    .ec-i {{ font-family: "Inter", sans-serif; font-weight: 600; font-size: 34px; color: #F3E7D3; display: flex; gap: 18px; align-items: baseline; white-space: nowrap; }}
    .ec-i b {{ font-family: "JetBrains Mono", monospace; font-weight: 400; font-size: 30px; color: #E3A23B; }}
    #ec-c {{ position: absolute; left: 96px; right: 164px; top: 1100px; padding: 26px 32px; border-radius: 22px; background: rgba(60,38,14,0.7); border: 2px solid #E3A23B; }}
    #ec-c .lbl {{ color: #E3A23B; }}
    #ec-n {{ font-family: "Inter", sans-serif; font-weight: 800; font-size: 76px; color: #F3E7D3; letter-spacing: 0.02em; margin-top: 6px; }}
    #ec-b {{ position: absolute; left: 0; right: 0; top: 1440px; text-align: center; font-family: "JetBrains Mono", monospace; font-size: 34px; letter-spacing: 0.3em; color: #C9B79C; }}
  </style>
  <div id="root" data-composition-id="endcard" data-width="1080" data-height="1920">
    <div id="endcard-host" class="host clip" data-start="0" data-duration="{ED}">
      <div id="endcard-bg" class="ins"><div class="grain"></div>
        <div id="ec-k" class="lbl">Jaipur Real Estate</div>
        <div id="ec-t">Ashwil Bhupesh</div><div id="ec-s">Make the right decision.</div>
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
      tl.fromTo(".ec-i", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.3, stagger: 0.04, ease: "power3.out" }}, 0.6);
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
PUNCH = [(0, 1.0), (6.0, 1.03), (14.08, 1.0), (21.16, 1.03), (28.52, 1.0), (35.10, 1.03), (43.26, 1.0), (52.60, 1.03), (62.20, 1.0), (73.34, 1.03), (81.82, 1.0), (90.22, 1.03), (96.14, 1.0), (98.06, 1.04)]
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
