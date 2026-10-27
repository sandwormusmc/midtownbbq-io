#!/usr/bin/env python3
"""Edit the Midtown logo on the DGX Spark with Flux.1 Dev inpainting.

Flux Kontext on this ComfyUI requires a Comfy.org login, so the local
Flux.1 Dev weights are used instead. Two masked edits:

1. Lengthen the fork handle past the center flame.
2. Plate LOW & SLOW. ★ DONE RIGHT. onto the bottom border.
"""

from __future__ import annotations

import json
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HOST = "http://192.168.1.205:8188"
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets" / "generated"
SRC = ROOT.parent / "brand-kit" / "logos" / "primary_logo_lockup.png"
CANVAS = (848, 800)  # multiples of 16
ORIGIN = (7, 0)  # center the 834px logo on the 848px canvas

FORK_PROMPT = (
    "Flat vector logo artwork on black. Continue the cream barbecue fork handle "
    "downward past the small orange flame. Thick black outline, same cream color "
    "as the existing fork, ending in a rounded handle tip with a circular hole. "
    "The handle is longer than before and does not stop at the flame. No text."
)
PLATE_PROMPT = (
    "Flat vector barbecue logo nameplate laid across the bottom gold border of the shield. "
    "A black enamel plate with a worn gold rim and a stamped metal recess behind the letters. "
    "Stamped gold capital letters in the same gold color as the logo read exactly: "
    "LOW & SLOW. then a stylized five-point gold star then DONE RIGHT. "
    "No bolts, no rivets, no other words, black around the plate."
)


def post_json(path, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        HOST + path, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def upload(path: Path) -> str:
    subprocess.run(
        [
            "curl", "-sS", "-m", "60",
            "-F", f"image=@{path}",
            "-F", "overwrite=true",
            "-F", "type=input",
            f"{HOST}/upload/image",
        ],
        check=True,
        capture_output=True,
    )
    return path.name


def flux_inpaint(image_name: str, mask_name: str, prompt: str, seed: int, prefix: str) -> Path:
    wf = {
        "prompt": {
            "1": {
                "class_type": "UNETLoader",
                "inputs": {"unet_name": "flux1-dev.safetensors", "weight_dtype": "default"},
            },
            "2": {
                "class_type": "DualCLIPLoader",
                "inputs": {
                    "clip_name1": "t5xxl_fp8_e4m3fn.safetensors",
                    "clip_name2": "clip_l.safetensors",
                    "type": "flux",
                },
            },
            "3": {"class_type": "VAELoader", "inputs": {"vae_name": "ae.safetensors"}},
            "4": {"class_type": "LoadImage", "inputs": {"image": image_name}},
            "5": {"class_type": "LoadImage", "inputs": {"image": mask_name}},
            "6": {
                "class_type": "ImageToMask",
                "inputs": {"image": ["5", 0], "channel": "red"},
            },
            "7": {
                "class_type": "CLIPTextEncodeFlux",
                "inputs": {
                    "clip": ["2", 0],
                    "clip_l": prompt[:220],
                    "t5xxl": prompt,
                    "guidance": 3.5,
                },
            },
            "8": {
                "class_type": "CLIPTextEncodeFlux",
                "inputs": {
                    "clip": ["2", 0],
                    "clip_l": "",
                    "t5xxl": "",
                    "guidance": 3.5,
                },
            },
            "9": {
                "class_type": "VAEEncodeForInpaint",
                "inputs": {
                    "pixels": ["4", 0],
                    "vae": ["3", 0],
                    "mask": ["6", 0],
                    "grow_mask_by": 6,
                },
            },
            "10": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["1", 0],
                    "seed": seed,
                    "steps": 24,
                    "cfg": 1.0,
                    "sampler_name": "euler",
                    "scheduler": "simple",
                    "positive": ["7", 0],
                    "negative": ["8", 0],
                    "latent_image": ["9", 0],
                    "denoise": 1.0,
                },
            },
            "11": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["10", 0], "vae": ["3", 0]},
            },
            "12": {
                "class_type": "SaveImage",
                "inputs": {"images": ["11", 0], "filename_prefix": prefix},
            },
        }
    }
    queued = post_json("/prompt", wf)
    prompt_id = queued["prompt_id"]
    print(f"queued {prefix} {prompt_id}", flush=True)
    deadline = time.time() + 900
    while time.time() < deadline:
        with urllib.request.urlopen(HOST + "/history/" + prompt_id, timeout=30) as resp:
            hist = json.load(resp)
        if prompt_id in hist:
            status = hist[prompt_id].get("status", {})
            if status.get("status_str") == "error":
                raise SystemExit(json.dumps(status)[:2000])
            outputs = hist[prompt_id].get("outputs", {})
            for node in outputs.values():
                for image in node.get("images", []):
                    q = urllib.parse.urlencode(
                        {
                            "filename": image["filename"],
                            "subfolder": image.get("subfolder", ""),
                            "type": image.get("type", "output"),
                        }
                    )
                    dest = OUT / f"{prefix}.png"
                    urllib.request.urlretrieve(HOST + "/view?" + q, dest)
                    print(f"saved {dest}", flush=True)
                    return dest
            raise SystemExit(f"no image for {prefix}: {outputs}")
        time.sleep(4)
    raise SystemExit(f"timeout {prefix}")


