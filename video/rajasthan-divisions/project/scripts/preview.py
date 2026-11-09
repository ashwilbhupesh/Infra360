import json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from shapely.geometry import shape
from shapely.ops import unary_union
R='/home/user/work/rajdiv/'
D=json.load(open(R+'data/rajasthan_districts.geojson'))['features']
V=json.load(open(R+'data/divisions.geojson'))['features']
COL={'Jaipur':'#e8a33d','Jodhpur':'#d9534f','Ajmer':'#8e6cc0','Udaipur':'#3fa36b','Kota':'#3b82c4','Bikaner':'#c9b458','Bharatpur':'#e07bb0'}
fig,ax=plt.subplots(figsize=(12,12),dpi=110)
def polys(g): return list(g.geoms) if hasattr(g,'geoms') else [g]
for f in D:
    g=shape(f['geometry']); p=f['properties']
    for q in polys(g):
        x,y=q.exterior.xy; ax.fill(x,y,fc=COL[p['division']],ec='white',lw=0.8,alpha=0.85 if not p['new_2023'] else 1.0, hatch='..' if p['new_2023'] else None)
    cx,cy=p['label']
    ax.text(cx,cy,p['district'],fontsize=7.2,ha='center',va='center',color='black',fontweight='bold' if p['new_2023'] else 'normal')
for f in V:
    for q in polys(shape(f['geometry'])):
        x,y=q.exterior.xy; ax.plot(x,y,color='black',lw=1.8)
ax.legend(handles=[Patch(fc=c,label=f"{k} ({sum(1 for f in D if f['properties']['division']==k)})") for k,c in COL.items()]+[Patch(fc='white',ec='k',hatch='..',label='2023 district (retained)')],loc='upper left',fontsize=9,title=f'Rajasthan: 7 divisions, {len(D)} districts')
ax.set_aspect(1/0.9); ax.axis('off')
ax.set_title('Rajasthan districts by division (approx. boundaries; new districts built from 2018 tehsils)',fontsize=11)
plt.savefig(R+'preview.png',bbox_inches='tight')
gs=[shape(f['geometry']) for f in D]; u=unary_union(gs)
print('sum',round(sum(g.area for g in gs),4),'union',round(u.area,4))
