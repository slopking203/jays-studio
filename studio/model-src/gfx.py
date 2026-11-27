"""Flat graphics used on screens, the poster, the book cover and the arcade (all original, brand palette)."""
import math, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tex")
os.makedirs(OUT, exist_ok=True)

G = (80, 139, 63)       # #508B3F
C = (46, 46, 46)        # #2E2E2E
Y = (255, 200, 87)      # #FFC857
CREAM = (240, 232, 214)
INK = (22, 23, 22)
G_DK = (44, 84, 38)
G_LT = (122, 176, 100)

FONT = "/usr/share/fonts/opentype/inter/Inter-%s.otf"


def font(weight, size):
    return ImageFont.truetype(FONT % weight, size)


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vgrad(w, h, top, bottom):
    im = Image.new("RGB", (w, h))
    px = im.load()
    for y in range(h):
        c = mix(top, bottom, y / max(1, h - 1))
        for x in range(w):
            px[x, y] = c
    return im


def play(d, cx, cy, r, fill):
    d.polygon([(cx - r * 0.42, cy - r * 0.58), (cx - r * 0.42, cy + r * 0.58), (cx + r * 0.62, cy)], fill=fill)


def tv():
    W, H = 1280, 720
    im = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(im)
    # top bar
    d.rounded_rectangle((40, 28, 150, 68), 20, fill=G)
    d.text((95, 48), "CH 1", font=font("Bold", 24), fill=CREAM, anchor="mm")
    d.rounded_rectangle((1010, 34, 1240, 62), 14, fill=(40, 42, 40))
    d.ellipse((1022, 40, 1038, 56), fill=Y)
    # featured video
    feat = vgrad(760, 428, G, G_DK)
    fd = ImageDraw.Draw(feat)
    for i in range(9):  # soft diagonal light bands
        fd.polygon([(i * 130 - 200, 428), (i * 130 - 120, 428), (i * 130 + 220, 0), (i * 130 + 140, 0)], fill=mix(G, G_LT, 0.25))
    feat = feat.filter(ImageFilter.GaussianBlur(18))
    mask = Image.new("L", (760, 428), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 759, 427), 22, fill=255)
    im.paste(feat, (40, 96), mask)
    d.ellipse((40 + 380 - 62, 96 + 214 - 62, 40 + 380 + 62, 96 + 214 + 62), fill=C)
    play(d, 40 + 380, 96 + 214, 50, Y)
    d.rounded_rectangle((40, 552, 560, 580), 8, fill=CREAM)
    d.rounded_rectangle((40, 596, 330, 616), 8, fill=(120, 122, 116))
    d.rounded_rectangle((40, 660, 800, 668), 4, fill=(60, 62, 60))
    d.rounded_rectangle((40, 660, 330, 668), 4, fill=Y)
    # up-next column
    tones = [(Y, mix(Y, C, 0.45)), (mix(G, C, 0.3), C), (mix(CREAM, C, 0.4), mix(CREAM, C, 0.75)), (G_LT, G_DK)]
    for i, (a, b) in enumerate(tones):
        y0 = 96 + i * 150
        th = vgrad(200, 112, a, b)
        m = Image.new("L", (200, 112), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, 199, 111), 12, fill=255)
        im.paste(th, (840, y0), m)
        d.rounded_rectangle((1060, y0 + 12, 1240, y0 + 30), 6, fill=CREAM)
        d.rounded_rectangle((1060, y0 + 44, 1190, y0 + 58), 6, fill=(110, 112, 106))
        d.rounded_rectangle((1060, y0 + 72, 1140, y0 + 86), 6, fill=(70, 72, 68))
    im.save(os.path.join(OUT, "tv.png"))


def laptop():
    W, H = 1280, 800
    im = Image.new("RGB", (W, H), (26, 28, 26))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 44), fill=(36, 38, 36))
    for i, c in enumerate([(210, 96, 84), Y, G]):
        d.ellipse((18 + i * 26, 14, 34 + i * 26, 30), fill=c)
    d.rounded_rectangle((300, 8, 520, 44), 8, fill=(26, 28, 26))
    d.rounded_rectangle((322, 22, 440, 32), 5, fill=CREAM)
    d.rectangle((0, 44, 250, H), fill=(32, 34, 32))
    rnd = random.Random(7)
    for i in range(15):
        ind = rnd.choice([0, 0, 22, 22, 44])
        d.rounded_rectangle((24 + ind, 74 + i * 34, 24 + ind + rnd.randint(70, 170), 86 + i * 34), 6,
                            fill=(96, 100, 94) if i != 4 else Y)
    y = 78
    pal = [G_LT, Y, CREAM, (132, 136, 128), G, (196, 170, 120)]
    for ln in range(20):
        d.text((274, y - 1), str(ln + 1).rjust(2), font=font("Medium", 15), fill=(84, 88, 82))
        if ln in (5, 11, 16):
            y += 34
            continue
        x = 320 + rnd.choice([0, 0, 36, 36, 72, 108])
        for _ in range(rnd.randint(2, 5)):
            w = rnd.randint(40, 190)
            if x + w > 1200:
                break
            d.rounded_rectangle((x, y, x + w, y + 14), 7, fill=rnd.choice(pal))
            x += w + 14
        y += 34
    d.rectangle((250, H - 30, W, H), fill=G)
    d.rounded_rectangle((270, H - 21, 400, H - 10), 5, fill=CREAM)
    im.save(os.path.join(OUT, "laptop.png"))


