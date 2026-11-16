import json, re, sys
P = "proj"; END = 73.1
words = json.load(open("words.json"))
# caption fixes (spellings and names; verbatim otherwise)
FIX = {"Ashfil.": "Ashwil.", "NTIC": "NTSE", "IT": "IIT", "contactors": "contractors", "They're": "I'm", "Behind": "Between", "Emergent": "Emergent"}
EM = {"ashwil.", "pwd", "ntse", "iit", "delhi", "98.", "1%", "left.", "build", "$50,000.", "half", "million", "hidden,", "contractors", "brokers,", "cut.",
      "platform,", "map.", "prices", "direct", "compete.", "co-founder", "build.", "mvp", "beta", "december.", "ef."}
toks = []
for i, w in enumerate(words):
    t = FIX.get(w["text"], w["text"])
    if w["text"] == "a" and i + 1 < len(words) and words[i + 1]["text"] == "track": continue        # "on a track" → "on track"
    toks.append({"t": t, "s": w["start"], "em": t.lower().strip(",") in EM or t.lower() in EM})
def glen(g): return len(" ".join(w["t"] for w in g))
groups, cur = [], []
for i, w in enumerate(toks):
    cur.append(w); nxt = toks[i + 1] if i + 1 < len(toks) else None
    if nxt is None or glen(cur + [nxt]) > 28 or w["t"][-1] in ".?!" or (w["t"][-1] == "," and glen(cur) >= 12) or (nxt["s"] - w["s"] > 1.2):
        groups.append(cur); cur = []
caps = []
for gi, g in enumerate(groups):
    nx = groups[gi + 1][0]["s"] - 0.04 if gi + 1 < len(groups) else END
    caps.append((round(max(0.05, g[0]["s"] - 0.06), 2), round(min(nx, g[-1]["s"] + 0.9), 2), g))
json.dump({"captions": [{"start": a, "end": b, "text": " ".join(w["t"] for w in g)} for a, b, g in caps]}, open("captions.json", "w"), indent=1)

H, J = [], []           # overlay html, timeline js
def at(sel, t, frm, to, d=0.45, ease="power3.out"): J.append(f'tl.fromTo("{sel}", {frm}, {{...{to}, duration: {d}, ease: "{ease}"}}, {t:.2f});')
def show(sel, t, d=0.45, y=24): at(sel, t, f"{{opacity:0, y:{y}}}", "{opacity:1, y:0}", d)
def pop(sel, t): at(sel, t, "{opacity:0, scale:0.6}", "{opacity:1, scale:1}", 0.4, "back.out(2)")
def hide(sel, t, d=0.3): J.append(f'tl.to("{sel}", {{opacity:0, y:-12, duration:{d}, ease:"power2.in"}}, {t:.2f});')
def box(i, a, b, inner, top=110, h=None, zone="top"):
    H.append(f'<div class="zone" id="{i}" style="top:{top}px;{f"height:{h}px;" if h else ""}">{inner}</div>')
    show(f"#{i}", a); hide(f"#{i}", b - 0.3)

# chapter bar (top)
CH = [("STORY", 0, 24.3), ("BUSINESS", 24.3, 34.6), ("PROBLEM", 34.6, 44.3), ("SOLUTION", 44.3, 56.2), ("THE ASK", 56.2, END)]
H.append('<div id="chap">' + "".join(f'<div class="ch" id="ch{k}"><i><b id="chf{k}"></b></i><span>{n}</span></div>' for k, (n, a, b) in enumerate(CH)) + "</div>")
for k, (n, a, b) in enumerate(CH):
    J.append(f'tl.fromTo("#chf{k}", {{width:"0%"}}, {{width:"100%", duration:{b - a:.2f}, ease:"none"}}, {a:.2f});')
    J.append(f'tl.fromTo("#ch{k} span", {{color:"rgba(255,255,255,0.55)"}}, {{color:"#FFB547", duration:0.2}}, {a:.2f});')
    J.append(f'tl.to("#ch{k} span", {{color:"rgba(255,255,255,0.55)", duration:0.2}}, {b:.2f});')

