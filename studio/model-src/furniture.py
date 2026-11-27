"""Everything that stands in the studio. Each builder makes one named piece (collection + root) at real-world size."""
import math
import random

import bpy

from lib import *  # noqa: F401,F403
from lib import (box, cyl, sphere, lathe, torus, quad, extrude, tube, soft_box, pillow, drape, leaves, piece, sub, add_obj,
                 books_row, books_stack, mesh_from)

PI = math.pi


def R(deg):
    return math.radians(deg)


def point_light(p, name, loc, power, color=(1.0, 0.78, 0.5), radius=0.03):
    L = bpy.data.lights.new(name, "POINT")
    L.energy = power
    L.color = color
    L.shadow_soft_size = radius
    return add_obj(p, name, L, loc=loc)


def no_shadow(o):
    o.visible_shadow = False
    return o


# ----------------------------------------------------------------------------- plants and small props
def pot(p, name, loc, r0, r1, h, mat, soil, wall=0.01):
    lathe(p, name, [(0.001, 0), (r0, 0), (r0 + 0.004, 0.006), (r1, h)], mat, loc=loc, solid=wall)
    cyl(p, name + ".Soil", (loc[0], loc[1], loc[2] + h * 0.86), (loc[0], loc[1], loc[2] + h * 0.9), r1 * 0.93, soil)


def mug(p, loc, mat, dark):
    x, y, z = loc
    lathe(p, "Mug", [(0.001, 0), (0.034, 0), (0.038, 0.004), (0.038, 0.088)], mat, loc=loc, solid=0.004)
    torus(p, "MugHandle", 0.022, 0.0048, mat, loc=(x + 0.05, y, z + 0.046), seg=24, tube=10)
    cyl(p, "Coffee", (x, y, z + 0.07), (x, y, z + 0.074), 0.034, dark)


def pothos(p, name, loc, M, seed=0, vines=((-90, 0.34),), n_top=14, scale=1.0):
    """Leafy pot plant; vines = (direction in degrees, hang length) for trailing stems."""
    rnd = random.Random(seed)
    specs = []
    x0, y0, z0 = loc
    for i in range(n_top):
        a = i * 2.39996 + rnd.uniform(-0.3, 0.3)
        rr = rnd.uniform(0.0, 0.03) * scale
        specs.append(dict(base=(x0 + rr * math.cos(a), y0 + rr * math.sin(a), z0), yaw=a - PI / 2,
                          tilt=R(rnd.uniform(18, 68)), length=rnd.uniform(0.07, 0.11) * scale, width=rnd.uniform(0.045, 0.065) * scale,
                          bend=rnd.uniform(0.5, 1.3), fold=0.12, shape="heart", roll=rnd.uniform(-0.3, 0.3), segs=6))
    for k, (deg, hang) in enumerate(vines):
        a = R(deg)
        dx, dy = math.cos(a), math.sin(a)
        pts = [(x0, y0, z0 + 0.01), (x0 + dx * 0.07, y0 + dy * 0.07, z0 + 0.02), (x0 + dx * 0.115, y0 + dy * 0.115, z0 - 0.06),
               (x0 + dx * 0.12, y0 + dy * 0.12, z0 - hang * 0.55), (x0 + dx * 0.115, y0 + dy * 0.115, z0 - hang)]
        tube(p, "%s.Vine%d" % (name, k), pts, 0.0022, M.leaf_soft)
        m = int(hang / 0.045)
        for j in range(m):
            t = (j + 1) / (m + 1)
            z = z0 - 0.04 - (hang - 0.04) * t
            side = 1 if j % 2 == 0 else -1
            ya = a - PI / 2 + side * rnd.uniform(0.5, 1.2)
            specs.append(dict(base=(x0 + dx * 0.118, y0 + dy * 0.118, z), yaw=ya, tilt=R(rnd.uniform(-70, -35)),
                              length=rnd.uniform(0.06, 0.085) * scale, width=rnd.uniform(0.04, 0.055) * scale,
                              bend=rnd.uniform(-0.2, 0.4), fold=0.1, shape="heart", roll=rnd.uniform(-0.4, 0.4), segs=5))
    leaves(p, name + ".Leaves", specs, M.leaf_soft)


def succulent(p, name, loc, M, seed=0, scale=1.0):
    rnd = random.Random(seed)
    specs = []
    for ring, (n, tilt, ln) in enumerate([(7, 20, 0.07), (6, 45, 0.06), (5, 70, 0.045)]):
        for i in range(n):
            a = i * 2 * PI / n + ring * 0.5 + rnd.uniform(-0.15, 0.15)
            specs.append(dict(base=loc, yaw=a, tilt=R(tilt + rnd.uniform(-6, 6)), length=ln * scale, width=0.028 * scale,
                              bend=-0.5, fold=0.3, shape="blade", segs=5))
    leaves(p, name, specs, M.leaf_snake)


# ----------------------------------------------------------------------------- lounge
def rug(M):
    p = piece("Rug")
    box(p, "Rug", (0.85, 0.42, 0), (3.72, 3.0, 0.016), M.rug, bevel=0.007, seg=3)
    return p


