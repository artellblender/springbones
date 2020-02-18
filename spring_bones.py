bl_info = {
    "name": "Spring Bones",
    "author": "Artell",
    "version": (0, 6),
    "blender": (2, 80, 0),
    "location": "Properties > Bones",
    "description": "Add a spring dynamic effect to a single/multiple bones",    
    "category": "Animation"}


import bpy
from bpy.app.handlers import persistent
from mathutils import *
import math
#from mathutils import Vector

                                          

#print('\n Start Spring Bones Addon... \n')


def set_active_object(object_name):
     bpy.context.view_layer.objects.active = bpy.data.objects[object_name]
     bpy.data.objects[object_name].select_set(state=1)

     
def get_pose_bone(name):  
    try:
        return bpy.context.object.pose.bones[name]
    except:
        return None
        
@persistent        
def spring_bone_frame_mode(foo):   
    if bpy.context.scene.sb_global_spring_frame == True:
        spring_bone(foo)
 
def lerp_vec(vec_a, vec_b, t):                        
    return vec_a*t + vec_b*(1-t)
                             
    
def spring_bone(foo):
    #print("running...")
    scene = bpy.context.scene    
    #point spring
    for bone in scene.sb_spring_bones:   
        if bone.sb_bone_collider == True:
            continue
        armature = bpy.data.objects[bone.armature]
        pose_bone = armature.pose.bones[bone.name]       
          
        emp_tail = bpy.data.objects.get(bone.name + '_spring_tail')        
        emp_head = bpy.data.objects.get(bone.name + '_spring')
        
        if emp_tail == None or emp_head == None:
            #print("no empties found, return")
            return
                       
        emp_tail_loc, rot, scale = emp_tail.matrix_world.decompose()

        # spring   
        """
        dir = emp_tail_loc - emp_head.location
        bone.speed += dir
        bone.speed *= pose_bone.sb_stiffness           
        emp_head.location += bone.speed * pose_bone.sb_damp
        """
        
        # colliders
        axis_locked = None
        
        if 'sb_lock_axis' in pose_bone.keys():
            axis_locked = pose_bone.sb_lock_axis
            #print("axis locked", axis_locked)
        # add gravity
        base_pos_dir = Vector((0,0,-pose_bone.sb_gravity))
        
        # add spring
        base_pos_dir += (emp_tail_loc - emp_head.location)
        
        for bone_col in scene.sb_spring_bones:
            
            if bone_col.sb_bone_collider == False:
                continue
            
            pose_bone_col = armature.pose.bones[bone_col.name]   
            sb_collider_dist = pose_bone_col.sb_collider_dist
            #col_dir = (pose_bone.head - pose_bone_col.head)
            pose_bone_center = (pose_bone.tail + pose_bone.head)*0.5
            p = project_point_onto_line(pose_bone_col.head, pose_bone_col.tail, pose_bone_center)
            col_dir = (pose_bone_center - p)
            dist = col_dir.magnitude
            
            if dist < sb_collider_dist:   
                push_vec = col_dir.normalized() * (sb_collider_dist-dist)*pose_bone_col.sb_collider_force
                if axis_locked != "NONE" and axis_locked != None:                    
                    if axis_locked == "+Y":                        
                        direction_check = pose_bone.y_axis.normalized().dot(push_vec)                      
                        if direction_check > 0:                        
                            locked_vec = project_point_onto_plane(push_vec, pose_bone.z_axis, pose_bone.y_axis)
                            push_vec = lerp_vec(push_vec, locked_vec, 0.3)
                            
                    elif axis_locked == "-Y":                        
                        direction_check = pose_bone.y_axis.normalized().dot(push_vec)                      
                        if direction_check < 0:                        
                            locked_vec = project_point_onto_plane(push_vec, pose_bone.z_axis, pose_bone.y_axis)
                            push_vec = lerp_vec(push_vec, locked_vec, 0.3)
                            
                    elif axis_locked == "+X":                        
                        direction_check = pose_bone.x_axis.normalized().dot(push_vec)                      
                        if direction_check > 0:                        
                            locked_vec = project_point_onto_plane(push_vec, pose_bone.y_axis, pose_bone.x_axis)
                            push_vec = lerp_vec(push_vec, locked_vec, 0.3)
                            
                    elif axis_locked == "-X":                        
                        direction_check = pose_bone.x_axis.normalized().dot(push_vec)                      
                        if direction_check < 0:                        
                            locked_vec = project_point_onto_plane(push_vec, pose_bone.y_axis, pose_bone.x_axis)
                            push_vec = lerp_vec(push_vec, locked_vec, 0.3)
                            
                    elif axis_locked == "+Z":                        
                        direction_check = pose_bone.z_axis.normalized().dot(push_vec)                      
                        if direction_check > 0:                        
                            locked_vec = project_point_onto_plane(push_vec, pose_bone.z_axis, pose_bone.x_axis)
                            push_vec = lerp_vec(push_vec, locked_vec, 0.3)
                            
                    elif axis_locked == "-Z":                        
                        direction_check = pose_bone.z_axis.normalized().dot(push_vec)                      
                        if direction_check < 0:                        
                            locked_vec = project_point_onto_plane(push_vec, pose_bone.z_axis, pose_bone.x_axis)
                            push_vec = lerp_vec(push_vec, locked_vec, 0.3)
                            
                #push_vec = push_vec - pose_bone.y_axis.normalized()*0.02
                base_pos_dir += push_vec
           
            
                                  
                                                                    
        
        bone.speed += base_pos_dir * pose_bone.sb_stiffness
        bone.speed *= pose_bone.sb_damp
        
        emp_head.location += bone.speed
                    
            
            
    return None

    
    
