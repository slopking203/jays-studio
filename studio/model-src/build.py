"""Builds the studio and renders it.  usage: python build.py --view hero --res 900 --samples 48 --out out.png"""
import argparse
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

from lib import *  # noqa: E402,F401,F403
import lib  # noqa: E402

ROOM_X, ROOM_Y, WALL_H, WALL_T, SLAB_T = 6.0, 5.2, 2.8, 0.18, 0.26
OPT = {}


def materials():
    M = SimpleNamespace()
    # --- the three brand colours, as real finishes
    M.green_wall = m_paint("Paint Green #508B3F", "#508746")
    M.charcoal_wall = m_paint("Paint Charcoal #2E2E2E", CHARCOAL, rough=0.78)
    M.shell = m_flat("Shell Charcoal", CHARCOAL, rough=0.72)
    M.base = m_flat("Baseboard Charcoal", CHARCOAL, rough=0.42)
    M.brass = m_metal("Brass Gold #FFC857", GOLD, rough=0.26)
    M.brass_brushed = m_metal("Brass Brushed", GOLD, rough=0.36, brushed=True)
    M.powder = m_flat("Powdercoat Charcoal", CHARCOAL, rough=0.5)
    M.plastic = m_flat("Plastic Charcoal", "#262626", rough=0.4)
    M.gloss = m_flat("Gloss Black", "#121212", rough=0.1, coat=0.6)
    M.sofa = m_fabric("Sofa Charcoal", CHARCOAL, sheen=0.65, var=0.08, fleck=0.16, weave=150, bump=0.9)
    M.headboard = m_fabric("Headboard Charcoal", "#353535", sheen=0.7, var=0.07, weave=260, bump=0.5)
    M.gold_velvet = m_fabric("Velvet Gold", GOLD, sheen=1.0, rough=0.8, sheen_rough=0.35, var=0.1, bump=0.15)
    M.green_velvet = m_fabric("Velvet Green", GREEN, sheen=1.0, rough=0.8, sheen_rough=0.35, var=0.1, bump=0.15)
    M.green_knit = m_knit("Knit Green", GREEN)
    M.green_throw = m_knit("Knit Throw Green", GREEN, rows=70.0, bump=0.8, direction="Y")
    M.gold_paint = m_flat("Lacquer Gold", GOLD, rough=0.35)
    M.green_paint = m_flat("Lacquer Green", GREEN, rough=0.4)
    # --- supporting naturals
    M.floor = m_floor("Oak Floor")
    M.backdrop = m_flat("Backdrop", "#E0DCD4", rough=0.95)
    M.walnut = m_wood("Walnut", "#4B2F1E", "#7C543A", rough=0.4, coat=0.15)
    M.slat = m_wood("Slat Charcoal Oak", "#242424", "#353535", rough=0.4, coat=0.25, along=1.6, across=60)
    M.felt = m_fabric("Felt Black", "#191919", sheen=0.3, var=0.03)
    M.linen = m_fabric("Linen Cream", "#E9E2D0", sheen=0.4, var=0.04, weave=300, bump=0.5, fleck=0.05)
    M.cotton = m_fabric("Cotton White", "#F1EDE3", sheen=0.3, var=0.03)
    M.rug = m_rug("Rug Cream", "#E4DCC8", accent_hex="#C9BFA8")
    M.ceramic_charcoal = m_flat("Ceramic Charcoal", "#2A2A2A", rough=0.6)
    M.ceramic_cream = m_flat("Ceramic Cream", "#E8E0CE", rough=0.3, coat=0.4)
    M.paper = m_flat("Paper", "#EFEADF", rough=0.7)
    M.soil = m_flat("Soil", "#2B1F17", rough=0.95)
    M.alu = m_metal("Aluminium Dark", "#5A5C5E", rough=0.38)
    M.glass = m_glass("Glass")
    M.leaf_rubber = m_leaf("Leaf Rubber", "#2F6B2C", "#173F1B", rough=0.22)
    M.leaf_snake = m_leaf("Leaf Snake", "#3E6B35", "#1F4423", edge_hex="#D9C56A", rough=0.3, bands=True)
    M.leaf_soft = m_leaf("Leaf Pothos", "#5E9A45", "#2F6B2C", rough=0.35)
    M.trunk = m_wood("Trunk", "#4A3A2A", "#6B5640", rough=0.8)["z"]
    M.shade = m_shade("Shade Linen", "#EFE4CB")
    # --- lit things
    M.tv = m_screen("Screen TV", "tv.png", 1.5)
    M.laptop = m_screen("Screen Laptop", "laptop.png", 1.8)
    M.arcade = m_screen("Screen Arcade", "arcade.png", 2.6)
    M.marquee = m_screen("Marquee", "marquee.png", 1.6)
    M.phone = m_screen("Screen Phone", "phone.png", 2.0)
    M.keys = m_print("Keys", "keys.png", rough=0.45)
    M.remote = m_print("Remote Top", "remote.png", rough=0.4)
    M.poster = m_print("Poster", "poster.png", rough=0.6)
    M.cover = m_print("Ebook Cover", "cover.png", rough=0.6)
    M.art = [m_print("Art %d" % i, "art%d.png" % i, rough=0.6) for i in range(3)]
    M.bulb = m_emit("Bulb Warm", "#FFD9A0", 30.0)
    M.ring = m_emit("Ring Light", "#FFF1DC", 9.0)
    M.led = m_emit("LED Gold", GOLD, 14.0)
    M.books = [m_flat("Book %s" % n, h, rough=0.75) for n, h in
               [("green", GREEN), ("charcoal", CHARCOAL), ("gold", GOLD), ("cream", "#E9E2D0"), ("deep green", "#2F5A2A"),
                ("stone", "#8E877A"), ("white", "#F1EDE3"), ("tan", "#B9976B")]]
    return M


