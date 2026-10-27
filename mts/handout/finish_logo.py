#!/usr/bin/env python3
"""Extend the fork past the flame and open the shield for the tagline.

The fork continuation is the original handle artwork, repeated along its own
angle, so the stroke, outline, and hole match the rest of the mark. Flux.1 Dev
inpainting kept stopping at the flame and cutting through MIDTOWN.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent
SRC = Path("/home/matt/projects/moldvan.com/mts/brand-kit/logos/primary_logo_lockup.png")
OUT = ROOT / "assets" / "generated"
NAMEPLATE = OUT / "nameplate_center.png"


def is_cream(p):
    r, g, b, a = p
    return a > 180 and r > 200 and g > 185 and b > 150 and abs(r - g) < 55


def is_dark(p):
    r, g, b, a = p
    return a > 160 and r + g + b < 150


def is_flame(p):
    r, g, b, a = p
    return a > 140 and r > 160 and 40 < g < 180 and b < 90 and r > g


def handle_mask(orig: Image.Image):
    px = orig.load()
    cream = []
    for y in range(318, 412):
        for x in range(334, 424):
            if is_cream(px[x, y]) and not is_flame(px[x, y]):
                cream.append((x, y))
    cream_set = set(cream)
    outline = []
    for y in range(308, 422):
        for x in range(322, 436):
            p = px[x, y]
            if not is_dark(p) or is_flame(p):
                continue
            if any((x + dx, y + dy) in cream_set for dy in range(-3, 4) for dx in range(-3, 4)):
                outline.append((x, y))
    return cream, outline


def sprite_from(orig: Image.Image, points):
    sprite = Image.new("RGBA", orig.size, (0, 0, 0, 0))
    sp = sprite.load()
    op = orig.load()
    for x, y in points:
        sp[x, y] = op[x, y]
    return sprite


def extend_fork(canvas: Image.Image, orig: Image.Image) -> None:
    cream, outline = handle_mask(orig)
    top = [p for p in cream if p[1] < 350]
    bot = [p for p in cream if p[1] > 376]

    def cen(pts):
        return sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)

    tx, ty = cen(top)
    bx, by = cen(bot)
    dx, dy = bx - tx, by - ty
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    # Far enough that the hole sits on the upper half of MIDTOWN, past the flame.
    shift = 92
    sx, sy = ux * shift, uy * shift

    shaft_pts = [(x, y) for x, y in cream + outline if 336 <= y <= 362]
    tip_pts = [(x, y) for x, y in cream + outline if y >= 370]
    shaft = sprite_from(orig, shaft_pts)
    tip = sprite_from(orig, tip_pts)

    # Cover the existing hole, then continue the same shaft past the flame.
    steps = int(shift) + 8
    for i in range(steps):
        ox = round(ux * i)
        oy = round(uy * i)
        canvas.alpha_composite(shaft, (ox, oy))
    canvas.alpha_composite(tip, (round(sx), round(sy)))


def extend_shield(canvas: Image.Image) -> Image.Image:
    """Stretch the existing lower rim into a deeper point. Same border, no plate."""
    cut = 616
    top = canvas.crop((0, 0, canvas.width, cut))
    bot = canvas.crop((0, cut, canvas.width, canvas.height))
    # Keep only the original shield point, not empty canvas below it.
    bbox = bot.getbbox()
    if bbox:
        bot = bot.crop((0, 0, bot.width, bbox[3]))
    bot = bot.resize((bot.width, 210), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", (canvas.width, cut + bot.height + 8), (0, 0, 0, 0))
    out.paste(top, (0, 0), top)
    out.paste(bot, (0, cut), bot)
    # The stretched rivet is a small gold blob above the point. Cover it.
    px = out.load()
    seen = set()
    blobs = []
    for y in range(cut + 30, out.height - 24):
        for x in range(340, 500):
            if (x, y) in seen:
                continue
            r, g, b, a = px[x, y]
            if not (a > 200 and r > 200 and g > 160 and b < 120):
                continue
            stack = [(x, y)]
            comp = []
            while stack:
                cx, cy = stack.pop()
                if (cx, cy) in seen or not (340 <= cx < 500 and cut + 30 <= cy < out.height - 24):
                    continue
                rr, gg, bb, aa = px[cx, cy]
                if not (aa > 200 and rr > 200 and gg > 160 and bb < 120):
                    continue
                seen.add((cx, cy))
                comp.append((cx, cy))
                stack.extend(((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)))
            if 8 < len(comp) < 400:
                blobs.append(comp)
    if blobs:
        blob = min(blobs, key=len)
        for x, y in blob:
            px[x, y] = (12, 8, 6, 255)
    return out


def place_tagline(canvas: Image.Image) -> None:
    """Lift the Flux lettering off the rejected plate and stamp it into the shield."""
    if not NAMEPLATE.exists():
        return
    words = Image.open(NAMEPLATE).convert("RGB")
    # Interior of the plate only: drop the rectangular frame and corner screws.
    words = words.crop((140, 96, 1260, 302))
    px = words.load()
    w, h = words.size
    cut = Image.new("RGBA", words.size, (0, 0, 0, 0))
    cp = cut.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if r > 145 and g > 95 and b < 130 and r > b + 35:
                cp[x, y] = (min(255, r + 10), g, b, 255)
    cut = cut.crop(cut.getbbox())
    max_w, max_h = 300, 62
    scale = min(max_w / cut.width, max_h / cut.height)
    cut = cut.resize((max(1, round(cut.width * scale)), max(1, round(cut.height * scale))), Image.Resampling.LANCZOS)
    x = (canvas.width - cut.width) // 2
    y = 618
    shadow = Image.new("RGBA", cut.size, (0, 0, 0, 0))
    sp = shadow.load()
    src = cut.load()
    for yy in range(cut.height):
        for xx in range(cut.width):
            if src[xx, yy][3] > 40:
                sp[xx, yy] = (12, 6, 2, 210)
    shadow = shadow.filter(ImageFilter.GaussianBlur(1.2))
    canvas.alpha_composite(shadow, (x + 2, y + 3))
    canvas.alpha_composite(cut, (x, y))


def build() -> Image.Image:
    orig = Image.open(SRC).convert("RGBA")
    extra = 120
    canvas = Image.new("RGBA", (orig.width, orig.height + extra), (0, 0, 0, 0))
    canvas.paste(orig, (0, 0), orig)
    extend_fork(canvas, orig)
    canvas = extend_shield(canvas)
    place_tagline(canvas)
    return canvas


def main() -> None:
    logo = build()
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / "logo_flux.png"
    logo.save(dest)
    print(f"wrote {dest} {logo.size}", flush=True)


if __name__ == "__main__":
    main()
