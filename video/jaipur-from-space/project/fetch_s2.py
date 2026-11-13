import json, urllib.request, numpy as np, rasterio
from rasterio.warp import transform_bounds, reproject, Resampling
from rasterio.windows import from_bounds
from PIL import Image
tok=json.load(urllib.request.urlopen("https://planetarycomputer.microsoft.com/api/sas/v1/token/sentinel-2-l2a",timeout=60))["token"]
F=[f for f in json.load(open("s2_scenes.json")) if f["id"].startswith("S2A_MSIL2A_20241209")][0]
BB=(75.62,26.72,76.00,27.06); out={}
for b in ("B04","B03","B02"):
    with rasterio.open(F["assets"][b]["href"]+"?"+tok) as src:
        bb=transform_bounds("EPSG:4326",src.crs,*BB); w=from_bounds(*bb,src.transform)
        out[b]=src.read(1,window=w).astype(np.float32); tr=src.window_transform(w); crs=src.crs.to_string()
np.savez_compressed("s2_2024.npz",R=out["B04"],G=out["B03"],B=out["B02"],crs=crs,tr=np.array(tr)[:6])
print(out["B04"].shape, crs)