def build_shell(M):
    p = piece("Shell")
    box(p, "Slab", (-WALL_T, 0, -SLAB_T), (ROOM_X, ROOM_Y + WALL_T, -0.02), M.shell, bevel=0.004)
    box(p, "Floor", (0, 0, -0.02), (ROOM_X, ROOM_Y, 0), M.floor, bevel=0.0015)
    box(p, "WallBack", (-WALL_T, ROOM_Y, -0.02), (ROOM_X, ROOM_Y + WALL_T, WALL_H), M.shell, bevel=0.004,
        face_mats={"-y": M.green_wall})
    box(p, "WallLeft", (-WALL_T, 0, -0.02), (0, ROOM_Y, WALL_H), M.shell, bevel=0.004, face_mats={"+x": M.charcoal_wall})
    box(p, "BaseBack", (0, ROOM_Y - 0.014, 0), (ROOM_X, ROOM_Y, 0.09), M.base, bevel=0.003)
    box(p, "BaseLeftA", (0, 0, 0), (0.014, 0.45, 0.09), M.base, bevel=0.003)
    box(p, "BaseLeftB", (0, 2.95, 0), (0.014, ROOM_Y - 0.014, 0.09), M.base, bevel=0.003)
    g = piece("Backdrop")
    box(g, "Ground", (-150, -150, -SLAB_T - 0.05), (150, 150, -SLAB_T), M.backdrop, bevel=0)
    return p


def build_slat_wall(M, y0=0.45, y1=2.95):
    p = piece("SlatWall")
    box(p, "Felt", (0, y0, 0), (0.008, y1, WALL_H), M.felt, bevel=0)
    pitch, w = 0.0403, 0.027
    n = int((y1 - y0) / pitch)
    for i in range(n):
        y = y0 + 0.007 + i * pitch
        box(p, "Slat.%02d" % i, (0.008, y, 0), (0.031, y + w, WALL_H), M.slat, bevel=0.0025)
    return p


