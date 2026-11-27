"""Full room -> baked, web-ready models.
   python bake.py --res 2048 --samples 48 --out web     (use --res 256 --samples 4 for a dry run)"""
import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


import bpy  # noqa
import bmesh  # noqa
import numpy as np  # noqa
from mathutils import Vector  # noqa

import build  # noqa
import furniture  # noqa
from lib import *  # noqa
from build import ROOM_X, ROOM_Y, WALL_H, WALL_T  # noqa

R = math.radians
DYNAMIC = {  # kept as their own nodes, not baked: the page paints on these
    "TV.Screen": "screen_tv", "Tripod.PhoneScreen": "screen_phone", "Arcade.Screen": "screen_arcade",
    "Poster.Art": "screen_frame", "Ebook.Book.Cover": "screen_ebook",
}
MOVING = {"Arcade.Stick": "stick", "Arcade.StickBall": "stick", "Arcade.Btn0": "btn0", "Arcade.Btn1": "btn1", "Arcade.Btn2": "btn2",
          "Arcade.Btn3": "btn3", "Arcade.Btn4": "btn4", "Arcade.Btn5": "btn5"}
SKIP = ("Backdrop.", "Shell.Slab")
INNER = {"Shell.Floor": (0, 0, 1), "Shell.WallBack": (0, -1, 0), "Shell.WallLeft": (1, 0, 0), "Front.Wall": (0, 1, 0),
         "Right.Wall": (-1, 0, 0), "Ceiling.Ceiling": (0, 0, -1)}
ATLAS_OF = {"floor": ("Shell.Floor",),
            "shell": ("Shell.", "Front.", "Right.", "Ceiling.", "Rug."),
            "big": ("Sofa.", "Bed.", "Console.", "CoffeeTable.", "Desk.", "Bookshelf.", "Arcade.", "SlatWall.", "Bench.", "Nightstand.",
                    "SofaConsole.", "Chair.", "TV.", "Pouf.")}


def close_room(M):
    """The two walls and ceiling the mockup left off, with windows and a door."""
    white = m_paint("Paint Warm White", "#E9E4D8", rough=0.85)
    ceil = m_paint("Paint Ceiling", "#F0EDE6", rough=0.9)
    frame = M.powder
    out = []
    f = piece("Front")
    out.append(box(f, "Wall", (-WALL_T, -WALL_T, -0.02), (ROOM_X + WALL_T, 0, WALL_H), M.shell, bevel=0, face_mats={"+y": white}))
    out.append(box(f, "Base", (0, 0, 0), (ROOM_X, 0.014, 0.09), M.base, bevel=0.003))
    r = piece("Right")
    out.append(box(r, "Wall", (ROOM_X, 0, -0.02), (ROOM_X + WALL_T, ROOM_Y, WALL_H), M.shell, bevel=0, face_mats={"-x": white}))
    out.append(box(r, "BaseA", (ROOM_X - 0.014, 0.014, 0), (ROOM_X, 0.33, 0.09), M.base, bevel=0.003))
    out.append(box(r, "BaseB", (ROOM_X - 0.014, 1.27, 0), (ROOM_X, ROOM_Y - 0.014, 0.09), M.base, bevel=0.003))
    c = piece("Ceiling")
    out.append(box(c, "Ceiling", (0, 0, WALL_H), (ROOM_X, ROOM_Y, WALL_H + 0.1), M.shell, bevel=0, face_mats={"-z": ceil}))
    panes = []

    def window(p, name, a0, a1, z0, z1, wall):
        """wall='front': spans x a0..a1 on y=0.  wall='right': spans y a0..a1 on x=ROOM_X."""
        t, d = 0.05, 0.06
        def bx(nm, u0, u1, w0, w1, dep=d):
            if wall == "front":
                out.append(box(p, name + nm, (u0, 0, w0), (u1, dep, w1), frame, bevel=0.004))
            else:
                out.append(box(p, name + nm, (ROOM_X - dep, u0, w0), (ROOM_X, u1, w1), frame, bevel=0.004))
        bx("L", a0 - t, a0, z0 - t, z1 + t); bx("R", a1, a1 + t, z0 - t, z1 + t)
        bx("T", a0, a1, z1, z1 + t); bx("B", a0 - 0.02, a1 + 0.02, z0 - t, z0, 0.1)
        mid = (a0 + a1) / 2
        bx("M", mid - 0.018, mid + 0.018, z0, z1, 0.045)
        zc = z0 + (z1 - z0) * 0.62
        bx("H", a0, a1, zc - 0.015, zc + 0.015, 0.045)
        if wall == "front":
            q = quad(p, name + "Pane", a1 - a0, z1 - z0, M.pane, (mid, 0.012, (z0 + z1) / 2), rot=(0, 0, math.pi))
        else:
            q = quad(p, name + "Pane", a1 - a0, z1 - z0, M.pane, (ROOM_X - 0.012, mid, (z0 + z1) / 2), rot=(0, 0, -math.pi / 2))
        panes.append(q)
    M.pane = m_emit("Window Light", "#EAF2FF", 1.0)
    window(f, "WinA", 0.9, 2.5, 0.85, 2.35, "front")
    window(f, "WinB", 3.1, 4.7, 0.85, 2.35, "front")
    window(r, "WinC", 2.1, 3.5, 0.85, 2.35, "right")
    # entry door on the right-hand wall
    out.append(box(r, "DoorFrame", (ROOM_X - 0.05, 0.33, 0), (ROOM_X, 1.27, 2.12), frame, bevel=0.004))
    out.append(box(r, "Door", (ROOM_X - 0.062, 0.38, 0.005), (ROOM_X - 0.02, 1.22, 2.07), M.walnut, bevel=0.004))
    out.append(cyl(r, "DoorKnob", (ROOM_X - 0.062, 0.47, 1.0), (ROOM_X - 0.12, 0.47, 1.0), 0.014, M.brass))
    out.append(sphere(r, "DoorKnobBall", (ROOM_X - 0.125, 0.47, 1.0), 0.03, M.brass, seg=16, rings=8))
    for o in out + panes:                       # daylight still reaches the room as in the approved mockup
        o.visible_shadow = False
    for q in panes:
        q.name = "Window.Pane%d" % panes.index(q)
    return panes