def sofa(M):
    p = piece("Sofa", (3.41, 1.7, 0), rz=-PI / 2)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl(p, "Leg", (sx * 0.98, sy * 0.36, 0), (sx * 0.98, sy * 0.36, 0.125), 0.017, M.brass, r2=0.023)
    soft_box(p, "Base", (-1.08, -0.44, 0.12), (1.08, 0.44, 0.27), M.sofa, P=10, crown=0.003, lump=0.002, seed=1)
    soft_box(p, "ArmL", (-1.10, -0.46, 0.12), (-0.92, 0.46, 0.61), M.sofa, P=6, crown=0.008, lump=0.003, seed=2)
    soft_box(p, "ArmR", (0.92, -0.46, 0.12), (1.10, 0.46, 0.61), M.sofa, P=6, crown=0.008, lump=0.003, seed=3)
    soft_box(p, "Back", (-0.92, 0.26, 0.25), (0.92, 0.46, 0.71), M.sofa, P=6, crown=0.008, lump=0.003, seed=4)
    soft_box(p, "SeatL", (-0.915, -0.455, 0.27), (-0.005, 0.27, 0.445), M.sofa, P=6, crown=0.016, lump=0.005, seed=5)
    soft_box(p, "SeatR", (0.005, -0.455, 0.27), (0.915, 0.27, 0.445), M.sofa, P=6, crown=0.016, lump=0.005, seed=6)
    for i, x0 in enumerate((-0.91, 0.01)):
        soft_box(p, "BackCushion%d" % i, (x0, 0.10, 0.44), (x0 + 0.90, 0.28, 0.85), M.sofa, P=5, crown=0.02, lump=0.006,
                 seed=7 + i, rot=(R(-10), 0, 0))
    pillow(p, "PillowGold", 0.46, 0.46, 0.19, M.gold_velvet, (-0.60, 0.0, 0.672), rot=(R(74), 0, R(7)), seed=1, prof=2.2)
    pillow(p, "PillowGreen", 0.44, 0.44, 0.19, M.green_velvet, (0.63, -0.02, 0.662), rot=(R(70), 0, R(-28)), seed=2, prof=2.2)
    return p


def coffee_table(M):
    p = piece("CoffeeTable", (1.85, 1.7, 0))
    box(p, "Top", (-0.31, -0.575, 0.365), (0.31, 0.575, 0.40), M.walnut, bevel=0.008, seg=3)
    box(p, "Shelf", (-0.265, -0.53, 0.13), (0.265, 0.53, 0.148), M.walnut, bevel=0.004)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(p, "Leg", (sx * 0.28 - 0.009, sy * 0.545 - 0.009, 0), (sx * 0.28 + 0.009, sy * 0.545 + 0.009, 0.365), M.brass,
                bevel=0.002)
    for sy in (-1, 1):
        box(p, "RailX", (-0.28, sy * 0.545 - 0.007, 0.347), (0.28, sy * 0.545 + 0.007, 0.365), M.brass, bevel=0.002)
    for sx in (-1, 1):
        box(p, "RailY", (sx * 0.28 - 0.007, -0.545, 0.347), (sx * 0.28 + 0.007, 0.545, 0.365), M.brass, bevel=0.002)
    z = books_stack(p, "Books", (0.03, 0.30, 0.40), [M.books[0], M.books[3], M.books[1]], n=2, seed=4, w=0.27, d=0.2)
    lathe(p, "Bowl", [(0.001, 0.0), (0.035, 0.0), (0.072, 0.03), (0.08, 0.048)], M.brass, loc=(0.03, 0.30, z), solid=0.004)
    mug(p, (-0.12, -0.02, 0.40), M.ceramic_cream, M.soil)
    books_stack(p, "ShelfBooks", (0.0, -0.2, 0.148), [M.books[5], M.books[4], M.books[6]], n=3, seed=9, w=0.3, d=0.22)
    r = piece("Remote", (1.80, 1.33, 0.40), rz=R(-28))
    box(r, "Body", (-0.023, -0.085, 0), (0.023, 0.085, 0.016), M.plastic, bevel=0.005, seg=3)
    quad(r, "Buttons", 0.04, 0.16, M.remote, (0, 0, 0.0166), rot=(R(-90), 0, 0))
    return p


def media_console(M):
    p = piece("Console", (0.26, 1.7, 0), rz=PI / 2)
    box(p, "Body", (-1.0, -0.20, 0.15), (1.0, 0.21, 0.56), M.walnut, bevel=0.006)
    for i in range(4):
        x0 = -0.99 + i * 0.4975
        box(p, "Door%d" % i, (x0 + 0.004, -0.214, 0.166), (x0 + 0.4935, -0.198, 0.544), M.powder, bevel=0.003)
        xk = x0 + (0.455 if i % 2 == 0 else 0.042)
        cyl(p, "Knob%d" % i, (xk, -0.198, 0.50), (xk, -0.232, 0.50), 0.009, M.brass)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl(p, "Leg", (sx * 0.95, sy * 0.17, 0), (sx * 0.9, sy * 0.15, 0.15), 0.011, M.brass, r2=0.017)
    box(p, "GameBox", (-0.84, -0.11, 0.56), (-0.54, 0.09, 0.604), M.plastic, bevel=0.006, seg=3)
    box(p, "GameBoxStripe", (-0.84, -0.111, 0.575), (-0.54, -0.109, 0.583), M.gold_paint, bevel=0)
    for i, m in enumerate((M.gold_paint, M.green_paint)):
        cyl(p, "GameBtn%d" % i, (-0.60 - i * 0.045, -0.05, 0.604), (-0.60 - i * 0.045, -0.05, 0.609), 0.012, m)
    z = books_stack(p, "Books", (-0.22, 0.0, 0.56), [M.books[1], M.books[3], M.books[4]], n=3, seed=2, w=0.28, d=0.2)
    sphere(p, "Orb", (-0.22, 0.0, z + 0.045), 0.045, M.brass)
    pot(p, "Pot", (0.74, 0.03, 0.56), 0.065, 0.085, 0.15, M.ceramic_cream, M.soil)
    pothos(p, "Pothos", (0.74, 0.03, 0.70), M, seed=5, vines=((-90, 0.3), (-40, 0.22)), n_top=16, scale=1.15)
    return p


