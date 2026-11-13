import numpy as np, json, math, glob
from PIL import Image, ImageFilter, ImageEnhance
from rasterio.warp import transform as rtx
D="proj/assets/img/"
L={y:np.load(f"ls_{y}.npz") for y in (1989,2000,2010,2025)}
S=np.load("s2_2024.npz"); BIG=np.load("ls_big_2024.npz"); CRS=str(S["crs"])
def utm(la,lo): x,y=rtx("EPSG:4326",CRS,[lo],[la]); return x[0],y[0]
def match(src,ref):
    s=src.ravel(); r=np.sort(ref.ravel()[::7]); q=np.argsort(s); o=np.empty_like(s); o[q]=r[np.linspace(0,len(r)-1,len(s)).astype(int)]; return o.reshape(src.shape)
s2=np.dstack([S["R"],S["G"],S["B"]]); lo,hi=np.percentile(s2[s2>0],(1,99.3))
def stretch(a): return (np.clip((a-lo)/(hi-lo),0,1)**0.9*255).astype(np.uint8)
LM={y:np.dstack([match(L[y][k],s2[...,i]) for i,k in enumerate("RGB")]) for y in L}
def crop(arr,tr,x,y,res,halfw_m):
    c=(x-tr[2])/tr[0]; r=(y-tr[5])/tr[4]; hw=halfw_m/res; hh=hw*16/9
    return arr[int(r-hh):int(r+hh), int(c-hw):int(c+hw)]
def out(a,name,sharp=True):
    im=Image.fromarray(stretch(a)).resize((1080,1920),Image.LANCZOS)
    if sharp: im=im.filter(ImageFilter.UnsharpMask(2,60,2))
    im.save(D+name,quality=88)
# 1 · city-wide time-lapse (centre on Jaipur)
cx,cy=utm(26.885,75.800)
for y in L: out(crop(LM[y],L[y]["tr"],cx,cy,30,9500),f"city_{y}.jpg")
# 2 · areas
A=json.load(open("areas.json"))
for a in A:
    x,y=utm(a["lat"],a["lon"])
    out(crop(LM[1989],L[1989]["tr"],x,y,30,2400),f"a_{a['k']}_1989.jpg")
    out(crop(s2,S["tr"],x,y,10,2400),f"a_{a['k']}_2024.jpg")
# 3 · big region 2024 + pixel transform for overlays
big=np.dstack([match(BIG[k],s2[...,i]) for i,k in enumerate("RGB")])
bx,by=utm(26.925,75.80); HW=17500
c=(bx-BIG["tr"][2])/BIG["tr"][0]; r=(by-BIG["tr"][5])/BIG["tr"][4]; hw=HW/60; hh=hw*16/9
r0=int(r-hh); c0=int(c-hw); sub=big[max(0,r0):int(r+hh), max(0,c0):int(c+hw)]
pad=np.zeros((int(2*hh)+4,int(2*hw)+4,3),np.float32); pad[max(0,-r0):max(0,-r0)+sub.shape[0], max(0,-c0):max(0,-c0)+sub.shape[1]]=sub
pad=pad[:int(2*hh),:int(2*hw)]; im=Image.fromarray(stretch(pad)).resize((1080,1920),Image.LANCZOS); im=ImageEnhance.Brightness(im).enhance(0.75); im.save(D+"region_2024.jpg",quality=86)
sx=1080/(2*hw); sy=1920/(2*hh)
def bigpx(la,lo):
    x,y=utm(la,lo); return ((( x-BIG["tr"][2])/BIG["tr"][0]-c0)*sx, ((y-BIG["tr"][5])/BIG["tr"][4]-r0)*sy)
def citypx(la,lo):
    x,y=utm(la,lo); return ((x-cx)/30/(9500/30)*540+540, (y-cy)/-30/(9500/30*16/9)*960+960)
# overlays (lat/lon sources)
pink=[]
for e in json.load(open("/home/user/work/plan/osm/metro.json"))["elements"]:
    if e.get("geometry") and e["tags"].get("name")=="Pink Line (Jaipur Metro)": pink.append([(g["lat"],g["lon"]) for g in e["geometry"]])
OST=[(26.7389,75.8647),(26.7854,75.8223),(26.7992,75.8119),(26.8060,75.8067),(26.8121,75.8021),(26.8262,75.7984),(26.8385,75.7939),(26.8465,75.7942),(26.8573,75.7953),(26.8650,75.7964),(26.8710,75.7971),(26.8790,75.7989),(26.8948,75.8087),(26.8996,75.8125),(26.9050,75.8148),(26.9134,75.8110),(26.9171,75.8004),(26.9265,75.7922),(26.9345,75.7940),(26.9380,75.7866),(26.93973,75.7778)]
rd=json.load(open("/home/user/work/metro/roads.json")); SK=sorted([p for p in rd["sikar"] if 26.9397<=p[0]<=26.985 and p[1]<75.785])[::6]
ring=[]
for f in glob.glob("/home/user/Infra360/video/jaipur-ajmer-road/project/osm/major_*.json"):
    for e in json.load(open(f)).get("elements",[]):
        t=e.get("tags",{})
        if (t.get("ref")=="ORR" or "outer ring road" in (t.get("name") or "").lower()) and e.get("geometry"): ring.append([(g["lat"],g["lon"]) for g in e["geometry"]][::2])
# JDA region (world z11 px, origin tile 1450,859) -> lat/lon
import sys; sys.argv=["x"]
src=open("/home/user/work/jda/build.py").read().split("def pd(")[0]
g={}; import os; cwd=os.getcwd(); os.chdir("/home/user/work/jda"); exec(src,g); os.chdir(cwd)
def w2ll(p):
    n=256*2**11; X=p[0]+1450*256; Y=p[1]+859*256
    lon=X/n*360-180; lat=math.degrees(math.atan(math.sinh(math.pi*(1-2*Y/n)))); return (lat,lon)
region=[w2ll(p) for p in g["REGION"]]
def P(f,pts): return [tuple(round(v,1) for v in f(*q)) for q in pts]
json.dump({"pink":[P(bigpx,s) for s in pink],"orange":P(bigpx,OST),"todi":P(bigpx,[OST[-1]]+SK),"ring":[P(bigpx,s) for s in ring],"region":P(bigpx,region),
           "city_pink":[P(citypx,s) for s in pink]},open("overlays.json","w"))
print("ok")
# area pins on the city time-lapse frame
pins=[{"name":a["name"].split(" ·")[0],"xy":citypx(a["lat"],a["lon"])} for a in A]
o=json.load(open("overlays.json")); o["pins"]=pins; json.dump(o,open("overlays.json","w"))
print(pins)
