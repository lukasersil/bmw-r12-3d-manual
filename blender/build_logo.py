# BMW roundel for the opening sequence: an enamel badge like the one on the R 12 frame gusset
# (nickel rim and inner ring, black enamel ring with raised metal letters and two slotted screws,
# slightly domed blue and white enamel quadrants split by thin metal lines), already fractured.
#   Blender -b -P build_logo.py -- <out_dir> [--glb] [--check]
# Built in the Blender XY plane facing +Z, then turned so the glTF file gets x right, y up and the
# face towards +z. Each shard is its own object with its origin at its centre, so the page can
# throw the pieces apart; together they read as an intact badge.
import bpy, bmesh, math, sys, os, random
from mathutils import Vector, Matrix

ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = os.path.abspath(ARGS[0] if ARGS else '.')
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

R = 0.34          # outer radius of the rim, metres
SEG = 192         # segments round the badge (multiple of 4 so quadrant borders fall on edges)

# ------------------------------------------------------------------------------ materials
def lin(h):
    """sRGB hex to linear RGB."""
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)

MATS = []
def mat(name, color, metal=0.0, rough=0.5, coat=0.0, coat_rough=0.03):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    if coat:
        p.inputs['Coat Weight'].default_value = coat
        p.inputs['Coat Roughness'].default_value = coat_rough
    MATS.append(m)
    return len(MATS) - 1

NICKEL = mat('logo_nickel', (0.86, 0.84, 0.8), metal=1, rough=0.09)
BLACK = mat('logo_black', lin('#060607'), rough=0.18, coat=1)
BLUE = mat('logo_blue', lin('#1f58a8'), rough=0.2, coat=1)
WHITE = mat('logo_white', lin('#e9e6dc'), rough=0.24, coat=1)
BACK = mat('logo_back', (0.36, 0.35, 0.33), metal=1, rough=0.46)
CORE = mat('logo_core', (0.11, 0.095, 0.08), metal=0.7, rough=0.7)   # raw metal under the plating, seen on the breaks

# ------------------------------------------------------------------------------ solids (XY plane, face +Z)
def lathe(bm, profile, mi, seg=SEG, a0=0.0):
    """Closed (r, z) profile revolved round Z into a closed solid."""
    n = len(profile)
    rings = []
    for k in range(seg):
        a = a0 + 2 * math.pi * k / seg
        c, s = math.cos(a), math.sin(a)
        rings.append([bm.verts.new((r * c, r * s, z)) for r, z in profile])
    for k in range(seg):
        A, B = rings[k], rings[(k + 1) % seg]
        for i in range(n):
            j = (i + 1) % n
            f = bm.faces.new((A[i], A[j], B[j], B[i]))
            f.material_index = mi

def dome_z(r, rq, z_edge, z_top):
    t = min(1.0, r / rq)
    return z_edge + (z_top - z_edge) * (1 - t * t)

