#!/usr/bin/env python3
"""Generate Midtown handout artwork on the DGX Spark ComfyUI (Flux.1 Dev)."""

import json
import time
import urllib.request
from pathlib import Path

HOST = "http://192.168.1.205:8188"
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets" / "generated"
OUT.mkdir(parents=True, exist_ok=True)

BRISKET = (
    "Photorealistic Texas barbecue smoked beef brisket, thick slices on a matte black "
    "sheet pan. The outside is a very dark coarse cracked black-pepper bark, almost "
    "black and crusty. Just under that bark is a thin pink smoke ring. The sliced "
    "interior is moist brownish-tan beef with a visible grain, not a rare red steak "
    "and not roast beef. A thick cap of rendered creamy white fat lies across the top "
    "of the meat. Glossy juices, warm low amber light, dark charcoal background, "
    "restaurant food photography, slightly underexposed. No herbs, no parsley, no "
    "lemon, no tomato, no bread, no toast, no sandwich, no hands, no people, no text."
)

TEXTURE = (
    "Very dark charcoal stained wood and black smoke texture, subtle warm ember "
    "glow deep in the grain, matte, low contrast, underexposed, rustic barbecue "
    "atmosphere, no food, no plate, no text, no logo, no people."
)

COMBOS = (
    "Photorealistic Midtown Smokehouse combo platter, Texas-style barbecue. "
    "Includes sliced brisket, pulled pork, ribs, and sausage on a dark wood cutting board. "
    "Accompanied by two small sides: baked beans and potato wedges. "
    "Crispy Texas toast on the side. Warm low amber light, dark charcoal background, "
    "restaurant food photography, slightly underexposed. No hands, no people, no text."
)

SANDWICHES = (
    "Photorealistic Midtown Smokehouse sandwich platter, Texas-style barbecue. "
    "Includes sliced brisket, pulled pork, and crispy chicken sandwiches on a dark wood board. "
    "Served with coleslaw and pickles. Warm low amber light, dark charcoal background, "
    "restaurant food photography, slightly underexposed. No hands, no people, no text."
)

WINGS = (
    "Photorealistic Midtown Smokehouse whole wings, Texas-style barbecue. "
    "Includes 6 smoked wings and 6 fried wings on a dark metal tray. "
    "Sauce glistening on the skin. Warm low amber light, dark charcoal background, "
    "restaurant food photography, slightly underexposed. No hands, no people, no text."
)

DESSERTS = (
    "Photorealistic Midtown Smokehouse dessert platter. "
    "Includes slices of carrot cake, strawberry cake, and a brownie. "
    "Also features a fruit cup with fresh berries. "
    "Served on a dark wood board with warm low amber light, dark charcoal background, "
    "restaurant food photography, slightly underexposed. No hands, no people, no text."
)


def post_json(path, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        HOST + path, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def flux_workflow(prompt, width, height, seed, prefix):
    return {
        "prompt": {
            "1": {
                "class_type": "UNETLoader",
                "inputs": {
                    "unet_name": "flux1-dev.safetensors",
                    "weight_dtype": "default",
                },
            },
            "2": {
                "class_type": "DualCLIPLoader",
                "inputs": {
                    "clip_name1": "t5xxl_fp8_e4m3fn.safetensors",
                    "clip_name2": "clip_l.safetensors",
                    "type": "flux",
                },
            },
            "3": {
                "class_type": "VAELoader",
                "inputs": {"vae_name": "ae.safetensors"},
            },
            "4": {
                "class_type": "CLIPTextEncodeFlux",
                "inputs": {
                    "clip": ["2", 0],
                    "clip_l": prompt[:220],
                    "t5xxl": prompt,
                    "guidance": 3.5,
                },
            },
            "5": {
                "class_type": "CLIPTextEncodeFlux",
                "inputs": {
                    "clip": ["2", 0],
                    "clip_l": "",
                    "t5xxl": "",
                    "guidance": 3.5,
                },
            },
            "6": {
                "class_type": "EmptySD3LatentImage",
                "inputs": {"width": width, "height": height, "batch_size": 1},
            },
            "7": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["1", 0],
                    "seed": seed,
                    "steps": 20,
                    "cfg": 1.0,
                    "sampler_name": "euler",
                    "scheduler": "simple",
                    "positive": ["4", 0],
                    "negative": ["5", 0],
                    "latent_image": ["6", 0],
                    "denoise": 1.0,
                },
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["7", 0], "vae": ["3", 0]},
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {"images": ["8", 0], "filename_prefix": prefix},
            },
        }
    }


def run(prompt, width, height, seed, prefix):
    queued = post_json("/prompt", flux_workflow(prompt, width, height, seed, prefix))
    prompt_id = queued["prompt_id"]
    print(f"queued {prefix} {prompt_id}", flush=True)
    deadline = time.time() + 900
    while time.time() < deadline:
        with urllib.request.urlopen(HOST + "/history/" + prompt_id, timeout=30) as resp:
            hist = json.load(resp)
        if prompt_id in hist:
            outputs = hist[prompt_id].get("outputs", {})
            for node in outputs.values():
                for image in node.get("images", []):
                    name = image["filename"]
                    q = urllib.parse.urlencode(
                        {
                            "filename": name,
                            "subfolder": image.get("subfolder", ""),
                            "type": image.get("type", "output"),
                        }
                    )
                    dest = OUT / f"{prefix}.png"
                    urllib.request.urlretrieve(HOST + "/view?" + q, dest)
                    print(f"saved {dest}", flush=True)
                    return dest
            raise SystemExit(f"no image in history for {prefix}: {outputs}")
        time.sleep(3)
    raise SystemExit(f"timeout waiting for {prefix}")


if __name__ == "__main__":
    import urllib.parse

    import sys

    only = sys.argv[1:] or ["brisket", "texture"]
    if "brisket" in only:
        run(BRISKET, 1408, 960, 20261022, "brisket_hero")
    if "texture" in only:
        run(TEXTURE, 1024, 1344, 20261021, "charcoal_texture")
    if "combos" in only:
        run(COMBOS, 800, 400, 20261024, "combos-hero")
    if "sandwiches" in only:
        run(SANDWICHES, 800, 400, 20261024, "sandwiches-hero")
    if "wings" in only:
        run(WINGS, 800, 400, 20261024, "wings-hero")
    if "desserts" in only:
        run(DESSERTS, 800, 400, 20261024, "desserts-hero")
