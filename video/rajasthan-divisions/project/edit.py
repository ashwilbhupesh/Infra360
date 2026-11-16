import json, subprocess
sil=json.load(open('sil.json'))
B=[0.0]+[float(x) for x in open('cuts.txt').read().split()]+[78.1]
segs=list(zip(B,B[1:]))
mid={round((s+e)/2,2):(s,e) for s,e in sil}
def speech(i):
    a,b=segs[i]
    sa=mid.get(round(a,2),(0,0))[1] if i>0 else 0
    sb=mid.get(round(b,2),(b,b))[0]
    return sa,sb
# start-of-segment -> (caption text, [names spoken in order])
T={0.82:("Rajasthan mein kitne district hain? 50? Galat.",[]),4.34:("December 2024 mein 9 district aur 3 sambhag khatam ho gaye.",[]),
8.9:("Ab hain 7 sambhag",[]),10.43:("aur 41 district.",[]),12.09:("Pehle 7 sambhag:",[]),13.41:("Jaipur,",["V:Jaipur"]),
14.21:("Jodhpur, Ajmer, Udaipur,",["V:Jodhpur","V:Ajmer","V:Udaipur"]),16.69:("Kota, Bikaner aur Bharatpur.",["V:Kota","V:Bikaner","V:Bharatpur"]),
19.19:("Ab ek-ek karke inke district dekhte hain. Jaipur sambhag:",["S:Jaipur"]),23.07:("Jhunjhunu,",["Jhunjhunu"]),24.15:("Khairthal-Tijara,",["Khairthal-Tijara"]),
25.42:("Sikar,",["Sikar"]),27.88:("Kotputli-Behror,",["Kotputli-Behror"]),29.33:("Alwar,",["Alwar"]),30.11:("Jaipur aur Dausa.",["Jaipur","Dausa"]),
31.82:("Jodhpur sambhag:",["S:Jodhpur"]),33.07:("Phalodi, Jaisalmer, Jodhpur,",["Phalodi","Jaisalmer","Jodhpur"]),35.62:("Barmer, Balotra,",["Barmer","Balotra"]),
37.32:("Pali aur Jalore, Sirohi.",["Pali","Jalore","Sirohi"]),39.22:("Ajmer sambhag:",["S:Ajmer"]),
40.95:("Nagaur, Didwana-Kuchaman, Ajmer, Beawar,",["Nagaur","Didwana-Kuchaman","Ajmer","Beawar"]),44.71:("Tonk aur Bhilwara.",["Tonk","Bhilwara"]),
46.33:("Udaipur sambhag:",["S:Udaipur"]),47.62:("Rajsamand, Chittorgarh, Udaipur,",["Rajsamand","Chittorgarh","Udaipur"]),50.46:("Salumber,",["Salumber"]),
51.46:("Pratapgarh, Dungarpur aur Banswara.",["Pratapgarh","Dungarpur","Banswara"]),54.31:("Kota sambhag:",["S:Kota"]),55.59:("Bundi,",["Bundi"]),
56.42:("Kota, Baran aur Jhalawar.",["Kota","Baran","Jhalawar"]),58.87:("Bikaner sambhag:",["S:Bikaner"]),60.3:("Sri Ganganagar, Hanumangarh,",["Sri Ganganagar","Hanumangarh"]),
63.59:("Bikaner aur Churu.",["Bikaner","Churu"]),66.58:("Bharatpur sambhag: Deeg,",["S:Bharatpur","Deeg"]),68.62:("Bharatpur,",["Bharatpur"]),
69.57:("Dholpur, Karauli aur Sawai Madhopur.",["Dholpur","Karauli","Sawai Madhopur"]),72.47:("Toh total 7 sambhag aur 41 district. Aapka district kaunsa hai?",[]),76.98:("Comment karo!",[])}
keep=[]
for i,(a,b) in enumerate(segs):
    k=round(a,2)
    if k in T:
        s,e=speech(i); keep.append([max(0,s-.1),e+.12,[(i,k)]])
m=[]
for a,b,x in keep:
    if m and a<=m[-1][1]: m[-1][1]=max(m[-1][1],b); m[-1][2]+=x
    else: m.append([a,b,x])
GAP={4.34:1.6}
acc=0; P=[]; EV={}; gaps=[]
for a,b,x in m:
    for i,k in x:
        s,e=speech(i); ns,ne=acc+s-a,acc+e-a; txt,names=T[k]
        P.append({"s":round(ns,2),"e":round(ne,2),"t":txt})
        # place names by char position
        low=txt.lower()
        for nm in names:
            key=nm.split(":")[-1]; pos=low.find(key.lower().split("-")[0][:5]) if "S:" not in nm else low.find(key.lower())
            tt=ns+(ne-ns)*max(0,pos)/len(txt)
            if nm.startswith("V:"): EV["V:"+key]=round(tt,2)
            elif nm.startswith("S:"): EV["S:"+key]=round(tt,2)
            else: EV.setdefault("D:"+key, round(tt,2))
    acc+=b-a; g=sum(GAP.get(k,0) for _,k in x); gaps.append(g); acc+=g
EV["galat"]=round(P[0]["s"]+(P[0]["e"]-P[0]["s"])*.82,2); EV["fifty"]=round(P[0]["s"]+(P[0]["e"]-P[0]["s"])*.62,2)
EV["count"]=P[2]["s"]; EV["divs"]=P[4]["s"]; EV["final"]=P[-2]["s"]; EV["cta"]=round(P[-2]["s"]+(P[-2]["e"]-P[-2]["s"])*.55,2); EV["end"]=round(acc+.8,2); EV["cancel"]=P[1]["s"]
json.dump({"phrases":P,"ev":EV},open('timing.json','w'),indent=0)
fc=[f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={b-a-0.02:.3f}:d=0.02" + (f",apad=pad_dur={gaps[i]:.3f}" if gaps[i] else "") + f"[a{i}]" for i,(a,b,_) in enumerate(m)]
fc.append("".join(f"[a{i}]" for i in range(len(m)))+f"concat=n={len(m)}:v=0:a=1,highpass=f=85,afftdn=nf=-25,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-15:TP=-1.5[o]")
subprocess.run(["ffmpeg","-y","-v","error","-i","rec.mp4","-filter_complex",";".join(fc),"-map","[o]","-ar","48000","-c:a","pcm_s16le","voice.wav"],check=True)
print(len(m),"pieces",round(acc,2),"first",m[0][0]); print(len([k for k in EV if k.startswith("D:")]),"districts"); print(EV)
