bl_info = {
    "name": "Spring Bones",
    "author": "Artell",
    "version": (0, 1),
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

def spring_bone():
    scene = bpy.context.scene
    #point spring
    for bone in scene.spring_bones:        
        armature = bpy.data.objects[bone.armature]
        pose_bone = armature.pose.bones[bone.name]       
        head = pose_bone.head
        arm_mat = armature.matrix_world      
        head = arm_mat @ head
        
        emp1 = bpy.data.objects.get(bone.name + '_spring_tail')        
        emp2 = bpy.data.objects.get(bone.name + '_spring')
        
        if emp1 == None or emp2 == None:
            print("no empties found, return")
            return
        
        emp1_loc, rot, scale = emp1.matrix_world.decompose()
        
        if bone.last_loc == (0,0,0):
            bone.last_loc = head
                    
        head_dir = (head - bone.last_loc)       
       
        bone.last_loc = head  

        dir = emp1_loc - emp2.location
        bone.speed += dir
        bone.speed *= pose_bone.stiffness
        emp2.location += bone.speed * pose_bone.damp
        """
        if head_dir.magnitude != 0.0:            
            bone.speed = (emp1_loc -emp2.location)* pose_bone.damp
            emp2.location += bone.speed   
        else:
            dir = emp1_loc - emp2.location
            bone.speed += dir
            bone.speed *= pose_bone.stiffness
            emp2.location += bone.speed * pose_bone.damp
        """
        print("evaluating")
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
        if len(bone.keys()) > 0:
            if 'bone_spring' in bone.keys():
                if bone['bone_spring']:
                    item = scene.spring_bones.add()
                    item.name = bone.name
                    #bone_tail = armature.matrix_world @ bone.tail 
                    bone_head = armature.matrix_world @ bone.head 
                    item.last_loc = bone_head
                    item.armature = armature.name
                    parent_name = bone.parent.name          

                    #create empty helpers
                    if not bpy.data.objects.get(item.name + '_spring'):
                        bpy.ops.object.mode_set(mode='OBJECT') 
                        print("create", item.name + '_spring')
                        bpy.ops.object.select_all(action='DESELECT')
                        bpy.ops.object.empty_add(type='PLAIN_AXES', radius = 0.01, location=bone_head, rotation=(0,0,0)) 
                        empty = bpy.context.active_object            
                        empty.name = item.name + '_spring'
                        
                    if not bpy.data.objects.get(item.name + '_spring_tail'):
                        bpy.ops.object.mode_set(mode='OBJECT') 
                        print("create", item.name + '_spring_tail')
                        bpy.ops.object.select_all(action='DESELECT')
                        bpy.ops.object.empty_add(type='PLAIN_AXES', radius = 0.01, location=bone_head, rotation=(0,0,0))
                        empty = bpy.context.active_object    
                        empty.name = item.name + '_spring_tail'                     
                        empty.parent = armature
                        empty.parent_type = 'BONE'
                        empty.parent_bone = parent_name
                        empty.matrix_world = bpy.data.objects[item.name + '_spring'].matrix_world
                        
                    #create constraints
                    set_active_object(armature.name)
                    bpy.ops.object.mode_set(mode='POSE')
                    if bone.constraints.get('spring') == None:
                        #cns = bone.constraints.new('DAMPED_TRACK')
                        cns = bone.constraints.new('COPY_LOCATION')
                        cns.target = bpy.data.objects[item.name + '_spring']                
                        cns.name = 'spring' 
                  
    print('Bones Collection:')
    for i, item in enumerate(scene.spring_bones):
        print(item.name)
        
    set_active_object(armature.name)
    bpy.ops.object.mode_set(mode='POSE')
 
    print("Updated.")
    
    
def end_spring_bone(context, self):
    if self.timer_handler:   
        wm = context.window_manager
        wm.event_timer_remove(self.timer_handler)

    context.scene.global_spring = False
    
    for item in context.scene.spring_bones:
        print(item.name)
        
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
    
    print("--End modal--")
    
class SB_OT_spring_modal(bpy.types.Operator):
    """Spring Bones"""
    
    bl_idname = "sb.spring_bone"
    bl_label = "spring_bone" 
    
    def __init__(self):
        self.timer_handler = None

    def modal(self, context, event):        
        if event.type == "ESC":         
            end_spring_bone(context, self)
            return {'FINISHED'}  
            
        if event.type == 'TIMER':
            print("spring bones...")
            spring_bone()
        
        return {'PASS_THROUGH'}
    
        
    def execute(self, context):     
        args = (self, context)  
        
        # enable skin selection
        if context.scene.global_spring == False:  
            wm = context.window_manager
            self.timer_handler = wm.event_timer_add(0.02, window=context.window)            
            wm.modal_handler_add(self)
            print("--Start modal--")
            
            context.scene.global_spring = True
            update_bone(self, context)
            
            return {'RUNNING_MODAL'}    
        
        # disable skin selection
        else:
            print("--End modal--")
            context.scene.global_spring = False
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
            col.operator(SB_OT_spring_modal.bl_idname, text="Start", icon='PAUSE')
        col = layout.column(align=True)
        
        col.label(text='Bone Parameters:')
        col.prop(active_bone, 'bone_spring', text="Enable Bone")
        col.prop(active_bone, 'stiffness', text="Bouncy")
        col.prop(active_bone,'damp', text="Speed")
        
        
#### REGISTER ############# 

class bones_collec(bpy.types.PropertyGroup):
    armature : bpy.props.StringProperty(default="")
    last_loc : bpy.props.FloatVectorProperty(name="Loc", subtype='DIRECTION', default=(0,0,0), size = 3)    
    speed : bpy.props.FloatVectorProperty(name="Speed", subtype='DIRECTION', default=(0,0,0), size = 3)
    dist: bpy.props.FloatProperty(name="distance", default=1.0)
    target_offset : bpy.props.FloatVectorProperty(name="TargetLoc", subtype='DIRECTION', default=(0,0,0), size = 3)    
    matrix_offset = Matrix()
    initial_matrix = Matrix()
    
classes = (SB_PT_ui, bones_collec, SB_OT_spring_modal)
        
def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)   
        
    #bpy.app.handlers.depsgraph_update_post.append(spring)
    
    bpy.types.Scene.spring_bones = bpy.props.CollectionProperty(type=bones_collec)  
    bpy.types.Scene.global_spring = bpy.props.BoolProperty(name="Enable spring", default = False)#, update=update_global_spring)     
    bpy.types.PoseBone.bone_spring = bpy.props.BoolProperty(name="Enabled", default=False, description="Enable this bone for spring", update=update_bone)
    bpy.types.PoseBone.stiffness = bpy.props.FloatProperty(name="Stiffness", default=0.5, min = 0.01, max = 1.0)
    bpy.types.PoseBone.damp = bpy.props.FloatProperty(name="Damp", default=0.7, min=0.0, max = 1.0)    

    
def unregister():
    from bpy.utils import unregister_class
    
    for cls in reversed(classes):
        unregister_class(cls)   
    
    #bpy.app.handlers.depsgraph_update_post.remove(spring)  
    
    del bpy.types.Scene.global_spring
    del bpy.types.Scene.spring_bones    
    del bpy.types.PoseBone.stiffness
    del bpy.types.PoseBone.damp
    del bpy.types.PoseBone.bone_spring
    
    
if __name__ == "__main__":
    register()
    