def tv(M):
    p = piece("TV", (0.115, 1.7, 1.42), rz=PI / 2)
    box(p, "Body", (-0.735, 0.0, -0.425), (0.735, 0.035, 0.425), M.gloss, bevel=0.006, seg=3)
    quad(p, "Screen", 1.44, 0.81, M.tv, (0, -0.0008, 0))
    box(p, "Mount", (-0.2, 0.035, -0.15), (0.2, 0.083, 0.15), M.powder, bevel=0.003)
    for i, (lo, hi) in enumerate([((-0.66, 0.036, 0.37), (0.66, 0.046, 0.385)), ((-0.66, 0.036, -0.385), (0.66, 0.046, -0.37)),
                                  ((-0.70, 0.036, -0.36), (-0.685, 0.046, 0.36)), ((0.685, 0.036, -0.36), (0.70, 0.046, 0.36))]):
        box(p, "Backlight%d" % i, lo, hi, M.led, bevel=0)
    return p


def arc_lamp(M):
    p = piece("ArcLamp", (3.52, 3.16, 0))
    lathe(p, "Base", [(0.001, 0), (0.17, 0), (0.18, 0.008), (0.18, 0.032), (0.172, 0.04), (0.001, 0.04)], M.base)
    hx, hy, hz = -0.77, -1.81, 1.30
    tube(p, "Stem", [(0, 0, 0.04), (0, 0, 0.95), (-0.05, -0.12, 1.60), (-0.27, -0.64, 1.94), (-0.58, -1.37, 1.82), (hx, hy, hz + 0.15)],
         0.011, M.brass)
    lathe(p, "Shade", [(0.17, 0.0), (0.166, 0.03), (0.15, 0.07), (0.12, 0.105), (0.07, 0.132), (0.02, 0.145), (0.001, 0.15)], M.brass,
          loc=(hx, hy, hz), solid=0.004)
    no_shadow(sphere(p, "Bulb", (hx, hy, hz + 0.05), 0.04, M.bulb))
    point_light(p, "Glow", (hx, hy, hz + 0.02), 110)
    return p


def sofa_console(M):
    p = piece("SofaConsole", (4.07, 1.7, 0))
    box(p, "Top", (-0.15, -0.95, 0.765), (0.15, 0.95, 0.80), M.walnut, bevel=0.006, seg=3)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(p, "Leg", (sx * 0.125 - 0.009, sy * 0.92 - 0.009, 0), (sx * 0.125 + 0.009, sy * 0.92 + 0.009, 0.765), M.brass, bevel=0.002)
    for sy in (-1, 1):
        box(p, "Stretcher", (-0.125, sy * 0.92 - 0.007, 0.12), (0.125, sy * 0.92 + 0.007, 0.134), M.brass, bevel=0.002)
    box(p, "Rail", (-0.007, -0.92, 0.12), (0.007, 0.92, 0.134), M.brass, bevel=0.002)
    # the ebook on a small brass easel, turned a little toward the open side of the room
    k = 1.35
    e = piece("Ebook", (4.07, 1.30, 0.80), rz=R(68))
    tube(e, "EaselFront", [(-0.075 * k, 0, 0), (0, 0.03 * k, 0.25 * k), (0.075 * k, 0, 0)], 0.004, M.brass, bezier=False)
    tube(e, "EaselBack", [(0, 0.03 * k, 0.25 * k), (0, 0.13 * k, 0)], 0.004, M.brass, bezier=False)
    box(e, "EaselLip", (-0.085 * k, -0.045 * k, 0.03 * k), (0.085 * k, -0.004 * k, 0.036 * k), M.brass, bevel=0.001)
    b = sub(e, "Book", (0, -0.037 * k, 0.036 * k), (R(-15), 0, 0))
    box(b, "Block", (-0.0715 * k, 0.0, 0.0), (0.0715 * k, 0.026, 0.232 * k), M.paper, bevel=0.002)
    box(b, "Jacket", (-0.0735 * k, -0.002, -0.001), (0.0735 * k, 0.028, 0.234 * k), M.books[0], bevel=0.002,
        face_mats={"+z": M.paper, "-z": M.paper, "+x": M.paper})
    quad(b, "Cover", 0.1456 * k, 0.233 * k, M.cover, (0.0, -0.0027, 0.1165 * k))
    # dressing
    pot(p, "Pot", (0.0, 0.34, 0.80), 0.045, 0.06, 0.09, M.brass, M.soil, wall=0.005)
    succulent(p, "Succulent", (0.0, 0.34, 0.885), M, seed=3, scale=1.2)
    z = books_stack(p, "Books", (0.0, -0.05, 0.80), [M.books[2], M.books[3], M.books[1]], n=3, seed=6, w=0.2, d=0.26)
    # little dome lamp
    lathe(p, "LampBase", [(0.001, 0), (0.05, 0), (0.055, 0.008), (0.02, 0.03), (0.012, 0.05), (0.012, 0.15)], M.brass, loc=(0.0, 0.78, 0.80))
    lathe(p, "LampDome", [(0.085, 0.0), (0.082, 0.03), (0.065, 0.062), (0.035, 0.08), (0.001, 0.086)], M.shade, loc=(0.0, 0.78, 0.93), solid=0.003)
    no_shadow(sphere(p, "LampBulb", (0.0, 0.78, 0.955), 0.022, M.bulb))
    point_light(p, "LampGlow", (0.0, 0.78, 0.95), 9)
    return p


