import numpy as np, soundfile as sf, sys
sr=48000; dur=float(sys.argv[2]); bpm=80; beat=60/bpm; bar=beat*4
t=np.arange(int(sr*dur))/sr
def n(m): return 440*2**((m-69)/12)
# Dm9 · Bbmaj7 · Fmaj7/A · C(add9)  -- slow, warm, two bars each
prog=[[50,57,62,65,69,64],[46,53,58,62,65,69],[45,53,57,60,64,69],[48,55,60,62,64,67]]
pad=np.zeros_like(t); chord_len=bar*2
rng=np.random.default_rng(7)
for i in range(int(dur/chord_len)+2):
    c=prog[i%4]; s=i*chord_len; e=s+chord_len+1.5
    m=(t>=s)&(t<e); tt=t[m]-s
    env=np.minimum(1,tt/1.4)*np.clip((e-t[m])/1.5,0,1)
    for k,note in enumerate(c):
        f=n(note)
        for det in (-0.12,0.0,0.13):
            ph=rng.uniform(0,2*np.pi)
            pad[m]+=env*(np.sin(2*np.pi*f*(1+det/100)*tt+ph)+0.25*np.sin(2*np.pi*2*f*tt+ph))*(0.9 if k else 1.2)/len(c)
# gentle low-pass (one-pole) for warmth
def lp(x,fc):
    a=np.exp(-2*np.pi*fc/sr); y=np.zeros_like(x); acc=0.0
    out=np.empty_like(x)
    for i in range(0,len(x),4096):
        seg=x[i:i+4096]; o=np.empty_like(seg)
        for j,v in enumerate(seg): acc=(1-a)*v+a*acc; o[j]=acc
        out[i:i+4096]=o
    return out
pad=lp(pad,1800)
# soft sub pulse on every beat + quiet tick on offbeats
pulse=np.zeros_like(t)
for b in range(int(dur/beat)):
    s=int(b*beat*sr); L=int(0.5*sr); tt=np.arange(L)/sr
    if s+L>len(t): break
    pulse[s:s+L]+=np.sin(2*np.pi*55*tt*(1+0.6*np.exp(-tt*30)))*np.exp(-tt*7)*0.55
    o=int((b+0.5)*beat*sr); L2=int(0.06*sr)
    if o+L2<len(t): pulse[o:o+L2]+=rng.standard_normal(L2)*np.exp(-np.arange(L2)/sr*90)*0.05
mix=pad*0.5+pulse*0.6
fade=np.minimum(1,t/2.0)*np.clip((dur-t)/2.5,0,1)
mix*=fade; mix/=np.max(np.abs(mix))*1.25
st=np.stack([mix*0.97+0.03*np.roll(mix,240), mix*0.97+0.03*np.roll(mix,-240)],1)
sf.write(sys.argv[1], st, sr)
