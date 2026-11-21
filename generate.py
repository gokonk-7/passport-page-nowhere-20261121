#!/usr/bin/env python3
"""Render the passport spread for make.fun bounty
the-passport-page-of-a-countr-2-20261121-0318.

The Republic of Veskar: a North Atlantic island nation (fishing and
geothermal), capital Vesthavn. Holder Elin Margaret Haldorsen, a certified
deep-sea fisher. Issued 02 JUN 2025, expires 02 JUN 2035. Schengen visa
01 JUL 2026 - 01 JAN 2027; stamps Jul-Oct 2026 form one coherent trip:
Vesthavn -> Bergen -> Keflavik -> Aberdeen -> Vesthavn.

Rendered at 2x with Pillow, downscaled to 1024x1024, saved as
assets/entry.png (PNG, under 1 MiB). Deterministic: fixed seed, no clock,
no network.
"""

import math
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "assets" / "entry.png"

S = 2  # supersample factor; layout numbers are in 1x units (1024 grid)
W, H = 1024, 1024

F_SERIF = "/usr/share/fonts/opentype/urw-base35/P052-Bold.otf"
F_SERIF_R = "/usr/share/fonts/opentype/urw-base35/P052-Roman.otf"
F_SERIF_I = "/usr/share/fonts/opentype/urw-base35/P052-Italic.otf"
F_SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
F_SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
F_SANS_I = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"
F_MONO = "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"
F_MONO_B = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"
F_SCRIPT = "/usr/share/fonts/opentype/urw-base35/Z003-MediumItalic.otf"

_rng = random.Random(20261121)


def font(path, size):
    return ImageFont.truetype(path, int(round(size * S)))


def text_size(draw, s, fnt):
    b = draw.textbbox((0, 0), s, font=fnt)
    return (b[2] - b[0]) / S, (b[3] - b[1]) / S


def draw_text(d, xy, s, fnt, fill, anchor="la", spacing=0):
    """Draw text at 1x coords; spacing = extra letter-spacing in 1x px."""
    x, y = xy
    if spacing == 0:
        d.text((x * S, y * S), s, font=fnt, fill=fill, anchor=anchor)
        return
    # letter-spaced: draw char by char, anchor handled by measuring first
    widths = []
    total = 0.0
    for ch in s:
        w, _ = text_size(d, ch, fnt)
        widths.append(w)
        total += w + spacing
    total -= spacing
    if anchor[0] == "l":  # left
        cx = x
    elif anchor[0] == "m":  # middle
        cx = x - total / 2
    else:  # right
        cx = x - total
    for ch, w in zip(s, widths):
        d.text((cx * S, y * S), ch, font=fnt, fill=fill, anchor="la")
        cx += w + spacing


def centered_text(d, cx, y, s, fnt, fill, spacing=0):
    draw_text(d, (cx, y), s, fnt, fill, anchor="ma", spacing=spacing)


# ---------------------------------------------------------------- palette
INK = (32, 42, 50, 255)          # near-black blue ink
TEAL = (31, 77, 90, 255)         # Veskar teal
GOLD = (176, 141, 63, 255)       # foil gold
GOLD_D = (146, 112, 44, 255)
PAGE = (244, 239, 228, 255)      # cream paper
PAGE_BLUE = (238, 241, 235, 255)
DESK = (35, 41, 48, 255)
RULE = (120, 110, 88, 255)