def dome(bm, rq, z_bot, z_edge, z_top, rings=28, seg=SEG):
    """Domed enamel field: one closed solid, quadrants coloured by angle."""
    top = []
    for i in range(1, rings + 1):
        r = rq * i / rings
        top.append([bm.verts.new((r * math.cos(2 * math.pi * k / seg), r * math.sin(2 * math.pi * k / seg),
                                  dome_z(r, rq, z_edge, z_top))) for k in range(seg)])
    c_top = bm.verts.new((0, 0, z_top))
    bot = [bm.verts.new((rq * math.cos(2 * math.pi * k / seg), rq * math.sin(2 * math.pi * k / seg), z_bot)) for k in range(seg)]
    c_bot = bm.verts.new((0, 0, z_bot))

    def colour(a):
        a %= 2 * math.pi
        q = int(a // (math.pi / 2))      # 0 top-right, 1 top-left, 2 bottom-left, 3 bottom-right
        return WHITE if q in (0, 2) else BLUE

    for k in range(seg):
        k2 = (k + 1) % seg
        am = 2 * math.pi * (k + 0.5) / seg
        f = bm.faces.new((c_top, top[0][k], top[0][k2]))
        f.material_index = colour(am)
        for i in range(rings - 1):
            f = bm.faces.new((top[i][k], top[i + 1][k], top[i + 1][k2], top[i][k2]))
            f.material_index = colour(am)
        f = bm.faces.new((top[-1][k], bot[k], bot[k2], top[-1][k2]))
        f.material_index = NICKEL
        f = bm.faces.new((c_bot, bot[k2], bot[k]))
        f.material_index = BACK

def strip(bm, p0, p1, w, rq, z_edge, z_top, lift=0.0012, depth=0.004, n=60):
    """Thin metal line lying on the dome from p0 to p1 (XY), rounded on top."""
    d = (p1 - p0).normalized()
    side = Vector((-d.y, d.x, 0))
    secs = []
    for i in range(n + 1):
        p = p0.lerp(p1, i / n)
        zt = dome_z(p.length, rq, z_edge, z_top) + lift
        zb = zt - lift - depth
        prof = [(-w / 2, zb), (w / 2, zb), (w / 2, zt - w * 0.25), (w * 0.22, zt), (-w * 0.22, zt), (-w / 2, zt - w * 0.25)]
        secs.append([bm.verts.new((p.x + side.x * u, p.y + side.y * u, z)) for u, z in prof])
    m = len(secs[0])
    for i in range(n):
        A, B = secs[i], secs[i + 1]
        for j in range(m):
            k = (j + 1) % m
            f = bm.faces.new((A[j], A[k], B[k], B[j]))
            f.material_index = NICKEL
    for cap, rev in ((secs[0], True), (secs[-1], False)):
        f = bm.faces.new(list(reversed(cap)) if rev else cap)
        f.material_index = NICKEL

def arc_profile(points, per=6):
    """Smooth closed (r, z) outline through control points (Catmull-Rom)."""
    P = [Vector(p) for p in points]
    n = len(P)
    out = []
    for i in range(n):
        p0, p1, p2, p3 = P[i - 1], P[i], P[(i + 1) % n], P[(i + 2) % n]
        for k in range(per):
            t = k / per
            t2, t3 = t * t, t * t * t
            v = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
            out.append((v.x, v.y))
    return out

FONT = None
def load_font():
    global FONT
    for d in ('5.2', '5.1', '5.0', '4.5'):
        p = f'/Applications/Blender.app/Contents/Resources/{d}/datafiles/fonts/Inter.woff2'
        if os.path.exists(p):
            try:
                FONT = bpy.data.fonts.load(p)
                return
            except Exception as e:
                print('font load failed', e)
    FONT = None

def letter(ch, cap, ang, rmid, z0, height, offset):
    """Raised metal letter, upright along the radius at angle ang (deg)."""
    cu = bpy.data.curves.new('L' + ch, 'FONT')
    cu.body = ch
    if FONT:
        cu.font = FONT
    cu.size = cap / 0.727
    cu.align_x = 'CENTER'
    cu.offset = offset
    cu.extrude = height / 2
    cu.bevel_depth = height * 0.18
    cu.bevel_resolution = 2
    cu.resolution_u = 8
    ob = bpy.data.objects.new('L' + ch, cu)
    scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob)
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    lo = Vector((min(v.co.x for v in bm.verts), min(v.co.y for v in bm.verts), min(v.co.z for v in bm.verts)))
    hi = Vector((max(v.co.x for v in bm.verts), max(v.co.y for v in bm.verts), max(v.co.z for v in bm.verts)))
    c = (lo + hi) / 2
    a = math.radians(ang)
    rot = Matrix.Rotation(a - math.pi / 2, 4, 'Z')
    for v in bm.verts:
        p = v.co - Vector((c.x, c.y, lo.z))
        v.co = rot @ p + Vector((rmid * math.cos(a), rmid * math.sin(a), z0))
    for f in bm.faces:
        f.material_index = NICKEL
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm

def screw(bm_target, ang, rmid, z0, rad, slot_ang):
    """Slotted round-head screw through the black ring."""
    a = math.radians(ang)
    centre = Vector((rmid * math.cos(a), rmid * math.sin(a), 0))
    h = rad * 0.42
    head = arc_profile([(rad * 0.02, z0 - 0.002), (rad, z0 - 0.002), (rad * 1.0, z0 + h * 0.25), (rad * 0.75, z0 + h * 0.85),
                        (rad * 0.02, z0 + h)], per=5)
    g = rad * 0.13
    rot = Matrix.Rotation(math.radians(slot_ang), 4, 'Z')
    for sgn in (1, -1):
        bm = bmesh.new()
        lathe(bm, head, NICKEL, seg=48)
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(sgn * g, 0, 0), plane_no=(-sgn, 0, 0), clear_outer=True)
        res = bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=0)
        for f in res['faces']:
            f.material_index = NICKEL
        for v in bm.verts:
            v.co = rot @ v.co + centre
        merge(bm_target, bm)
    # slot bottom
    bm = bmesh.new()
    lathe(bm, [(rad * 0.3, z0 - 0.002), (rad * 0.9, z0 - 0.002), (rad * 0.9, z0 + h * 0.35), (rad * 0.3, z0 + h * 0.35)], NICKEL, seg=32)
    for v in bm.verts:
        v.co = v.co + centre
    merge(bm_target, bm)

