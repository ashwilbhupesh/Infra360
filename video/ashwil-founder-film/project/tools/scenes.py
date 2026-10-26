import sys, os
P = sys.argv[1]
BASE = """
    @font-face { font-family: "Instrument Serif"; src: url("assets/fonts/instrument-serif-latin-400-normal.woff2") format("woff2"); font-style: normal; font-weight: 400; }
    @font-face { font-family: "Instrument Serif"; src: url("assets/fonts/instrument-serif-latin-400-italic.woff2") format("woff2"); font-style: italic; font-weight: 400; }
    #root { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
    .host { position: absolute; inset: 0; }
    .serif { font-family: "Instrument Serif", serif; font-weight: 400; color: #f2ede4; line-height: 0.92; letter-spacing: -0.01em; }
    .it { font-style: italic; }
    .gold { color: #c9a86a; }
    .sans { font-family: "Inter", sans-serif; color: #f2ede4; }
    .lbl { font-family: "JetBrains Mono", monospace; font-weight: 400; font-size: 26px; letter-spacing: 0.24em; text-transform: uppercase; color: #a8a194; }
    .lbl b { color: #c9a86a; font-weight: 400; }
    .panel { position: absolute; top: 0; bottom: 0; background: radial-gradient(130% 70% at 30% 25%, #1a1a1f 0%, #0c0c0e 65%); overflow: hidden; }
    .panel.full { left: 0; width: 1080px; }
    .panel.left { left: 0; width: 560px; border-right: 2px solid rgba(201,168,106,0.55); }
    .panel.right { left: 520px; width: 560px; border-left: 2px solid rgba(201,168,106,0.55); }
    .grain { position: absolute; inset: 0; opacity: 0.06; background-image: radial-gradient(rgba(255,255,255,0.9) 1px, transparent 1px); background-size: 7px 7px; }
    .col { position: absolute; left: 56px; right: 48px; }
    .rule { height: 2px; background: linear-gradient(90deg, #c9a86a, rgba(201,168,106,0)); transform-origin: 0 50%; }
    .scrim { position: absolute; left: 0; right: 0; top: 0; height: 760px; background: linear-gradient(180deg, rgba(12,12,14,0.86) 0%, rgba(12,12,14,0.55) 55%, rgba(12,12,14,0) 100%); }
"""
MOVE = 'duration: 0.62, ease: "power3.inOut"'

def scene(cid, dur, css, body, js):
    html = f"""<template>
  <style>{BASE}{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920">
    <div id="{cid}-host" class="host clip" data-start="0" data-duration="{dur}">{body}
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      const MOVE = {{ {MOVE} }};
      const IN = (sel, t, extra) => tl.fromTo(sel, Object.assign({{ opacity: 0, filter: "blur(10px)" }}, (extra||{{}}).from || {{}}), Object.assign({{ opacity: 1, filter: "blur(0px)", duration: 0.34, ease: "expo.out" }}, (extra||{{}}).to || {{}}), t);
{js}
      window.__timelines["{cid}"] = tl;
    }})();
  </script>
</template>
"""
    open(f"{P}/compositions/{cid}.html", "w").write(html)

# ---------- hook (overlay, 0-3.4) ----------
scene("hook", 3.4, """
    #hk-chips { position: absolute; top: 230px; left: 0; right: 0; display: flex; justify-content: center; gap: 18px; }
    .chip { font-family: "JetBrains Mono", monospace; font-size: 27px; letter-spacing: 0.18em; color: #f2ede4; padding: 12px 22px; border: 1.5px solid rgba(201,168,106,0.8); border-radius: 4px; background: rgba(12,12,14,0.55); }
    #hk-first { position: absolute; top: 175px; left: 0; right: 0; text-align: center; font-size: 230px; }
    #hk-first span { display: inline-block; }
    #hk-last { position: absolute; top: 400px; left: 0; right: 0; text-align: center; font-family: "Inter", sans-serif; font-weight: 700; font-size: 44px; letter-spacing: 0.62em; padding-left: 0.62em; color: #f2ede4; }
    #hk-loc { position: absolute; top: 480px; left: 0; right: 0; display: flex; justify-content: center; align-items: center; gap: 18px; }
    #hk-loc i { display: block; width: 60px; height: 1.5px; background: #c9a86a; }
""", """
      <div class="scrim" id="hk-scrim"></div>
      <div id="hk-chips"><span class="chip">IIT DELHI</span><span class="chip">NTSE SCHOLAR</span><span class="chip">TOP 1%</span></div>
      <div id="hk-first" class="serif it"><span>A</span><span>s</span><span>h</span><span>w</span><span>i</span><span>l</span></div>
      <div id="hk-last">BHUPESH</div>
      <div id="hk-loc"><i></i><span class="lbl">Jaipur, Rajasthan &nbsp;<b>26.91&deg;N 75.79&deg;E</b></span><i></i></div>""", """
      tl.fromTo("#hk-scrim", { opacity: 0 }, { opacity: 1, duration: 0.2 }, 0);
      tl.fromTo("#hk-chips .chip", { opacity: 0, y: 14, filter: "blur(6px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.3, stagger: 0.08, ease: "expo.out" }, 0.06);
      tl.to("#hk-chips .chip", { opacity: 0, filter: "blur(8px)", duration: 0.16, stagger: 0.03, ease: "power2.in" }, 0.7);
      tl.fromTo("#hk-first span", { opacity: 0.0, y: 30, filter: "blur(8px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.4, stagger: 0.05, ease: "expo.out" }, 0.86);
      tl.fromTo("#hk-last", { opacity: 0, letterSpacing: "0.9em" }, { opacity: 1, letterSpacing: "0.62em", duration: 0.7, ease: "expo.out" }, 1.2);
      tl.fromTo("#hk-loc", { opacity: 0 }, { opacity: 1, duration: 0.3 }, 2.22);
      tl.fromTo("#hk-loc i", { scaleX: 0 }, { scaleX: 1, duration: 0.5, ease: "expo.out" }, 2.22);
      tl.to("#hk-first, #hk-last, #hk-loc, #hk-scrim", { opacity: 0, filter: "blur(8px)", duration: 0.2, ease: "power2.in" }, 3.12);""")

