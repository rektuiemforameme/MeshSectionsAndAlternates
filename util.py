#Copyright (c) 2022 Matt Thompson
#GNU General Public License version 3
#See the 'LICENSE' file for additional licensing details
import math
import bpy
import bmesh

#Remakes of some bpy.ops operators to avoid lag from scene updates.

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
    for v in bpy.context.active_object.data.vertices:
        v.select = True
    if old_mode is not 'OBJECT':
        bpy.ops.object.mode_set(mode=old_mode)

def deselect_all_verts():
    old_mode = bpy.context.active_object.mode
    if old_mode is not 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    for p in bpy.context.active_object.data.polygons:                   
        p.select=False               
    for e in bpy.context.active_object.data.edges:
        e.select=False
    for v in bpy.context.active_object.data.vertices:
        v.select = False
    if old_mode is not 'OBJECT':
        bpy.ops.object.mode_set(mode=old_mode)

def deselect_all_verts_bmesh(bm):
    for f in bm.faces:                   
        f.select_set(False)               
    for e in bm.edges:
        e.select_set(False)        
    for v in bm.verts:
        v.select_set(False)    

def invert_selection():
    old_mode = bpy.context.active_object.mode
    if old_mode is not 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    for v in bpy.context.active_object.data.vertices:
        v.select ^= True
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

def vertex_group_select_bmesh(bm, vg):
    bm.verts.layers.deform.verify()
    deform = bm.verts.layers.deform.active
    for v in bm.verts:
        g = v[deform]
        if vg.index in g and g[vg.index] > 0.5:
            v.select_set(True)

def bmesh_join(list_of_bmeshes, normal_update=False):
    """ takes as input a list of bm references and outputs a single merged bmesh 
    allows an additional 'normal_update=True' to force _normal_ calculations.
    """

    bm = bmesh.new()
    add_vert = bm.verts.new
    add_face = bm.faces.new
    add_edge = bm.edges.new

    for bm_to_add in list_of_bmeshes:
        offset = len(bm.verts)

        for v in bm_to_add.verts:
            add_vert(v.co)

        bm.verts.index_update()
        bm.verts.ensure_lookup_table()

        if bm_to_add.faces:
            for face in bm_to_add.faces:
                add_face(tuple(bm.verts[i.index+offset] for i in face.verts))
            bm.faces.index_update()

        if bm_to_add.edges:
            for edge in bm_to_add.edges:
                edge_seq = tuple(bm.verts[i.index+offset] for i in edge.verts)
                try:
                    add_edge(edge_seq)
                except ValueError:
                    # edge exists!
                    pass
            bm.edges.index_update()

    if normal_update:
        bm.normal_update()

    return bm