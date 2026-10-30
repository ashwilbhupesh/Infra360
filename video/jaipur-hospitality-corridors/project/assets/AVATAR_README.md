# Source recording

`avatar.mp4` is not committed because of its size. To rebuild revision 3:

1. Take the original recording (a028408b-…mp4) and cut it into segments according to `../segs.json`. Each entry is `[start, end, speed]` in source seconds. For each segment run ffmpeg with `-ss start -t (end-start)` before `-i`, then apply `setpts=PTS/speed`, `atempo=speed`, and `trim`/`atrim` to the exact frame-rounded output duration.
2. Concatenate the segments, normalise loudness to −16 LUFS at 30 fps, and save the result here as `avatar.mp4` (92.23 s).
3. From `project/`, run `python3 build.py . owords.json ../osm_places.json`. `owords.json` holds the word timings already remapped to the edited track.
4. Run `npx hyperframes render -q delivery -f 30`. Then apply `volume=-2.5dB` to bring the output to −16 LUFS.
