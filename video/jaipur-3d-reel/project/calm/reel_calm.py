"""3D sample: Jaipur terrain (Copernicus DEM, Sentinel-2 drape) with price-multiplier bars rising per area and a drone camera path."""
import json
M = json.load(open("proj/assets/meta.json"))
END = 68.2
# three areas the camera visits (index into areas)
import math
TOUR = sorted(range(len(M['areas'])), key=lambda i: -M['areas'][i]['v'])  # geographic: south (Sitapura) -> north (Sikar Road)
STOPN = {'sitapura':19.38,'pratap':24.03,'jagatpura':26.67,'malviya':31.47,'mansarovar':33.55,'ajmer':37.40,'vaishali':39.56,'jhotwara':42.60,'vidyadhar':45.00,'sikar':47.80}
STOPS = [STOPN[M['areas'][i]['k']] for i in TOUR]
T3 = 15.85; TS = STOPS[0]; DS = 3.1; TO = 53.0; FACE_END = 2.0
HTML = """<!doctype html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script>
<style>*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#05070b}
#root{position:relative;width:1080px;height:1920px;overflow:hidden}#gl{position:absolute;inset:0;width:1080px;height:1920px}
.lb{position:absolute;left:0;top:0;transform:translate(-50%,-100%);opacity:0;text-align:center;white-space:nowrap;font-family:Inter,Arial,sans-serif}
.lb b{display:block;padding:6px 16px;border-radius:14px 14px 0 0;background:rgba(6,8,12,.78);font-weight:900;font-size:34px;color:#fff}
.lb span{display:block;padding:2px 16px 8px;border-radius:0 0 14px 14px;background:rgba(6,8,12,.78);font-weight:900;font-size:44px;color:#5CF08A}
.lb.hot b{font-size:46px}.lb.hot span{font-size:64px}.lb.hot i{display:block;margin-top:6px;padding:6px 14px;border-radius:12px;background:rgba(6,8,12,.8);font:800 36px Inter,Arial,sans-serif;font-style:normal;color:#fff}
.lb i{display:none}
.st{position:absolute;left:50px;right:50px;top:1330px;text-align:center;opacity:0}.st>span{display:inline-block;padding:14px 28px 16px;border-radius:24px;background:rgba(6,8,12,.62);font:900 66px/1.1 Inter,Arial,sans-serif;color:#fff;text-shadow:0 4px 0 #000}
.y{color:#5CF08A}
#brand{position:absolute;left:0;right:0;top:150px;text-align:center;font:700 24px "JetBrains Mono",monospace;letter-spacing:.2em;color:rgba(255,255,255,.85);text-shadow:0 2px 6px #000}
#tag3d{position:absolute;left:0;right:0;top:230px;text-align:center;opacity:0}#tag3d span{display:inline-block;padding:10px 22px;border-radius:14px;background:rgba(6,8,12,.75);font:800 30px "JetBrains Mono",monospace;letter-spacing:.14em;color:#FFE03A}
#fine{position:absolute;left:50px;right:50px;bottom:250px;text-align:center;font:500 20px/1.35 "JetBrains Mono",monospace;color:rgba(255,255,255,.8);padding:10px 16px;border-radius:14px;background:rgba(6,8,12,.7)}
#credit_x{position:absolute;left:40px;right:40px;bottom:90px;text-align:center;font:500 18px "JetBrains Mono",monospace;color:rgba(255,255,255,.65);text-shadow:0 1px 3px #000}
#pre .bgb{filter:blur(18px) brightness(.45);transform:scale(1.1)}#card{position:absolute;inset:0;transform-origin:540px 840px;transform:scale(.8);border-radius:30px;overflow:hidden;box-shadow:0 0 0 4px #5CF08A,0 30px 80px rgba(0,0,0,.7)}#card>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}#pins{position:absolute;inset:0}.pin b{font-size:34px!important}.pin{position:absolute;opacity:0}.pin i{position:absolute;left:-11px;top:-11px;width:22px;height:22px;border-radius:50%;background:#5CF08A;border:3px solid #111;box-shadow:0 0 14px #5CF08A}.pin b{position:absolute;left:18px;top:-22px;padding:4px 12px;border-radius:9px;background:rgba(8,12,20,.88);border:2px solid #5CF08A;font:800 28px Inter;color:#fff;white-space:nowrap}.pin b.r{left:auto;right:18px}
#hook{position:absolute;inset:0;overflow:hidden}#hook .full{position:absolute;inset:0}#hook .full img{width:100%;height:100%;object-fit:cover;display:block}
#h24{clip-path:inset(0 0 0 100%)}#hline{position:absolute;top:0;left:0;width:6px;height:1920px;background:#fff;box-shadow:0 0 24px #fff;opacity:0}#hline b{position:absolute;left:-34px;top:930px;width:74px;height:74px;border-radius:50%;background:#fff;color:#111;font:900 40px/74px Inter;text-align:center}
.yl2{position:absolute;left:40px;top:430px;opacity:0;padding:10px 22px;border-radius:14px;background:rgba(6,8,12,.75);font:900 54px Inter;color:#fff}.yl2.r{left:auto;right:40px;color:#FFE03A}
#ss{position:absolute;left:0;right:0;top:215px;display:flex;justify-content:center;gap:22px;opacity:0}#ss span{display:flex;align-items:center;gap:12px;padding:14px 24px;border-radius:40px;background:rgba(8,12,20,.85);border:2px solid rgba(255,255,255,.25);font:900 36px Inter,Arial,sans-serif;color:#fff}
#hh{position:absolute;left:0;right:0;top:310px;text-align:center;opacity:0;font-family:Inter,Arial,sans-serif}#hh b{display:inline-block;padding:0 36px 10px;border-radius:30px;background:rgba(6,8,12,.6);font-weight:900;font-size:100px;line-height:1.05;color:#5CF08A;text-shadow:0 6px 0 #000}#hh i{display:table;margin:12px auto 0;padding:8px 20px;border-radius:14px;background:rgba(6,8,12,.75);font:800 40px Inter;font-style:normal;color:#fff}#hh i.up{margin:0 auto 10px;color:#FFE03A}
#hprice{position:absolute;left:0;right:0;top:600px;text-align:center;opacity:0;font-family:Inter,Arial,sans-serif}#hprice b{display:inline-block;padding:0 30px 6px;border-radius:28px;background:rgba(6,8,12,.6);font-weight:900;font-size:110px;color:#FFE03A;text-shadow:0 6px 0 #000}#hprice i{display:table;margin:8px auto 0;padding:6px 16px;border-radius:12px;background:rgba(6,8,12,.75);font:800 30px "JetBrains Mono",monospace;font-style:normal;letter-spacing:.14em;color:#fff}
#rank{position:absolute;left:0;right:0;top:250px;text-align:center;opacity:0}#rank i{display:table;margin:0 auto 8px;padding:4px 14px;border-radius:10px;background:rgba(6,8,12,.75);font:800 24px "JetBrains Mono",monospace;font-style:normal;letter-spacing:.16em;color:#fff}#rank b{display:inline-block;padding:6px 30px;border-radius:22px;background:#2FD47A;font:900 64px Inter;color:#06210f;box-shadow:0 10px 30px rgba(0,0,0,.5)}
.st{position:absolute;left:50px;right:50px;top:1330px;text-align:center;opacity:0}.st>span{display:inline-block;padding:14px 28px 16px;border-radius:24px;background:rgba(6,8,12,.66);font:900 64px/1.1 Inter,Arial,sans-serif;color:#fff;text-shadow:0 4px 0 #000}.st small{display:block;margin-top:8px;font:800 46px Inter,Arial,sans-serif;color:#fff;text-shadow:0 3px 0 #000}
#fine{position:absolute;left:50px;right:50px;top:1575px;text-align:center;font:500 20px/1.35 "JetBrains Mono",monospace;color:rgba(255,255,255,.82);padding:10px 16px;border-radius:14px;background:rgba(6,8,12,.72);opacity:0}
#cta{position:absolute;left:60px;right:60px;top:1010px;display:flex;flex-direction:column;gap:20px;opacity:0}#cta span{display:flex;align-items:center;gap:20px;padding:18px 26px;border-radius:20px;background:rgba(8,12,20,.86);border:2px solid rgba(255,255,255,.2);font:900 40px Inter,Arial,sans-serif;color:#fff}
#credits{position:absolute;inset:0;opacity:0;background:#0b0d10;padding:300px 80px 0;font-family:Inter,Arial,sans-serif;color:#ddd}#credits b{display:block;margin:34px 0 14px;font:700 28px "JetBrains Mono",monospace;letter-spacing:.16em;color:#FFE03A}#credits p{font-size:32px;line-height:1.45;margin-bottom:18px}#credits i{display:block;margin-top:60px;font:700 26px "JetBrains Mono",monospace;letter-spacing:.2em;color:#fff;font-style:normal}
#cover{position:absolute;inset:0;opacity:0;overflow:hidden;background:radial-gradient(120% 80% at 70% 40%,#2B2016 0%,#1B140F 55%,#120d09 100%)}
#cvt{position:absolute;left:70px;right:70px;top:190px;font:900 140px/0.95 Inter,sans-serif;color:#F3E7D3;text-shadow:0 8px 40px rgba(0,0,0,.6)}#cvt small{display:block;font-size:56px}#cvt span{color:#F5B04A}
#cvs{position:absolute;left:76px;top:600px;font:800 52px/1.12 Inter,sans-serif;color:#F3E7D3}
#cvimg{position:absolute;left:76px;right:76px;top:720px;height:800px;border-radius:24px;overflow:hidden;border:3px solid #E3A23B;box-shadow:0 0 40px rgba(245,176,74,.35)}#cvimg>img,#cvb img{position:absolute;inset:0;width:928px;height:800px;object-fit:cover}#cvb{position:absolute;inset:0;clip-path:inset(0 0 0 50%)}
#cvimg i{position:absolute;left:50%;top:0;bottom:0;width:5px;margin-left:-2px;background:#fff;box-shadow:0 0 16px #fff}#cvimg b{position:absolute;top:18px;padding:6px 14px;border-radius:10px;background:rgba(27,20,15,.9);border:2px solid #E3A23B;font:800 30px Inter,sans-serif;color:#F3E7D3}#cvimg b.l{left:18px}#cvimg b.r{right:18px;background:#F5B04A;color:#1B140F}
#cvpill{position:absolute;left:76px;top:1570px;padding:12px 22px;border-radius:14px;background:rgba(60,38,14,.92);border:2px solid #E3A23B;font:800 40px Inter,sans-serif;color:#F3E7D3}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="__END__" data-width="1080" data-height="1920" data-fps="30">
<canvas id="gl" width="1080" height="1920" style="opacity:0"></canvas>
<div id="labels"></div>
<video id="avatar" class="clip" src="assets/avatar.mp4" data-start="0" data-duration="__END__" data-track-index="0" playsinline data-has-audio="true" data-volume="1" style="position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover"></video>
<div id="hook">__HOOK__</div>__TOPS__
<div id="brand">ASHWILLPOWER · JAIPUR REAL ESTATE</div>
<div id="rank"><i>SOUTH → NORTH</i><b id="rk">1 / 10</b></div>
__CAPS__
<div id="fine">Approx. rates · 1990–95 historical estimates · 2026 indicative listing rates · multipliers are calculated estimates, not verified investment returns · past growth ≠ future returns</div>
<div id="cta"><span><svg viewBox="0 0 24 24" width="56" height="56"><path d="M6 3h12v18l-6-4-6 4z" style="fill:#FFE03A"/></svg>Save it · check back in 10 years</span><span><svg viewBox="0 0 24 24" width="56" height="56"><path d="M3 11l18-8-8 18-2-8z" style="fill:none;stroke:#fff;stroke-width:2;stroke-linejoin:round"/></svg>Send to someone buying land</span></div>
<div id="credits"><b>CREDITS, SOURCES &amp; REFERENCES</b><p>MagicBricks (2026 Residential Plot Trends) · Housing.com (Jaipur Property Rates) · Rajasthan Registration &amp; Stamps Department (DLC Rates) · Rajasthan GIS Portal · Kapil Raisinghani (historical land-price account)</p><p>Terrain: Copernicus DEM GLO-30 (height ×4) · Imagery: contains modified Copernicus Sentinel-2 data (2024) · Landsat 5/9 courtesy NASA/USGS</p><b>DISCLAIMER</b><p>1990–1995 prices are historical estimates; 2026 prices are indicative market rates based on property listings. Appreciation multipliers are calculated estimates, not verified investment returns.</p><i>ASHWILLPOWER · JAIPUR REAL ESTATE</i></div>
<div id="cover"><div id="cvt"><small>UP TO</small>1,000×<br/><span>IN 35 YEARS</span></div><div id="cvs">Jaipur land prices · in 3D</div><div id="cvimg"><img src="assets/city_1989.jpg"/><div id="cvb"><img src="assets/city_2025.jpg"/></div><i></i><b class="l">1989</b><b class="r">2024</b></div><div id="cvpill">10 areas · south → north · in 3D</div></div>
<audio id="music" class="clip" src="assets/music_tune.mp3" data-start="0" data-duration="__END__" data-track-index="10" data-volume="0.14" data-fade-in="0.3" data-fade-out="2"></audio>
</div>
<script>__TL__</script>
<script type="module">
import * as THREE from "./assets/lib/three.module.min.js";
const M = __META__;
const TOUR = __TOUR__;
const END = __END__;
const SX = M.sx, SZ = M.sz, EX = 4.0;   // world units = 100 m; height exaggeration
const canvas = document.getElementById("gl");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(1080, 1920, false);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1c2230); scene.fog = new THREE.Fog(0x1c2230, 230, 520);
const camera = new THREE.PerspectiveCamera(42, 1080 / 1920, 0.5, 2000);
scene.add(new THREE.HemisphereLight(0xdfe8ff, 0x3a2a1a, 0.9));
const sun = new THREE.DirectionalLight(0xffe2b8, 2.2); sun.position.set(-200, 160, -120); scene.add(sun);

function loadImg(src){ return new Promise((res, rej) => { const im = new Image(); im.onload = () => res(im); im.onerror = rej; im.src = src; }); }
let H; // height lookup
function hAt(u, v){ // u,v in 0..1
  const x = Math.min(M.dw - 1, Math.max(0, u * (M.dw - 1))), y = Math.min(M.dh - 1, Math.max(0, v * (M.dh - 1)));
  const x0 = Math.floor(x), y0 = Math.floor(y), x1 = Math.min(M.dw - 1, x0 + 1), y1 = Math.min(M.dh - 1, y0 + 1), fx = x - x0, fy = y - y0;
  const g = (a, b) => H[b * M.dw + a];
  return (g(x0,y0)*(1-fx)+g(x1,y0)*fx)*(1-fy) + (g(x0,y1)*(1-fx)+g(x1,y1)*fx)*fy;
}
const wx = u => (u - .5) * SX, wz = v => (v - .5) * SZ;
const bars = [], labels = [];
const ready = (async () => {
  const [dem, tex] = await Promise.all([loadImg("assets/dem.png"), loadImg("assets/tex.jpg")]);
  const c = document.createElement("canvas"); c.width = dem.width; c.height = dem.height;
  const cx = c.getContext("2d"); cx.drawImage(dem, 0, 0); const px = cx.getImageData(0, 0, dem.width, dem.height).data;
  H = new Float32Array(dem.width * dem.height);
  for (let i = 0; i < H.length; i++) H[i] = ((px[i*4] << 8) | px[i*4+1]) / 65535 * 400 / 100 * EX; // (m-300)/100*EX
  const seg = 400, geo = new THREE.PlaneGeometry(SX, SZ, seg, seg); geo.rotateX(-Math.PI / 2);
  const pos = geo.attributes.position;
  for (let i = 0; i < pos.count; i++) { const u = pos.getX(i) / SX + .5, v = pos.getZ(i) / SZ + .5; pos.setY(i, hAt(u, v)); }
  geo.computeVertexNormals();
  const t = new THREE.Texture(tex); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; t.needsUpdate = true;
  scene.add(new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ map: t, roughness: .95, metalness: 0 })));
  const L = document.getElementById("labels");
  M.areas.forEach((a, k) => {
    const m = a.p1 / a.p0, h = 6 + m / 1200 * 42, base = hAt(a.u, a.v);
    const g = new THREE.CylinderGeometry(3.2, 3.2, 1, 40); g.translate(0, .5, 0);
    const kk = Math.min(1, m / 1200); const col = new THREE.Color().setHSL(0.27 + 0.10 * kk, .8, .58 - .2 * kk);
    const mat = new THREE.MeshStandardMaterial({ color: col, emissive: col, emissiveIntensity: .3, roughness: .4, metalness: .1 });
    const bar = new THREE.Mesh(g, mat); bar.position.set(wx(a.u), base, wz(a.v)); bar.scale.y = .001; scene.add(bar);
    const ring = new THREE.Mesh(new THREE.RingGeometry(3.2, 4.6, 48), new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: .8, side: THREE.DoubleSide }));
    ring.rotation.x = -Math.PI / 2; ring.position.set(wx(a.u), base + .3, wz(a.v)); scene.add(ring);
    bars.push({ bar, ring, h, base, k, m });
    const mult = m >= 1000 ? Math.round(m / 100) * 100 : Math.round(m / 10) * 10;
    const fmt = v => v >= 100000 ? "₹" + (v / 100000) + " lakh" : "₹" + v.toLocaleString("en-IN");
    const d = document.createElement("div"); d.className = "lb"; d.innerHTML = `<b>${a.name.split(" ·")[0]}</b><span>~${mult.toLocaleString("en-IN")}×</span><i>${fmt(a.p0)} → ${fmt(a.p1)} / sq yd</i>`;
    L.appendChild(d); labels.push(d);
  });
})();
window.__hf = window.__hf || {}; window.__hf.buildReady = window.__hf.buildReady || {}; window.__hf.buildReady["terrain"] = ready;

// camera keys: [time, camPos(u,v,height), target(u,v,height)]
const A = i => M.areas[i];
const T3 = __T3__, TS = __TS__, DS = __DS__, TO = __TO__, STOPS = __STOPS__;
const keys = [
  [0.0, [.50, .56, 560], [.50, .50, 0]],
  [T3, [.50, .58, 540], [.50, .50, 0]],
  [T3 + 2.4, [.52, 1.05, 260], [.47, .52, 0]],
  [TS - .9, [.50, .98, 220], [.47, .50, 0]],
];
TOUR.forEach((i, n) => { const a = A(i), t = STOPS[n], nx = n + 1 < STOPS.length ? STOPS[n + 1] : TO;
  keys.push([t - .05, [a.u + .09, a.v + .29, 112], [a.u, a.v - .02, 20]]); keys.push([nx - .85, [a.u + .03, a.v + .26, 100], [a.u, a.v - .02, 22]]); });
keys.push([TO + 1.6, [.50, 1.0, 240], [.47, .50, 0]]);
keys.push([END, [.50, 1.02, 250], [.47, .50, 0]]);
const sm = x => x * x * (3 - 2 * x);
function camAt(t){
  let i = 0; while (i < keys.length - 2 && t > keys[i + 1][0]) i++;
  const [t0, p0, q0] = keys[i], [t1, p1, q1] = keys[i + 1];
  const f = sm(Math.min(1, Math.max(0, (t - t0) / (t1 - t0))));
  const L = (a, b) => a.map((x, j) => x + (b[j] - x) * f);
  return [L(p0, p1), L(q0, q1)];
}
const v3 = new THREE.Vector3();
function renderAt(t){
  if (!H || t < T3 - .3) return;
  const [p, q] = camAt(t);
  camera.position.set(wx(p[0]), p[2], wz(p[1])); camera.lookAt(wx(q[0]), q[2], wz(q[1])); camera.updateMatrixWorld(true);
  let fi = -1; for (let n = 0; n < STOPS.length; n++) if (t >= STOPS[n] - .1) fi = n; const focus = (fi >= 0 && t < TO + .3) ? TOUR[fi] : -1;
  bars.forEach((b, j) => {
    const g = Math.min(1, Math.max(0, (t - T3 - 1.6 - j * .2) / 1.1)); const e = 1 - Math.pow(1 - g, 3);
    b.bar.scale.y = Math.max(.001, b.h * e); b.bar.material.emissiveIntensity = (focus === j ? .6 : .25) + .08 * Math.sin(t * 4 + j);
    b.ring.material.opacity = .25 + .55 * e; const s = 1 + .25 * Math.sin(t * 3 + j); b.ring.scale.set(s, s, s);
    v3.set(b.bar.position.x, b.base + b.h * e + 2, b.bar.position.z).project(camera);
    const d = labels[j], vis = e > .6 && v3.z < 1 && Math.abs(v3.x) < .8 && v3.y < .78 && v3.y > -.2 && t < TO + .5;
    d.style.left = ((v3.x + 1) / 2 * 1080).toFixed(1) + "px"; d.style.top = Math.max(focus === j ? 650 : 300, (1 - v3.y) / 2 * 1920).toFixed(1) + "px";
    d.style.opacity = vis ? (focus < 0 || focus === j ? 1 : 0) : 0; d.classList.toggle("hot", focus === j);
  });
  renderer.render(scene, camera);
}
window.addEventListener("hf-seek", e => { if (H) renderAt(e.detail.time); else e.detail.waitUntil(ready.then(() => renderAt(e.detail.time))); });
ready.then(() => renderAt(0));
</script></body></html>"""

