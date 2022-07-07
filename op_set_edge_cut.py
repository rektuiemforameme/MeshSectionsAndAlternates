import math
import bpy
from bpy.props import IntProperty, FloatProperty, EnumProperty
import bmesh
from . import util


class MESHSECTIONS_OT_mark_edge_cut(bpy.types.Operator):

    bl_idname = "mesh.mark_edge_cut"
    bl_label = "Mark Edge Cut"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Mark edges to be cut"


    def execute(self, context):

        if not self.is_invoked:        
            return self.invoke(context, None)

        obj_data = context.object.data
        bm = bmesh.from_edit_mesh(obj_data)

        cut_edge_layer = bm.edges.layers.int.get('cut_layer')
        if cut_edge_layer is None:
            cut_edge_layer = bm.edges.layers.int.new('cut_layer')

        mode = bpy.context.active_object.mode

        # we need to switch from Edit mode to Object mode so the selection gets updated
        #bpy.ops.object.mode_set(mode='OBJECT')
        selectedEdges = [e for e in bm.edges if e.select]
        
        for e in selectedEdges:
            e[cut_edge_layer] = 1
        
        bmesh.update_edit_mesh(obj_data)

        bpy.ops.object.mode_set(mode='OBJECT')
        # back to whatever mode we were in
        bpy.ops.object.mode_set(mode=mode)

        return {'FINISHED'}

    def invoke(self, context, event):
        # print("invoke")
        self.is_invoked = True
       
        return self.execute(context)


class MESHSECTIONS_OT_clear_edge_cut(bpy.types.Operator):

    bl_idname = "mesh.clear_edge_cut"
    bl_label = "Clear Edge Cut"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Unmark edges to be cut"


    def execute(self, context):

        if not self.is_invoked:
            return self.invoke(context, None)

        obj_data = context.object.data
        bm = bmesh.from_edit_mesh(obj_data)

        mode = bpy.context.active_object.mode

        # we need to switch from Edit mode to Object mode so the selection gets updated
        #bpy.ops.object.mode_set(mode='OBJECT')
        cut_edge_layer = bm.edges.layers.int.get('cut_layer')
        
        if cut_edge_layer is None:
            return
        
        selectedEdges = [e for e in bm.edges if e.select]

        for e in selectedEdges:
            e[cut_edge_layer] = 0

        bmesh.update_edit_mesh(obj_data)

        bpy.ops.object.mode_set(mode='OBJECT')
        # back to whatever mode we were in
        bpy.ops.object.mode_set(mode=mode)

        return {'FINISHED'}

    def invoke(self, context, event):
        # print("invoke")
        self.is_invoked = True

        return self.execute(context)


