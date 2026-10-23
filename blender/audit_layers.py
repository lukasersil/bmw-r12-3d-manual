# Geometry audit, run from build_r12.py with --audit before the meshes are merged:
#   Blender -b -P build_r12.py -- <out_dir> --audit
# 1. Overlays (coachlines, decals, plates, dial): signed distance of every vertex to the surface it
#    lies on. Below 0 = sunk into the paint (hidden), far above = floating.
# 2. Contact: every other object must come within CONTACT of some other object; parts that touch
#    nothing are floating or misplaced.
# Writes audit.json and prints the findings.
import bpy, bmesh, json, os, re
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OVERLAY = {'stripe', 'roundel', 'plate_front', 'plate_rear', 'dial'}
CONTACT = 0.004
SUNK, FLOAT = -0.0004, 0.004

dg = bpy.context.evaluated_depsgraph_get()
objs = [o for o in COL.objects if o.type == 'MESH']

def world_tris(o):
    ev = o.evaluated_get(dg)
    me = ev.to_mesh()
    mw = o.matrix_world
    verts = [mw @ v.co for v in me.vertices]
    me.calc_loop_triangles()
    tris = [tuple(t.vertices) for t in me.loop_triangles]
    mats = [me.materials[t.material_index].name if me.materials else '' for t in me.loop_triangles]
    ev.to_mesh_clear()
    return verts, tris, mats

def base(name):
    return re.sub(r'\.\d{3}$', '', re.sub(r'\.L(\.\d{3})?$', '', name))

data = {}
for o in objs:
    v, t, m = world_tris(o)
    if t:
        data[o.name] = (v, t, m)

overlay_names = [n for n, (v, t, m) in data.items() if m and all(x in OVERLAY for x in m)]
host_names = [n for n in data if n not in overlay_names]

# one tree over every non-overlay surface, with the owner of each triangle
V_all, T_all, owner = [], [], []
for n in host_names:
    v, t, m = data[n]
    off = len(V_all)
    V_all += v
    T_all += [(a + off, b + off, c + off) for a, b, c in t]
    owner += [n] * len(t)
host_tree = BVHTree.FromPolygons(V_all, T_all, all_triangles=True)

report = {'overlays': {}, 'no_contact': []}
for n in overlay_names:
    v, t, m = data[n]
    step = max(1, len(v) // 400)
    ds, own_of = [], []
    for co in v[::step]:
        hit = host_tree.find_nearest(co)
        if hit[0] is None:
            continue
        p, nrm, idx, dist = hit
        ds.append((co - p).dot(nrm))
        own_of.append(owner[idx])
    if not ds:
        continue
    ds_raw = list(ds)
    worst = sorted(zip(ds, v[::step], own_of), key=lambda q: q[0])[:3]
    ds.sort()
    sunk = sum(1 for d in ds if d < SUNK) / len(ds)
    flo = sum(1 for d in ds if d > FLOAT) / len(ds)
    b = base(n)
    r = report['overlays'].setdefault(b, {'objects': 0, 'min': 1, 'max': -1, 'sunk': 0.0, 'float': 0.0})
    r['objects'] += 1
    r['min'] = min(r['min'], ds[0])
    r['max'] = max(r['max'], ds[-1])
    r['sunk'] = max(r['sunk'], sunk)
    r['float'] = max(r['float'], flo)
    if ds[0] < SUNK:
        r.setdefault('worst', []).extend([[round(d * 1000, 2), round(c.x, 3), round(c.z, 3), round(-c.y, 3), w] for d, c, w in worst])
    if ds[-1] > FLOAT:
        hi = sorted(zip(ds_raw, v[::step], own_of), key=lambda q: -q[0])[:3]
        r.setdefault('high', []).extend([[round(d * 1000, 2), round(c.x, 3), round(c.z, 3), round(-c.y, 3), w] for d, c, w in hi])

# contact: any triangle of another object within CONTACT of a sampled vertex
all_tree = host_tree
for n in host_names:
    v, t, m = data[n]
    step = max(1, len(v) // 150)
    touch = False
    for co in v[::step]:
        for (p, nrm, idx, dist) in all_tree.find_nearest_range(co, CONTACT):
            if owner[idx] != n:
                touch = True
                break
        if touch:
            break
    if not touch:
        # embedded in another part (intersecting triangles) counts as attached
        own = BVHTree.FromPolygons(v, t, all_triangles=True)
        if any(owner[j] != n for i, j in own.overlap(host_tree)):
            continue
        c = sum(v, Vector()) / len(v)
        gap = min((all_tree.find_nearest_range(co, 0.05) or [(None, None, None, 1.0)]) and
                  min([d for (p_, n_, j, d) in all_tree.find_nearest_range(co, 0.05) if owner[j] != n] or [1.0]) for co in v[::step])
        report['no_contact'].append({'name': n, 'bike_xyz': [round(c.x, 3), round(c.z, 3), round(-c.y, 3)], 'gap_mm': round(gap * 1000, 1)})

json.dump(report, open(os.path.join(OUT, 'audit.json'), 'w'), indent=1)
print('AUDIT overlays (signed offset to the surface below, metres)')
for b, r in sorted(report['overlays'].items()):
    flag = []
    if r['sunk'] > 0.02:
        flag.append(f"SUNK {r['sunk']:.0%}")
    if r['float'] > 0.02:
        flag.append(f"FLOAT {r['float']:.0%}")
    print(f"  {b:34s} n={r['objects']:3d} min={r['min']*1000:7.2f}mm max={r['max']*1000:7.2f}mm {' '.join(flag)}")
    if r.get('worst') and flag:
        print('      worst (mm, bike x y z):', r['worst'][:4])
    if r.get('high') and 'FLOAT' in ' '.join(flag):
        print('      highest (mm, bike x y z):', r['high'][:4])
print('AUDIT objects touching nothing within', CONTACT * 1000, 'mm:', len(report['no_contact']))
for r in report['no_contact']:
    print('  ', r['name'], 'bike', r['bike_xyz'], 'nearest other part', r['gap_mm'], 'mm')
