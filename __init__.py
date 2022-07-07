from bpy.types import (
    AddonPreferences
)
bl_info = {
    "name": "ModularMeshSections",
    "category": "Mesh",
    "author": "Matt Thompson",
    "description": "Duplicates mesh into defined subsections.",
    "version": (0, 0),
    "location": "Mesh > Edge > Create Modular Meshes",
    "blender": (2, 93, 0),
    "tracker_url": "",
    "wiki_url": "" ,
}


if "bpy" in locals():
    import importlib

    importlib.reload(op_separate_mesh_sections)
    #importlib.reload(properties)
    #importlib.reload(op_set_edge_cut)
    #importlib.reload(op_draw_cut_edges)
else:

    from . import (
        op_separate_mesh_sections,
        #properties
        #op_set_edge_cut,
        #op_draw_cut_edges,
    )

import bpy
from bpy.app.handlers import persistent


class MeshSectionsPreferences(bpy.types.AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    section_vgroup_prefix: bpy.props.StringProperty(
        name="Section Vertex Group Prefix",
        default=r"MS_",
        description=(
            "Prefix for vertex groups that indicate Mesh Sections."
        )
    )

    alternate_vgroup_prefix: bpy.props.StringProperty(
        name="Alternate Part Vertex Group Prefix",
        default=r"MPA_",
        description=(
            "Prefix for vertex groups that indicate Mesh Part Alternates."
        )
    )

    alternate_merge_threshold: bpy.props.FloatProperty(
        name="Alternate Part Merge Threshold",
        default=0.0001,
        description=(
            "Distance threshold for merging Mesh Part Alternates."
        )
    )

    alternate_collection_name: bpy.props.StringProperty(
        name="Alternate Part Collection Name",
        default=r"MPA",
        description=(
            "The name of the collection that mesh part alternates will use."
        )
    )

    vgroup_overlap_threshold: bpy.props.IntProperty(
        name="Vertex Group Overlap Threshold",
        default=12,
        description=(
            "Threshold for number of vertices that have to overlap before two Vertex Groups are considered to be overlapping."
        )
    )

    apply_modifiers: bpy.props.BoolProperty(
        name="Apply Modifiers",
        default=True,
        description=(
            "Whether or not modifiers should be applied when creating sections and alternates."
        )
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text='Section Vertex Group Prefix:')
        row = layout.row()
        row.prop(self, 'section_vgroup_prefix', text="")
        layout.label(text='Alternate Part Vertex Group Prefix:')
        row = layout.row()
        row.prop(self, 'alternate_vgroup_prefix', text="")
        layout.label(text='Alternate Part Merge Threshold:')
        row.prop(self, 'alternate_merge_threshold', text="")
        layout.label(text='Alternate Part Collection Name:')
        row = layout.row()
        row.prop(self, 'alternate_collection_name', text="")
        layout.label(text='Vertex Group Overlap Threshold:')
        row = layout.row()
        row.prop(self, 'vgroup_overlap_threshold', text="")
        layout.label(text='Apply Modifiers:')
        row = layout.row()
        row.prop(self, 'apply_modifiers', text="")


# stuff which needs to be registered in blender
classes = [
    op_separate_mesh_sections.MESHSECTIONS_OT_separate_mesh_sections,
    MeshSectionsPreferences,
    #op_set_edge_cut.MESHSECTIONS_OT_mark_edge_cut,
    #op_set_edge_cut.MESHSECTIONS_OT_clear_edge_cut,
    #op_draw_cut_edges.MESHSECTIONS_PT_show_edge_cuts
]


@persistent
def scene_update_post_handler(dummy):
    pass

def menu_func(self, context):
    layout = self.layout
    layout.separator()

    layout.operator_context = "INVOKE_DEFAULT"

    #layout.operator(op_set_edge_cut.MESHSECTIONS_OT_mark_edge_cut.bl_idname, text='Mark Cut')
    #layout.operator(op_set_edge_cut.MESHSECTIONS_OT_clear_edge_cut.bl_idname, text='Clear Cut')


def menu_separate_sections(self, context):
    layout = self.layout
    layout.separator()

    layout.operator_context = "INVOKE_DEFAULT"

    layout.operator(op_separate_mesh_sections.MESHSECTIONS_OT_separate_mesh_sections.bl_idname, text='Separate Mesh Sections')


def register():
    for c in classes:
        bpy.utils.register_class(c)
    
    #bpy.types.VIEW3D_MT_edit_mesh_edges.append(menu_func)
    #bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(menu_func)

    bpy.types.VIEW3D_MT_edit_mesh.append(menu_separate_sections)
    bpy.types.VIEW3D_MT_object.append(menu_separate_sections)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    #bpy.types.VIEW3D_MT_edit_mesh_edges.remove(menu_func)
    #bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(menu_func)

    bpy.types.VIEW3D_MT_edit_mesh.remove(menu_separate_sections)
    bpy.types.VIEW3D_MT_object.remove(menu_separate_sections)


