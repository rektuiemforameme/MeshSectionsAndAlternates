import bpy
from .functions import utilities
from .functions import validations
from bpy.types import (
    AddonPreferences
)


class MeshSectionsPreferences(bpy.types.AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    vertex_group_prefix: bpy.props.StringProperty(
        name="Vertex Group Prefix",
        default=r"MS_",
        description=(
            "Prefix for vertex groups to be used when creating meshes."
        )
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text='Vertex Group Prefix:')
        row = layout.row()
        row.prop(self, 'vertext_group_prefix', text="")
