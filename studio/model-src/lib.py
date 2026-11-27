"""Modeling helpers and physically based materials for the studio (Blender 5.x, Cycles)."""
import math
import os
import random
from types import SimpleNamespace

import bmesh
import bpy
from mathutils import Matrix, Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "tex")

GREEN, CHARCOAL, GOLD = "#508B3F", "#2E2E2E", "#FFC857"


# ----------------------------------------------------------------------------- colour
def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hexlin(h, a=1.0):
    h = h.lstrip("#")
    return (lin(int(h[0:2], 16) / 255), lin(int(h[2:4], 16) / 255), lin(int(h[4:6], 16) / 255), a)


def scale_col(c, k):
    return (c[0] * k, c[1] * k, c[2] * k, c[3])


# ----------------------------------------------------------------------------- scene graph
def piece(name, loc=(0, 0, 0), rz=0.0, parent=None):
    """A named group: its own collection plus a root empty that everything is parented to."""
    if parent is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    else:
        coll = parent.coll
    root = bpy.data.objects.new(name, None)
    root.empty_display_size = 0.15
    coll.objects.link(root)
    if parent is not None:
        root.parent = parent.root
    root.location = loc
    root.rotation_euler = (0, 0, rz)
    return SimpleNamespace(name=name, coll=coll, root=root)


def sub(p, name, loc=(0, 0, 0), rot=(0, 0, 0)):
    """A child frame inside a piece (for tilted or turned sub-assemblies)."""
    root = bpy.data.objects.new(p.name + "." + name, None)
    root.empty_display_size = 0.08
    p.coll.objects.link(root)
    root.parent = p.root
    root.location = loc
    root.rotation_euler = rot
    return SimpleNamespace(name=p.name + "." + name, coll=p.coll, root=root)


def add_obj(p, name, data, loc=(0, 0, 0), rot=(0, 0, 0)):
    o = bpy.data.objects.new(p.name + "." + name, data)
    p.coll.objects.link(o)
    o.parent = p.root
    o.location = loc
    o.rotation_euler = rot
    return o


def pick(mat, size=None):
    """Wood comes as {'x','y','z'} variants; choose the one whose grain follows the longest side."""
    if isinstance(mat, dict):
        if size is None:
            return mat["x"]
        ax = max(range(3), key=lambda i: size[i])
        return mat["xyz"[ax]]
    return mat


def smooth(me, sharp_deg=None):
    for poly in me.polygons:
        poly.use_smooth = True
    if sharp_deg is not None:
        me.set_sharp_from_angle(angle=math.radians(sharp_deg))


def mesh_from(name, verts, faces, uvs=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    me.update()
    if uvs is not None:
        layer = me.uv_layers.new(name="UVMap")
        for poly in me.polygons:
            for li in poly.loop_indices:
                layer.data[li].uv = uvs[me.loops[li].vertex_index]
    return me


# ----------------------------------------------------------------------------- primitives
def box(p, name, lo, hi, mat, bevel=0.004, seg=2, rot=(0, 0, 0), face_mats=None):
    lo, hi = Vector(lo), Vector(hi)
    size = hi - lo
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size.x, v.co.y * size.y, v.co.z * size.z))
    bm.to_mesh(me)
    bm.free()
    o = add_obj(p, name, me, loc=(lo + hi) / 2, rot=rot)
    me.materials.append(pick(mat, size))
    if face_mats:
        axes = {"+x": (1, 0, 0), "-x": (-1, 0, 0), "+y": (0, 1, 0), "-y": (0, -1, 0), "+z": (0, 0, 1), "-z": (0, 0, -1)}
        for key, fm in face_mats.items():
            me.materials.append(pick(fm, size))
            idx = len(me.materials) - 1
            n = Vector(axes[key])
            for poly in me.polygons:
                if poly.normal.dot(n) > 0.9:
                    poly.material_index = idx
    if bevel > 0:
        b = o.modifiers.new("bevel", "BEVEL")
        b.width = min(bevel, 0.45 * min(size))
        b.segments = seg
        b.limit_method = "ANGLE"
        b.angle_limit = math.radians(40)
        w = o.modifiers.new("wn", "WEIGHTED_NORMAL")
        w.keep_sharp = True
        smooth(me)
    return o


def cyl(p, name, p0, p1, r, mat, r2=None, seg=24, cap=True):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=seg, radius1=r,
                          radius2=(r if r2 is None else r2), depth=d.length)
    bm.to_mesh(me)
    bm.free()
    o = add_obj(p, name, me, loc=(p0 + p1) / 2)
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    me.materials.append(pick(mat))
    for poly in me.polygons:
        poly.use_smooth = len(poly.vertices) == 4
    return o


def sphere(p, name, c, r, mat, scale=(1, 1, 1), seg=32, rings=16):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=r)
    for v in bm.verts:
        v.co = Vector((v.co.x * scale[0], v.co.y * scale[1], v.co.z * scale[2]))
    bm.to_mesh(me)
    bm.free()
    o = add_obj(p, name, me, loc=c)
    me.materials.append(pick(mat))
    smooth(me)
    return o