def merge(dst, src):
    me = bpy.data.meshes.new('tmp')
    src.to_mesh(me)
    src.free()
    dst.from_mesh(me)
    bpy.data.meshes.remove(me)

# ------------------------------------------------------------------------------ the badge
# radii as fractions of R, heights in metres (badge is ~10x real size, proportions of the frame badge)
R_IN = 0.60 * R        # enamel field
RB0, RB1 = 0.595 * R, 0.648 * R   # inner ring bead
RK0, RK1 = 0.64 * R, 0.935 * R    # black ring
RR0 = 0.925 * R        # rim bead inner edge
Z_ENAMEL = 0.0135
COMPONENTS = []        # (name, bmesh) closed solids

def comp(name):
    bm = bmesh.new()
    COMPONENTS.append((name, bm))
    return bm

load_font()

bm = comp('backplate')
# back face stamped with a few turned steps, like a pressed badge
lathe(bm, [(0.0004, 0.0012), (0.3 * R, 0.0012), (0.3 * R, 0.0), (0.62 * R, 0.0), (0.62 * R, 0.0009), (0.86 * R, 0.0009),
           (0.86 * R, 0.0), (0.985 * R, 0.0), (0.985 * R, 0.007), (0.0004, 0.007)], BACK)

bm = comp('rim')
rim = arc_profile([(RR0, 0.004), (RR0 + 0.004, 0.017), (0.952 * R, 0.0238), (0.978 * R, 0.0262), (0.996 * R, 0.0215),
                   (1.0 * R, 0.011), (0.998 * R, 0.002), (0.97 * R, 0.0)], per=6)
lathe(bm, rim, NICKEL)

bm = comp('blackring')
lathe(bm, [(RK0, 0.005), (RK1, 0.005), (RK1, Z_ENAMEL), (RK0, Z_ENAMEL)], BLACK)
bm.normal_update()      # new faces carry no normal until this
for f in bm.faces:
    if abs(f.normal.z) < 0.5:
        f.material_index = NICKEL

bm = comp('innerring')
lathe(bm, arc_profile([(RB0, 0.006), (RB1, 0.006), (RB1, 0.0145), (0.635 * R, 0.0192), (0.62 * R, 0.0204),
                       (0.605 * R, 0.0192), (RB0, 0.0145)], per=5), NICKEL)

bm = comp('enamel')
Z_EDGE, Z_TOP = 0.0158, 0.0262
dome(bm, R_IN, 0.006, Z_EDGE, Z_TOP)

bm = comp('dividers')
strip(bm, Vector((-R_IN * 0.985, 0, 0)), Vector((R_IN * 0.985, 0, 0)), 0.0042, R_IN, Z_EDGE, Z_TOP)
strip(bm, Vector((0, -R_IN * 0.985, 0)), Vector((0, R_IN * 0.985, 0)), 0.0042, R_IN, Z_EDGE, Z_TOP)

RMID = (RK0 + RK1) / 2
for ch, ang in (('B', 133), ('M', 90), ('W', 47)):
    bm = letter(ch, cap=0.072, ang=ang, rmid=RMID + 0.001, z0=Z_ENAMEL - 0.001, height=0.0048, offset=0.0024)
    COMPONENTS.append(('letter_' + ch, bm))

bm = comp('screws')
screw(bm, 0, RMID, Z_ENAMEL, 0.0165, 28)
screw(bm, 180, RMID, Z_ENAMEL, 0.0165, 74)

for name, bm in COMPONENTS:
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    open_edges = sum(1 for e in bm.edges if e.is_boundary)
    print('component', name, len(bm.faces), 'faces, open edges', open_edges)

# ------------------------------------------------------------------------------ fracture (Voronoi cells, cut with planes)
rng = random.Random(19)
seeds = [Vector((0.012, -0.008, 0))]
tries = 0
while tries < 6000:
    tries += 1
    rr = R * 1.02 * math.sqrt(rng.random())
    aa = rng.random() * 2 * math.pi
    p = Vector((rr * math.cos(aa), rr * math.sin(aa), 0))
    dmin = 0.05 + 0.045 * (rr / R)      # smaller pieces near the centre, where the badge breaks
    if all((p - q).length > dmin for q in seeds):
        seeds.append(p)
