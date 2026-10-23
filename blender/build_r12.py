# BMW R 12 (1935-1942), civilian single-carburettor model, built from code in Blender.
#   Blender -b -P build_r12.py -- <out_dir> [--glb] [--checks] [--blend]
# Bike coordinates in this file: x forward, y up, z to the rider's right, metres, origin on the
# ground midway between the axles (same frame as the three.js page). V() maps them to Blender
# (X forward, Y left, Z up); the glTF exporter turns Blender Z-up into Y-up, so the page gets the
# bike coordinates back unchanged.
# Dimensions: BMW Group Archive fact sheet (wheelbase 1380, 3.50-19 tyres, 200 mm drums, 78 x 78 mm)
# and the side, top and section drawings of the 1936 instruction book (side view ~1 px = 1 mm).
import bpy, bmesh, math, sys, os
from mathutils import Vector, Matrix, Quaternion
from mathutils.bvhtree import BVHTree

ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = os.path.abspath(ARGS[0] if ARGS else '.')
HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, 'textures')
os.makedirs(OUT, exist_ok=True)

def V(x, y, z):
    return Vector((x, -z, y))

def lerp(a, b, t):
    return a + (b - a) * t

# ------------------------------------------------------------------------------ scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
COL = bpy.data.collections.new('R12')
scene.collection.children.link(COL)

# ------------------------------------------------------------------------------ materials
MATS = {}
def mat(name, color, metal=0.0, rough=0.5, coat=0.0, coat_rough=0.05, alpha=1.0, emit=None, image=None, sheen=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    if coat:
        p.inputs['Coat Weight'].default_value = coat
        p.inputs['Coat Roughness'].default_value = coat_rough
    if sheen:
        p.inputs['Sheen Weight'].default_value = sheen
    if alpha < 1:
        p.inputs['Alpha'].default_value = alpha
        m.surface_render_method = 'BLENDED'
    if emit:
        p.inputs['Emission Color'].default_value = (*emit, 1)
        p.inputs['Emission Strength'].default_value = 1.0
    if image:
        img = bpy.data.images.load(os.path.join(TEX, image))
        tn = nt.nodes.new('ShaderNodeTexImage')
        tn.image = img
        nt.links.new(tn.outputs['Color'], p.inputs['Base Color'])
        if image in ('roundel.png', 'kneepad.png', 'lens.png'):
            nt.links.new(tn.outputs['Alpha'], p.inputs['Alpha'])
            m.surface_render_method = 'BLENDED'
        if image == 'lens.png':
            # the silvered reflector behind the flutes catches the daylight; the dark studio cannot give
            # it that, so a little of the texture is carried as emission
            nt.links.new(tn.outputs['Color'], p.inputs['Emission Color'])
            p.inputs['Emission Strength'].default_value = 0.32
    MATS[name] = m
    return m

M = {
    'paint': mat('paint', (0.006, 0.006, 0.007), rough=0.3, coat=1.0, coat_rough=0.04),
    'stripe': mat('stripe', (0.88, 0.87, 0.83), rough=0.3, coat=1.0, coat_rough=0.04),
    'chrome': mat('chrome', (0.96, 0.96, 0.96), metal=1, rough=0.05),
    'alu': mat('alu', (0.62, 0.62, 0.6), metal=1, rough=0.24),
    'alusatin': mat('alusatin', (0.72, 0.72, 0.7), metal=1, rough=0.48),   # bead-blasted cylinder heads
    'cast': mat('cast', (0.5, 0.5, 0.485), metal=0.85, rough=0.5),
    'steel': mat('steel', (0.55, 0.56, 0.58), metal=1, rough=0.3),
    'darkmetal': mat('darkmetal', (0.025, 0.025, 0.026), metal=0.7, rough=0.42),
    'black': mat('black', (0.012, 0.012, 0.012), rough=0.5),
    'rubber': mat('rubber', (0.016, 0.016, 0.016), rough=0.9),
    'leather': mat('leather', (0.011, 0.0105, 0.0098), rough=0.62),
    'glass': mat('glass', (1, 1, 1), rough=0.02, alpha=0.18),
    'dialglass': mat('dialglass', (1, 1, 1), rough=0.02, alpha=0.05),
    'redlens': mat('redlens', (0.45, 0.02, 0.02), rough=0.2, emit=(0.25, 0.0, 0.0)),
    'ivory': mat('ivory', (0.46, 0.42, 0.33), rough=0.4),
    'porcelain': mat('porcelain', (0.86, 0.84, 0.78), rough=0.2),
    'brass': mat('brass', (0.72, 0.52, 0.22), metal=1, rough=0.32),
    'roundel': mat('roundel', (1, 1, 1), rough=0.3, image='roundel.png'),
    'kneepad': mat('kneepad', (1, 1, 1), rough=0.85, image='kneepad.png'),
    'plate_front': mat('plate_front', (1, 1, 1), rough=0.5, image='plate_front.png'),
    'plate_rear': mat('plate_rear', (1, 1, 1), rough=0.5, image='plate_rear.png'),
    'dial': mat('dial', (1, 1, 1), rough=0.35, image='dial.png'),
    'lens': mat('lens', (1, 1, 1), rough=0.08, image='lens.png'),
}

M['leather'].node_tree.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value = 0.22

# ------------------------------------------------------------------------------ part groups
PART = None
def part(pid, explode=(0, 0, 0), name=None):
    """Start a new part object: an empty that carries the part id and its explode vector."""
    global PART
    e = bpy.data.objects.new(name or f'P.{pid}', None)
    e.empty_display_size = 0.05
    e['part'] = pid
    e['explode'] = list(explode)
    COL.objects.link(e)
    PART = e
    return e

def finish(bm, name, material, sharp=34, smooth=True, parent=None, subsurf=0):
    me = bpy.data.meshes.new(name)
    if smooth:
        for f in bm.faces:
            f.smooth = True
        lim = math.radians(sharp)
        for e in bm.edges:
            if len(e.link_faces) == 2 and e.calc_face_angle(0) > lim:
                e.smooth = False
    bm.to_mesh(me)
    bm.free()
    me.materials.append(M[material] if isinstance(material, str) else material)
    o = bpy.data.objects.new(name, me)
    COL.objects.link(o)
    o.parent = parent or PART
    if subsurf:
        mod = o.modifiers.new('sub', 'SUBSURF')
        mod.levels = subsurf
        mod.render_levels = subsurf
    return o

# ------------------------------------------------------------------------------ geometry helpers
def catmull(pts, per=10, closed=False):
    """Uniform Catmull-Rom through Vectors."""
    P = list(pts)
    if len(P) < 3:
        return P
    out = []
    n = len(P)
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = P[(i - 1) % n] if closed else P[max(i - 1, 0)]
        p1 = P[i]
        p2 = P[(i + 1) % n] if closed else P[i + 1]
        p3 = P[(i + 2) % n] if closed else P[min(i + 2, n - 1)]
        for k in range(per):
            t = k / per
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    if not closed:
        out.append(P[-1])
    return out

def frames(pts, ref=None):
    n = len(pts)
    T = []
    for i in range(n):
        d = pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]
        T.append(d.normalized())
    ref = ref or Vector((0, 0, 1))
    N = T[0].cross(ref)
    if N.length < 1e-6:
        N = T[0].cross(Vector((1, 0, 0)))
    N.normalize()
    out = [(T[0], N, T[0].cross(N))]
    for i in range(1, n):
        q = T[i - 1].rotation_difference(T[i])
        N = q @ N
        N = (N - T[i] * N.dot(T[i])).normalized()
        out.append((T[i], N, T[i].cross(N)))
    return out

def sweep(name, pts, profile, material, ref=None, caps=True, sharp=34, closed_path=False, subsurf=0):
    """Sweep a closed 2D profile [(u, v)] along Blender-space points."""
    bm = bmesh.new()
    fr = frames(pts, ref)
    rings = []
    for p, (t, n, b) in zip(pts, fr):
        rings.append([bm.verts.new(p + n * u + b * v) for (u, v) in profile])
    P = len(profile)
    segs = len(rings) if closed_path else len(rings) - 1
    for i in range(segs):
        a, c = rings[i], rings[(i + 1) % len(rings)]
        for j in range(P):
            bm.faces.new((a[j], a[(j + 1) % P], c[(j + 1) % P], c[j]))
    if caps and not closed_path:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finish(bm, name, material, sharp=sharp, subsurf=subsurf)

def circle_profile(r, seg=12):
    return [(r * math.cos(2 * math.pi * k / seg), r * math.sin(2 * math.pi * k / seg)) for k in range(seg)]

def rrect_profile(w, h, r, seg=3):
    pts = []
    cx, cy = w / 2 - r, h / 2 - r
    for (x, y, a0) in [(cx, cy, 0), (-cx, cy, 90), (-cx, -cy, 180), (cx, -cy, 270)]:
        for k in range(seg + 1):
            a = math.radians(a0 + 90 * k / seg)
            pts.append((x + r * math.cos(a), y + r * math.sin(a)))
    return pts

def tube(name, bike_pts, r, material, seg=14, per=8, caps=True):
    pts = catmull([V(*p) for p in bike_pts], per) if len(bike_pts) > 2 else [V(*p) for p in bike_pts]
    if len(bike_pts) == 2:
        a, b = pts
        pts = [a.lerp(b, k / 6) for k in range(7)]
    return sweep(name, pts, circle_profile(r, seg), material, caps=caps, sharp=60)

