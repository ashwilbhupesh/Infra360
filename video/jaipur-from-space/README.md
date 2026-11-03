# Jaipur from space: 1989 → 2024, prices then and now
`Jaipur_From_Space_TEXT.mp4`: 1080×1920, 70.5 s, about −16 LUFS. This is the **text-led version**; Ashwil's Hinglish voice-over will be added later. `cover_frame.jpg` is the Instagram cover in the Ajmer Road style: a 1989 | 2024 split of the whole city with "Land that cost ₹50 a gaj now costs ₹50,000+".

## Flow
| Time (s) | Section |
|---|---|
| 0 | Cover |
| 0.6 | SAVE / SHARE prompts. **Hook on the whole city:** 1989 satellite with "₹50–300 per gaj, 1990". A wipe reveals 2024, the price flips to "₹40,000–1.5 lakh", then pins with each area's multiplier pop across the city. |
| 7.4 | Old photos: 1890s archive, black-and-white street, old bazaar, Hawa Mahal 2002, Ramganj Bazaar ~2010, World Trade Park construction, Tholia House today. |
| 17.3 | City time-lapse: 1989 → 2000 → 2010 → 2024 (Landsat), with area pins on 2024. |
| 27.6 | 10 areas, each a 1989 → 2024 wipe of the same spot with price ₹/sq yd and multiplier. Jagatpura opens with the 150-gaj plot story (₹10,000 → ~₹1.17 crore counter, house builds, cash stacks). |
| 55 | What's next: Ring Road, Pink Line and Phase 2 Orange Line draw on the region map. Labelled "Projection · approved & announced projects". |
| 61.5 | Call to action: "Where's the next Jagatpura? Comment your answer", plus save and share. |
| 66 | Credits, sources and disclaimer. |

Text sits on translucent dark boxes for readability, and the fine print is kept clear of the captions.

## Revision 2 (slower, focused)
- Hook: a whole-Jaipur slider. 1989 full screen (0.5 s) → the slider stops at the middle showing 1989 | 2024 side by side (2.6–5.4 s) → full 2024 with the price flip ₹50–300 → ₹40,000–1.5 lakh per gaj and "Up to ~1,200× more" (to 8.9 s).
- Removed the old-photos montage and the city time-lapse (too much, too fast).
- Area scans are now 4 s each, Jagatpura 7 s: slower 1.4 s wipe, then price, then multiplier, one at a time. Runtime is 67.7 s.

## Prices
Supplied by Ashwil (ranges compiled with ChatGPT). The video shows the **mid-points** of each range:

| Area | 1990 (₹/sq yd) | Today (₹/sq yd) | Multiplier |
|---|---|---|---|
| Jagatpura | 65 | 77,500 | ~1,200× |
| Mansarovar | 175 | 1 lakh | ~570× |
| Vaishali Nagar | 260 | 1.5 lakh | ~580× |
| Sitapura | 50 | 57,500 | ~1,200× |
| Pratap Nagar | 95 | 75,000 | ~790× |
| Jhotwara | 200 | 70,000 | ~350× |
| Ajmer Road | 60 | 42,500 | ~710× |
| Vidyadhar Nagar | 200 | 1.25 lakh | ~620× |
| Sikar Road | 60 | 55,000 | ~920× |
| Malviya Nagar | 300 | 1.5 lakh | ~500× |

**Credits shown on screen:** MagicBricks; Housing.com; Rajasthan Registration & Stamps Dept (DLC); Rajasthan GIS Portal; Kapil Raisinghani.

**Disclaimer shown on screen:** prices are estimates or indicative; multipliers are calculated, not verified returns.

## Imagery
- **Landsat, courtesy NASA/USGS:** Landsat 5 (12 Dec 1989, 6 Dec 2010), Landsat 7 (2 Dec 2000), Landsat 9 (4 Dec 2024). Downloaded from Microsoft Planetary Computer; see `fetch.py`.
- **Sentinel-2 (2024):** used for the sharp area "after" images ("Contains modified Copernicus Sentinel-2 data").
- **Same-spot comparisons:** the 1989 frames are histogram-matched to the 2024 colours. The 1989 images are softer because Landsat 5 is 30 m resolution.
- **Photos:** supplied. The 1890s photo is an archive image with its labels removed. The World Trade Park photo keeps its © credit. AI "vintage" images and a branded Mansarovar graphic were not used.
