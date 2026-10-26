# EmpireTech Global — Instagram Reel

- `EmpireTech_Reel_final.mp4`: final 1080×1920, 30 fps, 18 s edit.
- `project/`: HyperFrames source (`index.html` + `compositions/`).

## Re-rendering

1. Put the graded talking-head clip at `project/assets/speaker.mp4`. It was made from the original iPhone HLG footage with:
   `ffmpeg -i IMG_7696.mov -map 0:v:0 -map 0:a:0 -vf "zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,fps=30,eq=contrast=1.06:saturation=1.12:gamma=0.98,colorbalance=rs=0.03:gs=-0.01:bs=-0.03:rm=0.03:bm=-0.02" -c:v libx264 -crf 14 -g 30 -c:a aac -b:a 192k speaker.mp4`
2. `cd project && npx hyperframes render -q delivery -o renders/out.mp4`

## Timeline

| Time | Beat |
| --- | --- |
| 0–2.9 s | Hook: punch-in, "Construction experts" tag, karaoke captions, warehouse/factory icons |
| 2.9–4.6 s | Brand card: emblem, EMPIRETECH GLOBAL, phone |
| 4.6–6.5 s | "Best price" / "Best quality" stamps with camera shake |
| 6.3–9.2 s | Drawn B-roll: warehouses → industries → sheds, with a picture-in-picture of the speaker |
| 8.8–12.7 s | Split layout checklist: civil engineering experts, contractors, team |
| 12.7–14.7 s | Progress bar to "Delivered on time" with captions |
| 14.7–18 s | End card: logo, tagline, services, "Call now 96721 19046" |

To swap real B-roll in, replace the `.br-shot` contents in `compositions/broll.html` with `<video muted>` clips of the same timing.
