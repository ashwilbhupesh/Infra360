# avatar.mp4 (not committed — 1080×1920 source recording)
Rebuild from the original upload in ONE filter_complex pass (no segment concat):
- keep 0–25.80 s, 29.80–87.05 s, 94.15–99.70 s (drops the first takes of "The palace sits right in the centre" and of the closing CTA — the clearer second takes are kept)
- 40 ms audio fades at each splice, loudnorm I=-16 TP=-1.5, 30 fps → `assets/avatar.mp4` (88.7 s)
Face is shown full-screen only for the opening line; after that the voice plays under the map.
`words.json` holds the transcript timings (Parakeet) on the trimmed timeline, with spellings fixed.
