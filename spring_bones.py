bl_info = {
    "name": "Spring Bones",
    "author": "Artell",
    "version": (0, 3),
    "blender": (2, 80, 0),
    "location": "Properties > Bones",
    "description": "Add a spring dynamic effect to a single/multiple bones",    
    "category": "Animation"}


import bpy
from bpy.app.handlers import persistent
from mathutils import *
import math


print('\n Start Spring Bones Addon... \n')


def set_active_object(object_name):
     bpy.context.view_layer.objects.active = bpy.data.objects[object_name]
     bpy.data.objects[object_name].select_set(state=1)

     
def get_pose_bone(name):  
    try:
        return bpy.context.object.pose.bones[name]
    except:
        return None
        
        
def spring_bone_frame_mode(foo):   
    if bpy.context.scene.global_spring_frame == True:
        spring_bone(foo)
    
    
def spring_bone(foo):
    #print("running...")
    scene = bpy.context.scene
    #point spring
    for bone in scene.spring_bones:        
        armature = bpy.data.objects[bone.armature]
        pose_bone = armature.pose.bones[bone.name]       
          
        emp_tail = bpy.data.objects.get(bone.name + '_spring_tail')        
        emp_head = bpy.data.objects.get(bone.name + '_spring')
        
        if emp_tail == None or emp_head == None:
            print("no empties found, return")
            return
        
        emp_tail_loc, rot, scale = emp_tail.matrix_world.decompose()
            
        dir = emp_tail_loc - emp_head.location
        bone.speed += dir
        bone.speed *= pose_bone.stiffness
        emp_head.location += bone.speed * pose_bone.damp
       
    return None
    

def update_bone(self, context):
    print("Updating data...")
    scene = bpy.context.scene
    
    armature = bpy.context.active_object  
    
    #update collection
        #delete all
    if len(scene.spring_bones) > 0:
        i = len(scene.spring_bones)
        while i >= 0:          
            scene.spring_bones.remove(i)
            i -= 1
            
        #add
    for bone in armature.pose.bones:
        if len(bone.keys()) == 0:            
            continue
        if not 'bone_spring' in bone.keys():
            continue
            
        if bone['bone_spring'] == False:
            spring_cns = bone.constraints.get("spring")
            if spring_cns:
                bone.constraints.remove(spring_cns)   
            continue
         
        item = scene.spring_bones.add()
        item.name = bone.name
        bone_tail = armature.matrix_world @ bone.tail 
        bone_head = armature.matrix_world @ bone.head 
        item.last_loc = bone_head
        item.armature = armature.name
        parent_name = bone.parent.name          
        rotation_enabled =  False
        if 'bone_rot' in bone.keys():
            if bone["bone_rot"]:
                rotation_enabled = True        
        item.bone_rot = rotation_enabled
        
        #create empty helpers
        if not bpy.data.objects.get(item.name + '_spring'):
            bpy.ops.object.mode_set(mode='OBJECT')       
            bpy.ops.object.select_all(action='DESELECT')
            if rotation_enabled:
                bpy.ops.object.empty_add(type='PLAIN_AXES', radius = 0.01, location=bone_tail, rotation=(0,0,0)) 
            else:
                bpy.ops.object.empty_add(type='PLAIN_AXES', radius = 0.01, location=bone_head, rotation=(0,0,0)) 
            empty = bpy.context.active_object   
            empty.hide_select = True
            empty.name = item.name + '_spring'
            
        if not bpy.data.objects.get(item.name + '_spring_tail'):
            bpy.ops.object.mode_set(mode='OBJECT')        
            bpy.ops.object.select_all(action='DESELECT')         
            if rotation_enabled:
                bpy.ops.object.empty_add(type='PLAIN_AXES', radius = 0.01, location=bone_tail, rotation=(0,0,0)) 
            else:
                bpy.ops.object.empty_add(type='PLAIN_AXES', radius = 0.01, location=bone_head, rotation=(0,0,0)) 
            empty = bpy.context.active_object    
            empty.hide_select = True
            mat = empty.matrix_world.copy()
            empty.name = item.name + '_spring_tail'                     
            empty.parent = armature
            empty.parent_type = 'BONE'
            empty.parent_bone = parent_name
            empty.matrix_world = mat#bpy.data.objects[item.name + '_spring'].matrix_world
            
        #create constraints
        if bone['bone_spring']:
            set_active_object(armature.name)
            bpy.ops.object.mode_set(mode='POSE')
            spring_cns = bone.constraints.get("spring")
            if spring_cns:
                bone.constraints.remove(spring_cns)                
            if bone.bone_rot:
                cns = bone.constraints.new('DAMPED_TRACK')
                cns.target = bpy.data.objects[item.name + '_spring']
            else:
                cns = bone.constraints.new('COPY_LOCATION')
                cns.target = bpy.data.objects[item.name + '_spring']                
            cns.name = 'spring' 
                  
        
    set_active_object(armature.name)
    bpy.ops.object.mode_set(mode='POSE')
 
    print("Updated.")


  