def tri_count(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    n = 0
    for o in objs:
        me = o.evaluated_get(dg).to_mesh()
        n += sum(len(p.vertices) - 2 for p in me.polygons)
        o.evaluated_get(dg).to_mesh_clear()
    return n


def realize(sc):
    """Every visible thing becomes a plain world-space mesh object: 'base' (no bevels) with the bevel kept as a modifier."""
    dg = bpy.context.evaluated_depsgraph_get()
    made = []
    src = [o for o in sc.objects if o.type in ("MESH", "CURVE")]
    for o in src:
        if o.name.startswith(SKIP):
            continue
        bev = None
        if o.type == "CURVE":
            o.data.resolution_u = 6
            o.data.bevel_resolution = 2
        else:
            for m in o.modifiers:
                if m.type == "BEVEL":
                    bev = (m.width, m.segments)
                if m.type in ("BEVEL", "WEIGHTED_NORMAL", "SUBSURF"):
                    m.show_viewport = False
                    m.show_render = False
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    for o in src:
        if o.name.startswith(SKIP):
            continue
        ev = o.evaluated_get(dg)
        me = bpy.data.meshes.new_from_object(ev, preserve_all_data_layers=True, depsgraph=dg)
        me.transform(o.matrix_world)
        me.name = o.name
        keep = INNER.get(o.name)
        if keep:
            bm = bmesh.new(); bm.from_mesh(me)
            n = Vector(keep)
            bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.normal.dot(n) < 0.9], context="FACES")
            bm.to_mesh(me); bm.free()
        bev = next(((m.width, m.segments) for m in o.modifiers if m.type == "BEVEL"), None) if o.type == "MESH" else None
        made.append((o.name, me, bev, o.visible_shadow))
    for o in sc.objects:
        if o.type == "LIGHT" and o.parent is not None:
            mw = o.matrix_world.copy()
            o.parent = None
            o.matrix_world = mw
    for o in list(sc.objects):
        if o.type in ("MESH", "CURVE", "EMPTY"):
            bpy.data.objects.remove(o, do_unlink=True)
    objs = []
    for name, me, bev, vis in made:
        n = bpy.data.objects.new(name, me)
        sc.collection.objects.link(n)
        n.visible_shadow = vis
        n["bev"] = bev[0] if bev else 0.0
        n["seg"] = bev[1] if bev else 0
        objs.append(n)
    return objs


def atlas_name(name):
    for k, pre in ATLAS_OF.items():
        if name.startswith(pre):
            return k
    return "props"


def select_only(objs, active=None):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = active or objs[0]


def unwrap(objs):
    for o in objs:
        lm = o.data.uv_layers.new(name="LM")
        o.data.uv_layers.active = lm
    select_only(objs)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=R(66), island_margin=0.0, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
    bpy.ops.uv.select_all(action="SELECT")
    bpy.ops.uv.average_islands_scale()
    bpy.ops.uv.pack_islands(rotate=True, margin=0.0035)
    bpy.ops.object.mode_set(mode="OBJECT")


