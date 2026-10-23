# Frame-exact screen capture of the BMW R 12 3D manual: virtual clock (rAF + performance.now + CSS animations),
# one screenshot per frame, scripted mouse and clicks, Czech captions and a visible cursor injected into the page.
#   python3 capture.py <frames_dir> [fps]
import asyncio, sys, os, math, json
from playwright.async_api import async_playwright

OUT = sys.argv[1]
FPS = int(sys.argv[2]) if len(sys.argv) > 2 else 30
DT = 1000 / FPS
W, H = 1280, 720           # CSS px; rendered at 1.5x = 1920 x 1080, so the UI reads at video size
os.makedirs(OUT, exist_ok=True)

CLOCK = """
(() => {
  let vt = 0, q = [], id = 0;
  performance.now = () => vt;
  window.requestAnimationFrame = (cb) => { q.push([++id, cb]); return id; };
  window.cancelAnimationFrame = (i) => { q = q.filter(([j]) => j !== i); };
  window.__vtStep = (dt) => {
    vt += dt;
    const cur = q; q = [];
    for (const [, cb] of cur) { try { cb(vt); } catch (e) { console.error(e); } }
    for (const a of document.getAnimations()) {
      if (a.__vt0 === undefined) { a.__vt0 = vt - dt; a.pause(); }
      a.currentTime = vt - a.__vt0;
    }
  };
})();
"""

OVERLAY = """
(() => {
  const st = document.createElement('style');
  st.textContent = `
    .hint, #intro-skip { display: none !important; }
    #cap { position: fixed; left: 50%; bottom: 52px; transform: translateX(-50%); z-index: 50; pointer-events: none;
      display: flex; align-items: stretch; gap: 0; white-space: nowrap; }
    #cap .chip { display: flex; align-items: center; background: var(--accent); color: var(--on-accent); font-family: 'DM Sans', sans-serif;
      font-weight: 700; font-size: 14px; letter-spacing: 0.14em; padding: 0 12px; text-transform: uppercase; }
    #cap .txt { background: rgba(8, 8, 8, 0.86); color: #fff; font-family: 'Bebas Neue', Impact, sans-serif; font-size: 44px; line-height: 1;
      padding: 8px 16px 4px; letter-spacing: 0.01em; border: 1px solid rgba(255,255,255,0.12); border-left: 0; }
    #cap.in { animation: capIn 0.32s cubic-bezier(.2,.8,.2,1) both; }
    @keyframes capIn { from { opacity: 0; transform: translate(-50%, 16px); } to { opacity: 1; transform: translate(-50%, 0); } }
    #cur { position: fixed; z-index: 60; width: 22px; height: 22px; pointer-events: none; left: -100px; top: -100px; }
    #cur svg { display: block; filter: drop-shadow(0 2px 3px rgba(0,0,0,0.55)); }
    .ripple { position: fixed; z-index: 59; width: 18px; height: 18px; margin: -9px 0 0 -9px; border-radius: 50%; border: 3px solid var(--accent);
      pointer-events: none; animation: rip 0.5s ease-out forwards; }
    @keyframes rip { from { transform: scale(0.4); opacity: 1; } to { transform: scale(2.6); opacity: 0; } }
  `;
  document.head.append(st);
  const cur = document.createElement('div');
  cur.id = 'cur';
  cur.innerHTML = '<svg width="22" height="22" viewBox="0 0 24 24"><path d="M3 2 L3 19 L7.6 14.8 L10.6 21.6 L13.6 20.3 L10.6 13.6 L16.8 13.6 Z" fill="#fff" stroke="#111" stroke-width="1.4" stroke-linejoin="round"/></svg>';
  document.body.append(cur);
  document.addEventListener('mousemove', (e) => { cur.style.left = (e.clientX - 3) + 'px'; cur.style.top = (e.clientY - 2) + 'px'; }, true);
  document.addEventListener('mousedown', (e) => {
    const r = document.createElement('div'); r.className = 'ripple'; r.style.left = e.clientX + 'px'; r.style.top = e.clientY + 'px';
    document.body.append(r); setTimeout(() => r.remove(), 3000);
  }, true);
  window.__cap = (chip, txt) => {
    document.getElementById('cap')?.remove();
    if (!txt) return;
    const c = document.createElement('div'); c.id = 'cap'; c.className = 'in';
    c.innerHTML = `<span class="chip"></span><span class="txt"></span>`;
    c.querySelector('.chip').textContent = chip; c.querySelector('.txt').textContent = txt;
    document.body.append(c);
  };
  window.__cursor = (on) => { cur.style.display = on ? '' : 'none'; };
  window.__capLayout = () => {
    const c = document.getElementById('cap');
    if (!c) return;
    const info = document.getElementById('info'), side = document.getElementById('side');
    const vis = (e) => e && !e.hidden && getComputedStyle(e).opacity !== '0' && e.getBoundingClientRect().width > 0;
    let L = 0, R = innerWidth;
    const scrim = [...document.querySelectorAll('.scrim')].some((d) => !d.hidden);
    if (!scrim) {
      if (vis(info)) L = info.getBoundingClientRect().right + 10;
      if (vis(side) && side.dataset.collapsed !== 'true') R = Math.min(R, side.getBoundingClientRect().left - 10);
      if (L === 0) { L = 0; R = innerWidth; }
    }
    c.style.left = ((L + R) / 2) + 'px';
  };
  // a screen point that picks the given part (searches round the projected centre)
  window.__findPart = (id) => {
    const r = window.__r12, V = r.camera.position.constructor;
    const c = r.parts.center(id, new V()).project(r.camera);
    const cv = document.querySelector('canvas').getBoundingClientRect();
    const cx = cv.left + (c.x + 1) / 2 * cv.width, cy = cv.top + (1 - c.y) / 2 * cv.height;
    for (let rad = 0; rad <= 160; rad += 8)
      for (let a = 0; a < 360; a += rad ? 30 : 360) {
        const x = cx + rad * Math.cos(a * Math.PI / 180), y = cy + rad * Math.sin(a * Math.PI / 180);
        if (r.pick(x, y) === id) return [x, y];
      }
    return [cx, cy];
  };
})();
"""