def lathe(p, name, profile, mat, seg=48, loc=(0, 0, 0), rot=(0, 0, 0), sharp=35, solid=0.0):
    """Revolve an (r, z) profile around Z. solid>0 gives the shell a wall thickness."""
    verts, faces = [], []
    n = len(profile)
    for (r, z) in profile:
        for k in range(seg):
            a = 2 * math.pi * k / seg
            verts.append((max(r, 1e-5) * math.cos(a), max(r, 1e-5) * math.sin(a), z))
    for i in range(n - 1):
        for k in range(seg):
            faces.append((i * seg + k, i * seg + (k + 1) % seg, (i + 1) * seg + (k + 1) % seg, (i + 1) * seg + k))
    me = mesh_from(name, verts, faces)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bm.to_mesh(me)
    bm.free()
    o = add_obj(p, name, me, loc=loc, rot=rot)
    me.materials.append(pick(mat))
    smooth(me, sharp)
    if solid > 0:
        s = o.modifiers.new("solid", "SOLIDIFY")
        s.thickness = solid
        s.offset = -1
    return o


def torus(p, name, R, r, mat, loc=(0, 0, 0), rot=(0, 0, 0), seg=64, tube=16, flat=1.0):
    """Ring in the local XZ plane (axis along local Y). flat<1 squashes the tube along the axis."""
    verts, faces = [], []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        for j in range(tube):
            b = 2 * math.pi * j / tube
            rr = R + r * math.cos(b)
            verts.append((rr * math.cos(a), r * math.sin(b) * flat, rr * math.sin(a)))
    for i in range(seg):
        for j in range(tube):
            a, b = i * tube + j, i * tube + (j + 1) % tube
            c, d = ((i + 1) % seg) * tube + (j + 1) % tube, ((i + 1) % seg) * tube + j
            faces.append((a, d, c, b))
    me = mesh_from(name, verts, faces)
    o = add_obj(p, name, me, loc=loc, rot=rot)
    me.materials.append(pick(mat))
    smooth(me)
    return o


def quad(p, name, w, h, mat, loc, rot=(0, 0, 0)):
    """Image plane in local XZ facing local -Y; u runs along +X, v along +Z."""
    verts = [(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)]
    me = mesh_from(name, verts, [(0, 1, 2, 3)], uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
    o = add_obj(p, name, me, loc=loc, rot=rot)
    me.materials.append(mat)
    return o


def extrude(p, name, pts, depth, mat, loc=(0, 0, 0), rot=(0, 0, 0), rim_mat=None, bevel=0.0):
    """Extrude a 2D outline given in (y, z) along local X, centred on x=0. Caps get planar UVs."""
    n = len(pts)
    ys, zs = [q[0] for q in pts], [q[1] for q in pts]
    y0, y1, z0, z1 = min(ys), max(ys), min(zs), max(zs)
    verts, uvs = [], []
    for x in (-depth / 2, depth / 2):
        for (y, z) in pts:
            verts.append((x, y, z))
            uvs.append(((y - y0) / (y1 - y0), (z - z0) / (z1 - z0)))
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    ccw = area > 0                                    # seen from +X looking back at the YZ plane
    cap_hi = list(range(n, 2 * n))
    cap_lo = list(range(n))
    faces = [tuple(cap_hi if ccw else cap_hi[::-1]), tuple(cap_lo[::-1] if ccw else cap_lo)]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i) if ccw else (j, i, n + i, n + j))
    me = mesh_from(name, verts, faces, uvs=uvs)
    o = add_obj(p, name, me, loc=loc, rot=rot)
    me.materials.append(pick(mat))
    if rim_mat is not None:
        me.materials.append(pick(rim_mat))
        for poly in me.polygons[2:]:
            poly.material_index = 1
    if bevel > 0:
        b = o.modifiers.new("bevel", "BEVEL")
        b.width = bevel
        b.segments = 2
        b.limit_method = "ANGLE"
        b.angle_limit = math.radians(50)
        w = o.modifiers.new("wn", "WEIGHTED_NORMAL")
        w.keep_sharp = True
        smooth(me)
    return o


def tube(p, name, pts, r, mat, bezier=True, res=16, loc=(0, 0, 0), rot=(0, 0, 0)):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 5
    cu.resolution_u = res
    cu.use_fill_caps = True
    if bezier:
        sp = cu.splines.new("BEZIER")
        sp.bezier_points.add(len(pts) - 1)
        for bp, q in zip(sp.bezier_points, pts):
            bp.co = q
            bp.handle_left_type = bp.handle_right_type = "AUTO"
    else:
        sp = cu.splines.new("POLY")
        sp.points.add(len(pts) - 1)
        for sp_pt, q in zip(sp.points, pts):
            sp_pt.co = (q[0], q[1], q[2], 1.0)
    cu.materials.append(pick(mat))
    return add_obj(p, name, cu, loc=loc, rot=rot)


