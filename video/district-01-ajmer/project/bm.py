import math, urllib.request, os
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
L="BlueMarble_NextGeneration"
def t(lat,lon,z):
    n=2**z; return int((lon+180)/360*n), int((1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n)
def get(z,x,y):
    f=f"/home/user/work/ajmer/tiles_bm/{z}_{x}_{y}.jpg"
    if os.path.exists(f): return
    u=f"https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/{L}/default/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpeg"
    for i in range(4):
        try: open(f,"wb").write(urllib.request.urlopen(u,timeout=30).read()); return
        except Exception as e: err=e
    print("fail",z,x,y,err)
def stitch(z,lat0,lon0,lat1,lon1,out):
    x0,y0=t(lat1,lon0,z); x1,y1=t(lat0,lon1,z)
    with ThreadPoolExecutor(8) as ex: list(ex.map(lambda p:get(z,*p),[(x,y) for x in range(x0,x1+1) for y in range(y0,y1+1)]))
    im=Image.new("RGB",((x1-x0+1)*256,(y1-y0+1)*256))
    for x in range(x0,x1+1):
        for y in range(y0,y1+1): im.paste(Image.open(f"/home/user/work/ajmer/tiles_bm/{z}_{x}_{y}.jpg"),((x-x0)*256,(y-y0)*256))
    im.save(out,quality=90); print(out,x0,y0,im.size)
stitch(4,-25,25,62,135,"bm4.jpg")