def guilloche(img, box, color, amp=5, step=7, alpha=26):
    """Fine wavy security lines across a page."""
    x0, y0, x1, y1 = box
    layer = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for yy in range(int(y0), int(y1), step):
        pts = []
        for xx in range(int(x0), int(x1) + 1, 6):
            pts.append(((xx + amp * math.sin((xx + yy) * 0.03)) * S,
                        (yy + amp * 0.45 * math.sin(xx * 0.05 + yy)) * S))
        ld.line(pts, fill=color + (alpha,), width=max(1, S // 2))
    img.paste(Image.alpha_composite(img, layer), (0, 0))


def noise_overlay(img, amount=7, seed=7):
    r = random.Random(seed)
    px = img.load()
    for _ in range(int(W * H * 0.012)):
        x = r.randrange(W)
        y = r.randrange(H)
        v = r.randint(-amount, amount)
        p = px[x, y]
        px[x, y] = tuple(max(0, min(255, c + v)) for c in p[:3]) + ((p[3],) if len(p) > 3 else ())


# ---------------------------------------------------------------- emblem
def draw_emblem(d, cx, cy, r, color, beak_color=None, face_color=None):
    if beak_color is None:
        beak_color = (198, 84, 48, 255)
    if face_color is None:
        face_color = (244, 239, 228, 255)
    """Gold seal: double ring, puffin over waves, star above."""
    x, y = cx * S, cy * S
    rr = r * S
    d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=color, width=max(2, int(2.4 * S)))
    d.ellipse([x - rr * 0.82, y - rr * 0.82, x + rr * 0.82, y + rr * 0.82],
              outline=color, width=max(1, int(1.1 * S)))
    # star
    sx, sy = x, y - rr * 0.52
    sr = rr * 0.13
    star = []
    for i in range(8):
        ang = -math.pi / 2 + i * math.pi / 4
        rad = sr if i % 2 == 0 else sr * 0.42
        star.append((sx + rad * math.cos(ang), sy + rad * math.sin(ang)))
    d.polygon(star, fill=color)
    # puffin body (facing left): black teardrop
    bx, by = x, y + rr * 0.05
    body = [(bx - rr * 0.42, by + rr * 0.28), (bx - rr * 0.46, by - rr * 0.10),
            (bx - rr * 0.28, by - rr * 0.38), (bx - rr * 0.02, by - rr * 0.42),
            (bx + rr * 0.22, by - rr * 0.28), (bx + rr * 0.34, by - rr * 0.02),
            (bx + rr * 0.30, by + rr * 0.28), (bx, by + rr * 0.38)]
    d.polygon(body, fill=color)
    # white face patch
    d.ellipse([bx - rr * 0.34, by - rr * 0.34, bx - rr * 0.02, by - rr * 0.06],
              fill=face_color)
    # beak (orange-red triangle)
    d.polygon([(bx - rr * 0.44, by - rr * 0.22), (bx - rr * 0.62, by - rr * 0.12),
               (bx - rr * 0.44, by - rr * 0.02)], fill=beak_color)
    # waves
    for i, wy in enumerate((0.44, 0.56, 0.68)):
        yy = y + rr * wy
        d.arc([x - rr * 0.55, yy - rr * 0.14, x - rr * 0.05, yy + rr * 0.14],
              180, 360, fill=color, width=max(1, int(1.2 * S)))
        d.arc([x + rr * 0.05, yy - rr * 0.14, x + rr * 0.55, yy + rr * 0.14],
              180, 360, fill=color, width=max(1, int(1.2 * S)))


# ---------------------------------------------------------------- portrait
def draw_portrait(w, h):
    """Flat-illustration passport photo: woman, late 30s, hair pulled back,
    navy jacket, pale blue-grey backdrop, slight grain."""
    img = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = w * S / 2
    # backdrop: vertical gradient
    top = (178, 190, 198)
    bot = (148, 163, 175)
    for yy in range(h * S):
        t = yy / (h * S)
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        d.line([(0, yy), (w * S, yy)], fill=c + (255,))
    # faint backdrop horizontal band (studio sweep)
    d.rectangle([0, int(h * S * 0.62), w * S, h * S], fill=(140, 155, 168, 60))
    skin = (224, 180, 143, 255)
    skin_sh = (206, 158, 120, 255)
    hair_c = (74, 50, 38, 255)
    hair_d = (58, 38, 28, 255)
    jacket = (38, 54, 72, 255)
    # shoulders / jacket
    sh_y = h * S * 0.74
    d.polygon([(0, h * S), (0, sh_y + 30 * S * 0.4), (cx - 52 * S, sh_y),
               (cx + 52 * S, sh_y), (w * S, sh_y + 30 * S * 0.4), (w * S, h * S)],
              fill=jacket)
    # shirt: light trapezoid under the collar (no tie shape)
    d.polygon([(cx - 30 * S, sh_y + 2), (cx + 30 * S, sh_y + 2),
               (cx + 22 * S, sh_y + 34 * S), (cx - 22 * S, sh_y + 34 * S)],
              fill=(226, 229, 233, 255))
    # jacket lapels: two separate flaps, not meeting at a point
    d.polygon([(cx - 30 * S, sh_y + 2), (cx - 52 * S, sh_y + 6 * S),
               (cx - 26 * S, sh_y + 44 * S), (cx - 12 * S, sh_y + 30 * S)],
              fill=(30, 44, 60, 255))
    d.polygon([(cx + 30 * S, sh_y + 2), (cx + 52 * S, sh_y + 6 * S),
               (cx + 26 * S, sh_y + 44 * S), (cx + 12 * S, sh_y + 30 * S)],
              fill=(30, 44, 60, 255))
    # neck
    d.rectangle([cx - 13 * S, h * S * 0.60, cx + 13 * S, sh_y + 4], fill=skin_sh)
    d.rectangle([cx - 13 * S, h * S * 0.60, cx + 13 * S, h * S * 0.64], fill=(190, 140, 105, 255))
    # hair back mass: frames the head, ends above the chin (no beard ring)
    d.ellipse([cx - 44 * S, h * S * 0.02, cx + 44 * S, h * S * 0.55], fill=hair_c)
    # face oval
    d.ellipse([cx - 34 * S, h * S * 0.14, cx + 34 * S, h * S * 0.64], fill=skin)
    # long side strands falling past the shoulders (pulled-back hair)
    d.polygon([(cx - 44 * S, h * S * 0.30), (cx - 34 * S, h * S * 0.30),
               (cx - 38 * S, h * S * 0.74), (cx - 48 * S, h * S * 0.74)], fill=hair_c)
    d.polygon([(cx + 44 * S, h * S * 0.30), (cx + 34 * S, h * S * 0.30),
               (cx + 38 * S, h * S * 0.74), (cx + 48 * S, h * S * 0.74)], fill=hair_c)
    # hair fringe: soft short arc across the forehead, centre part
    d.pieslice([cx - 36 * S, h * S * 0.08, cx + 36 * S, h * S * 0.28], 180, 360, fill=hair_c)
    d.polygon([(cx - 3 * S, h * S * 0.13), (cx + 3 * S, h * S * 0.13),
               (cx, h * S * 0.20)], fill=skin)
    # ears
    d.ellipse([cx - 38 * S, h * S * 0.34, cx - 30 * S, h * S * 0.44], fill=skin)
    d.ellipse([cx + 30 * S, h * S * 0.34, cx + 38 * S, h * S * 0.44], fill=skin)
    # eyebrows
    d.arc([cx - 23 * S, h * S * 0.315, cx - 7 * S, h * S * 0.355], 200, 340,
          fill=hair_d, width=max(1, int(1.2 * S)))
    d.arc([cx + 7 * S, h * S * 0.315, cx + 23 * S, h * S * 0.355], 200, 340,
          fill=hair_d, width=max(1, int(1.2 * S)))
    # eyes
    for sgn in (-1, 1):
        ex = cx + sgn * 15 * S
        ey = h * S * 0.375
        d.ellipse([ex - 7.5 * S, ey - 3.6 * S, ex + 7.5 * S, ey + 3.6 * S],
                  fill=(250, 248, 244, 255), outline=(90, 70, 55, 255), width=max(1, S // 2))
        d.ellipse([ex - 3.4 * S, ey - 3.2 * S, ex + 3.4 * S, ey + 3.2 * S],
                  fill=(52, 44, 38, 255))
        d.ellipse([ex - 1.2 * S, ey - 1.6 * S, ex + 1.2 * S, ey + 0.8 * S],
                  fill=(255, 255, 255, 255))
        d.arc([ex - 8 * S, ey - 4.6 * S, ex + 8 * S, ey + 2 * S], 180, 360,
              fill=(60, 45, 35, 255), width=max(1, int(1.3 * S)))
    # nose
    d.line([(cx, h * S * 0.40), (cx - 1.5 * S, h * S * 0.485)], fill=(196, 146, 110, 255),
           width=max(1, int(1.2 * S)))
    d.arc([cx - 5 * S, h * S * 0.475, cx + 5 * S, h * S * 0.505], 0, 180,
          fill=(196, 146, 110, 255), width=max(1, int(1.2 * S)))
    # lips: closed, calm
    d.arc([cx - 9 * S, h * S * 0.525, cx + 9 * S, h * S * 0.565], 15, 165,
          fill=(176, 96, 84, 255), width=max(2, int(1.8 * S)))
    d.arc([cx - 7 * S, h * S * 0.555, cx + 7 * S, h * S * 0.575], 0, 180,
          fill=(186, 128, 110, 255), width=max(1, int(1.1 * S)))
    # small gold stud earrings
    d.ellipse([cx - 36 * S, h * S * 0.435, cx - 33 * S, h * S * 0.455],
              fill=(176, 141, 63, 255))
    d.ellipse([cx + 33 * S, h * S * 0.435, cx + 36 * S, h * S * 0.455],
              fill=(176, 141, 63, 255))
    # grain
    px = img.load()
    r = random.Random(11)
    for _ in range(w * h * 6):
        x = r.randrange(w * S)
        y = r.randrange(h * S)
        v = r.randint(-9, 9)
        p = px[x, y]
        px[x, y] = tuple(max(0, min(255, c + v)) for c in p[:3]) + (p[3],)
    return img


# ---------------------------------------------------------------- MRZ
def mrz_check(s):
    weights = (7, 3, 1)
    total = 0
    for i, ch in enumerate(s):
        if ch.isdigit():
            v = int(ch)
        elif ch == "<":
            v = 0
        else:
            v = ord(ch) - 55  # A=10
        total += v * weights[i % 3]
    return str(total % 10)


def mrz_lines():
    line1 = "P<VSKHALDORSEN<<ELIN<MARGARET"
    line1 = line1 + "<" * (44 - len(line1))
    doc = "VSK004281"
    dob = "890314"
    exp = "350602"
    pers = "1403894821<<<<"
    l2 = (doc + mrz_check(doc) + "VSK" + dob + mrz_check(dob) + "F"
          + exp + mrz_check(exp) + pers + mrz_check(pers))
    l2 = l2 + mrz_check(l2)
    assert len(line1) == 44 and len(l2) == 44, (len(line1), len(l2))
    return line1, l2


# ---------------------------------------------------------------- stamps
def circular_text(base_img, cx, cy, r, text, fnt, fill, start_deg=-90, sweep=360,
                  flip=False):
    """Draw text along a circle on base_img (RGBA)."""
    d = ImageDraw.Draw(base_img)
    n = len(text)
    for i, ch in enumerate(text):
        ang = math.radians(start_deg + sweep * (i + 0.5) / n)
        x = cx + r * math.cos(ang)
        y = cy + r * math.sin(ang)
        ch_img = Image.new("RGBA", (40 * S, 40 * S), (0, 0, 0, 0))
        cd = ImageDraw.Draw(ch_img)
        cd.text((20 * S, 20 * S), ch, font=fnt, fill=fill, anchor="mm")
        rot = math.degrees(ang) + 90
        if flip:
            rot += 180
        ch_img = ch_img.rotate(-rot, resample=Image.BICUBIC, center=(20 * S, 20 * S))
        base_img.alpha_composite(ch_img, (int(x - 20 * S), int(y - 20 * S)))


def stamp_round(cx, cy, r, color, top_text, bottom_text, mid_text, date_text, angle):
    """Round border-control stamp; text on top and bottom arcs only."""
    size = int((r * 2 + 24) * S)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = size / 2
    rr = r * S
    d.ellipse([c - rr, c - rr, c + rr, c + rr], outline=color, width=max(2, int(2.2 * S)))
    d.ellipse([c - rr * 0.80, c - rr * 0.80, c + rr * 0.80, c + rr * 0.80],
              outline=color, width=max(1, int(1.2 * S)))
    f_top = font(F_SANS_B, 11)
    circular_text(img, c, c, rr * 0.88, top_text, f_top, color,
                  start_deg=-90 - 55, sweep=110)
    f_bot = font(F_SANS_B, 10)
    circular_text(img, c, c, rr * 0.88, bottom_text, f_bot, color,
                  start_deg=90 + 65, sweep=-130)
    f_mid = font(F_SANS_B, 15)
    d.text((c, c - 9 * S), mid_text, font=f_mid, fill=color, anchor="mm")
    f_dt = font(F_SANS_B, 12)
    d.text((c, c + 11 * S), date_text, font=f_dt, fill=color, anchor="mm")
    d.line([(c - rr * 0.42, c + 2 * S), (c + rr * 0.42, c + 2 * S)], fill=color,
           width=max(1, int(1.1 * S)))
    img = img.rotate(angle, resample=Image.BICUBIC, expand=False)
    return img, (int((cx - r - 12) * S), int((cy - r - 12) * S))


def stamp_rect(w, h, color, lines, angle):
    """Rectangular border stamp; lines = [(text, font, size)].
    Returns (image, cx_px, cy_px) of the rotated layer's centre offset:
    paste at (cx*S - img.width//2, cy*S - img.height//2)."""
    img = Image.new("RGBA", (int((w + 20) * S), int((h + 20) * S),), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x0, y0 = 10 * S, 10 * S
    x1, y1 = (w + 10) * S, (h + 10) * S
    d.rectangle([x0, y0, x1, y1], outline=color, width=max(2, int(2.2 * S)))
    d.rectangle([x0 + 3 * S, y0 + 3 * S, x1 - 3 * S, y1 - 3 * S], outline=color,
                width=max(1, int(1.1 * S)))
    total_h = sum(sz + 4 for _, _, sz in lines) - 4
    yy = (h - total_h) / 2
    for text, fpath, sz in lines:
        fnt = font(fpath, sz)
        d.text(((w + 20) * S / 2, (yy + 10) * S), text, font=fnt, fill=color,
               anchor="ma")
        yy += sz + 4
    return img.rotate(angle, resample=Image.BICUBIC, expand=True)


def paste_stamp(img, stamp, cx, cy):
    img.alpha_composite(stamp, (int(cx * S - stamp.width // 2),
                                int(cy * S - stamp.height // 2)))


def distress(img, seed, dots=260):
    """Fade a stamp layer slightly, like uneven ink."""
    r = random.Random(seed)
    px = img.load()
    w, h = img.size
    for _ in range(dots):
        x = r.randrange(w)
        y = r.randrange(h)
        if px[x, y][3] > 40:
            px[x, y] = px[x, y][:3] + (max(0, px[x, y][3] - r.randint(40, 130)),)
    return img

# ---------------------------------------------------------------- pages
def field(d, x, y, label, value, vsize=17, label_size=10.5, width=None):
    f_lab = font(F_SANS, label_size)
    f_val = font(F_SANS_B, vsize)
    d.text((x * S, y * S), label, font=f_lab, fill=(110, 105, 92, 255), anchor="la")
    d.text((x * S, (y + label_size + 3) * S), value, font=f_val, fill=INK, anchor="la")


def build_left(img, lx, ly, pw, ph):
    d = ImageDraw.Draw(img)
    # paper
    d.rectangle([lx * S, ly * S, (lx + pw) * S, (ly + ph) * S], fill=PAGE)
    # security tint: pale blue guilloche
    guilloche(img, (lx + 8, ly + 8, lx + pw - 8, ly + ph - 8), (90, 130, 160))
    # faint watermark emblem, centre
    wm = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wm)
    draw_emblem(wd, lx + pw / 2, ly + ph / 2 + 40, 120, (90, 130, 160, 16),
                beak_color=(90, 130, 160, 16), face_color=(90, 130, 160, 16))
    img.paste(Image.alpha_composite(img, wm), (0, 0))
    # inner frame
    d.rectangle([(lx + 10) * S, (ly + 10) * S, (lx + pw - 10) * S, (ly + ph - 10) * S],
                outline=(150, 138, 105, 255), width=max(1, int(1.2 * S)))
    cx = lx + pw / 2
    centered_text(d, cx, ly + 26, "LÝÐVELDIÐ VESKAR", font(F_SANS, 12.5), TEAL,
                  spacing=3)
    centered_text(d, cx, ly + 48, "REPUBLIC OF VESKAR", font(F_SERIF, 23), TEAL,
                  spacing=1.5)
    draw_emblem(d, cx, ly + 108, 27, GOLD_D)
    centered_text(d, cx, ly + 146, "PASSPORT", font(F_SANS_B, 21), INK, spacing=7)
    centered_text(d, cx, ly + 172, "FERÐABRÉF", font(F_SANS, 12), TEAL, spacing=4)
    d.line([(lx + 44) * S, (ly + 198) * S, (lx + pw - 44) * S, (ly + 198) * S],
           fill=GOLD, width=max(2, int(1.6 * S)))
    # type / code / number row
    y = ly + 212
    field(d, lx + 28, y, "TYPE / GERÐ", "P", vsize=16)
    field(d, lx + 118, y, "CODE / LAND", "VSK", vsize=16)
    field(d, lx + 218, y, "PASSPORT No. / NÚMER", "VSK 004281", vsize=16)
    # photo
    px, py, pw_, ph_ = lx + 28, ly + 258, 148, 188
    photo = draw_portrait(pw_, ph_)
    img.alpha_composite(photo, (int(px * S), int(py * S)))
    d.rectangle([px * S, py * S, (px + pw_) * S, (py + ph_) * S],
                outline=INK, width=max(2, int(1.6 * S)))
    # fields right of photo
    fx = lx + 196
    field(d, fx, ly + 258, "SURNAME / EFTIRNAFN", "HALDORSEN")
    field(d, fx, ly + 300, "GIVEN NAMES / FORNÖFN", "ELIN MARGARET")
    field(d, fx, ly + 342, "NATIONALITY / ÞJÓÐERNI", "VESKARI")
    field(d, fx, ly + 384, "SEX / KYN", "F")
    field(d, fx, ly + 428, "DATE OF BIRTH / FÆÐINGARDAGUR", "14 MAR 1989")
    # lower grid
    y = ly + 470
    field(d, lx + 28, y, "PLACE OF BIRTH / FÆÐINGARSTAÐUR", "VESTHAVN, VESKAR")
    field(d, lx + 258, y, "DATE OF ISSUE / ÚTGÁFUDAGUR", "02 JUN 2025")
    y = ly + 516
    field(d, lx + 28, y, "PERSONAL No. / KENNITALA", "140389-4821")
    field(d, lx + 258, y, "DATE OF EXPIRY / GILDISTÍMI", "02 JUN 2035")
    y = ly + 562
    field(d, lx + 28, y, "AUTHORITY / ÚTGEFANDI", "PASSPORT OFFICE, VESTHAVN",
          vsize=14)
    # signature
    f_sig = font(F_SCRIPT, 26)
    d.text(((lx + 286) * S, (ly + 588) * S), "Elin M. Haldorsen", font=f_sig,
           fill=(40, 50, 90, 255), anchor="la")
    d.line([(lx + 282) * S, (ly + 620) * S, (lx + pw - 28) * S, (ly + 620) * S],
           fill=(120, 110, 88, 255), width=max(1, int(1.1 * S)))
    d.text(((lx + 282) * S, (ly + 624) * S), "HOLDER'S SIGNATURE",
           font=font(F_SANS, 9), fill=(110, 105, 92, 255), anchor="la")
    # MRZ
    l1, l2 = mrz_lines()
    f_mrz = font(F_MONO, 14.5)
    d.text(((lx + 28) * S, (ly + ph - 52) * S), l1, font=f_mrz, fill=INK, anchor="la")
    d.text(((lx + 28) * S, (ly + ph - 32) * S), l2, font=f_mrz, fill=INK, anchor="la")


def build_right(img, rx, ly, pw, ph):
    d = ImageDraw.Draw(img)
    d.rectangle([rx * S, ly * S, (rx + pw) * S, (ly + ph) * S], fill=PAGE_BLUE)
    guilloche(img, (rx + 8, ly + 8, rx + pw - 8, ly + ph - 8), (110, 140, 110))
    wm = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wm)
    draw_emblem(wd, rx + pw / 2, ly + ph / 2 + 60, 120, (110, 140, 110, 14),
                beak_color=(110, 140, 110, 14), face_color=(110, 140, 110, 14))
    img.paste(Image.alpha_composite(img, wm), (0, 0))
    d.rectangle([(rx + 10) * S, (ly + 10) * S, (rx + pw - 10) * S, (ly + ph - 10) * S],
                outline=(150, 138, 105, 255), width=max(1, int(1.2 * S)))
    centered_text(d, rx + pw / 2, ly + 26, "VISAS", font(F_SERIF, 20), TEAL,
                  spacing=6)
    d.text(((rx + pw - 30) * S, (ly + 30) * S), "5", font=font(F_SANS, 13),
           fill=(110, 105, 92, 255), anchor="ra")
    d.line([(rx + 44) * S, (ly + 56) * S, (rx + pw - 44) * S, (ly + 56) * S],
           fill=GOLD, width=max(2, int(1.6 * S)))
    # --- Schengen visa sticker
    vx, vy, vw, vh = rx + 24, ly + 72, pw - 48, 148
    d.rectangle([vx * S, vy * S, (vx + vw) * S, (vy + vh) * S],
                fill=(232, 238, 244, 255), outline=(70, 95, 125, 255),
                width=max(2, int(1.8 * S)))
    d.rectangle([(vx + 5) * S, (vy + 5) * S, (vx + vw - 5) * S, (vy + vh - 5) * S],
                outline=(70, 95, 125, 255), width=max(1, int(1.0 * S)))
    # header band
    d.rectangle([vx * S, vy * S, (vx + vw) * S, (vy + 26) * S],
                fill=(38, 62, 92, 255))
    centered_text(d, vx + vw / 2, vy + 5, "SCHENGEN VISA  •  KINGDOM OF NORWAY",
                  font(F_SANS_B, 12.5), (240, 244, 248, 255), spacing=0)
    # Norwegian flag (simplified cross)
    fx0, fy0, fw, fh = vx + vw - 58, vy + 36, 44, 32
    d.rectangle([fx0 * S, fy0 * S, (fx0 + fw) * S, (fy0 + fh) * S],
                fill=(186, 36, 48, 255), outline=(120, 120, 120, 255), width=1)
    d.rectangle([(fx0 + 12) * S, fy0 * S, (fx0 + 20) * S, (fy0 + fh) * S],
                fill=(255, 255, 255, 255))
    d.rectangle([fx0 * S, (fy0 + 12) * S, (fx0 + fw) * S, (fy0 + 20) * S],
                fill=(255, 255, 255, 255))
    d.rectangle([(fx0 + 14) * S, fy0 * S, (fx0 + 18) * S, (fy0 + fh) * S],
                fill=(0, 44, 96, 255))
    d.rectangle([fx0 * S, (fy0 + 14) * S, (fx0 + fw) * S, (fy0 + 18) * S],
                fill=(0, 44, 96, 255))
    # visa rows
    f_vl = font(F_SANS, 10)
    f_vv = font(F_SANS_B, 13.5)
    rows = [("TYPE", "C  —  MULTIPLE ENTRIES"),
            ("VALID FROM  /  UNTIL", "01 JUL 2026  —  01 JAN 2027"),
            ("DURATION OF STAY", "90 DAYS"),
            ("No.", "NOR 2026 084417")]
    yy = vy + 33
    for lab, val in rows:
        d.text(((vx + 12) * S, yy * S), lab, font=f_vl, fill=(110, 105, 92, 255))
        d.text(((vx + 148) * S, (yy - 2) * S), val, font=f_vv, fill=INK)
        yy += 19
    f_cond = font(F_SANS_I, 11)
    d.text(((vx + 12) * S, (vy + 116) * S),
           "Conditions: no recourse to public funds. Employment only",
           font=f_cond, fill=(70, 70, 66, 255))
    d.text(((vx + 12) * S, (vy + 130) * S),
           "aboard Veskari-registered vessels.",
           font=f_cond, fill=(70, 70, 66, 255))
    # --- stamps grid: 2 cols x 3 rows
    BLUE = (38, 84, 150, 215)
    DBLUE = (30, 60, 120, 215)
    TEAL_I = (24, 110, 110, 215)
    PURP = (96, 60, 130, 215)
    GREEN = (34, 110, 70, 215)
    RED = (168, 44, 36, 215)
    gy = ly + 240
    gx0, gx1 = rx + 30, rx + pw / 2 + 6
    # row 1: round exit Veskar / rect entry Bergen
    st, pos = stamp_round(gx0 + 96, gy + 48, 46, BLUE, "VESKAR", "VESTHAVN",
                          "DEPARTURE", "12 JUL 2026", -6)
    img.alpha_composite(distress(st, 3), pos)
    st = stamp_rect(190, 84, BLUE, [("BERGEN — NORWAY", F_SANS_B, 13),
                                    ("ENTRY", F_SANS_B, 16),
                                    ("12 JUL 2026", F_SANS_B, 13)], 5)
    img.alpha_composite(distress(st, 4), (int((gx1 - 8) * S), int((gy - 6) * S)))
    # row 2: rect exit Bergen / rect entry Keflavik
    gy += 104
    st = stamp_rect(190, 84, DBLUE, [("BERGEN", F_SANS_B, 13),
                                     ("DEPARTURE", F_SANS_B, 16),
                                     ("28 JUL 2026", F_SANS_B, 13)], -4)
    img.alpha_composite(distress(st, 5), (int((gx0 - 8) * S), int((gy - 6) * S)))
    st = stamp_rect(190, 84, TEAL_I, [("KEFLAVÍK — ICELAND", F_SANS_B, 13),
                                      ("ENTRY", F_SANS_B, 16),
                                      ("28 JUL 2026", F_SANS_B, 13)], 4)
    img.alpha_composite(distress(st, 6), (int((gx1 - 8) * S), int((gy - 6) * S)))
    # row 3: rect entry Aberdeen / round arrival Veskar
    gy += 104
    st = stamp_rect(190, 84, PURP, [("ABERDEEN — UNITED KINGDOM", F_SANS_B, 11.5),
                                    ("ENTRY", F_SANS_B, 16),
                                    ("22 SEP 2026", F_SANS_B, 13)], -5)
    img.alpha_composite(distress(st, 7), (int((gx0 - 8) * S), int((gy - 6) * S)))
    st, pos = stamp_round(gx1 + 96, gy + 48, 46, GREEN, "VESKAR", "VESTHAVN",
                          "ARRIVAL", "14 OCT 2026", 6)
    img.alpha_composite(distress(st, 8), pos)
    # fee stamp (red), overlapping bottom-left of the stamp block
    st = stamp_rect(240, 56, RED, [("GEOTHERMAL LEVY  40 KR — PAID", F_SANS_B, 11)],
                    -11)
    paste_stamp(img, distress(st, 9, dots=180), rx + 168, ly + 588)
    # seaman's book note
    f_note = font(F_SERIF_I, 12.5)
    d.text(((rx + 28) * S, (ly + 646) * S),
           "NB: this passport is also the holder's seaman's book",
           font=f_note, fill=(70, 70, 66, 255), anchor="la")
    d.text(((rx + 28) * S, (ly + 662) * S),
           "(sjómannabók) under Veskar Maritime Code §12.",
           font=f_note, fill=(70, 70, 66, 255), anchor="la")


# ---------------------------------------------------------------- render
def main():
    img = Image.new("RGBA", (W * S, H * S), DESK)
    d = ImageDraw.Draw(img)
    # desk vignette + faint plank lines
    for i in range(0, H * S, 6):
        d.line([(0, i), (W * S, i)], fill=(30, 36, 43, 18), width=1)
    # soft shadow under the spread
    shadow = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([28 * S, 172 * S, 996 * S, 862 * S], radius=6 * S,
                         fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10 * S))
    img = Image.alpha_composite(img, shadow)
    d = ImageDraw.Draw(img)

    lx, ly, pw, ph = 32, 167, 474, 690
    rx = lx + pw + 10
    build_left(img, lx, ly, pw, ph)
    build_right(img, rx, ly, pw, ph)
    # centre gutter shadow
    gut = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gut)
    gd.rectangle([(lx + pw - 2) * S, ly * S, (lx + pw + 12) * S, (ly + ph) * S],
                 fill=(0, 0, 0, 60))
    gd.rectangle([(lx + pw + 8) * S, ly * S, (lx + pw + 10) * S, (ly + ph) * S],
                 fill=(0, 0, 0, 90))
    gut = gut.filter(ImageFilter.GaussianBlur(3 * S))
    img = Image.alpha_composite(img, gut)
    # page outer edges (slight curl highlight)
    d = ImageDraw.Draw(img)
    d.line([(lx) * S, ly * S, (lx) * S, (ly + ph) * S], fill=(255, 255, 255, 40),
           width=max(1, S // 2))
    d.line([(rx + pw) * S, ly * S, (rx + pw) * S, (ly + ph) * S],
           fill=(255, 255, 255, 40), width=max(1, S // 2))

    img = img.convert("RGB").resize((W, H), Image.LANCZOS)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, optimize=True)
    print(f"wrote {OUT} {OUT.stat().st_size} bytes, {img.size}")


if __name__ == "__main__":
    main()
