// Panels, manual card, hover label, lubrication markers and dialogs.
import * as THREE from 'three';
import { UI_TEXT } from './data/ui-text.js';
import { MEDIA, PART_MEDIA } from './data/media.js';

const $ = (id) => document.getElementById(id);
const store = {
  get(k) { try { return localStorage.getItem(k); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch { /* storage blocked */ } },
};

export function initUI({ DATA, parts, camera, actions }) {
  const { SYSTEMS, PARTS, LUBE = [], SPECS = [], ABOUT } = DATA;
  const touch = window.matchMedia('(hover: none)').matches;
  const narrow = () => window.matchMedia('(max-width: 760px)').matches;
  const state = {
    lang: store.get('r12-lang') ?? (/^(cs|sk)/i.test(navigator.language || '') ? 'cz' : /^de/i.test(navigator.language || '') ? 'de' : 'en'),
    hover: null,
    selected: null,
    systems: new Set(SYSTEMS.map((s) => s.id)),
    maint: false,
    explodeTarget: 0,
    explode: 0,
  };
  const t = (k) => UI_TEXT[state.lang][k] ?? k;
  const sysName = (id) => SYSTEMS.find((s) => s.id === id)?.[state.lang] ?? '';
  const part = (id) => PARTS[id]?.[state.lang] ?? { title: id };
  // source lines are written in English; in Czech and German mode translate the page markers and drop the English notes
  const srcText = (s) => {
    if (state.lang === 'en') return s;
    const t0 = s.replace(/\s\((?![^)]*\d)[^)]*\)/g, '');
    if (state.lang === 'de') return t0
      .replace(/\bpp?\.\s/g, 'S.\u00a0')
      .replace(/\bplates?\s/g, 'Tafel\u00a0')
      .replace(/\bFact sheet\b/g, 'Datenblatt')
      .replace(/\b[Pp]hoto\b/g, 'Foto')
      .replace(/\bpreface\b/g, 'Vorwort')
      .replace(/\band\b/g, 'und');
    return t0
      .replace(/\bpp?\.\s/g, 's.\u00a0')
      .replace(/\bFig\.\s/g, 'obr.\u00a0')
      .replace(/\band\b/g, 'a');
  };

  // ---------------------------------------------------------------- systems and part list
  const sysWrap = $('sys');
  const allBtn = document.createElement('button');
  allBtn.className = 'sys-btn';
  allBtn.type = 'button';
  allBtn.innerHTML = '<span class="dot"></span><span class="lbl"></span>';
  sysWrap.append(allBtn);
  const sysBtns = SYSTEMS.map((s) => {
    const b = document.createElement('button');
    b.className = 'sys-btn';
    b.type = 'button';
    const n = Object.values(PARTS).filter((p) => p.system === s.id).length;
    b.innerHTML = `<span class="dot"></span><span class="lbl"></span><span class="n">${n}</span>`;
    b.addEventListener('click', () => {
      // first click isolates one system; further clicks add or remove
      const all = state.systems.size === SYSTEMS.length;
      if (all) state.systems = new Set([s.id]);
      else if (state.systems.has(s.id)) state.systems.delete(s.id);
      else state.systems.add(s.id);
      if (state.systems.size === 0) state.systems = new Set(SYSTEMS.map((x) => x.id));
      applySystems();
    });
    sysWrap.append(b);
    return b;
  });
  allBtn.addEventListener('click', () => {
    state.systems = new Set(SYSTEMS.map((x) => x.id));
    applySystems();
  });

  const listWrap = $('part-list');
  const order = Object.keys(PARTS).filter((id) => parts.byId.has(id));
  const partBtns = new Map();
  for (const id of order) {
    const b = document.createElement('button');
    b.className = 'part-btn';
    b.type = 'button';
    b.addEventListener('click', () => select(id, true));
    b.addEventListener('mouseenter', () => hover(id));
    b.addEventListener('mouseleave', () => hover(null));
    listWrap.append(b);
    partBtns.set(id, b);
  }

  function applySystems() {
    const all = state.systems.size === SYSTEMS.length;
    allBtn.setAttribute('aria-pressed', String(all));
    SYSTEMS.forEach((s, i) => sysBtns[i].setAttribute('aria-pressed', String(!all && state.systems.has(s.id))));
    if (all) sysBtns.forEach((b) => b.setAttribute('aria-pressed', 'false'));
    parts.systems = all ? null : new Set(state.systems);
    // the part list appears once a system is picked; with all systems on it would bury the bike
    listWrap.hidden = all || state.maint;
    for (const [id, b] of partBtns) b.hidden = !parts.isActive(id);
    if (state.selected && !parts.isActive(state.selected)) select(null);
    parts.refresh();
    actions.interact();
  }

  // ---------------------------------------------------------------- views
  const viewWrap = $('views');
  const viewBtns = ['iso', 'left', 'right', 'front', 'rear', 'top'].map((v) => {
    const b = document.createElement('button');
    b.className = 'view-btn';
    b.type = 'button';
    b.dataset.view = v;
    b.addEventListener('click', () => {
      actions.interact();
      actions.setView(v);
    });
    viewWrap.append(b);
    return b;
  });
  $('btn-reset').addEventListener('click', () => {
    actions.interact();
    select(null);
    actions.reset();
  });

  // ---------------------------------------------------------------- explode
  const range = $('explode');
  const exBtn = $('btn-explode');
  range.addEventListener('input', () => {
    state.explodeTarget = range.value / 100;
    state.explode = state.explodeTarget; // follow the thumb directly
    parts.setExplode(state.explode);
    exBtn.textContent = state.explodeTarget > 0.5 ? t('explodeOff') : t('explodeOn');
    exBtn.setAttribute('aria-pressed', String(state.explodeTarget > 0.5));
    actions.interact();
  });
  exBtn.addEventListener('click', () => {
    state.explodeTarget = state.explodeTarget > 0.5 ? 0 : 1;
    exBtn.textContent = state.explodeTarget > 0.5 ? t('explodeOff') : t('explodeOn');
    exBtn.setAttribute('aria-pressed', String(state.explodeTarget > 0.5));
    actions.interact();
  });

  // ---------------------------------------------------------------- side panel toggle
  const side = $('side');
  const panelBtn = $('btn-panel');
  function sheets() {
    document.body.classList.toggle('sheet-open', !$('info').hidden || side.dataset.collapsed === 'false');
  }
  function openPanel(on) {
    side.dataset.collapsed = String(!on);
    panelBtn.setAttribute('aria-expanded', String(on));
    if (on && narrow()) $('info').hidden = true;
    sheets();
  }
  panelBtn.addEventListener('click', () => openPanel(side.dataset.collapsed === 'true'));
  if (narrow()) openPanel(false);

  // ---------------------------------------------------------------- manual card
  function renderInfo() {
    const id = state.selected;
    const info = $('info');
    if (!id) { info.hidden = true; sheets(); return; }
    const p = PARTS[id];
    const c = part(id);
    $('info-sys').textContent = sysName(p.system);
    $('info-title').textContent = c.title;
    $('info-de').textContent = p.term && state.lang !== 'de' ? `${t('german')}: ${p.term}` : '';
    const txt = $('info-text');
    txt.textContent = c.text || t('pending');
    txt.classList.toggle('pending', !c.text);
    const dl = $('info-data');
    dl.replaceChildren();
    for (const [k, v] of c.data ?? []) {
      const dt = document.createElement('dt');
      dt.textContent = k;
      const dd = document.createElement('dd');
      dd.textContent = v;
      dl.append(dt, dd);
    }
    dl.hidden = !(c.data && c.data.length);
    // maintenance: the part's own advice, then each lubrication point as interval and lubricant rows
    const lube = LUBE.filter((l) => l.part === id);
    $('info-care').hidden = !c.care && lube.length === 0;
    $('t-care').textContent = t('care');
    $('info-care-text').textContent = c.care ?? '';
    $('info-care-text').hidden = !c.care;
    const rows = $('info-lube');
    rows.replaceChildren();
    for (const l of lube) {
      const box = document.createElement('div');
      box.className = 'lube-row';
      const name = document.createElement('b');
      name.textContent = l[state.lang];
      box.append(name);
      for (const [k, val] of [['every', l['every_' + state.lang]], ['lubricant', l['lubricant_' + state.lang]]]) {
        if (!val) continue;
        const line = document.createElement('span');
        line.textContent = `${t(k)}: ${val}`;
        box.append(line);
      }
      rows.append(box);
    }
    rows.hidden = lube.length === 0;
    const src = $('info-src');
    src.replaceChildren();
    if (p.sources?.length) {
      const b = document.createElement('b');
      b.textContent = `${t('source')}: `;
      src.append(b, p.sources.map(srcText).join(' · '));
    }
    if (p.unverified?.length) {
      const u = p.unverified.map((x) => (typeof x === 'string' ? x : x[state.lang])).join('; ');
      src.append(document.createElement('br'), `${t('unverified')}: ${u}`);
    }
    src.hidden = !src.childNodes.length;
    const ids = (PART_MEDIA[id] ?? []).filter((m) => MEDIA[m]);
    $('t-media').textContent = t('media');
    fillThumbs($('info-media-grid'), ids);
    $('info-media').hidden = ids.length === 0;
    $('info-close').setAttribute('aria-label', t('close'));
    info.hidden = false;
    if (narrow()) openPanel(false);
    sheets();
  }
  $('info-close').addEventListener('click', () => select(null));

  function select(id, focus = false) {
    if (id && !parts.isActive(id) && !state.maint) id = null;
    state.selected = id;
    parts.selected = id;
    parts.refresh();
    for (const [pid, b] of partBtns) b.setAttribute('aria-current', String(pid === id));
    renderInfo();
    if (id && focus) actions.focusPart(id);
    actions.interact();
  }

  // ---------------------------------------------------------------- hover label
  const tip = $('tip');
  function hover(id) {
    if (id === state.hover) return;
    state.hover = id;
    parts.hover = id;
    parts.refresh();
    document.body.classList.toggle('pointing', !!id);
    if (!id) { tip.hidden = true; return; }
    $('tip-title').textContent = part(id).title;
    $('tip-sub').textContent = `${sysName(PARTS[id].system)} · ${t('clickForMore')}`;
    tip.hidden = false;
  }

  // ---------------------------------------------------------------- maintenance mode and markers
  const markerWrap = $('markers');
  let markers = [];
  function buildMarkers() {
    markerWrap.replaceChildren();
    markers = [];
    if (!state.maint) return;
    LUBE.forEach((l, i) => {
      for (const pt of parts.points(l.part)) {
        const b = document.createElement('button');
        b.className = 'marker';
        b.type = 'button';
        b.textContent = String(i + 1);
        b.setAttribute('aria-label', l[state.lang]);
        b.addEventListener('click', () => select(l.part, true));
        markerWrap.append(b);
        markers.push({ el: b, part: l.part, local: pt, k: markers.filter((m) => m.part === l.part && m.local.distanceTo(pt) < 1e-6).length });
      }
    });
  }
  function renderLube() {
    const list = $('lube-list');
    list.replaceChildren();
    $('lube-intro').textContent = LUBE.length ? t('lubeIntro') : t('lubeEmpty');
    LUBE.forEach((l, i) => {
      const li = document.createElement('li');
      const b = document.createElement('button');
      b.type = 'button';
      b.innerHTML = `<span class="num">${i + 1}</span><span><b></b><small></small></span>`;
      b.querySelector('b').textContent = l[state.lang];
      b.querySelector('small').textContent = [l['every_' + state.lang], l['lubricant_' + state.lang]].filter(Boolean).join(' · ');
      b.addEventListener('click', () => select(l.part, true));
      li.append(b);
      list.append(li);
    });
  }
  $('btn-maint').addEventListener('click', () => {
    state.maint = !state.maint;
    $('btn-maint').setAttribute('aria-pressed', String(state.maint));
    $('lube').hidden = !state.maint;
    side.classList.toggle('maint', state.maint);
    parts.focusIds = state.maint && LUBE.length ? new Set(LUBE.map((l) => l.part)) : null;
    renderLube();
    buildMarkers();
    applySystems();
  });

  // ---------------------------------------------------------------- period sources
  // thumbnails open a lightbox that pages through the same list
  const lb = { list: [], i: 0, back: null };
  function fillThumbs(grid, ids) {
    grid.replaceChildren();
    for (const [i, mid] of ids.entries()) {
      const m = MEDIA[mid];
      const b = document.createElement('button');
      b.type = 'button';
      b.dataset.kind = m.kind;
      b.title = `${t('zoom')}: ${m[state.lang].title}`;
      const img = document.createElement('img');
      img.src = `media/t/${mid}.jpg`;
      img.alt = m[state.lang].title;
      img.loading = 'lazy';
      img.decoding = 'async';
      const cap = document.createElement('small');
      cap.textContent = m.tag[state.lang];
      b.append(img, cap);
      b.addEventListener('click', () => openMedia(ids, i, b));
      grid.append(b);
    }
  }
  function showMedia() {
    const mid = lb.list[lb.i];
    const m = MEDIA[mid];
    const c = m[state.lang];
    const img = $('lb-img');
    img.src = `media/${mid}.jpg`;
    img.alt = c.title;
    $('lb-tag').textContent = m.tag[state.lang];
    $('lb-title').textContent = c.title;
    $('lb-text').textContent = c.text;
    $('lb-orig').textContent = m.orig ? `„${m.orig}“` : '';
    $('lb-orig').hidden = !m.orig;
    const cr = $('lb-credit');
    cr.replaceChildren(m.credit[state.lang]);
    if (m.url) {
      const a = document.createElement('a');
      a.href = m.url;
      a.target = '_blank';
      a.rel = 'noopener';
      a.textContent = state.lang === 'cz' ? 'Originál' : 'Original';
      cr.append(' ', a);
    }
    $('lb-count').textContent = `${lb.i + 1} / ${lb.list.length}`;
    $('lb-prev').hidden = $('lb-next').hidden = lb.list.length < 2;
    $('lb-prev').setAttribute('aria-label', t('prev'));
    $('lb-next').setAttribute('aria-label', t('next'));
    // warm the neighbours so paging feels instant
    for (const d of [1, -1]) {
      const n = lb.list[(lb.i + d + lb.list.length) % lb.list.length];
      if (n) new Image().src = `media/${n}.jpg`;
    }
  }
  function openMedia(list, i, back) {
    lb.list = list;
    lb.i = i;
    lb.back = back;
    showMedia();
    $('dlg-media').hidden = false;
    $('dlg-media').querySelector('[data-close]').focus();
  }
  function closeMedia() {
    $('dlg-media').hidden = true;
    lb.back?.focus();
  }
  function stepMedia(d) {
    lb.i = (lb.i + d + lb.list.length) % lb.list.length;
    showMedia();
  }
  $('lb-prev').addEventListener('click', () => stepMedia(-1));
  $('lb-next').addEventListener('click', () => stepMedia(1));
  $('dlg-media').addEventListener('click', (e) => { if (e.target === $('dlg-media') || e.target.closest('[data-close]')) closeMedia(); });
  document.addEventListener('keydown', (e) => {
    if ($('dlg-media').hidden) return;
    if (e.key === 'ArrowRight') stepMedia(1);
    else if (e.key === 'ArrowLeft') stepMedia(-1);
  });

  // ---------------------------------------------------------------- dialogs
  function openDialog(id) {
    const d = $(id);
    d.hidden = false;
    d.querySelector('[data-close]').focus();
  }
  for (const id of ['dlg-specs', 'dlg-about']) {
    const d = $(id);
    d.addEventListener('click', (e) => { if (e.target === d || e.target.closest('[data-close]')) d.hidden = true; });
  }
  function renderSpecs() {
    const body = $('spec-body');
    body.replaceChildren();
    for (const s of SPECS) {
      const tr = document.createElement('tr');
      const th = document.createElement('th');
      th.scope = 'row';
      th.textContent = s[state.lang];
      const td = document.createElement('td');
      td.textContent = s['value_' + state.lang];
      tr.append(th, td);
      body.append(tr);
    }
    const srcs = [...new Set(SPECS.map((s) => s.source).filter(Boolean))];
    $('spec-src').textContent = srcs.length ? `${t('source')}: ${srcs.map(srcText).join(' · ')}` : '';
    $('specs-title').textContent = t('specsTitle');
  }
  function renderAbout() {
    $('about-text').textContent = ABOUT?.[state.lang] ?? '';
    $('about-credits').textContent = `${t('credits')} ${t('disclaimer')}`;
    $('about-src-title').textContent = t('sourcesTitle');
    const ul = $('about-src');
    ul.replaceChildren();
    const all = new Set([...(ABOUT?.sources ?? []), 'Instruction Book R 12 / R 17, BMW 1936']);
    for (const s of all) {
      const li = document.createElement('li');
      li.textContent = s;
      ul.append(li);
    }
    $('about-media-title').textContent = t('media');
    fillThumbs($('about-media'), Object.keys(MEDIA));
  }
  $('btn-specs').addEventListener('click', () => { renderSpecs(); openDialog('dlg-specs'); });
  $('btn-about').addEventListener('click', () => { renderAbout(); openDialog('dlg-about'); });
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    if (!$('dlg-media').hidden) { closeMedia(); return; }
    for (const id of ['dlg-specs', 'dlg-about']) if (!$(id).hidden) { $(id).hidden = true; return; }
    if (state.selected) select(null);
  });

  // ---------------------------------------------------------------- language
  function setLang(lang) {
    state.lang = lang;
    store.set('r12-lang', lang);
    document.documentElement.lang = { cz: 'cs', en: 'en', de: 'de' }[lang];
    for (const l of ['cz', 'en', 'de']) $('lang-' + l).setAttribute('aria-pressed', String(lang === l));
    $('t-kicker').textContent = t('kicker');
    $('t-meta').textContent = t('meta');
    $('t-systems').textContent = t('systems');
    $('t-explode').textContent = t('explode');
    $('t-views').textContent = t('views');
    $('t-modes').textContent = t('modes');
    $('t-maint').textContent = t('maintenance');
    $('t-specs').textContent = t('specs');
    $('t-about').textContent = t('about');
    $('hint').textContent = touch ? t('hintTouch') : t('hint');
    if ($('intro-skip')) $('intro-skip').textContent = t('skipIntro');
    $('btn-reset').setAttribute('aria-label', t('reset'));
    $('btn-reset').title = t('reset');
    $('btn-panel').setAttribute('aria-label', t('menu'));
    allBtn.querySelector('.lbl').textContent = t('all');
    SYSTEMS.forEach((s, i) => { sysBtns[i].querySelector('.lbl').textContent = s[lang]; });
    for (const [id, b] of partBtns) b.textContent = part(id).title;
    viewBtns.forEach((b) => { b.textContent = UI_TEXT[lang].views_[b.dataset.view]; });
    exBtn.textContent = state.explodeTarget > 0.5 ? t('explodeOff') : t('explodeOn');
    for (const c of document.querySelectorAll('[data-close]')) c.setAttribute('aria-label', t('close'));
    renderInfo();
    renderLube();
    buildMarkers();
    if (!$('dlg-specs').hidden) renderSpecs();
    if (!$('dlg-about').hidden) renderAbout();
    if (!$('dlg-media').hidden) showMedia();
    if (state.hover) { const h = state.hover; state.hover = null; hover(h); }
  }
  $('lang-cz').addEventListener('click', () => setLang('cz'));
  $('lang-en').addEventListener('click', () => setLang('en'));
  $('lang-de').addEventListener('click', () => setLang('de'));
  setLang(UI_TEXT[state.lang] ? state.lang : 'en');
  applySystems();

  // ---------------------------------------------------------------- per frame
  const v = new THREE.Vector3();
  const api = {
    needsPick: false,
    selected: () => state.selected,
    // horizontal shift of the rendered view so the bike sits in the space the panels leave free
    shift() {
      const info = $('info');
      if (narrow()) {
        // phone: the card and the panel are bottom sheets, so lift the bike instead
        const sheet = !info.hidden ? info : side.dataset.collapsed === 'true' ? null : side;
        return [0, sheet ? (sheet.offsetHeight + 16) / 2 : 0];
      }
      const left = info.hidden ? 0 : info.offsetWidth + 16;
      const right = side.dataset.collapsed === 'true' ? 0 : side.offsetWidth + 16;
      return [(left - right) / 2, 0];
    },
    hover,
    select,
    frame(now, pointer, pick) {
      // animate the explode slider towards its target
      if (Math.abs(state.explode - state.explodeTarget) > 0.0005) {
        state.explode += (state.explodeTarget - state.explode) * 0.08;
        if (Math.abs(state.explode - state.explodeTarget) < 0.002) state.explode = state.explodeTarget;
        parts.setExplode(state.explode);
        range.value = String(Math.round(state.explode * 100));
        if (markers.length) buildMarkers();
      }
      if (api.needsPick && pointer && !pointer.touch) {
        api.needsPick = false;
        hover(pick(pointer.x, pointer.y));
      }
      if (pointer && !tip.hidden) tip.style.transform = `translate(${pointer.x + 14}px, ${pointer.y + 14}px)`;
      // project lubrication markers
      if (markers.length) {
        const w = window.innerWidth, h = window.innerHeight;
        const placed = [];
        for (const m of markers) {
          v.copy(m.local).project(camera);
          let x = ((v.x + 1) / 2) * w, y = ((1 - v.y) / 2) * h;
          // nudge sideways until the badge no longer covers one placed before it
          for (let guard = 0; guard < 8 && placed.some(([px, py]) => Math.abs(px - x) < 24 && Math.abs(py - y) < 24); guard++) x += 26;
          placed.push([x, y]);
          m.el.style.transform = `translate(${x}px, ${y}px)`;
          m.el.hidden = v.z > 1;
        }
      }
    },
  };
  return api;
}