def lighting(sc, sun_dir=(-0.12, 0.81, -0.575), sun=2.95, sky=0.4, fill=2.8):
    w = bpy.data.worlds.new("Sky")
    sc.world = w
    bg = next((n for n in w.node_tree.nodes if n.bl_idname == "ShaderNodeBackground"), None)
    if bg is None:
        bg = w.node_tree.nodes.new("ShaderNodeBackground")
        out = w.node_tree.nodes.new("ShaderNodeOutputWorld")
        w.node_tree.links.new(bg.outputs[0], out.inputs[0])
    bg.inputs["Color"].default_value = (0.76, 0.86, 1.0, 1)
    bg.inputs["Strength"].default_value = sky
    # the camera sees a plain studio backdrop above the cut walls; the room is still lit by the sky colour
    nt = w.node_tree
    outn = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeOutputWorld")
    lp = nt.nodes.new("ShaderNodeLightPath")
    seen = nt.nodes.new("ShaderNodeBackground")
    seen.inputs["Color"].default_value = (0.74, 0.72, 0.68, 1)
    mixs = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Camera Ray"], mixs.inputs[0])
    nt.links.new(bg.outputs[0], mixs.inputs[1])
    nt.links.new(seen.outputs[0], mixs.inputs[2])
    nt.links.new(mixs.outputs[0], outn.inputs["Surface"])
    L = bpy.data.lights.new("Sun", "SUN")
    L.energy = sun
    L.angle = math.radians(1.6)
    L.color = (1.0, 0.985, 0.95)
    o = bpy.data.objects.new("Sun", L)
    sc.collection.objects.link(o)
    o.rotation_euler = Vector(sun_dir).normalized().to_track_quat("-Z", "Y").to_euler()
    # broad soft daylight from the open right-hand side (where the window wall will be):
    # directional, so it lights the charcoal wall evenly instead of scorching whatever stands nearest
    F = bpy.data.lights.new("WindowFill", "SUN")
    F.energy = fill
    F.angle = math.radians(32)
    F.color = (0.95, 0.97, 1.0)
    fo = bpy.data.objects.new("WindowFill", F)
    sc.collection.objects.link(fo)
    fo.rotation_euler = Vector((-0.92, -0.08, -0.38)).normalized().to_track_quat("-Z", "Y").to_euler()
    return o


def add_camera(sc, name, target, az, el, dist, lens, shift=(0, 0)):
    cam = bpy.data.cameras.new(name)
    cam.lens = lens
    cam.sensor_width = 36
    cam.clip_start, cam.clip_end = 0.1, 500
    cam.shift_x, cam.shift_y = shift
    o = bpy.data.objects.new(name, cam)
    sc.collection.objects.link(o)
    a, e = math.radians(az), math.radians(el)
    d = Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)))
    o.location = Vector(target) + d * dist
    o.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    return o


