import sys, json, re
P, WJ = sys.argv[1], sys.argv[2]
VIDEO_END = 105.4
END = 109.4
exec(open(__file__.replace("build.py", "base_part.py")).read())  # BASE, INSERTS, rel(), scene()

# ---------- captions: Parakeet words (1:1 timing), numbers written as spoken ----------
NUM = {"1.": "One.", "2.": "Two.", "3.": "Three.", "4.": "Four.", "5.": "Five.", "6.": "Six.", "7.": "Seven.", "8.": "Eight.", "9.": "Nine.", "10.": "Ten."}
EM = {"will", "10", "ownership", "legal", "clarity", "share", "precisely", "address", "beneficiaries", "shares", "percentage", "backup",
      "unlisted", "executor", "formalities", "lawyer", "witnessing", "securely", "review", "surviving", "housing", "security", "documented",
      "fairness", "shared", "disagreements", "independent", "freely", "pressure", "respectful", "disputes", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"}
heard = json.load(open(WJ))
toks = []
for w in heard:
    t = NUM.get(w["text"], w["text"])
    if t == "address." and 18 < w["start"] < 19: t = "address,"
    if t == "plot" and 19 < w["start"] < 20: t = "plot"
    if t == "instructions" and 46 < w["start"] < 47: t = "instructions."
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


# 01 — verify ownership
s = 8.80
scene("t1", s, 14.05, LBL("Before the will") +
      '<div class="tag" id="t1-a" style="left:96px;top:300px">Jointly owned</div><div class="tag" id="t1-b" style="left:460px;top:300px">Inherited property</div>' +
      big("t1-c", 96, 430, 888, 210, "Get legal clarity on", "the share they can leave", True),
      f'      IN("#t1-a", {rel(9.04, s)}); IN("#t1-b", {rel(10.08, s)}); IN("#t1-c", {rel(11.2, s)});')
# 02 — identify every property
foot("t2a", 14.80, 17.30, "keys", "Every property, precisely", 15.04)
s = 17.30
it2 = [("Complete address", 17.92), ("Plot or flat number", 19.36), ("Relevant ownership details", 21.36)]
scene("t2b", s, 22.55, LBL("For each property") + ROWS("t2b", it2, 300, 110), ROWJS("t2b", it2, s))
# 03 — beneficiaries and shares (illustrative split, no real names)
s = 25.80
scene("t3", s, 31.10, f"""
      {LBL("Who receives what")}
      <div class="tag" id="t3-n" style="left:96px;top:290px">Full names</div>
      <div id="t3-p" style="position:absolute;left:96px;right:96px;top:410px;font-family:Inter,sans-serif;font-weight:700;font-size:40px;color:#F3E7D3">
        <div style="display:flex;gap:18px;align-items:center;margin-bottom:22px"><span style="color:#E3A23B">Property A</span><span>→ Beneficiary 1</span></div>
        <div style="display:flex;gap:18px;align-items:center"><span style="color:#E3A23B">Property B</span><span>→ Beneficiary 2</span></div></div>
      <div id="t3-s" style="position:absolute;left:96px;right:96px;top:620px;height:70px;border-radius:14px;overflow:hidden;display:flex;border:1.5px solid rgba(243,231,211,0.3)">
        <div style="width:50%;background:#E3A23B;color:#1B140F;font-family:Inter,sans-serif;font-weight:800;font-size:32px;display:flex;align-items:center;padding-left:20px">50%</div>
        <div style="width:30%;background:rgba(227,162,59,0.55);color:#1B140F;font-family:Inter,sans-serif;font-weight:800;font-size:32px;display:flex;align-items:center;padding-left:20px">30%</div>
        <div style="width:20%;background:rgba(243,231,211,0.18);color:#F3E7D3;font-family:Inter,sans-serif;font-weight:800;font-size:32px;display:flex;align-items:center;padding-left:20px">20%</div></div>
      <div class="lbl" id="t3-sl" style="position:absolute;left:96px;top:710px">…or a clear percentage each</div>
      <div class="note">Illustrative example</div>""",
      f'      IN("#t3-n", {rel(26.16, s)}); IN("#t3-p", {rel(27.92, s)}); IN("#t3-s", {rel(29.36, s)}); IN("#t3-sl", {rel(29.36, s)});')
# 04 — backups and unlisted assets
s = 34.80
scene("t4", s, 40.55, big("t4-a", 96, 270, 888, 200, "If a beneficiary dies first", "→ a named backup") +
      big("t4-b", 96, 520, 888, 200, "Assets not specifically mentioned", "→ who receives them", True),
      f'      IN("#t4-a", {rel(35.38, s)}); IN("#t4-b", {rel(37.94, s)});')
# 05 — executor and backup
s = 41.30
scene("t5a", s, 43.70, '<div class="tag amb" id="t5a-a" style="left:96px;top:380px;font-size:48px">Executor</div><div class="tag" id="t5a-b" style="left:96px;top:520px;font-size:48px">+ Backup executor</div>',
      f'      IN("#t5a-a", {rel(42.02, s)}); IN("#t5a-b", {rel(42.74, s)});')
foot("t5b", 43.70, 47.00, "lawyer", "Willing &amp; capable", 44.5)
# 06 — legal formalities
foot("t6a", 48.40, 50.95, "sign", "Complete the formalities carefully", 48.5)
s = 50.95
it6 = [("Qualified lawyer guides it", 51.32), ("Drafting", 52.60), ("Signing", 53.32), ("Witnessing requirements", 54.04)]
scene("t6b", s, 57.10, LBL("Legal formalities") + ROWS("t6b", it6, 300, 110) + '<div class="note">Requirements depend on the situation · consult a lawyer</div>', ROWJS("t6b", it6, s))
# 07 — store securely, review
foot("t7a", 58.00, 60.40, "paper", "Store the original securely", 58.12)
s = 60.40
scene("t7b", s, 67.00, big("t7b-a", 96, 270, 888, 190, "Tell the executor", "where it is kept") +
      big("t7b-b", 96, 500, 888, 190, "Review after major changes in", "assets or family", True),
      f'      IN("#t7b-a", {rel(60.84, s)}); IN("#t7b-b", {rel(63.08, s)});')
# 08 — surviving parent's needs
s = 70.60
it8 = [("Housing", 71.34), ("Living expenses", 71.90), ("Financial security", 73.18), ("Wishes clearly documented", 75.02)]
scene("t8", s, 76.80, LBL("Protect the surviving parent") + ROWS("t8", it8, 300, 110), ROWJS("t8", it8, s))
# 09 — fairness and shared ownership
s = 79.90
props = [("Value", 81.02), ("Loans", 81.90), ("Rental potential", 82.54)]
tiles = "".join(f'<div id="t9a-k{k}" style="position:absolute;left:{96 + k*302}px;top:330px;width:284px;height:300px;border-radius:20px;border:2px solid rgba(243,231,211,0.35);background:rgba(27,20,15,0.6)"><svg viewBox="0 0 100 80" style="position:absolute;left:62px;top:40px;width:160px;height:128px"><path class="ln" d="M10 40 L50 10 L90 40 V75 H10 Z"/></svg><div style="position:absolute;left:0;right:0;top:200px;text-align:center;font-family:Inter,sans-serif;font-weight:800;font-size:34px;color:#E3A23B">{n}</div></div>' for k, (n, _) in enumerate(props))
scene("t9a", s, 83.60, LBL("Properties differ in") + tiles + '<div class="note">Illustrative</div>',
      "\n".join(f'      IN("#t9a-k{k}", {rel(t, s) - 0.05}, {{ scale: 0.94 }}, {{ scale: 1 }});' for k, (_, t) in enumerate(props)))
s = 83.60
sib = "".join(f'<circle class="ln" cx="{240 + k*240}" cy="420" r="44"/><path id="t9b-l{k}" class="ln-a draw" pathLength="1" d="M480 200 L{240 + k*240} 376"/>' for k in range(3))
scene("t9b", s, 88.60, f"""
      {LBL("One property · several siblings")}
      <svg style="position:absolute;left:96px;top:280px;width:888px;height:500px" viewBox="0 0 960 540">
        <path class="ln-a" d="M400 200 L480 120 L560 200 V260 H400 Z" style="fill:rgba(227,162,59,0.15)"/>{sib}</svg>
      <div class="tag amb" id="t9b-t" style="left:96px;top:760px">Disagreements over use or sale</div>
      <div class="note" style="left:auto;right:96px">Illustrative</div>""",
      "\n".join(f'      DRAW("#t9b-l{k}", {rel(84.82, s) + k*0.15}, 0.4);' for k in range(3)) + f'\n      IN("#t9b-t", {rel(86.02, s)});')

# ---------- chrome ----------
SECT = [(6.16, "TIP 01/10", "Verify ownership first"), (14.24, "TIP 02/10", "Identify every property"), (22.64, "TIP 03/10", "Beneficiaries & shares"),
        (31.12, "TIP 04/10", "Backups & unlisted assets"), (40.66, "TIP 05/10", "Executor + a backup"), (47.78, "TIP 06/10", "Legal formalities"),
        (57.40, "TIP 07/10", "Store safely & review"), (67.90, "TIP 08/10", "The surviving parent"), (76.94, "TIP 09/10", "Fairness & shared ownership"),
        (88.74, "TIP 10/10", "Respect their wishes"), (99.94, "THE TAKEAWAY", "Prevent disputes tomorrow")]
cards = [(f"hd-{k+1}", t, (SECT[k+1][0] if k + 1 < len(SECT) else VIDEO_END), c, h) for k, (t, c, h) in enumerate(SECT)]
CALL = [("co-10a", 92.10, 95.50, "Their decision · made freely"), ("co-10b", 96.58, 99.80, "Respectful conversations")]
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
      <div id="op"><div id="op-a">PARENTS WRITING A WILL?</div><div id="op-b">10 TIPS TO AVOID TROUBLE</div></div>
      <div id="pg">{"".join(f'<i id="pg-{k+1}"></i>' for k in range(10))}</div>
      {hd_html}{co_html}
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#op", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, 0.12);
      tl.fromTo("#op-b", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35 }}, 0.5);
      tl.to("#op", {{ opacity: 0, y: -10, duration: 0.3, ease: "power2.in" }}, 5.8);
      tl.fromTo("#pg", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, 6.16);
      tl.to("#pg", {{ opacity: 0, duration: 0.3 }}, 99.7);{"".join(f"""
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
steps = ["Verify ownership", "Identify properties", "Beneficiaries & shares", "Backups", "Executor", "Legal formalities", "Store & review", "Surviving parent", "Fairness", "Their wishes"]
lis = "".join(f'<div class="ec-i"><b>{k+1:02d}</b>{t}</div>' for k, t in enumerate(steps))
ED = round(END - VIDEO_END, 2)
open(f"{P}/compositions/endcard.html", "w").write(f"""<template>
  <style>{BASE}
    #ec-k {{ position: absolute; left: 96px; top: 330px; }}
    #ec-t {{ position: absolute; left: 96px; right: 96px; top: 400px; font-family: "Instrument Serif", serif; font-size: 112px; line-height: 1.0; color: #F3E7D3; }}
    #ec-s {{ position: absolute; left: 96px; right: 96px; top: 530px; font-family: "Instrument Serif", serif; font-style: italic; font-size: 56px; color: #E3A23B; }}
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
        <div id="ec-t">Ashwil Bhupesh</div><div id="ec-s">Plan today. Prevent disputes tomorrow.</div>
        <div id="ec-l">{lis}</div>
        <div id="ec-c"><div class="lbl">Call / WhatsApp</div><div id="ec-n">96721 19046</div></div>
        <div id="ec-b">ASHWILLPOWER</div><div class="note" style="top:1510px;left:0;right:0;text-align:center">General information · not legal advice</div>
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
PUNCH = [(0, 1.0), (6.16, 1.03), (14.24, 1.0), (22.64, 1.03), (31.12, 1.0), (40.66, 1.03), (47.78, 1.0), (57.40, 1.03), (67.90, 1.0), (76.94, 1.03), (88.74, 1.0), (92.10, 1.03), (99.94, 1.0), (101.9, 1.04)]
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