def capsule(draw, a, b, width, fill=255):
    draw.line([a, b], fill=fill, width=width)
    r = width // 2
    for p in (a, b):
        draw.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=fill)


def prepare() -> tuple[Image.Image, Image.Image, Image.Image]:
    logo = Image.open(SRC).convert("RGBA")
    base = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    base.paste(logo, ORIGIN, logo)
    ox, oy = ORIGIN
    fork = Image.new("L", CANVAS, 0)
    plate = Image.new("L", CANVAS, 0)
    fd = ImageDraw.Draw(fork)
    # Lower half of the fork, from the existing handle through the open
    # space past the center flame and above the MIDTOWN letters.
    capsule(fd, (ox + 392, oy + 355), (ox + 338, oy + 424), 42)
    pd = ImageDraw.Draw(plate)
    # Nameplate sitting on the bottom gold border, overlapping the point.
    pd.rounded_rectangle((ox + 130, oy + 640, ox + 700, oy + 770), radius=18, fill=255)
    OUT.mkdir(parents=True, exist_ok=True)
    fork.save(OUT / "mask_fork.png")
    plate.save(OUT / "mask_plate.png")
    rgb = Image.new("RGB", CANVAS, (0, 0, 0))
    rgb.paste(base, mask=base.getchannel("A"))
    rgb.save(OUT / "logo_base.png")
    return base, fork, plate


def apply_edit(base: Image.Image, flux_path: Path, mask: Image.Image, keep_black: bool) -> Image.Image:
    flux = Image.open(flux_path).convert("RGB")
    if flux.size != base.size:
        flux = flux.resize(base.size, Image.Resampling.LANCZOS)
    soft = mask.filter(ImageFilter.GaussianBlur(1.2))
    out = base.copy()
    bp = out.load()
    fp = flux.load()
    mp = soft.load()
    fr, fg, fb = flux.split()
    for y in range(base.size[1]):
        for x in range(base.size[0]):
            m = mp[x, y]
            if m < 8:
                continue
            r, g, b = fp[x, y]
            if not keep_black and r + g + b < 48:
                continue
            src = bp[x, y]
            t = m / 255
            bp[x, y] = (
                int(src[0] * (1 - t) + r * t),
                int(src[1] * (1 - t) + g * t),
                int(src[2] * (1 - t) + b * t),
                max(src[3], m if (keep_black or r + g + b >= 48) else src[3]),
            )
    return out


def main() -> None:
    base, fork, plate = prepare()
    upload(OUT / "logo_base.png")
    upload(OUT / "mask_fork.png")
    fork_png = flux_inpaint("logo_base.png", "mask_fork.png", FORK_PROMPT, 20261020, "logo_fork")
    edited = apply_edit(base, fork_png, fork, keep_black=False)
    rgb = Image.new("RGB", CANVAS, (0, 0, 0))
    rgb.paste(edited, mask=edited.getchannel("A"))
    rgb.save(OUT / "logo_after_fork.png")
    upload(OUT / "logo_after_fork.png")
    upload(OUT / "mask_plate.png")
    plate_png = flux_inpaint(
        "logo_after_fork.png", "mask_plate.png", PLATE_PROMPT, 20261021, "logo_plate"
    )
    final = apply_edit(edited, plate_png, plate, keep_black=True)
    final.save(OUT / "logo_flux.png")
    print(f"wrote {OUT / 'logo_flux.png'}", flush=True)


if __name__ == "__main__":
    main()
