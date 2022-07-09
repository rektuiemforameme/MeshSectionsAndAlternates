import math
import bpy
from bpy.props import IntProperty, FloatProperty, EnumProperty
import bmesh
import addon_utils
amfowsk_is_enabled, is_loaded = addon_utils.check('ApplyModifierForObjectWithShapeKeys')
if amfowsk_is_enabled:
    import ApplyModifierForObjectWithShapeKeys
from . import util

class MESHSECTIONS_OT_generate_mesh_sections(bpy.types.Operator):

    bl_idname = "mesh.generate_mesh_sections"
    bl_label = "Generate Mesh Sections"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Generate mesh sections and alternates"

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
                    if c >= num:
                        return True
        return False

    def delete_vertex_group_faces(self, context, obj, vg):
        util.deselect_all_objs()
        obj.select_set(True)
        context.view_layer.objects.active = obj
        util.deselect_all_verts()
        obj.vertex_groups.active_index = vg.index
        util.vertex_group_select(obj,vg)
        past_mode = obj.mode
        bpy.ops.object.mode_set(mode='EDIT')
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
            l.append([vg, o])
        return l

    def get_new_object(self, context):
        objs = context.selected_objects
        for o in objs:
            if o is not context.active_object:
                return o
        return None
    
    def make_obj_from_vgroup_and_objs(self, context, base_obj, vg, other_vgobj_couples):
        if context.active_object.mode is not 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        util.deselect_all_objs()
        target_coll = base_obj.users_collection[0]
        #Create the obj for this section
        new_object = base_obj.copy()
        new_object.data = new_object.data.copy()
        target_coll.objects.link(new_object)
        
        if new_object is None:
            return

        msStringSub = context.preferences.addons[__package__].preferences.section_vgroup_prefix
        name_mpa_addition = ""          #The string to add onto the end of the mesh's name to specify which alternates are in the current mesh
        name_spacer = context.preferences.addons[__package__].preferences.name_spacer
        #If there are alternates to be joined, handle them
        if other_vgobj_couples is not None and len(other_vgobj_couples) > 0:
            util.deselect_all_objs()
            #Delete faces to be replaced by Alternate Parts
            for vgobj_couple in other_vgobj_couples:
                self.delete_vertex_group_faces(context, new_object, vgobj_couple[0])
            util.deselect_all_objs()
            #Select all desired Mesh Part Alternate meshes, duplicate them and merge them with the new base mesh
            for vgobj_couple in other_vgobj_couples:
                if vgobj_couple[1] is not None:
                    mpa_copy = vgobj_couple[1].copy()
                    mpa_copy.data = mpa_copy.data.copy()
                    target_coll.objects.link(mpa_copy)
                    mpa_copy.select_set(True)
                    name_mpa_addition += name_spacer + vgobj_couple[1].name
            new_object.select_set(True)
            context.view_layer.objects.active = new_object
            bpy.ops.object.join()
            #Merge vertices of Mesh Part Alternates so that they will form one mesh if close enough
            if context.preferences.addons[__package__].preferences.alternate_merge:
                util.deselect_all_verts()
                for vgobj_couple in other_vgobj_couples:    #Select the vertex groups to be merged
                    util.vertex_group_select(new_object,vgobj_couple[0])
                bpy.ops.object.mode_set(mode='EDIT')
                alt_merge_thresh = context.preferences.addons[__package__].preferences.alternate_merge_threshold
                bpy.ops.mesh.remove_doubles(threshold=alt_merge_thresh, use_unselected=False)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        util.deselect_all_objs()
        new_object.select_set(True)
        context.view_layer.objects.active = new_object
        #Try to apply modifiers that aren't in the blacklist if desired
        if context.preferences.addons[__package__].preferences.apply_modifiers and new_object.modifiers:
            modifiers_to_apply = [x for x in base_obj.modifiers.keys() if x not in set(context.preferences.addons[__package__].preferences.apply_modifiers_blacklist.split(","))]
            if new_object.data.shape_keys:  #If the mesh has shape keys, check for the AMFOWSK plugin and use it to apply the modifiers if available
                amfowsk_is_enabled, amfowsk_is_loaded = addon_utils.check('ApplyModifierForObjectWithShapeKeys')
                if amfowsk_is_enabled and amfowsk_is_loaded:
                    ApplyModifierForObjectWithShapeKeys.applyModifierForObjectWithShapeKeys(context, modifiers_to_apply, True)
            else:
                for mod in modifiers_to_apply:
                    bpy.ops.object.modifier_apply(modifier=mod)
        #Delete all vertices that aren't in the current Mesh Section vertex group
        util.deselect_all_verts()
        util.vertex_group_select_by_threshold(new_object,vg,0.99)
        util.invert_selection()
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='VERT')                    
        bpy.ops.object.mode_set(mode='OBJECT')
        #Give the new object and its mesh a new name determined by the section it's based on and the alternates used in it
        new_object.name = base_obj.name + name_spacer + vg.name[len(msStringSub):] + name_mpa_addition
        new_object.data.name = new_object.name
        return new_object

        

    def execute(self, context):
        if not self.is_invoked:        
            return self.invoke(context, None)
        #The object that we will base all sections and alternates off of
        base_obj = bpy.context.active_object
        mode = base_obj.mode
        #Mesh Section Prefix
        msStringSub = context.preferences.addons[__package__].preferences.section_vgroup_prefix
        #Mesh Part Alternate Prefix
        mpaStringSub = context.preferences.addons[__package__].preferences.alternate_vgroup_prefix
        msVGs = []      #List of Mesh Section Vertex Groups
        mpaVGs = []     #List of Mesh Part Alternate Vertex Groups
        
        vgs = context.object.vertex_groups
        vgNames = vgs.keys()
        #Fill both lists
        for vgn in vgNames:
            if len(vgn) >= len(msStringSub) and vgn[0:len(msStringSub)] == msStringSub:
                msVGs.append(vgs.get(vgn))
            elif len(vgn) >= len(mpaStringSub) and vgn[0:len(mpaStringSub)] == mpaStringSub:
                mpaVGs.append(vgs.get(vgn))
        #Name of the collection that contains the Mesh Part Alternates
        mpa_coll_name = context.preferences.addons[__package__].preferences.alternate_collection_name
        mpa_coll = bpy.data.collections.get(mpa_coll_name)
        #Number of overlapping vertices before two vertex groups are considered overlapping
        vg_overlap_threshold = context.preferences.addons[__package__].preferences.vgroup_overlap_threshold
        #Distance between objects that get generated. Default to 0, but it's nice to have some number for viewing
        object_separation = context.preferences.addons[__package__].preferences.object_separation
        section_num = 1         #Keeps track of the current section that we're working on
        new_objs = []
        for vg in msVGs:        #For each Mesh Section
            section_obj = self.make_obj_from_vgroup_and_objs(context, base_obj, vg, None)                     #Create the base Mesh Section mesh without any Alternates
            section_obj.location.x += section_num * object_separation
            new_objs.append(section_obj)
            if mpa_coll:
                mpavgs_to_combine = []                      #List of Mesh Part Alternates that are part of the current Mesh Section
                for avg in mpaVGs:
                    if self.vertex_groups_overlap_by_number(vg, avg, base_obj, vg_overlap_threshold):
                        mpavgs_to_combine.append(avg)       #Fill the list
                list_of_couple_combos = []                  #List of all valid combinations of each Mesh Part Alternate in the current Mesh Section, including combinations where none of a certain alternate type are used
                for n in range(len(mpavgs_to_combine)):     #For each Mesh Part Alternate that is part of the current Mesh Section
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
                
                list_of_couple_combos = self.clean_list_of_empty_lists(list_of_couple_combos)   #Remove empty combinations that got added        
                alternate_num = 1       #Keeps track of the current alternate combo that we're working on
                for couple_combos in list_of_couple_combos:
                    alternate_obj = self.make_obj_from_vgroup_and_objs(context, base_obj, vg, couple_combos)    #Create a Mesh Section mesh with this combination of Mesh Part Alternates
                    alternate_obj.location.x += section_num * object_separation
                    alternate_obj.location.y += alternate_num * object_separation
                    new_objs.append(alternate_obj)
                    alternate_num += 1
            section_num += 1
        bpy.ops.object.mode_set(mode='OBJECT')
        for obj in new_objs:
            obj.select_set(True)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.is_invoked = True
       
        return self.execute(context)

    
