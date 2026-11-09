"""Original music bed for Ashwillpower reels (composed in code — fully owned). D major, 100 BPM, I–V–vi–IV."""
import numpy as np, soundfile as sf
SR = 44100; BPM = 100; BEAT = 60 / BPM; BAR = 4 * BEAT
DUR = 100.0; N = int(DUR * SR); rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def add(sig, t, pan=0.0, g=1.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if i >= N: return
    s = sig[:j - i] * g; L[i:j] += s * np.sqrt(0.5 * (1 - pan)); R[i:j] += s * np.sqrt(0.5 * (1 + pan))
def env(n, a=0.005, d=0.4, sus=0.0, rel=0.1, dur=None):
    t = np.arange(n) / SR; e = np.minimum(1, t / a) * (sus + (1 - sus) * np.exp(-t / d))
    if dur is not None: e *= np.clip(1 - (t - dur) / rel, 0, 1)
    return e
def epiano(m, dur):
    n = int((dur + 0.6) * SR); t = np.arange(n) / SR; f = hz(m)
    mod = np.sin(2 * np.pi * f * 2 * t) * 1.2 * np.exp(-t / 0.25)
    s = np.sin(2 * np.pi * f * t + mod) * 0.6 + np.sin(2 * np.pi * f * 2 * t) * 0.12 * np.exp(-t / 0.3)
    return s * env(n, 0.004, 1.2, 0.25, 0.5, dur)
def pluck(m, dur=0.35):
    n = int((dur + 0.3) * SR); t = np.arange(n) / SR; f = hz(m)
    s = sum(np.sin(2 * np.pi * f * k * t) * (0.55 / k) * np.exp(-t * (6 + 5 * k)) for k in range(1, 6))
    return s * env(n, 0.002, 0.25)
def bass(m, dur):
    n = int((dur + 0.05) * SR); t = np.arange(n) / SR; f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    return np.tanh(1.5 * s) * env(n, 0.006, 0.5, 0.6, 0.05, dur)
def kick():
    n = int(0.35 * SR); t = np.arange(n) / SR; f = 45 + 110 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
def clap():
    n = int(0.25 * SR); t = np.arange(n) / SR; x = rng.standard_normal(n)
    x = np.convolve(x, np.ones(6) / 6, "same") - np.convolve(x, np.ones(60) / 60, "same")
    return x * np.exp(-t * 18) * 0.6
def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * SR); x = rng.standard_normal(n); x = x - np.convolve(x, np.ones(8) / 8, "same")
    return x * np.exp(-np.arange(n) / SR * (14 if open_ else 70)) * 0.25
CH = [(62, [62, 66, 69, 73]), (57, [61, 64, 69, 71]), (59, [62, 66, 69, 71]), (55, [62, 67, 71, 74])]   # Dmaj7, A(add9), Bm7, G(add)
MEL = [(0, 78, .5), (.5, 76, .5), (1, 74, 1), (2, 76, .5), (2.5, 78, 1.5),
       (4, 76, .5), (4.5, 74, .5), (5, 73, 1), (6, 69, 2),
       (8, 71, .5), (8.5, 73, .5), (9, 74, 1), (10, 76, .5), (10.5, 78, 1.5),
       (12, 79, .5), (12.5, 78, .5), (13, 76, 1), (14, 74, 2)]          # 4-bar motif, in beats
nbars = int(DUR / BAR) + 1
duck = np.ones(N)
for b in range(nbars):
    t0 = b * BAR; root, chord = CH[b % 4]
    sec = "intro" if b < 2 else "break" if 26 <= b < 30 else "outro" if b >= 40 else "full"
    for m in chord: add(epiano(m, BAR * 0.95), t0, pan=(m - 66) / 14, g=0.16)
    # arpeggio 8ths
    if sec != "intro":
        arp = [chord[0] + 12, chord[2], chord[1] + 12, chord[3]]
        for k in range(8): add(pluck(arp[k % 4], 0.25), t0 + k * BEAT / 2, pan=0.35 if k % 2 else -0.35, g=0.10 if sec == "break" else 0.12)
    if sec in ("full", "outro"):
        for k in range(4): add(bass(root - 24 + (7 if k == 3 and b % 2 else 0), BEAT * 0.9), t0 + k * BEAT, g=0.22)
        for k in (0, 2): add(kick(), t0 + k * BEAT, g=0.55); i = int((t0 + k * BEAT) * SR); duck[i:i + int(0.25 * SR)] = np.minimum(duck[i:i + int(0.25 * SR)], np.linspace(0.55, 1, int(0.25 * SR))[: max(0, min(N, i + int(.25 * SR)) - i)])
        if b % 2: add(kick(), t0 + 3.5 * BEAT, g=0.35)
        for k in (1, 3): add(clap(), t0 + k * BEAT, g=0.22)
        for k in range(8): add(hat(open_=(k == 7)), t0 + k * BEAT / 2, pan=0.2, g=0.30 if k % 2 else 0.16)
    if sec in ("full",) and (b // 4) % 2 == 1:
        for (bt, m, d) in MEL:
            if b % 4 == int(bt // 4):
                add(pluck(m, d * BEAT * 0.9) * 1.0 + 0.0, t0 + (bt % 4) * BEAT, pan=0.1, g=0.19)
L *= duck; R *= duck
# simple stereo reverb (decaying noise IR)
ir_n = int(1.6 * SR); ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR * 3.2); ir /= np.abs(ir).sum() / 6
from numpy.fft import rfft, irfft
def conv(x):
    n = len(x) + ir_n; m = 1 << (n - 1).bit_length(); return irfft(rfft(x, m) * rfft(ir, m), m)[:len(x)]
L = L + 0.18 * conv(L); R = R + 0.18 * conv(np.roll(R, 300))
mix = np.stack([L, R], 1)
fade = np.ones(N); fi = int(1.0 * SR); fo = int(4.0 * SR); fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo)
mix *= fade[:, None]; mix /= np.abs(mix).max() / 0.89
sf.write("/home/user/work/jtrip/music/bed.wav", mix.astype(np.float32), SR)
print("ok", DUR)
