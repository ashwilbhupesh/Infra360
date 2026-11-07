"""Original devotional-pop bed for the Khatu Shyam Ji reel (composed in code, fully owned). D, 96 BPM: tanpura drone, temple bell, dholak groove, bansuri-style melody."""
import numpy as np, soundfile as sf
SR=44100; BPM=96; BEAT=60/BPM; BAR=4*BEAT; DUR=69.0; N=int(DUR*SR); rng=np.random.default_rng(11)
L=np.zeros(N); R=np.zeros(N)
def hz(m): return 440*2**((m-69)/12)
def add(s,t,pan=0,g=1):
    i=int(t*SR); j=min(N,i+len(s))
    if i>=N: return
    s=s[:j-i]*g; L[i:j]+=s*np.sqrt(.5*(1-pan)); R[i:j]+=s*np.sqrt(.5*(1+pan))
def tanpura(m,dur):
    n=int(dur*SR); t=np.arange(n)/SR; f=hz(m)
    s=sum(np.sin(2*np.pi*f*k*t+0.3*np.sin(2*np.pi*.7*t))*(0.5/k**1.1)*(1+0.4*np.sin(2*np.pi*(0.25+k*.05)*t)) for k in range(1,9))
    return s*np.exp(-t/2.2)*np.minimum(1,t/.05)
def bell(m):
    n=int(3.5*SR); t=np.arange(n)/SR; f=hz(m)
    return sum(np.sin(2*np.pi*f*r*t)*a*np.exp(-t/d) for r,a,d in [(1,.5,1.6),(2.76,.3,.8),(5.4,.18,.4),(8.9,.08,.2),(1.003,.4,1.8)])
def dha():
    n=int(.4*SR); t=np.arange(n)/SR; f=70+90*np.exp(-t*20)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*7)
def na():
    n=int(.18*SR); t=np.arange(n)/SR; x=rng.standard_normal(n); x=x-np.convolve(x,np.ones(5)/5,'same')
    return (x*.35+np.sin(2*np.pi*520*t)*.6)*np.exp(-t*30)
def shaker():
    n=int(.07*SR); x=rng.standard_normal(n); x=x-np.convolve(x,np.ones(4)/4,'same'); return x*np.exp(-np.arange(n)/SR*55)*.18
def flute(m,dur):
    n=int((dur+.15)*SR); t=np.arange(n)/SR; vib=1+0.006*np.sin(2*np.pi*5.2*t)*np.minimum(1,t/.3)
    ph=2*np.pi*np.cumsum(hz(m)*vib)/SR; s=np.sin(ph)+.18*np.sin(2*ph)+.05*np.sin(3*ph)
    br=rng.standard_normal(n)*.04; e=np.minimum(1,t/.06)*np.clip(1-(t-dur)/.15,0,1)
    return (s+br)*e
def pad(ms,dur):
    n=int(dur*SR); t=np.arange(n)/SR
    s=sum(np.sin(2*np.pi*hz(m)*t*(1+d))*.2 for m in ms for d in (-.002,.002))
    return s*np.minimum(1,t/.8)*np.clip((dur-t)/.8,0,1)
CH=[[62,66,69],[60,64,67],[59,62,67],[57,61,64]]   # D, C, G/B, A  (Khamaj colour)
MEL=[(0,74,.5),(.5,76,.5),(1,78,1),(2,79,.5),(2.5,78,.5),(3,76,1),(4,74,.5),(4.5,72,.5),(5,71,1),(6,69,2),
     (8,74,.5),(8.5,76,.5),(9,78,.75),(9.75,81,.25),(10,79,1),(11,78,1),(12,76,.5),(12.5,74,.5),(13,72,1),(14,74,2)]
nb=int(DUR/BAR)+1
for b in range(nb):
    t0=b*BAR; full=2<=b<22
    add(tanpura(50,BAR),t0,-.3,.25); add(tanpura(57,BAR),t0+BEAT*1.5,.3,.18); add(tanpura(62,BAR),t0+BEAT*2.5,-.1,.15)
    add(pad(CH[b%4],BAR+.6),t0,0,.12)
    if b%2==0: add(bell(86),t0,.4,.22)
    if b>=1:
        for k in range(8):
            t=t0+k*BEAT/2
            if k in (0,3,4): add(dha(),t,0,.55 if full else .3)
            if k in (2,6): add(na(),t,.1,.5 if full else .25)
            if k in (5,7) and full: add(na(),t,-.1,.25)
        for k in range(16): add(shaker(),t0+k*BEAT/4,.5,.8 if k%2 else .4)
    if full and b>=4:
        for bt,m,d in MEL:
            if (b%4)*4<=bt<(b%4)*4+4: add(flute(m,d*BEAT),t0+(bt-(b%4)*4)*BEAT,-.15,.16)
x=np.stack([L,R],1)
# simple reverb
ir=np.exp(-np.arange(int(1.2*SR))/SR*4)*rng.standard_normal(int(1.2*SR))*.02
for c in range(2): x[:,c]+=np.convolve(x[:,c],ir)[:N]*.6
fade=np.ones(N); fo=int(2.5*SR); fade[-fo:]=np.linspace(1,0,fo); x*=fade[:,None]
x/=np.abs(x).max()*1.12
sf.write("khatu_bed.wav",x,SR)