# ------------- 2D timeline (face hook, slider, captions, counter, CTA) -------------
J=[]; CAPS=[]
def cap(i, html, a, b, top=None):
    CAPS.append(f'<div class="st" id="{i}"' + (f' style="top:{top}px"' if top else '') + f'><span>{html}</span></div>')
    J.append(f'tl.fromTo("#{i}",{{opacity:0,y:16,scale:.96}},{{opacity:1,y:0,scale:1,duration:.2,ease:"back.out(2)"}},{a:.2f}); tl.to("#{i}",{{opacity:0,duration:.12}},{b - .12:.2f});')
Y='<span class="y">'; E='</span>'
HOOK=('<div class="full" id="h89"><img src="assets/city_1989.jpg"/></div><div class="full" id="h24"><img src="assets/city_2025.jpg"/></div><div id="hline"><b>⟷</b></div>'
      '<div class="full" id="pre"><img class="bgb" src="assets/city_2025.jpg"/><div id="card"><img src="assets/city_2025.jpg"/><div id="pins"><div class="pin" id="pq0" style="left:853px;top:1336px"><i></i><b class="r">Jagatpura <span class="y">~1,200×</span></b></div><div class="pin" id="pq1" style="left:343px;top:1131px"><i></i><b class="r">Mansarovar <span class="y">~570×</span></b></div><div class="pin" id="pq2" style="left:212px;top:792px"><i></i><b class="">Vaishali Nagar <span class="y">~580×</span></b></div><div class="pin" id="pq3" style="left:770px;top:1607px"><i></i><b class="r">Sitapura <span class="y">~1,200×</span></b></div><div class="pin" id="pq4" style="left:645px;top:1482px"><i></i><b class="">Pratap Nagar <span class="y">~790×</span></b></div><div class="pin" id="pq5" style="left:199px;top:572px"><i></i><b class="">Jhotwara <span class="y">~350×</span></b></div><div class="pin" id="pq6" style="left:60px;top:1039px"><i></i><b class="">Ajmer Road <span class="y">~710×</span></b></div><div class="pin" id="pq7" style="left:424px;top:501px"><i></i><b class="">Vidyadhar Nagar <span class="y">~620×</span></b></div><div class="pin" id="pq8" style="left:367px;top:331px"><i></i><b class="">Sikar Road <span class="y">~920×</span></b></div><div class="pin" id="pq9" style="left:626px;top:1148px"><i></i><b class="">Malviya Nagar <span class="y">~500×</span></b></div></div></div></div><div class="yl2" id="hl89">1989</div><div class="yl2 r" id="hl24">2024</div><div id="hprice"><b id="hp">₹50 – 300</b><i id="hpi">PER GAJ · 1990</i></div>')
