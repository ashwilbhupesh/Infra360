import sys, json
P, MAPDIR = sys.argv[1], sys.argv[2]
paths = json.load(open(f"{MAPDIR}/paths.json"))
AMBER, TEAL = "#F5A524", "#2EC4B6"

BASE = """
    @font-face { font-family: "Instrument Serif"; src: url("assets/fonts/instrument-serif-latin-400-normal.woff2") format("woff2"); font-style: normal; }
    @font-face { font-family: "Instrument Serif"; src: url("assets/fonts/instrument-serif-latin-400-italic.woff2") format("woff2"); font-style: italic; }
    #root { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
    .host { position: absolute; inset: 0; }
    .sans { font-family: "Inter", sans-serif; color: #fff; }
    .serif { font-family: "Instrument Serif", serif; color: #fff; }
    .it { font-style: italic; }
    .amb { color: #F5A524; } .teal { color: #2EC4B6; }
    .lbl { font-family: "JetBrains Mono", monospace; font-size: 30px; letter-spacing: 0.2em; text-transform: uppercase; color: #9aa3b2; white-space: nowrap; }
    .lbl b { color: #F5A524; font-weight: 400; }
    .card { position: absolute; left: 44px; right: 44px; top: 905px; height: 420px; border-radius: 34px; overflow: hidden;
      background: linear-gradient(160deg, rgba(20,26,40,0.94), rgba(10,13,22,0.94)); border: 1.5px solid rgba(255,255,255,0.12);
      box-shadow: 0 30px 70px rgba(0,0,0,0.5); }
    .card::before { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 6px; background: #F5A524; }
    .fs { position: absolute; inset: 0; background: radial-gradient(120% 70% at 50% 30%, #172033 0%, #0B0F17 70%); overflow: hidden; }
    .grid { position: absolute; inset: 0; opacity: 0.22; background-image: linear-gradient(rgba(46,196,182,0.35) 1px, transparent 1px), linear-gradient(90deg, rgba(46,196,182,0.35) 1px, transparent 1px); background-size: 72px 72px; }
    .pip { position: absolute; right: 40px; top: 190px; width: 230px; height: 230px; border-radius: 50%; overflow: hidden; border: 4px solid #F5A524; box-shadow: 0 12px 34px rgba(0,0,0,0.5); }
    .pip video { position: absolute; left: -15px; top: -58px; width: 260px; height: 462px; object-fit: cover; }
    .kick { position: absolute; left: 64px; top: 200px; }
    .ttl { position: absolute; left: 64px; right: 300px; top: 250px; font-family: "Inter", sans-serif; font-weight: 800; font-size: 74px; line-height: 1.02; letter-spacing: -0.02em; color: #fff; }
    .ttl em { font-family: "Instrument Serif", serif; font-weight: 400; font-style: italic; color: #F5A524; font-size: 1.12em; letter-spacing: 0; }
    .src { position: absolute; left: 64px; right: 64px; top: 1175px; font-family: "JetBrains Mono", monospace; font-size: 28px; letter-spacing: 0.06em; color: #6f7888; white-space: nowrap; }
"""

def scene(cid, dur, css, body, js, pip_start=None):
    pip = ""
    if pip_start is not None:
        pip = f"""
      <div id="{cid}-pipw" class="pip"><video id="{cid}-pipv" class="clip" src="assets/talk.mp4" data-start="0" data-duration="{dur}" data-media-start="{pip_start}" muted playsinline></video></div>"""
    html = f"""<template>
  <style>{BASE}{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920">
    <div id="{cid}-host" class="host clip" data-start="0" data-duration="{dur}">{body}
    </div>{pip}
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      const IN = (sel, t, f, to) => tl.fromTo(sel, Object.assign({{ opacity: 0, filter: "blur(10px)" }}, f || {{}}), Object.assign({{ opacity: 1, filter: "blur(0px)", duration: 0.36, ease: "expo.out" }}, to || {{}}), t);
      const OUTALL = (sel, t) => tl.to(sel, {{ opacity: 0, filter: "blur(8px)", duration: 0.2, ease: "power2.in" }}, t);
{js}
      window.__timelines["{cid}"] = tl;
    }})();
  </script>
</template>
"""
    open(f"{P}/compositions/{cid}.html", "w").write(html)

def card_js(sel, dur, side):
    d = -1 if side == "left" else 1
    return f"""      tl.fromTo("{sel}", {{ x: {d*1100}, filter: "blur(16px)" }}, {{ x: 0, filter: "blur(0px)", duration: 0.5, ease: "expo.out" }}, 0);
      tl.to("{sel}", {{ x: {-d*1100}, filter: "blur(12px)", duration: 0.36, ease: "power3.in" }}, {dur-0.36});"""

def fs_js(sel, dur, side):
    d = -1 if side == "left" else 1
    return f"""      tl.fromTo("{sel}", {{ x: {d*1080}, filter: "blur(18px)" }}, {{ x: 0, filter: "blur(0px)", duration: 0.5, ease: "expo.out" }}, 0);
      tl.fromTo("#{sel[1:].split('-')[0]}-pipw", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.4, ease: "back.out(1.8)" }}, 0.35);
      tl.to("#{sel[1:].split('-')[0]}-pipw", {{ scale: 0.6, opacity: 0, duration: 0.2, ease: "power2.in" }}, {dur-0.42});
      tl.to("{sel}", {{ x: {-d*1080}, filter: "blur(14px)", duration: 0.38, ease: "power3.in" }}, {dur-0.38});"""

rj = paths["rj"]
# Jaipur in the map's coordinate space (from Rajasthan's geographic extents)
JX, JY = 27.16 + (75.79-69.48)/8.79*183.76, 173.07 + (30.20-26.91)/7.15*167.53

