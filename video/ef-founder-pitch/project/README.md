# Rebuild
1. Re-encode the source recording (b5bbe57f…mp4) at 30 fps with `loudnorm=I=-16`, and save it as `assets/avatar.mp4`.
2. Put `words.json` (Parakeet word timings) next to `build.py`, run `python3 build.py`, and copy the generated `index.html` into this folder.
3. Run `npx hyperframes@0.8.221 render -q delivery -f 30`, then apply `volume=-2.4dB`.