def project_point_onto_plane(q, p, n):
    # q = (vector) point
    # p = (vector) belonging to the plane
    # n = (vector) normal of the plane
    
    n = n.normalized()
    return q - ((q-p).dot(n)) * n 
    
def project_point_onto_line(a, b, p):
    # project the point p onto the line a,b
    ap = p-a
    ab = b-a
    
    fac_a = (p-a).dot(b-a)
    fac_b = (p-b).dot(b-a)
    
    result = a + ap.dot(ab)/ab.dot(ab) * ab
    
    if fac_a < 0:
        result = a
    if fac_b > 0:
        result = b
    
    return result
    
                    
def update_bone(self, context):
    print("Updating data...")
    
    scene = bpy.context.scene    
    armature = bpy.context.active_object  
    
    #update collection
        #delete all
    if len(scene.sb_spring_bones) > 0:
        i = len(scene.sb_spring_bones)
        while i >= 0:          
            scene.sb_spring_bones.remove(i)
            i -= 1
            
        #add
    for bone in armature.pose.bones:
        if len(bone.keys()) == 0:            
            continue
        if not 'sb_bone_spring' in bone.keys() and not 'sb_bone_collider' in bone.keys():
            continue
        
        if 'sb_bone_spring' in bone.keys():
            if bone['sb_bone_spring'] == False:
                spring_cns = bone.constraints.get("spring")
                if spring_cns:
                    bone.constraints.remove(spring_cns)   
            
            if 'sb_bone_collider' in bone.keys():
                if bone['sb_bone_spring'] == False and bone['sb_bone_collider'] == False:        
                    continue
         
        item = scene.sb_spring_bones.add()
        item.name = bone.name
        bone_tail = armature.matrix_world @ bone.tail 
        bone_head = armature.matrix_world @ bone.head 
        item.last_loc = bone_head
        item.armature = armature.name
        parent_name = ""
        if bone.parent:
            parent_name = bone.parent.name          
        rotation_enabled =  False
        collider_enabled = False
        if 'sb_bone_rot' in bone.keys():
            if bone["sb_bone_rot"]:
                rotation_enabled = True 
        if 'sb_bone_collider' in bone.keys():
            if bone["sb_bone_collider"]:
                collider_enabled = True
       
        item.sb_bone_rot = rotation_enabled
        item.sb_bone_collider = collider_enabled
       
        #create empty helpers
        if not collider_enabled:
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
            if bone['sb_bone_spring']:
                set_active_object(armature.name)
                bpy.ops.object.mode_set(mode='POSE')
                spring_cns = bone.constraints.get("spring")
                if spring_cns:
                    bone.constraints.remove(spring_cns)                
                if bone.sb_bone_rot:
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
    if context.scene.sb_global_spring:
        #print("GOING TO CLOSE TIMER...")        
        wm = context.window_manager
        wm.event_timer_remove(self.timer_handler)
        #print("CLOSE TIMER")
      
        context.scene.sb_global_spring = False
    
    for item in context.scene.sb_spring_bones:        
        
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
        #print("self.timer_handler =", self.timer_handler)
        if event.type == "ESC" or context.scene.sb_global_spring == False:         
            self.cancel(context)
            #print("ESCAPE")
            return {'FINISHED'}  
            
        if event.type == 'TIMER':       
            spring_bone(context)
        
        
        return {'PASS_THROUGH'}

        
    def execute(self, context):     
        args = (self, context)  
        #print("self.timer_handler =", self.timer_handler)
        # enable spring bone
        if context.scene.sb_global_spring == False:  
            wm = context.window_manager
            self.timer_handler = wm.event_timer_add(0.02, window=context.window)            
            wm.modal_handler_add(self)
            print("--Start modal--")
            
            context.scene.sb_global_spring = True
            update_bone(self, context)
            
            return {'RUNNING_MODAL'}    
        
        # disable spring selection
        
        else:
            print("--End modal--")
            #self.cancel(context)
            context.scene.sb_global_spring = False
            return {'FINISHED'}  
           
            
    def cancel(self, context):
        #if context.scene.sb_global_spring:
        #print("GOING TO CLOSE TIMER...")
        
        wm = context.window_manager
        wm.event_timer_remove(self.timer_handler)
        #print("CLOSED TIMER")
          
        context.scene.sb_global_spring = False
        
        for item in context.scene.sb_spring_bones:        
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
            
            
class SB_OT_spring(bpy.types.Operator):
    """Spring Bones, animation mode. Support baking."""
    
    bl_idname = "sb.spring_bone_frame"
    bl_label = "spring_bone_frame" 

   
    def execute(self, context):        
        if context.scene.sb_global_spring_frame == False:           
            context.scene.sb_global_spring_frame = True
            update_bone(self, context)
 
        else:
            end_spring_bone(context, self)
            context.scene.sb_global_spring_frame = False  
            
        return {'FINISHED'}  
        