# ---------- L1 intro: map, then manufacturing -> warehouse -> trade (0.2-5.2) ----------
scene("intro", 5.0, """
    #in-map { position: absolute; left: 50px; top: 40px; width: 380px; height: 340px; overflow: visible; }
    #in-rj { fill: #F5A524; }
    #in-pin { fill: #fff; } #in-ring { fill: none; stroke: #fff; stroke-width: 1.5; }
    #in-pinlbl { position: absolute; left: 335px; top: 168px; font-family: "JetBrains Mono", monospace; font-size: 30px; color: #fff; letter-spacing: 0.1em; }
    #in-t1 { position: absolute; left: 470px; top: 110px; font-size: 76px; font-weight: 900; letter-spacing: -0.02em; }
    #in-t2 { position: absolute; left: 470px; top: 200px; font-size: 64px; }
    #in-a { position: absolute; inset: 0; }
    #in-b { position: absolute; inset: 0; }
    .node { position: absolute; top: 120px; width: 270px; height: 190px; border-radius: 22px; border: 1.5px solid rgba(255,255,255,0.18); background: rgba(255,255,255,0.04); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px; text-align: center; }
    .node svg { width: 64px; height: 64px; }
    .node span { font-family: "Inter", sans-serif; font-weight: 700; font-size: 32px; color: #fff; line-height: 1.1; }
    #nd-1 { left: 40px; } #nd-2 { left: 352px; border: 3px solid #F5A524; background: rgba(245,165,36,0.1); } #nd-3 { left: 664px; }
    .arr { position: absolute; top: 205px; width: 42px; height: 3px; background: #F5A524; transform-origin: 0 50%; }
    #ar-1 { left: 310px; } #ar-2 { left: 622px; }
    #in-link { position: absolute; left: 352px; width: 270px; top: 330px; text-align: center; }
""", f"""
      <div id="intro-card" class="card">
        <div id="in-a">
          <svg id="in-map" viewBox="20 165 200 185"><path id="in-rj" d="{rj}"/><circle id="in-ring" cx="{JX:.1f}" cy="{JY:.1f}" r="9"/><circle id="in-pin" cx="{JX:.1f}" cy="{JY:.1f}" r="4"/></svg>
          <div id="in-pinlbl">JAIPUR</div>
          <div id="in-t1" class="sans">RAJASTHAN</div>
          <div id="in-t2" class="serif it amb">Warehousing</div>
        </div>
        <div id="in-b">
          <div id="nd-1" class="node"><svg viewBox="0 0 48 48" fill="none" stroke="#fff" stroke-width="3" stroke-linejoin="round"><path d="M4 42h40M6 42V24l10-6v6l10-6v6l10-6v24M34 42V10h6v32"/></svg><span>Manufacturing</span></div>
          <div id="ar-1" class="arr"></div>
          <div id="nd-2" class="node"><svg viewBox="0 0 48 48" fill="none" stroke="#F5A524" stroke-width="3" stroke-linejoin="round"><path d="M4 42h40M6 42V18L24 8l18 10v24"/><path d="M14 42V26h20v16M14 32h20M14 37h20"/></svg><span>Warehouse</span></div>
          <div id="ar-2" class="arr"></div>
          <div id="nd-3" class="node"><svg viewBox="0 0 48 48" fill="none" stroke="#fff" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"><path d="M3 14h26v20H3zM29 22h9l7 7v5H29z"/><circle cx="12" cy="37" r="4"/><circle cx="36" cy="37" r="4"/></svg><span>Trade &amp;<br/>Distribution</span></div>
          <div id="in-link" class="lbl"><b>The important link</b></div>
        </div>
      </div>""", card_js("#intro-card", 5.0, "left") + """
      tl.fromTo("#in-rj", { opacity: 0, scale: 0.85, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: 0.6, ease: "expo.out" }, 0.25);
      tl.fromTo("#in-ring", { scale: 0.3, opacity: 1, transformOrigin: "50% 50%" }, { scale: 2.6, opacity: 0, duration: 0.9, ease: "power2.out" }, 0.75);
      IN("#in-pin", 0.7); IN("#in-pinlbl", 0.8, { x: -10 }, { x: 0 });
      IN("#in-t1", 0.3, { y: 20 }, { y: 0 }); IN("#in-t2", 0.95, { y: 20 }, { y: 0 });
      OUTALL("#in-a", 1.45);
      IN("#nd-1", 1.6, { y: 30 }, { y: 0 });
      tl.fromTo("#ar-1", { scaleX: 0 }, { scaleX: 1, duration: 0.3, ease: "expo.out" }, 2.4);
      IN("#nd-3", 2.6, { y: 30 }, { y: 0 });
      IN("#nd-2", 3.15, { y: 30, scale: 0.9 }, { y: 0, scale: 1 });
      tl.fromTo("#ar-2", { scaleX: 0 }, { scaleX: 1, duration: 0.3, ease: "expo.out" }, 3.4);
      IN("#in-link", 3.9);
      tl.fromTo("#nd-2", { boxShadow: "0 0 0px rgba(245,165,36,0)" }, { boxShadow: "0 0 50px rgba(245,165,36,0.55)", duration: 0.3 }, 4.25);""")