def arcade():
    w, h = 120, 160
    im = Image.new("RGB", (w, h), (8, 10, 9))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 11), fill=(20, 24, 20))
    for i, on in enumerate([1, 1, 1, 0, 1, 1]):          # score blocks
        d.rectangle((6 + i * 7, 3, 10 + i * 7, 8), fill=Y if on else (60, 60, 50))
    for i in range(3):                                   # lives
        d.rectangle((98 + i * 7, 3, 102 + i * 7, 8), fill=G_LT)
    rows = [Y, Y, G_LT, G, G, CREAM]
    rnd = random.Random(3)
    for r, col in enumerate(rows):
        for c in range(10):
            if rnd.random() < 0.14 and r > 2:
                continue
            d.rectangle((5 + c * 11, 20 + r * 8, 14 + c * 11, 25 + r * 8), fill=col)
    d.rectangle((46, 142, 74, 146), fill=CREAM)
    d.rectangle((66, 104, 69, 107), fill=Y)
    for i, (x, y) in enumerate([(62, 112), (58, 120), (54, 128)]):
        d.rectangle((x, y, x + 2, y + 2), fill=mix(Y, (8, 10, 9), 0.45 + i * 0.18))
    big = im.resize((w * 5, h * 5), Image.NEAREST)
    bd = ImageDraw.Draw(big)
    for y in range(0, h * 5, 5):                         # scanlines
        bd.line((0, y, w * 5, y), fill=(0, 0, 0), width=1)
    big.save(os.path.join(OUT, "arcade.png"))


def marquee():
    W, H = 720, 168
    im = vgrad(W, H, mix(Y, (255, 255, 255), 0.25), mix(Y, (200, 130, 30), 0.35))
    d = ImageDraw.Draw(im)
    for i in range(4):
        x = 20 + i * 26
        d.polygon([(x, 28), (x + 14, 28), (x + 44, 84), (x + 14, 140), (x, 140), (x + 30, 84)], fill=G if i % 2 == 0 else C)
        x2 = W - 20 - i * 26
        d.polygon([(x2, 28), (x2 - 14, 28), (x2 - 44, 84), (x2 - 14, 140), (x2, 140), (x2 - 30, 84)], fill=G if i % 2 == 0 else C)
    f = font("Black", 92)
    text = "ARCADE"
    tw = sum(d.textlength(ch, font=f) for ch in text) + 10 * (len(text) - 1)
    x = (W - tw) / 2
    for ch in text:
        d.text((x + 3, 87), ch, font=f, fill=mix(Y, (150, 100, 20), 0.6), anchor="lm")
        d.text((x, 84), ch, font=f, fill=C, anchor="lm")
        x += d.textlength(ch, font=f) + 10
    im.save(os.path.join(OUT, "marquee.png"))


def phone():
    W, H = 360, 780
    im = vgrad(W, H, G_LT, mix(G_DK, C, 0.55))
    d = ImageDraw.Draw(im)
    for i in range(6):
        d.ellipse((-80 + i * 70, 420 + i * 22, 300 + i * 70, 900 + i * 22), fill=mix(G, C, 0.25 + i * 0.1))
    im = im.filter(ImageFilter.GaussianBlur(10))
    d = ImageDraw.Draw(im)
    d.ellipse((W / 2 - 70, 300, W / 2 + 70, 440), fill=Y)
    play(d, W / 2, 370, 56, C)
    d.rounded_rectangle((24, 24, W - 24, 32), 4, fill=(255, 255, 255))
    d.rounded_rectangle((24, 24, 150, 32), 4, fill=Y)
    d.rounded_rectangle((24, 664, 220, 688), 10, fill=CREAM)
    d.rounded_rectangle((24, 704, 160, 720), 8, fill=(200, 204, 190))
    for i in range(3):
        d.ellipse((W - 70, 500 + i * 62, W - 26, 544 + i * 62), fill=CREAM if i else Y)
    im.save(os.path.join(OUT, "phone.png"))


