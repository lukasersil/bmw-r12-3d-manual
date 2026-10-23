// Registry of named parts. Every piece of the bike belongs to one part id (the keys of PARTS in
// data/content.js). A part can be several objects (left and right cylinder), each with its own
// explode vector. The registry drives the exploded view, hover/selection highlight and the
// system filter (parts outside the chosen systems turn into a faint ghost and stop being pickable).
import * as THREE from 'three';
import { highlightOf, ghost } from './materials.js';

const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

export class Parts {
  constructor(systemOf) {
    this.systemOf = systemOf; // id → system id
    this.items = [];
    this.byId = new Map();
    this.meshes = [];
    this.hover = null;
    this.selected = null;
    this.systems = null; // null = all systems
    this.focusIds = null; // maintenance mode: only these parts stay solid
    this.explode = 0;
  }

  add(id, obj, explode = [0, 0, 0]) {
    if (!this.systemOf(id)) console.warn('unknown part', id);
    const it = { id, obj, base: obj.position.clone(), explode: new THREE.Vector3(...explode) };
    obj.traverse((m) => {
      if (!m.isMesh) return;
      m.userData.part = id;
      m.userData.mat = m.material;
      m.castShadow = !m.material.transparent;
      m.receiveShadow = true;
      this.meshes.push(m);
    });
    this.items.push(it);
    if (!this.byId.has(id)) this.byId.set(id, []);
    this.byId.get(id).push(it);
    return obj;
  }

  ids() {
    return [...this.byId.keys()];
  }

  setExplode(t) {
    this.explode = t;
    const e = ease(Math.min(1, Math.max(0, t)));
    for (const it of this.items) it.obj.position.copy(it.base).addScaledVector(it.explode, e);
  }

  isActive(id) {
    if (this.focusIds) return this.focusIds.has(id);
    return !this.systems || this.systems.has(this.systemOf(id));
  }

  refresh() {
    for (const m of this.meshes) {
      const id = m.userData.part;
      let mat = m.userData.mat;
      if (!this.isActive(id)) mat = ghost;
      else if (id === this.selected) mat = highlightOf(mat, true);
      else if (id === this.hover) mat = highlightOf(mat, false);
      if (m.material !== mat) m.material = mat;
      m.castShadow = mat !== ghost && !mat.transparent;
    }
  }

  pickables() {
    return this.meshes.filter((m) => this.isActive(m.userData.part) && m.visible);
  }

  // World-space centre of a part at the current explode state.
  center(id, out = new THREE.Vector3()) {
    const box = new THREE.Box3();
    for (const it of this.byId.get(id) ?? []) box.expandByObject(it.obj);
    return box.isEmpty() ? out.set(0, 0.45, 0) : box.getCenter(out);
  }

  // One representative point per object of a part (lubrication markers on both sides).
  points(id) {
    return (this.byId.get(id) ?? []).map((it) => new THREE.Box3().setFromObject(it.obj).getCenter(new THREE.Vector3()));
  }

  size(id) {
    const box = new THREE.Box3();
    for (const it of this.byId.get(id) ?? []) box.expandByObject(it.obj);
    return box.getSize(new THREE.Vector3()).length();
  }
}
