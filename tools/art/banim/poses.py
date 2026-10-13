"""Cut battle poses out of generated pixel-art sheets.

    python3 tools/art/banim/poses.py [anim ...]

poses/<anim>/sources.json lists, per pose: the generated sheet (kept outside the
repo, see GEN_DIR), the crop box, the target height in game pixels and an
optional mirror flag. The sheets are original art made with a free
text-to-image model; the indexed results are written to poses/<anim>/<pose>.png
and committed, so the build never needs the generator.

The palette for each animation is poses/<anim>/palette.json: 15 RGB colours
(indices 1-15), index 1 being the outline.
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from from_pixelart import convert  # noqa: E402

GEN_DIR = os.environ.get("AOT_GEN_DIR", "/mnt/project-files/art-sources")


def load_palette(anim):
    with open(os.path.join(HERE, "poses", anim, "palette.json")) as f:
        p = json.load(f)
    return [(0, 0, 0)] + [tuple(c) for c in p["colors"]], p.get("keep_edge", [])


def save_indexed(a, palette, path):
    im = Image.fromarray(a.astype(np.uint8), "P")
    flat = []
    for c in palette:
        flat += list(c)
    im.putpalette(flat + [0] * (768 - len(flat)))
    im.save(path, transparency=0)


def load_pose(anim, name):
    return np.array(Image.open(os.path.join(HERE, "poses", anim, name + ".png")))


def build(anim):
    d = os.path.join(HERE, "poses", anim)
    with open(os.path.join(d, "sources.json")) as f:
        src = json.load(f)
    pal, keep = load_palette(anim)
    for name, s in src.items():
        a = convert(os.path.join(GEN_DIR, s["sheet"]), tuple(s["box"]), s["height"], pal,
                    keep_edge=tuple(keep), tol=s.get("tol", 48), drop_shadow=s.get("drop_shadow", 0.12))
        if s.get("mirror"):
            a = a[:, ::-1]
        for fix in s.get("erase", []):  # [x0, y0, x1, y1] in pose pixels: stray bits of a neighbour
            a[fix[1]:fix[3], fix[0]:fix[2]] = 0
        save_indexed(a, pal, os.path.join(d, name + ".png"))
        print(f"{anim}/{name}: {a.shape[1]}x{a.shape[0]}")


if __name__ == "__main__":
    for anim in sys.argv[1:] or sorted(os.listdir(os.path.join(HERE, "poses"))):
        build(anim)