def poster():
    W, H = 1050, 1500
    im = Image.new("RGB", (W, H), C)
    d = ImageDraw.Draw(im)
    for i in range(9):                                   # fine horizon lines behind the sun
        y = 330 + i * 46
        d.line((120, y, W - 120, y), fill=mix(C, CREAM, 0.16), width=3)
    cx, cy, r = W // 2, 520, 250
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=Y)
    for i in range(5):                                   # cut-outs across the lower sun
        y = cy + 40 + i * 44
        d.rectangle((cx - r, y, cx + r, y + 10 + i * 5), fill=C)

    def hill(base, amp, phase, col, freq):
        pts = [(0, H)]
        for x in range(0, W + 1, 6):
            pts.append((x, base + amp * math.sin(x / W * math.pi * freq + phase)))
        pts.append((W, H))
        d.polygon(pts, fill=col)
    hill(840, 70, 0.4, G_LT, 2.0)
    hill(930, 80, 2.3, G, 1.6)
    hill(1040, 60, 4.2, G_DK, 2.4)
    d.rectangle((0, 1230, W, H), fill=CREAM)
    d.text((W / 2, 1318), "JAY'S STUDIO", font=font("Black", 96), fill=C, anchor="mm")
    d.rectangle((W / 2 - 60, 1392, W / 2 + 60, 1400), fill=G)
    d.text((W / 2, 1436), "MADE HERE", font=font("SemiBold", 30), fill=mix(C, CREAM, 0.35), anchor="mm")
    im.save(os.path.join(OUT, "poster.png"))


def cover():
    W, H = 600, 900
    im = vgrad(W, H, mix(G, G_LT, 0.15), mix(G, G_DK, 0.35))
    d = ImageDraw.Draw(im)
    d.rectangle((28, 28, W - 28, H - 28), outline=Y, width=6)
    cx, cy = W / 2, 300
    pts = []
    for i in range(16):                                  # eight-point spark
        a = i * math.pi / 8 - math.pi / 2
        rr = 150 if i % 2 == 0 else 46
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=Y)
    d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=G_DK)
    for i, wd in enumerate([400, 320, 220]):
        d.rounded_rectangle((W / 2 - wd / 2, 540 + i * 62, W / 2 + wd / 2, 574 + i * 62), 10, fill=CREAM)
    d.rectangle((28, 780, W - 28, H - 28), fill=C)
    d.rounded_rectangle((W / 2 - 110, 812, W / 2 + 110, 836), 8, fill=Y)
    im.save(os.path.join(OUT, "cover.png"))


def keys():
    W, H = 660, 440
    im = Image.new("RGB", (W, H), (58, 60, 58))
    d = ImageDraw.Draw(im)
    for r in range(5):
        for c in range(14):
            x = 24 + c * 44
            y = 20 + r * 40
            d.rounded_rectangle((x, y, x + 38, y + 34), 5, fill=(24, 25, 24))
    d.rounded_rectangle((24 + 4 * 44, 20 + 5 * 40, 24 + 9 * 44 + 38, 20 + 5 * 40 + 30), 5, fill=(24, 25, 24))
    d.rounded_rectangle((W / 2 - 130, 262, W / 2 + 130, 424), 10, fill=(50, 52, 50), outline=(70, 72, 70), width=2)
    im.save(os.path.join(OUT, "keys.png"))


def remote():
    W, H = 120, 420
    im = Image.new("RGB", (W, H), (30, 31, 30))
    d = ImageDraw.Draw(im)
    d.ellipse((44, 24, 76, 56), fill=Y)
    d.ellipse((22, 96, 98, 172), fill=(60, 62, 60))
    d.ellipse((44, 118, 76, 150), fill=(30, 31, 30))
    for r in range(4):
        for c in range(3):
            d.rounded_rectangle((18 + c * 30, 206 + r * 44, 40 + c * 30, 232 + r * 44), 6,
                                fill=G if (r, c) == (0, 2) else (78, 80, 78))
    im.save(os.path.join(OUT, "remote.png"))


def small_art():
    for k, (bg, a, b) in enumerate([(CREAM, G, Y), (C, Y, G_LT), (G_DK, CREAM, Y)]):
        im = Image.new("RGB", (400, 500), bg)
        d = ImageDraw.Draw(im)
        if k == 0:
            d.pieslice((60, 120, 340, 400), 180, 360, fill=a)
            d.ellipse((150, 70, 250, 170), fill=b)
            d.rectangle((60, 300, 340, 316), fill=C)
        elif k == 1:
            for i in range(5):
                d.arc((40 + i * 28, 90 + i * 28, 360 - i * 28, 410 - i * 28), 200, 340, fill=a if i % 2 == 0 else b, width=14)
        else:
            d.polygon([(200, 80), (330, 400), (70, 400)], fill=a)
            d.ellipse((230, 110, 320, 200), fill=b)
        im.save(os.path.join(OUT, "art%d.png" % k))


if __name__ == "__main__":
    for f in (tv, laptop, arcade, marquee, phone, poster, cover, keys, remote, small_art):
        f()
    print(sorted(os.listdir(OUT)))
