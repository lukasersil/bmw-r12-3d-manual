import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { Parts } from './core/parts.js';
import { createStage } from './stage.js';
import { createIntro } from './intro.js';
import { studioEnvironment, addSurfaceGrain } from './look.js';
import { initUI } from './ui.js';

// Full manual texts when present, otherwise titles and specifications only.
let DATA;
try {
  DATA = await import('./data/content.js');
} catch {
  DATA = await import('./data/content-stub.js');
}

const host = document.getElementById('stage3d');
const BG = 0x0c0c0c;
const TOUCH = window.matchMedia('(hover: none)').matches;
const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(host.clientWidth, host.clientHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.NeutralToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
renderer.setClearColor(BG, 1);
host.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(BG);
// reflections from a photo studio: overhead softbox, two strip lights, warm fill
scene.environment = studioEnvironment(renderer);
scene.environmentIntensity = 1.0;

// key light front-left above, rim light behind on the right, soft fill from below the horizon
const key = new THREE.DirectionalLight(0xffffff, 1.9);
key.position.set(1.8, 3.2, -1.6);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
key.shadow.camera.left = -1.6; key.shadow.camera.right = 1.6;
key.shadow.camera.top = 1.6; key.shadow.camera.bottom = -1.6;
key.shadow.camera.near = 0.5; key.shadow.camera.far = 8;
key.shadow.bias = -0.0004;
key.shadow.normalBias = 0.02;
key.shadow.radius = 4;
scene.add(key);
const rim = new THREE.DirectionalLight(0xdfe8ff, 1.3);
rim.position.set(-2.4, 1.6, 2.4);
scene.add(rim);
const hemi = new THREE.HemisphereLight(0xffffff, 0x202020, 0.35);
scene.add(hemi);

// promo studio: backdrop, reflective floor, light cone, dust, lettering wall
const stage = await createStage({ scene, touch: TOUCH });

// ------------------------------------------------------------------ the motorcycle (GLB built in Blender, Draco, base64)
const loading = document.getElementById('loading');
function b64ToBytes(text) {
  const bin = atob(text.trim());
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}
function wasmAllowed() {
  try { new WebAssembly.Module(new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0])); return true; } catch { return false; }
}
const draco = new DRACOLoader();
draco.setDecoderPath('./draco/');
draco.setDecoderConfig({ type: wasmAllowed() ? 'wasm' : 'js' });
async function loadGLB(url) {
  const bytes = b64ToBytes(await (await fetch(url)).text()).buffer;
  return new Promise((res, rej) => new GLTFLoader().setDRACOLoader(draco).parse(bytes, './', res, rej));
}
const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
// the fractured badge for the opening sequence; without it the page simply starts on the bike
const [gltf, logoGltf] = await Promise.all([
  loadGLB('./scene/r12.txt'),
  reduced ? null : loadGLB('./scene/logo.txt').catch(() => null),
]);
draco.dispose();
const bike = gltf.scene;
bike.name = 'BMW R 12';
scene.add(bike);
const maxAniso = renderer.capabilities.getMaxAnisotropy();
bike.traverse((o) => {
  if (!o.isMesh) return;
  const m = o.material;
  if (m.map) m.map.anisotropy = maxAniso;
  if (m.name === 'glass' || m.name === 'dialglass') { m.depthWrite = false; m.roughness = 0.02; }
  if (m.name === 'redlens') m.emissiveIntensity = 1.5;
  addSurfaceGrain(m); // sand-cast aluminium, iron, rubber and leather get a fine grain
});
// every part is an empty in Blender carrying { part, explode } as glTF extras
const parts = new Parts((id) => DATA.PARTS[id]?.system);
const holders = [];
bike.traverse((o) => { if (o.userData && o.userData.part) holders.push(o); });
for (const o of holders) parts.add(o.userData.part, o, o.userData.explode ?? [0, 0, 0]);
parts.refresh();
if (loading) loading.hidden = true;