# ----------------------------------------------------------------------------- sleep
def bed(M):
    p = piece("Bed", (4.96, 4.11, 0))
    box(p, "Plinth", (-0.74, -0.95, 0), (0.74, 0.96, 0.10), M.powder, bevel=0.004)
    box(p, "Frame", (-0.84, -1.06, 0.10), (0.84, 1.0, 0.28), M.walnut, bevel=0.012, seg=3)
    n = 7
    w = 1.80 / n
    for i in range(n):
        x0 = -0.90 + i * w
        soft_box(p, "Headboard%d" % i, (x0 + 0.002, 0.955, 0.14), (x0 + w - 0.002, 1.07, 1.08), M.headboard, P=4.5, crown=0.012,
                 lump=0.002, seed=20 + i, cuts=8)
    soft_box(p, "Mattress", (-0.80, -1.02, 0.28), (0.80, 0.95, 0.505), M.cotton, P=10, crown=0.008, lump=0.003, seed=30, cuts=12)
    soft_box(p, "Duvet", (-0.865, -1.075, 0.33), (0.865, 0.24, 0.59), M.linen, P=5, crown=0.02, lump=0.012, seed=31, cuts=16, lump_freq=2.4)
    soft_box(p, "DuvetFold", (-0.865, 0.14, 0.525), (0.865, 0.36, 0.625), M.cotton, P=3, crown=0.006, lump=0.008, seed=32, cuts=14, lump_freq=3.0)
    pillow(p, "PillowL", 0.72, 0.46, 0.17, M.cotton, (-0.40, 0.80, 0.725), rot=(R(62), 0, R(3)), seed=11, pinch=0.05)
    pillow(p, "PillowR", 0.72, 0.46, 0.17, M.cotton, (0.40, 0.81, 0.725), rot=(R(60), 0, R(-4)), seed=12, pinch=0.05)
    pillow(p, "PillowCharcoal", 0.48, 0.48, 0.15, M.sofa, (-0.30, 0.61, 0.735), rot=(R(68), 0, R(-6)), seed=13)
    pillow(p, "PillowGold", 0.52, 0.28, 0.12, M.gold_velvet, (0.16, 0.50, 0.65), rot=(R(64), 0, R(8)), seed=14)
    prof = [(-0.905, 0.25), (-0.90, 0.50), (-0.86, 0.615), (-0.5, 0.64), (0.0, 0.652), (0.5, 0.64), (0.86, 0.615), (0.90, 0.50),
            (0.91, 0.21)]
    drape(p, "Throw", prof, 0.62, M.green_throw, loc=(0, -0.62, 0), rot=(0, 0, R(2.5)), thick=0.014, seed=3, lump=0.007)
    return p


def bench(M):
    p = piece("Bench", (4.96, 2.74, 0))
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl(p, "Leg", (sx * 0.54, sy * 0.15, 0), (sx * 0.52, sy * 0.14, 0.30), 0.011, M.brass, r2=0.016)
    box(p, "Frame", (-0.60, -0.19, 0.30), (0.60, 0.19, 0.345), M.walnut, bevel=0.006, seg=3)
    soft_box(p, "Cushion", (-0.59, -0.185, 0.345), (0.59, 0.185, 0.445), M.linen, P=6, crown=0.012, lump=0.004, seed=51, cuts=12)
    prof = [(-0.196, 0.30), (-0.192, 0.42), (-0.15, 0.458), (0.0, 0.466), (0.15, 0.458), (0.192, 0.42), (0.198, 0.27)]
    drape(p, "Throw", prof, 0.34, M.gold_velvet, loc=(0.33, 0, 0), rot=(0, 0, R(90 + 3)), thick=0.016, seed=8, lump=0.005)
    books_stack(p, "Books", (-0.30, 0.0, 0.452), [M.books[1], M.books[3]], n=2, seed=12, w=0.24, d=0.18)
    return p


def pouf(M):
    p = piece("Pouf", (1.95, 0.74, 0.016))
    prof = [(0.001, 0.0)]
    for i in range(1, 16):                              # squashed ball
        a = -math.pi / 2 + math.pi * i / 16
        prof.append((0.245 * math.cos(a) ** 0.7, 0.17 + 0.17 * math.sin(a)))
    prof.append((0.001, 0.34))
    lathe(p, "Pouf", prof, M.green_knit, sharp=80)
    return p


def nightstand(M):
    p = piece("Nightstand", (3.745, 4.955, 0))
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl(p, "Leg", (sx * 0.19, sy * 0.175, 0), (sx * 0.19, sy * 0.175, 0.12), 0.012, M.brass, r2=0.016)
    box(p, "Body", (-0.225, -0.20, 0.12), (0.225, 0.21, 0.50), M.walnut, bevel=0.006)
    box(p, "DrawerTop", (-0.215, -0.212, 0.315), (0.215, -0.198, 0.49), M.walnut, bevel=0.003)
    box(p, "DrawerLow", (-0.215, -0.212, 0.13), (0.215, -0.198, 0.305), M.walnut, bevel=0.003)
    for z in (0.40, 0.22):
        cyl(p, "Knob", (0, -0.212, z), (0, -0.232, z), 0.01, M.brass)
    lathe(p, "LampBase", [(0.001, 0), (0.062, 0), (0.066, 0.01), (0.03, 0.035), (0.012, 0.07), (0.011, 0.25)], M.brass,
          loc=(-0.06, 0.04, 0.50))
    lathe(p, "LampShade", [(0.115, 0.0), (0.085, 0.18)], M.shade, loc=(-0.06, 0.04, 0.72), solid=0.002, sharp=80)
    no_shadow(sphere(p, "LampBulb", (-0.06, 0.04, 0.80), 0.028, M.bulb))
    point_light(p, "LampGlow", (-0.06, 0.04, 0.80), 16)
    books_stack(p, "Books", (0.11, -0.07, 0.50), [M.books[4], M.books[3]], n=2, seed=8, w=0.15, d=0.21)
    return p