# ---------- FS1 role (5.3-11.7) ----------
items = [("Inventory management", 2.86), ("Order processing", 3.98), ("Timely dispatch", 5.34)]
rows = "".join(f'<div id="rl-i{i}" class="rl-row" style="top:{700+i*130}px"><i>+</i><span>{t}</span></div>' for i, (t, _) in enumerate(items))
scene("role", 6.4, """
    #rl-stor { position: absolute; left: 64px; top: 440px; font-family: "Inter", sans-serif; font-weight: 900; font-size: 150px; letter-spacing: -0.03em; color: #fff; }
    #rl-stor small { display: block; font-family: "JetBrains Mono", monospace; font-weight: 400; font-size: 30px; letter-spacing: 0.2em; color: #9aa3b2; margin-bottom: 8px; }
    .rl-row { position: absolute; left: 64px; right: 64px; height: 108px; display: flex; align-items: center; gap: 28px; border-bottom: 1px solid rgba(255,255,255,0.12); }
    .rl-row i { font-style: normal; width: 76px; height: 76px; border-radius: 50%; background: #F5A524; color: #0B0F17; font-family: "Inter", sans-serif; font-weight: 900; font-size: 54px; display: flex; align-items: center; justify-content: center; }
    .rl-row span { font-family: "Inter", sans-serif; font-weight: 700; font-size: 62px; color: #fff; letter-spacing: -0.01em; }
    #rl-truck { position: absolute; left: 0; top: 1005px; width: 210px; height: 110px; }
    #rl-road { position: absolute; left: 64px; right: 64px; top: 1118px; height: 3px; background: repeating-linear-gradient(90deg, rgba(255,255,255,0.35) 0 30px, transparent 30px 54px); }
""", f"""
      <div id="role-fs" class="fs"><div class="grid"></div>
        <div class="kick lbl">Modern warehouse &middot; <b>role</b></div>
        <div class="ttl">Storage se <em>aage.</em></div>
        <div id="rl-stor"><small>NOT JUST</small>STORAGE</div>
        {rows}
        <div id="rl-road"></div>
        <svg id="rl-truck" viewBox="0 0 120 64"><path d="M2 8h72v40H2z" fill="#F5A524"/><path d="M74 22h24l18 16v10H74z" fill="#fff"/><path d="M80 26h14l10 10H80z" fill="#0B0F17"/><circle cx="22" cy="52" r="9" fill="#0B0F17" stroke="#fff" stroke-width="3"/><circle cx="94" cy="52" r="9" fill="#0B0F17" stroke="#fff" stroke-width="3"/></svg>
      </div>""", fs_js("#role-fs", 6.4, "right") + f"""
      IN("#role-fs .kick", 0.35); IN("#role-fs .ttl", 0.45, {{ y: 30 }}, {{ y: 0 }});
      IN("#rl-stor", 1.4, {{ scale: 1.15 }}, {{ scale: 1 }});
      tl.to("#rl-stor", {{ opacity: 0.25, duration: 0.3 }}, 2.6);
      {"".join(f'IN("#rl-i{i}", {t}, {{ x: 60 }}, {{ x: 0 }});' for i, (_, t) in enumerate(items))}
      IN("#rl-road", 5.3);
      tl.fromTo("#rl-truck", {{ x: -260 }}, {{ x: 1100, duration: 1.1, ease: "power2.in" }}, 5.36);""", pip_start=5.3)

# ---------- L2 source (11.8-15.45) ----------
scene("source", 3.65, """
    #sr-doc { position: absolute; left: 60px; top: 60px; width: 220px; height: 296px; border-radius: 12px; background: #f4f1ea; box-shadow: 0 16px 40px rgba(0,0,0,0.5); overflow: hidden; }
    #sr-doc i { position: absolute; left: 26px; height: 10px; border-radius: 5px; background: #c9ccd3; }
    #sr-doc .h { background: #0B0F17; height: 16px; }
    #sr-mark { position: absolute; left: 20px; top: 150px; width: 180px; height: 26px; background: rgba(245,165,36,0.55); transform-origin: 0 50%; }
    #sr-l { position: absolute; left: 330px; top: 80px; }
    #sr-n { position: absolute; left: 330px; top: 130px; font-weight: 800; font-size: 72px; letter-spacing: -0.02em; line-height: 1.02; }
    #sr-d { position: absolute; left: 330px; top: 290px; font-size: 52px; }
""", """
      <div id="source-card" class="card">
        <div id="sr-doc"><i class="h" style="top:30px;width:120px"></i><i style="top:66px;width:168px"></i><i style="top:90px;width:150px"></i><i style="top:114px;width:160px"></i><div id="sr-mark"></div><i style="top:158px;width:140px;background:#8a6a2a"></i><i style="top:194px;width:168px"></i><i style="top:218px;width:120px"></i><i style="top:242px;width:150px"></i></div>
        <div id="sr-l" class="lbl">Source &middot; <b>Report</b></div>
        <div id="sr-n" class="sans">Knight Frank<br/>India</div>
        <div id="sr-d" class="serif it amb">published coverage</div>
      </div>""", card_js("#source-card", 3.65, "right") + """
      IN("#sr-doc", 0.2, { y: 30, rotation: -4 }, { y: 0, rotation: 0 });
      IN("#sr-l", 0.3); IN("#sr-n", 0.38, { y: 20 }, { y: 0 });
      IN("#sr-d", 2.4, { y: 16 }, { y: 0 });
      tl.fromTo("#sr-mark", { scaleX: 0 }, { scaleX: 1, duration: 0.5, ease: "power2.out" }, 2.5);""")

