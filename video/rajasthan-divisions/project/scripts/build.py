"""Build current (2026) 41-district Rajasthan GeoJSON from geoBoundaries IND ADM2 (2021, pre-2023 33 districts)
+ ADM3 (2018 tehsils) for carving the 8 surviving 2023 districts."""
import json, sys
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
R='/home/user/work/rajdiv/'
d33=json.load(open(R+'raw/gb/raj_33.geojson'))['features']
teh=json.load(open(R+'raw/gb/raj_tehsils.geojson'))['features']
NAME={'Chittaurgarh':'Chittorgarh','Dhaulpur':'Dholpur','Ganganagar':'Sri Ganganagar','Jalor':'Jalore','Jhunjhunun':'Jhunjhunu'}
# new district -> list of (parent ADM2 name, 2018 tehsil name)
NEW={
 'Balotra':[('Barmer',t) for t in ['Pachpadra','Siwana','Samdari','Sindhari','Gida','Gudha Malani','Dhorimanna']],
 'Phalodi':[('Jodhpur',t) for t in ['Phalodi','Bap','Bapini','Lohawat','Dechu']],
 'Didwana-Kuchaman':[('Nagaur',t) for t in ['Didwana','Ladnu','Makrana','Parbatsar','Nawa','Kuchaman City']],
 'Beawar':[('Ajmer','Beawar'),('Ajmer','Masuda'),('Ajmer','Vijaynagar'),('Ajmer','Tatgarh'),('Pali','Jaitaran'),('Pali','Raipur'),('Bhilwara','Badnor')],
 'Kotputli-Behror':[('Jaipur','Kotputli'),('Jaipur','Viratnagar'),('Jaipur','Pavta'),('Alwar','Behror'),('Alwar','Neemrana'),('Alwar','Bansur'),('Alwar','Narayanpur')],
 'Khairthal-Tijara':[('Alwar',t) for t in ['Tijara','Kishangarh Bas','Kotkasim','Mandawar']],
 'Deeg':[('Bharatpur',t) for t in ['Deeg','Kaman','Kumher','Nagar','Pahari','Sikri']],
 'Salumber':[('Udaipur',t) for t in ['Salumbar','Sarada','Semari','Lasadiya']],
}
DIV={'Jaipur':['Jaipur','Dausa','Alwar','Jhunjhunu','Sikar','Kotputli-Behror','Khairthal-Tijara'],
 'Jodhpur':['Jodhpur','Phalodi','Barmer','Balotra','Jaisalmer','Jalore','Sirohi','Pali'],
 'Ajmer':['Ajmer','Beawar','Bhilwara','Nagaur','Didwana-Kuchaman','Tonk'],
 'Udaipur':['Udaipur','Salumber','Rajsamand','Chittorgarh','Pratapgarh','Banswara','Dungarpur'],
 'Kota':['Kota','Bundi','Baran','Jhalawar'],
 'Bikaner':['Bikaner','Churu','Sri Ganganagar','Hanumangarh'],
 'Bharatpur':['Bharatpur','Deeg','Dholpur','Karauli','Sawai Madhopur']}
D2V={d:v for v,ds in DIV.items() for d in ds}
geo={NAME.get(f['properties']['shapeName'],f['properties']['shapeName']):shape(f['geometry']).buffer(0) for f in d33}
tix={(f['properties']['dt'],f['properties']['shapeName']):shape(f['geometry']).buffer(0) for f in teh}
for nd,parts in NEW.items():
    pieces=[]
    for p,t in parts:
        g=tix[(p,t)]; pn=NAME.get(p,p)
        g=g.intersection(geo[pn])            # keep inside parent ADM2
        geo[pn]=geo[pn].difference(g); pieces.append(g)
    geo[nd]=unary_union([p.buffer(5e-4) for p in pieces]).buffer(-5e-4)
# clean slivers: drop tiny polygon parts
from shapely.geometry import MultiPolygon, Polygon
def clean(g, frac=0.002):
    def flat(x):
        if x.geom_type=='Polygon': return [x]
        if hasattr(x,'geoms'): return [p for y in x.geoms for p in flat(y)]
        return []
    ps=flat(g)
    big=max(p.area for p in ps)
    ps=[p for p in ps if p.area>=frac*big]
    return ps[0] if len(ps)==1 else MultiPolygon(ps)
geo={k:clean(v) for k,v in geo.items()}
assert len(geo)==41 and set(geo)==set(D2V), set(geo)^set(D2V)
from shapely.ops import polylabel
def lab(g):
    m=max(g.geoms,key=lambda p:p.area) if hasattr(g,'geoms') else g
    p=polylabel(m,0.005); return [round(p.x,4),round(p.y,4)]
fs=[{'type':'Feature','properties':{'district':k,'division':D2V[k],'new_2023':k in NEW,'label':lab(v)},'geometry':mapping(v.simplify(0.001))} for k,v in sorted(geo.items(),key=lambda kv:(D2V[kv[0]],kv[0]))]
json.dump({'type':'FeatureCollection','features':fs},open(R+'data/rajasthan_districts.geojson','w'))
dv=[{'type':'Feature','properties':{'division':v,'districts':ds,'n_districts':len(ds)},'geometry':mapping(clean(unary_union([geo[d].buffer(0.002) for d in ds]).buffer(-0.002)).simplify(0.002))} for v,ds in DIV.items()]
json.dump({'type':'FeatureCollection','features':dv},open(R+'data/divisions.geojson','w'))
st=clean(unary_union([g.buffer(0.002) for g in geo.values()]).buffer(-0.002))
json.dump({'type':'FeatureCollection','features':[{'type':'Feature','properties':{'name':'Rajasthan'},'geometry':mapping(st.simplify(0.002))}]},open(R+'data/rajasthan_outline.geojson','w'))
for k,v in sorted(geo.items()): print(f"{k:18s} {D2V[k]:10s} {v.geom_type:13s} area_deg2={v.area:.3f}")
