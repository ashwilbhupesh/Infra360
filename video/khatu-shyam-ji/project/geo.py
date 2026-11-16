import urllib.request, urllib.parse, json, sys
q='''[out:json][timeout:60];
(node["name"~"^(Khatushyamji|Khatu|Khatu Shyam Ji|Ringas|Reengus|Salasar|Kotputli|Kishangarh|Sikar|Chomu|Renwal|Naraina|Dudu|Palsana|Sundarpura|Jaipur)$"]["place"](26.3,74.5,27.9,76.4););
out;
node["name"~"Jeen|Salasar Balaji|Khatu Shyam"]["amenity"="place_of_worship"](26.9,74.5,27.9,75.9);out;'''
for m in ["https://overpass.kumi.systems/api/interpreter","https://overpass-api.de/api/interpreter","https://maps.mail.ru/osm/tools/overpass/api/interpreter"]:
    try:
        r=urllib.request.urlopen(m,data=urllib.parse.urlencode({"data":q}).encode(),timeout=90).read(); break
    except Exception as e: print(m,e)
d=json.loads(r)
for e in d["elements"]: print(e["tags"].get("name"),e["tags"].get("place",e["tags"].get("amenity")),round(e["lat"],4),round(e["lon"],4))
