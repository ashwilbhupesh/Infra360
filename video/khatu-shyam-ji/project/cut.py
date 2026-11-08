import json, subprocess
P=[(0.0, 0.4), (1.52, 1.88), (4.24, 5.82), (7.42, 7.76), (9.6, 10.12), (12.74, 13.22), (14.22, 14.56), (16.14, 16.52), (17.56, 18.62), (20.62, 21.08), (22.76, 23.3), (23.56, 24.08), (25.4, 25.96), (27.92, 28.46), (28.74, 29.24), (30.62, 31.12), (32.86, 33.22), (34.66, 35.16), (35.48, 35.88), (38.4, 38.74), (40.84, 41.74), (43.44, 43.98), (45.46, 45.98), (47.06, 47.48), (49.88, 50.34), (52.54, 52.84), (54.06, 54.68), (57.16, 57.5), (59.32, 60.12), (61.78, 62.2), (63.04, 63.48), (64.66, 65.08), (66.4, 67.32), (68.3, 68.66), (70.26, 70.8), (73.58, 74.22), (75.92, 79.32), (81.68, 82.34), (83.18, 83.98), (85.36, 86.12), (88.02, 88.74), (89.86, 90.26), (91.7, 92.1), (92.96, 93.28), (94.32, 94.62), (94.88, 95.66), (98.28, 98.84)]
START, END = 0.36, 98.45
rem=[(s+.17,e-.17) for s,e in P[1:-1] if e-s>0.5]
rem+= [(64.87,66.86),(91.9,95.27)]
rem=sorted(rem); merged=[]
for a,b in rem:
    if merged and a<=merged[-1][1]: merged[-1]=(merged[-1][0],max(b,merged[-1][1]))
    else: merged.append((a,b))
keep=[]; cur=START
for a,b in merged:
    if a>cur: keep.append((cur,a))
    cur=max(cur,b)
keep.append((cur,END))
json.dump(keep,open('keep.json','w'))
n=len(keep); fc=[]
for i,(a,b) in enumerate(keep):
    fc.append(f"[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={b-a-0.02:.3f}:d=0.02[a{i}]")
fc.append("".join(f"[v{i}][a{i}]" for i in range(n))+f"concat=n={n}:v=1:a=1[v][a];[a]loudnorm=I=-16:TP=-1.5[an]")
subprocess.run(["ffmpeg","-y","-v","error","-i","raw_rec.mp4","-filter_complex",";".join(fc),"-map","[v]","-map","[an]","-c:v","libx264","-crf","18","-preset","fast","-r","30","-c:a","aac","-b:a","192k","-ar","48000","voice_edit.mp4"],check=True)
print(n,"pieces; total",round(sum(b-a for a,b in keep),2))