def poster(M):
    p = piece("Poster", (4.96, 5.2, 1.80))
    W, H, bar, dep = 0.74, 1.04, 0.022, 0.032
    box(p, "Mat", (-W / 2 + 0.01, -0.012, -H / 2 + 0.01), (W / 2 - 0.01, -0.003, H / 2 - 0.01), M.paper, bevel=0)
    quad(p, "Art", 0.58, 0.83, M.poster, (0, -0.0125, 0))
    box(p, "FrameT", (-W / 2, -dep, H / 2 - bar), (W / 2, 0, H / 2), M.brass_brushed, bevel=0.002)
    box(p, "FrameB", (-W / 2, -dep, -H / 2), (W / 2, 0, -H / 2 + bar), M.brass_brushed, bevel=0.002)
    box(p, "FrameL", (-W / 2, -dep, -H / 2 + bar), (-W / 2 + bar, 0, H / 2 - bar), M.brass_brushed, bevel=0.002)
    box(p, "FrameR", (W / 2 - bar, -dep, -H / 2 + bar), (W / 2, 0, H / 2 - bar), M.brass_brushed, bevel=0.002)
    return p


# ----------------------------------------------------------------------------- work
def desk(M):
    p = piece("Desk", (2.05, 4.825, 0))
    box(p, "Top", (-0.80, -0.345, 0.715), (0.80, 0.345, 0.75), M.walnut, bevel=0.007, seg=3)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(p, "Leg", (sx * 0.74 - 0.016, sy * 0.30 - 0.016, 0), (sx * 0.74 + 0.016, sy * 0.30 + 0.016, 0.715), M.powder, bevel=0.003)
        box(p, "SideRail", (sx * 0.74 - 0.014, -0.30, 0.67), (sx * 0.74 + 0.014, 0.30, 0.715), M.powder, bevel=0.003)
        box(p, "FootRail", (sx * 0.74 - 0.012, -0.30, 0.10), (sx * 0.74 + 0.012, 0.30, 0.124), M.powder, bevel=0.003)
    box(p, "BackRail", (-0.74, 0.288, 0.40), (0.74, 0.312, 0.44), M.powder, bevel=0.003)
    box(p, "Drawer", (0.30, -0.30, 0.52), (0.70, 0.30, 0.713), M.walnut, bevel=0.004)
    box(p, "DrawerFront", (0.305, -0.312, 0.527), (0.695, -0.30, 0.706), M.walnut, bevel=0.003)
    box(p, "DrawerPull", (0.44, -0.326, 0.61), (0.56, -0.312, 0.622), M.brass, bevel=0.002)
    # laptop: its own piece so it can be a clickable object later
    lp = piece("Laptop", (2.0, 4.80, 0.75))
    box(lp, "Base", (-0.17, -0.1175, 0), (0.17, 0.1175, 0.013), M.alu, bevel=0.004, seg=3)
    quad(lp, "Keys", 0.326, 0.218, M.keys, (0, -0.002, 0.0134), rot=(R(-90), 0, 0))
    lid = sub(lp, "Lid", (0, 0.1175, 0.012), (R(-17), 0, 0))
    box(lid, "Shell", (-0.17, 0.0, 0.0), (0.17, 0.007, 0.228), M.alu, bevel=0.003, seg=3)
    quad(lid, "Display", 0.322, 0.204, M.laptop, (0, -0.0006, 0.118))
    # desk lamp (brass)
    lathe(p, "LampBase", [(0.001, 0), (0.075, 0), (0.078, 0.008), (0.078, 0.018), (0.001, 0.02)], M.brass, loc=(-0.62, 0.17, 0.75))
    tube(p, "LampArm", [(-0.62, 0.17, 0.77), (-0.62, 0.20, 1.08), (-0.50, 0.10, 1.19)], 0.006, M.brass, bezier=False)
    hd = sub(p, "LampHead", (-0.50, 0.10, 1.19), (R(30), R(-35), 0))
    lathe(hd, "Cone", [(0.02, 0.03), (0.03, 0.0), (0.075, -0.09)], M.brass, solid=0.003)
    no_shadow(sphere(hd, "Bulb", (0, 0, -0.045), 0.02, M.bulb))
    # microphone on a short stand
    lathe(p, "MicBase", [(0.001, 0), (0.055, 0), (0.058, 0.006), (0.058, 0.012), (0.001, 0.014)], M.powder, loc=(0.50, 0.12, 0.75))
    cyl(p, "MicPole", (0.50, 0.12, 0.762), (0.50, 0.12, 0.90), 0.006, M.powder)
    mh = sub(p, "MicHead", (0.50, 0.12, 0.90), (R(55), 0, R(-25)))
    cyl(mh, "Body", (0, 0, -0.03), (0, 0, 0.11), 0.027, M.plastic)
    cyl(mh, "Ring", (0, 0, 0.045), (0, 0, 0.055), 0.0285, M.brass)
    sphere(mh, "Grille", (0, 0, 0.11), 0.027, M.alu)
    # small things
    mug(p, (0.30, -0.16, 0.75), M.ceramic_charcoal, M.soil)
    box(p, "Notebook", (-0.50, -0.27, 0.75), (-0.345, -0.06, 0.763), M.books[0], bevel=0.003, rot=(0, 0, R(12)))
    cyl(p, "Pen", (-0.32, -0.25, 0.756), (-0.27, -0.11, 0.756), 0.004, M.brass)
    pot(p, "Pot", (0.68, 0.22, 0.75), 0.04, 0.052, 0.075, M.gold_paint, M.soil, wall=0.005)
    succulent(p, "Succulent", (0.68, 0.22, 0.82), M, seed=1)
    return p


