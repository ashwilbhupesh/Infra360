import json, glob, math, numpy as np, cv2
from scipy.optimize import minimize
def merc(lat,lon):
    n=256*2**11; return ((lon+180)/360*n, (1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n)
D="/home/user/Infra360/video/delhi-mumbai-expressway/project/osm/"
pts=[]
for f in glob.glob(D+"major_*.json"):
    for e in json.load(open(f)).get("elements",[]):
        t=e.get("tags",{})
        if t.get("highway") in ("motorway","trunk") and e.get("geometry"):
            g=e["geometry"]
            for a,b in zip(g,g[1:]):
                for s in np.linspace(0,1,4,endpoint=False):
                    la=a["lat"]+(b["lat"]-a["lat"])*s; lo=a["lon"]+(b["lon"]-a["lon"])*s
                    if 26.35<la<27.65 and 75.0<lo<76.45: pts.append(merc(la,lo))
pts=np.array(pts); print(len(pts))
im=cv2.imread("supplied/zones_2025.jpg")[:1840]
g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY); dark=(g<70).astype(np.uint8)
dt=cv2.distanceTransform(1-dark,cv2.DIST_L2,3)
A=np.array(json.load(open('affine.json'))["merc2px"])
S=np.array([[1e-2,1e-2],[1e-2,1e-2],[1,1]])
def mk(p): return A+p.reshape(3,2)*S
def cost(p):
    q=np.c_[pts,np.ones(len(pts))]@mk(p)
    ok=(q[:,0]>0)&(q[:,0]<1753)&(q[:,1]>70)&(q[:,1]<1839)
    if ok.sum()<100: return 50.0
    d=dt[q[ok,1].astype(int),q[ok,0].astype(int)]
    return np.mean(np.minimum(d,25)) + (1-ok.mean())*25
x=np.zeros(6); print("start",cost(x))
for sc in (1,):
    r=minimize(cost,x,method="Powell",options={"maxiter":20000,"xtol":1e-3,"ftol":1e-5}); x=r.x; print("fit",r.fun)
a=mk(x); json.dump({"merc2px":a.tolist()},open('affine_fit.json','w'))
q=(np.c_[pts,np.ones(len(pts))]@a).astype(int)
for X,Y in q:
    if 0<X<1754 and 0<Y<1840: cv2.circle(im,(X,Y),2,(0,0,255),-1)
cv2.imwrite('fitcheck.jpg',cv2.resize(im,(877,920)))
