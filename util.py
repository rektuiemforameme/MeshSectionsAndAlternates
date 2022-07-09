import math
import bpy
import bmesh

#Remakes of bpy.ops operators to avoid lag from scene updates.


def select_all_objs():
    for o in bpy.context.visible_objects:
        o.select_set(True)

def deselect_all_objs():
    for o in bpy.context.selected_objects:
        o.select_set(False)

def select_all_verts():
    old_mode = bpy.context.active_object.mode
    if old_mode is not 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    for v in bpy.context.active_object.vertices:
        v.select = True
    if old_mode is not 'OBJECT':
        bpy.ops.object.mode_set(mode=old_mode)

def deselect_all_verts():
    old_mode = bpy.context.active_object.mode
    if old_mode is not 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    for v in bpy.context.active_object.data.vertices:
        v.select = False
    if old_mode is not 'OBJECT':
        bpy.ops.object.mode_set(mode=old_mode)

def invert_selection():
    old_mode = bpy.context.active_object.mode
    if old_mode is not 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    for v in bpy.context.active_object.data.vertices:
        v.select = not v.select
    if old_mode is not 'OBJECT':
        bpy.ops.object.mode_set(mode=old_mode)

def vertex_group_select_by_threshold(obj, vg, thresh):
    old_mode = obj.mode
    if old_mode is not 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    for v in obj.data.vertices:
        for g in v.groups:
            if g.group == vg.index:
                if g.weight >= thresh:
                    v.select = True
                break
    if old_mode is not 'OBJECT':
        bpy.ops.object.mode_set(mode=old_mode)

def vertex_group_select(obj, vg):
    old_mode = obj.mode
    if old_mode is not 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    for v in obj.data.vertices:
        for g in v.groups:
            if g.group == vg.index:
                v.select = True
                break
    if old_mode is not 'OBJECT':
        bpy.ops.object.mode_set(mode=old_mode)