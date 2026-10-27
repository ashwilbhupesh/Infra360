import sys
f = sys.argv[1]; s = open(f).read()
def rep(a, b, n=1):
    global s
    assert a in s, a[:80]; s = s.replace(a, b, n)
rep("CUT_A, CUT_B, GAP = 26.96, 33.38, 4.0", "CUT_A, CUT_B, GAP = 26.96, 33.38, 4.5")
rep('top:985px;font-size:26px;color:#F3E7D3">JAIPUR', 'top:985px;font-size:28px;color:#F3E7D3">JAIPUR')
rep('<div class="mono" style="font-size:26px">Planning to buy in Jaipur?</div>', '<div class="mono" style="font-size:28px">Planning to buy in Jaipur?</div>')
rep('IN("#s3-a", 0.15); IN("#s3-ar", 0.9); IN("#s3-b", 1.2, { scale: 0.92 }, { scale: 1 }); IN("#s3-n", 1.6);', 'IN("#s3-a", 0.15); IN("#s3-ar", 0.6); IN("#s3-b", 0.8, { scale: 0.92 }, { scale: 1 }); IN("#s3-n", 0.5);')
rep("s = 33.85\nitems", "s = out(36.0) - 0.75\nitems")
rep('scene("s4", s, 37.95,', 'scene("s4", s, out(41.1),')
rep('[("dev", 0, 4.1)]', '[("dev", 0, round(out(41.1) - (out(36.0) - 0.75), 2))]')
rep('SHOW("#cta", {CUT_A + GAP + 0.05}, 33.85);', 'SHOW("#cta", {CUT_A + GAP + 0.05}, {round(out(36.0) - 0.75, 2)});')
rep("(37.95, 1.0)", "(out(41.1), 1.0)")
open(f, "w").write(s)
