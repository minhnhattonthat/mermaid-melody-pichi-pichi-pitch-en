"""Decode every bank resource and write greyscale tile sheets for the graphics survey.
    python -X utf8 tools/resdump.py ROM OUTDIR [--dirs work/res/dirs_all.json] [--cols 32]
Writes OUTDIR/<bank>_<idx>.bin and one labelled montage per bank (OUTDIR/<bank>_sheet_<n>.png).
"""
import json, os, sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
import banks  # noqa: E402


def tiles4(data, cols=32, mode="row"):
    n = len(data) // 32
    rows = (n + cols - 1) // cols
    img = Image.new("L", (cols * 8, rows * 8))
    px = img.load()
    for t in range(n):
        tx, ty = (t % cols, t // cols)
        for y in range(8):
            for x in range(8):
                b = data[t * 32 + y * 4 + x // 2]
                v = (b >> 4) if x & 1 else (b & 15)
                px[tx * 8 + x, ty * 8 + y] = v * 17
    return img


def main():
    rom = open(sys.argv[1], "rb").read()
    out = sys.argv[2]
    dirs = json.load(open(sys.argv[sys.argv.index("--dirs") + 1] if "--dirs" in sys.argv else "work/res/dirs_all.json"))
    cols = int(sys.argv[sys.argv.index("--cols") + 1]) if "--cols" in sys.argv else 32
    os.makedirs(out, exist_ok=True)
    for base, recs in dirs.items():
        imgs = []
        for i, (o, info) in enumerate(recs):
            d, _ = banks.decode_res(rom, int(o, 16), info)
            open(os.path.join(out, f"{base}_{i:03d}.bin"), "wb").write(d)
            imgs.append((i, info, tiles4(d, cols)))
        # montage pages of ~1400 px height
        page, y, n = [], 0, 0
        def flush(page, n):
            if not page: return
            h = sum(im.height + 12 for _, _, im in page)
            m = Image.new("L", (cols * 8, h), 40)
            dr = ImageDraw.Draw(m); yy = 0
            for i, info, im in page:
                dr.text((2, yy), f"{base} #{i} info={info:#x} {im.height // 8}r", fill=255)
                m.paste(im, (0, yy + 12)); yy += im.height + 12
            m.save(os.path.join(out, f"{base}_sheet_{n}.png"))
        for it in imgs:
            if y + it[2].height > 1400 and page:
                flush(page, n); n += 1; page, y = [], 0
            page.append(it); y += it[2].height + 12
        flush(page, n)


if __name__ == "__main__":
    main()
