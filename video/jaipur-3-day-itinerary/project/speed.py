import json, subprocess
P = json.load(open('phrases.json'))
d = {p['k']: p for p in P}
X = round((d[3]['e'] + d[4]['s']) / 2, 3); F = 1.2; SH = X - X / F
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", "voice.wav", "-filter_complex",
  f"[0:a]atrim=0:{X},asetpts=PTS-STARTPTS,atempo={F}[a];[0:a]atrim={X},asetpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=0:a=1[o]",
  "-map", "[o]", "-c:a", "pcm_s16le", "voice_fast.wav"], check=True)
for p in P:
    for k in ('s', 'e'): p[k] = round(p[k] / F if p[k] <= X else p[k] - SH, 2)
json.dump(P, open('phrases_fast.json', 'w'), indent=0)
json.dump({"X": X, "F": F}, open('speed.json', 'w'))
print(X, SH, d[3]['e'] / F)