# ----------------------------------------------------------------------------- soft goods
def soft_box(p, name, lo, hi, mat, P=7.0, crown=0.012, lump=0.004, cuts=10, seed=0, rot=(0, 0, 0), lump_freq=3.0):
    """Upholstery block: rounded like a cushion, slightly crowned faces, gentle uneven lumps."""
    lo, hi = Vector(lo), Vector(hi)
    half = (hi - lo) / 2
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2.0)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=cuts, use_grid_fill=True)
    off = Vector((seed * 7.13, seed * 3.71, seed * 1.37))
    for v in bm.verts:
        q = v.co.copy()
        ax = max(range(3), key=lambda i: abs(q[i]))
        i, j = [k for k in range(3) if k != ax]
        nrm = (abs(q.x) ** P + abs(q.y) ** P + abs(q.z) ** P) ** (1.0 / P)
        s = q / nrm
        co = Vector((s.x * half.x, s.y * half.y, s.z * half.z))
        co[ax] += math.copysign(crown * (1 - q[i] ** 2) * (1 - q[j] ** 2), q[ax])
        if lump:
            d = Vector((s.x, s.y, s.z)).normalized()
            co += d * lump * noise.noise(co * lump_freq + off)
        v.co = co
    bm.to_mesh(me)
    bm.free()
    o = add_obj(p, name, me, loc=(lo + hi) / 2, rot=rot)
    me.materials.append(pick(mat))
    smooth(me)
    s = o.modifiers.new("sub", "SUBSURF")
    s.levels = 1
    s.render_levels = 1
    return o


def pillow(p, name, w, d, t, mat, loc, rot=(0, 0, 0), n=20, pinch=0.07, seed=0, prof=2.6, lump=0.006):
    """Sewn cushion: knife-edge seam, puffed middle, corners that stick out a little."""
    verts, faces = [], []
    off = Vector((seed * 5.3, seed * 2.1, seed * 9.7))

    def co(u, v, sgn):
        f = ((1 - abs(u) ** prof) * (1 - abs(v) ** prof)) ** 0.72
        x = w / 2 * u * (1 - pinch * (1 - v * v) * abs(u))
        y = d / 2 * v * (1 - pinch * (1 - u * u) * abs(v))
        z = sgn * t / 2 * f
        z += f * lump * noise.noise(Vector((x, y, sgn)) * 6.0 + off)
        return (x, y, z)
    for sgn in (1, -1):
        base = len(verts)
        for i in range(n + 1):
            for j in range(n + 1):
                verts.append(co(-1 + 2 * i / n, -1 + 2 * j / n, sgn))
        for i in range(n):
            for j in range(n):
                a, b = base + i * (n + 1) + j, base + (i + 1) * (n + 1) + j
                c, e = base + (i + 1) * (n + 1) + j + 1, base + i * (n + 1) + j + 1
                faces.append((a, b, c, e) if sgn > 0 else (a, e, c, b))
    me = mesh_from(name, verts, faces)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bm.to_mesh(me)
    bm.free()
    o = add_obj(p, name, me, loc=loc, rot=rot)
    me.materials.append(pick(mat))
    smooth(me, 60)
    return o


def drape(p, name, profile, width, mat, loc=(0, 0, 0), rot=(0, 0, 0), thick=0.012, n_w=10, seed=0, lump=0.006, res=6):
    """Cloth strip: an (x, z) path swept along local Y, with thickness and soft wrinkles."""
    path = []
    for a, b in zip(profile[:-1], profile[1:]):
        for k in range(res):
            t = k / res
            path.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    path.append(profile[-1])
    m = len(path)
    off = Vector((seed * 4.1, seed * 8.3, seed * 2.9))
    verts, faces = [], []
    for i, (x, z) in enumerate(path):
        for j in range(n_w + 1):
            y = -width / 2 + width * j / n_w
            wob = lump * noise.noise(Vector((x, y, z)) * 7.0 + off)
            verts.append((x + wob * 0.5, y + 0.4 * lump * noise.noise(Vector((x * 3, i * 0.31, 0)) + off), z + wob))
    for i in range(m - 1):
        for j in range(n_w):
            a = i * (n_w + 1) + j
            faces.append((a, a + n_w + 1, a + n_w + 2, a + 1))
    me = mesh_from(name, verts, faces)
    o = add_obj(p, name, me, loc=loc, rot=rot)
    me.materials.append(pick(mat))
    smooth(me)
    s = o.modifiers.new("solid", "SOLIDIFY")
    s.thickness = thick
    s.offset = 1
    ss = o.modifiers.new("sub", "SUBSURF")
    ss.levels = 2
    ss.render_levels = 2
    return o