def lathe(name, profile, origin, axis, material, seg=48, sharp=40, subsurf=0):
    """Revolve [(r, t)] around the bike-space axis through origin."""
    o = V(*origin)
    ax = V(*axis).normalized()
    u = ax.cross(Vector((0, 0, 1)))
    if u.length < 1e-4:
        u = ax.cross(Vector((1, 0, 0)))
    u.normalize()
    w = ax.cross(u)
    bm = bmesh.new()
    rings = []
    for (r, t) in profile:
        ring = []
        for k in range(seg):
            a = 2 * math.pi * k / seg
            ring.append(bm.verts.new(o + ax * t + (u * math.cos(a) + w * math.sin(a)) * max(r, 1e-5)))
        rings.append(ring)
    for i in range(len(rings) - 1):
        a, c = rings[i], rings[i + 1]
        for k in range(seg):
            bm.faces.new((a[k], a[(k + 1) % seg], c[(k + 1) % seg], c[k]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=2e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finish(bm, name, material, sharp=sharp, subsurf=subsurf)

def cyl(name, a, b, r, material, seg=32, r2=None, sharp=40):
    A, B = Vector(a), Vector(b)
    L = (B - A).length
    return lathe(name, [(0, 0), (r, 0), (r2 if r2 is not None else r, L), (0, L)], a, tuple(B - A), material, seg=seg, sharp=sharp)

def rbox(name, center, size, r, material, rot=None, seg=3):
    """Rounded box in bike space; size = (x, y, z) extents, rot = Euler in bike space (deg, about z first)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))  # bike axes before mapping
    if r > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=r, segments=seg, profile=0.5, affect='EDGES', clamp_overlap=True)
    rz = math.radians(rot[0]) if rot else 0
    ry = math.radians(rot[1]) if rot and len(rot) > 1 else 0
    for v in bm.verts:
        x, y, z = v.co
        # rotate about bike z (pitch), then bike y (yaw)
        x, y = x * math.cos(rz) - y * math.sin(rz), x * math.sin(rz) + y * math.cos(rz)
        x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
        v.co = V(x + center[0], y + center[1], z + center[2])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finish(bm, name, material, sharp=35)

def slab(name, outline, thick, zc, material, bevel=0.0, per=6, smooth_outline=True, sharp=34):
    """Extrude a closed bike-space (x, y) outline to a slab centred on z = zc."""
    pts = catmull([Vector((x, y, 0)) for x, y in outline], per, closed=True) if smooth_outline else [Vector((x, y, 0)) for x, y in outline]
    bm = bmesh.new()
    f = [bm.verts.new(V(p.x, p.y, zc - thick / 2)) for p in pts]
    bm.faces.new(f)
    ret = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    for v in [e for e in ret['geom'] if isinstance(e, bmesh.types.BMVert)]:
        v.co += V(0, 0, thick)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bevel > 0:
        caps = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle(0) > math.radians(60)]
        bmesh.ops.bevel(bm, geom=caps, offset=bevel, segments=3, profile=0.5, affect='EDGES', clamp_overlap=True)
    return finish(bm, name, material, sharp=sharp)

def plate(name, outline, y0, y1, material, bevel=0.0, per=6, sharp=34):
    """Horizontal slab: a closed plan-view (x, z) outline in bike space, from height y0 up to y1."""
    pts = catmull([Vector((x, 0, z)) for x, z in outline], per, closed=True)
    bm = bmesh.new()
    f = [bm.verts.new(V(p.x, y0, p.z)) for p in pts]
    bm.faces.new(f)
    ret = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    for v in [e for e in ret['geom'] if isinstance(e, bmesh.types.BMVert)]:
        v.co += V(0, y1 - y0, 0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bevel > 0:
        caps = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle(0) > math.radians(60)]
        bmesh.ops.bevel(bm, geom=caps, offset=bevel, segments=3, profile=0.5, affect='EDGES', clamp_overlap=True)
    return finish(bm, name, material, sharp=sharp)

def loft(name, rings, material, cap=True, subsurf=2, sharp=80):
    """Rings: list of lists of bike-space points (same count)."""
    bm = bmesh.new()
    R = [[bm.verts.new(V(*p)) for p in ring] for ring in rings]
    P = len(rings[0])
    for i in range(len(R) - 1):
        a, c = R[i], R[i + 1]
        for j in range(P):
            bm.faces.new((a[j], a[(j + 1) % P], c[(j + 1) % P], c[j]))
    if cap:
        bm.faces.new(list(reversed(R[0])))
        bm.faces.new(R[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finish(bm, name, material, sharp=sharp, subsurf=subsurf)

def ribbon(name, pts, sides, width, material, double=0.0):
    """Flat strip through bike-space points; sides = unit vectors (bike space) across the strip.
    double > 0 draws the coachline pair of the R 12: two strips of 'width' with that gap between."""
    bm = bmesh.new()
    offs = (0.0,) if not double else (-(width + double) / 2, (width + double) / 2)
    for off in offs:
        L, Rr = [], []
        for p, s in zip(pts, sides):
            p, s = Vector(p), Vector(s)
            c = p + s * off
            L.append(bm.verts.new(V(*(c - s * width / 2))))
            Rr.append(bm.verts.new(V(*(c + s * width / 2))))
        for i in range(len(pts) - 1):
            bm.faces.new((L[i], Rr[i], Rr[i + 1], L[i + 1]))
    return finish(bm, name, material, sharp=80)

def disc_decal(name, center, normal, radius, material, seg=48, up=(0, 1, 0)):
    """UV-mapped disc facing a bike-space normal; 'up' (bike space) is the texture's up as seen from outside."""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new()
    n = Vector(normal).normalized()
    w = Vector(up) - n * Vector(up).dot(n)
    w.normalize()
    u = w.cross(n)  # screen right for a viewer looking at the face
    c = Vector(center)
    vs = [bm.verts.new(V(*(c + (u * math.cos(2 * math.pi * k / seg) + w * math.sin(2 * math.pi * k / seg)) * radius))) for k in range(seg)]
    f = bm.faces.new(vs)
    if f.normal.dot(V(*n)) < 0:
        f.normal_flip()
    for loop in f.loops:
        d = loop.vert.co - V(*c)
        loop[uvl].uv = (0.5 + d.dot(V(*u)) / (2 * radius), 0.5 + d.dot(V(*w)) / (2 * radius))
    return finish(bm, name, material, smooth=False)

def quad_decal(name, corners, material):
    """Four bike-space corners in order bl, br, tr, tl, UV-mapped 0..1."""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new()
    vs = [bm.verts.new(V(*p)) for p in corners]
    f = bm.faces.new(vs)
    for loop, uv in zip(f.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
        loop[uvl].uv = uv
    return finish(bm, name, material, smooth=False)

def poly_decal(name, outline, z, side, material):
    """Flat face on a closed (x, y) outline at depth z, UVs from its bounding box, readable from the 'side' (+1/-1) viewer."""
    xs = [p[0] for p in outline]; ys = [p[1] for p in outline]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new()
    vs = [bm.verts.new(V(x, y, z)) for x, y in outline]
    f = bm.faces.new(vs)
    if f.normal.dot(V(0, 0, side)) < 0:
        f.normal_flip()
    for loop in f.loops:
        co = loop.vert.co
        x, y = co.x, co.z
        u = (x - x0) / (x1 - x0) if side > 0 else (x1 - x) / (x1 - x0)
        loop[uvl].uv = (u, (y - y0) / (y1 - y0))
    return finish(bm, name, material, smooth=False)

def mirror(objs):
    """Duplicate objects to the other side (bike z -> -z) under the current part."""
    out = []
    for o in objs:
        me = o.data.copy()
        me.transform(Matrix.Scale(-1, 4, Vector((0, 1, 0))))
        me.flip_normals()
        c = bpy.data.objects.new(o.name + '.L', me)
        COL.objects.link(c)
        c.parent = PART
        for mo in o.modifiers:
            nm = c.modifiers.new(mo.name, mo.type)
            if mo.type == 'SUBSURF':
                nm.levels, nm.render_levels = mo.levels, mo.render_levels
        out.append(c)
    return out

def kids(e):
    return [o for o in COL.objects if o.parent == e]

# ------------------------------------------------------------------------------ key dimensions
XF, XR, AY = 0.69, -0.69, 0.33
TYRE_R, TYRE_T = 0.33, 0.045
# steering head angle measured on both handbook side views (fork covers from the axle up to the top bridge): 31-33 degrees
RAKE, OFFSET, FORK_Z = math.radians(31.5), 0.065, 0.105
sR, cR = math.sin(RAKE), math.cos(RAKE)

def forkpt(L):
    return (XF - sR * L, AY + cR * L)

def steerpt(L):
    x, y = forkpt(L)
    return (x - cR * OFFSET, y - sR * OFFSET)

FRAME_Z = 0.10
UPPER_A, UPPER_B = (0.328, 0.787), (-0.70, 0.395)
def upper_y(x):
    return UPPER_B[1] + (x - UPPER_B[0]) * (UPPER_A[1] - UPPER_B[1]) / (UPPER_A[0] - UPPER_B[0])

CYL_X, CYL_Y = 0.095, 0.35

# ==============================================================================================
# WHEELS AND BRAKES
# ==============================================================================================
def wheel(pid, x, explode, front):
    part(pid, explode)
    # tyre with a ribbed period tread
    lathe(f'{pid}.tyre', [(TYRE_R - 2 * TYRE_T + 0.004, -0.03), (TYRE_R - 0.03, -0.044), (TYRE_R - 0.008, -0.04), (TYRE_R, -0.024), (TYRE_R + 0.001, 0), (TYRE_R, 0.024), (TYRE_R - 0.008, 0.04), (TYRE_R - 0.03, 0.044), (TYRE_R - 2 * TYRE_T + 0.004, 0.03)], (x, AY, 0), (0, 0, 1), 'rubber', seg=128, sharp=70)
    for z0 in (-0.013, 0.013):
        lathe(f'{pid}.groove{z0}', [(TYRE_R + 0.0005, z0 - 0.003), (TYRE_R - 0.004, z0 - 0.002), (TYRE_R - 0.004, z0 + 0.002), (TYRE_R + 0.0005, z0 + 0.003)], (x, AY, 0), (0, 0, 1), 'black', seg=128)
    # period road tread: fine shallow blocks on the shoulders either side of the two grooves (Fig. 23, photos)
    for k in range(112):
        a = 2 * math.pi * (k + 0.5) / 112
        for sgn in (-1, 1):
            r = TYRE_R - 0.0035
            c = (x + r * math.cos(a), AY + r * math.sin(a), sgn * 0.0265)
            rbox(f'{pid}.lug', c, (0.0095, 0.004, 0.0105), 0.0015, 'rubber', rot=(math.degrees(a) - 90,))
    # black rim with a white line and plated nipples
    lathe(f'{pid}.rim', [(0.247, -0.032), (0.252, -0.03), (0.251, -0.022), (0.241, -0.016), (0.236, -0.006), (0.236, 0.006), (0.241, 0.016), (0.251, 0.022), (0.252, 0.03), (0.247, 0.032), (0.233, 0.028), (0.229, 0), (0.233, -0.028), (0.247, -0.032)], (x, AY, 0), (0, 0, 1), 'paint', seg=128, sharp=50)
    for sg in (-1, 1):
        # thin band on the sloped outer face of the rim, between (0.233, 0.028) and (0.247, 0.032)
        lathe(f'{pid}.rimline', [(0.2384, sg * 0.03007), (0.2416, sg * 0.03098)], (x, AY, 0), (0, 0, 1), 'stripe', seg=128)
    # 40 spokes, cross-laced to two flanges
    for i in range(40):
        side = 1 if i % 2 else -1
        aR = 2 * math.pi * i / 40
        aH = aR + (0.62 if (i // 2) % 2 else -0.62)
        rim = (x + 0.232 * math.cos(aR), AY + 0.232 * math.sin(aR), side * 0.006)
        hub = (x + 0.05 * math.cos(aH), AY + 0.05 * math.sin(aH), side * 0.045)
        cyl(f'{pid}.spoke', hub, rim, 0.0019, 'chrome', seg=6, sharp=80)
        cyl(f'{pid}.nipple', rim, (rim[0] - 0.012 * math.cos(aR), rim[1] - 0.012 * math.sin(aR), rim[2]), 0.0032, 'chrome', seg=6)
    # hub barrel, flanges and axle with nuts
    lathe(f'{pid}.hub', [(0.0, -0.07), (0.03, -0.07), (0.045, -0.06), (0.056, -0.05), (0.056, -0.042), (0.036, -0.036), (0.034, 0), (0.036, 0.036), (0.056, 0.042), (0.056, 0.05), (0.045, 0.06), (0.03, 0.07), (0.0, 0.07)], (x, AY, 0), (0, 0, 1), 'black', seg=48)
    cyl(f'{pid}.axle', (x, AY, -0.115), (x, AY, 0.115), 0.0095, 'steel', seg=16)
    for z0 in (-0.115, 0.1):
        cyl(f'{pid}.nut', (x, AY, z0), (x, AY, z0 + 0.015), 0.016, 'steel', seg=6, sharp=30)

wheel('frontwheel', XF, (0.6, 0, 0), True)
wheel('rearwheel', XR, (-0.45, 0, 0), False)

# front brake: 200 mm drum, aluminium anchor plate on the right with the lever arm and cable
part('brakes', (0.6, 0, 0.22), 'P.brakes.front')
lathe('brakes.front.drum', [(0.04, 0.045), (0.1, 0.045), (0.103, 0.05), (0.103, 0.085), (0.1, 0.088), (0.04, 0.088)], (XF, AY, 0), (0, 0, 1), 'black', seg=64)
lathe('brakes.front.hubcover', [(0.04, -0.088), (0.1, -0.088), (0.103, -0.085), (0.103, -0.05), (0.1, -0.045), (0.04, -0.045)], (XF, AY, 0), (0, 0, 1), 'black', seg=64)
lathe('brakes.front.hubcap', [(0.0, -0.096), (0.03, -0.096), (0.045, -0.09), (0.06, -0.088), (0.0, -0.088)], (XF, AY, 0), (0, 0, 1), 'black', seg=48)
# anchor plate sits inside a black drum ring that carries a circle of bolts (photo Commons NIK 4083)
# plain aluminium anchor plate (Fig. 7): Bowden adjuster 'a' at the top rear, the cam boss as a round
# bump at the lower front, two nuts below the axle
lathe('brakes.front.plate', [(0.02, 0.088), (0.088, 0.088), (0.089, 0.093), (0.08, 0.099), (0.04, 0.103), (0.02, 0.104)], (XF, AY, 0), (0, 0, 1), 'alusatin', seg=72)
ca = math.radians(-35)
lathe('brakes.front.cam', [(0.0, 0.0), (0.017, 0.0), (0.016, 0.006), (0.01, 0.01), (0.0, 0.011)], (XF + 0.06 * math.cos(ca), AY + 0.06 * math.sin(ca), 0.099), (0, 0, 1), 'alusatin', seg=32)
for a_ in (-105, -70):
    a = math.radians(a_)
    cyl('brakes.front.nut', (XF + 0.07 * math.cos(a), AY + 0.07 * math.sin(a), 0.097), (XF + 0.07 * math.cos(a), AY + 0.07 * math.sin(a), 0.104), 0.0055, 'steel', seg=6, sharp=30)
aa = math.radians(128)
AP = (XF + 0.078 * math.cos(aa), AY + 0.078 * math.sin(aa))
cyl('brakes.front.adjuster', (AP[0], AP[1], 0.096), (AP[0], AP[1], 0.112), 0.006, 'alusatin', seg=12)
rbox('brakes.front.wing', (AP[0], AP[1], 0.115), (0.02, 0.004, 0.006), 0.0015, 'steel', rot=(38,))
for k in range(16):
    a = 2 * math.pi * (k + 0.5) / 16
    cyl('brakes.front.bolt', (XF + 0.0945 * math.cos(a), AY + 0.0945 * math.sin(a), 0.087), (XF + 0.0945 * math.cos(a), AY + 0.0945 * math.sin(a), 0.0915), 0.0034, 'steel', seg=6, sharp=30)
tube('brakes.front.cable', [(AP[0], AP[1], 0.112), (AP[0] - 0.02, AP[1] + 0.06, 0.155), (0.56, 0.62, 0.158), (0.47, 0.78, 0.158), (0.4, 0.86, 0.18), (0.262, 0.884, 0.285)], 0.0032, 'black', seg=6)
# rear brake: drum inside the bevel-drive side of the hub, arm and rod from the pedal
part('brakes', (-0.45, 0, 0.16), 'P.brakes.rear')
lathe('brakes.rear.drum', [(0.04, 0.05), (0.114, 0.05), (0.118, 0.053), (0.118, 0.056), (0.04, 0.056)], (XR, AY, 0), (0, 0, 1), 'black', seg=72)
cyl('brakes.rear.arm', (XR + 0.04, AY - 0.11, 0.084), (XR + 0.065, AY - 0.14, 0.084), 0.008, 'steel', seg=8)

# ==============================================================================================
# FRAME
# ==============================================================================================
part('frame', (0, 0, 0))
PRESS = rrect_profile(0.05, 0.036, 0.015, 4)   # pressed channel, u in the bike plane, v across
UPPER_END = -0.6       # the top member runs into the rear bend of the lower member here
upper_pts = [Vector((UPPER_A[0] + (UPPER_END - UPPER_A[0]) * k / 30, upper_y(UPPER_A[0] + (UPPER_END - UPPER_A[0]) * k / 30), 0)) for k in range(31)]
# The lower member is one pressing per side (parts list 1938, plate 1 shows the bare frame): it drops almost
# vertically from the badge panel in front of the engine, turns through a rounded corner and runs back
# STRAIGHT and almost level under the engine and gearbox (about 0.23 m at the engine bolts, 0.26 m at the
# rear), then bends up in a tight U just in front of the rear axle and runs on into the top member. The axle
# sits in a lug on the back of that U. Heights from the parts-list side photo, the unrestored machine
# through a wheel-solved camera and the handbook side views; the steering head is tied to the badge panel
# by an unlined lug above it, not by a diagonal down tube
LOWER = [(0.262, 0.70), (0.259, 0.62), (0.256, 0.53), (0.258, 0.42), (0.26, 0.345), (0.252, 0.29), (0.23, 0.252), (0.19, 0.232),
         (0.12, 0.219), (0.0, 0.2246), (-0.15, 0.2328), (-0.3, 0.2410), (-0.45, 0.2492), (-0.57, 0.2567), (-0.615, 0.262),
         (-0.643, 0.278), (-0.658, 0.305), (-0.663, 0.34), (-0.663, 0.375), (-0.658, 0.4), (-0.645, 0.416), (-0.625, 0.425),
         (-0.6, upper_y(-0.6)), (-0.585, upper_y(-0.585))]
lower_pts = catmull([Vector((x, y, 0)) for x, y in LOWER], 10)
frame_objs = []
for side in (1,):
    z = side * FRAME_Z
    up = [V(p.x, p.y, z) for p in upper_pts]
    lo = [V(p.x, p.y, z) for p in lower_pts]
    frame_objs.append(sweep('frame.upper', up, PRESS, 'paint', ref=Vector((0, 1, 0)), sharp=50))
    frame_objs.append(sweep('frame.lower', lo, PRESS, 'paint', ref=Vector((0, 1, 0)), sharp=50))
    # badge panel and steering-head lug as one pressing: the panel is a teardrop below the top member,
    # narrowing into the front member; in front of it the unlined lug runs up to the steering head
    yc = upper_y
    GUSSET = [(0.12, yc(0.12)), (0.22, yc(0.22)), (0.30, yc(0.30)), (0.322, 0.802), (0.338, 0.785), (0.348, 0.762), (0.35, 0.742),
              (0.343, 0.724), (0.328, 0.708), (0.316, 0.69), (0.31, 0.672), (0.302, 0.648),
              (0.288, 0.615), (0.277, 0.585), (0.27, 0.555), (0.258, 0.53), (0.24, 0.555), (0.232, 0.58), (0.222, 0.612),
              (0.208, 0.64), (0.19, 0.662), (0.168, 0.677), (0.14, 0.687)]
    frame_objs.append(slab('frame.gusset', GUSSET, 0.04, z, 'paint', bevel=0.01))
    # rear axle plate joining both members
    # rear axle lug on the back of the U, a round boss round the axle (unrestored machine, parts list photo)
    frame_objs.append(slab('frame.axlelug', [(-0.648, 0.372), (-0.676, 0.366), (-0.703, 0.356), (-0.721, 0.338), (-0.722, 0.318),
                                            (-0.707, 0.301), (-0.682, 0.296), (-0.652, 0.298)], 0.016, z, 'paint', bevel=0.004, per=4))
    # curved strut each side from the top member down to the lower member behind the gearbox (plate 1)
    zs_ = z - side * 0.031             # on the inner faces of the members, just clear of the mudguard sides
    strut = catmull([Vector(p_) for p_ in [(-0.374, upper_y(-0.374) - 0.012, zs_), (-0.36, 0.45, zs_), (-0.352, 0.36, zs_), (-0.348, 0.29, zs_), (-0.345, 0.252, zs_)]], 8)
    frame_objs.append(sweep('frame.strut', [V(q.x, q.y, q.z) for q in strut], rrect_profile(0.032, 0.012, 0.005, 4), 'paint', ref=Vector((0, 1, 0)), sharp=50))
    # hand-drawn lines on the outer faces
    zf = z + side * 0.0172
    def lines_along(pts2d, offs, name, t0=0.02, t1=0.98):
        n = len(pts2d)
        i0, i1 = int(t0 * (n - 1)), int(t1 * (n - 1))
        for off in offs:
            P2, S2 = [], []
            for i in range(i0, i1 + 1):
                a, b = pts2d[max(i - 1, 0)], pts2d[min(i + 1, n - 1)]
                d = (b - a).normalized()
                nrm = Vector((-d.y, d.x, 0))
                P2.append((pts2d[i].x + nrm.x * off, pts2d[i].y + nrm.y * off, zf))
                S2.append((nrm.x, nrm.y, 0))
            frame_objs.append(ribbon(name, P2, S2, 0.003, 'stripe'))
    lines_along(upper_pts, (0.017, -0.017), 'frame.line.upper')
    # the front member's lines start where the badge panel's lines run into them
    i_start = next(i for i, p in enumerate(lower_pts) if p.y < 0.575)
    i_end = next(i for i, p in enumerate(lower_pts) if p.x < -0.24)
    lines_along(lower_pts, (0.017, -0.017), 'frame.line.lower', t0=i_start / (len(lower_pts) - 1), t1=i_end / (len(lower_pts) - 1))
    # double line round the badge panel: up the front edge, along under the top member, back down the
    # rear edge, open at the bottom where it becomes the front member's two lines
    GL = [(0.2735, 0.575), (0.279, 0.605), (0.289, 0.638), (0.298, 0.668), (0.301, 0.69), (0.297, yc(0.297) - 0.04),
          (0.283, yc(0.283) - 0.033), (0.24, yc(0.24) - 0.032), (0.19, yc(0.19) - 0.032), (0.165, yc(0.165) - 0.034),
          (0.174, 0.69), (0.2, 0.676), (0.222, 0.652), (0.234, 0.622), (0.2395, 0.592), (0.2405, 0.575)]
    g = catmull([Vector((x, y, 0)) for x, y in GL], 8)
    # lay the line on whichever pressing is under it (panel or member): ray from outside towards the frame
    _bm = bmesh.new()
    for o_ in frame_objs:
        _bm.from_mesh(o_.data)
    FR_BVH = BVHTree.FromBMesh(_bm)
    _bm.free()
    P2, S2 = [], []
    for i in range(len(g)):
        a, b = g[max(i - 1, 0)], g[min(i + 1, len(g) - 1)]
        d = (b - a).normalized()
        hit = FR_BVH.ray_cast(V(g[i].x, g[i].y, z + side * 0.2), V(0, 0, -side))
        zz = (-hit[0].y + side * 0.0009) if hit[0] is not None else z + side * 0.0208
        P2.append((g[i].x, g[i].y, zz))
        S2.append((-d.y, d.x, 0))
    frame_objs.append(ribbon('frame.line.gusset', P2, S2, 0.0028, 'stripe', double=0.003))
frame_objs += mirror(frame_objs)
# roundels are made per side (a mirrored copy would read backwards)
# enamel badge standing proud of the gusset on a backing plate, with a nickel rim (photos r03, r16)
# about 50 mm across (half the width of the fork cover at its top in the side photos), centred in the
# upper bulb of the panel
RB = (0.234, 0.69)
for side in (-1, 1):
    face = FRAME_Z + 0.02
    cyl('frame.badgeplate', (*RB, side * face), (*RB, side * (face + 0.0025)), 0.0235, 'black', seg=48)
    lathe('frame.badgerim', [(0.0215, 0.0), (0.025, 0.0), (0.025, 0.0014), (0.0234, 0.0032), (0.0215, 0.0026), (0.0215, 0.0)],
          (*RB, side * face), (0, 0, side), 'chrome', seg=64)
    disc_decal('frame.roundel', (*RB, side * (face + 0.0026)), (0, 0, side), 0.0215, 'roundel')
# steering head: the two frame halves wrap round the front of the head tube in a half circle and are tied
# behind it by pressed gusset angles riveted to their webs and flanges (German handbook p. 49-50, parts list
# 1938 plate 1): a pressed shroud, round at the front, opening back to the two side pressings
h0, h1 = steerpt(0.506), steerpt(0.63)
cyl('frame.head', (h0[0], h0[1], 0), (h1[0], h1[1], 0), 0.031, 'paint', seg=32)
hax = (Vector((*h1, 0)) - Vector((*h0, 0))).normalized()
hfw = Vector((hax.y, -hax.x, 0))                  # forward, square to the head axis in the side plane
zax_ = Vector((0, 0, 1))
def shroud_ring(c, rf=0.044, back=0.045, zb=0.07, n=40):
    pts = []
    for k in range(n + 1):                          # front half circle from the left side round to the right
        a = math.pi * k / n
        pts.append(c + hfw * (rf * math.sin(a)) - zax_ * (rf * math.cos(a)))
    pts.append(c - hfw * back * 0.5 + zax_ * (zb * 0.8))
    pts.append(c - hfw * back + zax_ * zb)
    pts.append(c - hfw * back - zax_ * zb)
    pts.append(c - hfw * back * 0.5 - zax_ * (zb * 0.8))
    return [tuple(q) for q in pts]
srings = []
for k in range(9):
    L = 0.512 + (0.62 - 0.512) * k / 8
    c = Vector((*steerpt(L), 0))
    srings.append(shroud_ring(c))
frame_objs_head = loft('frame.headshroud', srings, 'paint', subsurf=1, sharp=70)
for L, nm in ((0.506, 'bottom'), (0.63, 'top')):
    c = Vector((*steerpt(L), 0))
    lathe('frame.headcup', [(0.026, -0.005), (0.035, -0.005), (0.036, 0.0), (0.035, 0.005), (0.026, 0.005)], tuple(c), tuple(hax), 'steel', seg=32)
# the curved strut in front of the rear wheel is one pressing with its two cross pieces (German handbook p. 49)
rbox('frame.strutcross', (-0.346, 0.262, 0), (0.026, 0.016, 2 * FRAME_Z - 0.05), 0.005, 'paint')
for (x, y) in [(0.3, 0.775), (-0.15, 0.6), (-0.315, 0.2445), (0.25, 0.36)]:
    cyl('frame.cross', (x, y, -FRAME_Z), (x, y, FRAME_Z), 0.012, 'paint', seg=12)
# engine mounting plates
for z in (-FRAME_Z, FRAME_Z):
    rbox('frame.enginemount', (0.235, 0.27, z * 0.92), (0.06, 0.05, 0.01), 0.004, 'paint')


# footboards: cast aluminium boards on brackets from the lower loop. A raised field of transverse ribs on
# the outer two thirds of the width, a plain strip with two bolts along the inner edge and a plain front
# that ends under the cylinder axis, where the head overhangs it. Measured on the unrestored left side
# profile (photo c0h, head 170 mm as scale): tip at the cylinder axis, rear end 380 mm behind it, ribs from
# 90 to 375 mm behind it; the restored bike (p_engine, c3h) agrees. Ribs read as short upright strokes from
# the side (Fig. 1) and as cross stripes from above (Fig. 4).
FB_X0, FB_X1 = CYL_X - 0.33, CYL_X - 0.005
FB_DY = -0.01
for xb in (0.088, -0.185):
    cyl('frame.enginebolt', (xb, 0.232, -0.118), (xb, 0.232, 0.118), 0.0065, 'steel', seg=10)
for side in (-1, 1):
    zi, zo = 0.145, 0.255     # heads overhang the boards (Fig. 4)
    outline = [(FB_X0, zi), (FB_X0 - 0.002, 0.2), (FB_X0, zo), (FB_X0 + 0.2, zo + 0.001), (FB_X1 - 0.06, zo), (FB_X1 - 0.02, zo - 0.008),
               (FB_X1 - 0.002, zo - 0.035), (FB_X1, 0.19), (FB_X1 - 0.006, zi + 0.012), (FB_X1 - 0.03, zi + 0.001), (FB_X1 - 0.12, zi), (FB_X0 + 0.12, zi - 0.001)]
    plate('frame.footboard', [(x, side * z) for x, z in outline], 0.2 + FB_DY, 0.213 + FB_DY, 'alusatin', bevel=0.003, per=5)
    field = [(CYL_X - 0.325, 0.176), (CYL_X - 0.325, 0.246), (CYL_X - 0.06, 0.246), (CYL_X - 0.06, 0.176)]
    plate('frame.footboard.field', [(x, side * z) for x, z in field], 0.212 + FB_DY, 0.2155 + FB_DY, 'alusatin', bevel=0.0012, per=1)
    for k in range(24):
        x = CYL_X - 0.319 + k * 0.0108
        rbox('frame.footboard.rib', (x, 0.2175 + FB_DY, side * 0.211), (0.0046, 0.0045, 0.064), 0.0016, 'alusatin')
    # upturned inner flange of the casting, bolted to the ends of the engine bolts
    rbox('frame.footboard.flange', ((FB_X0 + FB_X1) / 2 - 0.01, 0.222, side * 0.142), (FB_X1 - FB_X0 - 0.05, 0.05, 0.007), 0.0025, 'alusatin')
    for xb in (0.088, -0.185):
        cyl('frame.footboard.nut', (xb, 0.232, side * 0.118), (xb, 0.232, side * 0.153), 0.011, 'steel', seg=6, sharp=30)
        cyl('frame.footboard.boltend', (xb, 0.232, side * 0.153), (xb, 0.232, side * 0.159), 0.0055, 'steel', seg=10)

# rear stand (Kippständer) after the parts list 1938, plate 5 no. 35: a pressed U whose bottom carries two lugs on
# a cross bolt (no. 34) under the lower frame members behind the footboards, the two legs folded back under the
# members, a treadle arm curling up on the right; a coil spring (no. 32) holds it up. Pivot after the parts list
# photo (two round lugs under the member ~0.3 m ahead of the rear axle)
part('stand', (-0.06, -0.12, 0), 'P.stand.rear')
SPV = (-0.30, 0.212)
SZ_ = 0.15
bow = [(SPV[0] + 0.004 - 0.012 * (1 - (k / 8) ** 2), SPV[1] - 0.008, SZ_ * k / 8) for k in range(-8, 9)]
tube('stand.bow', bow, 0.0085, 'paint', seg=8, per=2)
for s_ in (-1, 1):
    tube('stand.leg', [(SPV[0] + 0.004, SPV[1] - 0.008, s_ * SZ_), (SPV[0] - 0.04, SPV[1] - 0.002, s_ * SZ_), (SPV[0] - 0.1, SPV[1] + 0.004, s_ * SZ_),
                       (SPV[0] - 0.145, SPV[1] + 0.008, s_ * SZ_), (SPV[0] - 0.165, SPV[1] + 0.018, s_ * SZ_), (SPV[0] - 0.172, SPV[1] + 0.034, s_ * SZ_)],
         0.0085, 'paint', seg=8, per=6)
    rbox('stand.lug', (SPV[0], SPV[1], s_ * (SZ_ - 0.02)), (0.026, 0.026, 0.008), 0.004, 'paint')
cyl('stand.pivot', (SPV[0], SPV[1], -SZ_ + 0.01), (SPV[0], SPV[1], SZ_ - 0.01), 0.0055, 'steel', seg=8)
tube('stand.treadle', [(SPV[0] - 0.012, SPV[1] - 0.006, SZ_), (SPV[0] - 0.035, SPV[1] - 0.004, SZ_ + 0.02), (SPV[0] - 0.06, SPV[1] + 0.0, SZ_ + 0.027),
                       (SPV[0] - 0.072, SPV[1] + 0.016, SZ_ + 0.027)], 0.0065, 'paint', seg=8)
tube('stand.spring', [(SPV[0] - 0.06, SPV[1] + 0.0, SZ_ - 0.012), (SPV[0] - 0.035, SPV[1] + 0.02, SZ_ - 0.022), (SPV[0] - 0.012, SPV[1] + 0.036, SZ_ - 0.03)],
     0.0045, 'steel', seg=6, per=4)

# ==============================================================================================
# FORK, STEERING DAMPER, HANDLEBAR CONTROLS
# ==============================================================================================
part('fork', (0.24, 0.3, 0))
fork_objs = []
fx = lambda L: (*forkpt(L), FORK_Z)
fork_objs.append(cyl('fork.slider', fx(0.02), fx(0.3), 0.02, 'black', seg=24))
fork_objs.append(rbox('fork.clamp', (*forkpt(0.01), FORK_Z), (0.04, 0.1, 0.022), 0.008, 'black', rot=(math.degrees(RAKE),)))
fork_objs.append(cyl('fork.clampbolt', (*forkpt(-0.022), FORK_Z - 0.014), (*forkpt(-0.022), FORK_Z + 0.016), 0.006, 'steel', seg=6))
cfv = Vector((cR, sR, 0)); zax = Vector((0, 0, 1))
# spear-shaped pressed covers run from under the top yoke almost down to the axle (photos r09, r10,
# r16: ~8 cm wide at the top, ~3.5 cm at the rounded foot some 7 cm above the axle)
SPEAR_L0, SPEAR_L1 = 0.108, 0.635     # foot and triangle after the 1936 handbook (Fig. 1, 7)
SPEAR_E = 2.8                              # superellipse section: flat outer face like the pressing
def spear_half(L):
    t = max(0.0, (L - SPEAR_L0) / (SPEAR_L1 - SPEAR_L0))
    return 0.022 + 0.022 * t ** 0.8, 0.02 + 0.006 * t   # fore-aft, lateral semi-axes
def spear_ring(c, a_, b_, n=32):
    out = []
    for j in range(n):
        th = 2 * math.pi * j / n
        cx, sz = math.cos(th), math.sin(th)
        out.append(tuple(c + cfv * (a_ * math.copysign(abs(cx) ** (2 / SPEAR_E), cx)) + zax * (b_ * math.copysign(abs(sz) ** (2 / SPEAR_E), sz))))
    return out
cover_rings = []
for dl, sc in ((-0.0125, 0.12), (-0.011, 0.45), (-0.008, 0.75), (-0.004, 0.92)):
    a_, b_ = spear_half(SPEAR_L0)
    cover_rings.append(spear_ring(Vector((*forkpt(SPEAR_L0 + dl), FORK_Z)), a_ * sc, b_ * sc))
for k in range(24):
    L = SPEAR_L0 + (SPEAR_L1 - SPEAR_L0) * k / 23
    a_, b_ = spear_half(L)
    cover_rings.append(spear_ring(Vector((*forkpt(L), FORK_Z)), a_, b_))
fork_objs.append(loft('fork.cover', cover_rings, 'paint', subsurf=1))
# shock absorber oil inlet plug on top of each leg: a large hexagon nut on the top bridge with a small
# domed plug in its centre (Fig. 19, Fig. 1)
fork_objs.append(lathe('fork.cap', [(0.0, 0.0), (0.0232, 0.0), (0.0248, 0.0015), (0.0248, 0.0095), (0.0232, 0.011), (0.0, 0.011)],
                       fx(0.659), (-sR, cR, 0), 'darkmetal', seg=6, sharp=30))
fork_objs.append(lathe('fork.plug', [(0.0, 0.0105), (0.0118, 0.0105), (0.0112, 0.0142), (0.0078, 0.0172), (0.0, 0.0182)],
                       fx(0.659), (-sR, cR, 0), 'steel', seg=28))
# coachline pair round the spear near its edges, rounded at the foot, lying on the curved face
up = Vector((-sR, cR, 0))
def on_cover(L, x):
    """Point on the outer face of the cover at fore-aft offset x, with the face normal."""
    a_, b_ = spear_half(L)
    x = max(-a_ * 0.999, min(a_ * 0.999, x))
    zz = b_ * (1 - abs(x / a_) ** SPEAR_E) ** (1 / SPEAR_E)
    n = (cfv * (math.copysign(abs(x) ** (SPEAR_E - 1), x) / a_ ** SPEAR_E) + zax * (zz ** (SPEAR_E - 1) / b_ ** SPEAR_E)).normalized()
    p = Vector((*forkpt(L), FORK_Z)) + cfv * x + zax * zz
    return p + n * 0.0012, n
FL0, FL1, EDGE = 0.128, 0.596, 0.87
loop = []
for k in range(25):                       # rear edge up
    L = FL0 + (FL1 - FL0) * k / 24
    loop.append((L, -spear_half(L)[0] * EDGE))
for k in range(1, 8):                     # across under the yoke
    L = FL1
    a_ = spear_half(L)[0] * EDGE
    loop.append((L, -a_ + 2 * a_ * k / 8))
for k in range(25):                       # front edge down
    L = FL1 - (FL1 - FL0) * k / 24
    loop.append((L, spear_half(L)[0] * EDGE))
a_b = spear_half(FL0)[0] * EDGE
for k in range(1, 12):                    # rounded foot
    th = math.pi * k / 12
    loop.append((FL0 - a_b * 0.9 * math.sin(th), a_b * math.cos(th)))
loop.append(loop[0])
P3 = [on_cover(L, x) for L, x in loop]
LP, LS = [], []
for i in range(len(P3)):
    a, b = P3[max(i - 1, 0)][0], P3[min(i + 1, len(P3) - 1)][0]
    d = (b - a).normalized()
    LP.append(tuple(P3[i][0]))
    LS.append(tuple(d.cross(P3[i][1]).normalized()))
fork_objs.append(ribbon('fork.line', LP, LS, 0.0028, 'stripe', double=0.003))
# inverted triangle outline on the slider below the spear foot (Fig. 1, Fig. 7)
cf = Vector((cR, sR, 0))
SL_R = 0.02
t0, t1 = Vector((*forkpt(0.042), 0)), Vector((*forkpt(0.092), 0))
tri = [t1 + cf * 0.012, t1 - cf * 0.012, t0, t1 + cf * 0.012]
TP, TS = [], []
for i in range(3):
    a, b = tri[i], tri[i + 1]
    d = (b - a).normalized()
    for k in range(7):
        q = a.lerp(b, k / 6)
        off = (q - Vector((*forkpt(((q - Vector((XF, AY, 0))).dot(Vector((-sR, cR, 0))))), 0))).length
        zz = math.sqrt(max(0.0, (SL_R + 0.0011) ** 2 - off ** 2))
        TP.append((q.x, q.y, FORK_Z + zz))
        TS.append((-d.y, d.x, 0))
fork_objs.append(ribbon('fork.triangle', TP, TS, 0.0024, 'stripe'))
# joint where the upper cover meets the sliding lower cover (photo r09)
a_j, b_j = spear_half(0.46)
fork_objs.append(loft('fork.joint', [spear_ring(Vector((*forkpt(0.458), FORK_Z)), a_j * 1.012, b_j * 1.03),
                                     spear_ring(Vector((*forkpt(0.462), FORK_Z)), a_j * 1.012, b_j * 1.03)], 'black', subsurf=0))
fork_objs += mirror(fork_objs)
# lower bridge hidden inside the covers, top bridge sitting on top of them
for L in (0.48, 0.645):
    (ax, ay), (sx, sy) = forkpt(L), steerpt(L)
    # cast fork bridges shaped like a bone: a round boss over each leg, a boss round the steering stem
    # and a web between them (top bridge seen from above in Fig. 19)
    ax_ = Vector((-sR, cR, 0))
    hb = 0.014 if L > 0.5 else 0.012
    for zz in (-FORK_Z, FORK_Z):
        c = Vector((ax, ay, zz))
        cyl('fork.yoke', tuple(c - ax_ * hb), tuple(c + ax_ * hb), 0.031 if L > 0.5 else 0.02, 'black', seg=32)
    c = Vector((sx, sy, 0))
    cyl('fork.yoke', tuple(c - ax_ * hb), tuple(c + ax_ * hb), 0.03, 'black', seg=32)
    rbox('fork.yoke', ((ax + sx) / 2 - 0.004, (ay + sy) / 2, 0), (0.07 if L > 0.5 else 0.045, 2 * hb - 0.004, 2 * FORK_Z), 0.008, 'black', rot=(math.degrees(RAKE),))
s0, s1 = steerpt(0.465), steerpt(0.674)
cyl('fork.stem', (s0[0], s0[1], 0), (s1[0], s1[1], 0), 0.012, 'steel', seg=12)
# mudguard stays to the sliders
for s in (-1, 1):
    for (a, L) in ((100, 0.22), (165, 0.06)):
        r = 0.35 + f_rmod((a - F_A0) / (F_A1 - F_A0)) if 'f_rmod' in globals() else 0.35
        p = (XF + r * math.cos(math.radians(a)), AY + r * math.sin(math.radians(a)), s * 0.068)
        tube('fork.stay', [p, (*forkpt(L), s * FORK_Z)], 0.0055, 'paint', seg=8)

part('steeringdamper', (0.2, 0.72, 0))
k0, k1 = steerpt(0.672), steerpt(0.69)
# damper screw on top of the steering stem: a plated wing knob, round hub with two flat wings out to the
# sides, about 75 mm across (Fig. 19, photo of the 1940 machine)
kax = (Vector((*k1, 0)) - Vector((*k0, 0))).normalized()
lathe('steeringdamper.knob', [(0.0, 0.0), (0.013, 0.0), (0.013, 0.012), (0.0112, 0.0172), (0.006, 0.0205), (0.0, 0.021)],
      (k0[0], k0[1], 0), tuple(kax), 'steel', seg=28)
rbox('steeringdamper.wing', tuple(Vector((*k0, 0)) + kax * 0.011), (0.0075, 0.02, 0.078), 0.0065, 'steel',
     rot=(math.degrees(math.atan2(-kax.x, kax.y)),))
# friction damper at the bottom of the steering head, between the lower bridge and the head (German handbook p. 49)
d0, d1 = steerpt(0.494), steerpt(0.503)
cyl('steeringdamper.disc', (d0[0], d0[1], 0), (d1[0], d1[1], 0), 0.034, 'black', seg=32)
dm = Vector((*steerpt(0.498), 0))
tube('steeringdamper.arm', [(dm.x - 0.02, dm.y - 0.012, 0.025), (dm.x - 0.05, dm.y - 0.02, 0.05), (dm.x - 0.07, dm.y - 0.022, 0.07)], 0.006, 'steel', seg=8)

# handlebar: straight across the middle to about 250 mm either side, a short bend, then the grips swept
# back at about 40 degrees, ends 140 mm behind the straight (top view Fig. 4, scaled on the 900 mm overall
# width from the fact sheet); front brake lever right, clutch left
# front view (German handbook Abb. 31 through a camera solved on the cylinder heads): the bar is almost level,
# the grips only ~1.5 cm above the lamp centre, the ends ~0.86 m apart
HB_R = [(0.319, 0.882, 0), (0.319, 0.883, 0.088), (0.316, 0.884, 0.166), (0.308, 0.885, 0.219), (0.291, 0.887, 0.254),
        (0.264, 0.889, 0.282), (0.23, 0.89, 0.311), (0.194, 0.886, 0.349), (0.158, 0.881, 0.388)]
HB = [(x, y, -z) for x, y, z in reversed(HB_R[1:])] + HB_R
GRIP_A, GRIP_B = Vector((0.23, 0.89, 0.311)), Vector((0.158, 0.881, 0.388))
def grip_frame(side):
    a, b = Vector((GRIP_A.x, GRIP_A.y, side * GRIP_A.z)), Vector((GRIP_B.x, GRIP_B.y, side * GRIP_B.z))
    d = (b - a).normalized()
    n = Vector((-d.z, 0, d.x)) * side          # horizontal, ahead of the grip
    if n.x < 0:
        n = -n
    return a, b, d, n.normalized()
part('handlebar', (0.12, 0.58, 0))
tube('handlebar.bar', HB, 0.011, 'chrome', seg=16, per=10)
rbox('handlebar.clamp', (0.319, 0.872, 0), (0.04, 0.03, 0.08), 0.008, 'black')
UPV = Vector((0, 1, 0))
for s in (-1, 1):
    # the 1930s pattern: lever pivot lug on a chrome cone at the bar end, the lever curving back inwards
    # over the grip with its tip turned up (Fig. 3 right, Fig. 5 left)
    a, b, d, n = grip_frame(s)
    lathe('handlebar.endcap', [(0.0, 0.0), (0.0195, 0.0), (0.0195, 0.012), (0.018, 0.024), (0.013, 0.038), (0.007, 0.046), (0.0, 0.048)],
          tuple(b + d * 0.006), tuple(d), 'chrome', seg=28)
    piv = b + d * 0.026 + n * 0.017 + UPV * 0.004
    rbox('handlebar.leverpivot', tuple(piv), (0.022, 0.016, 0.02), 0.005, 'chrome', rot=(0, math.degrees(math.atan2(d.x, d.z))))
    cyl('handlebar.leverpin', tuple(piv - UPV * 0.011), tuple(piv + UPV * 0.011), 0.0042, 'steel', seg=10)
    lev = [piv + n * 0.006, b - d * 0.01 + n * 0.03 + UPV * 0.01, b - d * 0.055 + n * 0.036 + UPV * 0.012,
           b - d * 0.1 + n * 0.034 + UPV * 0.014, b - d * 0.128 + n * 0.028 + UPV * 0.022, b - d * 0.138 + n * 0.022 + UPV * 0.034]
    tube('handlebar.lever', [tuple(q) for q in lev], 0.0055, 'chrome', seg=10)

def grip(pid, side, explode, extra=None):
    part(pid, explode)
    a, b, d, n = grip_frame(side)
    a2 = a + d * 0.012
    cyl(f'{pid}.collar', tuple(a), tuple(a + d * 0.016), 0.0205, 'chrome', seg=24)
    cyl(f'{pid}.grip', tuple(a2), tuple(b + d * 0.008), 0.017, 'rubber', seg=24)
    for k in range(9):
        q = a2 + (b - a2) * (0.08 + 0.1 * k)
        lathe(f'{pid}.rib', [(0.0172, -0.002), (0.0185, 0), (0.0172, 0.002)], tuple(q), tuple(d), 'rubber', seg=20)
    if extra:
        extra()

grip('throttle', 1, (0.12, 0.58, 0.24), lambda: (
    tube('throttle.cable', [(0.238, 0.89, 0.3), (0.29, 0.86, 0.235), (0.335, 0.78, 0.16), (0.33, 0.68, 0.145), (0.25, 0.62, 0.145), (0.17, 0.6, 0.13), (0.1, 0.59, 0.07), (0.0, 0.585, 0.03), (-0.07, 0.582, 0.02), (-0.14, 0.572, 0)], 0.003, 'black', seg=6)))
# head lamp dimmer switch: round housing clamped on the bar inboard of the throttle grip, dimmer lever
# below it and the horn button beside (Fig. 3)
a_, b_, d_, n_ = grip_frame(1)
DC = a_ - d_ * 0.03 + UPV * 0.012 - n_ * 0.004
DAX = (Vector((-0.55, 0.84, 0.0)) - d_ * 0.0).normalized()
part('throttle', (0.12, 0.58, 0.24), 'P.throttle.dimmer')
cyl('throttle.dimmerclamp', tuple(a_ - d_ * 0.045), tuple(a_ - d_ * 0.016), 0.0135, 'black', seg=20)
lathe('throttle.dimmer', [(0.0, -0.009), (0.021, -0.009), (0.023, -0.004), (0.023, 0.006), (0.02, 0.01), (0.0, 0.011)], tuple(DC), tuple(DAX), 'black', seg=36)
cyl('throttle.dimmerscrew', tuple(DC + DAX * 0.01), tuple(DC + DAX * 0.014), 0.0045, 'chrome', seg=12)
tube('throttle.dimmerlever', [tuple(DC - UPV * 0.018 + n_ * 0.004), tuple(DC - UPV * 0.032 + n_ * 0.012 + d_ * 0.006), tuple(DC - UPV * 0.042 + n_ * 0.02 + d_ * 0.014)], 0.0035, 'chrome', seg=8)
part('horn', (0.12, 0.58, 0.3), 'P.horn.button')
cyl('horn.button', tuple(DC - UPV * 0.02 + d_ * 0.018), tuple(DC - UPV * 0.028 + d_ * 0.018), 0.0062, 'chrome', seg=14)
grip('advance', -1, (0.12, 0.58, -0.24), lambda: (
    tube('advance.cable', [(0.238, 0.89, -0.3), (0.29, 0.86, -0.235), (0.335, 0.78, -0.16), (0.33, 0.68, -0.145), (0.25, 0.62, -0.145), (0.17, 0.6, -0.13), (0.08, 0.6, -0.06), (-0.01, 0.6, 0.0), (-0.045, 0.57, 0.04), (-0.052, 0.497, 0.05)], 0.003, 'black', seg=6)))

part('killbutton', (0.12, 0.64, -0.12))
a_, b_, d_, n_ = grip_frame(-1)
KB = a_ - d_ * 0.05
cyl('killbutton.body', tuple(KB - d_ * 0.012), tuple(KB + d_ * 0.012), 0.0145, 'black', seg=20)
cyl('killbutton.button', tuple(KB + UPV * 0.012), tuple(KB + UPV * 0.021), 0.0065, 'chrome', seg=16)

# ==============================================================================================
# MUDGUARDS, NUMBER PLATES, TAIL LAMP
# ==============================================================================================
def guard(name, cx, cy, a0, a1, prof, segs=96, flare=None, rmod=None, zscale=None, inner=None):
    bm = bmesh.new()
    rings = []
    for i in range(segs + 1):
        t = i / segs
        a = math.radians(a0 + (a1 - a0) * t)
        k = (flare(t) if flare else 0)
        dr = rmod(t) if rmod else 0.0
        zs = zscale(t) if zscale else 1.0
        ring = []
        di = inner(t) if inner else 0.0
        for (r, z) in prof:
            rr = r + dr + (k if r > prof[0][0] + 0.01 else k * 0.5)
            if r < prof[0][0] + 0.001:
                rr += di          # valance edge: deeper skirts over the tyre side
            ring.append(bm.verts.new(V(cx + rr * math.cos(a), cy + rr * math.sin(a), z * zs)))
        rings.append(ring)
    P = len(prof)
    for i in range(segs):
        for j in range(P - 1):
            bm.faces.new((rings[i][j], rings[i][j + 1], rings[i + 1][j + 1], rings[i + 1][j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = finish(bm, name, 'paint', sharp=70)
    so = o.modifiers.new('thick', 'SOLIDIFY')
    so.thickness = 0.0025
    so.offset = 1
    return o

def guard_line(name, cx, cy, r, z, a0, a1, width=0.0028, segs=90, rmod=None, g0=None, g1=None, double=0.0, zmod=None):
    pts, sides = [], []
    for i in range(segs + 1):
        a = math.radians(a0 + (a1 - a0) * i / segs)
        tt = (math.degrees(a) - g0) / (g1 - g0) if g0 is not None else 0.0
        rr = r + (rmod(tt) if rmod else 0.0)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a), z * (zmod(tt) if zmod else 1.0)))
        sides.append((math.cos(a), math.sin(a), 0))
    return ribbon(name, pts, sides, width, 'stripe', double=double)

part('fenders', (0.6, 0.26, 0), 'P.fenders.front')
FPROF = [(0.345, -0.071), (0.415, -0.071), (0.432, -0.06), (0.442, -0.03), (0.445, 0), (0.442, 0.03), (0.432, 0.06), (0.415, 0.071), (0.345, 0.071)]
F_A0, F_A1 = 58.0, 210.0
def f_rmod(t):
    # t 0 = front tip (58 deg) .. 1 = rear beak (210 deg): 0.42 at the tip, 0.445 over the top, 0.39 at the beak
    a = F_A0 + (F_A1 - F_A0) * t
    if a < 85:
        return -0.025 * (85 - a) / 27
    if a > 125:
        return -0.055 * min(1, (a - 125) / 77)
    return 0.0
def f_zscale(t):
    # the rear beak flares out like a spoon below the end of the coachline (photo r10, Fig. 1)
    a = F_A0 + (F_A1 - F_A0) * t
    q = min(1.0, max(0.0, (a - 192) / 18))
    return 1 + 0.34 * q * q * (3 - 2 * q)
def f_inner(t):
    a = F_A0 + (F_A1 - F_A0) * t
    q = min(1.0, max(0.0, (a - 98) / 52))
    return -0.068 * q * q * (3 - 2 * q)
guard('fenders.front', XF, AY, F_A0, F_A1, FPROF, rmod=f_rmod, zscale=f_zscale, inner=f_inner)
# coachline pair along the lower edge of each valance (photos r10, r16, Commons NIK 4083)
for z in (-0.0738, 0.0738):
    guard_line('fenders.front.line', XF, AY, 0.3555, z, 60, 193, 0.003, rmod=lambda t: f_rmod(t) + f_inner(t), g0=F_A0, g1=F_A1, double=0.003)
# front number plate: a curved strip standing on the mudguard crown and following its arc, figures
# on both faces (pre-1945 German motorcycle front plate, cf. the Munich IIA-83356 in the Deutsches
# Museum); the texture is the strip laid straight, so u runs along the arc and the figures bend with it
# handbook Fig. 1 on a 2 cm grid: from ~0.11 m behind the axle round to ~0.18 m ahead of it, 70 mm high,
# sitting on two short posts just clear of the mudguard and following its crown, which falls away towards
# the front, so the lower edge closes in on the axle from the rear end to the front end
PA0, PA1 = 103.0, 66.0        # rear end and front end, degrees round the front axle
PR0, PRD, PH, PCR = 0.453, -0.016, 0.07, 0.011   # inner radius at the rear end, its change to the front end, height, corner radius
PLEN = math.radians(PA0 - PA1) * (PR0 + PRD / 2 + PH / 2)

def plate_xy(s, t):
    a = math.radians(PA0 + (PA1 - PA0) * s)
    r = PR0 + PRD * s + PH * t
    return (XF + r * math.cos(a), AY + r * math.sin(a))

def plate_t(s):
    """Usable t range at s, trimmed by the rounded corners."""
    dd = min(s, 1 - s) * PLEN
    if dd >= PCR:
        return 0.0, 1.0
    off = PCR - math.sqrt(max(0.0, PCR * PCR - (PCR - dd) ** 2))
    return off / PH, 1 - off / PH

c_ = PCR / PLEN
PS = [c_ * (1 - math.cos(math.pi / 2 * k / 8)) for k in range(8)] + [c_ + (1 - 2 * c_) * k / 48 for k in range(49)]
PS += [1 - v for v in reversed(PS[:8])]

def plate_strip(name, z, side):
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new()
    NT = 4
    rows = []
    for sv in PS:
        lo, hi = plate_t(sv)
        rows.append([(sv, lo + (hi - lo) * k / NT) for k in range(NT + 1)])
    verts = [[bm.verts.new(V(*plate_xy(sv, tv), z)) for sv, tv in row] for row in rows]
    for i in range(len(rows) - 1):
        for k in range(NT):
            quad = [(i, k), (i + 1, k), (i + 1, k + 1), (i, k + 1)]
            f = bm.faces.new([verts[a][b] for a, b in quad])
            if f.normal.dot(V(0, 0, side)) < 0:
                f.normal_flip()
            for loop in f.loops:
                for a, b in quad:
                    if verts[a][b] is loop.vert:
                        sv, tv = rows[a][b]
                        loop[uvl].uv = (sv if side > 0 else 1 - sv, tv)
    return finish(bm, name, 'plate_front', smooth=False)

plate_strip('fenders.plate.r', 0.0026, 1)
plate_strip('fenders.plate.l', -0.0026, -1)
PL = [plate_xy(sv, plate_t(sv)[0]) for sv in PS] + [plate_xy(sv, plate_t(sv)[1]) for sv in reversed(PS)]
slab('fenders.plate.edge', PL, 0.0048, 0, 'black', per=1, smooth_outline=False)
for ang in (97, 72.5):
    a = math.radians(ang)
    r0 = PR0 + PRD * (ang - PA0) / (PA1 - PA0)
    tube('fenders.plate.bracket', [(XF + (r0 + 0.004) * math.cos(a), AY + (r0 + 0.004) * math.sin(a), 0), (XF + (0.44 + f_rmod((ang - F_A0) / (F_A1 - F_A0))) * math.cos(a), AY + (0.44 + f_rmod((ang - F_A0) / (F_A1 - F_A0))) * math.sin(a), 0)], 0.005, 'paint', seg=8)

part('fenders', (-0.45, 0.28, 0), 'P.fenders.rear')
# the front end comes down in front of the tyre to just above the lower frame member, the tail ends below the
# axle (parts list photo, Fig. 1, unrestored machine)
R_A0, R_A1 = -9.0, 204.0
RPROF = [(0.318, -0.077), (0.36, -0.077), (0.374, -0.065), (0.383, -0.032), (0.386, 0), (0.383, 0.032), (0.374, 0.065), (0.36, 0.077), (0.318, 0.077)]
def r_zscale(t):
    # the tail ends in the same outward spoon as the front beak (photos r03, r09, Fig. 1); the front end, where
    # it comes down between the two arms of the curved frame strut, is narrower
    a = R_A0 + (R_A1 - R_A0) * t
    q = min(1.0, max(0.0, (a - 190) / 14))
    f = min(1.0, max(0.0, (55 - a) / 20))
    return (1 + 0.32 * q * q * (3 - 2 * q)) * (1 - 0.24 * f * f * (3 - 2 * f))
def r_rmod(t):
    a = R_A0 + (R_A1 - R_A0) * t
    q = min(1.0, max(0.0, (a - 192) / 12))
    return 0.026 * q * q
def r_inner(t):
    a = R_A0 + (R_A1 - R_A0) * t
    q = min(1.0, max(0.0, (a - 118) / 50))
    return -0.04 * q * q * (3 - 2 * q)
guard('fenders.rear', XR, AY, R_A0, R_A1, RPROF, zscale=r_zscale, rmod=r_rmod, inner=r_inner)
for z in (-0.08, 0.08):
    guard_line('fenders.rear.line', XR, AY, 0.3285, z, -6, 192, 0.003, rmod=lambda t: r_rmod(t) + r_inner(t), g0=R_A0, g1=R_A1, double=0.003, zmod=r_zscale)
# hinge of the lift-up tail section: two plated knuckles on the crown (photo of the 1940 machine, Fig. 25)
for zk in (-0.022, 0.022):
    lathe('fenders.rear.hinge', [(0.0, -0.012), (0.0055, -0.012), (0.0055, 0.012), (0.0, 0.012)], (XR + 0.391 * math.cos(math.radians(150)), AY + 0.391 * math.sin(math.radians(150)), zk), (0, 0, 1), 'chrome', seg=14)
for s in (-1, 1):
    for ang in (160, 192):
        r = 0.32
        p = (XR + r * math.cos(math.radians(ang)), AY + r * math.sin(math.radians(ang)), s * 0.08)
        tube('fenders.rear.stay', [p, (-0.688, 0.37, s * 0.1) if s < 0 else ((XR - 0.012, AY + 0.109, 0.104) if ang < 180 else (XR - 0.112, AY - 0.004, 0.1))], 0.0058, 'paint', seg=8)

part('taillight', (-0.55, 0.3, 0))
ta = math.radians(146)
tlx, tly = XR + 0.42 * math.cos(ta), AY + 0.42 * math.sin(ta)
# teardrop lamp body pointing back, small red lens at the tail
# long bullet body tapering forwards, lens in a chrome ring at the rear end (photo of the 1940 machine, Fig. 1)
TLO, TLA = (tlx - 0.012, tly + 0.016, 0), (-1, 0.12, 0)
lathe('taillight.body', [(0.0, -0.062), (0.006, -0.06), (0.013, -0.052), (0.019, -0.038), (0.023, -0.02), (0.0245, 0.0), (0.0245, 0.016), (0.0, 0.016)], TLO, TLA, 'paint', seg=32)
lathe('taillight.ring', [(0.0175, 0.014), (0.025, 0.014), (0.025, 0.02), (0.0215, 0.024), (0.0175, 0.022)], TLO, TLA, 'chrome', seg=32)
lathe('taillight.lens', [(0.0, 0.016), (0.019, 0.016), (0.018, 0.024), (0.012, 0.029), (0.0, 0.031)], TLO, TLA, 'redlens', seg=32)
rbox('taillight.foot', (tlx + 0.004, tly - 0.006, 0), (0.035, 0.016, 0.03), 0.005, 'paint', rot=(-56,))
# plate at the tail of the mudguard just under the lamp, held off it on two spacers
pa_ = math.radians(165)
pc = Vector((XR + 0.418 * math.cos(pa_), AY + 0.418 * math.sin(pa_), 0))
pup = Vector((math.sin(pa_), -math.cos(pa_), 0))   # up along the plate
pout = Vector((math.cos(pa_), math.sin(pa_), 0))
# rear plate: two lines, top corners clipped (pre-1945 German motorcycle rear plate)
RW_, RH_, RCH_ = 0.19, 0.125, 0.034
ZW = Vector((0, 0, 1))
r_out = [(-RW_ / 2, -RH_ / 2), (RW_ / 2, -RH_ / 2), (RW_ / 2, RH_ / 2 - RCH_), (RW_ / 2 - RCH_, RH_ / 2),
         (-RW_ / 2 + RCH_, RH_ / 2), (-RW_ / 2, RH_ / 2 - RCH_)]
def rear_pt(w, h, lift):
    return pc + pup * h + ZW * w + pout * lift
bm = bmesh.new()
uvl = bm.loops.layers.uv.new()
f = bm.faces.new([bm.verts.new(V(*rear_pt(w, h, 0.004))) for w, h in r_out])
if f.normal.dot(V(*pout)) < 0:
    f.normal_flip()
for loop in f.loops:
    for w, h in r_out:
        if (loop.vert.co - V(*rear_pt(w, h, 0.004))).length < 1e-7:
            loop[uvl].uv = (w / RW_ + 0.5, h / RH_ + 0.5)
finish(bm, 'taillight.plate', 'plate_rear', smooth=False)
# black backing plate the enamel sits on
bm = bmesh.new()
f = bm.faces.new([bm.verts.new(V(*rear_pt(w * 1.03, h * 1.03, 0.0035))) for w, h in r_out])
if f.normal.dot(V(*pout)) < 0:
    f.normal_flip()
ext = bmesh.ops.extrude_face_region(bm, geom=[f])
bmesh.ops.translate(bm, vec=V(*(-pout * 0.004)), verts=[e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)])
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
finish(bm, 'taillight.plate.back', 'black', smooth=False)
for zz in (-0.055, 0.055):
    a0 = pc + ZW * zz
    cyl('taillight.plate.spacer', tuple(a0), tuple(a0 - pout * 0.032), 0.006, 'paint', seg=10)
tube('taillight.cable', [(tlx + 0.01, tly - 0.01, 0.02), (XR + 0.38 * math.cos(math.radians(130)), AY + 0.38 * math.sin(math.radians(130)), 0.05)], 0.003, 'rubber', seg=6)

# ==============================================================================================
# TANK, KNEE GRIPS, SADDLE, CARRIER
# ==============================================================================================
part('tank', (0, 0.42, 0))
# stations: x, top y, bottom y, half width
# Side profile from the three period side views (handbook Fig. 1, German Abb. 2, parts list 1938 photo), measured
# on a 1 cm grid as height above the top frame member and scaled by the member slope (the figures are flattened
# to ~0.79 in height): nearly level over the cap, then the top runs on as one smooth, almost straight plane down
# under the saddle and lands flat on the top member at x -0.205, a thin wide tail and no cut-off end. From above
# (Abb. 6, parts list plate 8, no. 24) the tank keeps its full width right back under the saddle, the tail is
# broad with rounded corners and carries the two rear mounting lugs over the frame members (plate 8 list: one
# screw in front, two at the rear). Pressed shallow recess in the tail under the saddle nose, where the nose
# stay lies (plate 8; not visible in front of the saddle in Abb. 6).
# About 14 litres, 0.3 m wide.
TANK = [
    (0.287, 0.79, 0.775, 0.042),
    (0.278, 0.812, 0.77, 0.094),
    (0.26, 0.823, 0.763, 0.124),
    (0.22, 0.828, 0.742, 0.142),
    (0.15, 0.829, 0.702, 0.149),
    (0.08, 0.826, 0.667, 0.15),
    (0.04, 0.818, 0.652, 0.15),
    (0.0, 0.799, 0.638, 0.15),
    (-0.04, 0.775, 0.628, 0.15),
    (-0.08, 0.748, 0.619, 0.149),
    (-0.12, 0.719, 0.617, 0.147),
    (-0.16, 0.687, 0.615, 0.143),
    (-0.18, 0.664, 0.611, 0.139),
    (-0.195, 0.643, 0.606, 0.134),
    (-0.201, 0.632, 0.606, 0.124),
    (-0.205, 0.622, 0.606, 0.106),
    (-0.207, 0.615, 0.607, 0.078),
]
NR = 96
E_TOP, E_BOT = 2.8, 3.0
REC_HW, REC_X = 0.05, (-0.142, -0.15, -0.188, -0.196)
def tank_ring(x, top, bot, hw):
    pts = []
    h = top - bot
    a0, a1, b1, b0 = REC_X
    dep = 0.0
    if b0 < x < a0:
        dep = min(1.0, (a0 - x) / (a0 - a1), (x - b0) / (b1 - b0))
    for k in range(NR):
        a = 2 * math.pi * k / NR
        c, sn = math.cos(a), math.sin(a)
        e = E_TOP if sn > 0 else E_BOT
        zz = hw * math.copysign(abs(c) ** (2 / e), c)
        yy = bot + h * 0.42 + h * (0.58 if sn > 0 else 0.42) * math.copysign(abs(sn) ** (2 / e), sn)
        if sn > 0 and dep > 0:
            m = min(1.0, max(0.0, (REC_HW + 0.006 - abs(zz)) / 0.012))
            m = m * m * (3 - 2 * m)
            fl = top - 0.01 * dep
            if yy > fl:
                yy -= (yy - fl) * m
        pts.append((x, yy, zz))
    return pts
def tank_z(st, yy):
    x, top, bot, hw = st
    h = top - bot
    base = bot + h * 0.42
    if yy >= base:
        q, e = min(1.0, (yy - base) / (h * 0.58)), E_TOP
    else:
        q, e = min(1.0, (base - yy) / (h * 0.42)), E_BOT
    return hw * max(0.0, 1 - q ** e) ** (1 / e)
# smooth the station table along x before lofting
ST = []
cols = list(zip(*TANK))
curves = [catmull([Vector((i, v, 0)) for i, v in enumerate(col)], 6) for col in cols]
for k in range(len(curves[0])):
    ST.append(tuple(c[k].y for c in curves))
tank_obj = loft('tank.shell', [tank_ring(*st) for st in ST], 'paint', subsurf=0, sharp=89)
# the two rear lugs at the corners of the tail, bolted down onto the top members (plate 8, nos. 17, 13-15)
for s_ in (-1, 1):
    ly = upper_y(-0.212) + 0.026
    rbox('tank.lug', (-0.212, ly, s_ * 0.09), (0.02, 0.003, 0.022), 0.0012, 'paint')
    cyl('tank.lug.bolt', (-0.214, ly + 0.0015, s_ * 0.09), (-0.214, ly + 0.0065, s_ * 0.09), 0.0045, 'steel', seg=6, sharp=30)
def st_at(x):
    """Tank station (x, top, bottom, half width) interpolated at x."""
    xs = [st[0] for st in ST]
    for i in range(len(ST) - 1):
        a, b = ST[i], ST[i + 1]
        if (a[0] - x) * (b[0] - x) <= 0:
            t = 0 if a[0] == b[0] else (x - a[0]) / (b[0] - a[0])
            return tuple(a[j] + (b[j] - a[j]) * t for j in range(4))
    return ST[0] if x > xs[0] else ST[-1]
from mathutils.bvhtree import BVHTree
_tbm = bmesh.new(); _tbm.from_mesh(tank_obj.data); _tbm.transform(tank_obj.matrix_world)
TANK_BVH = BVHTree.FromBMesh(_tbm)
def tank_snap(p_bike):
    """Nearest point on the tank shell (bike space) and its outward normal, lifted 1.2 mm."""
    loc, nrm, _i, _d = TANK_BVH.find_nearest(V(*p_bike))
    pb = Vector((loc.x, loc.z, -loc.y))
    nb = Vector((nrm.x, nrm.z, -nrm.y)).normalized()
    return pb + nb * 0.0012, nb
def tank_pt(x, yy, side):
    return Vector((x, yy, side * tank_z(st_at(x), yy)))
# the line in side projection: crosses the nose at x 0.352, ~25 mm under the crown along the side, then runs
# parallel to the top edge down the tail, closing in on it as the tail thins (Fig. 1, Abb. 2, parts list photo)
TL_SIDE = [(0.272, -0.022), (0.24, -0.024), (0.2, -0.025), (0.1, -0.026), (0.04, -0.027), (0.0, -0.027), (-0.04, -0.026),
           (-0.08, -0.025), (-0.12, -0.022), (-0.16, -0.018), (-0.185, -0.014), (-0.197, -0.012)]
for side in (-1, 1):
    pts = []
    x0 = TL_SIDE[0][0]
    top0 = st_at(x0)[1]
    for k in range(8):                                   # over the crown at the nose
        yy = top0 - 0.0005 - (0.026 - 0.0005) * (1 - math.cos(math.pi / 2 * k / 7))
        pts.append(tank_pt(x0, yy, side))
    side_pts = catmull([Vector((x, st_at(x)[1] + d, 0)) for x, d in TL_SIDE], 8)
    for q in side_pts[1:]:
        pts.append(tank_pt(q.x, q.y, side))
    snapped = [tank_snap(q) for q in pts]
    P3, S3 = [], []
    for i in range(len(snapped)):
        a, b = snapped[max(i - 1, 0)][0], snapped[min(i + 1, len(snapped) - 1)][0]
        tng = (b - a).normalized()
        P3.append(tuple(snapped[i][0]))
        S3.append(tuple(tng.cross(snapped[i][1]).normalized()))
    ribbon('tank.line', P3, S3, 0.003, 'stripe', double=0.003)
TCY = tank_snap(Vector((0.09, 0.9, 0.0)))[0].y - 0.004
lathe('tank.cap', [(0.0, 0.0), (0.04, 0.0), (0.041, 0.004), (0.039, 0.011), (0.034, 0.016), (0.0, 0.017)], (0.09, TCY, 0), (0, 1, 0), 'chrome', seg=48)
lathe('tank.cap.dome', [(0.0, 0.0), (0.028, 0.0), (0.026, 0.006), (0.018, 0.011), (0.0, 0.013)], (0.09, TCY + 0.016, 0), (0, 1, 0), 'chrome', seg=40)
rbox('tank.cap.lever', (0.065, TCY + 0.022, 0), (0.028, 0.005, 0.012), 0.0025, 'chrome', rot=(-12,))
cyl('tank.tap', (-0.02, 0.665, -0.05), (-0.02, 0.625, -0.05), 0.008, 'brass', seg=12)
cyl('tank.tap.lever', (-0.02, 0.635, -0.05), (-0.02, 0.635, -0.085), 0.004, 'brass', seg=8)
# BMW knee grips: oval rubber pads with a knurled face and raised BMW, the right one carries the gear gate
KX, KY, KA, KRX, KRY = -0.03, 0.664, math.radians(18), 0.072, 0.042
def kpt(lx, ly):
    return (KX + lx * math.cos(KA) - ly * math.sin(KA), KY + lx * math.sin(KA) + ly * math.cos(KA))
KZ = tank_z(st_at(KX), KY) + 0.005
# Both pads are thick rubber cushions standing ~25 mm proud of the tank. The right one is the gear gate: its
# front end is a chrome segment with the two fore-aft slots (top/second above, third/first below, neutral
# between), and the lever comes up from the gearbox UNDER the rubber, runs inside the pad and leaves through
# the gate (handbook Fig. 6; "Kniekissen rechts mit Schaltsegment", parts list 1938 plate 1; 1940 machine).
KT, KB = 0.03, 0.008          # pad thickness and edge rounding
KG = 0.03                     # the chrome gate covers the pad ahead of this local x
ga = math.degrees(math.acos(KG / KRX))
def knee(side, gate=False):
    zz = side * (KZ + 0.012)
    nm = 'gearlever.gate' if gate else 'tank.kneegrip'
    if gate:
        pts = [kpt(KRX * math.cos(math.radians(d)), KRY * math.sin(math.radians(d))) for d in range(int(ga), 360 - int(ga) + 1, 4)]
        pts += [kpt(KG, -KRY * math.sin(math.radians(ga))), kpt(KG, KRY * math.sin(math.radians(ga)))]
        slab(nm, pts, KT, zz, 'rubber', bevel=KB, per=1, smooth_outline=False)
    else:
        pts = [kpt(KRX * math.cos(2 * math.pi * k / 48), KRY * math.sin(2 * math.pi * k / 48)) for k in range(48)]
        slab(nm, pts, KT, zz, 'rubber', bevel=KB, per=1, smooth_outline=False)
    zf = zz + side * (KT / 2 + 0.0003)
    x0, x1 = -KRX + 0.008, (0.045 if gate else KRX - 0.008)
    lx = (x0, x1) if side > 0 else (x1, x0)
    ky = KRY - 0.008
    corners = [(*kpt(lx[0], -ky), zf), (*kpt(lx[1], -ky), zf), (*kpt(lx[1], ky), zf), (*kpt(lx[0], ky), zf)]
    quad_decal(nm + '.face', corners, 'kneepad')
    for (dx, dy) in ((0.05, 0.026), (-0.055, -0.024)) if not gate else ((-0.055, -0.024),):
        x, y = kpt(dx, dy)
        cyl(nm + '.screw', (x, y, zz + side * (KT / 2 - 0.002)), (x, y, zz + side * (KT / 2 + 0.0025)), 0.0055, 'chrome', seg=12)
knee(-1)

part('gearlever', (0.02, 0.32, 0.26))
knee(1, gate=True)
# chrome gate segment forming the front end of the right pad, its face flush with the rubber (Fig. 6)
gate_pts = [kpt(KRX * math.cos(math.radians(d)), KRY * math.sin(math.radians(d))) for d in range(-int(ga), int(ga) + 1, 4)]
gate_pts += [kpt(KG, KRY * math.sin(math.radians(ga))), kpt(KG, -KRY * math.sin(math.radians(ga)))]
GZ = KZ + 0.012
slab('gearlever.gateplate', gate_pts, KT + 0.002, GZ, 'alu', bevel=0.009, per=1, smooth_outline=False)
GO = GZ + (KT + 0.002) / 2              # outer face of the gate
for (a, b) in (((0.04, 0.016), (0.066, 0.016)), ((0.04, -0.016), (0.066, -0.016)), ((0.052, -0.016), (0.052, 0.016))):
    (x0, y0), (x1, y1) = kpt(*a), kpt(*b)
    cx_, cy_ = (x0 + x1) / 2, (y0 + y1) / 2
    ln = math.hypot(x1 - x0, y1 - y0) + 0.006
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    rbox('gearlever.slot', (cx_, cy_, GO + 0.0003), (ln, 0.0062, 0.002), 0.0028, 'black', rot=(ang,))
# the lever: straight up out of the lever cover on top of the gearbox, curving forwards and out, in under the lower
# edge of the pad, inside the pad to the
# gate, out through the neutral slot and on forwards and upwards to the black ball knob (Fig. 6; knob centre
# x 0.095, y 0.73 on a 1 cm grid in Fig. 1)
gx, gy = kpt(0.052, 0.0)
KN = Vector((0.0933, 0.7313, KZ + 0.049))
kd = (KN - Vector((gx + 0.024, gy + 0.018, KZ + 0.036))).normalized()
lever = [(-0.138, 0.476, 0.078), (-0.135, 0.52, 0.088), (-0.117, 0.56, 0.108), (-0.088, 0.592, 0.132), (-0.058, 0.612, KZ - 0.002),
         (-0.03, 0.632, KZ + 0.004), (gx - 0.016, gy - 0.014, KZ + 0.008), (gx, gy, GO - 0.004), (gx + 0.008, gy + 0.006, GO + 0.006),
         (gx + 0.024, gy + 0.018, KZ + 0.036), tuple(KN - kd * 0.03), tuple(KN - kd * 0.014)]
tube('gearlever.lever', lever, 0.0068, 'chrome', seg=12)
cyl('gearlever.ferrule', tuple(KN - kd * 0.022), tuple(KN - kd * 0.015), 0.0085, 'chrome', seg=14)
bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=14, radius=0.0175); bmesh.ops.translate(bm, verts=bm.verts, vec=V(*KN)); finish(bm, 'gearlever.knob', 'black')

part('saddle', (-0.12, 0.4, 0))
# Pagusa sprung saddle: a pressed pan covered in leather, deep side skirts with a row of rivets near
# their lower edge, a dished seat, a narrow nose turned slightly up and a raised rolled rear edge
# (parts list 1938 photo, unrestored machine, 1940 machine). Lowest point of the seat at 0.71 m
# (handbook: saddle height 0.70 m).
SAD_DY = -0.045
#        x      half width  seat top  skirt bottom
SADS = [(-0.148, 0.018, 0.738, 0.716), (-0.158, 0.032, 0.735, 0.706), (-0.18, 0.054, 0.729, 0.694), (-0.215, 0.082, 0.721, 0.68),
        (-0.26, 0.112, 0.715, 0.668), (-0.31, 0.138, 0.711, 0.66), (-0.36, 0.156, 0.713, 0.658), (-0.4, 0.164, 0.721, 0.66),
        (-0.43, 0.163, 0.734, 0.668), (-0.449, 0.152, 0.747, 0.68), (-0.461, 0.13, 0.754, 0.694), (-0.468, 0.094, 0.754, 0.708),
        (-0.472, 0.052, 0.751, 0.72)]
def saddle_ring(x, hw, top, bot, n=36):
    """Inverted U: skirts nearly upright, rounded shoulders, a seat dished across; closed underneath."""
    pts = []
    sh = min(0.022, 0.45 * hw)                     # shoulder radius
    for k in range(n):
        t = k / (n - 1)                            # 0 = left skirt bottom ... 1 = right skirt bottom
        u = 2 * t - 1                              # -1..1 across
        side = -1 if u < 0 else 1
        a = abs(u)
        if a > 0.78:                               # skirt: from the bottom up to the shoulder, flared out a little
            q = (a - 0.78) / 0.22                  # 1 at the bottom
            zz = side * (hw + 0.004 * q)
            yy = (top - sh) - q * (top - sh - bot)
        elif a > 0.55:                             # shoulder arc
            q = (a - 0.55) / 0.23                  # 0 at the top, 1 at the skirt
            ang = q * math.pi / 2
            zz = side * (hw - sh + sh * math.sin(ang))
            yy = top - sh + sh * math.cos(ang)
        else:                                      # seat, dished 6 mm in the middle
            q = a / 0.55
            zz = side * (hw - sh) * q
            yy = top - 0.006 * (1 - q * q)
        pts.append((x, yy, zz))
    # underside: a flat pan a little inside the skirts
    for k in range(1, 6):
        zz = (hw - 0.008) * (1 - 2 * k / 6)
        pts.append((x, bot + 0.012, zz))
    return pts
loft('saddle.pan', [saddle_ring(*st) for st in SADS], 'leather', subsurf=1, sharp=70)
# rivets along the skirts, 10 mm above the lower edge, about 28 mm apart (unrestored machine)
def sad_at(x):
    for a_, b_ in zip(SADS, SADS[1:]):
        if b_[0] <= x <= a_[0]:
            t = (x - a_[0]) / (b_[0] - a_[0])
            return tuple(a_[j] + (b_[j] - a_[j]) * t for j in range(4))
    return SADS[-1]
for k in range(11):
    x = -0.19 - k * 0.0265
    _x, hw, top, bot = sad_at(x)
    for s_ in (-1, 1):
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=7, radius=0.0055)
        bmesh.ops.scale(bm, vec=(1, 1, 0.5), verts=bm.verts)
        bmesh.ops.translate(bm, verts=bm.verts, vec=V(x, bot + 0.01, s_ * (hw + 0.0046)))
        finish(bm, 'saddle.rivet', 'steel')
# embossed maker's oval on each skirt, towards the front
for s_ in (-1, 1):
    x0 = -0.26
    hw0 = 0.112
    pts = [(x0 + 0.022 * math.cos(2 * math.pi * k / 24), 0.692 + 0.011 * math.sin(2 * math.pi * k / 24)) for k in range(24)]
    slab('saddle.badge', pts, 0.0016, s_ * (hw0 + 0.0042), 'leather', per=1, smooth_outline=False)
# rear suspension of the Pagusa saddle (parts list 1938, plate 2): one plain rod on each side drops straight
# down from the rear corner of the pan, through a lug on top of the top frame member and into a coil spring
# hooked under that lug, nut at the bottom; spring and rod sit just outboard of the member, so in the side
# views the coils overlap the member (handbook Fig. 1, German Abb. 2, unrestored machine, 1940 machine)
SPX = -0.385
SPZ = 0.137
sp_top = upper_y(SPX) + 0.018
for s in (-1, 1):
    zz = s * SPZ
    # lug on top of the member, reaching out over the spring
    slab('saddle.springlug', [(SPX - 0.028, sp_top - 0.004), (SPX + 0.028, sp_top - 0.004 + 0.01), (SPX + 0.006, sp_top + 0.022), (SPX - 0.012, sp_top + 0.019)],
         0.006, s * (FRAME_Z + 0.012), 'paint', bevel=0.0015, per=1, smooth_outline=False)
    rbox('saddle.springlug', (SPX, sp_top + 0.006, s * 0.124), (0.03, 0.005, 0.04), 0.002, 'paint')
    pts = []
    NT = 11
    for i in range(NT * 16 + 1):
        t = i / (NT * 16)
        a = t * NT * 2 * math.pi
        pts.append(V(SPX + 0.016 * math.cos(a), sp_top - 0.004 - 0.082 * t, zz + 0.016 * math.sin(a)))
    sweep('saddle.spring', pts, circle_profile(0.0028, 6), 'paint', caps=True, sharp=80)
    tube('saddle.springhook', [(SPX + 0.016, sp_top - 0.004, zz), (SPX + 0.017, sp_top + 0.006, zz), (SPX + 0.008, sp_top + 0.009, zz)], 0.0028, 'paint', seg=6)
    cyl('saddle.springnut', (SPX, sp_top - 0.094, zz), (SPX, sp_top - 0.086, zz), 0.0075, 'steel', seg=6, sharp=30)
    cyl('saddle.springrod', (SPX, sp_top - 0.1, zz), (SPX, 0.664, zz), 0.0048, 'steel', seg=10)
# nose stay: a curved strap from under the saddle nose, down over the tail of the tank to a cross bracket
# between the top members just behind it (curved line under the saddle nose in Fig. 1, Abb. 2, parts list photo)
tube('saddle.nose', [(-0.152, 0.709, 0), (-0.16, 0.697, 0), (-0.168, 0.682, 0), (-0.183, 0.662, 0), (-0.198, 0.65, 0),
                     (-0.211, 0.631, 0), (-0.22, upper_y(-0.22) + 0.026, 0)], 0.0055, 'paint', seg=10)
rbox('saddle.nosebracket', (-0.222, upper_y(-0.222) + 0.02, 0), (0.03, 0.012, 0.21), 0.004, 'paint')
# luggage carrier over the rear mudguard: one bent tube frame with rounded corners and two cross
# bars (three openings, Fig. 4), black like the frame; a stay from each rear corner down to the
# axle plate and the front ends bent down to the frame (Fig. 1, Fig. 4)
RK_X0, RK_X1, RK_HW, RK_R, RK_Y = -0.53, -0.825, 0.086, 0.028, 0.724
def rack_y(x):
    return RK_Y + 0.006 * math.sin(math.pi * (x - RK_X0) / (RK_X1 - RK_X0))
loop = []
# walk round: front-left corner, rear-left, rear-right, front-right (angles in the x/z plane)
for (cx, cz, a0, a1) in [(RK_X0 - RK_R, -RK_HW + RK_R, 0, 90), (RK_X1 + RK_R, -RK_HW + RK_R, 90, 180),
                         (RK_X1 + RK_R, RK_HW - RK_R, 180, 270), (RK_X0 - RK_R, RK_HW - RK_R, 270, 360)]:
    for k in range(6):
        a = math.radians(a0 + (a1 - a0) * k / 6)
        x, z = cx + RK_R * math.cos(a), cz - RK_R * math.sin(a)
        loop.append(V(x, rack_y(x), z))
sweep('saddle.rack.frame', loop, circle_profile(0.0075, 10), 'paint', ref=Vector((0, 0, 1)), closed_path=True, sharp=60)
for x in (RK_X0 + (RK_X1 - RK_X0) / 3, RK_X0 + 2 * (RK_X1 - RK_X0) / 3):
    cyl('saddle.rack.bar', (x, rack_y(x), -RK_HW), (x, rack_y(x), RK_HW), 0.0065, 'paint', seg=10)
for s in (-1, 1):
    tube('saddle.rack.front', [(RK_X0 - 0.01, rack_y(RK_X0), s * RK_HW), (-0.49, 0.67, s * 0.092), (-0.475, 0.6, s * 0.098),
                               (-0.47, upper_y(-0.47) + 0.02, s * 0.1)], 0.0075, 'paint', seg=8)
    # on the right the stay bolts to a lug on top of the rear drive housing (Bielefeld 2018, 1940 machine)
    tube('saddle.rack.rear', [(RK_X1 + 0.02, rack_y(RK_X1), s * RK_HW), (RK_X1 + 0.03, 0.62, s * 0.1), (-0.69, 0.395 if s < 0 else AY + 0.112, s * 0.1)], 0.0075, 'paint', seg=8)

# ==============================================================================================
# ENGINE
# ==============================================================================================
part('crankcase', (0.1, 0, 0))
# crankcase casting, front-view section after Fig. 20: rounded sump below, flat cylinder mounting faces,
# shoulders narrowing to the magneto platform on top; ends slightly drawn in so the edges read as cast
CC_HALF = [(0.196, 0.0), (0.196, 0.044), (0.202, 0.06), (0.216, 0.07), (0.24, 0.075), (0.27, 0.077), (0.29, 0.08), (0.304, 0.095), (0.322, 0.104),
           (0.35, 0.107), (0.40, 0.106), (0.428, 0.1), (0.448, 0.084), (0.461, 0.062), (0.468, 0.05), (0.471, 0.03), (0.471, 0.0)]
CC_LOOP = CC_HALF + [(y, -z) for (y, z) in reversed(CC_HALF[1:-1])]
CC_PTS = catmull([Vector((y, z, 0)) for y, z in CC_LOOP], 3, closed=True)
def cc_ring(x, k):
    cy = 0.335
    return [(x, cy + (p.x - cy) * k, p.y * k) for p in CC_PTS]
CC_ST = [(-0.075, 0.94), (-0.072, 0.975), (-0.067, 0.995), (-0.06, 1.0), (0.0, 1.0), (0.1, 1.0), (0.18, 1.0), (0.19, 0.99), (0.196, 0.97), (0.2, 0.935)]
loft('crankcase.body', [cc_ring(x, k) for x, k in CC_ST], 'cast', subsurf=1, sharp=60)
lathe('crankcase.timingcover', [(0, 0.2), (0.09, 0.2), (0.096, 0.21), (0.092, 0.226), (0.06, 0.236), (0, 0.238)], (0, 0.35, 0), (1, 0, 0), 'cast', seg=48)
rbox('crankcase.chaincase', (0.181, 0.505, 0), (0.05, 0.17, 0.09), 0.024, 'cast')
for k in range(3):
    rbox('crankcase.sumprib', (0.055, 0.197, -0.016 + k * 0.016), (0.15, 0.02, 0.007), 0.003, 'cast')
cyl('crankcase.drainplug', (0.06, 0.19, 0), (0.06, 0.175, 0), 0.012, 'steel', seg=6, sharp=30)
# lug for the front engine bolt, which passes through both lower frame members and carries the footboards
cyl('crankcase.mountboss', (0.088, 0.262, -0.083), (0.088, 0.262, 0.083), 0.017, 'cast', seg=20)
# engine oil inlet on the left of the case behind the cylinder, knurled cap on the dipstick (Fig. 20, text p. 14: dipstick on the left of the housing)
cyl('crankcase.filler', (-0.045, 0.405, -0.07), (-0.045, 0.41, -0.1), 0.013, 'cast', seg=20)
lathe('crankcase.fillercap', [(0.0, 0.0), (0.019, 0.0), (0.0205, 0.003), (0.019, 0.006), (0.0205, 0.009), (0.019, 0.012), (0.016, 0.015), (0.0, 0.016)],
      (-0.045, 0.41, -0.098), (0, 0.17, -1), 'cast', seg=40)
cyl('crankcase.breather', (-0.03, 0.462, 0.02), (-0.03, 0.488, 0.02), 0.01, 'cast', seg=12)

# side-valve cylinder: a black cast-iron block whose fins are rounded rectangles (the valve chamber
# sits beside the bore, under the chest on top), and an aluminium head shaped like a pillow, its
# horizontal ribs following the dome round to the flange (photos r04, Commons NIK 4083, r09)
# the head covers the bore and the valve chamber above it, so its centre sits 24 mm above the bore
# axis (Fig. 1 at 1 px = 1 mm: head spans y 0.293..0.454); square-ish top corners, rounder bottom
HEAD_A, HEAD_B, HEAD_P = 0.085, 0.08, 3.2      # half width (x), half height (y), superellipse exponent
HEAD_PT, HEAD_PB = 3.8, 2.7                    # exponents above / below the centre line
HEAD_YC = CYL_Y + 0.024
HEAD_Z0, HEAD_H = 0.262, 0.032                 # back face on the block, dome height
def se_pt(t, a, b, p=None):
    c, s_ = math.cos(t), math.sin(t)
    if p is None:
        p = HEAD_PT if s_ > 0 else HEAD_PB
    return a * math.copysign(abs(c) ** (2 / p), c), b * math.copysign(abs(s_) ** (2 / p), s_)
def head_n(dx, dy):
    p = HEAD_PT if dy > 0 else HEAD_PB
    return (abs(dx / HEAD_A) ** p + abs(dy / HEAD_B) ** p) ** (1 / p)
def head_z(dx, dy):
    n = min(1.0, head_n(dx, dy))
    return HEAD_Z0 + 0.008 + HEAD_H * max(0.0, 1 - n ** 2.5) ** 0.6
PLUG_BASE = Vector((CYL_X - 0.004, HEAD_YC + 0.06, head_z(-0.004, 0.06) - 0.002))
PLUG_DIR = Vector((-0.03, 0.82, 0.57)).normalized()

def head_shell(name):
    bm = bmesh.new()
    NT, NR = 72, 14
    rings = []
    for i in range(1, NR + 1):
        n = i / NR
        ring = []
        for k in range(NT):
            dx, dy = se_pt(2 * math.pi * k / NT, HEAD_A * n, HEAD_B * n)
            ring.append(bm.verts.new(V(CYL_X + dx, HEAD_YC + dy, head_z(dx, dy) if i < NR else HEAD_Z0 + 0.008)))
        rings.append(ring)
    back = []
    for k in range(NT):
        dx, dy = se_pt(2 * math.pi * k / NT, HEAD_A, HEAD_B)
        back.append(bm.verts.new(V(CYL_X + dx, HEAD_YC + dy, HEAD_Z0)))
    top = bm.verts.new(V(CYL_X, HEAD_YC, head_z(0, 0)))
    bc = bm.verts.new(V(CYL_X, HEAD_YC, HEAD_Z0))
    for k in range(NT):
        k2 = (k + 1) % NT
        bm.faces.new((top, rings[0][k], rings[0][k2]))
        for i in range(NR - 1):
            bm.faces.new((rings[i][k], rings[i + 1][k], rings[i + 1][k2], rings[i][k2]))
        bm.faces.new((rings[-1][k], back[k], back[k2], rings[-1][k2]))
        bm.faces.new((bc, back[k2], back[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finish(bm, name, 'alusatin', sharp=50)

def head_rib(name, dy):
    """One horizontal rib lying on the dome, running down the sides to the flange."""
    p = HEAD_PT if dy > 0 else HEAD_PB
    xm = HEAD_A * max(0.0, 1 - abs(dy / HEAD_B) ** p) ** (1 / p) * 0.975
    # cast fin: wide root, tapering to a rounded tip
    prof = [(-0.0034, -0.003), (0.0034, -0.003), (0.0026, 0.0048), (0.0013, 0.0072), (-0.0013, 0.0072), (-0.0026, 0.0048)]
    bm = bmesh.new()
    secs = []
    N = 28
    for i in range(N + 1):
        dx = -xm + 2 * xm * i / N
        zs = head_z(dx, dy)
        secs.append([bm.verts.new(V(CYL_X + dx, HEAD_YC + dy + py, zs + pz)) for py, pz in prof])
    m = len(prof)
    for i in range(N):
        A, B = secs[i], secs[i + 1]
        for j in range(m):
            bm.faces.new((A[j], A[(j + 1) % m], B[(j + 1) % m], B[j]))
    bm.faces.new(list(reversed(secs[0])))
    bm.faces.new(secs[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finish(bm, name, 'alusatin', sharp=50)

def cylinder_side():
    objs = []
    # block core and its fins (rounded rectangles round bore and valve chamber)
    objs.append(rbox('cylinders.block', (CYL_X, CYL_Y + 0.02, 0.18), (0.118, 0.16, 0.164), 0.02, 'darkmetal'))
    fin = [se_pt(2 * math.pi * k / 48, 0.08, 0.087, 3.0) for k in range(48)]
    fin = [(CYL_X + x, CYL_Y + 0.02 + y) for x, y in fin]
    for k in range(11):
        objs.append(slab('cylinders.fin', fin, 0.004, 0.118 + k * 0.0129, 'darkmetal', smooth_outline=False, sharp=60))
    # base flange on the crankcase
    objs.append(rbox('cylinders.flange', (CYL_X, CYL_Y, 0.105), (0.136, 0.136, 0.012), 0.022, 'darkmetal'))
    # side-valve chest on top with its cover, ports at front (exhaust) and rear (inlet)
    objs.append(rbox('cylinders.valvechest', (CYL_X - 0.01, 0.437, 0.185), (0.125, 0.036, 0.1), 0.015, 'cast'))
    # valve chamber cover 31, polished, held by the single head screw 32 (Fig. 20, p. 21)
    objs.append(rbox('cylinders.valvecover', (CYL_X - 0.01, 0.4585, 0.185), (0.1, 0.01, 0.078), 0.012, 'alu', seg=4))
    objs.append(cyl('cylinders.coverscrew', (CYL_X - 0.01, 0.462, 0.185), (CYL_X - 0.01, 0.472, 0.185), 0.008, 'steel', seg=6, sharp=30))
    objs.append(cyl('cylinders.coverscrew', (CYL_X - 0.01, 0.472, 0.185), (CYL_X - 0.01, 0.478, 0.185), 0.0045, 'steel', seg=12))
    # base flange nuts
    for (dx, dy) in ((-0.052, -0.052), (0.052, -0.052), (-0.052, 0.052), (0.052, 0.052)):
        objs.append(cyl('cylinders.basenut', (CYL_X + dx, CYL_Y + dy, 0.106), (CYL_X + dx, CYL_Y + dy, 0.116), 0.0065, 'steel', seg=6, sharp=30))
    # exhaust port boss on the front of the valve chest, standing just proud of the fins (photo Wilster 2018)
    objs.append(rbox('cylinders.exhaustport', (CYL_X + 0.066, 0.432, 0.2), (0.04, 0.044, 0.05), 0.008, 'cast'))
    # inlet port on the REAR face of the cylinder at valve-chamber level, below the chest itself: a round boss
    # through the fins and a two-eared flange with one stud above and one below the pipe (1940 machine from both
    # sides, unrestored machine, Fig. 20 shows the matching exhaust port on the front face)
    IP = (CYL_X - 0.09, 0.40, 0.19)
    objs.append(cyl('cylinders.inletport', (CYL_X - 0.05, IP[1], IP[2]), (IP[0] + 0.006, IP[1], IP[2]), 0.021, 'cast', seg=24))
    objs.append(cyl('cylinders.inletflange', (IP[0] + 0.006, IP[1], IP[2]), (IP[0] - 0.003, IP[1], IP[2]), 0.023, 'cast', seg=28))
    objs.append(rbox('cylinders.inletflange', (IP[0] + 0.0015, IP[1], IP[2]), (0.009, 0.076, 0.022), 0.009, 'cast'))
    for dy in (-0.029, 0.029):
        objs.append(cyl('cylinders.inletbolt', (IP[0] - 0.003, IP[1] + dy, IP[2]), (IP[0] - 0.009, IP[1] + dy, IP[2]), 0.0055, 'steel', seg=6, sharp=30))
    # pillow head: dome, eleven ribs, smooth band on top for the plug boss
    objs.append(head_shell('cylinders.head'))
    for k in range(11):
        objs.append(head_rib('cylinders.headrib', -0.067 + k * 0.0112))
    objs.append(cyl('cylinders.plugboss', tuple(PLUG_BASE - PLUG_DIR * 0.012), tuple(PLUG_BASE + PLUG_DIR * 0.004), 0.016, 'alusatin', seg=24))
    return objs

part('cylinders', (0, 0, 0.34), 'P.cylinders.right')
cr = cylinder_side()
part('cylinders', (0, 0, -0.34), 'P.cylinders.left')
mirror(cr)

def plug_side():
    o = []
    base = PLUG_BASE + PLUG_DIR * 0.004
    d = PLUG_DIR
    o.append(cyl('sparkplugs.hex', tuple(base), tuple(base + d * 0.016), 0.012, 'steel', seg=6, sharp=30))
    o.append(cyl('sparkplugs.insulator', tuple(base + d * 0.016), tuple(base + d * 0.05), 0.0085, 'porcelain', seg=16, r2=0.007))
    p0, p1 = base + d * 0.045, base + d * 0.07
    o.append(tube('sparkplugs.cap', [tuple(p0), tuple(p1), tuple(p1 + Vector((-0.012, 0.012, -0.004))), tuple(p1 + Vector((-0.03, 0.016, -0.012)))], 0.0105, 'black', seg=16, per=6))
    return o
part('sparkplugs', (0, 0.14, 0.42), 'P.sparkplugs.right')
pr = plug_side()
part('sparkplugs', (0, 0.14, -0.42), 'P.sparkplugs.left')
mirror(pr)

# lighting and ignition magneto (single-carburettor R 12): a horizontal cylinder resting in a cradle on
# the crankcase platform and held by a steel tightening band (Fig. 20, text p. 37, photo Wilster 2018).
# Chain drive at the front under a domed cover; breaker, regulator and dynamo end at the rear.
part('ignition', (0.16, 0.32, 0))
MX0, MX1, MY, MRAD = -0.028, 0.15, 0.57, 0.044
cyl('ignition.body', (0.03, MY, 0), (MX1, MY, 0), MRAD, 'cast', seg=48)
rbox('ignition.cradle', ((MX0 + MX1) / 2, 0.5, 0), (MX1 - MX0 - 0.01, 0.06, 0.07), 0.01, 'cast')
lathe('ignition.frontcover', [(0.0, 0.0), (MRAD + 0.002, 0.0), (MRAD + 0.002, 0.006), (0.04, 0.014), (0.03, 0.021), (0.0, 0.024)],
      (MX1, MY, 0), (1, 0, 0), 'cast', seg=48)
# tightening band over the middle, down to lugs bolted to the platform
BX = 0.07
band = [(BX, 0.48, -0.047), (BX, 0.52, -0.047), (BX, 0.56, -0.047)]
for k in range(1, 12):
    a = math.pi - math.pi * k / 12
    band.append((BX, MY + (MRAD + 0.0025) * math.sin(a), (MRAD + 0.0025) * math.cos(a)))
band += [(BX, 0.56, 0.047), (BX, 0.52, 0.047), (BX, 0.48, 0.047)]
tube('ignition.band', band, 0.0035, 'chrome', seg=10)
for zs in (-1, 1):
    rbox('ignition.lug', (BX, 0.476, zs * 0.052), (0.026, 0.014, 0.014), 0.003, 'cast')
    cyl('ignition.lugbolt', (BX, 0.476, zs * 0.06), (BX, 0.476, zs * 0.066), 0.0045, 'steel', seg=6)
# high-tension outlets on top at the front, one elbow cap per cylinder
for zs in (-1, 1):
    cyl('ignition.httower', (0.128, MY + 0.03, zs * 0.016), (0.128, MY + 0.05, zs * 0.03), 0.009, 'black', seg=14)
# flap lubricators (oil runs in at one and out at the other, p. 15)
for xl in (0.045, 0.115):
    cyl('ignition.lubricator', (xl, MY + MRAD - 0.003, 0.0), (xl, MY + MRAD + 0.008, 0.0), 0.0055, 'brass', seg=10)
for s in (-1, 1):
    base = PLUG_BASE + PLUG_DIR * 0.079
    tube('ignition.htlead', [(0.128, MY + 0.05, s * 0.03), (0.13, MY + 0.055, s * 0.07), (0.16, 0.56, s * 0.15), (0.14, 0.52, s * 0.21), (base.x - 0.02, base.y + 0.012, s * (base.z - 0.016))], 0.0045, 'rubber', seg=8)

# dynamo end of the same unit: rear section, black end cap with the breaker, regulator box on the side
part('generator', (-0.14, 0.44, 0))
cyl('generator.body', (MX0, MY, 0), (0.03, MY, 0), MRAD, 'cast', seg=48)
lathe('generator.endcover', [(0.0, 0.0), (MRAD + 0.001, 0.0), (MRAD + 0.001, -0.006), (0.04, -0.016), (0.0, -0.019)], (MX0, MY, 0), (1, 0, 0), 'black', seg=48)
rbox('generator.regulator', (0.0, MY + 0.012, 0.045), (0.042, 0.036, 0.016), 0.005, 'black')
for dx in (-0.012, 0.012):
    cyl('generator.regscrew', (dx, MY + 0.024, 0.053), (dx, MY + 0.024, 0.056), 0.0028, 'brass', seg=8)
tube('ignition.advancearm', [(MX0 - 0.016, MY - 0.012, 0.03), (MX0 - 0.02, MY - 0.03, 0.045), (MX0 - 0.024, MY - 0.045, 0.05)], 0.0042, 'steel', seg=8)
tube('generator.lead', [(0.0, MY + 0.03, 0.05), (-0.03, MY + 0.05, 0.06), (-0.13, 0.55, -0.08)], 0.0028, 'rubber', seg=6)

# single SUM carburettor behind the magneto, float chamber on the left, air filter to the rear
part('carburettor', (-0.08, 0.36, 0))
# sits over the front of the gearbox, behind the magneto, about 0.23 m behind the cylinder head centre and
# just above the gearbox top (parts list 1938 photo; unrestored machine through the wheel-solved camera)
CX, CY = -0.14, 0.50
# SUM carburettor after Fig. 14: mixing body with the throttle-slide tower (1, 9, 10) and its cable
# adjuster on top, the float chamber (2) as a separate cylinder on the left with the tickler and the fuel
# union (19) on its lid, the starting piston (20-22) as a horizontal barrel with the push button 22,
# mounting flange with four screws (18) to the intake T, air horn to the rear into the filter
rbox('carburettor.body', (CX, CY, 0), (0.062, 0.05, 0.05), 0.012, 'cast')
cyl('carburettor.slidebody', (CX, CY + 0.02, 0), (CX, CY + 0.07, 0), 0.0215, 'cast', seg=32)
lathe('carburettor.slidecap', [(0.0, 0.0), (0.0235, 0.0), (0.0235, 0.006), (0.02, 0.011), (0.009, 0.013), (0.0, 0.013)], (CX, CY + 0.07, 0), (0, 1, 0), 'cast', seg=32)
cyl('carburettor.cableadj', (CX, CY + 0.083, 0), (CX, CY + 0.099, 0), 0.0052, 'steel', seg=6, sharp=30)
cyl('carburettor.cablenut', (CX, CY + 0.087, 0), (CX, CY + 0.092, 0), 0.0075, 'steel', seg=6, sharp=30)
for dz in (-0.022, 0.022):
    for dy in (-0.017, 0.017):
        cyl('carburettor.flangescrew', (CX + 0.032, CY + dy, dz), (CX + 0.037, CY + dy, dz), 0.0034, 'steel', seg=8)
rbox('carburettor.flange', (CX + 0.034, CY, 0), (0.006, 0.052, 0.058), 0.004, 'cast')
cyl('carburettor.float', (CX - 0.004, CY - 0.034, -0.05), (CX - 0.004, CY + 0.012, -0.05), 0.024, 'cast', seg=32)
lathe('carburettor.floatcap', [(0.0, 0.0), (0.0255, 0.0), (0.0255, 0.007), (0.02, 0.01), (0.0, 0.01)], (CX - 0.004, CY + 0.012, -0.05), (0, 1, 0), 'cast', seg=32)
cyl('carburettor.tickler', (CX - 0.004, CY + 0.022, -0.05), (CX - 0.004, CY + 0.034, -0.05), 0.0035, 'steel', seg=8)
cyl('carburettor.ticklerknob', (CX - 0.004, CY + 0.034, -0.05), (CX - 0.004, CY + 0.039, -0.05), 0.0065, 'steel', seg=12)
cyl('carburettor.union', (CX + 0.012, CY + 0.018, -0.05), (CX + 0.026, CY + 0.018, -0.05), 0.0045, 'brass', seg=10)
cyl('carburettor.feed', (CX - 0.004, CY - 0.012, -0.027), (CX - 0.004, CY - 0.012, -0.03), 0.009, 'cast', seg=12)
cyl('carburettor.drain', (CX - 0.004, CY - 0.034, -0.05), (CX - 0.004, CY - 0.041, -0.05), 0.007, 'steel', seg=6, sharp=30)
cyl('carburettor.startpiston', (CX - 0.01, CY - 0.012, 0.024), (CX - 0.01, CY - 0.012, 0.05), 0.0095, 'cast', seg=16)
cyl('carburettor.startknob', (CX - 0.01, CY - 0.012, 0.05), (CX - 0.01, CY - 0.012, 0.057), 0.0072, 'black', seg=16)
FUEL_A = (CX + 0.026, CY + 0.018, -0.05)

part('intake', (0.0, 0.24, 0))
FX_, FY_ = CX - 0.088, CY + 0.024
lathe('intake.horn', [(0.0, 0.0), (0.017, 0.0), (0.019, 0.012), (0.026, 0.024), (0.034, 0.03), (0.0, 0.03)], (CX - 0.031, CY, 0), (-1, 0.12, -0.35), 'cast', seg=32)
# round air cleaner with a pressed lid and a slotted face (photo of the unrestored machine)
lathe('intake.filter', [(0.0, 0.0), (0.05, 0.0), (0.053, 0.004), (0.053, 0.022), (0.05, 0.026), (0.0, 0.026)], (FX_, FY_, -0.036), (0, 0, -1), 'cast', seg=48)
lathe('intake.filterlid', [(0.0, 0.0), (0.044, 0.0), (0.046, 0.003), (0.03, 0.008), (0.0, 0.01)], (FX_, FY_, -0.062), (0, 0, -1), 'alusatin', seg=48)
# air slots round the drum (axis across the bike, so the slots sit on its rim)
for k in range(16):
    a = 2 * math.pi * k / 16
    rbox('intake.filterslot', (FX_ + 0.0535 * math.cos(a), FY_ + 0.0535 * math.sin(a), -0.049), (0.003, 0.0065, 0.016), 0.0012, 'black', rot=(math.degrees(a),))
cyl('intake.filternut', (FX_, FY_, -0.071), (FX_, FY_, -0.077), 0.007, 'steel', seg=6, sharp=30)
tube('intake.elbow', [(CX - 0.045, CY + 0.002, -0.016), (CX - 0.06, CY + 0.008, -0.026), (FX_, FY_, -0.034)], 0.019, 'cast', seg=16)
# T-piece in front of the carburettor; each branch runs out sideways and forwards high over the gearbox, then
# bends DOWN and forwards into the inlet flange on the rear face of the cylinder (1940 machine from the right,
# unrestored machine from the left)
cyl('intake.tee', (CX + 0.035, CY, 0), (CX + 0.07, CY - 0.004, 0), 0.02, 'cast', seg=20)
for s in (-1, 1):
    tube('intake.manifold', [(CX + 0.065, CY - 0.004, 0), (CX + 0.072, CY - 0.005, s * 0.05), (CX + 0.085, CY - 0.01, s * 0.105),
                              (CX + 0.1, 0.485, s * 0.15), (CX + 0.112, 0.47, s * 0.178), (CYL_X - 0.13, 0.445, s * 0.19),
                              (CYL_X - 0.128, 0.415, s * 0.19), (CYL_X - 0.118, 0.402, s * 0.19), (CYL_X - 0.105, 0.4, s * 0.19), (CYL_X - 0.093, 0.4, s * 0.19)],
         0.0185, 'cast', seg=16, per=8)

# exhausts: header in front of the cylinder, under the footboard, silencer to the rear. Measured on a 1 cm
# grid on the handbook side views (Fig. 1, German Abb. 2), the parts list 1938 photo, and the unrestored
# machine and the 1940 machine through wheel-solved cameras: the header leaves the front of the head near
# its top, bends forward and down in front of the cylinder and runs back almost level under the footboard
# straight into the silencer; the silencer, about 60 mm across, rises about 5 degrees towards the rear,
# and from a seam two thirds of the way back the tube flattens into an upright fishtail blade, taller
# than the tube, whose rear edge is raked so the lower corner is the rearmost point, ~0.13 m behind the axle
EX_Z = 0.198
EX_X0 = -0.335                    # front tip of the silencer (joint with the header)
EX_Y0, EX_SLOPE = 0.168, 0.08     # silencer axis height at the joint, rise per metre towards the rear
def ex_axis(x):
    return EX_Y0 + (EX_X0 - x) * EX_SLOPE
def exhaust_side():
    o = []
    hdr = [(CYL_X + 0.082, 0.4, EX_Z + 0.002), (0.21, 0.398, EX_Z + 0.008), (0.24, 0.377, EX_Z + 0.013), (0.255, 0.336, EX_Z + 0.016),
           (0.256, 0.265, EX_Z + 0.017), (0.245, 0.207, EX_Z + 0.016), (0.214, 0.176, EX_Z + 0.013), (0.15, 0.164, EX_Z + 0.008),
           (0.0, 0.1645, EX_Z + 0.003), (-0.15, 0.166, EX_Z), (-0.28, 0.1675, EX_Z), (EX_X0 + 0.004, 0.168, EX_Z)]
    o.append(tube('exhaust.header', hdr, 0.0172, 'chrome', seg=20, per=10))
    o.append(lathe('exhaust.nut', [(0.0172, -0.007), (0.0235, -0.007), (0.0235, 0.007), (0.0172, 0.007)], (CYL_X + 0.089, 0.4, EX_Z + 0.002), (1, 0.05, 0.06), 'chrome', seg=6, sharp=30))
    # silencer (unrestored machine, 1940 machine, parts list photo): a short cone from the header out to the
    # round body, the body, a seam ring, then a rounded bullet tapering to a point; the fishtail is a flat
    # pressed blade in the middle plane, its top edge carrying on the top line of the body and rising a little,
    # its rear edge raked so the lower corner is the rearmost point, its lower edge running forward under the bullet
    ax = Vector((-1.0, EX_SLOPE, 0.0)).normalized()      # along the silencer, towards the rear (rising)
    SR = 0.031
    X_CONE, X_SEAM, X_TIP = EX_X0 - 0.055, -0.685, -0.765
    L_SEAM = (EX_X0 - X_SEAM) / -ax.x
    prof = [(0.0, -0.004), (0.0176, -0.004), (0.0176, 0.0)]
    for k in range(1, 7):                                   # front cone, slightly convex
        t = k / 6
        prof.append((0.0176 + (SR - 0.0176) * (1 - (1 - t) ** 1.6), (EX_X0 - X_CONE) / -ax.x * t))
    prof.append((SR, L_SEAM))
    L_TIP = (EX_X0 - X_TIP) / -ax.x
    for k in range(1, 11):                                  # bullet
        t = k / 10
        prof.append((SR * max(0.0, 1 - t ** 1.9) ** 0.55, L_SEAM + (L_TIP - L_SEAM) * t))
    prof.append((0.0, L_TIP))
    o.append(lathe('exhaust.silencer', prof, (EX_X0, ex_axis(EX_X0), EX_Z), tuple(ax), 'chrome', seg=48))
    for xr in (X_CONE, X_SEAM):
        o.append(lathe('exhaust.seam', [(SR - 0.0005, -0.003), (SR + 0.0013, -0.0022), (SR + 0.0013, 0.0022), (SR - 0.0005, 0.003)],
                       (xr, ex_axis(xr), EX_Z), tuple(ax), 'chrome', seg=48))
    def ab(x, dy):
        return (x, ex_axis(x) + dy)
    blade = [ab(-0.655, SR * 0.92), ab(-0.70, SR + 0.002), ab(-0.74, SR + 0.004), ab(-0.766, SR + 0.006),
             (-0.776, ex_axis(-0.776) + SR + 0.004), (-0.818, 0.158), (-0.811, 0.155), (-0.76, 0.161), ab(-0.70, -SR - 0.003),
             ab(-0.67, -SR * 0.95), ab(-0.655, -SR * 0.85)]
    o.append(slab('exhaust.fishtail', blade, 0.008, EX_Z, 'chrome', bevel=0.0028, per=3, smooth_outline=True, sharp=60))
    # clamp collar where the header slides into the silencer, hanger eye below it (parts list photo, Fig. 1)
    c0 = Vector((EX_X0 + 0.01, ex_axis(EX_X0 + 0.01), EX_Z))
    o.append(lathe('exhaust.collar', [(0.0174, -0.009), (0.0226, -0.009), (0.0238, -0.006), (0.0238, 0.006), (0.0226, 0.009), (0.0174, 0.009)], tuple(c0), tuple(ax), 'chrome', seg=40))
    o.append(rbox('exhaust.hanger', (c0.x, c0.y - 0.034, EX_Z), (0.014, 0.024, 0.0045), 0.002, 'chrome'))
    o.append(cyl('exhaust.hangerbolt', (c0.x, c0.y - 0.04, EX_Z - 0.006), (c0.x, c0.y - 0.04, EX_Z + 0.006), 0.0035, 'steel', seg=6, sharp=30))
    # strap round the silencer with a bolt below and a stay up to the lower frame member (parts list photo, Fig. 1)
    xs_ = -0.505
    cs_ = Vector((xs_, ex_axis(xs_), EX_Z))
    o.append(lathe('exhaust.clip', [(SR - 0.0005, -0.007), (SR + 0.0025, -0.007), (SR + 0.0025, 0.007), (SR - 0.0005, 0.007)], tuple(cs_), tuple(ax), 'paint', seg=40))
    o.append(rbox('exhaust.cliplug', (xs_, cs_.y - SR - 0.006, EX_Z), (0.012, 0.012, 0.012), 0.002, 'paint'))
    o.append(cyl('exhaust.clipbolt', (xs_, cs_.y - SR - 0.009, EX_Z - 0.009), (xs_, cs_.y - SR - 0.009, EX_Z + 0.009), 0.004, 'steel', seg=6, sharp=30))
    o.append(tube('exhaust.bracket', [(xs_, cs_.y + SR * 0.7, EX_Z - SR * 0.7), (xs_ - 0.004, 0.236, 0.14), (xs_ - 0.005, 0.244, 0.118)], 0.0055, 'paint', seg=8))
    return o
part('exhaust', (0, -0.06, 0.42), 'P.exhaust.right')
er = exhaust_side()
part('exhaust', (0, -0.06, -0.42), 'P.exhaust.left')
mirror(er)

# kickstarter behind the left footboard. The gearbox shafts run fore and aft, so the kick shaft does too
# and the lever swings across the machine (handbook p. 33: segment R and spur wheels on the gear shafts):
# seen from above (Fig. 4) a plated arm runs out sideways just behind the board and the knurled rubber
# pedal on its end points backwards along the machine; at rest the arm rises slightly outwards
part('kickstarter', (-0.2, -0.04, -0.28))
# heights here are before the engine group is lowered by ENG_DY (0.03)
KS = Vector((-0.258, 0.283, -0.06))
PY, PZ, PX0, PX1 = 0.243, -0.188, -0.266, -0.338
cyl('kickstarter.boss', (-0.245, KS.y, KS.z), (KS.x - 0.004, KS.y, KS.z), 0.018, 'cast', seg=20)
cyl('kickstarter.nut', (KS.x - 0.004, KS.y, KS.z), (KS.x - 0.012, KS.y, KS.z), 0.009, 'steel', seg=6, sharp=30)
tube('kickstarter.lever', [(KS.x - 0.008, KS.y, KS.z - 0.006), (KS.x - 0.008, 0.25, -0.072), (KS.x - 0.008, 0.234, -0.1), (KS.x - 0.008, 0.234, -0.145), (KS.x - 0.008, PY, PZ)],
     0.0075, 'chrome', seg=12)
cyl('kickstarter.stem', (KS.x - 0.008, PY, PZ), (PX0, PY, PZ), 0.008, 'chrome', seg=12)
cyl('kickstarter.pedal', (PX0, PY, PZ), (PX1, PY, PZ), 0.0115, 'rubber', seg=16)
for k in range(6):
    xq = PX0 - 0.006 - k * 0.0118
    lathe('kickstarter.knurl', [(0.0112, -0.002), (0.0124, 0), (0.0112, 0.002)], (xq, PY, PZ), (1, 0, 0), 'rubber', seg=16)
lathe('kickstarter.cap', [(0.0, 0.0), (0.0118, 0.0), (0.0118, 0.004), (0.009, 0.008), (0.0, 0.009)], (PX1, PY, PZ), (-1, 0, 0), 'chrome', seg=16)
tube('kickstarter.spring', [(PX1 + 0.006, PY + 0.008, PZ - 0.004), (-0.334, 0.29, -0.196), (-0.33, 0.33, -0.198)], 0.0042, 'steel', seg=6, per=5)

# ==============================================================================================
# DRIVETRAIN
# ==============================================================================================
part('clutch', (0.0, -0.18, 0))
lathe('clutch.bell', [(0.06, -0.103), (0.1, -0.103), (0.106, -0.097), (0.106, -0.083), (0.1, -0.077), (0.06, -0.077)], (0, 0.355, 0), (1, 0, 0), 'cast', seg=56)
cyl('clutch.arm', (-0.245, 0.43, 0), (-0.29, 0.49, 0.02), 0.0075, 'steel', seg=8)
CLUTCH_A = (-0.29, 0.46, 0.02)
CLUTCH_REST = [(-0.25, 0.555, -0.03), (-0.1, 0.578, -0.05), (0.1, 0.6, -0.085), (0.17, 0.612, -0.142), (0.25, 0.634, -0.16), (0.345, 0.69, -0.162), (0.352, 0.79, -0.175), (0.31, 0.865, -0.235), (0.27, 0.882, -0.272)]

part('gearbox', (-0.22, 0, 0))
# bolted straight to the crankcase; the toolbox lid sits ~0.25 m behind the cylinder head centre (parts list
# 1938 photo, unrestored machine)
lathe('gearbox.casing', [(0.0, -0.256), (0.06, -0.256), (0.082, -0.25), (0.096, -0.236), (0.1, -0.21), (0.102, -0.145), (0.106, -0.118), (0.11, -0.103), (0.0, -0.103)], (0, 0.35, 0), (1, 0, 0), 'cast', seg=56)
rbox('gearbox.top', (-0.165, 0.448, 0), (0.12, 0.03, 0.085), 0.01, 'cast')
# tools live in a container cast into the gearbox, closed by a round hinged lid on the left
lathe('gearbox.toolbox', [(0.0, 0.0), (0.056, 0.0), (0.058, 0.004), (0.054, 0.011), (0.0, 0.013)], (-0.152, 0.355, -0.098), (0, 0, -1), 'cast', seg=40)
cyl('gearbox.hinge', (-0.182, 0.297, -0.106), (-0.122, 0.297, -0.106), 0.005, 'steel', seg=10)
cyl('gearbox.latch', (-0.152, 0.413, -0.106), (-0.152, 0.413, -0.116), 0.006, 'steel', seg=10)
cyl('gearbox.filler', (-0.125, 0.4, 0.085), (-0.125, 0.4, 0.098), 0.012, 'steel', seg=6, sharp=30)
cyl('gearbox.drain', (-0.18, 0.25, 0.04), (-0.18, 0.236, 0.04), 0.01, 'steel', seg=6, sharp=30)
cyl('gearbox.mountboss', (-0.185, 0.262, -0.083), (-0.185, 0.262, 0.083), 0.017, 'cast', seg=20)

# the engine and gearbox sit ~30 mm lower than first built: cylinder head centre at 0.34-0.35 m in the
# parts list photo, both handbook side views and the unrestored machine; everything bolted to them moves
# with them, the cables are laid afterwards to the new ends
ENG_DY = -0.03
ENGINE_PARTS = ('crankcase.', 'cylinders.', 'sparkplugs.', 'ignition.', 'generator.', 'carburettor.', 'intake.', 'kickstarter.', 'clutch.', 'gearbox.')
for o in list(COL.objects):
    if o.type == 'MESH' and o.name.startswith(ENGINE_PARTS):
        o.matrix_world = Matrix.Translation(V(0, ENG_DY, 0)) @ o.matrix_world
def eng(p):
    return (p[0], p[1] + ENG_DY, p[2])
part('carburettor', (-0.08, 0.36, 0), 'P.carburettor.fuel')
tube('carburettor.fuelline', [eng(FUEL_A), (FUEL_A[0] + 0.03, 0.6, -0.058), (-0.02, 0.628, -0.05)], 0.0035, 'brass', seg=8)
part('clutch', (0.0, -0.18, 0), 'P.clutch.cable')
tube('clutch.cable', [eng(CLUTCH_A)] + CLUTCH_REST, 0.0032, 'black', seg=6)

# Rear of the gearbox and the gearbox end of the drive shaft, from the original parts (parts list 1938):
# the upper part of the casing runs back to the flat rear cover (plate 21 no. 15) at x -0.29 (Fig. 1 on a 2 cm
# grid), no wider than the casing. In a round pocket of that cover, sealed by a large felt ring (plate 21
# no. 37), turns the shock-absorber flange (plate 23 no. 21 / plate 6 no. 21) keyed on the output shaft, its
# three pins in the driver (plate 6 no. 30), a dark disc with four holes whose face sits nearly flush with the
# cover inside its guard ring (no. 22). From the middle of the driver the cup end of the drive shaft (no. 20)
# with the adjusting nut and lock nut (nos. 23, 24), then the plain shaft back to the bevel box outside the
# frame strut; the rubber flexing in the flange lets the shaft run at an angle. Nothing stands proud of the
# cover but the face of the driver (Fig. 1: only the shaft and its collar behind x -0.29; Fig. 8 photo).
# The speedometer worm sits on the output shaft in front of the coupling (Fig. 18 text), its drive on top of
# the rear part with the cable going up.
# On top of the main casing, front right: the gear lever cover (plate 21 no. 1), a domed boss with a neck
# that the lever leaves upwards with its ball hood (plate 23 nos. 19, 26; Fig. 1, Abb. 2, Fig. 6).
part('gearbox', (-0.22, 0, 0), 'P.gearbox.rear')
# rear cover (plate 21 no. 15): an oval casting closing the whole rear of the casing behind a vertical joint at
# x -0.205, its sides and rear edge well rounded; the coupling turns in its rear face low on the right
# (civilian R 12 from the right, Bielefeld 2018, and the 1940 machine; Fig. 1 on a 2 cm grid)
RC_Y, RC_Z, RC_H, RC_W, RC_P = 0.37, 0.03, 0.065, 0.112, 2.6
def rc_ring(x, k, n=64):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        c, s_ = math.cos(t), math.sin(t)
        pts.append((x, RC_Y + k * RC_H * math.copysign(abs(s_) ** (2 / RC_P), s_), RC_Z + k * RC_W * math.copysign(abs(c) ** (2 / RC_P), c)))
    return pts
RC_ST = [(-0.205, 0.94), (-0.21, 0.99), (-0.24, 1.0), (-0.258, 0.985), (-0.271, 0.955), (-0.28, 0.915), (-0.2865, 0.86), (-0.2903, 0.79), (-0.2925, 0.7), (-0.2935, 0.55), (-0.294, 0.3)]
loft('gearbox.rearcover', [rc_ring(x, k) for x, k in RC_ST], 'cast', subsurf=1, sharp=89)
loft('gearbox.rearjoint', [rc_ring(-0.2035, 0.955), rc_ring(-0.2075, 0.955)], 'cast', subsurf=0, sharp=30)
GOUT = Vector((-0.284, 0.35, 0.1))                  # centre of the coupling, low on the right of the domed rear face
GX = Vector((-1.0, 0.0, 0.0))                      # coupling axis = gearbox output axis
# speedometer drive: the cable enters the top of the rear cover through a rubber sleeve (photos)
SPD = Vector((-0.232, 0.426, 0.07))
cyl('gearbox.speedodrive', tuple(SPD), tuple(SPD + Vector((0, 0.012, 0))), 0.009, 'cast', seg=16)
cyl('gearbox.speedonut', tuple(SPD + Vector((0, 0.012, 0))), tuple(SPD + Vector((0, 0.03, 0))), 0.0072, 'rubber', seg=12)
LC = Vector((-0.138, 0.38, 0.078))
lathe('gearbox.levercover', [(0.0, 0.0), (0.034, 0.0), (0.033, 0.014), (0.026, 0.034), (0.016, 0.044), (0.015, 0.087), (0.0, 0.087)], tuple(LC), (0, 1, 0), 'cast', seg=32)
lathe('gearbox.levercap', [(0.0, 0.0), (0.017, 0.0), (0.017, 0.006), (0.012, 0.012), (0.0, 0.013)], tuple(LC + Vector((0, 0.087, 0))), (0, 1, 0), 'chrome', seg=24)

part('driveshaft', (-0.24, -0.06, 0.2))
SB = Vector((-0.565, 0.35, 0.1))                     # straight back, parallel to the bike (photos, Fig. 18)
DF = GOUT + GX * 0.016                               # face of the coupling, just proud of the domed cover
# the coupling: shock-absorber flange and driver (plate 6 nos. 21, 30) inside the polished guard ring (no. 22),
# seated in the rear face; the dark driver face with its four holes sits just inside the ring
lathe('driveshaft.guardring', [(0.027, -0.03), (0.0305, -0.03), (0.0305, -0.0015), (0.029, 0.0), (0.027, 0.0)], tuple(DF), tuple(GX), 'chrome', seg=48)
lathe('driveshaft.driver', [(0.0, -0.03), (0.0272, -0.03), (0.0272, -0.002), (0.0, -0.002)], tuple(DF), tuple(GX), 'darkmetal', seg=48)
for k in range(4):
    a_ = 2 * math.pi * k / 4 + math.radians(20)
    cyl('driveshaft.hole', (DF.x + 0.0025, DF.y + 0.018 * math.sin(a_), DF.z + 0.018 * math.cos(a_)), (DF.x + 0.0015, DF.y + 0.018 * math.sin(a_), DF.z + 0.018 * math.cos(a_)), 0.0042, 'black', seg=12)
sdir = (SB - DF).normalized()
def sat(t):
    return tuple(DF + sdir * t)
# cup end of the shaft, adjusting nut and lock nut, then the plain shaft
lathe('driveshaft.cup', [(0.0, 0.0), (0.0165, 0.0), (0.0165, 0.016), (0.014, 0.02), (0.0, 0.02)], sat(-0.002), tuple(sdir), 'chrome', seg=28)
cyl('driveshaft.nut', sat(0.017), sat(0.026), 0.0145, 'chrome', seg=24)
cyl('driveshaft.locknut', sat(0.026), sat(0.032), 0.0125, 'chrome', seg=6, sharp=30)
cyl('driveshaft.shaft', sat(0.032), tuple(SB - sdir * 0.03), 0.011, 'chrome', seg=24)
cyl('driveshaft.joint', tuple(SB - sdir * 0.035), tuple(SB - sdir * 0.005), 0.02, 'steel', seg=24)

part('reardrive', (-0.3, 0, 0.34))
# bevel-drive housing: a smooth aluminium dome over the crown wheel, cover flange at its rim (photos, Fig. 1, 8);
# it sits in the frame's rear loop on the right, which wraps round it, its body centred on the straight drive
# shaft so the input neck leaves the middle of its front (1940 machine from the right rear, Bielefeld 2018)
RD = 0.005
lathe('reardrive.housing', [(0.0, 0.07 + RD), (0.08, 0.07 + RD), (0.1, 0.078 + RD), (0.106, 0.092 + RD), (0.107, 0.108 + RD), (0.103, 0.118 + RD), (0.0, 0.118 + RD)], (XR, AY, 0), (0, 0, 1), 'alusatin', seg=64)
lathe('reardrive.cover', [(0.0, 0.117 + RD), (0.106, 0.117 + RD), (0.108, 0.124 + RD), (0.104, 0.133 + RD), (0.094, 0.141 + RD), (0.07, 0.148 + RD), (0.035, 0.152 + RD), (0.0, 0.153 + RD)], (XR, AY, 0), (0, 0, 1), 'alusatin', seg=72)
# input neck of the bevel box, stepped: a wide collar with a bolted flange, then a narrower sleeve (Fig. 8)
NA, NB = Vector((XR + 0.067, 0.35, 0.1)), Vector((-0.565, 0.35, 0.1))
nd = (NB - NA).normalized()
cyl('reardrive.nose', tuple(NA), tuple(NA + nd * 0.04), 0.042, 'cast', seg=40)
cyl('reardrive.noseflange', tuple(NA + nd * 0.034), tuple(NA + nd * 0.042), 0.043, 'cast', seg=40)
nux = Vector((0, 1, 0)).cross(nd).normalized(); nuy = nd.cross(nux).normalized()
for k in range(3):
    a_ = 2 * math.pi * k / 3 + 0.5
    off = (nux * math.cos(a_) + nuy * math.sin(a_)) * 0.04
    cyl('reardrive.nosebolt', tuple(NA + nd * 0.042 + off), tuple(NA + nd * 0.048 + off), 0.0045, 'steel', seg=6, sharp=30)
cyl('reardrive.sleeve', tuple(NA + nd * 0.042), tuple(NB), 0.028, 'cast', seg=32)
cyl('reardrive.sleevering', tuple(NB - nd * 0.006), tuple(NB), 0.032, 'cast', seg=32)
for k in range(6):
    a = 2 * math.pi * k / 6 + 0.3
    cyl('reardrive.bolt', (XR + 0.086 * math.cos(a), AY + 0.086 * math.sin(a), 0.141 + RD), (XR + 0.086 * math.cos(a), AY + 0.086 * math.sin(a), 0.149 + RD), 0.0058, 'steel', seg=6, sharp=30)
cyl('reardrive.cap', (XR, AY, 0.151 + RD), (XR, AY, 0.16 + RD), 0.019, 'cast', seg=24)
rbox('reardrive.slot', (XR, AY, 0.1605 + RD), (0.026, 0.004, 0.002), 0.001, 'black', rot=(10,))
# drain plug below the centre and the brake-anchor lug with its two holes at the bottom (photo, Fig. 8)
cyl('reardrive.drain', (XR + 0.012, AY - 0.05, 0.146 + RD), (XR + 0.012, AY - 0.05, 0.155 + RD), 0.008, 'steel', seg=6, sharp=30)
for dx in (-0.018, 0.018):
    rbox('reardrive.lug', (XR + dx, AY - 0.104, 0.099), (0.012, 0.034, 0.02), 0.004, 'cast')
    cyl('reardrive.lughole', (XR + dx, AY - 0.112, 0.108), (XR + dx, AY - 0.112, 0.11), 0.0035, 'black', seg=10)
rbox('reardrive.staylug', (XR - 0.006, AY + 0.106, 0.104), (0.03, 0.016, 0.014), 0.004, 'cast')
rbox('reardrive.staylug', (XR - 0.106, AY - 0.004, 0.1), (0.014, 0.024, 0.014), 0.004, 'cast')
cyl('reardrive.filler', (XR - 0.05, AY + 0.075, 0.113 + RD), (XR - 0.05, AY + 0.09, 0.113 + RD), 0.009, 'steel', seg=6, sharp=30)

# rear brake pedal behind the right footboard, rod to the drum arm
part('footbrake', (-0.1, -0.06, 0.3))
# pedal just behind the rear end of the right board, in line with its inner half and clear above the
# exhaust header; pivot inboard on the frame (Fig. 4, photo p_engine)
FBP = FB_X0 - 0.02
cyl('footbrake.pivot', (FBP, 0.205, 0.125), (FBP, 0.205, 0.158), 0.012, 'black', seg=12)
tube('footbrake.arm', [(FBP, 0.205, 0.158), (FBP - 0.008, 0.222, 0.17), (FBP - 0.014, 0.232, 0.178)], 0.008, 'paint', seg=8)
rbox('footbrake.pad', (FBP - 0.016, 0.238, 0.2), (0.034, 0.016, 0.05), 0.005, 'rubber')
tube('footbrake.rod', [(FBP, 0.195, 0.125), (-0.32, 0.18, 0.124), (-0.45, 0.19, 0.122), (XR + 0.06, AY - 0.137, 0.088)], 0.0045, 'steel', seg=8)

# ==============================================================================================
# ELECTRICS
# ==============================================================================================
part('headlamp', (0.62, 0.34, 0))
HX, HY = 0.47, 0.908
shell_obj = lathe('headlamp.shell', [(0.0, -0.118), (0.035, -0.114), (0.068, -0.096), (0.092, -0.062), (0.105, -0.022), (0.108, 0.012), (0.108, 0.03), (0.105, 0.04)], (HX, HY, 0), (1, 0, 0), 'paint', seg=64)
lathe('headlamp.rim', [(0.098, 0.036), (0.109, 0.038), (0.112, 0.048), (0.108, 0.056), (0.098, 0.058), (0.098, 0.036)], (HX, HY, 0), (1, 0, 0), 'chrome', seg=64)
lathe('headlamp.reflector', [(0.0, -0.03), (0.04, -0.022), (0.075, -0.002), (0.098, 0.03), (0.0995, 0.038)], (HX, HY, 0), (1, 0, 0), 'chrome', seg=48)
lathe('headlamp.lens', [(0.099, 0.052), (0.08, 0.058), (0.04, 0.062), (0.0, 0.063)], (HX, HY, 0), (1, 0, 0), 'glass', seg=48)
cyl('headlamp.socket', (HX - 0.031, HY, 0), (HX + 0.004, HY, 0), 0.008, 'steel', seg=16)
cyl('headlamp.bulb', (HX + 0.004, HY, 0), (HX + 0.03, HY, 0), 0.012, 'glass', seg=16)
# fluted lens pattern just inside the glass (vertical prism flutes of the period Bosch lamp)
disc_decal('headlamp.lensface', (HX + 0.0585, HY, 0), (1, 0, 0), 0.0985, 'lens', seg=64, up=(0, 1, 0))
# speedometer let into the rear of the shell top, key with check lamp and safety plug in a row ahead of it.
# The bezel covers the rear ~45 % of the shell top and leans back about 40 degrees (photo of the 1940
# machine from the side); a clear band of black shell between it and the key row (Fig. 19)
sp = Vector((HX - 0.072, HY + 0.079, 0))
sd = Vector((-0.616, 0.788, 0)).normalized()
# speedometer let into the shell: a chrome bezel ring standing a few millimetres proud of the shell all
# round (its foot follows the curved shell), the dial recessed inside it (photo of the 1940 machine, Fig. 19)
_sb = bmesh.new(); _sb.from_mesh(shell_obj.data); SHELL_BVH = BVHTree.FromBMesh(_sb); _sb.free()
su = Vector((1, 0, 0)) - sd * sd.x; su.normalize(); sw = sd.cross(su)
def shell_hit(q):
    h = SHELL_BVH.ray_cast(V(*(q + sd * 0.1)), V(*(-sd)))
    return Vector((h[0].x, h[0].z, -h[0].y)) if h[0] is not None else q
NB = 64
# dial plane just above the highest point of the shell inside the bezel, so the shell never covers it
H0 = max((shell_hit(sp + (su * math.cos(2 * math.pi * k / 48) + sw * math.sin(2 * math.pi * k / 48)) * rr) - sp).dot(sd)
         for k in range(48) for rr in (0.0, 0.02, 0.0425)) + 0.0012
bm = bmesh.new()
rings = []
for (rr, mode) in ((0.0505, 'foot'), (0.0505, H0 + 0.0045), (0.0485, H0 + 0.0062), (0.0445, H0 + 0.0062), (0.0425, H0 + 0.0035), (0.0415, H0 - 0.001)):
    ring = []
    for k in range(NB):
        a = 2 * math.pi * k / NB
        q = sp + (su * math.cos(a) + sw * math.sin(a)) * rr
        if mode == 'foot':
            q = shell_hit(q) - sd * 0.002
        else:
            q = q + sd * mode
        ring.append(bm.verts.new(V(*q)))
    rings.append(ring)
for i in range(len(rings) - 1):
    for k in range(NB):
        k2 = (k + 1) % NB
        bm.faces.new((rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
finish(bm, 'headlamp.speedo', 'chrome', sharp=60)
cyl('headlamp.speedobody', tuple(sp - sd * 0.03), tuple(sp + sd * (H0 - 0.0005)), 0.0418, 'black', seg=48)
disc_decal('headlamp.dial', tuple(sp + sd * (H0 + 0.0002)), tuple(sd), 0.0412, 'dial', up=(1, 0, 0))
lathe('headlamp.glass', [(0.0, H0 + 0.0028), (0.042, H0 + 0.0028), (0.042, H0 + 0.0034), (0.0, H0 + 0.004)], tuple(sp), tuple(sd), 'dialglass', seg=48)
# key row about a fifth of the way back from the rim (photo of the 1940 machine, Fig. 19)
cyl('headlamp.key', (HX + 0.001, HY + 0.102, 0), (HX + 0.001, HY + 0.111, 0), 0.0065, 'chrome', seg=12)
rbox('headlamp.keybow', (HX + 0.001, HY + 0.115, 0), (0.014, 0.009, 0.0035), 0.0017, 'chrome')
# check lamp glass and safety plug each in a plated ring standing a few millimetres proud (Fig. 19)
for zq in (-0.032, 0.032):
    lathe('headlamp.fitting', [(0.0062, 0.0), (0.0098, 0.0), (0.0098, 0.0035), (0.0084, 0.0052), (0.0062, 0.0052)], (HX + 0.002, HY + 0.1, zq), (0, 1, 0), 'chrome', seg=24)
lathe('headlamp.checklamp', [(0.0, 0.0), (0.0064, 0.0), (0.0064, 0.0048), (0.004, 0.0062), (0.0, 0.0066)], (HX + 0.002, HY + 0.1, -0.032), (0, 1, 0), 'redlens', seg=20)
lathe('headlamp.safetyplug', [(0.0, 0.0), (0.0064, 0.0), (0.0064, 0.007), (0.005, 0.0088), (0.0, 0.009)], (HX + 0.002, HY + 0.1, 0.032), (0, 1, 0), 'black', seg=20)
rbox('headlamp.plugslot', (HX + 0.002, HY + 0.109, 0.032), (0.0012, 0.0012, 0.008), 0.0, 'chrome')
# Size and place: in Fig. 19 the shell is 0.87 of the bracket spacing, and the brackets sit over the fork
# legs (0.21 m apart), so the shell is about 0.18 m across; the shell top is ~4.5 cm under the first build
# (photo of the unrestored machine through the wheel-solved camera; side views of the handbook). The lamp is
# built at its first size above and scaled as a whole so the speedometer and key row keep their proportions.
LS = 0.84
HX0, HY0 = HX, HY
HX, HY = 0.462, 0.874
def lamp_xf(p):
    return (HX + LS * (p[0] - HX0), HY + LS * (p[1] - HY0), LS * p[2])
_M = Matrix.Translation(V(HX, HY, 0)) @ Matrix.Scale(LS, 4) @ Matrix.Translation(-V(HX0, HY0, 0))
for o in list(COL.objects):
    if o.type == 'MESH' and o.name.startswith('headlamp.') and o.parent == PART:
        o.matrix_world = _M @ o.matrix_world
yx, yy_ = forkpt(0.645)
for s in (-1, 1):
    slab('headlamp.bracket', [(yx - 0.02, yy_ - 0.01), (yx + 0.02, yy_ - 0.015), (HX - 0.005, HY - 0.022), (HX - 0.018, HY + 0.018), (HX - 0.044, HY + 0.01)], 0.008, s * 0.104, 'paint', bevel=0.002, per=4)
    # the lamp hangs on a plated domed cap nut each side (photo of the 1940 machine)
    cyl('headlamp.bolt', (HX - 0.021, HY, s * 0.086), (HX - 0.021, HY, s * 0.11), 0.008, 'steel', seg=12)
    lathe('headlamp.capnut', [(0.0, 0.0), (0.015, 0.0), (0.015, 0.0055), (0.0122, 0.0105), (0.0068, 0.013), (0.0044, 0.013), (0.0044, 0.01), (0.0, 0.01)],
          (HX - 0.021, HY, s * 0.1078), (0, 0, s), 'chrome', seg=32)
# speedometer drive cable: from the worm drive on the gearbox along the right side under the tank, below the
# head lug and in front of the lower fork bridge into the bottom of the lamp
tube('headlamp.speedocable', [(-0.232, 0.454, 0.07), (-0.235, 0.49, 0.072), (-0.25, 0.52, 0.074), (-0.215, 0.54, 0.074), (-0.16, 0.565, 0.078), (-0.1, 0.588, 0.08), (-0.03, 0.6, 0.1), (0.06, 0.61, 0.12), (0.15, 0.63, 0.135), (0.25, 0.62, 0.138),
                              (0.32, 0.628, 0.132), (0.37, 0.65, 0.09), (0.43, 0.70, 0.055), (0.452, 0.745, 0.048), (0.44, 0.775, 0.04), (0.428, 0.795, 0.035)], 0.0035, 'black', seg=6)

# disc horn between the two front frame members below the badge panel, face forward; the handbook
# side view shows it edge-on just ahead of the front member (Fig. 1), photo p_head from the front quarter
part('horn', (0.5, 0.0, 0))
HO = (0.27, 0.565, 0)
lathe('horn.body', [(0, -0.032), (0.03, -0.03), (0.042, -0.014), (0.044, 0.004), (0.0, 0.006)], HO, (1, 0, 0), 'black', seg=40)
lathe('horn.rim', [(0.036, 0.004), (0.045, 0.004), (0.046, 0.01), (0.036, 0.012)], HO, (1, 0, 0), 'chrome', seg=40)
lathe('horn.grille', [(0.0, 0.02), (0.02, 0.018), (0.036, 0.011)], HO, (1, 0, 0), 'chrome', seg=40)
cyl('horn.bracket', (0.23, 0.565, -0.083), (0.23, 0.565, 0.083), 0.006, 'black', seg=8)
cyl('horn.strap', (0.229, 0.565, 0), (0.242, 0.565, 0), 0.009, 'black', seg=10)

part('battery', (-0.04, 0.06, -0.36))
# a tall light-coloured hard-rubber case standing on a black bracket on the left lower member right behind
# the gearbox, its bottom at the top of the member, ~0.08 m long and 0.17 m tall (parts list 1938 photo on a
# 1 cm grid; the unrestored machine has the same light case)
BX, BZ, BY0 = -0.27, -0.164, 0.252
rbox('battery.tray', (BX, BY0 - 0.004, BZ), (0.09, 0.008, 0.085), 0.003, 'paint')
rbox('battery.case', (BX, BY0 + 0.075, BZ), (0.08, 0.15, 0.08), 0.006, 'ivory')
rbox('battery.lid', (BX, BY0 + 0.156, BZ), (0.084, 0.012, 0.084), 0.004, 'black')
rbox('battery.bracket', (BX + 0.046, BY0 + 0.01, BZ), (0.008, 0.05, 0.03), 0.002, 'paint')
cyl('battery.terminal', (BX - 0.018, BY0 + 0.162, BZ + 0.02), (BX - 0.018, BY0 + 0.175, BZ + 0.02), 0.006, 'brass', seg=10)
cyl('battery.terminal', (BX + 0.018, BY0 + 0.162, BZ - 0.02), (BX + 0.018, BY0 + 0.175, BZ - 0.02), 0.006, 'brass', seg=10)
rbox('battery.strap', (BX, BY0 + 0.1, BZ), (0.084, 0.012, 0.084), 0.003, 'black')
tube('battery.cable', [(BX - 0.018, BY0 + 0.175, BZ + 0.02), (BX + 0.01, BY0 + 0.21, BZ + 0.03), (-0.23, 0.5, -0.105), (-0.13, 0.52, -0.1)], 0.0035, 'rubber', seg=6)

# ==============================================================================================
# FINISH: apply modifiers, merge per part and material, export
# ==============================================================================================
def apply_all():
    dg = bpy.context.evaluated_depsgraph_get()
    for o in list(COL.objects):
        if o.type != 'MESH' or not o.modifiers:
            continue
        ev = o.evaluated_get(dg)
        me = bpy.data.meshes.new_from_object(ev)
        old = o.data
        o.modifiers.clear()
        o.data = me
        bpy.data.meshes.remove(old)

def merge_by_material():
    empties = [o for o in COL.objects if o.type == 'EMPTY']
    for e in empties:
        groups = {}
        for c in kids(e):
            if c.type == 'MESH':
                groups.setdefault(c.data.materials[0].name, []).append(c)
        for mname, objs in groups.items():
            if len(objs) < 2:
                objs[0].name = f"{e['part']}.{mname}"
                continue
            with bpy.context.temp_override(active_object=objs[0], selected_editable_objects=objs, selected_objects=objs):
                bpy.ops.object.join()
            objs[0].name = f"{e['part']}.{mname}"

if '--audit' in ARGS:
    exec(open(os.path.join(HERE, 'audit_layers.py')).read(), globals())
if '--debug' in ARGS:
    exec(open(ARGS[ARGS.index('--debug') + 1]).read(), globals())

apply_all()
merge_by_material()

tris = sum(len(o.data.loop_triangles) if o.data.calc_loop_triangles() is None else 0 for o in COL.objects if o.type == 'MESH')
print('OBJECTS', len([o for o in COL.objects if o.type == 'MESH']), 'TRIS', tris)

if '--blend' in ARGS:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'r12.blend'))

if '--glb' in ARGS:
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, 'r12.glb'), export_format='GLB', use_selection=False, export_apply=True,
        export_extras=True, export_yup=True, export_materials='EXPORT', export_image_format='AUTO',
        export_cameras=False, export_lights=False, export_texcoords=True, export_normals=True,
        export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=7,
        export_draco_position_quantization=14, export_draco_normal_quantization=10,
        export_draco_texcoord_quantization=12, export_draco_generic_quantization=12)
    print('GLB', os.path.getsize(os.path.join(OUT, 'r12.glb')))

# ------------------------------------------------------------------------------ check renders
if '--checks' in ARGS:
    world = bpy.data.worlds.new('w')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.9, 0.9, 0.9, 1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.9
    scene.world = world
    sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 3.0
    so = bpy.data.objects.new('sun', sun); scene.collection.objects.link(so)
    so.rotation_euler = (math.radians(50), math.radians(10), math.radians(30))
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'Standard'
    cam = bpy.data.cameras.new('cam')
    co = bpy.data.objects.new('cam', cam); scene.collection.objects.link(co)
    scene.camera = co
    def shot(name, loc, look, ortho=None, res=(2000, 1333), lens=50):
        scene.render.resolution_x, scene.render.resolution_y = res
        cam.type = 'ORTHO' if ortho else 'PERSP'
        if ortho:
            cam.ortho_scale = ortho
        cam.lens = lens
        co.location = Vector(loc)
        d = (Vector(look) - Vector(loc))
        co.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = os.path.join(OUT, name)
        bpy.ops.render.render(write_still=True)
    # right side, same frame as the instruction-book side view: x -1..1, y -0.323..1.01
    shot('check_right.png', V(0, 0.3435, 5.0), V(0, 0.3435, 0), ortho=2.0)
    shot('check_left.png', V(0, 0.45, -5.0), V(0, 0.45, 0), ortho=2.2, res=(1600, 1000))
    # top view with the front at the top of the image (camera rolled so bike +x points up)
    scene.render.resolution_x, scene.render.resolution_y = 1000, 1700
    cam.type = 'ORTHO'; cam.ortho_scale = 2.55
    co.location = V(-0.03, 5.0, 0)
    co.rotation_euler = (0.0, 0.0, -math.pi / 2)
    scene.render.filepath = os.path.join(OUT, 'check_top.png')
    bpy.ops.render.render(write_still=True)
    shot('check_front.png', V(5.0, 0.5, 0.0001), V(0, 0.5, 0), ortho=1.3, res=(1000, 1100))
    shot('check_34.png', V(2.1, 1.25, -2.4), V(0.0, 0.45, 0), res=(1600, 1100), lens=55)
    shot('check_34r.png', V(-2.0, 1.1, 2.4), V(0.0, 0.45, 0), res=(1600, 1100), lens=55)
    shot('close_engine_r.png', V(-0.35, 0.95, 0.95), V(0.02, 0.38, 0.12), res=(1400, 1000), lens=45)
    shot('close_front.png', V(1.25, 0.95, 1.05), V(0.52, 0.62, 0.0), res=(1200, 1200), lens=45)
    shot('close_rear_r.png', V(-1.55, 0.75, 1.35), V(-0.6, 0.42, 0.05), res=(1400, 1000), lens=45)
    shot('close_tank_l.png', V(0.15, 1.2, -1.0), V(0.05, 0.72, 0.0), res=(1400, 1000), lens=45)
    shot('close_engine_l.png', V(0.05, 0.62, -1.05), V(-0.03, 0.42, -0.08), res=(1400, 1000), lens=45)
    shot('close_gate_r.png', V(0.25, 0.85, 0.62), V(0.0, 0.7, 0.11), res=(1000, 1200), lens=50)
    shot('close_headlamp_top.png', V(0.62, 1.45, 0.0001), V(0.45, 0.9, 0.0), res=(1000, 1100), lens=50)
    shot('close_fork_l.png', V(0.95, 0.42, -0.75), V(0.66, 0.38, -0.08), res=(1000, 1200), lens=45)
    shot('close_reardrive_r.png', V(-0.55, 0.42, 0.75), V(-0.62, 0.34, 0.12), res=(1300, 1000), lens=45)
