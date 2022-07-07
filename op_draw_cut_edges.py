import bpy
import bgl
import blf
import gpu
from gpu_extras.batch import batch_for_shader
import bmesh
import mathutils

cut_verts = []
shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
batch = batch_for_shader(shader, 'LINES', {"pos": cut_verts})


def draw_lines():
    if bpy.context.scene.show_edge_cuts and bpy.context.active_object is not None and bpy.context.active_object.mode == 'EDIT':
        cut_verts = []
        obj_data = bpy.context.object.data
        #bm = bmesh.from_edit_mesh(obj_data)
        bm = bmesh.new()
        bm.from_object(bpy.context.object, bpy.context.evaluated_depsgraph_get())

        cut_edge_layer = bm.edges.layers.int.get('cut_layer')
        if cut_edge_layer is None:
            return
        
        viewForwardV = mathutils.Vector((0.0, 0.0, -1.0))
        viewForwardV.rotate(bpy.context.region_data.view_rotation)

        for e in bm.edges:
            
            if e[cut_edge_layer] and (viewForwardV.dot(e.verts[0].normal) < 0 or viewForwardV.dot(e.verts[1].normal) < 0):
                cut_verts.append((e.verts[0].co.x, e.verts[0].co.y, e.verts[0].co.z))
                cut_verts.append((e.verts[1].co.x, e.verts[1].co.y, e.verts[1].co.z))
        
        batch = batch_for_shader(shader, 'LINES', {"pos": cut_verts})
        bgl.glLineWidth(7)
        bgl.glEnable(bgl.GL_BLEND)
        shader.bind()
        shader.uniform_float("color", (1, 1, 1, 0.2))
        batch.draw(shader)
        bgl.glLineWidth(1)


bpy.types.SpaceView3D.draw_handler_add(draw_lines, (), 'WINDOW', 'POST_VIEW')

   


class MESHSECTIONS_PT_show_edge_cuts(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_parent_id = 'VIEW3D_PT_overlay_edit_mesh'
    bl_label = "Modular Mesh Cuts"

    bpy.types.Scene.show_edge_cuts = bpy.props.BoolProperty(
        name="Show Edge Cuts",
        description="Show edge cuts for modular mesh sections",
        default=True
    )

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def draw(self, context):
        layout = self.layout

        view = context.space_data
        overlay = view.overlay
        display_all = overlay.show_overlays

        col = layout.column()
        col.active = display_all

        row = col.row(align=True)
        row.prop(context.scene, "show_edge_cuts", text="Show Cuts")
