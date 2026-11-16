import json
keep=json.load(open('keep.json'))
def s2n(t):
    acc=0
    for a,b in keep:
        if t<a: return acc
        if t<=b: return acc+t-a
        acc+=b-a
    return acc
B=[0.0]+[float(x) for x in open('cuts.txt').read().split()]+[98.85]
TXT=["Khatu Shyam Ji —","agle 5 saal mein jagah pehchaan mein nahi aayegi","Har saal lakhon bhakt yahan aate hain","aur ab yahan pahunchna hoga aur bhi aasaan",
"India, Rajasthan, aur yeh raha Khatu Shyam Ji","Delhi ho ya Jaipur,","har taraf se connectivity aa rahi hai","4 bade projects",
"Ek — Kotputli–Kishangarh greenfield expressway","Khatu Shyam Ji se hokar ja raha hai","Do —","Jaipur–Ringas highway","ab 4 ki jagah 6-lane hone wala hai",
"Teen —","Khatu ka apna ring road","poore traffic ko bypass karne ke liye","mele mein bhi jaana hoga aasaan","Chaar —",
"Ringas se Khatu Shyam Ji nayi rail line aa rahi hai","aur naya Sundarpura station aa raha hai","Mandir ko mil raha hai heritage look","zyada bhakt, zyada demand",
"Lakhon log aate hain","par hotels aur dharamshala kam pad jaate hain","isliye Khatu ban raha hai tourism, hotels","aur housing ka agla hub",
"Saath mein Salasar Balaji aur Jeen Mata","poora temple circuit connect karte hain","Poora region badal raha hai","Khatu mein hotels","Ringas mein commercial",
None,"Chomu mein housing","expressway ke paas logistics","Kishangarh, Kotputli mein industry aur highway business","Jahan connectivity, wahan growth",
"Agar aap bhi is area mein nivesh karne ka soch rahe hain","toh chukiyega mat","Lekin nivesh karne se pehle","approval aur patta zaroor check karein",
"Kitni baar Khatu gaye hain?","Comment kariye — Jai Shree Shyam!",None,None,None,"Aur bhejiye usko jo har Ekadashi Khatu Shyam jaate hain"]
P=[(0.0, 0.4), (1.52, 1.88), (4.24, 5.82), (7.42, 7.76), (9.6, 10.12), (12.74, 13.22), (14.22, 14.56), (16.14, 16.52), (17.56, 18.62), (20.62, 21.08), (22.76, 23.3), (23.56, 24.08), (25.4, 25.96), (27.92, 28.46), (28.74, 29.24), (30.62, 31.12), (32.86, 33.22), (34.66, 35.16), (35.48, 35.88), (38.4, 38.74), (40.84, 41.74), (43.44, 43.98), (45.46, 45.98), (47.06, 47.48), (49.88, 50.34), (52.54, 52.84), (54.06, 54.68), (57.16, 57.5), (59.32, 60.12), (61.78, 62.2), (63.04, 63.48), (64.66, 65.08), (66.4, 67.32), (68.3, 68.66), (70.26, 70.8), (73.58, 74.22), (75.92, 79.32), (81.68, 82.34), (83.18, 83.98), (85.36, 86.12), (88.02, 88.74), (89.86, 90.26), (91.7, 92.1), (92.96, 93.28), (94.32, 94.62), (94.88, 95.66), (98.28, 98.84)]
assert len(TXT)==len(P)-1, (len(TXT),len(P))
out=[]
for i,t in enumerate(TXT):
    if t is None: continue
    s,e=P[i][1],P[i+1][0]   # speech start/end in source
    out.append({"i":i,"s":round(s2n(s),2),"e":round(s2n(e),2),"t":t})
json.dump(out,open('phrases.json','w'),indent=0,ensure_ascii=False)
for o in out: print(o["i"],o["s"],o["e"],o["t"])