def leaves(p, name, specs, mat, loc=(0, 0, 0)):
    """One mesh holding many leaves. Each spec: dict(base, yaw, tilt, length, width, bend, fold, shape, roll)."""
    verts, faces, uvs = [], [], []
    for sp in specs:
        L, W = sp["length"], sp["width"]
        nseg = sp.get("segs", 9)
        shape = sp.get("shape", "blade")
        rows = []
        ang, y, z = 0.0, 0.0, 0.0
        for i in range(nseg + 1):
            s = i / nseg
            if shape == "blade":            # sword leaf
                wv = W * (0.55 + 0.45 * math.sin(math.pi * min(1.0, s * 1.6) * 0.5)) * (1 - s ** 3) ** 0.75
            elif shape == "oval":           # broad leaf on a short stalk
                wv = W * math.sin(math.pi * (0.04 + 0.96 * s) ** 0.85) ** 0.8
            else:                           # heart
                wv = W * math.sin(math.pi * (0.1 + 0.9 * s) ** 0.65) ** 0.7
            rows.append((y, z, wv, s))
            ang += sp.get("bend", 0.0) / nseg
            y += math.cos(ang) * L / nseg
            z += math.sin(ang) * L / nseg * -1
        mat3 = (Matrix.Rotation(sp["yaw"], 4, "Z") @ Matrix.Rotation(sp.get("tilt", 0.0), 4, "X")
                @ Matrix.Rotation(sp.get("roll", 0.0), 4, "Y"))
        b0 = len(verts)
        fold = sp.get("fold", 0.15)
        for (yy, zz, wv, s) in rows:
            for k, u in enumerate((-1, 0, 1)):
                q = Vector((u * wv / 2, yy, zz + abs(u) * wv * fold))
                q = mat3 @ q + Vector(sp["base"])
                verts.append(q)
                uvs.append(((u + 1) / 2, s))
        for i in range(nseg):
            for k in range(2):
                a = b0 + i * 3 + k
                faces.append((a, a + 1, a + 4, a + 3))
    me = mesh_from(name, verts, faces, uvs=uvs)
    o = add_obj(p, name, me, loc=loc)
    me.materials.append(mat)
    smooth(me)
    s = o.modifiers.new("solid", "SOLIDIFY")
    s.thickness = 0.0025
    ss = o.modifiers.new("sub", "SUBSURF")
    ss.levels = 1
    ss.render_levels = 1
    return o


