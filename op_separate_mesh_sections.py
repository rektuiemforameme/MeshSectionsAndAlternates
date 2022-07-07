import math
import bpy
from bpy.props import IntProperty, FloatProperty, EnumProperty
import bmesh
import addon_utils
amfowsk_is_enabled, is_loaded = addon_utils.check('ApplyModifierForObjectWithShapeKeys')
if amfowsk_is_enabled:
    import ApplyModifierForObjectWithShapeKeys
from . import util

class MESHSECTIONS_OT_separate_mesh_sections(bpy.types.Operator):

    bl_idname = "mesh.separate_mesh_sections"
    bl_label = "Separate Mesh Sections"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Mark edges to be cut"

    def vertex_groups_overlap(self, vg1, vg2, obj):
        for v in obj.data.vertices:
            overlap1 = False
            overlap2 = False
            for g in v.groups:
                if g.group == vg1.index:
                    overlap1 = True
                elif g.group == vg2.index:
                    overlap2 = True
                if overlap1 and overlap2:
                    return True
        
        return False

    def vertex_groups_overlap_by_number(self, vg1, vg2, obj, num):
        c = 0
        for v in obj.data.vertices:
            overlap1 = False
            overlap2 = False
            for g in v.groups:
                if g.group == vg1.index:
                    overlap1 = True
                elif g.group == vg2.index:
                    overlap2 = True
                if overlap1 and overlap2:
                    c += 1

        return c >= num

    def delete_vertex_group_faces(self, context, obj, vg):
        util.deselect_all_obj()
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        past_mode = obj.mode
        bpy.ops.object.mode_set(mode='EDIT')
        util.deselect_all_verts()
        obj.vertex_groups.active_index = vg.index
        bpy.ops.object.vertex_group_select()
        bpy.ops.mesh.delete(type = 'FACE')
        bpy.ops.object.mode_set(mode=past_mode)

    def multiply_and_add_list(self, list_of_lists, list_to_add):
        new_list_of_lists = []
        for l1 in list_of_lists:
            new_list = l1.copy()
            new_list_of_lists.append(new_list)
            for l2 in list_to_add:
                new_list = l1.copy()
                new_list.append(l2)
                new_list_of_lists.append(new_list)

        return new_list_of_lists

    def clean_list_of_empty_lists(self, list_of_lists):
        new_l = []
        for l in list_of_lists:
            if len(l) > 0:
                new_l.append(l)
        return new_l

    def make_couples_of_vg_and_objs(self, vg, objs):
        l = []
        for o in objs:
            l_to_add = [vg, o]
            l.append(l_to_add)

        return l

    def get_new_object(self, context):
        objs = context.selected_objects
        for o in objs:
            if o is not context.active_object:
                return o
        return None
    
    def make_obj_from_vgroup_and_objs(self, context, base_obj, vg, other_vgobj_couples):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        base_obj.select_set(True)
        context.view_layer.objects.active = base_obj
        bpy.ops.object.duplicate_move()
        
        
        """
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        context.object.vertex_groups.active_index = vg.index
        bpy.ops.object.vertex_group_select()
        bpy.ops.mesh.duplicate_move()
        bpy.ops.mesh.separate(type='SELECTED')
        """
        
        new_object = context.view_layer.objects.active
        
        if new_object is None:
            return

        msStringSub = context.preferences.addons[__package__].preferences.section_vgroup_prefix
        name_addition = ""

        if other_vgobj_couples is not None and len(other_vgobj_couples) > 0:
            name_addition = ""
            bpy.ops.object.select_all(action='DESELECT')
            #Delete faces to be replaced by Alternate Parts
            for vgobj_couple in other_vgobj_couples:
                self.delete_vertex_group_faces(context, new_object, vgobj_couple[0])
            bpy.ops.object.select_all(action='DESELECT')
            for vgobj_couple in other_vgobj_couples:
                vgobj_couple[1].select_set(True)
                name_addition += "_" + vgobj_couple[1].name
            bpy.ops.object.duplicate_move()
            bpy.ops.object.select_all(action='DESELECT')

            for vgobj_couple in other_vgobj_couples:
                dup_obj = bpy.data.objects[vgobj_couple[1].name + ".001"]
                if dup_obj is not None:
                    dup_obj.select_set(True)

            new_object.select_set(True)
            context.view_layer.objects.active = new_object
            bpy.ops.object.join()
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            for vgobj_couple in other_vgobj_couples:
                new_object.vertex_groups.active_index = vgobj_couple[0].index
                bpy.ops.object.vertex_group_select()
            alt_merge_thresh = context.preferences.addons[__package__].preferences.alternate_merge_threshold
            bpy.ops.mesh.remove_doubles(threshold=alt_merge_thresh, use_unselected=False)
        
        apply_modifiers = context.preferences.addons[__package__].preferences.apply_modifiers
        amfowsk_is_enabled, amfowsk_is_loaded = addon_utils.check('ApplyModifierForObjectWithShapeKeys')
        if apply_modifiers and amfowsk_is_enabled and amfowsk_is_loaded:
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            new_object.select_set(True)
            context.view_layer.objects.active = new_object
            modifiers_to_apply = ['Mirror', 'Subdivision']
            for mod in modifiers_to_apply:
                ApplyModifierForObjectWithShapeKeys.applyModifierForObjectWithShapeKeys(context, mod, True)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        context.object.vertex_groups.active_index = vg.index
        bpy.ops.object.vertex_group_select()
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')

        new_object.name = vg.name[len(msStringSub):] + name_addition
        new_object.data.name = new_object.name

        

    def execute(self, context):
        if not self.is_invoked:        
            return self.invoke(context, None)

        base_obj = bpy.context.active_object
        mode = base_obj.mode

        bpy.ops.object.mode_set(mode='EDIT')

        msStringSub = context.preferences.addons[__package__].preferences.section_vgroup_prefix
        mpaStringSub = context.preferences.addons[__package__].preferences.alternate_vgroup_prefix
        msVGs = []
        mpaVGs = []
        
        vgs = context.object.vertex_groups
        vgNames = vgs.keys()

        for vgn in vgNames:
            if vgn[0:len(msStringSub)] == msStringSub:
                msVGs.append(vgs.get(vgn))
            elif vgn[0:len(mpaStringSub)] == mpaStringSub:
                mpaVGs.append(vgs.get(vgn))
        
        mpa_coll_name = context.preferences.addons[__package__].preferences.alternate_collection_name
        mpa_coll = bpy.data.collections.get(mpa_coll_name)

        vg_overlap_threshold = context.preferences.addons[__package__].preferences.vgroup_overlap_threshold
        
        for vg in msVGs:
            self.make_obj_from_vgroup_and_objs(context, base_obj, vg, None)

            if mpa_coll:
                mpavgs_to_combine = []
                for avg in mpaVGs:
                    if self.vertex_groups_overlap_by_number(vg, avg, base_obj, vg_overlap_threshold):
                        mpavgs_to_combine.append(avg)
                list_of_couple_combos = []
                for n in range(len(mpavgs_to_combine)):
                    current_vg = mpavgs_to_combine[n]
                    vg_coll = mpa_coll.children.get(current_vg.name[len(mpaStringSub):])
                    if vg_coll is not None:
                        vg_obj_couples = self.make_couples_of_vg_and_objs(current_vg, vg_coll.all_objects)
                        if n == 0:
                            list_of_couple_combos.append([])
                            for c in vg_obj_couples:
                                list_of_couple_combos.append([c])
                        else:
                            list_of_couple_combos = self.multiply_and_add_list(list_of_couple_combos, vg_obj_couples)
                
                list_of_couple_combos = self.clean_list_of_empty_lists(list_of_couple_combos)
                for couple_combos in list_of_couple_combos:
                    self.make_obj_from_vgroup_and_objs(context, base_obj, vg, couple_combos)

        #bpy.ops.object.mode_set(mode='EDIT')
        
        #bmesh.update_edit_mesh(obj_data)

        bpy.ops.object.mode_set(mode='OBJECT')
        # back to whatever mode we were in
        bpy.ops.object.mode_set(mode=mode)

        return {'FINISHED'}

    def invoke(self, context, event):
        # print("invoke")
        self.is_invoked = True
       
        return self.execute(context)

    
