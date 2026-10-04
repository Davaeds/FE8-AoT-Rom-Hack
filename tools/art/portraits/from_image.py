"""Turn a generated character image into a 16-colour FE8 portrait sheet.

    python3 tools/art/portraits/from_image.py [name ...] [--preview DIR]

Sources live in tools/art/portraits/generated/<name>.png: anime-style busts on
a flat light background, made with a text-to-image model (original art, not
taken from the show or its games). Each entry in SOURCES says where to crop
and where the eyes and mouth are, so the talking and blinking frames can be
painted over the base portrait.
"""
import os
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pkit import BG, MOUTHS, gba  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "AoT", "Graphics", "Portraits")
SRC = os.path.join(HERE, "generated")

# crop: (x0, y0, width) in the source; the box is 96:80 and may run off the image.
# Feature positions below are in portrait pixels (96x80):
# eyes: two (x0, y0, x1, y1) boxes; mouth: (cx, cy, half width);
# skin: a cheek pixel to sample for the eyelids; mini: (cx, cy, size) of the minimug.
SOURCES = {}


def load_sources():
    import json
    with open(os.path.join(SRC, "sources.json")) as f:
        SOURCES.update(json.load(f))


def background_mask(rgb, tol=26.0):
    """Flood fill from the border through pixels close to their neighbour."""
    h, w, _ = rgb.shape
    a = rgb.astype(np.int32)
    bg = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        q.append((0, x)); q.append((h - 1, x))
    for y in range(h):
        q.append((y, 0)); q.append((y, w - 1))
    for y, x in q:
        bg[y, x] = True
    ref = np.median(np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]), axis=0)
    while q:
        y, x = q.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < h and 0 <= nx < w and not bg[ny, nx]:
                d1 = np.abs(a[ny, nx] - a[y, x]).sum()
                d2 = np.abs(a[ny, nx] - ref).sum()
                c = a[ny, nx]
                if d1 < tol and d2 < tol * 4 and c[1] - c[0] > 6:
                    bg[ny, nx] = True
                    q.append((ny, nx))
    # enclosed pockets of background (between an arm and the body, say)
    c = a.reshape(-1, 3)
    pocket = (c[:, 1] - c[:, 0] > 8) & (c[:, 1] - c[:, 2] > 12) & (c.sum(1) > 450)
    return bg | pocket.reshape(h, w)


def crop_rgba(img, box, size):
    """Crop box (x0, y0, w, h) from img (padding with transparency) and resize."""
    x0, y0, w, h = box
    canvas = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
    canvas.paste(img, (int(-x0), int(-y0)))
    return canvas.resize(size, Image.LANCZOS)


def kmeans(px, k, iters=20, seed=1):
    """Plain k-means; saturated pixels count extra so small coloured details (eyes) keep a colour."""
    rng = np.random.default_rng(seed)
    # start from luminance quantiles so dark outlines always get a colour
    lum = px @ np.array([0.3, 0.59, 0.11])
    order = np.argsort(lum)
    c = px[order[np.linspace(0, len(px) - 1, k).astype(int)]].astype(float)
    for _ in range(iters):
        d = ((px[:, None, :] - c[None]) ** 2).sum(-1)
        lab = d.argmin(1)
        for i in range(k):
            m = lab == i
            c[i] = px[m].mean(0) if m.any() else px[rng.integers(len(px))]
    return c


def nearest(pal, rgb):
    return int((((pal - np.array(rgb)) ** 2).sum(1)).argmin())