TOPS=('<div id="ss"><span><svg viewBox="0 0 24 24" width="38" height="38"><path d="M6 3h12v18l-6-4-6 4z" style="fill:#FFE03A"/></svg>SAVE this</span><span><svg viewBox="0 0 24 24" width="38" height="38"><path d="M3 11l18-8-8 18-2-8z" style="fill:none;stroke:#fff;stroke-width:2.4;stroke-linejoin:round"/></svg>SHARE it</span></div>'
      '<div id="hh"><i class="up">UP TO</i><b>1,000×</b></div>')
F=FACE_END
J += ['tl.set("#cover",{opacity:0},0);',
      f'tl.set("#hook",{{opacity:0}},0); tl.set("#hook",{{opacity:1}},{F:.2f}); tl.fromTo("#avatar",{{opacity:1}},{{opacity:0,duration:.01}},{F + .05:.2f});',
      f'tl.fromTo("#h89 img,#h24 img",{{scale:1}},{{scale:1.07,duration:{T3 - F:.2f},ease:"none"}},{F:.2f});',
      'tl.to("#h24",{clipPath:"inset(0 0 0 50%)",duration:1.0,ease:"power2.inOut"},7.9); tl.to("#h24",{clipPath:"inset(0 0 0 0%)",duration:1.0,ease:"power2.inOut"},9.8);',
      'tl.set("#hline",{x:1080},0); tl.set("#hline",{opacity:1},7.9); tl.to("#hline",{x:540,duration:1.0,ease:"power2.inOut"},7.9); tl.to("#hline",{x:0,duration:1.0,ease:"power2.inOut"},9.8); tl.to("#hline",{opacity:0,duration:.2},10.8);',
      f'tl.fromTo("#hl89",{{opacity:0}},{{opacity:1,duration:.3}},5.7); tl.to("#hl89",{{opacity:0,duration:.3}},10.4); tl.fromTo("#hl24",{{opacity:0}},{{opacity:1,duration:.3}},8.5); tl.to("#hl24",{{opacity:0,duration:.3}},{T3:.2f});',
      'tl.set("#pre",{opacity:1},0); tl.to("#pre",{opacity:0,duration:.4},5.55); tl.fromTo("#card",{scale:.95},{scale:.8,duration:.6,ease:"power2.out"},2.0);',
      'tl.fromTo("#pq0",{opacity:0,scale:.3},{opacity:1,scale:1,duration:.25,ease:"back.out(3)"},2.40);',
      'tl.fromTo("#pq1",{opacity:0,scale:.3},{opacity:1,scale:1,duration:.25,ease:"back.out(3)"},2.60);',
      'tl.fromTo("#pq2",{opacity:0,scale:.3},{opacity:1,scale:1,duration:.25,ease:"back.out(3)"},2.80);',
      'tl.fromTo("#pq3",{opacity:0,scale:.3},{opacity:1,scale:1,duration:.25,ease:"back.out(3)"},3.00);',
      'tl.fromTo("#pq4",{opacity:0,scale:.3},{opacity:1,scale:1,duration:.25,ease:"back.out(3)"},3.20);',
      'tl.fromTo("#pq5",{opacity:0,scale:.3},{opacity:1,scale:1,duration:.25,ease:"back.out(3)"},3.40);',
      'tl.fromTo("#pq6",{opacity:0,scale:.3},{opacity:1,scale:1,duration:.25,ease:"back.out(3)"},3.60);',
      'tl.fromTo("#pq7",{opacity:0,scale:.3},{opacity:1,scale:1,duration:.25,ease:"back.out(3)"},3.80);',
      'tl.fromTo("#pq8",{opacity:0,scale:.3},{opacity:1,scale:1,duration:.25,ease:"back.out(3)"},4.00);',
      'tl.fromTo("#pq9",{opacity:0,scale:.3},{opacity:1,scale:1,duration:.25,ease:"back.out(3)"},4.20);',
      'tl.fromTo("#ss",{opacity:0,y:-30},{opacity:1,y:0,duration:.35,ease:"back.out(2)"},0.6); tl.to("#ss span",{scale:1.08,duration:.3,yoyo:true,repeat:3,stagger:.15},1.0); tl.to("#ss",{opacity:0,duration:.25},2.3);',
      'tl.fromTo("#hh",{opacity:0,scale:1.6},{opacity:1,scale:1,duration:.45,ease:"back.out(2)"},1.4); tl.to("#hh",{opacity:0,duration:.25},2.3);',
      'tl.fromTo("#hprice",{opacity:0,scale:.6},{opacity:1,scale:1,duration:.4,ease:"back.out(2)"},10.1); tl.to("#hprice",{opacity:0,duration:.3},15.75);',
      'tl.call(()=>{document.getElementById("hp").textContent="₹50 – 300";document.getElementById("hpi").textContent="PER GAJ · 1990"},null,10.0);',
      'tl.call(()=>{document.getElementById("hp").textContent="₹40,000 – 1.5 lakh";document.getElementById("hpi").textContent="PER GAJ · TODAY"},null,12.88); tl.fromTo("#hp",{scale:1.35},{scale:1,duration:.5,ease:"back.out(2)"},12.88);',
      f'tl.to("#gl",{{opacity:1,duration:.01}},{T3 - .3:.2f}); tl.to("#hook",{{opacity:0,duration:.9,ease:"power1.in"}},{T3:.2f});']