# ---------- FS2 jaipur numbers (15.45-23.25) ----------
H25 = 300; H24 = round(H25/1.24)
scene("jaipur", 7.8, f"""
    #jp-num {{ position: absolute; left: 64px; top: 420px; display: flex; align-items: baseline; gap: 22px; }}
    #jp-n {{ font-family: "Inter", sans-serif; font-weight: 900; font-size: 230px; letter-spacing: -0.04em; color: #fff; line-height: 1; font-variant-numeric: tabular-nums; }}
    #jp-u {{ font-size: 76px; }}
    #jp-sub {{ position: absolute; left: 64px; top: 670px; font-family: "Inter", sans-serif; font-weight: 600; font-size: 44px; color: #c9d0db; }}
    #jp-chart {{ position: absolute; left: 64px; right: 64px; top: 740px; height: 420px; }}
    .bar {{ position: absolute; bottom: 60px; width: 220px; border-radius: 14px 14px 0 0; transform-origin: 50% 100%; }}
    #b24 {{ left: 120px; height: {H24}px; background: #3a4458; }}
    #b25 {{ left: 420px; height: {H25}px; background: linear-gradient(180deg, #F5A524, #c9801a); }}
    .bl {{ position: absolute; bottom: 0; width: 220px; text-align: center; }}
    .bv {{ position: absolute; width: 220px; text-align: center; font-family: "Inter", sans-serif; font-weight: 800; font-size: 44px; color: #fff; }}
    #gr {{ position: absolute; left: 680px; top: 40px; padding: 18px 28px; border-radius: 18px; background: rgba(46,196,182,0.14); border: 2px solid #2EC4B6; }}
    #gr b {{ display: block; font-family: "Inter", sans-serif; font-weight: 900; font-size: 92px; color: #2EC4B6; line-height: 1; }}
    #gr span {{ font-family: "JetBrains Mono", monospace; font-size: 28px; color: #9aa3b2; letter-spacing: 0.14em; }}
""", f"""
      <div id="jaipur-fs" class="fs"><div class="grid"></div>
        <div class="kick lbl">Jaipur &middot; <b>2025</b></div>
        <div class="ttl">Warehousing <em>transactions</em></div>
        <div id="jp-num"><span id="jp-n">0.0</span><span id="jp-u" class="serif it amb">lakh sq ft</span></div>
        <div id="jp-sub">Annual growth</div>
        <div id="jp-chart">
          <div id="b24" class="bar"></div><div id="b25" class="bar"></div>
          <div class="bv" style="left:120px;bottom:{H24+76}px" id="v24">~10.6</div>
          <div class="bv" style="left:420px;bottom:{H25+76}px;color:#F5A524" id="v25">13.1</div>
          <div class="bl lbl" style="left:120px">2024*</div><div class="bl lbl" style="left:420px"><b>2025</b></div>
          <div id="gr"><b>+24%</b><span>YoY GROWTH</span></div>
        </div>
        <div class="src">Source: Knight Frank India (as reported) &middot; *implied from 24% growth</div>
      </div>""", fs_js("#jaipur-fs", 7.8, "left") + """
      IN("#jaipur-fs .kick", 0.35); IN("#jaipur-fs .ttl", 0.45, { y: 30 }, { y: 0 });
      IN("#jp-num", 3.75);
      const n = document.getElementById("jp-n"); const c = { v: 0 };
      tl.fromTo(c, { v: 0 }, { v: 13.1, duration: 1.4, ease: "expo.out", onUpdate: () => { n.textContent = c.v.toFixed(1); } }, 3.85);
      IN("#jp-sub", 6.05);
      tl.fromTo("#b24", { scaleY: 0 }, { scaleY: 1, duration: 0.6, ease: "expo.out" }, 5.9);
      tl.fromTo("#b25", { scaleY: 0 }, { scaleY: 1, duration: 0.8, ease: "expo.out" }, 6.1);
      IN("#v24", 6.3); IN("#v25", 6.5);
      tl.fromTo("#jaipur-fs .bl", { opacity: 0 }, { opacity: 1, duration: 0.3 }, 5.95);
      IN("#gr", 6.25, { scale: 0.6 }, { scale: 1, ease: "back.out(2)" });
      IN("#jaipur-fs .src", 1.2);""", pip_start=15.45)

# ---------- L3 donut 35% (23.3-27.6) ----------
import math
R = 120; C = 2*math.pi*R
scene("donut", 4.3, f"""
    #dn-svg {{ position: absolute; left: 60px; top: 60px; width: 300px; height: 300px; }}
    #dn-bg {{ fill: none; stroke: #2a3346; stroke-width: 44; }}
    #dn-fg {{ fill: none; stroke: #F5A524; stroke-width: 44; stroke-linecap: butt; stroke-dasharray: {C:.1f}; stroke-dashoffset: {C:.1f}; transform: rotate(-90deg); transform-origin: 150px 150px; }}
    #dn-c {{ position: absolute; left: 60px; top: 160px; width: 300px; text-align: center; font-family: "Inter", sans-serif; font-weight: 900; font-size: 84px; color: #fff; }}
    #dn-l {{ position: absolute; left: 410px; top: 80px; }}
    #dn-t {{ position: absolute; left: 410px; top: 130px; font-weight: 800; font-size: 62px; line-height: 1.04; letter-spacing: -0.02em; }}
    #dn-s {{ position: absolute; left: 410px; top: 285px; font-size: 52px; }}
""", f"""
      <div id="donut-card" class="card">
        <svg id="dn-svg" viewBox="0 0 300 300"><circle id="dn-bg" cx="150" cy="150" r="{R}"/><circle id="dn-fg" cx="150" cy="150" r="{R}"/></svg>
        <div id="dn-c">35%</div>
        <div id="dn-l" class="lbl">Leasing <b>share</b></div>
        <div id="dn-t" class="sans">Manufacturing<br/>companies</div>
        <div id="dn-s" class="serif it amb">of leasing activity</div>
      </div>""", card_js("#donut-card", 4.3, "left") + f"""
      IN("#dn-svg", 0.2); IN("#dn-l", 0.3); IN("#dn-t", 0.46, {{ y: 20 }}, {{ y: 0 }});
      tl.fromTo("#dn-fg", {{ strokeDashoffset: {C:.1f} }}, {{ strokeDashoffset: {C*0.65:.1f}, duration: 1.0, ease: "expo.out" }}, 2.9);
      IN("#dn-c", 2.95, {{ scale: 0.7 }}, {{ scale: 1, ease: "back.out(2)" }});
      IN("#dn-s", 2.95, {{ y: 16 }}, {{ y: 0 }});""")

