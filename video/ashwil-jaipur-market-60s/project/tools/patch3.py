import sys
f = sys.argv[1]; s = open(f).read()
def rep(a, b):
    global s
    assert a in s, a[:80]; s = s.replace(a, b, 1)
rep("s = out(36.0) - 0.75\nitems", "s = out(36.0) - 0.30\nitems")
rep('[("dev", 0, round(out(41.1) - (out(36.0) - 0.75), 2))]', '[("dev", 0, round(out(41.1) - (out(36.0) - 0.30), 2))]')
rep('SHOW("#cta", {CUT_A + GAP + 0.05}, {round(out(36.0) - 0.75, 2)});', 'SHOW("#cta", {CUT_A + GAP + 0.05}, {round(out(36.0) - 0.30, 2)});')
rep("Rising prices can push your choice beyond budget", "Rising prices may push it beyond budget")
rep("Rushing without verification can cost more", "Rushing without verification costs more")
open(f, "w").write(s)
