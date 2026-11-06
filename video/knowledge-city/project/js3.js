<script type="module">
import * as THREE from "./assets/three.module.min.js";
const D = __D3__;
const W = 2304, Hh = 3072;
const wx = p => p[0] - W / 2, wz = p => p[1] - Hh / 2;
const canvas = document.getElementById("gl");
const R = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
R.setPixelRatio(1); R.setSize(1080, 1920, false); R.outputColorSpace = THREE.SRGBColorSpace; R.toneMapping = THREE.ACESFilmicToneMapping; R.toneMappingExposure = 1.1;
const scene = new THREE.Scene(); scene.background = new THREE.Color(0x2a1d3a); scene.fog = new THREE.Fog(0x3a2740, 500, 1500);
const cam = new THREE.PerspectiveCamera(46, 1080 / 1920, 1, 4000);
scene.add(new THREE.HemisphereLight(0xffe9c8, 0x30263a, 1.0));
const sun = new THREE.DirectionalLight(0xffc98a, 2.4); sun.position.set(-300, 260, 200); scene.add(sun);
function img(src){ return new Promise((r, j) => { const i = new Image(); i.onload = () => r(i); i.onerror = j; i.src = src; }); }
let ok = false; const B = [], LB = []; let road, spur, head;
const ready = (async () => {
  const tex = new THREE.Texture(await img("assets/img/sat.jpg")); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8; tex.needsUpdate = true;
  const g = new THREE.PlaneGeometry(W, Hh); g.rotateX(-Math.PI / 2);
  scene.add(new THREE.Mesh(g, new THREE.MeshStandardMaterial({ map: tex, roughness: 1, color: 0x9a8f9c })));
  const curve = new THREE.CatmullRomCurve3(D.road.map(p => new THREE.Vector3(wx(p), 1.2, wz(p))));
  road = new THREE.Mesh(new THREE.TubeGeometry(curve, 600, 4.2, 8, false), new THREE.MeshStandardMaterial({ color: 0xffd36b, emissive: 0xffb000, emissiveIntensity: 1.4 }));
  scene.add(road); road.userData.n = road.geometry.index.count;
  scene.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 600, 3.0, 6, false), new THREE.MeshBasicMaterial({ color: 0xffe2a0, transparent: true, opacity: .35 })));
  const sc = new THREE.CatmullRomCurve3(D.spur.map(p => new THREE.Vector3(wx(p), 1.2, wz(p))));
  spur = new THREE.Mesh(new THREE.TubeGeometry(sc, 80, 3.6, 8, false), new THREE.MeshStandardMaterial({ color: 0x5cf08a, emissive: 0x2fd47a, emissiveIntensity: 1.3 }));
  scene.add(spur); spur.userData.n = spur.geometry.index.count;
  head = new THREE.Mesh(new THREE.SphereGeometry(5, 20, 20), new THREE.MeshBasicMaterial({ color: 0xfff4d0 })); scene.add(head);
  head.add(new THREE.PointLight(0xffc860, 3, 120));
  const rl = document.createElement('div'); rl.id = 'rlab'; rl.innerHTML = '<b>DIGGI MALPURA ROAD</b><i>SH-12 →</i>'; document.getElementById('l3').appendChild(rl);
  const kc = new THREE.Vector3(wx(D.kc), 0, wz(D.kc));
  const wc = document.createElement("canvas"); wc.width = 64; wc.height = 256; const g2 = wc.getContext("2d"); g2.fillStyle = "#000"; g2.fillRect(0, 0, 64, 256);
  let sd = 7; const rn = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
  for (let y = 4; y < 252; y += 10) for (let x = 4; x < 60; x += 10) if (rn() > .35) { g2.fillStyle = rn() > .5 ? "#ffd27a" : "#fff0c8"; g2.fillRect(x, y, 6, 6); }
  const wtex = new THREE.CanvasTexture(wc); wtex.colorSpace = THREE.SRGBColorSpace;
  D.blocks.forEach((b, k) => {
    const geo = new THREE.BoxGeometry(b.w, 1, b.d); geo.translate(0, .5, 0);
    const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: b.c, emissive: 0xffffff, emissiveMap: wtex, emissiveIntensity: 1.1, roughness: .35, metalness: .25 }));
    m.position.set(kc.x + b.x, 0, kc.z + b.z); m.scale.y = .001; scene.add(m);
    m.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo), new THREE.LineBasicMaterial({ color: 0xfff1c9, transparent: true, opacity: .7 })));
    B.push({ m, h: b.h, k });
    if (b.label) { const d = document.createElement("div"); d.className = "l3"; d.textContent = b.label; document.getElementById("l3").appendChild(d); LB.push({ d, m, h: b.h }); }
  });
  ok = true;
})();
window.__hf = window.__hf || {}; window.__hf.buildReady = window.__hf.buildReady || {}; window.__hf.buildReady["k3d"] = ready;
const sm = x => x * x * (3 - 2 * x), cl = x => Math.max(0, Math.min(1, x));
const v = new THREE.Vector3();
function rise(t, k) {
  let e = 0;
  if (t < 20) { const a = cl((t - 5.0 - k * .03) / .55); e = 1 - Math.pow(1 - a, 3); e *= 1 - sm(cl((t - 7.6 - k * .01) / 1.2)); }
  else { const a = cl((t - 48.0 - k * .025) / .55); e = 1 - Math.pow(1 - a, 3); }
  return e;
}
function renderAt(t) {
  if (!ok) return;
  if (!((t > 1.7 && t < 9.9) || (t > 47.3 && t < 59.8))) { document.querySelectorAll('#l3 > *').forEach(d => d.style.opacity = 0); return; }
  const kc = new THREE.Vector3(wx(D.kc), 0, wz(D.kc));
  const p = t < 20 ? cl((t - 1.9) / 3.1) : 1, ps = t < 20 ? cl((t - 4.6) / .6) : 1;
  road.geometry.setDrawRange(0, Math.floor(road.userData.n * sm(p) / 6) * 6);
  spur.geometry.setDrawRange(0, Math.floor(spur.userData.n * ps / 6) * 6);
  const rc = road.geometry.parameters.path, scv = spur.geometry.parameters.path;
  const hp = p < 1 ? rc.getPointAt(sm(p)) : scv.getPointAt(ps); head.position.copy(hp).setY(6); head.visible = t < 5.4;
  if (t < 4.8) {
    const q = sm(p); const a = rc.getPointAt(Math.max(0, q - .16));
    const b2 = rc.getPointAt(Math.min(1, q + .10)); cam.position.set(a.x + 60, 330 - 60 * q, a.z - 70); cam.lookAt(b2.x, 0, b2.z);
  } else {
    const ph = t < 20 ? (t - 4.8) : (t - 47.4) + 3;
    const blend = t < 20 ? sm(cl((t - 4.8) / 1.0)) : 1;
    const ang = .9 + ph * .08, rad = 470 - 60 * Math.min(1, ph / 4), hgt = 300 - 50 * Math.min(1, ph / 4);
    const target = new THREE.Vector3(kc.x, 25, kc.z), orb = new THREE.Vector3(kc.x + Math.cos(ang) * rad, hgt, kc.z + Math.sin(ang) * rad);
    if (blend < 1) { const a = rc.getPointAt(.84); const from = new THREE.Vector3(a.x + 60, 270, a.z - 70); cam.position.copy(from.lerp(orb, blend)); }
    else cam.position.copy(orb);
    cam.lookAt(target);
  }
  cam.updateMatrixWorld(true);
  { const rl = document.getElementById('rlab'); v.copy(head.position).setY(14).project(cam); const vis = t > 2.0 && t < 5.3; rl.style.left = ((v.x + 1) / 2 * 1080 + 40).toFixed(1) + 'px'; rl.style.top = ((1 - v.y) / 2 * 1920).toFixed(1) + 'px'; rl.style.opacity = vis ? 1 : 0; }
  B.forEach(b => { const e = rise(t, b.k); b.m.scale.y = Math.max(.001, b.h * e); b.m.visible = e > .002; });
  LB.forEach(l => { v.set(l.m.position.x, l.m.scale.y + 6, l.m.position.z).project(cam);
    const vis = l.m.scale.y > l.h * .8 && v.z < 1 && Math.abs(v.x) < .78 && v.y < .62 && v.y > -.35; l.d.style.left = ((v.x + 1) / 2 * 1080).toFixed(1) + "px"; l.d.style.top = ((1 - v.y) / 2 * 1920).toFixed(1) + "px"; l.d.style.opacity = vis ? 1 : 0; });
  R.render(scene, cam);
}
window.addEventListener("hf-seek", e => { if (ok) renderAt(e.detail.time); else e.detail.waitUntil(ready.then(() => renderAt(e.detail.time))); });
ready.then(() => renderAt(0));
</script>
