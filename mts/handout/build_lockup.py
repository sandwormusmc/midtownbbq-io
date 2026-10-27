#!/usr/bin/env python3
"""Build the Midtown lockup with LOW & SLOW. DONE RIGHT. set along the shield border.

The previous lockup (mts/brand-kit/logos/primary_logo_lockup.png) is the border
reference: the tagline rides the chevron under the shield, each letter rotated
to the local angle of that edge, in the same aged gold as the rim. It reads as
part of the badge instead of a separate plate bolted onto the logo.

Output: assets/generated/logo_lockup_v2.png  (RGBA, transparent corners)
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
SRC = ROOT.parent / "brand-kit" / "logos" / "primary_logo_lockup.png"
OUT = ROOT / "assets" / "generated"
FONT = ROOT / "fonts" / "Oswald[wght].ttf"

EXTRA_BOTTOM = 78  # room below the shield for the tagline


def bottom_edge(img: Image.Image) -> dict[int, int]:
    """Lowest opaque pixel per column: the outer edge of the chevron."""
    px = img.load()
    w, h = img.size
    edge: dict[int, int] = {}
    for x in range(w):
        last = 0
        for y in range(h - 1, 480, -1):
            if px[x, y][3] > 40:
                last = y
                break
        edge[x] = last
    return edge


def edge_y(edge: dict[int, int], x: float) -> float:
    xs = sorted(edge)
    if x <= xs[0]:
        return float(edge[xs[0]])
    if x >= xs[-1]:
        return float(edge[xs[-1]])
    lo = xs[0]
    for hi in xs[1:]:
        if x <= hi:
            t = (x - lo) / (hi - lo) if hi > lo else 0
            return edge[lo] + t * (edge[hi] - edge[lo])
        lo = hi
    return float(edge[xs[-1]])


def edge_angle(edge: dict[int, int], x: float) -> float:
    d = 8
    return math.degrees(math.atan2(edge_y(edge, x + d) - edge_y(edge, x - d), 2 * d))


def stamp_word(
    canvas: Image.Image,
    text: str,
    font: ImageFont.FreeTypeFont,
    gold: tuple[int, int, int],
    edge: dict[int, int],
    x_start: float,
    x_end: float,
    tracking: float = 4.0,
    gap: float = 10.0,
) -> None:
    widths = [font.getlength(ch) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = x_start + ((x_end - x_start) - total) / 2
    ascent, descent = font.getmetrics()
    pad = 8
    for ch, w in zip(text, widths):
        cx = x + w / 2
        ang = edge_angle(edge, cx)
        gw = int(math.ceil(w)) + pad * 2
        gh = ascent + descent + pad * 2
        tile = Image.new("RGBA", (gw, gh), (0, 0, 0, 0))
        d = ImageDraw.Draw(tile)
        d.text((pad, pad), ch, font=font, fill=(48, 24, 4, 255))
        d.text((pad, pad - 1), ch, font=font, fill=gold + (255,))
        rot = tile.rotate(-ang, resample=Image.Resampling.BICUBIC, expand=True)
        shadow = Image.new("RGBA", rot.size, (0, 0, 0, 0))
        shadow.paste((10, 6, 2, 190), (0, 0), rot.split()[3])
        shadow = shadow.filter(ImageFilter.GaussianBlur(1.5))
        # Baseline follows the chevron; the word sits just below that edge.
        py = edge_y(edge, cx) + gap - (pad + ascent)
        canvas.alpha_composite(shadow, (int(cx - rot.width / 2) + 2, int(py) + 3))
        canvas.alpha_composite(rot, (int(cx - rot.width / 2), int(py)))
        x += w + tracking


def build() -> Image.Image:
    src = Image.open(SRC).convert("RGBA")
    edge = bottom_edge(src)

    canvas = Image.new("RGBA", (src.width, src.height + EXTRA_BOTTOM), (0, 0, 0, 0))
    canvas.alpha_composite(src, (0, 0))

    px = src.load()
    acc = [0, 0, 0]
    n = 0
    for x in range(40, src.width - 40, 6):
        y = edge[x]
        if 560 < y < 700:
            r, g, b, a = px[x, y - 3]
            if a > 180 and r > 190 and g > 140:
                acc[0] += r
                acc[1] += g
                acc[2] += b
                n += 1
    gold = tuple(v // n for v in acc) if n else (239, 157, 29)

    size = 46
    font = ImageFont.truetype(str(FONT), size)
    try:
        font.set_variation_by_axes([600])
    except Exception:
        pass
    # Each word rides one half of the chevron, mirrored.
    stamp_word(canvas, "LOW & SLOW", font, gold, edge, 70, 380)
    stamp_word(canvas, "DONE RIGHT", font, gold, edge, 454, 764)

    return canvas


def main() -> None:
    logo = build()
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / "logo_lockup_v2.png"
    logo.save(dest)
    print(f"wrote {dest} {logo.size}", flush=True)


if __name__ == "__main__":
    main()
