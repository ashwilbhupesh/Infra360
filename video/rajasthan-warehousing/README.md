# Rajasthan Warehousing — explainer reel

- `Rajasthan_Warehousing.mp4`: final 1080×1920, 30 fps, 67.5 s, Hinglish captions.
- `project/`: HyperFrames source. `project/tools/build.py` generates every scene; `captions.py` builds the captions from the phrase script and the word timings in `words.json`.
- Map shapes: `@svg-maps/india` (CC BY 4.0, credited on screen; licence in `tools/`).
- Data on screen is as stated in the video and attributed to Knight Frank India (as reported). The 2024 bar (~10.6 lakh sq ft) is derived from 13.1 lakh sq ft at 24% growth and is labelled as implied.

To re-render, put the 30 fps source at `project/assets/talk.mp4`, then run `cd project && npx hyperframes render -q delivery -o renders/out.mp4`.

| Time | Beat |
| --- | --- |
| 0.2–5.2 | Card: Rajasthan map with Jaipur pin → Manufacturing → Warehouse → Trade flow |
| 5.3–11.7 | Full screen: "Storage se aage" + inventory / order processing / dispatch, with a truck |
| 11.8–15.5 | Card: source, Knight Frank India report |
| 15.5–23.3 | Full screen: 13.1 lakh sq ft counter, 2024 vs 2025 bars, +24% |
| 23.3–27.6 | Card: 35% donut, manufacturing share of leasing |
| 27.6–34.8 | Full screen: map with Rajasthan and its 5 bordering states, Logistics Policy 2025 |
| 34.8–40.5 | Card: Opportunity → Successful project, stamped "Execution" |
| 40.5–48.5 | Full screen: warehouse blueprint (location, truck movement, floor load, clear height, fire safety) |
| 48.5–55.3 | Cards: tenant requirements match; revenue from lease or storage & handling |
| 55.2–61.6 | Full screen: 01 Customer demand → 02 Construction |
| 61.9–67.5 | Name lower third, recap end card |