class SB_OT_select_bone(bpy.types.Operator):
    """Select this bone"""
    
    bl_idname = "sb.select_bone"
    bl_label = "select_bone" 
    
    bone_name : bpy.props.StringProperty(default="")
   
    def execute(self, context):        
        data_bone = get_pose_bone(self.bone_name).bone
        bpy.context.active_object.data.bones.active = data_bone
        data_bone.select = True
        for i, l in enumerate(data_bone.layers):
            if l == True and bpy.context.active_object.data.layers[i] == False:
                bpy.context.active_object.data.layers[i] = True
                print("enabled layer", i)
            
        #get_pose_bone(self.bone_name).select = True
            
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
        #col.prop(scene, 'sb_global_spring', text="Enable spring")
        if context.scene.sb_global_spring == False:
            col.operator(SB_OT_spring_modal.bl_idname, text="Start - Interactive Mode", icon='PLAY')           
        if context.scene.sb_global_spring == True:
            col.operator(SB_OT_spring_modal.bl_idname, text="Stop", icon='PAUSE')          
      
        col.enabled = not context.scene.sb_global_spring_frame
      
        col = layout.column(align=True)
        if context.scene.sb_global_spring_frame == False:          
            col.operator(SB_OT_spring.bl_idname, text="Start - Animation Mode", icon='PLAY')
        if context.scene.sb_global_spring_frame == True:           
            col.operator(SB_OT_spring.bl_idname, text="Stop", icon='PAUSE')
            
        col.enabled = not context.scene.sb_global_spring
        
        col = layout.column(align=True)
        
        col.label(text='Bone Parameters:')
        col.prop(active_bone, 'sb_bone_spring', text="Spring")        
        col.prop(active_bone, 'sb_bone_rot', text="Rotation")
        col.prop(active_bone, 'sb_stiffness', text="Bouncy")
        col.prop(active_bone,'sb_damp', text="Speed")
        col.prop(active_bone,'sb_gravity', text="Gravity")
        col.label(text="Lock axis when colliding:")
        col.prop(active_bone, 'sb_lock_axis', text="")
        col.enabled = not active_bone.sb_bone_collider
        
        layout.separator()
        col = layout.column(align=True)
        col.prop(active_bone, 'sb_bone_collider', text="Collider")
        col.prop(active_bone, 'sb_collider_dist', text="Collider Distance")
        col.prop(active_bone, 'sb_collider_force', text="Collider Force")       
        col.enabled = not active_bone.sb_bone_spring
        
        layout.separator()
        layout.prop(scene, "sb_show_colliders")
        col = layout.column(align=True)
        
        if scene.sb_show_colliders:
            for pbone in bpy.context.active_object.pose.bones:
                if "sb_bone_collider" in pbone.keys():
                    if pbone.sb_bone_collider:
                        row = col.row()
                        row.label(text=pbone.name)
                        r = row.operator(SB_OT_select_bone.bl_idname, text="Select")
                        r.bone_name = pbone.name
        
        
        
#### REGISTER ############# 

