# Source recording

`avatar.mp4` is not committed because of its size. To rebuild revision 3:

1. Take the original recording (a028408b-…mp4) and cut it according to `../segs.json`. Each entry is `[start, end, speed]` in source seconds. Do it in **one** ffmpeg `filter_complex` pass:
   - per segment, `trim`/`atrim`, then `setpts=(PTS-STARTPTS)/speed` and `atempo=speed`, cut to the frame-rounded duration
   - `concat=v=1:a=1`, then `loudnorm=I=-16`, at 30 fps

   Save the result here as `avatar.mp4`. Joining separately encoded segments with `-c copy` drifts the audio by about 0.1 s, so don't do that.
2. Run `npx hyperframes@0.8.221 render …` in step 4.
3. From `project/`, run `python3 build.py . owords.json ../osm_places.json`. `owords.json` holds the word timings already remapped to the edited track.
4. Run `npx hyperframes render -q delivery -f 30`. Then apply `volume=-2.5dB` to bring the output to −16 LUFS.
