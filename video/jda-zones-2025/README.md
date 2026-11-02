# JDA zones 2025: "Jaipur is now bigger than Goa"
`JDA_Zones_2025.mp4` (1080×1920, 99.6 s, −16 LUFS, lip-sync offset 0 ms). It has Ashwil's voice-over and verbatim captions (`JDA_Zones_2025.srt`).

**Cover:** `cover_frame.jpg` is a sleek editorial cover (it is also frame 0 of the video, 0–0.55 s): a dark satellite image, the JDA region drawn in a fine gold line, the serif headline "Jaipur, redrawn.", and "27 zones · 5,994 sq km · now larger than Goa".

**Edits:**
- Ashwil's face is shown only for the opening line "Jaipur is now bigger than Goa…", which then dissolves into the map.
- Every beat is cued to his words. The outer zones light up as each town is named; Mozmabad (not spoken) lights up together with Dudu.
- The approval card was softened to "Check the scheme's approval" (the spoken line stays verbatim in the captions).

**Round 3:**
- Cut the line "and your plot zone may have just changed" (original recording 2.70–5.45 s). The avatar is now three segments: 0.35–2.70, 5.45–35.50 and 42.20–106.6 s, 96.8 s in total.
- Music: `music_tune.mp3` is an original piano-pop groove composed in code (`music/compose.py`, D major, 100 BPM, I–V–vi–IV). It is fully owned, with no licence restrictions. Volume 0.22 under the voice.
- Cover redone in the Ajmer Road style: dark brown background with a dot grid, "JDA / ZONES" in cream and amber, the region in a glowing amber outline with town tags, and a "14 → 27 zones · 5,994 sq km" pill.

**Round 2:**
- At "four times Delhi", 4 true-scale Delhi NCT outlines (OSM relation 1942586, 1,477 sq km measured) tile across the JDA region.
- At "bigger than all of Goa", a true-scale Goa outline (OSM, 3,633 sq km measured) is laid over it. Both are projected in km at Jaipur's latitude.
- Zones 1–9 flash yellow one by one at "1 to 9", and the PRN zones flash at "Prithviraj Nagar".
- The JDA site plan (Riyasat Town, Chaksu, Zone 14; supplied) appears at "patta", and the supplied 90-A graphic at "90-A conversion".

**Caption fixes:** GD→JDA, Pithfirajnagar→Prithviraj Nagar, "Add the map"→"Add them up", Telhi→Delhi, "Jaipurino"→"Jaipur you know", "2 kilometers"→"2 sq km", the town names (Shahpura, Jalsoo, Dudu, Phagi, Madhorajpura, Chaksu, Bassi, Toonga), JDNR→"JDA now", "90"→"90-A", Jagarpura→Jagatpura, Vishali→Vaishali.

## Earlier text-only version (beats below were retimed to the voice)

## Story beats
| Time (s) | Beat |
|---|---|
| 0–3.2 | Hook "JAIPUR IS NOW BIGGER THAN GOA". The region outline draws on and the zones flash. "Your plot's zone may have changed." |
| 3.2 | JDA office order dated 10 Oct 2025, with the JDA building photo. |
| 6.6 | "Before: 14 zones", shown on the old zone map. |
| 9.6 | Counter goes 14→27 while the zones pop in one by one, centre outwards. "25 zones + Prithviraj Nagar North & South." |
| 16.4 | Area bars: JDA region 5,994 sq km (the sum of the official table), Goa 3,702, Delhi NCT 1,484. "4× Delhi." |
| 23 | Zoom to the core: "Zones 1–9 + PRN". Zone 3 is 2 sq km. |
| 30 | Zone 13 (Amer & Jamwaramgarh) is the biggest at 596 sq km. |
| 34 | The new frontier: zones 15–25 light up with their tehsil names. |
| 41.5 | Dainik Bhaskar clipping: Master Plan 2047, 272 villages could join. |
| 45.5 | "Why should you care?" ① approval (with a scheme layout), ② 90-A conversion, ③ zone and master-plan rules. |
| 56.6 | Quiz: "Jagatpura / Vaishali Nagar / Mansarovar / Tonk Road → Zone ?" |
| 63 | Call to action: "Comment your area — I'll tell you your zone", plus the share icon "Send to someone buying a plot". |

## How the map was made
- **Fitting the zone map:** the official JDA map (office order dated 10.10.2025) was fitted to Web-Mercator. An affine fit was seeded from town points and then optimised (`fit.py`) by matching the map's highways to OSM motorway and trunk lines. Expect an error of roughly 1–2 km.
- **Zone shapes:** each zone was extracted by colour segmentation (`zones2.py`). The measured areas of the outer zones match the official table to within about 5%. Zones 3 and PRN N were traced by hand.
- **Labels:** zone boundaries are shown as approximate, and the on-screen credit says so.

## Assets
| Asset | Source |
|---|---|
| Satellite | Sentinel-2 cloudless 2016 by EOX (CC BY 4.0). The 2016 layer was chosen because its licence allows commercial use; later layers are NC. |
| Zone maps (2025 and old) | JDA, supplied by Ashwil |
| JDA building, Bhaskar clipping, Jagatpura, Vaishali Nagar, Tonk Road | Image supplied |
| Mansarovar | Pacific Jaipur, supplied; labelled on screen as a rendering |
| Scheme layout | Supplied. Cropped to remove the developer logo, RERA number and QR code. |
| Music | Original synthesized pad, same as the earlier reels |
| SFX | Bundled with HyperFrames (Pixabay Content License) |
| Fonts | Inter and JetBrains Mono (OFL) |

## Not used
- Composite "Jagatpura" image: Hawa Mahal was pasted next to a metro station.
- "Vidyadhar Nagar" photo: it is actually the University of Rajasthan.
- Jodhpur JDA plot plan: it is not from Jaipur.
- PinkWalk rendering.

## Fact-check before posting
- Goa area 3,702 sq km and Delhi area 1,484 sq km (standard official figures).
- "Before: 14 zones" comes from the old supplied map.
- The 272-village figure is attributed to Dainik Bhaskar's report.
