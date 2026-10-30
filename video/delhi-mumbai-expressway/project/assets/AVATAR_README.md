# Source recording

`avatar.mp4` is not committed because of its size. To rebuild:

1. Take the original recording (bf6c940b…mp4). Re-encode it at 30 fps with loudness normalised to −16 LUFS (`loudnorm=I=-16:TP=-1.5:LRA=11`), and save it here as `avatar.mp4`. Use the full take; there are no cuts.
2. From `project/`, run `python3 build.py . words.json places.json`. The OpenStreetMap geometry is read from `osm/`.
3. Run `npx hyperframes@0.8.221 render -q delivery -f 30`, then apply `volume=-2.6dB` to bring the output to −16 LUFS.
