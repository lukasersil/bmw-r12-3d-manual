# Open r12_scene.blend looking through the photo camera, material preview shading.
#   Blender blender/r12_scene.blend -P blender/open_view.py
import bpy

def setup():
    for win in bpy.context.window_manager.windows:
        for area in win.screen.areas:
            if area.type == 'VIEW_3D':
                sp = area.spaces.active
                sp.shading.type = 'MATERIAL'
                sp.overlay.show_floor = False
                sp.overlay.show_axis_x = sp.overlay.show_axis_y = False
                sp.region_3d.view_perspective = 'CAMERA'
                sp.lock_camera = False
    return None

bpy.app.timers.register(setup, first_interval=1.0)