def shelves(M):
    p = piece("Shelves", (2.05, 5.09, 0))
    for k, z in enumerate((1.36, 1.80)):
        box(p, "Board%d" % k, (-0.70, -0.11, z), (0.70, 0.11, z + 0.03), M.walnut, bevel=0.005)
        for sx in (-1, 1):
            box(p, "Bracket%d" % k, (sx * 0.58 - 0.004, -0.09, z - 0.012), (sx * 0.58 + 0.004, 0.11, z), M.brass, bevel=0.001)
            box(p, "BracketV%d" % k, (sx * 0.58 - 0.004, 0.098, z - 0.13), (sx * 0.58 + 0.004, 0.11, z), M.brass, bevel=0.001)
    box(p, "LED", (-0.64, -0.098, 1.352), (0.64, -0.088, 1.36), M.led, bevel=0)
    z1, z2 = 1.39, 1.83
    books_row(p, "RowA", (-0.66, -0.085, z1), 0.46, M.books, depth=0.16, seed=11)
    # camera
    box(p, "CamBody", (-0.10, -0.06, z1), (0.03, 0.01, z1 + 0.085), M.plastic, bevel=0.006, seg=3)
    cyl(p, "CamLens", (-0.035, -0.06, z1 + 0.042), (-0.035, -0.125, z1 + 0.042), 0.034, M.plastic)
    cyl(p, "CamRing", (-0.035, -0.118, z1 + 0.042), (-0.035, -0.127, z1 + 0.042), 0.036, M.brass)
    cyl(p, "CamGlass", (-0.035, -0.127, z1 + 0.042), (-0.035, -0.129, z1 + 0.042), 0.027, M.gloss)
    box(p, "CamTop", (-0.02, -0.045, z1 + 0.085), (0.02, -0.005, z1 + 0.10), M.plastic, bevel=0.003)
    # leaning framed print
    fr = sub(p, "Print", (0.26, 0.085, z1), (R(-9), 0, 0))
    box(fr, "Frame", (-0.085, -0.012, 0.0), (0.085, 0.0, 0.215), M.powder, bevel=0.002)
    quad(fr, "Art", 0.15, 0.19, M.art[0], (0, -0.0125, 0.108))
    pot(p, "Pot", (0.56, -0.01, z1), 0.05, 0.062, 0.10, M.ceramic_cream, M.soil)
    pothos(p, "Pothos", (0.56, -0.01, z1 + 0.09), M, seed=2, vines=((-90, 0.42), (-55, 0.3)), n_top=14)
    # upper shelf
    z = books_stack(p, "StackA", (-0.50, -0.01, z2), [M.books[1], M.books[2], M.books[3], M.books[4]], n=3, seed=3, w=0.25, d=0.17)
    sphere(p, "Orb", (-0.50, -0.01, z + 0.04), 0.04, M.brass)
    books_row(p, "RowB", (-0.22, -0.085, z2), 0.42, M.books, depth=0.16, seed=17)
    box(p, "Speaker", (0.36, -0.085, z2), (0.52, 0.06, z2 + 0.20), M.plastic, bevel=0.012, seg=3)
    cyl(p, "SpeakerCone", (0.44, -0.085, z2 + 0.075), (0.44, -0.09, z2 + 0.075), 0.05, M.felt)
    cyl(p, "SpeakerTweeter", (0.44, -0.085, z2 + 0.155), (0.44, -0.09, z2 + 0.155), 0.02, M.brass)
    return p


def chair(M):
    p = piece("Chair", (1.98, 3.92, 0), rz=R(180 + 16))
    soft_box(p, "Seat", (-0.24, -0.24, 0.40), (0.24, 0.24, 0.495), M.gold_velvet, P=5, crown=0.014, lump=0.003, seed=41)
    soft_box(p, "Back", (-0.235, 0.17, 0.52), (0.235, 0.255, 0.88), M.gold_velvet, P=4, crown=0.016, lump=0.003, seed=42,
             rot=(R(-11), 0, 0))
    box(p, "SeatPan", (-0.215, -0.215, 0.375), (0.215, 0.215, 0.405), M.powder, bevel=0.006)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl(p, "Leg", (sx * 0.25, sy * 0.25, 0), (sx * 0.19, sy * 0.19, 0.385), 0.010, M.powder, r2=0.016)
        cyl(p, "BackPost", (sx * 0.17, 0.215, 0.39), (sx * 0.17, 0.26, 0.60), 0.011, M.powder)
    return p


# ----------------------------------------------------------------------------- play
ARCADE_PROFILE = [(-0.36, 0.0), (-0.36, 0.80), (-0.46, 0.88), (-0.46, 0.95), (-0.24, 1.04), (-0.17, 1.52), (-0.34, 1.60),
                  (-0.34, 1.82), (0.40, 1.82), (0.40, 0.0)]


