#!/usr/bin/env python3
"""Flux.1 Dev on the DGX Spark: fork handle, in-shield tagline, four TV backgrounds."""

from __future__ import annotations

import gen_assets
import gen_logo
from PIL import Image, ImageDraw

OUT = gen_logo.OUT
SRC = gen_logo.SRC
CANVAS = gen_logo.CANVAS
ORIGIN = gen_logo.ORIGIN

FORK_PROMPT = (
    "Flat vector logo. Lengthen the lower half of the barbecue fork handle so it "
    "continues downward well past the small orange flame and ends in a rounded "
    "cream handle tip with a circular hole. Thick black outline, same cream color "
    "as the fork head. The handle must not stop at the flame. No new text."
)
TAG_PROMPT = (
    "Stamp gold lettering into the existing black shield, using the same gold as "
    "the word SMOKEHOUSE. The letters are part of the shield, not a separate sign "
    "or rectangle. Exact text with a small five-point gold star between the phrases: "
    "LOW & SLOW. star DONE RIGHT. No plaque, no screws, no bolts, no extra border."
)

BACKGROUNDS = [
    (
        "bg-platters",
        "Dark restaurant photograph of two barbecue platters on a black table, "
        "one smaller and one large. Sliced smoked brisket with pepper bark, St. Louis ribs, "
        "pulled pork, smoked sausage, half a smoked chicken, Texas toast, and small sides. "
        "Warm low light, charcoal background, no text, no logo, no people, no hands.",
    ),
    (
        "bg-sandwiches",
        "Dark restaurant photograph of barbecue sandwiches and specials: a sliced brisket "
        "sandwich, a brisket grilled cheese, a smoked quesadilla cut in wedges, and a baked "
        "potato loaded with mac and cheese and brisket. Black tray, warm low light, no text, "
        "no logo, no people, no hands.",
    ),
    (
        "bg-alacarte",
        "Dark restaurant photograph of barbecue by the pound and wings: a pile of sliced "
        "brisket, pulled pork, rib tips, smoked sausage links, smoked chicken, and a tray of "
        "whole chicken wings both smoked and fried. Black surface, warm low light, no text, "
        "no logo, no people, no hands.",
    ),
    (
        "bg-sides",
        "Dark restaurant photograph of barbecue sides, drinks, and desserts: macaroni and "
        "cheese, collard greens, baked beans, sweet corn, potato wedges, a hotel pan of sides, "
        "soda cans, iced tea, carrot cake, strawberry cake, a brownie, and a fruit cup. "
        "Warm low light, charcoal background, no text, no logo, no people, no hands.",
    ),
]


def main() -> None:
    logo = Image.open(SRC).convert("RGBA")
    base = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    base.paste(logo, ORIGIN, logo)
    ox, oy = ORIGIN
    fork = Image.new("L", CANVAS, 0)
    gen_logo.capsule(ImageDraw.Draw(fork), (ox + 400, oy + 330), (ox + 300, oy + 520), 56)
    fork.save(OUT / "mask_fork.png")
    rgb = Image.new("RGB", CANVAS, (0, 0, 0))
    rgb.paste(base, mask=base.getchannel("A"))
    rgb.save(OUT / "logo_base.png")
    gen_logo.upload(OUT / "logo_base.png")
    gen_logo.upload(OUT / "mask_fork.png")
    fork_png = gen_logo.flux_inpaint("logo_base.png", "mask_fork.png", FORK_PROMPT, 11, "logo_fork2")
    edited = gen_logo.apply_edit(base, fork_png, fork, keep_black=False)

    tag = Image.new("L", CANVAS, 0)
    ImageDraw.Draw(tag).polygon(
        [
            (ox + 200, oy + 618),
            (ox + 634, oy + 618),
            (ox + 470, oy + 698),
            (ox + 364, oy + 698),
        ],
        fill=255,
    )
    tag.save(OUT / "mask_tag.png")
    rgb = Image.new("RGB", CANVAS, (0, 0, 0))
    rgb.paste(edited, mask=edited.getchannel("A"))
    rgb.save(OUT / "logo_after_fork.png")
    gen_logo.upload(OUT / "logo_after_fork.png")
    gen_logo.upload(OUT / "mask_tag.png")
    tag_png = gen_logo.flux_inpaint("logo_after_fork.png", "mask_tag.png", TAG_PROMPT, 12, "logo_tag")
    final = gen_logo.apply_edit(edited, tag_png, tag, keep_black=True)
    final.save(OUT / "logo_flux.png")
    print(f"wrote {OUT / 'logo_flux.png'}", flush=True)

    for name, prompt in BACKGROUNDS:
        png = gen_assets.run(prompt, 1408, 768, 20261020, name)
        im = Image.open(png).convert("RGB")
        im.save(OUT.parent / f"{name}.jpg", quality=90, optimize=True)
        print(f"wrote {OUT.parent / f'{name}.jpg'}", flush=True)


if __name__ == "__main__":
    main()