cap("v0", f"Jaipur has given {Y}up to 1,000×{E}", .9, 3.15, top=1530)
cap("v1", f"returns in the {Y}last 35 years{E}", 3.2, 5.6, top=1530)
cap("v2", f"This is Jaipur in {Y}1989{E}", 5.68, 7.88)
cap("v3", f"and this is {Y}today.{E}", 7.92, 9.3)
cap("v4", f"Back then: {Y}₹50 to ₹300{E} a gaj", 9.36, 12.84)
cap("v5", f"Today: {Y}₹40,000 to ₹1.5 lakh{E}", 12.88, 15.88)
cap("v6", f"Now watch it {Y}in 3D{E}", 15.92, 17.58)
cap("v7", f"The taller the bar, {Y}the bigger the jump{E}", 17.6, 19.34)
for n, i in enumerate(TOUR):
    a = M['areas'][i]; m = a['p1'] / a['p0']; t = STOPS[n]; nx = STOPS[n + 1] if n + 1 < len(STOPS) else TO
    mm = f"~{round(m, -2) if m >= 1000 else round(m, -1):,.0f}×"
    f = lambda v: f"₹{v / 100000:g} lakh" if v >= 100000 else f"₹{v:,}"
    cap(f"a{n}", f"{a['name'].split(' ·')[0]}: {Y}{mm}{E}<small>{f(a['p0'])} → {f(a['p1'])} per sq yd</small>", t, nx - .02)
    J.append(f'tl.call(()=>{{document.getElementById("rk").textContent="{n + 1} / {len(TOUR)}"}},null,{t - .05:.2f}); tl.fromTo("#rank b",{{scale:1.5}},{{scale:1,duration:.35,ease:"back.out(2.5)"}},{t:.2f});')
