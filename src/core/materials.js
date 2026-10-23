// Highlight and ghost materials for the part registry. The model's own materials come from the GLB.
import * as THREE from 'three';

export const ACCENT = 0xffe600;

// Highlight copies for hover and selection, cached per source material.
const hiCache = new Map();
export function highlightOf(mat, strong = false) {
  const key = mat.uuid + (strong ? ':s' : ':h');
  let h = hiCache.get(key);
  if (!h) {
    h = mat.clone();
    if (h.emissive) {
      h.emissive = new THREE.Color(ACCENT);
      h.emissiveIntensity = strong ? 0.42 : 0.26;
    }
    hiCache.set(key, h);
  }
  return h;
}

// One shared ghost for parts outside the selected systems.
export const ghost = new THREE.MeshStandardMaterial({
  color: 0x9a9a9a, roughness: 1, metalness: 0, transparent: true, opacity: 0.07, depthWrite: false,
});
ghost.name = 'ghost';