def end_spring_bone(context, self):
    if context.scene.global_spring:
        if self.timer_handler:   
            wm = context.window_manager
            wm.event_timer_remove(self.timer_handler)

        context.scene.global_spring = False
    
    for item in context.scene.spring_bones:
        
        active_bone = bpy.context.active_object.pose.bones.get(item.name)
        if active_bone == None:
            continue
            
        cns = active_bone.constraints.get('spring')
        if cns:            
            active_bone.constraints.remove(cns)  
               
        emp1 = bpy.data.objects.get(active_bone.name + '_spring')
        emp2 = bpy.data.objects.get(active_bone.name + '_spring_tail')
        if emp1:     
            bpy.data.objects.remove(emp1)        
        if emp2:        
            bpy.data.objects.remove(emp2)
    
    print("--End--")
    
class SB_OT_spring_modal(bpy.types.Operator):
    """Spring Bones, interactive mode"""
    
    bl_idname = "sb.spring_bone"
    bl_label = "spring_bone" 
    
    def __init__(self):
        self.timer_handler = None

    def modal(self, context, event):        
        if event.type == "ESC" or context.scene.global_spring == False:         
            end_spring_bone(context, self)
            return {'FINISHED'}  
            
        if event.type == 'TIMER':       
            spring_bone(context)
        
        return {'PASS_THROUGH'}
    
        
    def execute(self, context):     
        args = (self, context)  
        
        # enable spring bone
        if context.scene.global_spring == False:  
            wm = context.window_manager
            self.timer_handler = wm.event_timer_add(0.02, window=context.window)            
            wm.modal_handler_add(self)
            print("--Start modal--")
            
            context.scene.global_spring = True
            update_bone(self, context)
            
            return {'RUNNING_MODAL'}    
        
        # disable spring selection
        else:
            print("--End modal--")
            end_spring_bone(context, self)            
            return {'FINISHED'}  
            
            
class SB_OT_spring(bpy.types.Operator):
    """Spring Bones, animation mode. Support baking."""
    
    bl_idname = "sb.spring_bone_frame"
    bl_label = "spring_bone_frame" 

   
    def execute(self, context):        
        if context.scene.global_spring_frame == False:           
            context.scene.global_spring_frame = True
            update_bone(self, context)
 
        else:
            end_spring_bone(context, self)
            context.scene.global_spring_frame = False  
            
        return {'FINISHED'}  
            
            
###########  UI PANEL  ###################