// ------------------------------------------------------------------ camera
const camera = new THREE.PerspectiveCamera(32, (host.clientWidth || window.innerWidth) / (host.clientHeight || window.innerHeight) || 1.5, 0.05, 40);
const TARGET0 = new THREE.Vector3(0, 0.46, 0);
const VIEWS = {
  iso: [2.35, 1.2, -2.55],
  left: [0.05, 0.62, -3.6],
  right: [0.05, 0.62, 3.6],
  front: [3.6, 0.72, 0.05],
  rear: [-3.6, 0.72, 0.05],
  top: [0.02, 3.9, 0.02],
};
camera.position.set(...VIEWS.iso);
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.copy(TARGET0);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 0.55;
controls.maxDistance = 10;
controls.maxPolarAngle = Math.PI * 0.495;
controls.autoRotateSpeed = 0.55;
controls.update();

// narrow screens: start further out so the whole bike fits
function fitDistance() {
  // the pane can start hidden at zero size: fall back to the window
  const w = host.clientWidth || window.innerWidth, h = host.clientHeight || window.innerHeight;
  return w && h ? THREE.MathUtils.clamp(0.93 / (w / h), 1, 2.4) : 1;
}
camera.position.sub(TARGET0).multiplyScalar(fitDistance()).add(TARGET0);
controls.update();
// the haze scales with the starting distance, so a phone (camera further out) sees the bike as clearly
const FOG = { near: scene.fog.near, far: scene.fog.far };
function fitFog() {
  scene.fog.near = FOG.near * fitDistance();
  scene.fog.far = FOG.far * fitDistance();
}
fitFog();
const endView = { position: camera.position.clone(), target: TARGET0.clone() };

// smooth camera moves: the target slides straight, the camera orbits round it (spherical, shortest way round),
// so a move from the rear to the front swings past the bike instead of flying through it
let tween = null;
const sph0 = new THREE.Spherical(), sph1 = new THREE.Spherical(), sphT = new THREE.Spherical();
function flyTo(pos, target, ms = 900) {
  const q0 = controls.target.clone(), q1 = target.clone();
  sph0.setFromVector3(camera.position.clone().sub(q0));
  sph1.setFromVector3(pos.clone().sub(q1));
  let dTheta = sph1.theta - sph0.theta;
  dTheta = Math.atan2(Math.sin(dTheta), Math.cos(dTheta));
  tween = { t0: performance.now(), ms, q0, q1, r0: sph0.radius, r1: sph1.radius, ph0: sph0.phi, ph1: sph1.phi, th0: sph0.theta, dTheta };
}
function setView(name) {
  const p = new THREE.Vector3(...VIEWS[name]);
  p.sub(TARGET0).multiplyScalar(fitDistance()).add(TARGET0);
  flyTo(p, TARGET0);
}
function focusPart(id) {
  const c = parts.center(id);
  const dist = THREE.MathUtils.clamp(parts.size(id) * 3.5, 2.6, 3.6) * fitDistance();
  const dir = camera.position.clone().sub(controls.target).normalize();
  if (dir.y < 0.12) dir.y = 0.12;
  dir.normalize();
  flyTo(c.clone().addScaledVector(dir, dist), c);
}

// ------------------------------------------------------------------ picking
const ray = new THREE.Raycaster();
const ndc = new THREE.Vector2();
let pointer = null; // last pointer position over the canvas
let down = null;
let idleSince = performance.now();

function pick(x, y) {
  const r = renderer.domElement.getBoundingClientRect();
  ndc.set(((x - r.left) / r.width) * 2 - 1, -((y - r.top) / r.height) * 2 + 1);
  ray.setFromCamera(ndc, camera);
  const hit = ray.intersectObjects(parts.pickables(), false)[0];
  return hit ? hit.object.userData.part : null;
}

const el = renderer.domElement;
el.addEventListener('pointermove', (e) => {
  if (intro?.active) return;
  pointer = { x: e.clientX, y: e.clientY, touch: e.pointerType !== 'mouse' };
  if (e.pointerType === 'mouse') ui.needsPick = true;
});
el.addEventListener('pointerleave', () => {
  pointer = null;
  ui.hover(null);
});
el.addEventListener('pointerdown', (e) => {
  if (intro?.active) return;
  down = { x: e.clientX, y: e.clientY, t: performance.now() };
  controls.autoRotate = false;
  idleSince = performance.now();
});
el.addEventListener('pointerup', (e) => {
  if (!down) return;
  const moved = Math.hypot(e.clientX - down.x, e.clientY - down.y);
  if (moved < 6 && performance.now() - down.t < 600) ui.select(pick(e.clientX, e.clientY), true);
  down = null;
  idleSince = performance.now();
});
controls.addEventListener('start', () => {
  controls.autoRotate = false;
  tween = null;
});