class bones_collec(bpy.types.PropertyGroup):
    armature : bpy.props.StringProperty(default="")
    last_loc : bpy.props.FloatVectorProperty(name="Loc", subtype='DIRECTION', default=(0,0,0), size = 3)    
    speed : bpy.props.FloatVectorProperty(name="Speed", subtype='DIRECTION', default=(0,0,0), size = 3)
    dist: bpy.props.FloatProperty(name="distance", default=1.0)
    target_offset : bpy.props.FloatVectorProperty(name="TargetLoc", subtype='DIRECTION', default=(0,0,0), size = 3)    
    sb_bone_rot : bpy.props.BoolProperty(name="Bone Rot", default=False)
    sb_bone_collider: bpy.props.BoolProperty(name="Bone collider", default=False)
    sb_collider_dist : bpy.props.FloatProperty(name="Bone collider distance", default=0.5)
    sb_collider_force : bpy.props.FloatProperty(name="Bone collider force", default=1.0)    
    matrix_offset = Matrix()
    initial_matrix = Matrix()
    
classes = (SB_PT_ui, bones_collec, SB_OT_spring_modal, SB_OT_spring, SB_OT_select_bone)
        
def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)   
        
    bpy.app.handlers.frame_change_post.append(spring_bone_frame_mode)
    
    bpy.types.Scene.sb_spring_bones = bpy.props.CollectionProperty(type=bones_collec)       
    bpy.types.Scene.sb_global_spring = bpy.props.BoolProperty(name="Enable spring", default = False)#, update=update_global_spring)
    bpy.types.Scene.sb_global_spring_frame = bpy.props.BoolProperty(name="Enable Spring", description="Enable Spring on frame change only", default = False)
    bpy.types.Scene.sb_show_colliders = bpy.props.BoolProperty(name="Show Colliders", description="Show active colliders names", default = False)
    bpy.types.PoseBone.sb_bone_spring = bpy.props.BoolProperty(name="Enabled", default=False, description="Enable spring effect on this bone")
    bpy.types.PoseBone.sb_bone_collider = bpy.props.BoolProperty(name="Collider", default=False, description="Enable this bone as collider")
    bpy.types.PoseBone.sb_collider_dist = bpy.props.FloatProperty(name="Collider Distance", default=0.5, description="Minimum distance to handle collision between the spring and collider bones")
    bpy.types.PoseBone.sb_collider_force = bpy.props.FloatProperty(name="Collider Force", default=1.0, description="Amount of repulsion force when colliding")
    bpy.types.PoseBone.sb_stiffness = bpy.props.FloatProperty(name="Stiffness", default=0.5, min = 0.01, max = 1.0, description="Bouncy/elasticity value, higher values lead to more bounciness")
    bpy.types.PoseBone.sb_damp = bpy.props.FloatProperty(name="Damp", default=0.7, min=0.0, max = 10.0, description="Speed/damping force applied to the bone to go back to it initial position") 
    bpy.types.PoseBone.sb_gravity = bpy.props.FloatProperty(name="Gravity", description="Additional vertical force to simulate gravity", default=0.0, min=-100.0, max = 100.0) 
    bpy.types.PoseBone.sb_bone_rot = bpy.props.BoolProperty(name="Rotation", default=False, description="The spring effect will apply on the bone rotation instead of location")
    bpy.types.PoseBone.sb_lock_axis = bpy.props.EnumProperty(items=(('NONE', 'None', ""), ('+X', '+X', ''), ('-X', '-X', ''), ('+Y', "+Y", ""), ('-Y', '-Y', ""), ('+Z', '+Z', ""), ('-Z', '-Z', '')), default="NONE")
    
    
    
def unregister():
    from bpy.utils import unregister_class
    
    for cls in reversed(classes):
        unregister_class(cls)   
    
    bpy.app.handlers.frame_change_post.remove(spring_bone_frame_mode) 
    
    del bpy.types.Scene.sb_spring_bones  
    del bpy.types.Scene.sb_global_spring
    del bpy.types.Scene.sb_global_spring_frame
    del bpy.types.Scene.sb_show_colliders
    del bpy.types.PoseBone.sb_bone_spring
    del bpy.types.PoseBone.sb_bone_collider
    del bpy.types.PoseBone.sb_collider_dist
    del bpy.types.PoseBone.sb_collider_force
    del bpy.types.PoseBone.sb_stiffness
    del bpy.types.PoseBone.sb_damp
    del bpy.types.PoseBone.sb_gravity
    del bpy.types.PoseBone.sb_bone_rot
    del bpy.types.PoseBone.sb_lock_axis
    
    
    
if __name__ == "__main__":
    register()
    
