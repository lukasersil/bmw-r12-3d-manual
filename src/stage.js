// Promo studio around the bike: dark backdrop with a pool of light, reflective floor that fades into
// the dark, a soft light cone from above, slow dust in the light and a faint lettering wall far behind.
import * as THREE from 'three';
import { Reflector } from 'three/addons/objects/Reflector.js';

function canvasTex(w, h, draw, srgb = true) {
  const c = document.createElement('canvas');
  c.width = w;
  c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c);
  if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

function radial(stops) {
  return (g, w, h) => {
    const gr = g.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2);
    for (const [o, c] of stops) gr.addColorStop(o, c);
    g.fillStyle = gr;
    g.fillRect(0, 0, w, h);
  };
}

export async function createStage({ scene, touch }) {
  const stage = new THREE.Group();
  stage.name = 'stage';
  scene.add(stage);

  // backdrop: lighter behind the bike, falling off to near black at the edges of the frame
  scene.background = canvasTex(1024, 1024, radial([[0, '#18181a'], [0.5, '#0e0e0f'], [1, '#050505']]));
  scene.fog = new THREE.Fog(0x0b0b0c, 3.5, 10);

  // reflective floor (desktop): mirror under a dark glaze that is clear near the bike and opaque further out
  if (!touch) {
    const mirror = new Reflector(new THREE.CircleGeometry(14, 96), {
      color: 0x1c1c1e,
      textureWidth: Math.min(2048, window.innerWidth * window.devicePixelRatio),
      textureHeight: Math.min(2048, window.innerHeight * window.devicePixelRatio),
      clipBias: 0.003,
    });
    mirror.rotation.x = -Math.PI / 2;
    mirror.position.y = -0.0005;
    stage.add(mirror);
  }
  const glazeAlpha = canvasTex(512, 512, radial(touch
    ? [[0, '#e6e6e6'], [0.5, '#f4f4f4'], [1, '#ffffff']]
    : [[0, '#7a7a7a'], [0.08, '#8e8e8e'], [0.25, '#dadada'], [0.5, '#ffffff'], [1, '#ffffff']]), false);
  const glaze = new THREE.Mesh(
    new THREE.CircleGeometry(14, 96),
    new THREE.MeshStandardMaterial({ color: 0x050506, roughness: 0.92, metalness: 0, transparent: true, alphaMap: glazeAlpha, depthWrite: false }),
  );
  glaze.rotation.x = -Math.PI / 2;
  glaze.position.y = 0.0005;
  glaze.receiveShadow = true;
  glaze.renderOrder = 1;
  stage.add(glaze);
  // shadow catcher on top of the glaze
  const shadow = new THREE.Mesh(new THREE.CircleGeometry(6, 96), new THREE.ShadowMaterial({ opacity: 0.6, depthWrite: false }));
  shadow.rotation.x = -Math.PI / 2;
  shadow.position.y = 0.001;
  shadow.receiveShadow = true;
  shadow.renderOrder = 2;
  stage.add(shadow);
  // pool of light on the floor
  const pool = new THREE.Mesh(
    new THREE.CircleGeometry(2.2, 96),
    new THREE.MeshBasicMaterial({
      color: 0xfff6ea, transparent: true, opacity: 0.06, depthWrite: false, blending: THREE.AdditiveBlending,
      alphaMap: canvasTex(512, 512, radial([[0, '#ffffff'], [0.35, '#8a8a8a'], [1, '#000000']]), false),
    }),
  );
  pool.rotation.x = -Math.PI / 2;
  pool.position.y = 0.0015;
  pool.renderOrder = 3;
  stage.add(pool);

  // soft cone of light from above
  const coneMat = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    uniforms: { uStrength: { value: touch ? 0.05 : 0.07 } },
    vertexShader: `varying float vH; varying vec3 vN; varying vec3 vV;
      void main(){ vH = uv.y; vec4 mv = modelViewMatrix * vec4(position,1.0); vN = normalize(normalMatrix * normal); vV = normalize(-mv.xyz); gl_Position = projectionMatrix * mv; }`,
    fragmentShader: `uniform float uStrength; varying float vH; varying vec3 vN; varying vec3 vV;
      void main(){ float edge = pow(abs(dot(vN, vV)), 1.6); float fall = pow(vH, 1.4); gl_FragColor = vec4(vec3(1.0, 0.98, 0.94), uStrength * edge * fall); }`,
  });
  const cone = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 1.55, 3.6, 64, 1, true), coneMat);
  cone.position.set(0, 1.8, 0);
  cone.renderOrder = 4;
  stage.add(cone);

  // dust in the light
  const N = touch ? 140 : 320;
  const pos = new Float32Array(N * 3);
  const seed = new Float32Array(N);
  for (let i = 0; i < N; i++) {
    const r = Math.sqrt(Math.random()) * 1.5;
    const a = Math.random() * Math.PI * 2;
    pos[i * 3] = Math.cos(a) * r;
    pos[i * 3 + 1] = Math.random() * 2.4;
    pos[i * 3 + 2] = Math.sin(a) * r;
    seed[i] = Math.random() * 100;
  }
  const dustGeo = new THREE.BufferGeometry();
  dustGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const dot = canvasTex(64, 64, radial([[0, 'rgba(255,255,255,1)'], [0.4, 'rgba(255,255,255,0.35)'], [1, 'rgba(255,255,255,0)']]));
  const dust = new THREE.Points(dustGeo, new THREE.PointsMaterial({ size: 0.012, map: dot, transparent: true, opacity: 0.55, depthWrite: false, blending: THREE.AdditiveBlending, sizeAttenuation: true }));
  dust.renderOrder = 5;
  stage.add(dust);

  // lettering wall far behind, faint, in the brand display face
  try { await document.fonts.load('400 200px "Bebas Neue"'); } catch { /* fallback face */ }
  const wallTex = canvasTex(4096, 512, (g, w, h) => {
    g.clearRect(0, 0, w, h);
    g.fillStyle = 'rgba(255,255,255,1)';
    g.font = '400 300px "Bebas Neue", Impact, sans-serif';
    g.textBaseline = 'middle';
    // one cycle of words spread evenly over the full width, so the wrap seam falls in a gap
    const words = ['R 12', '1935–1942', '745 CCM', '18 PS'];
    const widths = words.map((wd) => g.measureText(wd).width);
    const gap = (w - widths.reduce((x, y) => x + y, 0)) / words.length;
    let x = gap / 2;
    words.forEach((wd, i) => {
      g.fillText(wd, x, h / 2 + 10);
      x += widths[i] + gap;
    });
  });
  wallTex.wrapS = THREE.RepeatWrapping;
  // seen from inside, so mirror back; repeat round the wall so the letters keep their proportions
  const circ = 2 * Math.PI * 13, texW = 4096 * (2.2 / 512);
  wallTex.repeat.set(-Math.round(circ / texW), 1);
  const wall = new THREE.Mesh(
    new THREE.CylinderGeometry(13, 13, 2.2, 128, 1, true),
    new THREE.MeshBasicMaterial({ map: wallTex, transparent: true, opacity: 0.022, side: THREE.BackSide, depthWrite: false, fog: false }),
  );
  wall.position.y = 1.15;
  wall.renderOrder = -1;
  stage.add(wall);

  return {
    group: stage,
    update(now) {
      const t = now * 0.001;
      const p = dustGeo.attributes.position;
      for (let i = 0; i < N; i++) {
        let y = p.getY(i) + 0.0009;
        if (y > 2.4) y = 0;
        p.setY(i, y);
        p.setX(i, p.getX(i) + Math.sin(t * 0.6 + seed[i]) * 0.0004);
      }
      p.needsUpdate = true;
      wall.rotation.y = t * 0.01;
    },
  };
}
