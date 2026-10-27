import sys
f = sys.argv[1]; s = open(f).read()
def rep(a, b):
    global s
    assert a in s, a[:80]; s = s.replace(a, b, 1)
JP = '''# 2b · JAIPUR establishing (user-supplied photo)
s = 14.40
scene("jp", s, 17.45, """
    <img src="assets/img/hawa_bg.jpg" style="position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover" alt="">
    <div id="jp-f" style="position:absolute;left:96px;top:330px;width:888px;border-radius:24px;overflow:hidden;box-shadow:0 30px 70px rgba(0,0,0,.55);border:2px solid rgba(243,231,211,.35)">
      <img id="jp-i" src="assets/img/hawa.jpg" style="display:block;width:888px;height:auto" alt="Hawa Mahal, Jaipur"></div>
    <div class="chip amb" id="jp-t" style="left:96px;top:880px;font-size:44px">Jaipur</div>
    <div class="mono" id="jp-s" style="position:absolute;left:96px;top:980px;color:#F3E7D3">Source: PropEquity · calendar year 2024</div>""",
      """      IN("#jp-f", 0.05, { scale: 0.96 }, { scale: 1 }); tl.fromTo("#jp-i", { scale: 1.0 }, { scale: 1.06, duration: 3.05, ease: "none" }, 0);
      IN("#jp-t", 0.5); IN("#jp-s", 0.45);""")

# 3 · DATA — gap card'''
rep("# 3 · DATA — gap card", JP)
rep('''      <div class="ins"><div class="grain"></div>
        <div id="cd-k" class="mono">Explore property in Jaipur</div>''', '''      <div class="ins"><img src="assets/img/amer_bg.jpg" style="position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover" alt=""><div class="grain"></div>
        <div id="cd-f" style="position:absolute;left:96px;top:250px;width:888px;border-radius:24px;overflow:hidden;box-shadow:0 30px 70px rgba(0,0,0,.55);border:2px solid rgba(243,231,211,.35)"><img id="cd-i" src="assets/img/amer.jpg" style="display:block;width:888px;height:auto" alt="Amer Fort, Jaipur"></div>
        <div id="cd-k" class="mono">Explore property in Jaipur</div>''')
rep("#cd-k {{ position: absolute; left: 96px; top: 520px; }}", "#cd-k {{ position: absolute; left: 96px; top: 1000px; }}")
rep("#cd-n {{ position: absolute; left: 96px; right: 164px; top: 580px;", "#cd-n {{ position: absolute; left: 96px; right: 164px; top: 1050px;")
rep("#cd-r {{ position: absolute; left: 96px; top: 740px;", "#cd-r {{ position: absolute; left: 96px; top: 1195px;")
rep("width: 300px; top: 840px;", "width: 300px; top: 1285px;")
rep("#cd-c {{ position: absolute; left: 96px; top: 890px;", "#cd-c {{ position: absolute; left: 96px; top: 1320px;")
rep("#cd-p {{ position: absolute; left: 96px; top: 940px;", "#cd-p {{ position: absolute; left: 96px; top: 1365px;")
rep('''      ["#cd-k", "#cd-n",''', '''      tl.fromTo("#cd-f", {{ opacity: 0, scale: 0.97 }}, {{ opacity: 1, scale: 1, duration: 0.6, ease: "power3.out" }}, 0.15);
      tl.fromTo("#cd-i", {{ scale: 1 }}, {{ scale: 1.05, duration: {CD}, ease: "none" }}, 0);
      ["#cd-k", "#cd-n",''')
rep('SHOW("#src", {out(14.75)}, {CUT_A});', 'SHOW("#src", 17.45, {CUT_A});')
rep("(14.4, 1.0)", "(17.45, 1.0)")
open(f, "w").write(s)
