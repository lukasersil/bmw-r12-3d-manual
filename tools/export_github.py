# Clean public export of the project for GitHub: copies only whitelisted files into <target>, turns the
# artifact page into a standalone index.html, strips local paths, and leaves out working notes, old
# screenshots, the Artlist music and anything else that is not ours to give away.
#   python3 tools/export_github.py <target_dir> [--video path.mp4] [--shots dir]
import json, os, re, shutil, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = sys.argv[1:]
TARGET = os.path.abspath(args[0])
VIDEO = args[args.index('--video') + 1] if '--video' in args else None
SHOTS = args[args.index('--shots') + 1] if '--shots' in args else None

KEEP = [
    'src', 'scene/r12.txt', 'scene/logo.txt', 'draco', 'media', 'assets/avatar.png',
    'blender/build_r12.py', 'blender/build_logo.py', 'blender/make_plates.py', 'blender/audit_layers.py',
    'blender/save_scene.py', 'blender/open_view.py', 'blender/r12_scene.blend', 'blender/textures',
    'blender/refs/c3h_r12_1940_spurzem.jpg', 'blender/refs/etl_r12_1938_partslist.jpg', 'blender/refs/cam_c3h.json',
    'tools/make_media.py', 'tools/media_spec.py', 'tools/make_lens.py', 'tools/capture_demo.py', 'tools/export_github.py',
]
# never exported, even if a rule above would match them
SKIP = re.compile(r'(NALEZY\.md|\.blend1$|/screenshots/|/compare/|\.DS_Store$|__pycache__)')

for name in os.listdir(TARGET) if os.path.isdir(TARGET) else []:
    if name != '.git':
        p = os.path.join(TARGET, name)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
os.makedirs(TARGET, exist_ok=True)

def copy(rel, dst_rel=None):
    src, dst = os.path.join(HERE, rel), os.path.join(TARGET, dst_rel or rel)
    if os.path.isdir(src):
        for root, _, files in os.walk(src):
            for f in files:
                r = os.path.relpath(os.path.join(root, f), HERE)
                if not SKIP.search('/' + r):
                    copy(r, os.path.join(dst_rel, os.path.relpath(r, rel)) if dst_rel else None)
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)

for rel in KEEP:
    copy(rel)
for glb in ('r12.glb', 'logo.glb'):
    copy(f'blender/out/{glb}', f'model/{glb}')

# repository docs (README, licences, credits, .gitignore) live in github/ and go to the root
for f in os.listdir(os.path.join(HERE, 'github')):
    shutil.copy2(os.path.join(HERE, 'github', f), os.path.join(TARGET, f))

# standalone page: the artifact body wrapped in a document, as in preview.html
body = open(os.path.join(HERE, 'index.html'), encoding='utf-8').read()
head = ('<!doctype html><html lang="cs"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
        '<style>[hidden]{display:none!important}body{margin:0}</style></head><body>')
open(os.path.join(TARGET, 'index.html'), 'w', encoding='utf-8').write(head + body + '\n</body></html>\n')

# no local paths in the camera file of the reference photo
cam = os.path.join(TARGET, 'blender/refs/cam_c3h.json')
d = json.load(open(cam))
d['image'] = 'c3h_r12_1940_spurzem.jpg'
json.dump(d, open(cam, 'w'), indent=1)
# the .blend keeps the author's home folder in its file header: re-save it uncompressed with the image paths
# left relative, then blank every absolute path (the strings are null-padded fields, so the file stays valid)
BLENDER = '/Applications/Blender.app/Contents/MacOS/Blender'
blend = os.path.join(TARGET, 'blender/r12_scene.blend')
if os.path.exists(BLENDER):
    import subprocess, tempfile
    saver = os.path.join(TARGET, '_save.py')
    open(saver, 'w').write('import bpy, sys\nbpy.ops.wm.save_as_mainfile(filepath=sys.argv[-1], compress=False, copy=True, relative_remap=False)\n')
    raw = blend + '.raw'
    subprocess.run([BLENDER, '-b', blend, '-P', saver, '--', raw], check=True, capture_output=True)
    os.remove(saver)
    data = bytearray(open(raw, 'rb').read())
    for m in re.finditer(rb'/(Users|private|home)/[^\x00]*', bytes(data)):
        data[m.start():m.end()] = b'\x00' * (m.end() - m.start())
    open(blend, 'wb').write(data)
    os.remove(raw)
else:
    print('WARNING: Blender not found, r12_scene.blend not cleaned')
# the content comment pointed at a working file outside the project
c = os.path.join(TARGET, 'src/data/content.js')
s = open(c, encoding='utf-8').read().replace('Detail ke stránkám: ../../sources.md', 'Prameny: CREDITS.md')
open(c, 'w', encoding='utf-8').write(s)

if VIDEO:                       # the version without music: the Artlist licence does not allow redistribution
    os.makedirs(os.path.join(TARGET, 'video'), exist_ok=True)
    shutil.copy2(VIDEO, os.path.join(TARGET, 'video/bmw-r12-3d-manual-demo.mp4'))
if SHOTS:
    os.makedirs(os.path.join(TARGET, 'docs'), exist_ok=True)
    for f in sorted(os.listdir(SHOTS)):
        if f.endswith('.jpg'):
            shutil.copy2(os.path.join(SHOTS, f), os.path.join(TARGET, 'docs', f))

# last check: nothing that looks like a local path, an e-mail or a key may leave
bad = re.compile(r'(/Users/|/private/tmp|scratchpad|personal-os|@gmail\.com|claude-cron|api[_-]?key)', re.I)
hits = []
for root, _, files in os.walk(TARGET):
    if '/.git' in root:
        continue
    for f in files:
        if f.endswith(('.py', '.js', '.html', '.md', '.json', '.css', '.txt')) and not f.endswith(('r12.txt', 'logo.txt', 'export_github.py')):
            p = os.path.join(root, f)
            for i, line in enumerate(open(p, encoding='utf-8', errors='ignore'), 1):
                if bad.search(line):
                    hits.append(f'{os.path.relpath(p, TARGET)}:{i}: {line.strip()[:120]}')
print('\n'.join(hits) if hits else 'clean: no local paths, e-mails or keys')