// ------------------------------------------------------------------ UI
const ui = initUI({
  DATA,
  parts,
  camera,
  renderer,
  actions: {
    setView,
    focusPart,
    reset: () => setView('iso'),
    interact: () => {
      controls.autoRotate = false;
      idleSince = performance.now();
    },
  },
});

// ------------------------------------------------------------------ post: ambient occlusion in the creases (desktop)
let composer = null;
if (!TOUCH) {
  // multisampled target: the composer path otherwise loses the canvas antialiasing on spokes and lines
  const rt = new THREE.WebGLRenderTarget(host.clientWidth || 1, host.clientHeight || 1, { type: THREE.HalfFloatType, samples: 4 });
  composer = new EffectComposer(renderer, rt);
  composer.addPass(new RenderPass(scene, camera));
  const ao = new GTAOPass(scene, camera, host.clientWidth, host.clientHeight);
  ao.blendIntensity = 0.85;
  ao.updateGtaoMaterial({ radius: 0.12, distanceExponent: 1.4, thickness: 1.2, scale: 1.0, samples: 16 });
  composer.addPass(ao);
  composer.addPass(new OutputPass());
}

// ------------------------------------------------------------------ loop
function resize() {
  const w = host.clientWidth, h = host.clientHeight;
  renderer.setSize(w, h);
  if (composer) composer.setSize(w, h);
  camera.aspect = w / h;
  camera.setViewOffset(w, h, -viewShift[0], viewShift[1], w, h);
  camera.updateProjectionMatrix();
  if (!intro?.active) fitFog();
}
window.addEventListener('resize', resize);

const viewShift = [0, 0];

// ------------------------------------------------------------------ opening sequence (skipped with reduced motion)
let intro = null;
if (logoGltf) {
  intro = createIntro({
    scene, camera, controls, logo: logoGltf.scene, lights: { key, rim, hemi }, target: TARGET0, endView, zoom: fitDistance(),
    onDone: () => { idleSince = performance.now(); },
  });
} else {
  const f = document.getElementById('intro-fade');
  if (f) f.hidden = true;
  document.body.classList.add('ui-ready');
}
const size = new THREE.Vector2();
renderer.setAnimationLoop((now) => {
  // the pane can start hidden (zero size): follow the host size every frame
  renderer.getSize(size);
  if (host.clientWidth && host.clientHeight && (size.x !== host.clientWidth || size.y !== host.clientHeight)) resize();
  if (!host.clientWidth || !host.clientHeight) return;
  if (tween) {
    const k = Math.min(1, (now - tween.t0) / tween.ms);
    const e = k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
    controls.target.lerpVectors(tween.q0, tween.q1, e);
    sphT.set(tween.r0 + (tween.r1 - tween.r0) * e, tween.ph0 + (tween.ph1 - tween.ph0) * e, tween.th0 + tween.dTheta * e);
    camera.position.setFromSpherical(sphT).add(controls.target);
    if (k >= 1) tween = null;
  }
  stage.update(now);
  if (intro?.active) {
    intro.update(now);
  } else {
    if (!reduced && !ui.selected() && !tween && now - idleSince > 9000) controls.autoRotate = true;
    controls.update();
  }
  const [sx, sy] = intro?.active ? [0, 0] : ui.shift(); // panels are hidden during the intro
  if (Math.abs(sx - viewShift[0]) > 0.5 || Math.abs(sy - viewShift[1]) > 0.5) {
    viewShift[0] += (sx - viewShift[0]) * 0.12;
    viewShift[1] += (sy - viewShift[1]) * 0.12;
    const w = host.clientWidth, h = host.clientHeight;
    camera.setViewOffset(w, h, -viewShift[0], viewShift[1], w, h);
  }
  if (!intro?.active) ui.frame(now, pointer, pick);
  if (composer) composer.render();
  else renderer.render(scene, camera);
});

// handle for automated checks (read-only)
window.__r12 = { scene, bike, parts, camera, controls, pick, intro, select: (id) => ui.select(id), ids: () => parts.ids(), project: (v) => v.clone().project(camera) };