# ---------- FS3 map (27.6-34.75) ----------
neigh = [("pb","Punjab"),("hr","Haryana"),("up","Uttar Pradesh"),("mp","Madhya Pradesh"),("gj","Gujarat")]
others = "".join(f'<path d="{d}" class="mp-o"/>' for k, d in paths.items() if k not in dict(neigh) and k != "rj")
nb = "".join(f'<path id="mp-{k}" d="{paths[k]}" class="mp-n"/>' for k, _ in neigh)
# label anchor points in map space
lab = {"pb": (150, 140, "Punjab"), "hr": (172, 196, "Haryana"), "up": (250, 232, "Uttar Pradesh"), "mp": (205, 330, "Madhya Pradesh"), "gj": (40, 352, "Gujarat")}
labels = "".join(f'<g id="ml-{k}" class="ml"><circle cx="{x}" cy="{y}" r="3.2"/><text x="{x+6}" y="{y+4}">{t}</text></g>' for k, (x, y, t) in lab.items())
scene("mapfs", 7.15, """
    #mp-svg { position: absolute; left: 58px; top: 395px; width: 964px; height: 700px; overflow: hidden; }
    #mp-zoom { transform-origin: 120px 257px; }
    .mp-o { fill: #222b3b; stroke: #0B0F17; stroke-width: 0.6; }
    .mp-n { fill: #222b3b; stroke: #0B0F17; stroke-width: 0.6; }
    #mp-rj { fill: #F5A524; stroke: #0B0F17; stroke-width: 0.6; }
    .ml circle { fill: #fff; } .ml text { font-family: "Inter", sans-serif; font-weight: 700; font-size: 12px; fill: #fff; paint-order: stroke; stroke: #0B0F17; stroke-width: 2.5px; }
    #mp-five { position: absolute; left: 64px; top: 400px; display: flex; align-items: baseline; gap: 18px; }
    #mp-five b { font-family: "Inter", sans-serif; font-weight: 900; font-size: 150px; color: #2EC4B6; line-height: 0.9; }
    #mp-five span { font-family: "Inter", sans-serif; font-weight: 700; font-size: 40px; color: #fff; line-height: 1.1; }
    #mp-pol { position: absolute; left: 64px; top: 1105px; display: flex; align-items: center; gap: 18px; padding: 14px 24px; border-radius: 20px; background: rgba(245,165,36,0.12); border: 2px solid #F5A524; }
    #mp-pol svg { width: 50px; height: 50px; }
    #mp-pol div { font-family: "Inter", sans-serif; font-weight: 800; font-size: 38px; color: #fff; line-height: 1.05; }
    #mp-pol small { display: block; font-family: "JetBrains Mono", monospace; font-weight: 400; font-size: 28px; color: #F5A524; letter-spacing: 0.16em; }
    #mp-dev { position: absolute; right: 64px; top: 1125px; padding: 14px 22px; border-radius: 14px; background: #2EC4B6; font-family: "Inter", sans-serif; font-weight: 800; font-size: 32px; color: #0B0F17; }
    #mp-credit { position: absolute; left: 64px; top: 340px; font-family: "JetBrains Mono", monospace; font-size: 28px; color: #5d6676; }
""", f"""
      <div id="mapfs-fs" class="fs"><div class="grid"></div>
        <div class="kick lbl">Rajasthan &middot; <b>connectivity</b></div>
        <div class="ttl"><em>5-state</em> connectivity</div>
        <svg id="mp-svg" viewBox="-15 105 420 305"><g id="mp-zoom">{others}{nb}<path id="mp-rj" d="{rj}"/>{labels}</g></svg>
        <div id="mp-five"><b>5</b><span>bordering<br/>states</span></div>
        <div id="mp-pol"><svg viewBox="0 0 48 48" fill="none" stroke="#F5A524" stroke-width="3" stroke-linejoin="round"><path d="M10 4h20l8 8v32H10z"/><path d="M30 4v8h8M16 22h16M16 29h16M16 36h10"/></svg><div><small>RAJASTHAN</small>Logistics Policy 2025</div></div>
        <div id="mp-dev">Sector development &uarr;</div>
        <div id="mp-credit">Map: @svg-maps/india (CC BY 4.0)</div>
      </div>""", fs_js("#mapfs-fs", 7.15, "right") + """
      IN("#mapfs-fs .kick", 0.35); IN("#mapfs-fs .ttl", 0.45, { y: 30 }, { y: 0 });
      tl.fromTo("#mp-zoom", { scale: 0.96 }, { scale: 1.06, duration: 7.0, ease: "power1.inOut" }, 0);
      tl.fromTo("#mp-rj", { fill: "#222b3b" }, { fill: "#F5A524", duration: 0.4 }, 0.7);
      ["pb","hr","up","mp","gj"].forEach((k, i) => {
        tl.fromTo("#mp-" + k, { fill: "#222b3b" }, { fill: "#2EC4B6", duration: 0.25 }, 1.55 + i * 0.2);
        tl.fromTo("#ml-" + k, { opacity: 0 }, { opacity: 1, duration: 0.2 }, 1.6 + i * 0.2);
      });
      IN("#mp-five", 1.6, { x: -30 }, { x: 0 });
      IN("#mp-pol", 3.0, { y: 30 }, { y: 0 });
      IN("#mp-dev", 5.8, { scale: 0.7 }, { scale: 1, ease: "back.out(2)" });
      IN("#mp-credit", 0.6);""", pip_start=27.6)

