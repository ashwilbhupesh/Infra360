import json, math
def rings(f):
    rel=json.load(open(f))["elements"][0]
    segs=[[(p["lat"],p["lon"]) for p in m["geometry"]] for m in rel["members"] if m["type"]=="way" and m.get("role")=="outer" and m.get("geometry")]
    out=[]
    while segs:
        r=segs.pop(0)
        while True:
            if r[0]==r[-1] and len(r)>3: break
            for i,s in enumerate(segs):
                if s[0]==r[-1]: r+=s[1:]; segs.pop(i); break
                if s[-1]==r[-1]: r+=s[::-1][1:]; segs.pop(i); break
            else: break
        out.append(r)
    return out
def km(r,lat0,lon0):
    return [((lon-lon0)*111.32*math.cos(math.radians(lat0)), (lat0-lat)*110.57) for lat,lon in r]
def area(p): return abs(sum(p[i][0]*p[i-1][1]-p[i-1][0]*p[i][1] for i in range(len(p))))/2
res={}
for nm in ("delhi","goa"):
    R=rings(f"osm/{nm}.json"); R.sort(key=len,reverse=True)
    lat0=sum(p[0] for p in R[0])/len(R[0]); lon0=sum(p[1] for p in R[0])/len(R[0])
    K=[km(r,lat0,lon0) for r in R]; A=[area(k) for k in K]
    print(nm,len(R),[round(a) for a in A[:5]], round(sum(A)))
    keep=[k for k,a in zip(K,A) if a>5]
    # thin
    res[nm]=[k[::max(1,len(k)//400)] for k in keep]
json.dump(res,open("outlines_km.json","w"))
