# How the studio model is made

The room in `/studio/` is a baked model: the lighting is rendered once and painted into textures.

1. `pip install bpy numpy pillow` (Blender as a Python module, 5.x).
2. `python gfx.py` draws the screen and poster graphics into `tex/`.
3. Edit the room in `furniture.py` (objects) and `build.py` (shell, materials, light).
4. `python bake.py --res 2048 --samples 32 --out web` renders the lighting and writes
   `studio-full.glb`, `studio-lite.glb`, four texture sheets and `meta.json`.
5. Shrink the `.glb` files with `gltf-transform meshopt --quantize-texcoord 14`, save each sheet as
   `<name>-2k.jpg` and a half-size `<name>-1k.jpg`, and copy everything into `../model/`.

`build.py --view hero` renders a still of the corner cutaway.
