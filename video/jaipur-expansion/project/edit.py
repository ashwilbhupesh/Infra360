import json, subprocess
sil=json.load(open('sil.json'))
B=[0.0]+[float(x) for x in open('cuts.txt').read().split()]+[122.2]
segs=list(zip(B,B[1:]))
mid={round((s+e)/2,2):(s,e) for s,e in sil}
def speech(i):
    a,b=segs[i]
    sa=mid.get(round(a,2),(0,0))[1] if i>0 else next((e for s,e in sil if s<=0.05),0)
    sb=mid.get(round(b,2),(b,b))[0]
    return sa,sb
T={0.0:"Jaipur mein property lene se pehle, Jaipur ka structure samajh lo.",4.63:"Jaipur chaaron taraf se highways se ghira hai:",7.96:"Delhi Road, Sikar Road,",
9.87:"Kalwar Road, Sirsi Road, Ajmer Road, Diggi Road, Tonk Road aur Agra Road.",15.58:"Aur inko jodti hai Ring Road.",
24.59:"Inke beech mein hai Central Jaipur:",27.37:"Pink City, C-Scheme, Civil Lines, Bani Park,",31.02:"Raja Park,",
32.03:"Jawahar Nagar, Lal Kothi. Aur aas-paas bade residential hubs:",35.87:"Vaishali Nagar, Shyam Nagar, Mansarovar, Vidhyadhar Nagar, Murlipura, Jagatpura",
42.87:"Lekin Central Jaipur mein zameen ab 1 se 3 lakh rupaye per gaj tak hai.",51.64:"Naya middle class yahan ghar banane ka sochta bhi nahi.",
54.7:"Isliye log bahar shift ho rahe hain,",56.83:"inhi roads ke saath-saath.",58.66:"Sabse zyada growth: Ajmer Road se Tonk Road ke beech,",
62.66:"Diggi Road ke aas-paas.",64.24:"Yahi hai Jaipur ka naya expansion zone.",66.99:"Yahan nayi colonies bas rahi hain:",69.3:"Bhankrota, Mahapura,",
71.27:"Patrakar Colony, Narayan Vihar, Muhana, Shivdaspura.",75.68:"Kyun?",76.46:"Kyunki yahan aa raha hai rozgaar, hospitals,",
79.19:"schools, colleges, connectivity, shops aur commercial.",86.08:"Aur Jaipur ab sirf city tak simit nahi.",88.95:"October 2025 ki JDA notification ke baad",
91.87:"Jaipur region lagbhag 3,000 se 7,000 sq km ho gaya hai,",99.8:"aur 693 naye gaon bhi jode ja chuke hain.",102.96:"Matlab growth bahar ki taraf aa rahi hai.",
105.63:"Aaj ka mauka Jaipur ke bahar ke ilaakon mein hai,",108.57:"kyunki growth wahan pahunchegi.",110.59:"Bas plot lene se pehle approval aur patta zaroor check karein.",
114.31:"Aapke hisaab se kaunsa road sabse tez badhega?",117.2:"Comment mein likhiye,",118.33:"aur Part 2 ke liye follow kijiye."}
keep=[]
for i,(a,b) in enumerate(segs):
    k=round(a,2)
    if k in T:
        s,e=speech(i); keep.append([max(0,s-.12),e+.15,[(i,T[k])]])
m=[]
for a,b,x in keep:
    if m and a<=m[-1][1]: m[-1][1]=max(m[-1][1],b); m[-1][2]+=x
    else: m.append([a,b,x])
acc=0; P=[]
for a,b,x in m:
    for i,t in x:
        s,e=speech(i); P.append({"k":len(P),"s":round(acc+s-a,2),"e":round(acc+e-a,2),"t":t,"src":round(s,2)})
    acc+=b-a
json.dump(P,open('phrases.json','w'),indent=0)
fc=[f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={b-a-0.02:.3f}:d=0.02[a{i}]" for i,(a,b,_) in enumerate(m)]
fc.append("".join(f"[a{i}]" for i in range(len(m)))+f"concat=n={len(m)}:v=0:a=1,highpass=f=85,afftdn=nf=-25,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-15:TP=-1.5[o]")
subprocess.run(["ffmpeg","-y","-v","error","-i","rec.mp4","-filter_complex",";".join(fc),"-map","[o]","-ar","48000","-c:a","pcm_s16le","voice.wav"],check=True)
print(len(m),"pieces",round(acc,2), "first src", m[0][0])
for p in P: print(p["k"],p["s"],p["e"],p["t"][:60])