J.append(f'tl.fromTo("#rank",{{opacity:0}},{{opacity:1,duration:.3}},{TS - .1:.2f}); tl.to("#rank",{{opacity:0,duration:.3}},{TO:.2f});')
J.append(f'tl.fromTo("#fine",{{opacity:0}},{{opacity:1,duration:.3}},9.9); tl.to("#fine",{{opacity:0,duration:.3}},{TO:.2f});')
cap("e0", f"Which area in Jaipur will be {Y}the next 1,000×?{E}", 53.08, 56.4)
cap("e1", "Comment below 👇", 56.44, 57.45)
cap("e2", f"Save this reel &amp; {Y}send it{E} to someone planning to buy a plot", 57.48, 60.72)
cap("e3", f"Don't get late — {Y}and if you want, contact me.{E}", 60.76, 63.75)
J.append(f'tl.fromTo("#cta",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.4}},56.4); tl.to("#cta svg",{{scale:1.15,duration:.4,yoyo:true,repeat:5}},56.9); tl.to("#cta",{{opacity:0,duration:.3}},63.7);')
J.append(f'tl.fromTo("#credits",{{opacity:0}},{{opacity:1,duration:.4}},63.85);')
J.append(f'tl.to("#brand",{{opacity:0,duration:.3}},63.85);')
SFX=[]
def sfx(n,t,v=.25): SFX.append(f'<audio class="clip" src="assets/sfx/{n}.mp3" data-start="{t:.2f}" data-duration="2" data-track-index="{20 + len(SFX)}" data-volume="{v}"></audio>')
sfx("impact-bass-1",1.4,.3); sfx("whoosh",7.9,.22); sfx("ping",12.88,.22); sfx("whoosh",T3,.3)
for j in range(len(TOUR)): sfx("click-soft",T3+1.6+.2*j,.15)
for n in range(len(TOUR)): sfx("whoosh-short",STOPS[n]-.8,.2)
sfx("sparkle",53.08,.22)
TL = 'const tl = gsap.timeline({ paused: true });\n' + "\n".join(J) + '\nwindow.__timelines = window.__timelines || {}; window.__timelines["main"] = tl;'
HTML = HTML.replace("__HOOK__", HOOK).replace("__TOPS__", TOPS).replace("__CAPS__", "".join(CAPS)).replace("__TL__", TL).replace('<audio id="music"', "".join(SFX) + '<audio id="music"')
HTML = HTML.replace("__T3__", str(T3)).replace("__TS__", str(TS)).replace("__DS__", str(DS)).replace("__TO__", str(TO)).replace("__STOPS__", json.dumps(STOPS))
html = HTML.replace("__META__", json.dumps(M)).replace("__TOUR__", json.dumps(TOUR)).replace("__END__", str(END))
open("reel_calm/index.html", "w").write(html)
print("ok", END, TOUR, TO)