# ---------- L4 execution (34.8-40.45) ----------
scene("exec", 5.65, """
    #ex-a { position: absolute; left: 60px; top: 70px; }
    #ex-op { position: absolute; left: 60px; top: 120px; font-weight: 800; font-size: 76px; letter-spacing: -0.02em; }
    #ex-arrow { position: absolute; left: 60px; top: 228px; width: 520px; height: 4px; background: #F5A524; transform-origin: 0 50%; }
    #ex-head { position: absolute; left: 580px; top: 214px; width: 0; height: 0; border-left: 26px solid #F5A524; border-top: 16px solid transparent; border-bottom: 16px solid transparent; }
    #ex-pr { position: absolute; left: 60px; top: 268px; font-size: 64px; }
    #ex-stamp { position: absolute; right: 44px; top: 250px; padding: 16px 26px; border: 5px solid #F5A524; border-radius: 16px; text-align: center; }
    #ex-stamp small { display: block; font-family: "JetBrains Mono", monospace; font-size: 28px; letter-spacing: 0.16em; color: #9aa3b2; }
    #ex-stamp b { font-family: "Inter", sans-serif; font-weight: 900; font-size: 52px; color: #F5A524; letter-spacing: 0.02em; }
""", """
      <div id="exec-card" class="card">
        <div id="ex-a" class="lbl">For the <b>developer</b></div>
        <div id="ex-op" class="sans">Opportunity</div>
        <div id="ex-arrow"></div><div id="ex-head"></div>
        <div id="ex-pr" class="serif it amb">Successful project</div>
        <div id="ex-stamp"><small>DEPENDS ON</small><b>EXECUTION</b></div>
      </div>""", card_js("#exec-card", 5.65, "right") + """
      IN("#ex-a", 0.3); IN("#ex-op", 1.5, { y: 20 }, { y: 0 });
      tl.fromTo("#ex-arrow", { scaleX: 0 }, { scaleX: 1, duration: 0.6, ease: "expo.out" }, 2.2);
      IN("#ex-head", 2.7);
      IN("#ex-pr", 2.75, { y: 20 }, { y: 0 });
      tl.fromTo("#ex-stamp", { opacity: 0, scale: 2.2, rotation: -6 }, { opacity: 1, scale: 1, rotation: -6, duration: 0.22, ease: "power4.in" }, 4.5);""")