class Rec:
    def __init__(self, pg):
        self.pg, self.n, self.mouse = pg, 0, (W / 2, H / 2)

    async def frames(self, k):
        for _ in range(int(round(k))):
            await self.pg.evaluate(f'__vtStep({DT}); __capLayout()')
            await self.pg.screenshot(path=f'{OUT}/f{self.n:05d}.jpg', type='jpeg', quality=93)
            self.n += 1

    async def secs(self, s):
        await self.frames(s * FPS)

    async def cap(self, chip, txt=None):
        await self.pg.evaluate(f'__cap({json.dumps(chip)}, {json.dumps(txt)})')

    async def move(self, x, y, s=0.6):
        x0, y0 = self.mouse
        k = max(1, int(s * FPS))
        for i in range(1, k + 1):
            t = i / k
            e = t * t * (3 - 2 * t)
            await self.pg.mouse.move(x0 + (x - x0) * e, y0 + (y - y0) * e)
            await self.frames(1)
        self.mouse = (x, y)

    async def drag(self, dx, dy, s=2.0):
        x0, y0 = self.mouse
        await self.pg.mouse.down()
        await self.frames(2)
        k = int(s * FPS)
        for i in range(1, k + 1):
            t = i / k
            e = t * t * (3 - 2 * t)
            await self.pg.mouse.move(x0 + dx * e, y0 + dy * e)
            await self.frames(1)
        await self.pg.mouse.up()
        self.mouse = (x0 + dx, y0 + dy)

    async def click_at(self, x, y, s=0.6):
        await self.move(x, y, s)
        await self.frames(3)
        await self.pg.mouse.down()
        await self.frames(2)
        await self.pg.mouse.up()

    async def click(self, sel, s=0.6, dx=0.5, dy=0.5):
        box = await self.pg.locator(sel).first.bounding_box()
        await self.click_at(box['x'] + box['width'] * dx, box['y'] + box['height'] * dy, s)

    async def part(self, pid):
        return await self.pg.evaluate(f"__findPart('{pid}')")

    async def wheel(self, dy, s=1.0, steps=10):
        k = int(s * FPS)
        per = max(1, k // steps)
        for i in range(k):
            if i % per == 0:
                await self.pg.mouse.wheel(0, dy / steps)
            await self.frames(1)

    async def scroll_el(self, sel, to, s=1.2):
        k = int(s * FPS)
        start = await self.pg.evaluate(f"document.querySelector('{sel}').scrollTop")
        for i in range(1, k + 1):
            t = i / k
            e = t * t * (3 - 2 * t)
            await self.pg.evaluate(f"document.querySelector('{sel}').scrollTop = {start + (to - start) * e}")
            await self.frames(1)


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chrome', headless=True, args=['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=1.5, locale='cs-CZ')
        await ctx.add_init_script(CLOCK)
        await ctx.add_init_script("try { localStorage.setItem('r12-lang', 'cz'); } catch (e) {}")
        pg = await ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:4336/preview.html')
        # let the page load with the clock frozen, so the intro starts at the first recorded frame
        for _ in range(600):
            await pg.evaluate('__vtStep(0)')
            if await pg.evaluate('!!(window.__r12 && window.__r12.intro)'):
                break
            await pg.wait_for_timeout(100)
        await pg.evaluate("document.fonts.ready")
        await pg.evaluate(OVERLAY)
        await pg.wait_for_timeout(1500)
        await pg.evaluate("__cursor(false)")
        r = Rec(pg)

        # 1 intro
        await r.cap('BMW R 12', 'INTERAKTIVNÍ 3D MANUÁL')
        await r.secs(2.6)
        await r.cap('BMW R 12', 'MOTORKA Z ROKU 1935')
        await r.secs(3.4)
        await pg.evaluate("window.__r12.intro.active && window.__r12.intro.finish()")
        await r.secs(0.6)
        await pg.evaluate("__cursor(true)")
        r.mouse = (733, 507)
        await pg.mouse.move(*r.mouse)

        # 2 rotate and zoom
        await r.cap('OVLÁDÁNÍ', 'TAŽENÍM MOTORKOU OTÁČÍM')
        await r.move(667, 480, 0.5)
        await r.drag(-347, 27, 2.4)
        await r.secs(0.5)
        await r.drag(280, -20, 1.8)
        await r.secs(0.4)
        await r.cap('OVLÁDÁNÍ', 'KOLEČKEM PŘIBLÍŽÍM')
        await r.move(640, 373, 0.5)
        await r.wheel(-900, 1.4)
        await r.secs(0.5)
        await r.wheel(900, 1.2)
        await r.secs(0.4)
        await pg.evaluate("document.getElementById('btn-reset').click()")
        await r.secs(1.0)

        # 3 hover
        await r.cap('DÍLY', 'NAJEDU NA DÍL A UKÁŽE SE JEHO NÁZEV')
        for pid in ('tank', 'cylinders', 'headlamp', 'saddle'):
            x, y = await r.part(pid)
            await r.move(x, y, 0.7)
            await r.secs(0.9)

        # 4 manual card
        await r.cap('MANUÁL', 'KLIKNU NA DÍL A OTEVŘE SE MANUÁL')
        x, y = await r.part('cylinders')
        await r.click_at(x, y, 0.6)
        await pg.evaluate("document.getElementById('info').hidden && window.__r12.select('cylinders')")
        await r.secs(1.6)
        await r.cap('MANUÁL', 'POPIS A ÚDAJE Z DOBOVÉ PŘÍRUČKY')
        await r.move(173, 280, 0.7)
        await r.secs(1.4)
        await r.cap('MANUÁL', 'JAK SE O DÍL STARAT')
        await r.scroll_el('#info', 380, 1.4)
        await r.secs(1.0)

        # 5 period sources
        await r.cap('PRAMENY', 'U DÍLU JSOU DOBOVÉ OBRÁZKY A FOTKY')
        await r.scroll_el('#info', 2000, 1.0)
        await r.secs(0.6)
        await r.click('#info-media-grid button', 0.6)
        await pg.wait_for_timeout(1200)
        await r.cap('PRAMENY', 'ZVĚTŠÍM OBRÁZEK S POPISKEM')
        await r.secs(1.8)
        await r.click('#lb-next', 0.7)
        await pg.wait_for_timeout(1000)
        await r.secs(1.6)
        await r.click('#dlg-media [data-close]', 0.6)
        await r.secs(0.6)
        await r.click('#info-close', 0.6)
        await pg.evaluate("document.getElementById('info').hidden || window.__r12.select(null)")
        await pg.evaluate("document.getElementById('btn-reset').click()")
        await r.secs(1.0)

        # 6 systems
        await r.cap('SYSTÉMY', 'ZOBRAZÍM JEN MOTOR')
        await r.click('#sys .sys-btn >> nth=1', 0.7)
        await r.secs(1.6)
        await r.cap('SYSTÉMY', 'PŘIDÁM PŘEVODOVKU A POHON')
        await r.click('#sys .sys-btn >> nth=2', 0.6)
        await r.secs(1.4)
        await r.cap('SYSTÉMY', 'A ZASE CELOU MOTORKU')
        await r.click('#sys .sys-btn >> nth=0', 0.6)
        await r.secs(1.0)

        # 7 explode
        await r.cap('ROZLOŽENÍ', 'ROZLOŽÍM MOTORKU NA DÍLY')
        await pg.evaluate("document.getElementById('btn-reset').click()")
        await r.secs(0.6)
        await r.move(640, 400, 0.4)
        await r.wheel(1300, 0.9)
        await r.click('#btn-explode', 0.7)
        await r.secs(2.0)
        await r.move(700, 507, 0.6)
        await r.drag(-170, 0, 2.0)
        await r.secs(0.4)
        await r.cap('ROZLOŽENÍ', 'KAŽDÝ DÍL JDE OTEVŘÍT')
        x, y = await r.part('tank')
        await r.click_at(x, y, 0.7)
        await pg.evaluate("document.getElementById('info').hidden && window.__r12.select('tank')")
        await r.secs(1.8)
        await r.click('#info-close', 0.5)
        await pg.evaluate("document.getElementById('info').hidden || window.__r12.select(null)")
        await r.cap('ROZLOŽENÍ', 'A SLOŽÍM ZPÁTKY')
        await r.click('#btn-explode', 0.6)
        await r.secs(1.6)

        # 8 views
        for v, t in (('left', 'LEVÝ BOK'), ('front', 'ZEPŘEDU'), ('top', 'SHORA'), ('rear', 'ZEZADU'), ('iso', 'A ZPÁTKY NA 3/4')):
            await r.cap('POHLEDY', t)
            await r.click(f'.view-btn[data-view="{v}"]', 0.45)
            await r.secs(1.5)

        # 9 maintenance
        await r.cap('ÚDRŽBA', 'MAZACÍ PLÁN PŘÍMO NA MOTORCE')
        await r.click('#btn-maint', 0.6)
        await r.secs(2.0)
        await r.cap('ÚDRŽBA', 'CO, JAK ČASTO A ČÍM MAZAT')
        await r.move(1040, 347, 0.6)
        await r.scroll_el('#side', 600, 1.6)
        await r.secs(0.8)
        await r.scroll_el('#side', 0, 0.6)
        await r.click('#btn-maint', 0.6)
        await r.secs(0.8)
        await pg.evaluate("document.getElementById('btn-reset').click()")
        await r.secs(0.6)

        # 10 specs and about
        await r.cap('ÚDAJE', 'TECHNICKÉ ÚDAJE Z ARCHIVU BMW')
        await r.click('#btn-specs', 0.6)
        await r.secs(2.4)
        await pg.keyboard.press('Escape')
        await r.secs(0.4)
        await r.cap('O MOTORCE', 'HISTORIE A VŠECHNY DOBOVÉ PRAMENY')
        await r.click('#btn-about', 0.6)
        await r.secs(1.4)
        await r.scroll_el('#dlg-about .dialog', 900, 1.6)
        await r.secs(1.0)
        await pg.keyboard.press('Escape')
        await r.secs(0.4)

        # 11 languages
        await r.cap('JAZYKY', 'ČESKY')
        x, y = await r.part('fork')
        await r.click_at(x, y, 0.6)
        await pg.evaluate("document.getElementById('info').hidden && window.__r12.select('fork')")
        await r.secs(1.2)
        await r.cap('JAZYKY', 'ENGLISH')
        await r.click('#lang-en', 0.6)
        await r.secs(1.4)
        await r.cap('JAZYKY', 'DEUTSCH')
        await r.click('#lang-de', 0.4)
        await r.secs(1.4)
        await r.click('#lang-cz', 0.4)
        await r.click('#info-close', 0.5)
        await pg.evaluate("document.getElementById('info').hidden || window.__r12.select(null)")
        await r.secs(0.3)

        # 12 end
        await pg.evaluate("document.getElementById('btn-reset').click()")
        await r.move(1253, 707, 0.6)
        await pg.evaluate("__cursor(false)")
        await r.cap('LUKÁŠ ERŠIL', 'BMW R 12 · INTERAKTIVNÍ 3D MANUÁL')
        await pg.evaluate("window.__r12.controls.autoRotate = true; window.__r12.controls.autoRotateSpeed = 1.6")
        await r.secs(3.6)
        print('frames', r.n, 'errors', errs)
        await b.close()

asyncio.run(main())
