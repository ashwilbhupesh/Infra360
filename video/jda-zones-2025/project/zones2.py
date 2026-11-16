import cv2, numpy as np, json
im=cv2.imread("supplied/zones_2025.jpg")[:1840]
lab=cv2.cvtColor(im,cv2.COLOR_BGR2LAB).astype(np.float32)
SEED=json.load(open("zones_px.json")); SEED={k:v["seed"] for k,v in SEED.items()}
L=lab[...,0]; chroma=np.hypot(lab[...,1]-128,lab[...,2]-128)
wild=(chroma<10)&(L<215)            # black/grey lines & text
C={}
for k,(x,y) in SEED.items():
    win=lab[y-6:y+7,x-6:x+7].reshape(-1,3); ok=~wild[y-6:y+7,x-6:x+7].reshape(-1)
    C[k]=np.median(win[ok],0)
keys=list(C); P=np.array([C[k] for k in keys])
dist=np.stack([np.linalg.norm(lab-p,axis=2) for p in P],0)
nearest=dist.argmin(0); dmin=dist.min(0)
out={}; vis=im.copy()
for i,k in enumerate(keys):
    x,y=SEED[k]
    m=((nearest==i)&(dmin<20)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(13,13)))
    if k in ("3","PRN N","7"):
        w=np.zeros_like(m); w[y-120:y+120,x-120:x+120]=1; m=m*w
        m=cv2.morphologyEx(((nearest==i)&(dmin<20)).astype(np.uint8)*w,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,cc=cv2.connectedComponents(m)
    lbl=cc[y,x]
    if lbl==0:
        w=cc[y-15:y+16,x-15:x+16].ravel(); w=w[w>0]; lbl=np.bincount(w).argmax() if len(w) else 0
    comp=(cc==lbl).astype(np.uint8)
    comp=cv2.morphologyEx(comp,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    cs,_=cv2.findContours(comp,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cm=max(cs,key=cv2.contourArea)
    out[k]={"poly":cv2.approxPolyDP(cm,2.0,True)[:,0].tolist(),"area_px":float(cv2.contourArea(cm)),"seed":[x,y]}
    col=tuple(int(v) for v in np.random.RandomState(i*7+3).randint(0,200,3))
    cv2.polylines(vis,[np.array(out[k]["poly"])],True,col,3); cv2.putText(vis,k,(x,y),0,1,(0,0,0),3)
json.dump(out,open("zones_px.json","w"))
cv2.imwrite("zonecheck.jpg",cv2.resize(vis,(877,920)))
T={"1":30,"2":118,"3":2,"4":18,"5":26,"6":34,"7":35,"8":47,"9":80,"10":320,"11":286,"12":364,"13":596,"14":273,"PRN N":14,"PRN S":13,"15":364,"16":317,"17":436,"18":385,"19":221,"20":350,"21":314,"22":370,"23":365,"24":326,"25":290}
r=[out[k]["area_px"]/T[k] for k in keys]; med=np.median(r)
for k,v in zip(keys,r): print(k, round(v/med,2), end=" | ")