# ---------- FS4 blueprint (40.45-48.45) ----------
scene("blue", 8.0, """
    #bp { position: absolute; left: 40px; top: 400px; width: 1000px; height: 760px; overflow: visible; }
    #bp .ln { fill: none; stroke: #2EC4B6; stroke-width: 3; stroke-dasharray: 1; stroke-dashoffset: 1; }
    #bp .fl { fill: none; stroke: #F5A524; stroke-width: 6; stroke-dasharray: 1; stroke-dashoffset: 1; }
    .ann { position: absolute; display: flex; align-items: center; gap: 14px; padding: 12px 20px; border-radius: 14px; background: rgba(11,15,23,0.86); border: 1.5px solid rgba(255,255,255,0.18); font-family: "Inter", sans-serif; font-weight: 800; font-size: 36px; color: #fff; white-space: nowrap; }
    .ann i { font-style: normal; display: flex; width: 44px; height: 44px; border-radius: 50%; background: #F5A524; color: #0B0F17; align-items: center; justify-content: center; font-family: "JetBrains Mono", monospace; font-size: 28px; font-weight: 700; }
    #an-2 { left: 64px; top: 1045px; } #an-3 { left: 64px; top: 1125px; } #an-4 { right: 64px; top: 520px; } #an-5 { left: 330px; top: 430px; }
    #an-3 small { font-family: "Instrument Serif", serif; font-style: italic; font-weight: 400; font-size: 36px; color: #F5A524; }
    #bp-truck { position: absolute; left: 0; top: 935px; width: 170px; height: 90px; }
    .drop { fill: #2EC4B6; }
    .ldarr { stroke: #F5A524; stroke-width: 4; fill: #F5A524; }
""", """
      <div id="blue-fs" class="fs"><div class="grid" style="opacity:0.35"></div>
        <div class="kick lbl">Execution &middot; <b>checklist</b></div>
        <div class="ttl">What makes it <em>work</em></div>
        <svg id="bp" viewBox="0 0 1000 760">
          <path class="ln" pathLength="1" d="M120 620 V260 L500 120 L880 260 V620"/>
          <path class="ln" pathLength="1" d="M120 260 H880"/>
          <path class="ln" pathLength="1" d="M300 620 V420 H460 V620 M540 620 V420 H700 V620"/>
          <path class="fl" pathLength="1" d="M60 620 H940"/>
          <g id="bp-ht"><path d="M930 620 V260" stroke="#fff" stroke-width="3"/><path d="M915 275 L930 255 L945 275 M915 605 L930 625 L945 605" stroke="#fff" stroke-width="3" fill="none"/></g>
          <g id="bp-load"><path class="ldarr" d="M360 500 V560 M345 545 L360 565 L375 545"/><path class="ldarr" d="M500 500 V560 M485 545 L500 565 L515 545"/><path class="ldarr" d="M640 500 V560 M625 545 L640 565 L655 545"/></g>
          <g id="bp-spr"><path d="M200 262 V290 M800 262 V290" stroke="#2EC4B6" stroke-width="4"/><circle class="drop" cx="200" cy="310" r="6"/><circle class="drop" cx="190" cy="330" r="5"/><circle class="drop" cx="210" cy="330" r="5"/><circle class="drop" cx="800" cy="310" r="6"/><circle class="drop" cx="790" cy="330" r="5"/><circle class="drop" cx="810" cy="330" r="5"/></g>
        </svg>
        <svg id="bp-truck" viewBox="0 0 120 64"><path d="M2 8h72v40H2z" fill="#2EC4B6"/><path d="M74 22h24l18 16v10H74z" fill="#fff"/><circle cx="22" cy="52" r="9" fill="#0B0F17" stroke="#fff" stroke-width="3"/><circle cx="94" cy="52" r="9" fill="#0B0F17" stroke="#fff" stroke-width="3"/></svg>
        <div id="an-5" class="ann"><i>1</i>Location</div>
        <div id="an-2" class="ann"><i>2</i>Truck movement</div>
        <div id="an-3" class="ann"><i>3</i>Floor load capacity <small>kitna weight?</small></div>
        <div id="an-4" class="ann"><i>4</i>Clear height</div>
        <div id="an-6" class="ann" style="left:64px;top:560px"><i>5</i>Fire safety</div>
      </div>""", fs_js("#blue-fs", 8.0, "left") + """
      IN("#blue-fs .kick", 0.35); IN("#blue-fs .ttl", 0.45, { y: 30 }, { y: 0 });
      tl.fromTo("#bp .ln", { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 1.2, stagger: 0.12, ease: "power2.inOut" }, 0.3);
      IN("#an-5", 0.6, { y: 20 }, { y: 0 });
      tl.fromTo("#bp-truck", { x: -200 }, { x: 760, duration: 1.6, ease: "power2.inOut" }, 1.5);
      IN("#an-2", 1.65, { y: 20 }, { y: 0 });
      tl.fromTo("#bp .fl", { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 0.6, ease: "expo.out" }, 2.4);
      tl.fromTo("#bp-load", { opacity: 0, y: -30 }, { opacity: 1, y: 0, duration: 0.4, ease: "expo.out" }, 2.5);
      IN("#an-3", 2.5, { y: 20 }, { y: 0 });
      tl.fromTo("#bp-ht", { opacity: 0, scaleY: 0, transformOrigin: "930px 620px" }, { opacity: 1, scaleY: 1, duration: 0.5, ease: "expo.out" }, 6.2);
      IN("#an-4", 6.2, { x: 30 }, { x: 0 });
      tl.fromTo("#bp-spr", { opacity: 0 }, { opacity: 1, duration: 0.3 }, 7.0);
      tl.fromTo("#bp-spr .drop", { y: -10 }, { y: 16, duration: 0.6, ease: "power1.in" }, 7.0);
      IN("#an-6", 7.0, { y: 20 }, { y: 0 });""", pip_start=40.45)

# ---------- L5 tenant match (48.5-51.25) ----------
scene("tenant", 2.75, """
    #tn-l { position: absolute; left: 60px; top: 70px; }
    #tn-t { position: absolute; left: 60px; top: 120px; font-weight: 800; font-size: 64px; line-height: 1.05; letter-spacing: -0.02em; }
    #tn-m { position: absolute; right: 60px; top: 110px; width: 210px; height: 210px; border-radius: 50%; background: #2EC4B6; display: flex; flex-direction: column; align-items: center; justify-content: center; }
    #tn-m svg { width: 90px; height: 90px; }
    #tn-m span { font-family: "Inter", sans-serif; font-weight: 900; font-size: 34px; color: #0B0F17; letter-spacing: 0.08em; }
""", """
      <div id="tenant-card" class="card">
        <div id="tn-l" class="lbl">Tenant <b>fit</b></div>
        <div id="tn-t" class="sans">Operational<br/>requirements</div>
        <div id="tn-m"><svg viewBox="0 0 24 24" fill="none" stroke="#0B0F17" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg><span>MATCH</span></div>
      </div>""", card_js("#tenant-card", 2.75, "right") + """
      IN("#tn-l", 0.2); IN("#tn-t", 0.3, { y: 20 }, { y: 0 });
      tl.fromTo("#tn-m", { opacity: 0, scale: 0.3 }, { opacity: 1, scale: 1, duration: 0.45, ease: "back.out(2.2)" }, 1.1);""")

# ---------- L6 revenue (51.3-55.25) ----------
scene("revenue", 3.95, """
    #rv-l { position: absolute; left: 60px; top: 50px; }
    .rv { position: absolute; top: 100px; width: 440px; height: 296px; border-radius: 24px; padding: 30px; background: rgba(255,255,255,0.05); border: 1.5px solid rgba(255,255,255,0.14); }
    #rv-1 { left: 40px; } #rv-2 { left: 512px; }
    .rv b { display: flex; width: 70px; height: 70px; border-radius: 50%; background: #F5A524; color: #0B0F17; align-items: center; justify-content: center; font-family: "Inter", sans-serif; font-weight: 900; font-size: 40px; }
    .rv div { margin-top: 18px; font-family: "Inter", sans-serif; font-weight: 800; font-size: 46px; line-height: 1.05; color: #fff; }
    .rv small { display: block; margin-top: 10px; font-family: "Instrument Serif", serif; font-style: italic; font-size: 38px; color: #F5A524; }
""", """
      <div id="revenue-card" class="card">
        <div id="rv-l" class="lbl">Revenue <b>streams</b></div>
        <div id="rv-1" class="rv"><b>&#8377;</b><div>Lease</div><small>rental income</small></div>
        <div id="rv-2" class="rv"><b>&#8377;</b><div>Storage &amp; handling</div><small>services</small></div>
      </div>""", card_js("#revenue-card", 3.95, "left") + """
      IN("#rv-l", 0.2);
      IN("#rv-1", 0.85, { y: 40 }, { y: 0 });
      IN("#rv-2", 2.5, { y: 40 }, { y: 0 });""")

