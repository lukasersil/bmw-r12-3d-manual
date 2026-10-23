// Photographic look: a studio environment for reflections and a fine surface grain for the cast,
// rubber and leather parts, which the procedural meshes carry no textures for.
import * as THREE from 'three';

// Dark studio with a large softbox overhead, two upright strip lights and a warm fill in front.
// Long soft highlights on the black paint and the plating come from these panels.
export function studioEnvironment(renderer) {
  const env = new THREE.Scene();
  env.background = new THREE.Color(0x202022);
  const room = new THREE.Mesh(
    new THREE.BoxGeometry(24, 12, 24),
    new THREE.MeshBasicMaterial({ color: 0x3c3c40, side: THREE.BackSide }),   // grey studio walls
  );
  room.position.y = 5;
  env.add(room);
  // floor a little lighter than the walls, as a studio cyclorama is
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(24, 24), new THREE.MeshBasicMaterial({ color: 0x55555a }));
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -0.99;
  env.add(floor);
  const panel = (w, h, power, pos, tint = 0xffffff) => {
    const m = new THREE.Mesh(
      new THREE.PlaneGeometry(w, h),
      new THREE.MeshBasicMaterial({ color: new THREE.Color(tint).multiplyScalar(power), side: THREE.DoubleSide }),
    );
    m.position.set(...pos);
    m.lookAt(0, 0.5, 0);
    env.add(m);
  };
  panel(8, 4, 6, [0.4, 7, -0.6]);                     // overhead softbox
  panel(1.8, 6.5, 5, [-3.4, 2.8, 4.8]);               // strip, rear right
  panel(1.8, 6.5, 4.4, [3.8, 2.8, -4.6]);             // strip, front left
  panel(4.5, 3, 2.4, [5.4, 1.6, 1.8], 0xfff0de);      // warm fill in front
  panel(4.5, 3, 1.6, [-5.6, 1.6, -2.2], 0xe8eeff);    // cool fill behind
  panel(18, 0.8, 1.4, [-9.5, 1.4, -2]);               // horizon line behind
  const pmrem = new THREE.PMREMGenerator(renderer);
  const tex = pmrem.fromScene(env, 0.025, 0.1, 100, { size: 512 }).texture;
  pmrem.dispose();
  return tex;
}

const NOISE = /* glsl */ `
varying vec3 vSdW;
uniform float uSdFine, uSdCoarse, uSdRough, uSdBump;
float sdHash(vec3 p) { p = fract(p * 0.3183099 + 0.1); p *= 17.0; return fract(p.x * p.y * p.z * (p.x + p.y + p.z)); }
float sdNoise(vec3 x) {
  vec3 i = floor(x), f = fract(x);
  f = f * f * (3.0 - 2.0 * f);
  return mix(mix(mix(sdHash(i), sdHash(i + vec3(1, 0, 0)), f.x), mix(sdHash(i + vec3(0, 1, 0)), sdHash(i + vec3(1, 1, 0)), f.x), f.y),
             mix(mix(sdHash(i + vec3(0, 0, 1)), sdHash(i + vec3(1, 0, 1)), f.x), mix(sdHash(i + vec3(0, 1, 1)), sdHash(i + vec3(1, 1, 1)), f.x), f.y), f.z);
}
float sdFbm(vec3 p) { return 0.62 * sdNoise(p) + 0.28 * sdNoise(p * 2.07 + 3.1) + 0.1 * sdNoise(p * 4.3 + 7.7); }
`;

// Grain by material name: fine scale (per metre) for the bump, coarse for blotchy roughness.
const GRAIN = {
  cast: { fine: 300, coarse: 14, rough: 0.12, bump: 0.018 },
  alusatin: { fine: 320, coarse: 18, rough: 0.1, bump: 0.014 },
  alu: { fine: 280, coarse: 14, rough: 0.08, bump: 0.012 },
  darkmetal: { fine: 260, coarse: 18, rough: 0.14, bump: 0.025 },
  rubber: { fine: 420, coarse: 24, rough: 0.14, bump: 0.06 },
  leather: { fine: 360, coarse: 12, rough: 0.12, bump: 0.045 },
  black: { fine: 200, coarse: 14, rough: 0.08, bump: 0.01 },
};

export function addSurfaceGrain(material) {
  const g = GRAIN[material.name];
  if (!g || material.userData.grain) return;
  material.userData.grain = true;
  material.onBeforeCompile = (shader) => {
    shader.uniforms.uSdFine = { value: g.fine };
    shader.uniforms.uSdCoarse = { value: g.coarse };
    shader.uniforms.uSdRough = { value: g.rough };
    shader.uniforms.uSdBump = { value: g.bump };
    shader.vertexShader = 'varying vec3 vSdW;\n' + shader.vertexShader.replace(
      '#include <project_vertex>',
      '#include <project_vertex>\n  vSdW = (modelMatrix * vec4(transformed, 1.0)).xyz;',
    );
    shader.fragmentShader = NOISE + shader.fragmentShader
      .replace('#include <roughnessmap_fragment>', `#include <roughnessmap_fragment>
  {
    float sdC = sdFbm(vSdW * uSdCoarse);
    float sdF = sdNoise(vSdW * uSdFine);
    roughnessFactor = clamp(roughnessFactor + (sdC - 0.5) * uSdRough + (sdF - 0.5) * uSdRough * 0.35, 0.03, 1.0);
  }`)
      .replace('#include <normal_fragment_maps>', `#include <normal_fragment_maps>
  {
    vec3 sp = vSdW * uSdFine;
    // fade the grain out where it gets finer than a pixel, so it never shimmers
    float sdFade = clamp(1.4 - length(fwidth(sp)) * 1.6, 0.0, 1.0);
    if (sdFade > 0.0) {
      float n0 = sdNoise(sp);
      vec3 gw = vec3(sdNoise(sp + vec3(0.37, 0.0, 0.0)) - n0, sdNoise(sp + vec3(0.0, 0.37, 0.0)) - n0, sdNoise(sp + vec3(0.0, 0.0, 0.37)) - n0) / 0.37;
      vec3 gv = (viewMatrix * vec4(gw, 0.0)).xyz;
      normal = normalize(normal - uSdBump * sdFade * (gv - dot(gv, normal) * normal));
    }
  }`);
  };
  material.customProgramCacheKey = () => 'grain-' + material.name;
  material.needsUpdate = true;
}
