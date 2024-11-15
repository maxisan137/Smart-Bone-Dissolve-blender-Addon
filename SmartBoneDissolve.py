bl_info = {
    "name": "Smart Bone Dissolve",
    "author": "maxisan137",
    "version": (1, 0),
    "blender": (2, 92, 0),
    "location": "View3D > Armature",
    "description": "Dissolves bones and re-distributes their weights onto parent bones in any affectted meshes",
    "warning": "",
    "wiki_url": "",
    "category": "Armature"
}

import bpy
from bpy.types import (
    Operator
)

##################################################
# SMART BONE DISSOLVE BY MAXISAN137
#################################################
# This addon is aimed to ease the process of removing exsess bones from an already rigged mesh or collection of meshes
# Applying it to any number of selected armature bones will remove them and add their weights to any remaining parent bones weights
# This applies to all meshes that are parented to the selected armature and use it in an Armature modifier
#
# Once installed, the option will appear under the Armature menu in 3D View when in Armature Edit mode
##################################################

class ARMATURE_OT_smart_bone_dissolve(Operator):
    bl_label = "Smart Bone Dissolve"
    bl_idname = "armature.smart_bone_dissolve"
    bl_description = "Dissolves bones and re-distributes their weights onto parent bones in any affectted meshes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        
        # Capturing the selected object and checking if it's an Armature type
        sel_arm = bpy.context.active_object
        
        if sel_arm.type != "ARMATURE":
            print("Selected object is not an Armature type!")
            return {"FINISHED"}
        else:
            pass
        
        # Finding all child meshes of the selected Armature
        child_meshes = [child for child in sel_arm.children if child.type == "MESH"]
        if len(child_meshes) == 0:
            print("Selected Armature has no parented meshes")
        
        # Capturing the selected bones of the Armature
        bones_to_dissolve = [b.name for b in bpy.context.selected_bones]
        
        print("")
        print("----- BEGIN SMART BONE DISSOLVE -----")
        print("")
        print("Bones to dissolve:", "; ".join(bones_to_dissolve))
        print("")
        
        for bone_name in bones_to_dissolve:
            
            print("Dissolving bone", bone_name, "...")
            print("")
            
            bone = [b for b in sel_arm.data.edit_bones if b.name == bone_name][0]
            parent_bone_name = bone.parent.name
            
            for mesh in child_meshes:

                # Check if mesh has an armature modifier with the selected armature as object and if it has a vertex group named after the bone in question
                print("Examining mesh", mesh.name, "...")
                if True in [arm_mod.object == sel_arm for arm_mod in [mod for mod in mesh.modifiers if mod.type == "ARMATURE"]]:
                    print("Found armature modifier with the selected armature as object")
                    if bone_name in [vg.name for vg in mesh.vertex_groups]:
                        
                        print("Found vertex group corresponding to selected bone")
                        
                        mixmod = mesh.modifiers.new("SmartBoneMix", "VERTEX_WEIGHT_MIX")
                        # If the mesh does not have a vertex group for the parent bone, such group shall be created
                        if parent_bone_name not in [vg.name for vg in mesh.vertex_groups]:
                            print("No vertex group detected for parent bone", parent_bone_name, ", creating an empty vertex group")
                            mesh.vertex_groups.new(name = parent_bone_name)
                        # Setting up and mixing the weights
                        mixmod.vertex_group_a = parent_bone_name
                        mixmod.vertex_group_b = bone_name
                        mixmod.mix_set = "B"
                        mixmod.mix_mode = "ADD"
                        
                        # Exiting edit mode if currently in it
                        if sel_arm.mode == "EDIT":
                            bpy.ops.object.editmode_toggle()
                        # Setting the mesh to be active object
                        mesh.select_set(True)
                        bpy.context.view_layer.objects.active = mesh
                        # Applying the weight mix modifier
                        print("Applying weight mix modifier")
                        bpy.ops.object.modifier_apply(modifier=mixmod.name)
                        
                        # Deleting the redundant vertex group
                        print("Deleting vertex group", bone_name, "from mesh", mesh.name)
                        mesh.vertex_groups.remove(mesh.vertex_groups[bone_name])
                        
                        # Deselecting the mesh
                        mesh.select_set(False)
                        
                    else:
                        print("Corresponding vertex group not found")
                else:
                    print("No armature modifier found with the selected armature as object")
                
                print("")
                        
            # Selecting the armature and switching to Edit mode
            print("Selecting armature")
            bpy.context.view_layer.objects.active = sel_arm
            if bpy.context.active_object.mode != "EDIT":
                print("Switching to edit mode")
                bpy.ops.object.editmode_toggle()
            
            # Re-defining bone and parent because for some reason they are not recognised at this point anymore
            bone = [b for b in sel_arm.data.edit_bones if b.name == bone_name][0]
            parent_bone = bone.parent
            
            # Selecting the bone
            print("Selecting bone", bone_name)
            for b in sel_arm.data.edit_bones:
                b.select = False
                b.select_head = False
                b.select_tail = False
            bone.select = True
            bone.select_head = True
            bone.select_tail = True
                        
            # Memorizing the tail position of the bone if it is an only child
            new_tail_xyz = None
            print("Bone parent", parent_bone.name, "has a total of", len(parent_bone.children), "children")
            if len(parent_bone.children) == 1:
                new_tail_xyz = bone.tail.xyz
                print("Bone was found to be an only child. Tail coordinates:", new_tail_xyz)
                        
            # Deleting the bone
            print("Deleting bone", bone_name)
            sel_arm.data.edit_bones.remove(bone)
                        
            # Moving the parent bone tail if needed
            if new_tail_xyz is not None:
                print("Setting tail of parent bone", parent_bone.name, "to", new_tail_xyz)
                parent_bone.tail.xyz = new_tail_xyz
                
            print("")
        
        print("")
        print("----- FINISH SMART BONE DISSOLVE -----")
        print("")
            
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(ARMATURE_OT_smart_bone_dissolve.bl_idname)

def register():
    bpy.utils.register_class(ARMATURE_OT_smart_bone_dissolve)
    bpy.types.VIEW3D_MT_edit_armature.append(menu_func)

def unregister():
    bpy.utils.unregister_class(ARMATURE_OT_smart_bone_dissolve)
    bpy.types.VIEW3D_MT_armature.remove(menu_func)


if __name__ == "__main__":
        register()
