# Ashwil Bhupesh — Founder Film (investor reel)

- `Ashwil_Founder_Film.mp4`: final 1080×1920, 30 fps, 64 s.
- `project/`: HyperFrames source. `project/tools/` holds the scripts that made it:
  - `cut.py`: the edit decision list (source keep-ranges), cut at 1.07× speed with tonemapping and grading.
  - `scenes.py`, `captions.py`: generate `compositions/*.html` (re-run after edits).
  - `pad.py`: the synthesized ambient music bed.

## Re-rendering
1. Rebuild `project/assets/talk.mp4` from `IMG_7644.mp4` using the keep-list in `tools/cut.py`.
2. `cd project && npx hyperframes render -q delivery -o renders/out.mp4`

## Structure
| Time | Beat | Layout |
| --- | --- | --- |
| 0–3.3 | Name and credentials teaser | Over the speaker |
| 3.3–7.1 | 100 crore+ people (dot field) | Full push, right to left |
| 7.1–12.3 | "difficult… prestigious." | Over the speaker |
| 12.3–16.9 | 10/10 CGPA · NTSE Scholar | Split, panel from left |
| 16.9–20.3 | IIT Delhi · category rank 98 | Full push, left to right |
| 20.3–26.5 | First in family · Civil Services Stage II · 1% | Split, panel from right |
| 26.5–33.6 | Top 1% · "Build a company" | Over the speaker |
| 33.6–39.8 | Real Estate · Problems → Technology | Split, panel from left |
| 39.8–49.9 | Five years · Jobs · One platform | Full push, then narrows to a right split |
| 49.9–53.1 | Transparent · FAIR · justifiable | Over the speaker |
| 53.1–61.0 | The last person · per-capita income ↑ | Split, panel from right |
| 61.0–64.0 | Ashwil Bhupesh | Full push |
