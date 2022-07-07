import math
import bpy

#Remakes of bpy.ops operators to avoid lag from scene updates.


def select_all_obj():
    for o in bpy.context.visible_objects:
        o.select_set(True)

def deselect_all_obj():
    for o in bpy.context.selected_objects:
        o.select_set(False)

def select_all_verts():
    me = bpy.context.active_object.to_mesh()
    for v in me.vertices:
        v.select = True
    bpy.context.active_object.to_mesh_clear()


def deselect_all_verts():
    me = bpy.context.active_object.to_mesh()
    for v in me.vertices:
        v.select = False
    bpy.context.active_object.to_mesh_clear()
