import json, subprocess
S=[(0.0, 0.64), (1.0, 1.94), (3.3, 3.62), (6.14, 6.52), (8.86, 9.34), (9.84, 10.3), (11.52, 11.92), (13.22, 13.62), (15.5, 15.82), (17.04, 18.34), (21.18, 21.84), (23.36, 23.74), (25.22, 25.9), (27.56, 28.06), (29.98, 30.58), (31.2, 31.6), (33.26, 34.4), (35.98, 36.28), (37.18, 37.94), (39.18, 39.48), (41.46, 42.12), (43.12, 43.58), (46.52, 46.82), (48.2, 48.9), (49.46, 50.1), (51.72, 52.04), (53.28, 53.64), (54.08, 54.58), (57.26, 57.86), (59.8, 60.3), (61.54, 62.14), (63.36, 63.88), (70.0, 70.74), (71.32, 72.02), (73.9, 74.34), (74.7, 75.04), (76.38, 76.9), (78.08, 78.8), (79.52, 80.34), (82.94, 85.3), (85.34, 86.5), (88.22, 88.58), (88.6, 89.12), (91.58, 92.1), (92.74, 93.06), (95.2, 95.5), (96.56, 97.26), (97.62, 98.14), (99.12, 99.44), (101.08, 101.42), (103.64, 104.26), (106.88, 107.36), (107.9, 108.52), (109.54, 110.02), (111.02, 111.4), (112.58, 112.98), (114.46, 116.02), (116.04, 116.36), (120.0, 120.6), (124.1, 124.44)]
cuts=[(s+e)/2 for s,e in S if s>0.1 and e<124.4]
segB=[0.0]+cuts+[124.5]
# speech bounds for each segment k: (silence ending inside/at start, silence starting at end)
sil_mid={round((s+e)/2,3):(s,e) for s,e in S}
def speech(k):
    a=segB[k]; b=segB[k+1]
    sa = sil_mid.get(round(a,3),(0,0.64))[1] if k>0 else 0.64
    sb = sil_mid.get(round(b,3),(124.1,124.44))[0]
    return sa, sb
T={1:"Kya aap bhi Jaipur ja rahe hain?",2:"Toh yeh 3 din ka time-wise plan save kar lo.",3:"Ghoomna, khaana aur shopping, sab ek saath.",
4:"Day 1.",5:"Day 1 par purana shehar.",6:"Subah 9 baje Hawa Mahal,",9:"Aur uske saamne Tattoo Cafe ki chhat se best view.",10:"Sawa das, City Palace,",11:"andar Baradari mein coffee.",12:"12:15, Jantar Mantar.",
13:"Lunch mein Rawat ki pyaaz kachori.",14:"Thoda aaram,",15:"phir The Johri mein chai-nashta.",16:"Johari Bazaar mein jewellery,",17:"LMB ki mithai.",
18:"4 baje Bapu Bazaar:",19:"mojari, bandhej, lac ki chudiyan.",20:"Shaam ko MI Road:",21:"Amrapali ki silver jewellery, Lassiwala ki lassi,",22:"aur dinner Niros mein.",
23:"Day 2.",24:"Day 2 mein cover karenge forts.",25:"8 baje Amer Fort,",26:"andar",27:"1135 AD mein royal lunch ya chai.",28:"11 baje Panna Meena ka Kund,",
29:"aur 12 baje Jal Mahal.",30:"Lunch aur aaram.",31:"4:30 Nahargarh. Padao Cafe mein sunset, aur raat ko poore Jaipur ki lights.",
32:"Day 3.",33:"Day 3 mein mandir aur modern Jaipur.",34:"Subah",35:"saade saat baje Galta Ji,",36:"10 baje Birla Mandir.",
38:"Saade gyarah baje Patrika Gate pe photos le lijiye.",43:"Phir shopping:",44:"Anokhi aur Gulabji se Jaipur print,",45:"saath mein blue pottery.",
46:"Chai",47:"Tapri Central mein.",48:"Shaam 6 baje Albert Hall,",49:"aur raat Chokhi Dhani mein Rajasthani dinner.",
50:"Best time to come is between October aur March.",51:"Rukiye",52:"Central Jaipur ke andar.",53:"Khaana mat bhooliyega:",54:"dal baati churma,",55:"ghewar aur pyaaz ki kachori.",
58:"Save kariye, aur comment kariye ki agli city kaunsi dekhni hai!"}
keep=[]; out=[]
ks=sorted(T)
for i,k in enumerate(ks):
    s,e=speech(k)
    pre=.14; post=.16
    if T[k].startswith("Day") and len(T[k])<8: pre=.3
    keep.append([max(0,s-pre),e+post,k])
# merge overlapping
m=[]
for a,b,k in keep:
    if m and a<=m[-1][1]: m[-1][1]=max(m[-1][1],b); m[-1][2].append(k)
    else: m.append([a,b,[k]])
GAP={5:2.6,24:2.2,33:2.4}
acc=0; newt={}; gaps=[]
for a,b,ks_ in m:
    for k in ks_:
        s,e=speech(k); newt[k]=(round(acc+s-a,2),round(acc+e-a,2))
    acc+=b-a
    g=sum(GAP.get(k,0) for k in ks_); gaps.append(g); acc+=g
json.dump([{"k":k,"s":newt[k][0],"e":newt[k][1],"t":T[k]} for k in ks],open('phrases.json','w'),indent=0)
fc=[]
for i,(a,b,_) in enumerate(m):
    pad=f",apad=pad_dur={gaps[i]:.3f}" if gaps[i] else ""
    fc.append(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={b-a-0.02:.3f}:d=0.02{pad}[a{i}]")
fc.append("".join(f"[a{i}]" for i in range(len(m)))+f"concat=n={len(m)}:v=0:a=1,highpass=f=85,afftdn=nf=-25,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-15:TP=-1.5[o]")
subprocess.run(["ffmpeg","-y","-v","error","-i","rec.mp4","-filter_complex",";".join(fc),"-map","[o]","-ar","48000","-c:a","pcm_s16le","voice.wav"],check=True)
print("pieces",len(m),"dur",round(acc,2))
for k in ks: print(k,newt[k],T[k][:50])
