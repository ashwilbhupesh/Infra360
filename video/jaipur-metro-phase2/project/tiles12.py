import math, urllib.request, os, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
def t(lat,lon,z):
    n=2**z; return int((lon+180)/360*n), int((1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n)
def get(z,x,y):
    f=f"tiles/{z}_{x}_{y}.jpg"
    if os.path.exists(f): return
    u=f"https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/g/{z}/{y}/{x}.jpg"
    for i in range(4):
        try: open(f,"wb").write(urllib.request.urlopen(u,timeout=30).read()); return
        except Exception as e: err=e
    print("fail",z,x,y,err)
def stitch(z,lat0,lon0,lat1,lon1,out):
    x0,y0=t(lat1,lon0,z); x1,y1=t(lat0,lon1,z)
    with ThreadPoolExecutor(8) as ex: list(ex.map(lambda p:get(z,*p),[(x,y) for x in range(x0,x1+1) for y in range(y0,y1+1)]))
    im=Image.new("RGB",((x1-x0+1)*256,(y1-y0+1)*256))
    for x in range(x0,x1+1):
        for y in range(y0,y1+1):
            try: im.paste(Image.open(f"tiles/{z}_{x}_{y}.jpg"),((x-x0)*256,(y-y0)*256))
            except Exception: pass
    im.save(out,quality=88); print(out,x0,y0,im.size)
stitch(12,26.40,75.45,27.30,76.15,"s2_z12.jpg")