# 1 · name card (0–2.3)
box("g1", 0.0, 2.35, '<div class="kick">FOUNDER · JAIPUR, INDIA</div><div class="big serif">Ashwil Bhupesh</div><div class="sub">Land development · Real estate</div>')
J.append('tl.set("#g1", {opacity:1, y:0}, 0);')
H.append('<div class="lower" id="efc"><span class="dot"></span>Pitch for Entrepreneurs First</div>'); show("#efc", 0.3); hide("#efc", 2.3)
# 2 · roots (2.4–8.6)
road = ('<svg width="300" height="120" viewBox="0 0 300 120"><path d="M0 100 C80 100 120 20 300 20" style="fill:none;stroke:#3B3F45;stroke-width:34;stroke-linecap:round"/>'
        '<path id="rd" d="M0 100 C80 100 120 20 300 20" style="fill:none;stroke:#FFD27A;stroke-width:4;stroke-dasharray:16 14"/></svg>')
box("g2", 2.4, 8.7, f'<div class="row">{road}<div><div class="kick">WHERE I COME FROM</div><div class="mid">Grew up on road sites</div><div class="sub">Father · Public Works Dept, Rajasthan</div></div></div>')
J.append('tl.fromTo("#rd", {strokeDashoffset:0}, {strokeDashoffset:-180, duration:6, ease:"none"}, 2.4);')
H.append('<div class="lower medal" id="ntse">🏅 NTSE Scholar</div>'); pop("#ntse", 7.5); hide("#ntse", 8.7)
# 3 · IIT Delhi (8.8–11.95)
box("g3", 8.8, 12.0, '<div class="row"><div class="stat"><span id="rk">999</span></div><div><div class="kick">IIT DELHI</div><div class="mid">Category rank</div><div class="sub">Engineering · India\'s top institute</div></div></div>')
J.append('const rk={v:999}; tl.to(rk, {v:98, duration:1.5, ease:"power3.out", onUpdate:()=>{document.getElementById("rk").textContent=Math.round(rk.v)}}, 9.55);')
# 4 · civil services (12.2–18.5)
box("g4", 12.2, 18.6, '<div class="kick">UPSC CIVIL SERVICES</div><div class="mid">"To work for the common man"</div><div class="bar"><b id="cb"></b><span id="cbt">Top 1% · Prelims</span></div>')
at("#cb", 16.2, "{width:'0%'}", "{width:'99%'}", 1.2, "power2.out"); pop("#cbt", 17.2)
# 5 · then I left (18.7–24.2)
H.append('<div class="zone center" id="g5a"><div class="stamp">THEN I LEFT.</div></div>'); at("#g5a", 18.7, "{opacity:0, scale:1.6}", "{opacity:1, scale:1}", 0.35, "back.out(1.4)"); hide("#g5a", 19.75, 0.2)
box("g5", 19.8, 24.3, '<div class="paths"><div class="pth" id="ps">Safe path<i></i></div><div class="arrow">→</div><div class="pth hot" id="pb">BUILD</div></div>')
J.append('tl.fromTo("#ps i", {width:"0%"}, {width:"100%", duration:0.4}, 21.4);'); pop("#pb", 22.9)
# 6 · traction (24.3–31.9)
box("g6", 24.3, 31.95, '<div class="kick">TRACTION · 3 YEARS</div><div class="chart"><div class="col"><b id="b1"></b><span>$50K</span><em>started with</em></div>'
    '<div class="col"><b id="b2" class="hot"></b><span id="b2t">~$500K</span><em>revenue this year · on track</em></div></div>')