def arcade(M):
    p = piece("Arcade", (0.45, 4.78, 0))
    inner = [(y * 0.985 + 0.004, z * 0.994) for (y, z) in ARCADE_PROFILE]
    extrude(p, "Body", inner, 0.62, M.plastic)
    for sx in (-1, 1):
        extrude(p, "Side%s" % ("R" if sx > 0 else "L"), ARCADE_PROFILE, 0.022, M.plastic, loc=(sx * 0.32, 0, 0), rim_mat=M.gold_paint)
    # screen: sits on the face that runs from (-0.24, 1.04) up to (-0.17, 1.52)
    lean = math.atan2(0.07, 0.48)
    ny, nz = -math.cos(lean), math.sin(lean)
    cy, cz = -0.205 * 0.985 + 0.004, 1.28 * 0.994
    quad(p, "Bezel", 0.59, 0.47, M.gloss, (0, cy + ny * 0.002, cz + nz * 0.002), rot=(-lean, 0, 0))
    quad(p, "Screen", 0.52, 0.42, M.arcade, (0, cy + ny * 0.004, cz + nz * 0.004), rot=(-lean, 0, 0))
    quad(p, "Marquee", 0.60, 0.18, M.marquee, (0, -0.34 * 0.985 + 0.004 - 0.002, 1.71 * 0.994))
    # control deck: from (-0.46, 0.95) to (-0.24, 1.04)
    sl = math.atan2(0.09, 0.22)
    dn = (0.0, -math.sin(sl), math.cos(sl))            # deck normal
    ds = (0.0, math.cos(sl), math.sin(sl))             # up the slope
    dc = (0.0, -0.35 * 0.985 + 0.004, 0.995 * 0.994)

    def on_deck(x, s, lift=0.0):
        return (x, dc[1] + ds[1] * s + dn[1] * lift, dc[2] + ds[2] * s + dn[2] * lift)
    cyl(p, "StickBase", on_deck(-0.17, 0.0, 0.0), on_deck(-0.17, 0.0, 0.006), 0.026, M.gloss)
    cyl(p, "Stick", on_deck(-0.17, 0.0, 0.0), on_deck(-0.17, 0.0, 0.065), 0.005, M.alu)
    sphere(p, "StickBall", on_deck(-0.17, 0.0, 0.075), 0.019, M.gold_paint)
    for i in range(6):
        x = -0.02 + (i % 3) * 0.052 + (0.012 if i >= 3 else 0)
        s = 0.028 if i >= 3 else -0.028
        cyl(p, "Btn%d" % i, on_deck(x, s, 0.0), on_deck(x, s, 0.008), 0.015, M.gold_paint if i % 2 == 0 else M.green_paint)
    fy = -0.36 * 0.985 + 0.004
    box(p, "CoinDoor", (-0.13, fy - 0.008, 0.30), (0.13, fy + 0.002, 0.58), M.alu, bevel=0.004)
    for sx in (-1, 1):
        box(p, "CoinSlot", (sx * 0.06 - 0.018, fy - 0.011, 0.44), (sx * 0.06 + 0.018, fy - 0.007, 0.50), M.led, bevel=0)
    # side stripes on the face that looks into the room
    xs = 0.3315
    for nm, m, pts in (("StripeGreen", M.green_paint, [(-0.36, 0.22), (0.40, 0.82), (0.40, 1.04), (-0.36, 0.44)]),
                       ("StripeGold", M.gold_paint, [(-0.36, 0.49), (0.40, 1.09), (0.40, 1.16), (-0.36, 0.56)])):
        me = mesh_from(nm, [(xs, y, z) for (y, z) in pts], [(0, 1, 2, 3)])
        me.materials.append(m)
        add_obj(p, nm, me)
    return p


def neon_play(M):
    p = piece("NeonPlay", (0.45, 5.2, 2.34))
    cu = tube(p, "Tube", [(-0.14, -0.035, -0.17), (-0.14, -0.035, 0.17), (0.16, -0.035, 0.0)], 0.011, M.led, bezier=False)
    cu.data.splines[0].use_cyclic_u = True
    for (x, z) in ((-0.14, -0.1), (-0.14, 0.1), (0.1, 0.0)):
        cyl(p, "Standoff", (x, -0.035, z), (x, 0.0, z), 0.004, M.powder)
    return p


def bookshelf(M):
    p = piece("Bookshelf", (0.17, 3.5, 0))
    levels = [0.10, 0.52, 0.94, 1.36, 1.78]
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(p, "Post", (sx * 0.14 - 0.011, sy * 0.39 - 0.011, 0), (sx * 0.14 + 0.011, sy * 0.39 + 0.011, 1.86), M.powder, bevel=0.002)
    for k, z in enumerate(levels):
        box(p, "Shelf%d" % k, (-0.15, -0.40, z), (0.15, 0.40, z + 0.025), M.walnut, bevel=0.004)
    f = 0.125                                            # shelf front line (books' spines)
    for i, y0 in enumerate((-0.37, 0.02)):               # bottom: two linen storage boxes
        box(p, "Bin%d" % i, (-0.13, y0, 0.125), (0.13, y0 + 0.35, 0.40), M.linen, bevel=0.012, seg=3)
        box(p, "BinPull%d" % i, (0.13, y0 + 0.13, 0.30), (0.136, y0 + 0.22, 0.325), M.brass, bevel=0.002)
    books_row(p, "RowA", (f, -0.37, 0.545), 0.74, M.books, depth=0.2, seed=21, along="y", hmin=0.2, hmax=0.3)
    books_row(p, "RowB", (f, -0.37, 0.965), 0.36, M.books, depth=0.2, seed=22, along="y", hmin=0.2, hmax=0.28)
    box(p, "RetroConsole", (-0.11, 0.07, 0.965), (0.11, 0.34, 1.02), M.ceramic_cream, bevel=0.008, seg=3)
    box(p, "RetroSlot", (-0.05, 0.12, 1.02), (0.05, 0.29, 1.024), M.plastic, bevel=0)
    cyl(p, "RetroBtn", (0.07, 0.10, 1.02), (0.07, 0.10, 1.026), 0.012, M.green_paint)
    books_row(p, "RowC", (f, 0.0, 1.385), 0.37, M.books, depth=0.2, seed=23, along="y", hmin=0.19, hmax=0.27)
    z = books_stack(p, "StackC", (0.0, -0.22, 1.385), [M.books[2], M.books[1], M.books[5]], n=3, seed=5, w=0.2, d=0.27)
    sphere(p, "Orb", (0.0, -0.22, z + 0.05), 0.05, M.brass)
    pot(p, "Pot", (0.02, -0.2, 1.805), 0.06, 0.075, 0.12, M.ceramic_charcoal, M.soil)
    pothos(p, "Pothos", (0.02, -0.2, 1.915), M, seed=9, vines=((0, 0.5), (-50, 0.34), (40, 0.26)), n_top=18, scale=1.2)
    books_stack(p, "StackTop", (0.0, 0.2, 1.805), [M.books[3], M.books[0]], n=2, seed=7, w=0.2, d=0.26)
    return p


def wall_art(M):
    p = piece("WallArt", (0.0, 3.5, 2.33), rz=PI / 2)
    box(p, "Frame", (-0.21, -0.022, -0.26), (0.21, 0.0, 0.26), M.brass_brushed, bevel=0.003)
    box(p, "Mat", (-0.19, -0.024, -0.24), (0.19, -0.02, 0.24), M.paper, bevel=0)
    quad(p, "Art", 0.31, 0.39, M.art[1], (0, -0.0245, 0))
    return p


