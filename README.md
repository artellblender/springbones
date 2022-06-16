# Spring Bones
Blender addon to add spring/bouncy dynamic effect to bones.

![alt text](https://github.com/artellblender/springbones/blob/master/bbones_chain.gif)

Warning, it's currently in a very early state, alpha-proof of concept.
The effect applies to the bone position and rotation in option.
It's not production ready, it's mainly a toy to play with.
User support is not granted for it considering this early state, it may be buggy but still fun to play with :)


### System Requirements

| **OS** | **Blender** |
| ------------- | ------------- |
| OSX | Blender 2.80+ |
| Windows | Blender 2.80+ |
| Linux | Not Tested |


### Installation Process

1. Download the latest <b>[release](https://github.com/artellblender/springbones/releases/)</b>
2. If you downloaded the zip file.
3. Open Blender.
4. Go to File -> User Preferences -> Addons.
5. At the bottom of the window, choose *Install From File*.
6. Select the file `SpringBones-VERSION.zip` from your download location..
7. Activate the checkbox for the plugin that you will now find in the list.

## Usage

- In Pose Mode, go to the "Spring Bones" panel in the Bone tools section on the right.

![alt text](https://github.com/artellblender/springbones/blob/master/SpringBones-v091.png)

- Click "Enable Bone" to enable spring on a bone (must be a child bone)
- You can adjust the "Bouncy", "Speed" and other parameters parameters such as collision
- Click "Start" to enable the effect interactively, or "Start - Animation Mode" to enable it on frame change only (support baking)
- When moving the parent bone, the child will move dynamically with bouncy motion
- To bake, use the Blender baking tool: press F3 > type "bake" > NLA Bake
- Multiple bones can be editted at once now, this makes for faster and easier experience.
- Continous update makes it possible to make edits while animation plays. When OFF playmodes stop and need to enabled again manually.
- Presets can be saved using the preset manager in the panel header. They are saved under userfiles > scripts > presets > springbones.



### Changelog

[Full Changelog](CHANGELOG.md)