def add_camera_at(sc, name, loc, target, lens, shift_y=0.0, level=False):
    """Camera at a standing position. level=True keeps it horizontal and uses lens shift to look down,
    the way interiors are photographed, so the walls stay vertical."""
    cam = bpy.data.cameras.new(name)
    cam.lens = lens
    cam.sensor_width = 36
    cam.clip_start, cam.clip_end = 0.05, 500
    cam.shift_y = shift_y
    o = bpy.data.objects.new(name, cam)
    sc.collection.objects.link(o)
    o.location = loc
    t = Vector(target)
    if level:
        t.z = loc[2]
    o.rotation_euler = (t - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return o


ANCHORS = {
    "TV": (0.12, 1.7, 1.42), "Remote": (1.80, 1.33, 0.42), "Phone on tripod": (5.509, 0.691, 1.57), "Arcade": (0.45, 4.37, 1.28),
    "Laptop": (2.0, 4.86, 0.87), "Poster": (4.96, 5.18, 1.80), "Ebook": (4.10, 1.29, 0.98),
}


def pins(sc, cam):
    """Where each clickable object lands in the picture, and whether the camera can actually see it."""
    from bpy_extras.object_utils import world_to_camera_view
    dg = bpy.context.evaluated_depsgraph_get()
    out = {}
    for k, v in ANCHORS.items():
        x, y, z = world_to_camera_view(sc, cam, Vector(v))
        o = cam.matrix_world.translation
        d = Vector(v) - o
        hit, loc, *_ = sc.ray_cast(dg, o, d.normalized(), distance=d.length - 0.06)
        out[k] = dict(x=round(x, 4), y=round(1 - y, 4), in_frame=bool(0 < x < 1 and 0 < y < 1 and z > 0), clear=not hit,
                      blocked_at=[round(c, 2) for c in loc] if hit else None)
    return out


def render_settings(sc, res, samples, aspect=1.0):
    sc.render.engine = "CYCLES"
    c = sc.cycles
    c.device = "CPU"
    c.samples = samples
    c.use_adaptive_sampling = True
    c.adaptive_threshold = 0.025
    c.use_denoising = True
    c.denoiser = "OPENIMAGEDENOISE"
    c.denoising_input_passes = "RGB_ALBEDO_NORMAL"
    c.max_bounces = 8
    c.diffuse_bounces = 4
    c.glossy_bounces = 4
    c.transmission_bounces = 6
    c.transparent_max_bounces = 8
    c.sample_clamp_indirect = 6.0
    c.caustics_reflective = False
    c.caustics_refractive = False
    sc.render.resolution_x = int(res * aspect) if aspect >= 1 else res
    sc.render.resolution_y = res if aspect >= 1 else int(res / aspect)
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.view_settings.view_transform = "Khronos PBR Neutral"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    sc.view_settings.gamma = 1.0
    sc.render.use_persistent_data = False


def build_all(stage="all"):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    M = materials()
    build_shell(M)
    build_slat_wall(M)
    if stage != "shell":
        import furniture
        furniture.build(M)
    lighting(sc, sun=OPT.get('sun', 2.95), sky=OPT.get('sky', 0.4), fill=OPT.get('fill', 2.8))
    cams = {
        "hero": add_camera(sc, "Cam.Hero", (2.85, 2.7, 0.92), -45, 30, 24, 93),
        "top": add_camera(sc, "Cam.Top", (3.1, 2.7, 0), -90, 89.9, 30, 110),
    }
    cams["eye"] = add_camera_at(sc, "Cam.Eye", (5.05, -0.25, 1.5), (0.39, 3.52, 1.5), 24, shift_y=-0.14, level=True)
    return sc, M, cams


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--view", default="hero")
    ap.add_argument("--res", type=int, default=800)
    ap.add_argument("--aspect", type=float, default=1.0)
    ap.add_argument("--samples", type=int, default=48)
    ap.add_argument("--out", default="out.png")
    ap.add_argument("--stage", default="all")
    ap.add_argument("--exposure", type=float, default=0.0)
    ap.add_argument("--save", default="")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--border", default="")
    ap.add_argument("--pins", default="")
    ap.add_argument("--sun", type=float, default=2.95)
    ap.add_argument("--sky", type=float, default=0.4)
    ap.add_argument("--fill", type=float, default=2.8)
    a = ap.parse_args(argv)
    OPT.update(sun=a.sun, sky=a.sky, fill=a.fill)
    t0 = time.time()
    sc, M, cams = build_all(a.stage)
    print("built in %.1fs, objects: %d" % (time.time() - t0, len(bpy.data.objects)))
    render_settings(sc, a.res, a.samples, a.aspect)
    sc.view_settings.exposure = a.exposure
    if a.save:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, a.save))
    sc.camera = cams[a.view]
    if a.border:
        x0, y0, x1, y1 = [float(v) for v in a.border.split(",")]      # fractions, origin top-left
        sc.render.use_border = True
        sc.render.use_crop_to_border = True
        sc.render.border_min_x, sc.render.border_max_x = x0, x1
        sc.render.border_min_y, sc.render.border_max_y = 1 - y1, 1 - y0
    if a.pins:
        import json
        bpy.context.view_layer.update()
        res = pins(sc, sc.camera)
        json.dump(res, open(os.path.join(HERE, a.pins), "w"), indent=1)
        for k, v in res.items():
            print("PIN %-16s %s" % (k, v))
    sc.render.filepath = os.path.join(HERE, a.out)
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    print("rendered %s in %.1fs" % (a.out, time.time() - t0))
    if a.probe:
        from bpy_extras.object_utils import world_to_camera_view
        from PIL import Image
        im = Image.open(sc.render.filepath).convert("RGB")
        W, H = im.size
        pts = {"green wall right": (3.1, ROOM_Y, 2.45), "green wall left": (1.2, ROOM_Y, 2.5), "green wall mid": (3.2, ROOM_Y, 1.9),
               "charcoal wall": (0.0, 4.2, 2.35), "slats": (0.031, 2.6, 2.4), "floor": (5.0, 2.6, 0.0),
               "backdrop": (8.0, -3.0, -SLAB_T)}
        for k, v in pts.items():
            x, y, z = world_to_camera_view(sc, sc.camera, Vector(v))
            px, py = int(x * W), int((1 - y) * H)
            if 2 <= px < W - 2 and 2 <= py < H - 2:
                reg = im.crop((px - 2, py - 2, px + 3, py + 3)).resize((1, 1), Image.BOX).getpixel((0, 0))
                print("PROBE %-18s px(%4d,%4d) rgb %s  #%02X%02X%02X" % (k, px, py, reg, *reg))
