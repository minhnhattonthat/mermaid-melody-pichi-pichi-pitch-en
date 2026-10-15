"""Bank resource <-> editable 4bpp index sheet.

Layouts (decided by the info byte, see docs/re/README.md):
  info & 8 (OBJ/strip): chunk c slice s (0x200 B = 16 tiles); info&1: row (c//2)*4+s, half c%2;
                        else row (c%8)*4+s, half c//8. Sheet 32 tiles wide = 2D OBJ VRAM order (checked against
                        gfxload.lua DMA logs for #27 #28 #35 #72 #209).
  else (linear):        tiles in order, 32 tiles per sheet row.
4bpp only (8bpp resources are flagged and handled separately).
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
import banks, mmcomp  # noqa: E402

DIRS = json.load(open(os.path.join(HERE, "dirs.json")))  # bank -> [[ptr, info]] (copy of work/scan_dirs.py output)


def rec(bank, idx):
    o, info = DIRS[bank][idx]
    return int(o, 16), info


def decode(rom, bank, idx):
    off, info = rec(bank, idx)
    return banks.decode_res(rom, off, info)[0], info


def tiles_to_idx(tb):
    """tile bytes (32 B 4bpp) -> 8x8 uint8 index array"""
    a = np.frombuffer(tb, np.uint8)
    out = np.empty(64, np.uint8)
    out[0::2] = a & 15
    out[1::2] = a >> 4
    return out.reshape(8, 8)


def idx_to_tile(a):
    a = a.reshape(64).astype(np.uint8)
    return bytes((a[0::2] | (a[1::2] << 4)).tolist())


def slots(n_bytes, info):
    """List of (byte offset in resource, tile x, tile y) for every tile."""
    nt = n_bytes // 32
    res = []
    if info & 8:
        N = (info >> 4) + 1
        csz = banks.chunk_size(info)
        for t in range(nt):
            o = t * 32
            c, r = divmod(o, csz)
            s, k = divmod(r, 0x200)
            if info & 1:   # chunks alternate left/right half, 4 tile rows per pair
                row, half = (c // 2) * 4 + s, c % 2
            else:          # 8 chunks down the left half, then the right half
                row, half = (c % 8) * 4 + s, c // 8
            res.append((o, half * 16 + k // 32, row))
    else:
        for t in range(nt):
            res.append((t * 32, t % 32, t // 32))
    return res


def to_sheet(data, info):
    sl = slots(len(data), info)
    w = 32
    h = max(y for _, _, y in sl) + 1
    img = np.zeros((h * 8, w * 8), np.uint8)
    for o, x, y in sl:
        img[y * 8:y * 8 + 8, x * 8:x * 8 + 8] = tiles_to_idx(data[o:o + 32])
    return img


def from_sheet(img, info, n_bytes):
    out = bytearray(n_bytes)
    for o, x, y in slots(n_bytes, info):
        out[o:o + 32] = idx_to_tile(img[y * 8:y * 8 + 8, x * 8:x * 8 + 8])
    return bytes(out)


def pal16(palbin, n):
    """16 RGB tuples from a palette RAM dump (n = 0..31; 16+ = OBJ)."""
    import struct
    cols = []
    for i in range(16):
        v = struct.unpack_from("<H", palbin, (n * 16 + i) * 2)[0]
        cols.append(((v & 31) << 3, ((v >> 5) & 31) << 3, ((v >> 10) & 31) << 3))
    return cols


def save_png(img, path, pal=None, zoom=1):
    from PIL import Image
    im = Image.fromarray(img, "P")
    flat = []
    for c in (pal or [(i * 17,) * 3 for i in range(16)]):
        flat += list(c)
    im.putpalette(flat + [0] * (768 - len(flat)))
    if zoom > 1:
        im = im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)
    im.save(path)


def _selftest():
    rom = open(os.path.join(ROOT, "work", "orig.gba"), "rb").read()
    for bank, recs in DIRS.items():
        for i, (o, info) in enumerate(recs):
            d, _ = decode(rom, bank, i)
            assert from_sheet(to_sheet(d, info), info, len(d)) == d
    print("res selftest ok")


if __name__ == "__main__":
    _selftest()