# ---------- crore (full, from right; 3.3-7.75) ----------
dots = []
R, C, sp = 13, 13, 50
for r in range(R):
    for c in range(C):
        x = c * sp; y = r * sp
        d = ((r - R//2)**2 + (c - C//2)**2) ** 0.5
        if (r, c) == (R//2, C//2): continue
        dots.append(f'<circle class="cr-dot" data-d="{d:.2f}" cx="{x+25}" cy="{y+25}" r="5"/>')
scene("crore", 4.45, """
    #cr-panel { transform: translateX(1080px); }
    #cr-lbl { top: 250px; }
    #cr-grid { position: absolute; left: 215px; top: 330px; width: 650px; height: 650px; }
    .cr-dot { fill: #3a3833; }
    #cr-one { fill: #c9a86a; }
    #cr-ring { fill: none; stroke: #c9a86a; stroke-width: 2; }
    #cr-one-lbl { position: absolute; left: 600px; top: 600px; }
    #cr-num { position: absolute; left: 0; right: 0; top: 1000px; display: flex; justify-content: center; align-items: baseline; gap: 26px; }
    #cr-100 { font-size: 250px; }
    #cr-crore { font-size: 140px; }
""", f"""
      <div id="cr-panel" class="panel full"><div class="grain"></div>
        <div id="cr-lbl" class="col lbl" style="text-align:center;left:0;right:0">India &middot; <b>Population</b></div>
        <svg id="cr-grid" viewBox="0 0 650 650">{''.join(dots)}<circle id="cr-ring" cx="325" cy="325" r="22"/><circle id="cr-one" cx="325" cy="325" r="9"/></svg>
        <div id="cr-one-lbl" class="lbl"><b>1</b> child</div>
        <div id="cr-num"><span id="cr-100" class="serif">100</span><span id="cr-crore" class="serif it gold">crore+</span></div>
      </div>""", """
      tl.fromTo("#cr-panel", { x: 1080 }, { x: 0, ...MOVE }, 0);
      IN("#cr-lbl", 0.45);
      tl.fromTo("#cr-one", { scale: 0, transformOrigin: "50% 50%" }, { scale: 1, duration: 0.45, ease: "back.out(2)" }, 0.4);
      tl.fromTo("#cr-ring", { scale: 0.4, opacity: 1, transformOrigin: "50% 50%" }, { scale: 2.2, opacity: 0, duration: 0.9, ease: "power2.out" }, 0.42);
      IN("#cr-one-lbl", 0.55, { from: { x: -12 }, to: { x: 0 } });
      tl.to("#cr-one-lbl", { opacity: 0, duration: 0.2 }, 1.25);
      const dots = Array.from(document.querySelectorAll(".cr-dot"));
      dots.forEach((d) => {
        const k = parseFloat(d.getAttribute("data-d"));
        tl.fromTo(d, { opacity: 0, scale: 0, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: 0.3, ease: "power2.out" }, 1.25 + k * 0.17);
      });
      tl.fromTo(dots, { fill: "#3a3833" }, { fill: "#6b655a", duration: 0.4 }, 2.6);
      IN("#cr-100", 2.6, { from: { y: 40 }, to: { y: 0 } });
      IN("#cr-crore", 2.82, { from: { x: 30 }, to: { x: 0 } });
      tl.to("#cr-panel", { x: -1080, ...MOVE }, 3.8);""")

# ---------- difficult (overlay; 7.5-10.5) ----------
scene("difficult", 3.0, """
    #df-a { position: absolute; left: 0; right: 0; top: 230px; text-align: center; }
    #df-b { position: absolute; left: 0; right: 0; top: 290px; text-align: center; font-size: 170px; }
    #df-c { position: absolute; left: 0; right: 0; top: 290px; text-align: center; font-size: 170px; }
""", """
      <div class="scrim" id="df-scrim"></div>
      <div id="df-a" class="lbl">It was always</div>
      <div id="df-b" class="serif">difficult</div>
      <div id="df-c" class="serif it gold">prestigious.</div>""", """
      tl.fromTo("#df-scrim", { opacity: 0 }, { opacity: 1, duration: 0.25 }, 0);
      IN("#df-a", 0.08);
      IN("#df-b", 0.34, { from: { y: 26 }, to: { y: 0 } });
      tl.to("#df-a", { opacity: 0, duration: 0.2 }, 1.95);
      tl.to("#df-b", { opacity: 0, filter: "blur(10px)", duration: 0.2, ease: "power2.in" }, 2.1);
      IN("#df-c", 2.26, { from: { y: 26 }, to: { y: 0 } });
      tl.to("#df-c, #df-scrim", { opacity: 0, filter: "blur(8px)", duration: 0.2 }, 2.78);""")

# ---------- grades (split left; 12.3-17.5) ----------
scene("grades", 5.2, """
    #gr-panel { transform: translateX(-560px); }
    #gr-l1 { top: 250px; }
    #gr-ten { top: 300px; display: flex; align-items: baseline; }
    #gr-ten .a { font-size: 300px; }
    #gr-ten .b { font-size: 130px; margin-left: 10px; }
    #gr-cgpa { top: 610px; font-family: "Inter", sans-serif; font-weight: 800; font-size: 46px; letter-spacing: 0.32em; color: #f2ede4; }
    #gr-rule { top: 720px; }
    #gr-l2 { top: 770px; }
    #gr-ntse { top: 820px; font-family: "Inter", sans-serif; font-weight: 900; font-size: 150px; letter-spacing: -0.02em; color: #f2ede4; line-height: 0.95; }
    #gr-sch { top: 965px; font-size: 120px; }
""", """
      <div id="gr-panel" class="panel left"><div class="grain"></div>
        <div id="gr-l1" class="col lbl">Class X &middot; <b>Board</b></div>
        <div id="gr-ten" class="col serif"><span class="a">10</span><span class="b it gold">/10</span></div>
        <div id="gr-cgpa" class="col">CGPA</div>
        <div id="gr-rule" class="col rule"></div>
        <div id="gr-l2" class="col lbl">Class X &middot; <b>National</b></div>
        <div id="gr-ntse" class="col">NTSE</div>
        <div id="gr-sch" class="col serif it gold">Scholar</div>
      </div>""", """
      tl.fromTo("#gr-panel", { x: -560 }, { x: 0, ...MOVE }, 0);
      IN("#gr-l1", 0.5);
      IN("#gr-ten .a", 0.56, { from: { y: 40 }, to: { y: 0 } });
      IN("#gr-ten .b", 0.74, { from: { x: -20 }, to: { x: 0 } });
      IN("#gr-cgpa", 1.2, { from: { letterSpacing: "0.6em" }, to: { letterSpacing: "0.32em", duration: 0.6 } });
      tl.fromTo("#gr-rule", { scaleX: 0 }, { scaleX: 1, duration: 0.6, ease: "expo.out" }, 2.3);
      IN("#gr-l2", 2.45);
      IN("#gr-ntse", 2.8, { from: { y: 40 }, to: { y: 0 } });
      IN("#gr-sch", 3.45, { from: { x: -20 }, to: { x: 0 } });
      tl.to("#gr-panel", { x: 1080, ...MOVE }, 4.55);""")

# ---------- iit (full, from left; 16.85-20.95) ----------
scene("iit", 4.1, """
    #ii-panel { transform: translateX(-1080px); }
    #ii-lbl { top: 250px; text-align: center; left: 0; right: 0; }
    #ii-iit { position: absolute; left: 0; right: 0; top: 300px; text-align: center; font-family: "Inter", sans-serif; font-weight: 900; font-size: 330px; letter-spacing: -0.03em; color: #f2ede4; line-height: 1; }
    #ii-delhi { position: absolute; left: 0; right: 0; top: 600px; text-align: center; font-size: 190px; }
    #ii-rule { position: absolute; left: 290px; right: 290px; top: 840px; height: 2px; background: #c9a86a; transform-origin: 50% 50%; }
    #ii-lbl2 { top: 880px; text-align: center; left: 0; right: 0; }
    #ii-rank { position: absolute; left: 0; right: 0; top: 925px; text-align: center; font-size: 260px; }
    #ii-rank small { font-size: 110px; color: #a8a194; margin-right: 12px; }
""", """
      <div id="ii-panel" class="panel full"><div class="grain"></div>
        <div id="ii-lbl" class="col lbl">Admission &middot; <b>Engineering</b></div>
        <div id="ii-iit">IIT</div>
        <div id="ii-delhi" class="serif it gold">Delhi</div>
        <div id="ii-rule"></div>
        <div id="ii-lbl2" class="col lbl">National <b>Category</b> Rank</div>
        <div id="ii-rank" class="serif"><small class="it">#</small><span id="ii-num">0</span></div>
      </div>""", """
      tl.fromTo("#ii-panel", { x: -1080 }, { x: 0, ...MOVE }, 0);
      IN("#ii-lbl", 0.45);
      IN("#ii-iit", 0.36, { from: { scale: 1.15 }, to: { scale: 1, duration: 0.5 } });
      IN("#ii-delhi", 0.83, { from: { y: 30 }, to: { y: 0 } });
      tl.fromTo("#ii-rule", { scaleX: 0 }, { scaleX: 1, duration: 0.6, ease: "expo.out" }, 1.4);
      IN("#ii-lbl2", 1.55);
      IN("#ii-rank", 1.7);
      const num = document.getElementById("ii-num"); const c = { v: 0 };
      tl.fromTo(c, { v: 1000 }, { v: 98, duration: 1.15, ease: "expo.out", onUpdate: () => { num.textContent = Math.round(c.v); } }, 1.7);
      tl.to("#ii-panel", { x: -1080, ...MOVE }, 3.45);""")

# ---------- civil (split right; 20.3-27.1) ----------
scene("civil", 6.8, """
    #cv-panel { transform: translateX(560px); }
    #cv-first { top: 230px; font-size: 170px; }
    #cv-fam { top: 400px; font-family: "Inter", sans-serif; font-weight: 600; font-size: 40px; color: #f2ede4; }
    #cv-lbl { top: 500px; }
    .cv-row { position: absolute; left: 56px; right: 48px; height: 78px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(242,237,228,0.14); }
    .cv-row .s { font-family: "JetBrains Mono", monospace; font-size: 26px; letter-spacing: 0.16em; color: #a8a194; }
    .cv-row .n { font-family: "Inter", sans-serif; font-weight: 600; font-size: 40px; color: #6f6a62; }
    #cv-r1 { top: 545px; } #cv-r2 { top: 623px; } #cv-r3 { top: 701px; }
    #cv-hl { position: absolute; left: 40px; right: 32px; top: 623px; height: 78px; border: 2px solid #c9a86a; background: rgba(201,168,106,0.1); transform-origin: 0 50%; }
    #cv-one { top: 820px; font-size: 290px; }
    #cv-one-lbl { top: 1100px; }
""", """
      <div id="cv-panel" class="panel right"><div class="grain"></div>
        <div id="cv-first" class="col serif it gold">First</div>
        <div id="cv-fam" class="col">in my family to attempt</div>
        <div id="cv-lbl" class="col lbl">Civil <b>Services</b></div>
        <div id="cv-hl"></div>
        <div id="cv-r1" class="cv-row"><span class="s">STAGE I</span><span class="n">Prelims</span></div>
        <div id="cv-r2" class="cv-row"><span class="s">STAGE II</span><span class="n">Mains</span></div>
        <div id="cv-r3" class="cv-row"><span class="s">STAGE III</span><span class="n">Interview</span></div>
        <div id="cv-one" class="col serif gold">1%</div>
        <div id="cv-one-lbl" class="col lbl">Only <b>1%</b> get here</div>
      </div>""", """
      tl.fromTo("#cv-panel", { x: 560 }, { x: 0, ...MOVE }, 0);
      IN("#cv-first", 0.8, { from: { y: 30 }, to: { y: 0 } });
      IN("#cv-fam", 1.0);
      IN("#cv-lbl", 2.15);
      tl.fromTo(".cv-row", { opacity: 0, x: 30 }, { opacity: 1, x: 0, duration: 0.35, stagger: 0.07, ease: "expo.out" }, 2.25);
      tl.fromTo("#cv-hl", { scaleX: 0, opacity: 0 }, { scaleX: 1, opacity: 1, duration: 0.45, ease: "expo.out" }, 3.95);
      tl.fromTo("#cv-r2 .n", { color: "#6f6a62" }, { color: "#f2ede4", duration: 0.2 }, 3.95);
      tl.fromTo("#cv-r2 .s", { color: "#a8a194" }, { color: "#c9a86a", duration: 0.2 }, 3.95);
      IN("#cv-one", 5.05, { from: { y: 40, scale: 0.94 }, to: { y: 0, scale: 1, duration: 0.5 } });
      IN("#cv-one-lbl", 5.3);
      tl.to("#cv-panel", { x: 560, ...MOVE }, 6.15);""")

# ---------- top1 (overlay; 26.9-29.75) ----------
scene("top1", 2.85, """
    #t1-a { position: absolute; left: 0; right: 0; top: 260px; text-align: center; font-size: 130px; }
    #t1-top { position: absolute; left: 0; right: 0; top: 215px; text-align: center; font-family: "Inter", sans-serif; font-weight: 300; font-size: 58px; letter-spacing: 0.7em; padding-left: 0.7em; color: #f2ede4; }
    #t1-one { position: absolute; left: 0; right: 0; top: 270px; text-align: center; font-size: 300px; }
""", """
      <div class="scrim" id="t1-scrim"></div>
      <div id="t1-a" class="serif it">time and again.</div>
      <div id="t1-top">TOP</div>
      <div id="t1-one" class="serif gold">1%</div>""", """
      tl.fromTo("#t1-scrim", { opacity: 0 }, { opacity: 1, duration: 0.25 }, 0);
      IN("#t1-a", 0.14, { from: { y: 24 }, to: { y: 0 } });
      tl.to("#t1-a", { opacity: 0, filter: "blur(10px)", duration: 0.2, ease: "power2.in" }, 1.55);
      IN("#t1-top", 1.8, { from: { letterSpacing: "1.1em" }, to: { letterSpacing: "0.7em", duration: 0.6 } });
      IN("#t1-one", 2.32, { from: { scale: 1.2 }, to: { scale: 1, duration: 0.45 } });
      tl.to("#t1-top, #t1-one, #t1-scrim", { opacity: 0, filter: "blur(8px)", duration: 0.12 }, 2.72);""")

# ---------- mission (overlay; 29.75-33.6) ----------
scene("mission", 3.85, """
    #ms-a { position: absolute; left: 0; right: 0; top: 230px; text-align: center; font-size: 170px; }
    #ms-b { position: absolute; left: 0; right: 0; top: 410px; text-align: center; font-family: "Inter", sans-serif; font-weight: 800; font-size: 64px; letter-spacing: 0.02em; color: #f2ede4; }
    #ms-c { position: absolute; left: 0; right: 0; top: 410px; text-align: center; font-size: 110px; }
""", """
      <div class="scrim" id="ms-scrim"></div>
      <div id="ms-a" class="serif it">Build</div>
      <div id="ms-b">A COMPANY. NOW.</div>
      <div id="ms-c" class="serif it gold">for employment.</div>""", """
      tl.fromTo("#ms-scrim", { opacity: 0 }, { opacity: 1, duration: 0.25 }, 0);
      IN("#ms-a", 0.37, { from: { y: 26 }, to: { y: 0 } });
      tl.fromTo("#ms-b", { opacity: 0, clipPath: "inset(0 100% 0 0)" }, { opacity: 1, clipPath: "inset(0 0% 0 0)", duration: 0.5, ease: "expo.out" }, 0.7);
      tl.to("#ms-b", { opacity: 0, y: -20, duration: 0.2, ease: "power2.in" }, 2.6);
      IN("#ms-c", 2.85, { from: { y: 26 }, to: { y: 0 } });
      tl.to("#ms-a, #ms-c, #ms-scrim", { opacity: 0, filter: "blur(8px)", duration: 0.18 }, 3.62);""")

# ---------- realty (split left; 33.65-40.45) ----------
sky = ("M0,260 L0,170 L40,170 L40,120 L90,120 L90,190 L120,190 L120,60 L170,60 L170,30 L190,30 L190,60 L220,60 L220,200 "
       "L260,200 L260,100 L320,100 L320,150 L350,150 L350,80 L400,80 L400,210 L440,210 L440,140 L456,140 L456,260 Z")
wins = "".join(f'<path class="rl-w" pathLength="1" d="M{x},{y} h14"/>' for x, y in [(130,90),(150,90),(130,120),(150,120),(130,150),(150,150),(270,130),(290,130),(360,110),(380,110),(360,140),(380,140),(360,170),(380,170),(50,150),(65,140)])
scene("realty", 6.8, """
    #rl-panel { transform: translateX(-560px); }
    #rl-lbl { top: 250px; }
    #rl-real { top: 300px; font-size: 180px; }
    #rl-est { top: 450px; font-size: 180px; }
    #rl-sky { position: absolute; left: 56px; top: 680px; width: 456px; height: 260px; overflow: visible; }
    #rl-sky path { fill: none; stroke: #c9a86a; stroke-width: 2.5; stroke-linejoin: round; stroke-dasharray: 1; stroke-dashoffset: 1; }
    #rl-sky .rl-w { stroke: rgba(242,237,228,0.5); stroke-width: 2; }
    #rl-prob { top: 985px; font-family: "Inter", sans-serif; font-weight: 800; font-size: 72px; color: #f2ede4; }
    #rl-strike { position: absolute; left: 50px; top: 1028px; width: 330px; height: 5px; background: #c9a86a; transform-origin: 0 50%; }
    #rl-tech { top: 1075px; font-size: 120px; }
""", f"""
      <div id="rl-panel" class="panel left"><div class="grain"></div>
        <div id="rl-lbl" class="col lbl">Currently &middot; <b>Working in</b></div>
        <div id="rl-real" class="col serif">Real</div>
        <div id="rl-est" class="col serif it gold">Estate</div>
        <svg id="rl-sky" viewBox="0 0 456 260"><path id="rl-line" pathLength="1" d="{sky}"/>{wins}</svg>
        <div id="rl-prob" class="col">Problems</div>
        <div id="rl-strike"></div>
        <div id="rl-tech" class="col serif it gold">Technology.</div>
      </div>""", """
      tl.fromTo("#rl-panel", { x: -560 }, { x: 0, ...MOVE }, 0);
      IN("#rl-lbl", 0.45);
      IN("#rl-real", 0.5, { from: { y: 30 }, to: { y: 0 } });
      IN("#rl-est", 0.72, { from: { y: 30 }, to: { y: 0 } });
      tl.fromTo("#rl-line", { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 1.6, ease: "power2.inOut" }, 0.8);
      tl.fromTo(".rl-w", { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 0.25, stagger: 0.04, ease: "power1.out" }, 1.9);
      IN("#rl-prob", 2.65, { from: { x: -24 }, to: { x: 0 } });
      tl.fromTo("#rl-strike", { scaleX: 0 }, { scaleX: 1, duration: 0.35, ease: "expo.out" }, 4.95);
      tl.to("#rl-prob", { opacity: 0.35, duration: 0.3 }, 5.0);
      IN("#rl-tech", 5.55, { from: { y: 30 }, to: { y: 0 } });
      tl.to("#rl-panel", { x: -1080, ...MOVE }, 6.15);""")

# ---------- vision (full -> right split; 39.8-50.5) ----------
scene("vision", 10.7, """
    #vs-panel { transform: translateX(1080px); }
    #vs-lbl { top: 250px; left: 0; right: 0; text-align: center; }
    #vs-five { position: absolute; left: 0; right: 0; top: 300px; text-align: center; font-size: 260px; }
    #vs-line { position: absolute; left: 140px; right: 140px; top: 690px; height: 2px; background: #c9a86a; transform-origin: 0 50%; }
    .vs-tick { position: absolute; top: 676px; width: 30px; height: 30px; margin-left: -15px; border-radius: 50%; border: 2px solid #c9a86a; background: #0c0c0e; }
    .vs-y { position: absolute; top: 730px; width: 120px; margin-left: -60px; text-align: center; }
    #vs-tick-5 { background: #c9a86a; }
    #vs-mkt { position: absolute; left: 0; right: 0; top: 840px; text-align: center; font-size: 110px; }
    #vs-mkt2 { position: absolute; left: 0; right: 0; top: 960px; text-align: center; font-family: "Inter", sans-serif; font-weight: 700; font-size: 46px; letter-spacing: 0.3em; color: #f2ede4; }
    #vs-p2 { position: absolute; left: 576px; width: 470px; top: 0; bottom: 0; }
    #vs-lbl2 { position: absolute; top: 250px; left: 0; }
    #vs-emp { position: absolute; top: 300px; left: 0; font-size: 130px; }
    .vs-li { position: absolute; left: 0; right: 0; display: flex; align-items: center; gap: 20px; font-family: "Inter", sans-serif; font-weight: 700; font-size: 54px; color: #f2ede4; }
    .vs-li i { display: block; width: 14px; height: 14px; background: #c9a86a; transform: rotate(45deg); }
    #vs-li1 { top: 520px; } #vs-li2 { top: 610px; }
    #vs-plat { position: absolute; top: 740px; left: 0; font-size: 120px; }
""", """
      <div id="vs-panel" class="panel full"><div class="grain"></div>
        <div id="vs-p1">
          <div id="vs-lbl" class="col lbl">The next <b>five</b> years</div>
          <div id="vs-five" class="serif">Five years.</div>
          <div id="vs-line"></div>
          <div class="vs-tick" style="left:140px"></div><div class="vs-tick" style="left:340px"></div><div class="vs-tick" style="left:540px"></div><div class="vs-tick" style="left:740px"></div><div id="vs-tick-5" class="vs-tick" style="left:940px"></div>
          <div class="vs-y lbl" style="left:140px">Y1</div><div class="vs-y lbl" style="left:340px">Y2</div><div class="vs-y lbl" style="left:540px">Y3</div><div class="vs-y lbl" style="left:740px">Y4</div><div class="vs-y lbl" style="left:940px"><b>Y5</b></div>
          <div id="vs-mkt" class="serif it gold">India's real estate</div>
          <div id="vs-mkt2">MARKET</div>
        </div>
        <div id="vs-p2">
          <div id="vs-lbl2" class="lbl">Creating <b>opportunity</b></div>
          <div id="vs-emp" class="serif">Jobs</div>
          <div id="vs-li1" class="vs-li"><i></i>Employees</div>
          <div id="vs-li2" class="vs-li"><i></i>Stakeholders</div>
          <div id="vs-plat" class="serif it gold">One platform.</div>
        </div>
      </div>""", """
      tl.fromTo("#vs-panel", { x: 1080 }, { x: 0, ...MOVE }, 0);
      IN("#vs-lbl", 0.4);
      IN("#vs-five", 0.48, { from: { y: 36 }, to: { y: 0 } });
      tl.fromTo("#vs-line", { scaleX: 0 }, { scaleX: 1, duration: 2.4, ease: "power1.inOut" }, 1.0);
      document.querySelectorAll(".vs-tick").forEach((el, i) => tl.fromTo(el, { scale: 0 }, { scale: 1, duration: 0.3, ease: "back.out(2)" }, 1.0 + i * 0.6));
      document.querySelectorAll(".vs-y").forEach((el, i) => tl.fromTo(el, { opacity: 0 }, { opacity: 1, duration: 0.2 }, 1.05 + i * 0.6));
      IN("#vs-mkt", 2.85, { from: { y: 24 }, to: { y: 0 } });
      IN("#vs-mkt2", 3.4, { from: { letterSpacing: "0.6em" }, to: { letterSpacing: "0.3em", duration: 0.6 } });
      // narrow to the right half: the speaker returns from the left
      tl.to("#vs-p1", { opacity: 0, filter: "blur(10px)", duration: 0.25, ease: "power2.in" }, 4.2);
      tl.fromTo("#vs-panel", { clipPath: "inset(0px 0px 0px 0px)" }, { clipPath: "inset(0px 0px 0px 520px)", ...MOVE }, 4.45);
      tl.fromTo("#vs-panel", { borderLeft: "0px solid rgba(201,168,106,0)" }, { borderLeft: "0px solid rgba(201,168,106,0)", duration: 0.01 }, 0);
      IN("#vs-lbl2", 4.9);
      IN("#vs-emp", 5.2, { from: { y: 30 }, to: { y: 0 } });
      IN("#vs-li1", 7.05, { from: { x: 30 }, to: { x: 0 } });
      IN("#vs-li2", 8.35, { from: { x: 30 }, to: { x: 0 } });
      IN("#vs-plat", 9.75, { from: { y: 30 }, to: { y: 0 } });
      tl.to("#vs-panel", { x: 560, ...MOVE }, 10.05);""")

# ---------- pillars (overlay; 50.35-53.1) ----------
scene("pillars", 2.75, """
    #pl-1 { position: absolute; left: 0; right: 0; top: 200px; text-align: center; font-size: 160px; }
    #pl-2 { position: absolute; left: 0; right: 0; top: 345px; text-align: center; font-family: "Inter", sans-serif; font-weight: 900; font-size: 130px; letter-spacing: 0.12em; padding-left: 0.12em; color: #c9a86a; line-height: 1; }
    #pl-3 { position: absolute; left: 0; right: 0; top: 485px; text-align: center; font-family: "JetBrains Mono", monospace; font-size: 54px; letter-spacing: 0.2em; color: #f2ede4; }
""", """
      <div class="scrim" id="pl-scrim" style="height:820px"></div>
      <div id="pl-1" class="serif it">Transparent</div>
      <div id="pl-2">FAIR</div>
      <div id="pl-3">justifiable</div>""", """
      tl.fromTo("#pl-scrim", { opacity: 0 }, { opacity: 1, duration: 0.25 }, 0);
      IN("#pl-1", 0.27, { from: { y: 24 }, to: { y: 0 } });
      IN("#pl-2", 0.83, { from: { scale: 1.25 }, to: { scale: 1, duration: 0.4 } });
      tl.fromTo("#pl-3", { opacity: 0, clipPath: "inset(0 100% 0 0)" }, { opacity: 1, clipPath: "inset(0 0% 0 0)", duration: 0.5, ease: "steps(11)" }, 1.15);
      tl.to("#pl-1, #pl-2, #pl-3, #pl-scrim", { opacity: 0, filter: "blur(8px)", duration: 0.2 }, 2.5);""")

# ---------- access (split right; 53.1-61.7) ----------
scene("access", 8.6, """
    #ac-panel { transform: translateX(560px); }
    #ac-lbl { top: 250px; }
    #ac-last { top: 300px; font-size: 150px; }
    #ac-per { top: 430px; font-size: 150px; }
    #ac-acc { top: 610px; font-family: "Inter", sans-serif; font-weight: 600; font-size: 42px; line-height: 1.25; color: #f2ede4; }
    #ac-chart { position: absolute; left: 56px; top: 790px; width: 456px; height: 300px; overflow: visible; }
    #ac-chart .ax { stroke: rgba(242,237,228,0.25); stroke-width: 2; fill: none; }
    #ac-chart #ac-curve { stroke: #c9a86a; stroke-width: 5; fill: none; stroke-linecap: round; stroke-dasharray: 1; stroke-dashoffset: 1; }
    #ac-chart #ac-area { fill: url(#ac-grad); }
    #ac-dot { fill: #c9a86a; }
    #ac-lbl2 { top: 1110px; }
    #ac-earn { position: absolute; right: 48px; top: 760px; font-size: 96px; }
""", """
      <div id="ac-panel" class="panel right"><div class="grain"></div>
        <div id="ac-lbl" class="col lbl">Access &middot; <b>for all</b></div>
        <div id="ac-last" class="col serif">The last</div>
        <div id="ac-per" class="col serif it gold">person.</div>
        <div id="ac-acc" class="col">Access to the market<br/>around them.</div>
        <svg id="ac-chart" viewBox="0 0 456 300">
          <defs><linearGradient id="ac-grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c9a86a" stop-opacity="0.35"/><stop offset="1" stop-color="#c9a86a" stop-opacity="0"/></linearGradient></defs>
          <path class="ax" d="M0,0 V290 H456"/>
          <path id="ac-area" d="M0,270 C90,262 150,240 220,200 S350,90 446,24 L446,290 L0,290 Z"/>
          <path id="ac-curve" pathLength="1" d="M0,270 C90,262 150,240 220,200 S350,90 446,24"/>
          <circle id="ac-dot" cx="446" cy="24" r="10"/>
        </svg>
        <div id="ac-earn" class="serif it">Earn.</div>
        <div id="ac-lbl2" class="col lbl">Per capita <b>income &uarr;</b></div>
      </div>""", """
      tl.fromTo("#ac-panel", { x: 560 }, { x: 0, ...MOVE }, 0);
      IN("#ac-lbl", 0.5);
      IN("#ac-last", 1.2, { from: { y: 30 }, to: { y: 0 } });
      IN("#ac-per", 1.5, { from: { y: 30 }, to: { y: 0 } });
      IN("#ac-acc", 2.7, { from: { y: 16 }, to: { y: 0 } });
      IN("#ac-earn", 5.2, { from: { y: 20 }, to: { y: 0 } });
      tl.to("#ac-earn", { opacity: 0, duration: 0.2 }, 5.6);
      tl.fromTo("#ac-chart .ax", { opacity: 0 }, { opacity: 1, duration: 0.3 }, 5.55);
      tl.fromTo("#ac-curve", { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 1.7, ease: "power2.inOut" }, 5.7);
      tl.fromTo("#ac-area", { opacity: 0 }, { opacity: 1, duration: 1.2 }, 6.3);
      tl.fromTo("#ac-dot", { scale: 0, transformOrigin: "50% 50%" }, { scale: 1, duration: 0.35, ease: "back.out(2.5)" }, 7.35);
      IN("#ac-lbl2", 5.75);
      tl.to("#ac-panel", { x: -1080, ...MOVE }, 7.95);""")

# ---------- end card (full; 61.05-64) ----------
scene("endcard", 2.95, """
    #ec-panel { transform: translateX(1080px); }
    #ec-first { position: absolute; left: 0; right: 0; top: 520px; text-align: center; font-size: 230px; }
    #ec-last { position: absolute; left: 0; right: 0; top: 720px; text-align: center; font-size: 230px; }
    #ec-rule { position: absolute; left: 390px; right: 390px; top: 985px; height: 2px; background: #c9a86a; transform-origin: 50% 50%; }
    #ec-sub { position: absolute; left: 0; right: 0; top: 1030px; text-align: center; }
""", """
      <div id="ec-panel" class="panel full"><div class="grain"></div>
        <div id="ec-first" class="serif">Ashwil</div>
        <div id="ec-last" class="serif it gold">Bhupesh</div>
        <div id="ec-rule"></div>
        <div id="ec-sub" class="lbl">IIT Delhi &nbsp;&middot;&nbsp; NTSE Scholar &nbsp;&middot;&nbsp; <b>Jaipur</b></div>
      </div>""", """
      tl.fromTo("#ec-panel", { x: 1080 }, { x: 0, ...MOVE }, 0);
      IN("#ec-first", 0.5, { from: { y: 30 }, to: { y: 0, duration: 0.6 } });
      IN("#ec-last", 0.68, { from: { y: 30 }, to: { y: 0, duration: 0.6 } });
      tl.fromTo("#ec-rule", { scaleX: 0 }, { scaleX: 1, duration: 0.7, ease: "expo.out" }, 0.95);
      IN("#ec-sub", 1.1);""")

# ---------- chapters (0-61) ----------
scene("chapters", 61, """
    .ch { position: absolute; left: 56px; top: 186px; display: flex; align-items: center; gap: 16px; opacity: 0; }
    .ch i { display: block; width: 44px; height: 1.5px; background: #c9a86a; transform-origin: 0 50%; }
""", """
      <div id="ch-1" class="ch"><span class="lbl"><b>01</b></span><i></i><span class="lbl">The Journey</span></div>
      <div id="ch-2" class="ch"><span class="lbl"><b>02</b></span><i></i><span class="lbl">The Mission</span></div>
      <div id="ch-3" class="ch"><span class="lbl"><b>03</b></span><i></i><span class="lbl">The Vision</span></div>""", """
      [["#ch-1", 3.95], ["#ch-2", 29.85], ["#ch-3", 40.4]].forEach(([s, t]) => {
        tl.fromTo(s, { opacity: 0, x: -16 }, { opacity: 1, x: 0, duration: 0.4, ease: "expo.out" }, t);
        tl.fromTo(s + " i", { scaleX: 0 }, { scaleX: 1, duration: 0.5, ease: "expo.out" }, t + 0.1);
        tl.to(s, { opacity: 0, duration: 0.3 }, t + 2.4);
      });""")
print("ok")