print('SEEDS', len(seeds))

def cut_piece(src, si):
    bm = src.copy()
    for sj in seeds:
        if sj is si:
            continue
        d = sj - si
        if d.length > 0.32:
            continue
        n = d.normalized()
        co = (si + sj) / 2
        side = [(v.co - co).dot(n) for v in bm.verts]
        if not side:
            break
        if max(side) <= 1e-7:
            continue
        if min(side) >= -1e-7:
            bm.free()
            return None
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=co, plane_no=n,
                               clear_outer=True, dist=1e-7)
        edges = [e for e in bm.edges if e.is_boundary]
        if edges:
            res = bmesh.ops.holes_fill(bm, edges=edges, sides=0)
            for f in res['faces']:
                f.material_index = CORE
                f.smooth = False
    if not bm.verts:
        bm.free()
        return None
    return bm

TO_GLTF = Matrix.Rotation(math.radians(90), 4, 'X')   # (x, y, z) -> (x, -z, y): face +Z becomes glTF +z
col = bpy.data.collections.new('logo')
scene.collection.children.link(col)
shards = 0
for idx, si in enumerate(seeds):
    cell = bmesh.new()
    for name, src in COMPONENTS:
        piece = cut_piece(src, si)
        if piece is None:
            continue
        for f in piece.faces:
            f.smooth = f.material_index != CORE
        lim = math.radians(36)
        for e in piece.edges:
            if len(e.link_faces) == 2 and e.calc_face_angle(0) > lim:
                e.smooth = False
            if any(f.material_index == CORE for f in e.link_faces):
                e.smooth = False
        bmesh.ops.recalc_face_normals(piece, faces=piece.faces)
        merge(cell, piece)
    if not cell.verts:
        cell.free()
        continue
    ctr = sum((v.co for v in cell.verts), Vector()) / len(cell.verts)
    for v in cell.verts:
        v.co = TO_GLTF @ (v.co - ctr)
    me = bpy.data.meshes.new(f'shard_{idx:03d}')
    cell.to_mesh(me)
    cell.free()
    for m in MATS:
        me.materials.append(m)
    ob = bpy.data.objects.new(f'shard_{idx:03d}', me)
    ob.location = TO_GLTF @ ctr
    col.objects.link(ob)
    shards += 1

for o in col.objects:
    # drop material slots a shard does not use, keeps the glTF primitives few
    idx = [p.material_index for p in o.data.polygons]
    keep = sorted(set(idx))
    remap = {old: new for new, old in enumerate(keep)}
    o.data.materials.clear()          # clearing the slots resets the indices, so set them afterwards
    for i in keep:
        o.data.materials.append(MATS[i])
    o.data.polygons.foreach_set('material_index', [remap[i] for i in idx])
    o.data.update()

tris = 0
for o in col.objects:
    o.data.calc_loop_triangles()
    tris += len(o.data.loop_triangles)
print('SHARDS', shards, 'TRIS', tris)

if '--glb' in ARGS:
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, 'logo.glb'), export_format='GLB', use_selection=False, export_apply=True,
        export_extras=False, export_yup=True, export_materials='EXPORT', export_cameras=False, export_lights=False,
        export_texcoords=False, export_normals=True,
        export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=7,
        export_draco_position_quantization=16, export_draco_normal_quantization=12,
        export_draco_generic_quantization=12)
    print('GLB', os.path.getsize(os.path.join(OUT, 'logo.glb')))

# ------------------------------------------------------------------------------ check render
if '--check' in ARGS:
    world = bpy.data.worlds.new('w')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.35, 0.35, 0.36, 1)
    scene.world = world
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x, scene.render.resolution_y = 1200, 1200
    for loc, energy in (((-1.2, -1.6, 1.4), 220), ((1.4, -1.0, 0.6), 90), ((0.0, 1.2, 1.5), 60)):
        ld = bpy.data.lights.new('l', 'AREA')
        ld.energy = energy
        ld.size = 1.2
        lo = bpy.data.objects.new('l', ld)
        lo.location = loc
        lo.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        scene.collection.objects.link(lo)
    cam = bpy.data.cameras.new('c')
    cam.lens = 85
    co = bpy.data.objects.new('c', cam)
    scene.collection.objects.link(co)
    scene.camera = co
    for fname, loc in (('logo_front.png', (0.0, -2.6, 0.0)), ('logo_angle.png', (1.5, -1.9, 0.5))):
        co.location = loc
        co.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = os.path.join(OUT, fname)
        bpy.ops.render.render(write_still=True)
