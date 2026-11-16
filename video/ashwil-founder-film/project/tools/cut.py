import json, subprocess, sys
S = sys.argv[1]; SRC = sys.argv[2]; SPEED = 1.07
# keep-list in source seconds
keep = [(0.45,3.85),(4.40,8.70),(8.80,12.30),(12.45,15.05),(15.25,17.30),(17.35,19.55),(20.33,23.95),
        (25.45,26.05),(26.72,31.05),(31.48,33.15),(35.25,38.70),(39.05,43.30),(43.82,45.80),(46.30,50.92),
        (51.20,62.05),(66.85,69.70),(69.70,72.42),(72.75,75.30),(75.35,79.40)]
# merge contiguous
m = []
for a,b in keep:
    if m and abs(m[-1][1]-a) < 1e-6: m[-1] = (m[-1][0], b)
    else: m.append((a,b))
keep = m
words = json.load(open(f"{S}/v2/words.json"))
# map source time -> output time
out = []; t = 0.0; segs = []
for a,b in keep:
    segs.append({"src":[a,b], "out":[round(t/SPEED,3), round((t+b-a)/SPEED,3)]})
    for w in words:
        if a - 0.05 <= w["start"] < b - 0.05:
            out.append({"text": w["text"], "start": round((t + max(w["start"],a) - a)/SPEED,3), "end": round((t + min(w["end"], b) - a)/SPEED,3), "src": w["start"]})
    t += b - a
json.dump({"segments":segs,"words":out,"duration":round(t/SPEED,3)}, open(f"{S}/v2/cut.json","w"), indent=1)
print("out duration", round(t/SPEED,2), "segments", len(keep))
vf = "zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,eq=contrast=1.07:saturation=1.0:gamma=0.97,colorbalance=rs=0.02:bs=-0.02:rm=0.02:bm=-0.015,vignette=angle=0.45"
parts=[]; fc=[]
for i,(a,b) in enumerate(keep):
    fc.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={b-a-0.015:.3f}:d=0.015[a{i}]")
    parts.append(f"[v{i}][a{i}]")
fc.append("".join(parts)+f"concat=n={len(keep)}:v=1:a=1[vc][ac]")
fc.append(f"[vc]setpts=PTS/{SPEED},fps=30,{vf}[vo];[ac]atempo={SPEED},loudnorm=I=-16:TP=-1.5:LRA=9[ao]")
cmd=["ffmpeg","-v","error","-y","-i",SRC,"-filter_complex",";".join(fc),"-map","[vo]","-map","[ao]","-c:v","libx264","-crf","15","-preset","medium","-g","30","-c:a","aac","-b:a","192k","-ar","48000",f"{S}/v2/proj/assets/talk.mp4"]
subprocess.run(cmd, check=True)
