from bpy.types import (
    AddonPreferences
)
bl_info = {
    "name": "Modular Mesh Sections",
    "category": "Mesh",
    "author": "Matt Thompson",
    "description": "Duplicates mesh into defined subsections with alternates.",
    "version": (0, 0),
    "location": "Mesh > Edge > Generate Mesh Sections",
    "blender": (2, 93, 0),
    "tracker_url": "",
    "wiki_url": "" ,
}


if "bpy" in locals():
    import importlib

    importlib.reload(op_generate_mesh_sections)
else:

    from . import (
        op_generate_mesh_sections,
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
            "Prefix for vertex groups that indicate Mesh Sections"
        )
    )

    alternate_vgroup_prefix: bpy.props.StringProperty(
        name="Alternate Part Vertex Group Prefix",
        default=r"MPA_",
        description=(
            "Prefix for vertex groups that indicate Mesh Part Alternates"
        )
    )

    alternate_collection_name: bpy.props.StringProperty(
        name="Alternate Part Collection Name",
        default=r"MPA",
        description=(
            "The name of the collection that Mesh Part Alternates will use"
        )
    )

    name_spacer: bpy.props.StringProperty(
        name="Object Name Spacer",
        default=r"_",
        description=(
            """A substring that separates the base mesh name from the Mesh Section name from the Mesh Alternate Part name. 
            For example, a spacer of '_' will produce an object name of Base_Section_AlternateA_AlternateB, 
            while an empty spacer of '' will produce an object name of BaseSectionAlternateAAlternateB"""
        )
    )

    alternate_merge: bpy.props.BoolProperty(
        name="Merge Alternate Verts",
        default=True,
        description=(
            "Merge vertices of Mesh Part Alternate meshes after joined with parts"
        )
    )

    alternate_merge_threshold: bpy.props.FloatProperty(
        name="Alternate Part Merge Threshold",
        default=0.0001,
        description=(
            "Distance threshold for merging Mesh Part Alternate vertices"
        ),
        min=0
    )

    vgroup_overlap_threshold: bpy.props.IntProperty(
        name="Vertex Group Overlap Threshold",
        default=12,
        description=(
            "Threshold for number of vertices that have to overlap before two vertex groups are considered to be overlapping"
        ),
        min=0
    )

    object_separation: bpy.props.FloatProperty(
        name="Object Separation Distance",
        default=0,
        description=(
            "Distance between generated mesh objects"
        ),
        min=0
    )

    apply_modifiers: bpy.props.BoolProperty(
        name="Apply Modifiers",
        default=True,
        description=(
            "Whether or not modifiers should be applied when creating sections and alternates"
        )
    )

    apply_modifiers_blacklist: bpy.props.StringProperty(
        name="Apply Modifiers Blacklist",
        default=r"Armature",
        description=(
            "List of modifiers to not apply when creating alternates. Separate modifier names with commas. For example: 'Mirror,Armature,DataTransfer'"
        )
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column(heading="Naming")
        col.prop(self, 'section_vgroup_prefix')
        col.prop(self, 'alternate_vgroup_prefix')
        col.prop(self, 'alternate_collection_name')
        col.prop(self, 'name_spacer')
        col = layout.column(heading="Generation")
        col.prop(self, 'alternate_merge')
        row = col.row()
        row.enabled = context.preferences.addons[__package__].preferences.alternate_merge
        row.prop(self, 'alternate_merge_threshold')
        col.prop(self, 'object_separation')
        col = layout.column(heading="Section Detection")
        col.prop(self, 'vgroup_overlap_threshold')
        col = layout.column(heading="Modifier Handling")
        col.prop(self, 'apply_modifiers')
        row = col.row()
        row.enabled = context.preferences.addons[__package__].preferences.apply_modifiers
        row.prop(self, 'apply_modifiers_blacklist')


# stuff which needs to be registered in blender
classes = [
    op_generate_mesh_sections.MESHSECTIONS_OT_generate_mesh_sections,
    MeshSectionsPreferences,
]


@persistent
def scene_update_post_handler(dummy):
    pass

def menu_func(self, context):
    layout = self.layout
    layout.separator()

    layout.operator_context = "INVOKE_DEFAULT"


def menu_generate_sections(self, context):
    layout = self.layout
    layout.separator()

    layout.operator_context = "INVOKE_DEFAULT"

    layout.operator(op_generate_mesh_sections.MESHSECTIONS_OT_generate_mesh_sections.bl_idname, text='Generate Mesh Section Alternates')


def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.VIEW3D_MT_edit_mesh.append(menu_generate_sections)
    bpy.types.VIEW3D_MT_object.append(menu_generate_sections)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    bpy.types.VIEW3D_MT_edit_mesh.remove(menu_generate_sections)
    bpy.types.VIEW3D_MT_object.remove(menu_generate_sections)