# ---------- FS5 demand first (55.2-61.6) ----------
scene("demand", 6.4, """
    .st { position: absolute; left: 64px; right: 64px; height: 230px; border-radius: 28px; padding: 34px 40px; display: flex; align-items: center; gap: 34px; }
    .st b { font-family: "JetBrains Mono", monospace; font-weight: 400; font-size: 34px; letter-spacing: 0.1em; }
    .st div { font-family: "Inter", sans-serif; font-weight: 900; font-size: 74px; letter-spacing: -0.02em; line-height: 1; }
    .st small { display: block; margin-top: 10px; font-family: "Instrument Serif", serif; font-style: italic; font-weight: 400; font-size: 44px; letter-spacing: 0; }
    #st-d { top: 470px; background: #F5A524; color: #0B0F17; }
    #st-d div, #st-d small { color: #0B0F17; }
    #st-c { top: 820px; background: rgba(255,255,255,0.05); border: 2px solid rgba(255,255,255,0.2); color: #fff; }
    #st-c div { color: #fff; } #st-c small { color: #9aa3b2; }
    #st-ar { position: absolute; left: 50%; top: 715px; width: 4px; height: 92px; margin-left: -2px; background: #F5A524; transform-origin: 50% 0; }
""", """
      <div id="demand-fs" class="fs"><div class="grid"></div>
        <div class="kick lbl">Successful project &middot; <b>order</b></div>
        <div class="ttl">Shuruaat <em>kahan se?</em></div>
        <div id="st-d" class="st"><b>01</b><div>Customer demand<small>pehle samjhein</small></div></div>
        <div id="st-ar"></div>
        <div id="st-c" class="st"><b>02</b><div>Construction<small>uske baad</small></div></div>
      </div>""", fs_js("#demand-fs", 6.4, "right") + """
      IN("#demand-fs .kick", 0.35); IN("#demand-fs .ttl", 0.45, { y: 30 }, { y: 0 });
      IN("#st-c", 2.95, { y: 30 }, { y: 0 });
      IN("#st-d", 4.2, { y: -60, scale: 0.95 }, { y: 0, scale: 1 });
      tl.fromTo("#st-ar", { scaleY: 0 }, { scaleY: 1, duration: 0.4, ease: "expo.out" }, 4.6);""", pip_start=55.2)

# ---------- L7 name lower third (61.85-64.35) ----------
scene("name", 2.5, """
    #nm { position: absolute; left: 44px; top: 1080px; padding: 26px 40px 26px 34px; border-radius: 22px; background: rgba(11,15,23,0.9); border-left: 6px solid #F5A524; }
    #nm > b { display: block; font-family: "Inter", sans-serif; font-weight: 900; font-size: 64px; color: #fff; letter-spacing: -0.02em; }
""", """
      <div id="nm"><b>Ashwil Bhupesh</b><span class="lbl">Real estate &middot; <b>Rajasthan</b></span></div>""", """
      tl.fromTo("#nm", { x: -700, filter: "blur(12px)" }, { x: 0, filter: "blur(0px)", duration: 0.5, ease: "expo.out" }, 0);
      tl.to("#nm", { opacity: 0, duration: 0.2 }, 2.25);""")

# ---------- END card (64.35-67) ----------
scene("endc", 3.15, """
    #ec-n { position: absolute; left: 0; right: 0; top: 520px; text-align: center; font-family: "Inter", sans-serif; font-weight: 900; font-size: 110px; letter-spacing: -0.03em; color: #fff; }
    #ec-s { position: absolute; left: 0; right: 0; top: 660px; text-align: center; font-size: 70px; }
    #ec-chips { position: absolute; left: 0; right: 0; top: 820px; display: flex; flex-direction: column; align-items: center; gap: 18px; }
    .chp { padding: 16px 30px; border-radius: 16px; border: 1.5px solid rgba(255,255,255,0.18); background: rgba(255,255,255,0.05); font-family: "Inter", sans-serif; font-weight: 800; font-size: 44px; color: #fff; }
    .chp b { color: #F5A524; }
""", """
      <div id="endc-fs" class="fs"><div class="grid"></div>
        <div id="ec-n">Ashwil Bhupesh</div>
        <div id="ec-s" class="serif it amb">Rajasthan warehousing, explained</div>
        <div id="ec-chips"><div class="chp"><b>13.1 lakh</b> sq ft &middot; Jaipur 2025</div><div class="chp"><b>+24%</b> annual growth</div><div class="chp"><b>35%</b> manufacturing leasing</div></div>
        <div class="src" style="text-align:center">Data: Knight Frank India (as reported)</div>
      </div>""", """
      tl.fromTo("#endc-fs", { x: 1080, filter: "blur(18px)" }, { x: 0, filter: "blur(0px)", duration: 0.5, ease: "expo.out" }, 0);
      IN("#ec-n", 0.4, { y: 30 }, { y: 0 }); IN("#ec-s", 0.6, { y: 20 }, { y: 0 });
      tl.fromTo(".chp", { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.35, stagger: 0.1, ease: "expo.out" }, 0.55);
      IN("#endc-fs .src", 0.7);""")
print("ok")