def with_bevels(objs):
    for o in objs:
        if o["bev"] > 0:
            b = o.modifiers.new("bevel", "BEVEL")
            b.width = o["bev"]
            b.segments = min(2, int(o["seg"]))
            b.limit_method = "ANGLE"
            b.angle_limit = R(40)


def join(objs, name):
    """Copies of objs (modifiers applied) merged into one mesh."""
    dg = bpy.context.evaluated_depsgraph_get()
    copies = []
    for o in objs:
        me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
        c = bpy.data.objects.new("tmp", me)
        bpy.context.scene.collection.objects.link(c)
        c.visible_shadow = o.visible_shadow
        copies.append(c)
    if len(copies) > 1:
        select_only(copies)
        bpy.ops.object.join()
    j = copies[0]
    j.name = name
    return j


def neutral(rgb):
    """Khronos PBR Neutral tone map (the one the approved renders used), then sRGB."""
    c = np.maximum(rgb, 0.0)
    x = c.min(axis=-1, keepdims=True)
    off = np.where(x < 0.08, x - 6.25 * x * x, 0.04)
    c = c - off
    peak = c.max(axis=-1, keepdims=True)
    sc_, d = 0.76, 0.24
    newp = 1.0 - d * d / (peak + d - sc_)
    hi = peak >= sc_
    c2 = c * np.where(hi, newp / np.maximum(peak, 1e-6), 1.0)
    g = 1.0 - 1.0 / (0.15 * (peak - newp) + 1.0)
    c2 = np.where(hi, c2 * (1 - g) + newp * g, c2)
    c2 = np.clip(c2, 0, 1)
    return np.where(c2 <= 0.0031308, c2 * 12.92, 1.055 * np.power(c2, 1 / 2.4) - 0.055)


