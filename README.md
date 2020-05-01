# Spring Bones
Blender addon to add spring/bouncy dynamic effect to bones.

![alt text](https://github.com/artellblender/springbones/blob/master/bbones_chain.gif)

Warning, it's currently in a very early state, alpha-proof of concept.
The effect applies to the bone position and rotation in option.
It's not production ready, it's mainly a toy to play with.
User support is not granted for it considering this early state, it may be buggy but still fun to play with :)

## Installation

- Download and install the spring_bones.py file in Blender 2.8
- In Pose Mode, go to the "Spring Bones" panel in the Bone tools section on the right.

![alt text](https://github.com/artellblender/springbones/blob/master/1.png)

- Click "Enable Bone" to enable spring on a bone (must be a child bone)
- You can adjust the "Bouncy", "Speed" and other parameters parameters such as collision
- Click "Start" to enable the effect interactively, or "Start - Animation Mode" to enable it on frame change only (support baking)
- When moving the parent bone, the child will move dynamically with bouncy motion
- To bake, use the Blender baking tool: press F3 > type "bake" > NLA Bake



