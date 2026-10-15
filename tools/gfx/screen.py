"""Screen-space view of a PPU dump (L.dump_ppu prefix: .vram.bin .pal.bin .oam.bin .io.bin).

obj_layer(d) -> (idx, pal, src): 160x240 arrays; idx -1 = no sprite pixel; src[y,x] = (sx, sy) pixel in the
OBJ VRAM sheet (2D mapping, 256x256 px, 4bpp) or (-1,-1). Topmost sprite = lowest OAM index.
bg_layer(d, n) -> (idx, pal, src) for text BG n; src = (byte offset of the tile in VRAM, px, py).
rgb(...) renders for viewing.
"""
import struct
import numpy as np

SIZES = {(0, 0): (8, 8), (0, 1): (16, 16), (0, 2): (32, 32), (0, 3): (64, 64), (1, 0): (16, 8), (1, 1): (32, 8),
         (1, 2): (32, 16), (1, 3): (64, 32), (2, 0): (8, 16), (2, 1): (8, 32), (2, 2): (16, 32), (2, 3): (32, 64)}


class Dump:
    def __init__(self, prefix):
        self.vram = open(prefix + ".vram.bin", "rb").read()
        self.pal = open(prefix + ".pal.bin", "rb").read()
        self.oam = open(prefix + ".oam.bin", "rb").read()
        self.io = open(prefix + ".io.bin", "rb").read()

    def color(self, bank, i):
        v = struct.unpack_from("<H", self.pal, (bank * 16 + i) * 2)[0]
        return ((v & 31) << 3, ((v >> 5) & 31) << 3, ((v >> 10) & 31) << 3)

    def objs(self):
        out = []
        for i in range(128):
            a0, a1, a2 = struct.unpack_from("<HHH", self.oam, i * 8)
            if (a0 >> 8) & 3 == 2 or (a0 >> 14) == 3:
                continue
            W, H = SIZES[(a0 >> 14, a1 >> 14)]
            y, x = a0 & 255, a1 & 511
            if y >= 160: y -= 256
            if x >= 256: x -= 512
            out.append(dict(i=i, x=x, y=y, w=W, h=H, tile=a2 & 1023, pal=a2 >> 12, bpp8=bool(a0 & 0x2000),
                            hf=bool(a1 & 0x1000) and not a0 & 0x100, vf=bool(a1 & 0x2000) and not a0 & 0x100,
                            affine=bool(a0 & 0x100), prio=(a2 >> 10) & 3))
        return out


def sheet_px(vram, sx, sy):
    t = (sy // 8) * 32 + sx // 8
    b = vram[0x10000 + t * 32 + (sy % 8) * 4 + (sx % 8) // 2]
    return (b >> 4) if sx & 1 else (b & 15)


def obj_layer(d, area=None):
    """area = (x0, y0, x1, y1) in sheet pixels: only sprites whose tiles start inside it are drawn."""
    idx = np.full((160, 240), -1, np.int16)
    pal = np.zeros((160, 240), np.int16)
    src = np.full((160, 240, 2), -1, np.int16)
    for o in reversed(d.objs()):  # draw back to front so OAM 0 ends on top
        if o["bpp8"]:
            continue
        if area:
            tx, ty = (o["tile"] % 32) * 8, (o["tile"] // 32) * 8
            if not (area[0] <= tx < area[2] and area[1] <= ty < area[3]):
                continue
        tx0, ty0 = o["tile"] % 32, o["tile"] // 32
        for yy in range(o["h"]):
            for xx in range(o["w"]):
                X, Y = o["x"] + xx, o["y"] + yy
                if not (0 <= X < 240 and 0 <= Y < 160):
                    continue
                lx = o["w"] - 1 - xx if o["hf"] else xx
                ly = o["h"] - 1 - yy if o["vf"] else yy
                sx, sy = tx0 * 8 + lx, ty0 * 8 + ly
                if sy >= 256 or sx >= 256:
                    continue
                v = sheet_px(d.vram, sx, sy)
                if v or idx[Y, X] < 0:
                    idx[Y, X] = v
                    pal[Y, X] = 16 + o["pal"]
                    src[Y, X] = (sx, sy)
    return idx, pal, src


def edit_obj(dump, sheet, origin, rect, draw, view=None):
    """Screen-space edit of an OBJ resource sheet.
    sheet: resource index sheet (res.to_sheet); origin: (tile x, tile y) of the sheet's top-left in OBJ VRAM;
    rect: (x0, y0, x1, y1) screen area; draw(canvas, covered) edits canvas in place (uint8 indices, -1 = no sprite).
    Pixels are written back only where a sprite of this resource covers the screen."""
    ox, oy = origin[0] * 8, origin[1] * 8
    H, W = sheet.shape
    idx, pal, src = obj_layer(dump, (ox, oy, ox + W, oy + H))
    x0, y0, x1, y1 = rect
    cov = np.zeros((y1 - y0, x1 - x0), bool)
    canvas = np.zeros((y1 - y0, x1 - x0), np.int16) - 1
    for y in range(y0, y1):
        for x in range(x0, x1):
            sx, sy = src[y, x]
            if sx >= 0 and 0 <= sx - ox < W and 0 <= sy - oy < H:
                cov[y - y0, x - x0] = True
                canvas[y - y0, x - x0] = sheet[sy - oy, sx - ox]
    if view:
        from PIL import Image
        im = Image.new("RGB", (x1 - x0, y1 - y0), (255, 0, 255))
        for y in range(y1 - y0):
            for x in range(x1 - x0):
                if cov[y, x]:
                    im.putpixel((x, y), dump.color(pal[y + y0, x + x0], canvas[y, x]))
        im.resize((im.width * 4, im.height * 4), Image.NEAREST).save(view)
    draw(canvas, cov)
    for y in range(y0, y1):
        for x in range(x0, x1):
            if cov[y - y0, x - x0]:
                sx, sy = src[y, x]
                sheet[sy - oy, sx - ox] = canvas[y - y0, x - x0]
    return sheet


def rgb(d, idx, pal, bg=(255, 0, 255)):
    from PIL import Image
    im = Image.new("RGB", (240, 160), bg)
    px = im.load()
    for y in range(160):
        for x in range(240):
            if idx[y, x] > 0:
                px[x, y] = d.color(pal[y, x], idx[y, x])
    return im