# ----------------------------------------------------------------------------- materials
class NT:
    def __init__(self, name):
        self.mat = bpy.data.materials.new(name)
        self.nt = self.mat.node_tree
        self.bsdf = next(n for n in self.nt.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
        self.out = next(n for n in self.nt.nodes if n.bl_idname == "ShaderNodeOutputMaterial")

    def n(self, idname, **props):
        node = self.nt.nodes.new(idname)
        for k, v in props.items():
            setattr(node, k, v)
        return node

    def link(self, a, b):
        self.nt.links.new(a, b)

    def set(self, **kw):
        for k, v in kw.items():
            self.bsdf.inputs[k.replace("_", " ")].default_value = v

    def math(self, op, a, b=None, clamp=False):
        node = self.n("ShaderNodeMath", operation=op, use_clamp=clamp)
        for idx, val in enumerate((a, b)):
            if val is None:
                continue
            if isinstance(val, (int, float)):
                node.inputs[idx].default_value = val
            else:
                self.link(val, node.inputs[idx])
        return node.outputs[0]

    def noise(self, vec, scale, detail=3.0, rough=0.55, distortion=0.0, w=None):
        node = self.n("ShaderNodeTexNoise", noise_dimensions="4D" if w is not None else "3D")
        if vec is not None:
            self.link(vec, node.inputs["Vector"])
        node.inputs["Scale"].default_value = scale
        node.inputs["Detail"].default_value = detail
        node.inputs["Roughness"].default_value = rough
        node.inputs["Distortion"].default_value = distortion
        if w is not None:
            self.link(w, node.inputs["W"])
        return node.outputs["Factor"]

    def obj_coords(self, scale=(1, 1, 1)):
        tc = self.n("ShaderNodeTexCoord")
        mp = self.n("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = scale
        self.link(tc.outputs["Object"], mp.inputs["Vector"])
        return mp.outputs["Vector"]

    def rand(self):
        return self.n("ShaderNodeObjectInfo").outputs["Random"]

    def ramp(self, fac, stops):
        node = self.n("ShaderNodeValToRGB")
        els = node.color_ramp.elements
        while len(els) < len(stops):
            els.new(0.5)
        for el, (pos, col) in zip(els, stops):
            el.position = pos
            el.color = col
        self.link(fac, node.inputs[0])
        return node.outputs["Color"]

    def value_mul(self, col, val):
        node = self.n("ShaderNodeHueSaturation")
        self.link(col, node.inputs["Color"])
        if isinstance(val, (int, float)):
            node.inputs["Value"].default_value = val
        else:
            self.link(val, node.inputs["Value"])
        return node.outputs["Color"]

    def bump(self, height, strength=0.3, distance=0.001):
        node = self.n("ShaderNodeBump")
        node.inputs["Strength"].default_value = strength
        node.inputs["Distance"].default_value = distance
        self.link(height, node.inputs["Height"])
        self.link(node.outputs["Normal"], self.bsdf.inputs["Normal"])
        return node

    def maprange(self, val, a, b, c, d, smooth=False):
        node = self.n("ShaderNodeMapRange")
        if smooth:
            node.interpolation_type = "SMOOTHSTEP"
        self.link(val, node.inputs["Value"])
        for key, v in (("From Min", a), ("From Max", b), ("To Min", c), ("To Max", d)):
            node.inputs[key].default_value = v
        return node.outputs["Result"]


def m_paint(name, hexcol, rough=0.82, var=0.035, bump=0.18):
    """Rolled wall paint: the stated colour, with faint roller texture so it does not look like a flat fill."""
    t = NT(name)
    base = hexlin(hexcol)
    co = t.obj_coords()
    big = t.noise(co, 0.9, 3, 0.5)
    t.link(t.value_mul(_rgb(t, base), t.maprange(big, 0.25, 0.75, 1 - var, 1 + var)), t.bsdf.inputs["Base Color"])
    fine = t.noise(co, 260.0, 2, 0.6)
    t.link(t.maprange(fine, 0, 1, rough - 0.06, rough + 0.06), t.bsdf.inputs["Roughness"])
    t.bump(fine, bump, 0.0006)
    return t.mat


def _rgb(t, col):
    node = t.n("ShaderNodeRGB")
    node.outputs[0].default_value = col
    return node.outputs[0]


def m_flat(name, hexcol, rough=0.6, metal=0.0, coat=0.0):
    t = NT(name)
    t.set(Base_Color=hexlin(hexcol), Roughness=rough, Metallic=metal)
    if coat:
        t.set(Coat_Weight=coat, Coat_Roughness=0.12)
    return t.mat


def m_fabric(name, hexcol, sheen=0.55, rough=0.9, var=0.07, weave=420.0, bump=0.35, sheen_tint=None, sheen_rough=0.5, fleck=0.0):
    """Woven cloth: soft sheen at grazing angles, thread-scale bump, and optional yarn flecks you can see up close."""
    t = NT(name)
    base = hexlin(hexcol)
    co = t.obj_coords()
    w4 = t.math("MULTIPLY", t.rand(), 40.0)
    mott = t.noise(co, 9.0, 4, 0.6, w=w4)
    val = t.maprange(mott, 0.2, 0.8, 1 - var, 1 + var)
    if fleck:
        fl = t.noise(t.obj_coords((260, 260, 260)), 1.0, 2, 0.8, w=w4)
        val = t.math("MULTIPLY", val, t.maprange(fl, 0.25, 0.75, 1 - fleck, 1 + fleck))
    t.link(t.value_mul(_rgb(t, base), val), t.bsdf.inputs["Base Color"])
    t.set(Roughness=rough, Sheen_Weight=sheen, Sheen_Roughness=sheen_rough)
    t.bsdf.inputs["Sheen Tint"].default_value = sheen_tint or (min(1, base[0] * 2.5 + 0.25), min(1, base[1] * 2.5 + 0.25),
                                                                min(1, base[2] * 2.5 + 0.25), 1)
    w = t.noise(t.obj_coords((weave, weave, weave)), 1.0, 2, 0.7)
    t.bump(w, bump, 0.0008)
    return t.mat


def m_knit(name, hexcol, rows=95.0, bump=1.0, direction="Z"):
    """Chunky knit: visible rows of stitches, deep soft relief."""
    t = NT(name)
    base = hexlin(hexcol)
    co = t.obj_coords()
    wv = t.n("ShaderNodeTexWave", wave_type="BANDS", bands_direction=direction, wave_profile="SIN")
    t.link(co, wv.inputs["Vector"])
    wv.inputs["Scale"].default_value = rows
    wv.inputs["Distortion"].default_value = 0.25
    wv.inputs["Detail"].default_value = 1.0
    wv.inputs["Detail Scale"].default_value = 3.0
    st = t.n("ShaderNodeTexVoronoi")
    t.link(t.obj_coords((rows * 1.6, rows * 1.6, rows * 0.55)), st.inputs["Vector"])
    h = t.math("ADD", t.math("MULTIPLY", wv.outputs["Factor"], 0.6), t.math("MULTIPLY", st.outputs["Distance"], 0.7))
    mott = t.noise(co, 7.0, 3, 0.6)
    val = t.math("MULTIPLY", t.maprange(mott, 0.2, 0.8, 0.9, 1.08), t.maprange(h, 0.2, 1.0, 0.72, 1.08))
    t.link(t.value_mul(_rgb(t, base), val), t.bsdf.inputs["Base Color"])
    t.set(Roughness=0.95, Sheen_Weight=0.8, Sheen_Roughness=0.55)
    t.bsdf.inputs["Sheen Tint"].default_value = (min(1, base[0] * 2 + 0.2), min(1, base[1] * 2 + 0.2), min(1, base[2] * 2 + 0.2), 1)
    t.bump(h, bump, 0.004)
    return t.mat


def m_wood(name, dark_hex, light_hex, rough=0.42, coat=0.0, along=2.2, across=38.0):
    """Returns grain-along-x / y / z variants; box() picks the one that follows the board."""
    out = {}
    for ax in "xyz":
        t = NT(name + "." + ax)
        sc = [across, across, across]
        sc["xyz".index(ax)] = along
        co = t.obj_coords(tuple(sc))
        w = t.math("MULTIPLY", t.rand(), 60.0)
        g = t.noise(co, 1.0, 5, 0.6, 0.9, w=w)
        col = t.ramp(g, [(0.28, hexlin(dark_hex)), (0.72, hexlin(light_hex))])
        t.link(col, t.bsdf.inputs["Base Color"])
        sc2 = [across * 9, across * 9, across * 9]
        sc2["xyz".index(ax)] = along * 4
        pores = t.noise(t.obj_coords(tuple(sc2)), 1.0, 2, 0.7, w=w)
        t.link(t.maprange(g, 0.2, 0.8, rough - 0.08, rough + 0.1), t.bsdf.inputs["Roughness"])
        h = t.math("ADD", t.math("MULTIPLY", g, 0.5), t.math("MULTIPLY", pores, 0.5))
        t.bump(h, 0.22, 0.0006)
        if coat:
            t.set(Coat_Weight=coat, Coat_Roughness=0.2)
        out[ax] = t.mat
    return out


def m_floor(name, L=1.3, rowH=0.14):
    """Oak plank floor: staggered boards, per-board tone, grain along the board, recessed seams, satin lacquer."""
    t = NT(name)
    tc = t.n("ShaderNodeTexCoord")
    sep = t.n("ShaderNodeSeparateXYZ")
    t.link(tc.outputs["Object"], sep.inputs[0])
    X, Y = sep.outputs["X"], sep.outputs["Y"]
    ry = t.math("DIVIDE", Y, rowH)
    row = t.math("FLOOR", ry)
    fy = t.math("FRACT", ry)
    wn1 = t.n("ShaderNodeTexWhiteNoise", noise_dimensions="1D")
    t.link(row, wn1.inputs["W"])
    px = t.math("ADD", t.math("DIVIDE", X, L), t.math("MULTIPLY", wn1.outputs["Value"], 7.31))
    colx = t.math("FLOOR", px)
    fx = t.math("FRACT", px)
    cmb = t.n("ShaderNodeCombineXYZ")
    t.link(colx, cmb.inputs[0])
    t.link(row, cmb.inputs[1])
    wn2 = t.n("ShaderNodeTexWhiteNoise", noise_dimensions="2D")
    t.link(cmb.outputs[0], wn2.inputs["Vector"])
    prand = wn2.outputs["Value"]
    dy = t.math("MULTIPLY", t.math("MINIMUM", fy, t.math("SUBTRACT", 1.0, fy)), rowH)
    dx = t.math("MULTIPLY", t.math("MINIMUM", fx, t.math("SUBTRACT", 1.0, fx)), L)
    seam = t.maprange(t.math("MINIMUM", dx, dy), 0.0, 0.0022, 0.0, 1.0, smooth=True)   # 0 in the gap, 1 on the board
    gv = t.n("ShaderNodeCombineXYZ")
    t.link(t.math("ADD", t.math("MULTIPLY", X, 2.0), t.math("MULTIPLY", prand, 41.0)), gv.inputs[0])
    t.link(t.math("ADD", t.math("MULTIPLY", Y, 42.0), t.math("MULTIPLY", row, 3.7)), gv.inputs[1])
    t.link(t.math("MULTIPLY", prand, 9.0), gv.inputs[2])
    g = t.noise(gv.outputs[0], 1.0, 5, 0.62, 1.1)
    col = t.ramp(g, [(0.25, hexlin("#A88B69")), (0.55, hexlin("#C2A47F")), (0.8, hexlin("#D6BA96"))])
    col = t.value_mul(col, t.maprange(prand, 0, 1, 0.84, 1.1))
    mix = t.n("ShaderNodeMix", data_type="RGBA")
    mix.inputs[6].default_value = hexlin("#3A2A1C")
    t.link(col, mix.inputs[7])
    t.link(seam, mix.inputs[0])
    t.link(mix.outputs[2], t.bsdf.inputs["Base Color"])
    pv = t.n("ShaderNodeCombineXYZ")
    t.link(t.math("MULTIPLY", X, 9.0), pv.inputs[0])
    t.link(t.math("MULTIPLY", Y, 520.0), pv.inputs[1])
    t.link(prand, pv.inputs[2])
    pores = t.noise(pv.outputs[0], 1.0, 2, 0.7)
    t.link(t.maprange(g, 0.2, 0.8, 0.3, 0.5), t.bsdf.inputs["Roughness"])
    h = t.math("ADD", t.math("MULTIPLY", seam, 1.0), t.math("ADD", t.math("MULTIPLY", g, 0.06), t.math("MULTIPLY", pores, 0.04)))
    t.bump(h, 0.5, 0.0012)
    t.set(Coat_Weight=0.3, Coat_Roughness=0.22)
    return t.mat


def m_metal(name, hexcol, rough=0.28, var=0.06, brushed=False):
    t = NT(name)
    t.set(Base_Color=hexlin(hexcol), Metallic=1.0)
    co = t.obj_coords((6, 6, 300) if brushed else (14, 14, 14))
    nz = t.noise(co, 1.0, 3, 0.6)
    t.link(t.maprange(nz, 0.2, 0.8, rough - var, rough + var), t.bsdf.inputs["Roughness"])
    return t.mat


def m_emit(name, hexcol, strength, base="#101010"):
    t = NT(name)
    t.set(Base_Color=hexlin(base), Roughness=0.4, Emission_Strength=strength)
    t.bsdf.inputs["Emission Color"].default_value = hexlin(hexcol)
    return t.mat


def _img(t, filename):
    node = t.n("ShaderNodeTexImage")
    node.image = bpy.data.images.load(os.path.join(TEX, filename), check_existing=True)
    node.extension = "EXTEND"
    return node


def m_screen(name, filename, strength=1.8):
    """A lit display: the picture is emitted, the glass in front of it stays glossy."""
    t = NT(name)
    im = _img(t, filename)
    t.set(Base_Color=(0.004, 0.004, 0.004, 1), Roughness=0.12, Emission_Strength=strength)
    t.link(im.outputs["Color"], t.bsdf.inputs["Emission Color"])
    return t.mat


def m_print(name, filename, rough=0.55, coat=0.0):
    """Ink on paper or card."""
    t = NT(name)
    im = _img(t, filename)
    t.link(im.outputs["Color"], t.bsdf.inputs["Base Color"])
    t.set(Roughness=rough)
    if coat:
        t.set(Coat_Weight=coat, Coat_Roughness=0.1)
    return t.mat


def m_glass(name, tint=(1, 1, 1, 1), rough=0.02):
    t = NT(name)
    t.set(Base_Color=tint, Roughness=rough, Transmission_Weight=1.0, IOR=1.5)
    return t.mat


def m_leaf(name, mid_hex, dark_hex, edge_hex=None, rough=0.32, bands=False):
    t = NT(name)
    uv = t.n("ShaderNodeTexCoord").outputs["UV"]
    sep = t.n("ShaderNodeSeparateXYZ")
    t.link(uv, sep.inputs[0])
    u, v = sep.outputs["X"], sep.outputs["Y"]
    r = t.rand()
    nz = t.noise(t.obj_coords((14, 14, 14)), 1.0, 3, 0.6)
    col = t.ramp(nz, [(0.3, hexlin(dark_hex)), (0.75, hexlin(mid_hex))])
    if bands:                                         # snake-plant cross banding
        cv = t.n("ShaderNodeCombineXYZ")
        t.link(t.math("MULTIPLY", v, 26.0), cv.inputs[1])
        t.link(t.math("MULTIPLY", u, 2.0), cv.inputs[0])
        bz = t.noise(cv.outputs[0], 1.0, 2, 0.7, 1.5)
        mixb = t.n("ShaderNodeMix", data_type="RGBA")
        t.link(t.maprange(bz, 0.42, 0.62, 0, 0.75, smooth=True), mixb.inputs[0])
        t.link(col, mixb.inputs[6])
        mixb.inputs[7].default_value = hexlin("#8FA77A")
        col = mixb.outputs[2]
    if edge_hex:
        edge = t.math("ABSOLUTE", t.math("SUBTRACT", u, 0.5))
        m = t.n("ShaderNodeMix", data_type="RGBA")
        t.link(t.maprange(edge, 0.33, 0.4, 0, 1, smooth=True), m.inputs[0])
        t.link(col, m.inputs[6])
        m.inputs[7].default_value = hexlin(edge_hex)
        col = m.outputs[2]
    else:                                             # pale midrib
        rib = t.math("ABSOLUTE", t.math("SUBTRACT", u, 0.5))
        m = t.n("ShaderNodeMix", data_type="RGBA")
        t.link(t.maprange(rib, 0.0, 0.05, 0.35, 0.0, smooth=True), m.inputs[0])
        t.link(col, m.inputs[6])
        m.inputs[7].default_value = hexlin("#9DBF7A")
        col = m.outputs[2]
    t.link(t.value_mul(col, t.maprange(r, 0, 1, 0.8, 1.15)), t.bsdf.inputs["Base Color"])
    t.set(Roughness=rough, Subsurface_Weight=0.0, Coat_Weight=0.25, Coat_Roughness=0.25)
    # thin leaves let some light through
    tr = t.n("ShaderNodeBsdfTranslucent")
    t.link(t.value_mul(col, 1.3), tr.inputs["Color"])
    mx = t.n("ShaderNodeMixShader")
    mx.inputs[0].default_value = 0.22
    t.link(t.bsdf.outputs[0], mx.inputs[1])
    t.link(tr.outputs[0], mx.inputs[2])
    t.link(mx.outputs[0], t.out.inputs["Surface"])
    return t.mat


def m_shade(name, hexcol, translucency=0.45):
    """Lamp shade fabric that glows when the bulb inside is on."""
    t = NT(name)
    base = hexlin(hexcol)
    t.set(Base_Color=base, Roughness=0.9, Sheen_Weight=0.3)
    w = t.noise(t.obj_coords((500, 500, 120)), 1.0, 2, 0.7)
    t.bump(w, 0.3, 0.0006)
    tr = t.n("ShaderNodeBsdfTranslucent")
    tr.inputs["Color"].default_value = base
    mx = t.n("ShaderNodeMixShader")
    mx.inputs[0].default_value = translucency
    t.link(t.bsdf.outputs[0], mx.inputs[1])
    t.link(tr.outputs[0], mx.inputs[2])
    t.link(mx.outputs[0], t.out.inputs["Surface"])
    return t.mat


def m_rug(name, hexcol, accent_hex=None):
    t = NT(name)
    base = hexlin(hexcol)
    co = t.obj_coords()
    mott = t.noise(co, 3.5, 4, 0.65)
    col = t.value_mul(_rgb(t, base), t.maprange(mott, 0.2, 0.8, 0.9, 1.06))
    if accent_hex:                                    # loose hand-knotted line pattern
        wv = t.n("ShaderNodeTexWave", wave_type="BANDS", bands_direction="DIAGONAL")
        t.link(co, wv.inputs["Vector"])
        wv.inputs["Scale"].default_value = 1.15
        wv.inputs["Distortion"].default_value = 2.4
        wv.inputs["Detail"].default_value = 1.5
        line = t.maprange(wv.outputs["Factor"], 0.9, 0.97, 0, 0.75, smooth=True)
        m = t.n("ShaderNodeMix", data_type="RGBA")
        t.link(line, m.inputs[0])
        t.link(col, m.inputs[6])
        m.inputs[7].default_value = hexlin(accent_hex)
        col = m.outputs[2]
    t.link(col, t.bsdf.inputs["Base Color"])
    t.set(Roughness=0.95, Sheen_Weight=0.8, Sheen_Roughness=0.6)
    pile = t.noise(t.obj_coords((330, 330, 330)), 1.0, 3, 0.8)
    loops = t.n("ShaderNodeTexVoronoi")
    t.link(t.obj_coords((150, 150, 150)), loops.inputs["Vector"])
    h = t.math("ADD", t.math("MULTIPLY", pile, 0.6), t.math("MULTIPLY", loops.outputs["Distance"], 0.8))
    t.bump(h, 0.9, 0.004)
    return t.mat


# ----------------------------------------------------------------------------- small set dressing
def books_row(p, name, origin, length, mats, depth=0.15, seed=0, along="x", lean_last=True, hmin=0.17, hmax=0.26):
    """Upright books. origin is the front-bottom start of the row: spines line up on it and the books run back from it.
    along="x": spines face -Y, books run +Y.   along="y": spines face +X, books run -X."""
    rnd = random.Random(seed)
    x = 0.0
    i = 0
    ox, oy, oz = origin
    while x < length - 0.02:
        w = rnd.uniform(0.016, 0.042)
        if x + w > length:
            break
        h = rnd.uniform(hmin, hmax)
        d = rnd.uniform(depth * 0.78, depth)
        mat = rnd.choice(mats)
        if along == "x":
            lo, hi = (ox + x, oy, oz), (ox + x + w, oy + d, oz + h)
        else:
            lo, hi = (ox - d, oy + x, oz), (ox, oy + x + w, oz + h)
        rot = (0, 0, 0)
        if lean_last and x + w * 2.2 > length and i > 2:
            rot = (0, math.radians(9), 0) if along == "x" else (math.radians(-9), 0, 0)
        box(p, "%s.%d" % (name, i), lo, hi, mat, bevel=0.0025, rot=rot)
        x += w + rnd.uniform(0.0, 0.003)
        i += 1
    return x


def books_stack(p, name, c, mats, n=3, seed=0, w=0.24, d=0.17):
    rnd = random.Random(seed)
    z = c[2]
    for i in range(n):
        h = rnd.uniform(0.022, 0.04)
        ww, dd = w * rnd.uniform(0.82, 1.0), d * rnd.uniform(0.85, 1.0)
        box(p, "%s.%d" % (name, i), (c[0] - ww / 2, c[1] - dd / 2, z), (c[0] + ww / 2, c[1] + dd / 2, z + h), rnd.choice(mats),
            bevel=0.003, rot=(0, 0, math.radians(rnd.uniform(-9, 9))))
        z += h
    return z
