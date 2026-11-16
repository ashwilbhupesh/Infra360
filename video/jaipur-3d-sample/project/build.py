"""3D sample: Jaipur terrain (Copernicus DEM, Sentinel-2 drape) with price-multiplier bars rising per area and a drone camera path."""
import json
M = json.load(open("proj/assets/meta.json"))
END = 15.0
# three areas the camera visits (index into areas)
TOUR = [0, 1, 2]  # Jagatpura, Mansarovar, Vaishali Nagar
HTML = """<!doctype html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script>
<style>*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#05070b}
#root{position:relative;width:1080px;height:1920px;overflow:hidden}#gl{position:absolute;inset:0;width:1080px;height:1920px}
.lb{position:absolute;left:0;top:0;transform:translate(-50%,-100%);opacity:0;text-align:center;white-space:nowrap;font-family:Inter,Arial,sans-serif}
.lb b{display:block;padding:6px 16px;border-radius:14px 14px 0 0;background:rgba(6,8,12,.78);font-weight:900;font-size:34px;color:#fff}
.lb span{display:block;padding:2px 16px 8px;border-radius:0 0 14px 14px;background:rgba(6,8,12,.78);font-weight:900;font-size:44px;color:#FFE03A}
.lb.hot b{font-size:46px}.lb.hot span{font-size:64px}.lb.hot i{display:block;margin-top:6px;padding:4px 12px;border-radius:10px;background:rgba(6,8,12,.8);font:700 26px "JetBrains Mono",monospace;font-style:normal;color:#fff}
.lb i{display:none}
.st{position:absolute;left:50px;right:50px;top:1330px;text-align:center;opacity:0}.st>span{display:inline-block;padding:14px 28px 16px;border-radius:24px;background:rgba(6,8,12,.62);font:900 66px/1.1 Inter,Arial,sans-serif;color:#fff;text-shadow:0 4px 0 #000}
.y{color:#FFE03A}
#brand{position:absolute;left:0;right:0;top:150px;text-align:center;font:700 24px "JetBrains Mono",monospace;letter-spacing:.2em;color:rgba(255,255,255,.85);text-shadow:0 2px 6px #000}
#tag3d{position:absolute;left:0;right:0;top:230px;text-align:center;opacity:0}#tag3d span{display:inline-block;padding:10px 22px;border-radius:14px;background:rgba(6,8,12,.75);font:800 30px "JetBrains Mono",monospace;letter-spacing:.14em;color:#FFE03A}
#fine{position:absolute;left:50px;right:50px;bottom:250px;text-align:center;font:500 20px/1.35 "JetBrains Mono",monospace;color:rgba(255,255,255,.8);padding:10px 16px;border-radius:14px;background:rgba(6,8,12,.7)}
#credit{position:absolute;left:40px;right:40px;bottom:90px;text-align:center;font:500 18px "JetBrains Mono",monospace;color:rgba(255,255,255,.65);text-shadow:0 1px 3px #000}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="__END__" data-width="1080" data-height="1920" data-fps="30">
<canvas id="gl" width="1080" height="1920"></canvas>
<div id="labels"></div>
<div id="brand">ASHWILLPOWER · JAIPUR REAL ESTATE</div>
<div id="tag3d"><span>JAIPUR · 3D · LAND PRICE GROWTH 1990 → TODAY</span></div>
<div class="st" id="s0"><span>Taller bar = <span class="y">bigger jump</span></span></div>
<div class="st" id="s1"><span>Jagatpura: <span class="y">~1,200×</span></span></div>
<div class="st" id="s2"><span>Mansarovar: <span class="y">~570×</span></span></div>
<div class="st" id="s3"><span>Vaishali Nagar: <span class="y">~580×</span></span></div>
<div id="fine">Approx. rates · historical estimates &amp; indicative listing rates · not verified investment returns</div>
<div id="credit">Terrain: Copernicus DEM GLO-30 · Imagery: contains modified Copernicus Sentinel-2 data (2024) · height ×4</div>
<audio id="music" class="clip" src="assets/music_tune.mp3" data-start="0" data-duration="__END__" data-track-index="10" data-volume="0.8" data-fade-in="0.3" data-fade-out="2"></audio>
</div>
<script>
const tl = gsap.timeline({ paused: true });
function st(id,a,b){ tl.fromTo(id,{opacity:0,y:20},{opacity:1,y:0,duration:.3,ease:"back.out(2)"},a); tl.to(id,{opacity:0,duration:.2},b-.2); }
tl.fromTo("#tag3d",{opacity:0},{opacity:1,duration:.4},0.3); tl.to("#tag3d",{opacity:0,duration:.3},2.0);
st("#s0",1.0,4.8); st("#s1",5.6,8.8); st("#s2",8.9,11.8); st("#s3",11.9,14.9);
window.__timelines = window.__timelines || {}; window.__timelines["main"] = tl;
</script>
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
    const col = new THREE.Color().setHSL(0.12 - 0.11 * Math.min(1, m / 1200), .95, .5);
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
const keys = [
  [0.0, [.50, 1.25, 330], [.48, .52, 0]],
  [4.6, [.50, 1.02, 210], [.47, .50, 0]],
];
const tourT = [5.4, 8.7, 11.8];
TOUR.forEach((i, n) => { const a = A(i); keys.push([tourT[n], [a.u + .10, a.v + .30, 115], [a.u, a.v - .02, 20]]); keys.push([tourT[n] + 2.6, [a.u + .04, a.v + .27, 105], [a.u, a.v - .02, 22]]); });
keys.push([END, [A(TOUR[2]).u, A(TOUR[2]).v + .25, 100], [A(TOUR[2]).u, A(TOUR[2]).v - .02, 24]]);
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
  if (!H) return;
  const [p, q] = camAt(t);
  camera.position.set(wx(p[0]), p[2], wz(p[1])); camera.lookAt(wx(q[0]), q[2], wz(q[1])); camera.updateMatrixWorld(true);
  const focus = t >= 5.4 ? TOUR[Math.min(2, Math.floor((t - 5.4) / 3.25))] : -1;
  bars.forEach((b, j) => {
    const g = Math.min(1, Math.max(0, (t - 1.2 - j * .22) / 1.1)); const e = 1 - Math.pow(1 - g, 3);
    b.bar.scale.y = Math.max(.001, b.h * e); b.bar.material.emissiveIntensity = (focus === j ? .6 : .25) + .08 * Math.sin(t * 4 + j);
    b.ring.material.opacity = .25 + .55 * e; const s = 1 + .25 * Math.sin(t * 3 + j); b.ring.scale.set(s, s, s);
    v3.set(b.bar.position.x, b.base + b.h * e + 2, b.bar.position.z).project(camera);
    const d = labels[j], vis = e > .6 && v3.z < 1 && Math.abs(v3.x) < .8 && v3.y < .82 && v3.y > -.6;
    d.style.left = ((v3.x + 1) / 2 * 1080).toFixed(1) + "px"; d.style.top = ((1 - v3.y) / 2 * 1920).toFixed(1) + "px";
    d.style.opacity = vis ? (focus < 0 || focus === j ? 1 : 0) : 0; d.classList.toggle("hot", focus === j);
  });
  renderer.render(scene, camera);
}
window.addEventListener("hf-seek", e => { if (H) renderAt(e.detail.time); else e.detail.waitUntil(ready.then(() => renderAt(e.detail.time))); });
ready.then(() => renderAt(0));
</script></body></html>"""
html = HTML.replace("__META__", json.dumps(M)).replace("__TOUR__", json.dumps(TOUR)).replace("__END__", str(END))
open("proj/index.html", "w").write(html)
print("ok", END)
