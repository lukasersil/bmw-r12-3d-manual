// Opening sequence: an enamel BMW roundel (built in Blender, already fractured) turns to face the
// viewer on pure black, cracks and blows apart to the sides. Only then does the motorcycle appear
// behind it, and the camera pushes in through the debris to the normal view.
import * as THREE from 'three';

const clamp01 = (x) => Math.min(1, Math.max(0, x));
const easeInOut = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
const easeOut = (x) => 1 - Math.pow(1 - x, 3);
const easeIn = (x) => x * x * x;
const UP = new THREE.Vector3(0, 1, 0);
const R = 0.34; // badge radius in the GLB

export function createIntro({ scene, camera, controls, logo, lights, target, endView, zoom = 1, onDone }) {
  const T = { fadeIn: 0.8, spinStart: 0.3, spinEnd: 2.35, crack: 2.4, burst: 2.8, camStart: 2.45, camLen: 2.8 };
  T.end = T.camStart + T.camLen + 0.1;

  // ---------------------------------------------------------------- camera path
  // start further out and slightly round to the side, then push in to the normal view
  const rel = endView.position.clone().sub(endView.target);
  const L = rel.length();
  const dirEnd = rel.clone().normalize();
  const ARC = 0.2;
  const dLogo = 1.95 * Math.max(1, zoom * 0.85);
  const L0 = L + dLogo + 1.3;
  const dirAt = (a) => dirEnd.clone().applyAxisAngle(UP, a);
  const camPos = (k, extra) => target.clone().addScaledVector(dirAt(ARC * (1 - k)), L0 + extra + (L - L0) * k);
  const CREEP = 0.3;
  const cam0 = camPos(0, 0);

  // ---------------------------------------------------------------- the badge, between camera and bike
  const holder = new THREE.Group();
  holder.position.copy(target).addScaledVector(dirAt(ARC), L0 - dLogo);
  const home = holder.position.clone();
  holder.lookAt(cam0); // +z of the badge faces the camera
  const spin = new THREE.Group();
  holder.add(spin);
  spin.add(logo);
  scene.add(holder);

  const shards = [];
  const mats = new Set();
  for (const o of [...logo.children]) {
    const h = o.position.clone();
    const radial = new THREE.Vector3(h.x, h.y, 0);
    const r = radial.length();
    if (r < 0.02) radial.set(Math.random() - 0.5, Math.random() - 0.5, 0);
    radial.normalize();
    const speed = 1.5 + Math.random() * 1.9;
    shards.push({
      o, home: h, radial, r,
      vel: radial.clone().multiplyScalar(speed).add(new THREE.Vector3(0, (Math.random() - 0.35) * 0.9, -0.3 + Math.random() * 1.1)),
      axis: new THREE.Vector3(Math.random() - 0.5, Math.random() - 0.5, Math.random() - 0.5).normalize(),
      rate: 4 + Math.random() * 9,
      delay: (r / R) * 0.06,
      jit: new THREE.Vector3(Math.random() - 0.5, Math.random() - 0.5, 0),
    });
    o.traverse((m) => {
      if (!m.isMesh) return;
      m.castShadow = false;
      for (const mm of [].concat(m.material)) mats.add(mm);
    });
  }
  // the studio is dark: let the plating and the enamel pick up more of the environment
  for (const m of mats) m.envMapIntensity = m.name === 'logo_core' ? 1.0 : m.metalness > 0.5 ? 2.2 : 1.4;

  // its own light: a key from the upper left, a gleam that sweeps across, a flash for the break
  const logoKey = new THREE.PointLight(0xfff6ea, 14, 0, 2);
  logoKey.position.set(-0.6, 0.6, 1.0);
  holder.add(logoKey);
  const logoFill = new THREE.PointLight(0xe4ecff, 6, 0, 2);
  logoFill.position.set(0.8, -0.35, 0.9);
  holder.add(logoFill);
  const gleam = new THREE.PointLight(0xffffff, 0, 0, 2);
  holder.add(gleam);
  const flash = new THREE.PointLight(0xfff1dc, 0, 0, 2);
  flash.position.set(0, 0, 0.25);
  holder.add(flash);

  // black curtain right behind the badge: nothing else is visible until the badge breaks,
  // then it dissolves and the bike appears where the badge was
  const curtain = new THREE.Mesh(
    new THREE.PlaneGeometry(80, 80),
    new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 1, fog: false, toneMapped: false }),
  );
  curtain.position.set(0, 0, -0.6);
  curtain.renderOrder = 10;
  holder.add(curtain);

  // the bike waits in the dark and the haze until the badge breaks
  const base = {
    key: lights.key.intensity, rim: lights.rim.intensity, hemi: lights.hemi.intensity,
    near: scene.fog.near, far: scene.fog.far,
  };
  const fogNear0 = dLogo + 0.5;
  const fogFar0 = fogNear0 + (L0 - fogNear0) / 0.42;

  camera.position.copy(camPos(0, CREEP));
  controls.target.copy(target);
  controls.enabled = false;
  camera.lookAt(target);

  const fade = document.getElementById('intro-fade');
  const skipBtn = document.getElementById('intro-skip');
  let t0 = null;
  let held = null; // fixed time for checks
  let active = true;
  let opaque = true;

  function setLights(kb) {
    lights.key.intensity = base.key * (0.35 + 0.65 * kb);
    lights.rim.intensity = base.rim * (0.4 + 0.6 * kb);
    lights.hemi.intensity = base.hemi * (0.25 + 0.75 * kb);
  }

  function finish() {
    if (!active) return;
    active = false;
    scene.remove(holder);
    holder.traverse((o) => { if (o.isMesh) o.geometry.dispose(); });
    for (const m of mats) m.dispose();
    curtain.material.dispose();
    lights.key.intensity = base.key;
    lights.rim.intensity = base.rim;
    lights.hemi.intensity = base.hemi;
    scene.fog.near = base.near;
    scene.fog.far = base.far;
    camera.position.copy(endView.position);
    controls.target.copy(endView.target);
    controls.enabled = true;
    controls.update();
    if (fade) fade.hidden = true;
    if (skipBtn) skipBtn.hidden = true;
    document.body.classList.add('ui-ready');
    onDone?.();
  }
  skipBtn?.addEventListener('click', finish);
  window.addEventListener('keydown', (e) => { if (active && (e.key === 'Escape' || e.key === ' ')) finish(); });

  return {
    get active() { return active; },
    finish,
    hold(t) { held = t; },
    update(now) {
      if (!active) return;
      if (t0 === null) t0 = now;
      const t = held ?? (now - t0) / 1000;
      if (fade) fade.style.opacity = String(1 - clamp01(t / T.fadeIn));

      // ---- camera: slow creep, then the push through the debris
      const kc = easeInOut(clamp01((t - T.camStart) / T.camLen));
      camera.position.copy(camPos(kc, CREEP * (1 - clamp01(t / T.camStart))));
      const tb = t - T.burst;
      if (tb > 0 && tb < 0.5) camera.position.y += 0.012 * Math.exp(-tb * 9) * Math.sin(tb * 70);
      controls.target.copy(target);
      camera.lookAt(target);
      scene.fog.near = THREE.MathUtils.lerp(fogNear0, base.near, kc);
      scene.fog.far = THREE.MathUtils.lerp(fogFar0, base.far, kc);
      setLights(easeOut(clamp01(tb / 1.1)));

      // ---- badge: drifts in, spins up twice round, settles facing the camera
      const a0 = -0.6;
      const a1 = a0 + 0.3 * T.spinStart;
      spin.rotation.y = t < T.spinStart ? a0 + 0.3 * t
        : a1 + (Math.PI * 4 - a1) * easeInOut(clamp01((t - T.spinStart) / (T.spinEnd - T.spinStart)));
      holder.position.copy(home);
      holder.position.y += Math.sin(t * 1.7) * 0.006;

      // gleam across the face once it has settled
      const kg = clamp01((t - (T.spinEnd - 0.2)) / (T.burst - T.spinEnd + 0.2));
      gleam.position.set(-0.75 + 1.5 * kg, 0.5 - 0.8 * kg, 0.4);
      gleam.intensity = 9 * Math.sin(kg * Math.PI);

      // cracks open, the badge trembles
      const kk = easeIn(clamp01((t - T.crack) / (T.burst - T.crack)));
      if (kk > 0 && tb <= 0) {
        holder.position.x += (Math.random() - 0.5) * 0.004 * kk;
        holder.position.y += (Math.random() - 0.5) * 0.004 * kk;
      }

      // break: pieces blow out to the sides, tumble and fade once they are clear
      flash.intensity = tb > 0 && tb < 0.35 ? 22 * Math.exp(-tb * 11) : 0;
      logoKey.intensity = 14 * (1 - clamp01(tb / 0.6));
      logoFill.intensity = 6 * (1 - clamp01(tb / 0.6));
      for (const s of shards) {
        const ts = tb - s.delay;
        const p = s.o.position.copy(s.home);
        if (ts <= 0) {
          p.addScaledVector(s.radial, 0.0035 * kk).addScaledVector(s.jit, 0.0012 * kk * Math.sin(t * 80 + s.r * 40));
          s.o.quaternion.identity();
          continue;
        }
        const te = (1 - Math.exp(-0.9 * ts)) / 0.9;
        p.addScaledVector(s.radial, 0.0035).addScaledVector(s.vel, te);
        p.y -= 1.1 * ts * ts;
        s.o.quaternion.setFromAxisAngle(s.axis, s.rate * te);
      }
      curtain.material.opacity = 1 - easeOut(clamp01(tb / 0.75));
      curtain.visible = curtain.material.opacity > 0.002;
      if (tb > 0) {
        const op = 1 - clamp01((tb - 0.85) / 0.55);
        if (opaque) {
          for (const m of mats) { m.transparent = true; m.needsUpdate = true; }
          opaque = false;
        }
        for (const m of mats) m.opacity = op;
        holder.visible = op > 0.01;
      }

      if (skipBtn && t > 0.4) skipBtn.hidden = false;
      if (held === null && t >= T.end) finish();
    },
  };
}
