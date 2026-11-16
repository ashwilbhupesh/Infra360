import json, urllib.request, numpy as np, rasterio
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds
from PIL import Image
tok=json.load(urllib.request.urlopen("https://planetarycomputer.microsoft.com/api/sas/v1/token/landsat-c2-l2",timeout=60))["token"]
BB=(75.62,26.72,76.00,27.06)   # lon/lat box around Jaipur
PICK={1989:"LT05_L2SP_147041_19891212_02_T1",2000:"LE07_L2SP_147041_20001202_02_T1",2010:"LT05_L2SP_147041_20101206_02_T1",2025:"LC09_L2SP_147041_20241204_02_T1"}
for yr,sid in [(2025,PICK[2025])]:
    F=json.load(open(f"scenes_{yr}.json")); f=[x for x in F if x["id"]==sid][0]; A=f["assets"]
    bands=[]
    for b in ("red","green","blue","nir08","swir16"):
        href=A[b]["href"]+"?"+tok
        with rasterio.open(href) as src:
            bb=transform_bounds("EPSG:4326",src.crs,*BB); w=from_bounds(*bb,src.transform)
            arr=src.read(1,window=w).astype(np.float32)
            if b=="red": prof=(src.crs.to_string(),src.window_transform(w))
        bands.append(arr*0.0000275-0.2)
    R,G,B,N,S=bands
    np.savez_compressed(f"ls_{yr}.npz",R=R,G=G,B=B,N=N,S=S,crs=prof[0],tr=np.array(prof[1])[:6])
    rgb=np.dstack([R,G,B]); lo,hi=np.percentile(rgb[rgb>0],(2,98)); img=np.clip((rgb-lo)/(hi-lo),0,1)**0.85
    Image.fromarray((img*255).astype(np.uint8)).save(f"ls_{yr}.png"); print(yr,R.shape)