def bake(obj, name, res, samples, outdir, imgs):
    """The solid and the no-shadow half of a group paint into the same sheet."""
    sc = bpy.context.scene
    sheet = name.replace("_open", "")
    fresh = sheet not in imgs
    img = imgs.get(sheet) or bpy.data.images.new("bake_" + sheet, res, res, alpha=False, float_buffer=True)
    imgs[sheet] = img
    for m in obj.data.materials:
        nt = m.node_tree
        n = nt.nodes.get("BAKE") or nt.nodes.new("ShaderNodeTexImage")
        n.name = "BAKE"
        n.image = img
        for k in nt.nodes:
            k.select = False
        n.select = True
        nt.nodes.active = n
    obj.data.uv_layers.active = obj.data.uv_layers["LM"]
    select_only([obj])
    sc.cycles.samples = samples
    sc.render.bake.margin = max(4, res // 256)
    sc.render.bake.margin_type = "EXTEND"
    sc.render.bake.use_clear = fresh
    sc.render.bake.target = "IMAGE_TEXTURES"
    t = time.time()
    bpy.ops.object.bake(type="COMBINED")
    px = np.array(img.pixels[:], dtype=np.float32).reshape(res, res, 4)[::-1, :, :3]
    from PIL import Image
    out = (neutral(px) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(out).save(os.path.join(outdir, sheet + ".png"))
    print("BAKED %s %dpx in %.0fs" % (name, res, time.time() - t), flush=True)


def b2t(v):
    return [round(v[0], 4), round(v[2], 4), round(-v[1], 4)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", type=int, default=2048)
    ap.add_argument("--samples", type=int, default=48)
    ap.add_argument("--out", default="web")
    ap.add_argument("--only", default="")
    ap.add_argument("--nobake", action="store_true")
    a = ap.parse_args()
    outdir = os.path.join(HERE, a.out)
    os.makedirs(outdir, exist_ok=True)
    sc, M, cams = build.build_all()
    panes = close_room(M)
    build.render_settings(sc, 512, a.samples)
    bpy.context.view_layer.update()
    print("tris before realize:", tri_count([o for o in sc.objects if o.type == "MESH"]), flush=True)

    pieces = {}
    dg = bpy.context.evaluated_depsgraph_get()
    for o in sc.objects:
        if o.type not in ("MESH", "CURVE") or o.name.startswith(SKIP):
            continue
        pn = o.name.split(".")[0]
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo, hi = pieces.setdefault(pn, ([1e9] * 3, [-1e9] * 3))
            for i in range(3):
                lo[i] = min(lo[i], w[i]); hi[i] = max(hi[i], w[i])
    objs = realize(sc)
    bpy.context.view_layer.update()
    by = {o.name: o for o in objs}
    dyn = [o for o in objs if o.name in DYNAMIC or o.name.startswith("Window.Pane")]
    static = [o for o in objs if o not in dyn]
    groups = {}
    for o in static:
        groups.setdefault(atlas_name(o.name), []).append(o)
    meta = {"screens": {}, "atlases": list(groups.keys()),
            "pieces": {k: {"min": [round(lo[0], 3), round(lo[2], 3), round(-hi[1], 3)], "max": [round(hi[0], 3), round(hi[2], 3), round(-lo[1], 3)]}
                       for k, (lo, hi) in pieces.items()}}
    for o in dyn:                                   # corners in uv order (0,0) (1,0) (1,1) (0,1)
        uv = o.data.uv_layers[0].data
        pts = {}
        for li, l in enumerate(o.data.loops):
            u = uv[li].uv
            pts[(round(u[0]), round(u[1]))] = b2t(o.data.vertices[l.vertex_index].co)
        key = DYNAMIC.get(o.name, o.name)
        meta["screens"][key] = [pts[(0, 0)], pts[(1, 0)], pts[(1, 1)], pts[(0, 1)]]
    for k, g in groups.items():
        t = time.time()
        unwrap(g)
        print("unwrapped %s: %d objects, %.1fs" % (k, len(g), time.time() - t), flush=True)
    # lite: no bevels
    lite = {}
    for o in static:                                # low-poly: thin out anything round or soft
        if len(o.data.polygons) > 250 and o.name not in MOVING:
            d = o.modifiers.new("lite", "DECIMATE")
            d.ratio = 0.22 if len(o.data.polygons) > 700 else 0.4
    bpy.context.view_layer.update()
    def split(g):
        fixed = [o for o in g if o.name not in MOVING]
        return [o for o in fixed if o.visible_shadow], [o for o in fixed if not o.visible_shadow]
    for k, g in groups.items():
        solid, open_ = split(g)
        lite[k] = join(solid, "lite_" + k)
        if open_:
            lite[k + "_open"] = join(open_, "lite_" + k + "_open")
    for o in lite.values():
        o.hide_render = True
    for o in static:
        for m in [m for m in o.modifiers if m.type == "DECIMATE"]:
            o.modifiers.remove(m)
    movers = {}
    for o in static:
        if o.name in MOVING:
            movers.setdefault(MOVING[o.name], []).append(o)
    with_bevels(static)
    bpy.context.view_layer.update()
    full = {}
    for k, g in groups.items():
        solid, open_ = split(g)
        full[k] = join(solid, "full_" + k)
        if open_:
            full[k + "_open"] = join(open_, "full_" + k + "_open")
            full[k + "_open"].visible_shadow = False
    mv = {}
    for k, g in movers.items():
        mv[k] = join(g, "move_" + k)
        c = sum((Vector(v.co) for v in mv[k].data.vertices), Vector()) / len(mv[k].data.vertices)
        meta.setdefault("movers", {})[k] = b2t(c)
    for o in static:
        bpy.data.objects.remove(o, do_unlink=True)
    for k in full:
        print("%s: full %d tris, lite %d tris" % (k, tri_count([full[k]]), tri_count([lite[k]])), flush=True)

    if not a.nobake:
        imgs = {}
        for k in full:
            if a.only and k not in a.only.split(","):
                continue
            res = a.res if not k.startswith("shell") else max(256, a.res // 2)
            bake(full[k], k, res, a.samples, outdir, imgs)

    # ---- export
    for o in list(full.values()) + list(lite.values()) + list(mv.values()):
        for l in [l for l in o.data.uv_layers if l.name != "LM"]:
            o.data.uv_layers.remove(l)
        o.data.materials.clear()
    for o in lite.values():
        o.hide_render = False
    for o in dyn:
        o.data.materials.clear()
        o.name = DYNAMIC.get(o.name, o.name.replace("Window.Pane", "pane"))
    for tag, sel in (("full", list(full.values())), ("lite", list(lite.values()))):
        select_only(sel + list(mv.values()) + dyn)
        bpy.ops.export_scene.gltf(filepath=os.path.join(outdir, "studio-%s.glb" % tag), export_format="GLB", use_selection=True,
                                  export_normals=False, export_materials="NONE", export_yup=True, export_apply=False,
                                  export_cameras=False, export_lights=False, export_animations=False)
        print("exported", tag, os.path.getsize(os.path.join(outdir, "studio-%s.glb" % tag)) // 1024, "KB", flush=True)
    json.dump(meta, open(os.path.join(outdir, "meta.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
