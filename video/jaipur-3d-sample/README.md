# Jaipur 3D sample: land-price bars on real terrain
`Jaipur_3D_Sample.mp4` is a 15 s, 1080×1920 test of the 3D look.

## How it's built
- **Engine:** Three.js 0.160 inside HyperFrames, drawn from timeline time in the `hf-seek` listener. The render is deterministic.
- **Terrain:** Copernicus DEM GLO-30, resampled to 60 m. Height is exaggerated ×4.
- **Imagery:** Sentinel-2, 9 Dec 2024, draped over the terrain.
- **Bars:** one per area, height proportional to its price multiplier (from `../jaipur-from-space/project/areas.json`), coloured yellow to red. HTML labels are projected from the 3D position of each bar.
- **Camera:** an overview descent, then stops at Jagatpura, Mansarovar and Vaishali Nagar.
- **Render:** uses a software GPU, roughly 20–30 min for 15 s.

## Not committed (size)
`assets/tex.jpg` and `assets/dem.png`. Rebuild them from the Sentinel-2 / DEM `npz` files in `../jaipur-from-space/project` using the prep steps in this session's work folder.
