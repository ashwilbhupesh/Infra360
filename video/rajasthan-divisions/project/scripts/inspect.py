import json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from shapely.geometry import shape
R='/home/user/work/rajdiv/'
fig,axs=plt.subplots(1,2,figsize=(20,10))
for ax,bb in zip(axs,[(73.3,75.3,25.3,26.8),(75.6,77.2,27.3,28.3)]):
    for f in json.load(open(R+'raw/gb/raj_tehsils.geojson'))['features']:
        g=shape(f['geometry']); 
        for p in (g.geoms if hasattr(g,'geoms') else [g]):
            x,y=p.exterior.xy; ax.plot(x,y,'k-',lw=.4)
        c=g.representative_point()
        if bb[0]<c.x<bb[1] and bb[2]<c.y<bb[3]: ax.text(c.x,c.y,f['properties']['shapeName']+'\n'+f['properties']['dt'],fontsize=7,ha='center')
    for f in json.load(open(R+'data/rajasthan_districts.geojson'))['features']:
        g=shape(f['geometry'])
        for p in (g.geoms if hasattr(g,'geoms') else [g]):
            x,y=p.exterior.xy; ax.fill(x,y,alpha=.3); ax.plot(x,y,'r-',lw=1.2)
    ax.set_xlim(bb[0],bb[1]); ax.set_ylim(bb[2],bb[3])
plt.savefig(R+'raw/inspect.png',dpi=80)
