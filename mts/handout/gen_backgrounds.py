#!/usr/bin/env python3
"""Generate different background options for the Midtown handout."""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parent
ASSET = ROOT / "assets"
GEN = ASSET / "generated"


def generate_charcoal():
    """Simple charcoal gradient background."""
    W, H = 2550, 3300
    canvas = Image.new("RGB", (W, H), (11, 11, 11))
    
    # Add subtle gradient
    fade = Image.new("L", (1, H), 0)
    fp = fade.load()
    for row in range(H):
        if row < int(H * 0.1):
            fp[0, row] = 0
        elif row > int(H * 0.9):
            fp[0, row] = 85
        else:
            fp[0, row] = int(85 * (row - int(H * 0.1)) / (int(H * 0.9) - int(H * 0.1)))
    mask = fade.resize((W, H))
    
    # Darker charcoal bottom
    charcoal = Image.new("RGB", (W, H), (8, 7, 6))
    canvas = Image.composite(charcoal, canvas, mask)
    
    # Vignette
    vignette = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vignette)
    vd.rectangle((0, 0, W, H), fill=100)
    vd.ellipse((-int(W * 0.08), -int(H * 0.02), int(W * 1.08), int(H * 0.62)), fill=0)
    vignette = vignette.filter(ImageFilter.GaussianBlur(90))
    canvas = Image.composite(Image.new("RGB", (W, H), (11, 11, 11)), canvas, vignette)
    
    canvas = ImageEnhance.Brightness(canvas).enhance(0.95)
    canvas.save(ASSET / "background_charcoal.jpg", quality=90, optimize=True)
    print(f"Created: background_charcoal.jpg")


def generate_wood():
    """Warm wood tone background."""
    W, H = 2550, 3300
    canvas = Image.new("RGB", (W, H), (100, 70, 50))
    
    # Add subtle noise
    draw = ImageDraw.Draw(canvas)
    import random
    for _ in range(5000):
        x = random.randint(0, W - 1)
        y = random.randint(0, H - 1)
        val = random.randint(0, 30)
        draw.point((x, y), fill=(val, val, val))
    
    # Gradient
    fade = Image.new("L", (1, H), 0)
    fp = fade.load()
    for row in range(H):
        fp[0, row] = int(150 * (row / H))
    mask = fade.resize((W, H))
    
    dark = Image.new("RGB", (W, H), (70, 50, 40))
    canvas = Image.composite(canvas, dark, mask)
    
    canvas.save(ASSET / "background_wood.jpg", quality=90, optimize=True)
    print(f"Created: background_wood.jpg")


def generate_dark():
    """Very dark background with subtle texture."""
    W, H = 2550, 3300
    canvas = Image.new("RGB", (W, H), (8, 7, 6))
    
    # Add subtle noise
    draw = ImageDraw.Draw(canvas)
    import random
    for _ in range(30000):
        x = random.randint(0, W - 1)
        y = random.randint(0, H - 1)
        val = random.randint(0, 10)
        draw.point((x, y), fill=(val, val, val))
    
    # Fade to darker
    fade = Image.new("L", (1, H), 0)
    fp = fade.load()
    for row in range(H):
        fp[0, row] = int(200 * (row / H))
    mask = fade.resize((W, H))
    
    charcoal = Image.new("RGB", (W, H), (5, 5, 5))
    canvas = Image.composite(charcoal, canvas, mask)
    
    canvas.save(ASSET / "background_dark.jpg", quality=90, optimize=True)
    print(f"Created: background_dark.jpg")


def regenerate_all():
    """Regenerate backgrounds using existing assets."""
    from build import composite_background, prepare_tv_backgrounds
    composite_background()
    prepare_tv_backgrounds()
    print("Regenerated all backgrounds from assets")


def main():
    parser = argparse.ArgumentParser(description="Generate background options")
    parser.add_argument("type", choices=["charcoal", "wood", "dark", "all", "regen"], 
                       help="Background type to generate")
    args = parser.parse_args()
    
    if args.type == "charcoal":
        generate_charcoal()
    elif args.type == "wood":
        generate_wood()
    elif args.type == "dark":
        generate_dark()
    elif args.type == "all":
        generate_charcoal()
        generate_wood()
        generate_dark()
    elif args.type == "regen":
        regenerate_all()


if __name__ == "__main__":
    main()