# ----------------------------------------------------------------------------- create
def tripod(M):
    p = piece("Tripod", (5.3, 1.9, 0), rz=R(-53.13))
    hub = 0.72
    for k in range(3):
        a = R(90 + k * 120)
        fx, fy = 0.42 * math.cos(a), 0.42 * math.sin(a)
        cyl(p, "Leg%d" % k, (fx, fy, 0.012), (0, 0, hub), 0.0085, M.powder, r2=0.011, seg=16)
        sphere(p, "Foot%d" % k, (fx, fy, 0.012), 0.015, M.plastic, seg=16, rings=8)
        cyl(p, "Brace%d" % k, (fx * 0.42, fy * 0.42, hub * 0.59), (0, 0, 0.36), 0.0045, M.powder, seg=12)
    cyl(p, "Hub", (0, 0, hub - 0.03), (0, 0, hub + 0.03), 0.022, M.plastic)
    cyl(p, "Collar", (0, 0, 0.34), (0, 0, 0.38), 0.016, M.plastic)
    cyl(p, "Column", (0, 0, 0.30), (0, 0, 1.30), 0.012, M.powder)
    cyl(p, "ColumnTop", (0, 0, 1.30), (0, 0, 1.345), 0.016, M.brass)
    cz = 1.565
    torus(p, "RingHousing", 0.215, 0.024, M.powder, loc=(0, 0.006, cz), flat=0.75)
    torus(p, "RingLight", 0.215, 0.017, M.ring, loc=(0, -0.012, cz), flat=0.45)
    cyl(p, "Gooseneck", (0, 0.004, 1.345), (0, 0.004, 1.478), 0.006, M.powder)
    box(p, "ClampBottom", (-0.045, -0.016, 1.472), (0.045, 0.014, 1.487), M.plastic, bevel=0.003)
    box(p, "ClampBack", (-0.02, 0.0, 1.487), (0.02, 0.012, 1.66), M.plastic, bevel=0.003)
    box(p, "ClampTop", (-0.03, -0.016, 1.652), (0.03, 0.014, 1.664), M.plastic, bevel=0.003)
    box(p, "Phone", (-0.0385, -0.012, 1.487), (0.0385, -0.003, 1.652), M.gloss, bevel=0.0035, seg=3)
    quad(p, "PhoneScreen", 0.071, 0.156, M.phone, (0, -0.0126, 1.5695))
    return p


# ----------------------------------------------------------------------------- big plants
def rubber_plant(M):
    p = piece("RubberPlant", (3.13, 4.80, 0))
    lathe(p, "Planter", [(0.001, 0), (0.15, 0), (0.156, 0.008), (0.19, 0.38)], M.brass_brushed, solid=0.012)
    cyl(p, "Soil", (0, 0, 0.33), (0, 0, 0.34), 0.178, M.soil)
    trunk = [(0, 0, 0.33), (0.015, 0.0, 0.7), (-0.01, 0.015, 1.1), (0.02, 0.0, 1.45), (0.03, -0.01, 1.66)]
    tube(p, "Trunk", trunk, 0.013, M.trunk)
    rnd = random.Random(12)
    specs = []
    n = 19
    for i in range(n):
        t = i / (n - 1)
        z = 0.62 + t * 1.06
        k = min(len(trunk) - 2, int((z - 0.33) / (1.66 - 0.33) * (len(trunk) - 1)))
        a, b = trunk[k], trunk[k + 1]
        f = (z - a[2]) / (b[2] - a[2])
        bx, by = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
        ang = i * 2.39996 + rnd.uniform(-0.25, 0.25)
        if math.sin(ang) > 0.45:                       # keep leaves out of the wall behind
            ang = -ang
        specs.append(dict(base=(bx, by, z), yaw=ang - PI / 2, tilt=R(18 + 52 * t + rnd.uniform(-8, 8)),
                          length=rnd.uniform(0.25, 0.33) * (1.0 - 0.25 * t), width=rnd.uniform(0.13, 0.165) * (1.0 - 0.2 * t),
                          bend=rnd.uniform(0.35, 0.95), fold=0.1, shape="oval", roll=rnd.uniform(-0.25, 0.25), segs=9))
    leaves(p, "Leaves", specs, M.leaf_rubber)
    return p


def snake_plant(M):
    p = piece("SnakePlant", (0.30, 0.235, 0))
    lathe(p, "Pot", [(0.001, 0), (0.12, 0), (0.126, 0.008), (0.15, 0.31)], M.ceramic_cream, solid=0.012)
    cyl(p, "Soil", (0, 0, 0.27), (0, 0, 0.28), 0.14, M.soil)
    rnd = random.Random(4)
    specs = []
    for i in range(13):
        a = i * 2.39996
        rr = 0.02 + 0.055 * rnd.random()
        specs.append(dict(base=(rr * math.cos(a), rr * math.sin(a), 0.27), yaw=a - PI / 2 + rnd.uniform(-0.4, 0.4),
                          tilt=R(rnd.uniform(74, 88)), length=rnd.uniform(0.5, 0.92), width=rnd.uniform(0.06, 0.085),
                          bend=rnd.uniform(-0.05, 0.3), fold=0.22, shape="blade", roll=rnd.uniform(-0.6, 0.6), segs=10))
    leaves(p, "Leaves", specs, M.leaf_snake)
    return p


def build(M):
    for f in (rug, sofa, coffee_table, media_console, tv, arc_lamp, sofa_console, pouf, bed, bench, nightstand, poster, desk, shelves, chair,
              arcade, neon_play, bookshelf, wall_art, tripod, rubber_plant, snake_plant):
        f(M)