def convert(name, cfg):
    src = Image.open(os.path.join(SRC, name + ".png")).convert("RGB")
    # background removal at a working size, then upscale the mask
    work = src.resize((src.width // 4, src.height // 4), Image.BILINEAR)
    mask = background_mask(np.asarray(work))
    mask = Image.fromarray((~mask * 255).astype(np.uint8)).resize(src.size, Image.BILINEAR)
    mask = mask.filter(ImageFilter.MinFilter(3))
    rgba = src.copy()
    rgba.putalpha(mask)

    x0, y0, w = cfg["crop"]
    h = w * 80 / 96
    big = crop_rgba(rgba, (x0, y0, w, h), (384, 320))
    big = Image.fromarray(np.asarray(big)).filter(ImageFilter.UnsharpMask(2, 80, 2))
    small = np.asarray(big.resize((96, 80), Image.LANCZOS)).astype(float)
    alpha = np.asarray(big.split()[3].resize((96, 80), Image.BILINEAR)) >= 120
    rgb = small[..., :3]

    # mini mug from the same crop
    mcx, mcy, ms = cfg["mini"]
    sx = w / 96
    mbox = (x0 + (mcx - ms / 2) * sx, y0 + (mcy - ms / 2) * sx, ms * sx, ms * sx)
    mini = np.asarray(crop_rgba(rgba, mbox, (128, 128)).resize((32, 32), Image.LANCZOS)).astype(float)
    malpha = mini[..., 3] >= 120

    # 15 colours shared by the portrait and the minimug
    px = np.concatenate([rgb[alpha], mini[..., :3][malpha]])
    keep = [np.array(c, float) for c in cfg.get("keep", [])]
    pal = kmeans(px, 15 - len(keep))
    if keep:
        pal = np.concatenate([pal, np.array(keep)])
    pal = np.array([gba(tuple(int(round(v)) for v in c)) for c in pal], float)
    dark = int((pal @ np.array([0.3, 0.59, 0.11])).argmin())

    def index(img, a):
        out = np.zeros(a.shape, np.uint8)
        d = ((img[..., None, :] - pal[None, None]) ** 2).sum(-1)
        out[a] = d.argmin(-1)[a] + 1
        # crisp outline where the figure meets the background (not along the bottom edge)
        edge = a & ~(np.pad(a, 1, constant_values=True)[:-2, 1:-1] & np.pad(a, 1, constant_values=True)[2:, 1:-1]
                     & np.pad(a, 1, constant_values=True)[1:-1, :-2] & np.pad(a, 1, constant_values=True)[1:-1, 2:])
        out[edge] = dark + 1
        return out

    base = index(rgb, alpha)
    mini_i = index(mini[..., :3], malpha)

    skin = base[cfg["skin"][1], cfg["skin"][0]]
    mouth_col = nearest(pal, cfg.get("mouth_rgb", (96, 32, 36))) + 1
    teeth_col = nearest(pal, (240, 236, 226)) + 1

    def with_mouth(state):
        img = base.copy()
        if cfg.get("static"):
            return img
        cx, cy, hw = cfg["mouth"]
        open_h = {"open": 3, "half": 2, "closed_talk": 1, "smile_open": 3, "smile_half": 2, "smile_closed": 0}[state]
        smile = state.startswith("smile")
        if state == "smile_closed":
            for dx in (-hw, hw):
                img[cy - 1, cx + dx] = dark + 1
            return img
        for dx in range(-hw, hw + 1):
            lift = 1 if smile and abs(dx) == hw else 0
            rows = open_h - (1 if abs(dx) == hw and open_h > 1 else 0)
            for dy in range(rows):
                img[cy + dy - lift, cx + dx] = mouth_col
            img[cy - lift - 1 if open_h else cy, cx + dx] = dark + 1
        if open_h >= 3:
            for dx in range(-hw + 1, hw):
                img[cy, cx + dx] = teeth_col
        return img

    def with_eyes(state):
        img = base.copy()
        if cfg.get("static"):
            return img
        for (ex0, ey0, ex1, ey1) in cfg["eyes"]:
            mid = (ey0 + ey1) // 2
            cut = mid if state == "half" else ey1
            img[ey0:cut + 1, ex0:ex1 + 1] = skin
            line_y = mid if state == "half" else ey1 - 1
            img[line_y, ex0:ex1 + 1] = dark + 1
        return img

    mt = cfg.get("mouth_tile") or (max(0, round((cfg["mouth"][0] - 16) / 8)), max(0, round((cfg["mouth"][1] - 8) / 8)))
    et = cfg.get("eye_tile") or (max(0, round((min(e[0] for e in cfg["eyes"]) + max(e[2] for e in cfg["eyes"])) / 2 - 16) // 8),
                                 max(0, round((cfg["eyes"][0][1] + cfg["eyes"][0][3]) / 2 - 8) // 8))
    sheet = np.zeros((112, 128), np.uint8)
    sheet[0:80, 0:96] = base
    mx, my = mt[0] * 8, mt[1] * 8
    for n, m in enumerate(MOUTHS):
        fx, fy = (n % 3) * 32, 80 + (n // 3) * 16
        sheet[fy:fy + 16, fx:fx + 32] = with_mouth(m)[my:my + 16, mx:mx + 32]
    ex, ey = et[0] * 8, et[1] * 8
    sheet[48:64, 96:128] = with_eyes("half")[ey:ey + 16, ex:ex + 32]
    sheet[64:80, 96:128] = with_eyes("closed")[ey:ey + 16, ex:ex + 32]
    sheet[16:48, 96:128] = mini_i

    img = Image.fromarray(sheet, "P")
    flat = list(gba(BG))
    for c in pal:
        flat += [int(v) for v in c]
    flat += [0] * (768 - len(flat))
    img.putpalette(flat)
    return img, mt, et


def main(argv):
    from pkit import preview
    load_sources()
    prev = None
    if "--preview" in argv:
        i = argv.index("--preview")
        prev = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    for name in argv or list(SOURCES):
        cfg = SOURCES[name]
        img, mt, et = convert(name, cfg)
        img.save(os.path.join(OUT, cfg["out"] + ".png"))
        if prev:
            preview(img, os.path.join(prev, name + ".png"))
        print(f"wrote {cfg['out']}.png  mouth tile {mt}  eye tile {et}")


if __name__ == "__main__":
    main(sys.argv[1:])