at("#b1", 27.3, "{height:0}", "{height:22}", 0.6); at("#b2", 30.5, "{height:0}", "{height:220}", 1.0, "power2.out"); pop("#b2t", 30.8)
# 7 · model (31.9–34.5)
box("g7", 31.9, 34.55, '<div class="kick">WHAT I DO</div><div class="steps"><span id="s1">Buy land</span><i>→</i><span id="s2">Develop</span><i>→</i><span id="s3">Sell</span></div>')
for k, t in enumerate([32.1, 33.0, 33.8]): pop(f"#s{k+1}", t)
# 8 · problem (34.6–44.3)
box("g8", 34.6, 44.35, '<div class="kick red">THE PROBLEM · FROM INSIDE</div><div class="xl"><div id="x1">✕ Prices are hidden</div><div id="x2">✕ Good contractors are hard to find</div><div id="x3">✕ 3–4 brokers between buyer &amp; owner</div></div>')
for k, t in enumerate([36.8, 38.0, 40.0]): show(f"#x{k+1}", t, 0.35, 12)
chain = ('<div class="chain" id="chain"><span class="pp">Buyer</span>' + "".join(f'<i>→</i><span class="bk" id="bk{k}">Broker<em id="cut{k}">− cut</em></span>' for k in range(3)) + '<i>→</i><span class="pp">Owner</span></div>')
H.append(f'<div class="lower2" id="g8b">{chain}</div>'); show("#g8b", 40.4)
for k in range(3): pop(f"#bk{k}", 41.9 + 0.2 * k); pop(f"#cut{k}", 43.3 + 0.15 * k)
J.append('tl.to(".bk", {opacity:0, scale:0.4, width:0, padding:0, margin:0, duration:0.5, ease:"power2.in"}, 45.0);')
J.append('tl.to("#chain > i", {opacity:0, duration:0.3}, 45.0);')
H.append('<div class="lower2" id="g8c"><div class="chain"><span class="pp">Buyer</span><span class="direct">⟷ direct ⟷</span><span class="pp">Owner</span></div></div>')
hide("#g8b", 45.4, 0.2); show("#g8c", 45.6, 0.35); hide("#g8c", 55.9)
# 9 · solution (44.3–56.1)
feat = [("🗺️", "Whole area on a map", 47.2), ("₹", "Real prices · materials &amp; services", 48.7), ("🤝", "Direct contact with owners", 51.4), ("🏗️", "Contractors list work &amp; compete", 53.2)]
box("g9", 44.3, 56.15, '<div class="kick green">THE FIX · ONE PLATFORM</div><div class="grid">' + "".join(f'<div class="ft" id="f{k}"><b>{ic}</b>{tx}</div>' for k, (ic, tx, _) in enumerate(feat)) + "</div>")
for k, (_, _, t) in enumerate(feat): pop(f"#f{k}", t)
# 10 · edge (56.2–60.4)
box("g10", 56.2, 60.45, '<div class="kick">MY EDGE</div><div class="edge"><div id="e0" class="dim">Not technical</div><div id="e1">✓ I know the ground</div><div id="e2">✓ I know the people</div><div id="e3">✓ I know how to sell</div></div>')
for k, t in enumerate([56.3, 57.6, 58.6, 59.5]): show(f"#e{k}", t, 0.3, 10)
# 11 · the ask (60.5–62.8)
H.append('<div class="zone center" id="g11"><div class="ask"><div class="kick">I\'M LOOKING FOR</div><div class="big">A TECHNICAL<br>CO-FOUNDER</div></div></div>')
at("#g11", 60.5, "{opacity:0, scale:0.8}", "{opacity:1, scale:1}", 0.4, "back.out(1.6)")
J.append('tl.fromTo("#g11 .ask", {boxShadow:"0 0 0 0 rgba(255,181,71,0.0)"}, {boxShadow:"0 0 0 18px rgba(255,181,71,0.0)", duration:0.7, repeat:2, ease:"sine.out"}, 61.0);')
J.append('tl.fromTo("#g11 .ask", {borderColor:"#FFB547"}, {borderColor:"#FFF1D0", duration:0.35, repeat:5, yoyo:true}, 61.0);')
hide("#g11", 62.75)
# 12 · progress (62.9–69.9)
box("g12", 62.9, 70.0, '<div class="kick">WHERE IT STANDS</div><div class="tline"><div class="ms" id="m1"><b>✓</b>MVP built<em>on Emergent</em></div><div class="trk"><b id="tp"></b></div><div class="ms" id="m2"><b id="m2b">○</b>Beta launch<em>December</em></div></div>')
pop("#m1", 63.3); at("#tp", 64.8, "{width:'0%'}", "{width:'72%'}", 2.2, "power1.inOut"); pop("#m2", 65.5)
J.append('tl.fromTo("#m2b", {scale:1}, {scale:1.35, duration:0.4, yoyo:true, repeat:3}, 66.3);')
# 13 · close (70.1–END)
box("g13", 70.05, END + 0.3, '<div class="kick">THANK YOU</div><div class="big serif">Ashwil Bhupesh</div><div class="sub">Looking forward to joining EF</div>')
H.append('<div class="lower" id="efc2"><span class="dot"></span>Seeking a technical co-founder</div>'); show("#efc2", 70.4)

