# Source recording

`avatar.mp4` is not committed because of its size. To rebuild:

1. Take the original recording (a028408b-…mp4), normalise its loudness to −16 LUFS at 30 fps, and save it here as `avatar.mp4`.
2. Run `python3 build.py . words.json ../osm_places.json`.
3. Run `npx hyperframes render -q delivery -f 30`.
