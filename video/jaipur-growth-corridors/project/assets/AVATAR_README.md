# Source recording

`avatar.mp4` is not committed because of its size. To rebuild it:

1. Cut the original recording (79a05a28-…mp4) to the segments in `../keep.json`.
2. Normalise the loudness to −16 LUFS at 30 fps and save it here as `avatar.mp4`.
3. Run `python3 build.py . owords.json ../osm_places.json`.
4. Run `npx hyperframes render -q delivery -f 30`.