# captions
cap_html = "".join(f'<div class="cp" id="cp{gi}"><div class="cpi">' + " ".join(f'<span class="w{" em" if w["em"] else ""}">{w["t"]}</span>' for w in g) + '</div></div>' for gi, (a, b, g) in enumerate(caps))
for gi, (a, b, g) in enumerate(caps):
    J.append(f'tl.fromTo("#cp{gi}", {{opacity:0, y:8}}, {{opacity:1, y:0, duration:0.12}}, {a});')
    for k, w in enumerate(g): J.append(f'tl.fromTo("#cp{gi} .w:nth-child({k+1})", {{opacity:0.55}}, {{opacity:1, duration:0.08, ease:"none"}}, {w["s"]:.2f});')
    J.append(f'tl.to("#cp{gi}", {{opacity:0, duration:0.08}}, {b - 0.08:.2f});')

CSS = """
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#000}
#root{position:relative;width:1080px;height:1920px;overflow:hidden}
#avatar{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover}
#topfade{position:absolute;left:0;right:0;top:0;height:560px;background:linear-gradient(180deg,rgba(8,10,14,0.72),rgba(8,10,14,0.35) 70%,rgba(8,10,14,0))}
#botfade{position:absolute;left:0;right:0;bottom:0;height:520px;background:linear-gradient(0deg,rgba(8,10,14,0.8),rgba(8,10,14,0.4) 60%,rgba(8,10,14,0))}
.zone{position:absolute;left:56px;right:56px;opacity:0;font-family:Inter,Helvetica,Arial,sans-serif;color:#fff}
.zone.center{top:150px;display:flex;justify-content:center}
.kick{font:600 26px/1 "JetBrains Mono",monospace;letter-spacing:.18em;color:#FFB547;margin-bottom:12px}
.kick.red{color:#FF7A6B}.kick.green{color:#7EE2A8}
.big{font-weight:900;font-size:84px;line-height:.98;letter-spacing:-.01em;text-shadow:0 6px 28px rgba(0,0,0,.6)}
.serif{font-family:"Instrument Serif",Georgia,serif;font-weight:400;font-size:104px}
.mid{font-weight:800;font-size:54px;line-height:1.05;text-shadow:0 4px 20px rgba(0,0,0,.6)}
.sub{font-weight:600;font-size:32px;color:#E8E3DA;margin-top:10px}
.row{display:flex;align-items:center;gap:28px}
.stat{font-weight:900;font-size:150px;line-height:1;color:#FFB547;min-width:250px;text-align:right;text-shadow:0 6px 30px rgba(255,181,71,.35)}
.bar{position:relative;margin-top:22px;height:64px;border-radius:32px;background:rgba(255,255,255,.14);overflow:hidden}
.bar b{position:absolute;left:0;top:0;bottom:0;background:linear-gradient(90deg,#FFB547,#FFD98A);border-radius:32px}
.bar span{position:absolute;right:24px;top:12px;font-weight:900;font-size:36px;color:#1A1208}
.stamp{font-weight:900;font-size:120px;letter-spacing:-.02em;padding:18px 40px;border:6px solid #FF7A6B;color:#FF7A6B;border-radius:18px;transform:rotate(-4deg);background:rgba(8,10,14,.55)}
.paths{display:flex;align-items:center;justify-content:center;gap:30px;margin-top:40px}
.pth{position:relative;font-weight:800;font-size:56px;padding:16px 30px;border-radius:16px;background:rgba(255,255,255,.12)}
.pth i{position:absolute;left:10px;top:50%;height:6px;background:#FF7A6B;border-radius:3px}
.pth.hot{background:#FFB547;color:#1A1208;font-weight:900}
.arrow{font-size:60px;color:#FFB547}
.chart{display:flex;align-items:flex-end;gap:60px;height:330px;padding-left:20px}
.col{display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:330px}
.col b{display:block;width:150px;border-radius:12px 12px 0 0;background:rgba(255,255,255,.5)}.col b.hot{background:linear-gradient(180deg,#FFD98A,#FFB547)}
.col span{font-weight:900;font-size:50px;margin-top:8px}.col em{font-style:normal;font-weight:600;font-size:24px;color:#E8E3DA}
.steps{display:flex;align-items:center;gap:18px;margin-top:20px}.steps span{font-weight:900;font-size:54px;padding:16px 26px;border-radius:16px;background:rgba(255,255,255,.14)}
.steps i{font-style:normal;font-size:48px;color:#FFB547}
.xl div{font-weight:800;font-size:46px;margin:12px 0;color:#fff;text-shadow:0 3px 14px rgba(0,0,0,.6)}
.lower,.lower2{position:absolute;left:0;right:0;top:1700px;display:flex;justify-content:center;opacity:0;font-family:Inter,Helvetica,Arial,sans-serif}
.lower{font-weight:800;font-size:34px;color:#fff;gap:14px;align-items:center}
.lower .dot{width:16px;height:16px;border-radius:50%;background:#FFB547;box-shadow:0 0 0 6px rgba(255,181,71,.25)}
.lower.medal{font-size:40px}
.chain{display:flex;align-items:center;gap:10px}.chain i{font-style:normal;color:#FFB547;font-size:32px}
.chain .pp{font-weight:900;font-size:34px;padding:12px 20px;border-radius:14px;background:#fff;color:#111}
.chain .bk{position:relative;font-weight:800;font-size:28px;padding:10px 14px;border-radius:12px;background:rgba(255,122,107,.25);border:2px solid #FF7A6B;color:#fff;overflow:visible;white-space:nowrap}
.chain .bk em{position:absolute;left:50%;top:-40px;transform:translateX(-50%);font-style:normal;font-weight:900;font-size:26px;color:#FF7A6B}
.direct{font-weight:900;font-size:34px;color:#7EE2A8;padding:0 18px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:6px}
.ft{display:flex;align-items:center;gap:14px;font-weight:800;font-size:31px;line-height:1.15;padding:18px 20px;border-radius:18px;background:rgba(20,24,30,.78);border:2px solid rgba(126,226,168,.6)}
.ft b{font-size:44px;min-width:52px;text-align:center;color:#7EE2A8}
.edge div{font-weight:800;font-size:50px;margin:8px 0;color:#fff;text-shadow:0 3px 14px rgba(0,0,0,.6)}.edge .dim{color:rgba(255,255,255,.6);font-size:38px}
.ask{padding:30px 46px;border-radius:26px;background:rgba(8,10,14,.82);border:5px solid #FFB547;text-align:center}
.ask .big{font-size:96px;color:#FFB547}
.tline{display:flex;align-items:center;gap:18px;margin-top:20px}
.ms{display:flex;flex-direction:column;align-items:center;font-weight:900;font-size:40px;text-align:center}
.ms b{display:flex;align-items:center;justify-content:center;width:84px;height:84px;border-radius:50%;background:#7EE2A8;color:#0B2016;font-size:46px;margin-bottom:8px}
#m2 b{background:transparent;border:5px solid #FFB547;color:#FFB547}
.ms em{font-style:normal;font-weight:600;font-size:26px;color:#E8E3DA}
.trk{flex:1;height:12px;border-radius:6px;background:rgba(255,255,255,.2);position:relative;top:-40px}.trk b{position:absolute;left:0;top:0;bottom:0;border-radius:6px;background:#FFB547}
#chap{position:absolute;left:56px;right:56px;top:40px;display:flex;gap:10px;font-family:"JetBrains Mono",monospace}
.ch{flex:1}.ch i{display:block;height:6px;border-radius:3px;background:rgba(255,255,255,.25);overflow:hidden}.ch i b{display:block;height:100%;width:0;background:#FFB547}
.ch span{display:block;margin-top:8px;font-size:18px;letter-spacing:.14em;color:rgba(255,255,255,.55)}
.cp{position:absolute;left:70px;right:70px;top:1500px;display:flex;justify-content:center;opacity:0}
.cpi{text-align:center;padding:12px 24px 14px;border-radius:18px;background:rgba(8,10,14,.72);font-family:Inter,Helvetica,Arial,sans-serif;font-weight:800;font-size:52px;line-height:1.15;color:#fff}
.w{opacity:.55}.w.em{color:#FFB547}
"""
fonts = '<style>@font-face{font-family:"Instrument Serif";src:url(assets/fonts/instrument-serif-latin-400-normal.woff2)}</style>'
open(f"{P}/index.html", "w").write(f"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/><script src="assets/gsap.min.js"></script>{fonts}<style>{CSS}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1080" data-height="1920" data-fps="30">
<video id="avatar" class="clip" src="assets/avatar.mp4" data-start="0" data-duration="{END}" data-track-index="0" playsinline data-has-audio="true" data-volume="1"></video>
<div id="topfade"></div><div id="botfade"></div>
{"".join(H)}
{cap_html}
<audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="10" data-volume="0.18" data-fade-in="1.0" data-fade-out="2.0"></audio>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(J)}
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>""")
print("caption groups", len(caps))
for a, b, g in caps: print(f"{a:6.2f}-{b:6.2f} " + " ".join(w["t"] for w in g))