class SB_PT_ui(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'bone'
    bl_label = "Spring Bones"    
    
    @classmethod
    def poll(cls, context):
        if context.active_object is not None:            
            if context.mode == 'POSE':
                if context.active_pose_bone is not None:
                    return True
        
    def draw(self, context):    
        layout = self.layout
        object = context.object
        active_bone = bpy.context.active_pose_bone
        scene = context.scene
        col = layout.column(align=True)
        
        col.label(text='Scene Parameters:')
        col = layout.column(align=True)
        #col.prop(scene, 'global_spring', text="Enable spring")
        if context.scene.global_spring == False:
            col.operator(SB_OT_spring_modal.bl_idname, text="Start", icon='PLAY')           
        if context.scene.global_spring == True:
            col.operator(SB_OT_spring_modal.bl_idname, text="Stop", icon='PAUSE')          
      
        col.enabled = not context.scene.global_spring_frame
      
        col = layout.column(align=True)
        if context.scene.global_spring_frame == False:          
            col.operator(SB_OT_spring.bl_idname, text="Start - Animation Mode", icon='PLAY')
        if context.scene.global_spring_frame == True:           
            col.operator(SB_OT_spring.bl_idname, text="Start - Animation Mode", icon='PAUSE')
            
        col.enabled = not context.scene.global_spring
        
        col = layout.column(align=True)
        
        col.label(text='Bone Parameters:')
        col.prop(active_bone, 'bone_spring', text="Enable Bone")
        col.prop(active_bone, 'bone_rot', text="Rotation")
        col.prop(active_bone, 'stiffness', text="Bouncy")
        col.prop(active_bone,'damp', text="Speed")
        
        
        
#### REGISTER ############# 

class bones_collec(bpy.types.PropertyGroup):
    armature : bpy.props.StringProperty(default="")
    last_loc : bpy.props.FloatVectorProperty(name="Loc", subtype='DIRECTION', default=(0,0,0), size = 3)    
    speed : bpy.props.FloatVectorProperty(name="Speed", subtype='DIRECTION', default=(0,0,0), size = 3)
    dist: bpy.props.FloatProperty(name="distance", default=1.0)
    target_offset : bpy.props.FloatVectorProperty(name="TargetLoc", subtype='DIRECTION', default=(0,0,0), size = 3)    
    bone_rot : bpy.props.BoolProperty(name="Bone Rot", default=False)
    matrix_offset = Matrix()
    initial_matrix = Matrix()
    
classes = (SB_PT_ui, bones_collec, SB_OT_spring_modal, SB_OT_spring)
        
def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)   
        
    bpy.app.handlers.frame_change_post.append(spring_bone_frame_mode)
    
    bpy.types.Scene.spring_bones = bpy.props.CollectionProperty(type=bones_collec)       
    bpy.types.Scene.global_spring = bpy.props.BoolProperty(name="Enable spring", default = False)#, update=update_global_spring)
    bpy.types.Scene.global_spring_frame = bpy.props.BoolProperty(name="Enable Spring", description="Enable Spring on frame change only", default = False)
    bpy.types.PoseBone.bone_spring = bpy.props.BoolProperty(name="Enabled", default=False, description="Enable this bone for spring")
    bpy.types.PoseBone.stiffness = bpy.props.FloatProperty(name="Stiffness", default=0.5, min = 0.01, max = 1.0)
    bpy.types.PoseBone.damp = bpy.props.FloatProperty(name="Damp", default=0.7, min=0.0, max = 10.0)    
    bpy.types.PoseBone.bone_rot = bpy.props.BoolProperty(name="Rotation", default=False, description="Enable spring rotation instead of location")
    
    
def unregister():
    from bpy.utils import unregister_class
    
    for cls in reversed(classes):
        unregister_class(cls)   
    
    bpy.app.handlers.frame_change_post.remove(spring_bone_frame_mode)  
    
    del bpy.types.Scene.global_spring
    del bpy.types.Scene.global_spring_frame
    del bpy.types.Scene.spring_bones    
    del bpy.types.PoseBone.stiffness
    del bpy.types.PoseBone.damp
    del bpy.types.PoseBone.bone_spring
    del bpy.types.PoseBone.bone_rot
    
    
if __name__ == "__main__":
    register()
    
