# Save the built model as an inspectable Blender scene with the photo-matched cameras.
#   Blender -b -P build_r12.py -- <out_dir> --debug save_scene.py
# Each refs/cam_*.json (solved from landmarks in the photo, see refs/) becomes a camera whose background
# is that photo at half opacity, so the model can be checked against the real machine through it.
import bpy, json, glob, math, os
from mathutils import Vector, Matrix

scene = bpy.context.scene
world = bpy.data.worlds.new('studio')
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.32, 0.32, 0.34, 1)
bg.inputs['Strength'].default_value = 1.0
scene.world = world
for name, energy, rot in (('key', 3.5, (50, 10, 30)), ('fill', 1.2, (60, 0, 200))):
    ld = bpy.data.lights.new(name, 'SUN'); ld.energy = energy
    lo = bpy.data.objects.new(name, ld); scene.collection.objects.link(lo)
    lo.rotation_euler = tuple(math.radians(a) for a in rot)

def B(p):
    return Vector((p[0], -p[2], p[1]))

refs = os.path.join(HERE, 'refs')
first = None
for path in sorted(glob.glob(os.path.join(refs, 'cam_*.json'))):
    c = json.load(open(path))
    tag = os.path.basename(path)[4:-5]
    photo = [p for p in glob.glob(os.path.join(refs, tag + '_*.jpg'))][0]
    cd = bpy.data.cameras.new('foto ' + tag)
    co = bpy.data.objects.new('foto ' + tag, cd)
    scene.collection.objects.link(co)
    pos, fwd, up = B(c['pos']), B(c['fwd']).normalized(), B(c['up'])
    zc = -fwd
    yc = (up - zc * up.dot(zc)).normalized()
    xc = yc.cross(zc)
    co.matrix_world = Matrix.Translation(pos) @ Matrix((xc, yc, zc)).transposed().to_4x4()
    W, H = c['size']
    cd.sensor_fit = 'HORIZONTAL'
    cd.sensor_width = 36.0
    cd.lens = c['f'] / W * 36.0
    cd.shift_x = (W / 2 - c['pp'][0]) / W
    cd.shift_y = (c['pp'][1] - H / 2) / W
    cd.clip_start = 0.05
    cd.show_background_images = True
    bi = cd.background_images.new()
    bi.image = bpy.data.images.load(photo)
    bi.alpha = 0.5
    bi.display_depth = 'FRONT'
    if first is None:
        first = (co, W, H)
if first:
    co, W, H = first
    scene.camera = co
    scene.render.resolution_x, scene.render.resolution_y = W, H
    scene.render.resolution_percentage = 50
dst = os.path.join(HERE, 'r12_scene.blend')
bpy.ops.wm.save_as_mainfile(filepath=dst, copy=True)
print('SAVED', dst)
