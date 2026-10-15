"""Which bank resource holds the tiles of a screen region?
    python -X utf8 tools/gfx/whose.py DUMP_PREFIX [--obj] [--bg N] [--rect x0,y0,x1,y1]
Indexes every 4bpp tile of every resource (raw, unflipped) and reports matches for the OBJ sprites (or BG n
tilemap) that cover the rect.
"""
import os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import res, screen  # noqa: E402


def index(rom):
    idx = collections.defaultdict(set)
    for bank, recs in res.DIRS.items():
        for i in range(len(recs)):
            d, info = res.decode(rom, bank, i)
            for o in range(0, len(d), 32):
                t = d[o:o + 32]
                if any(t):
                    idx[t].add((bank, i))
    return idx


def main():
    rom = open(os.path.join(ROOT, "work", "orig.gba"), "rb").read()
    d = screen.Dump(sys.argv[1])
    rect = (0, 0, 240, 160)
    if "--rect" in sys.argv:
        rect = tuple(int(v) for v in sys.argv[sys.argv.index("--rect") + 1].split(","))
    ix = index(rom)
    hits = collections.Counter()
    for o in d.objs():
        if o["x"] + o["w"] <= rect[0] or o["x"] >= rect[2] or o["y"] + o["h"] <= rect[1] or o["y"] >= rect[3]:
            continue
        for ty in range(o["h"] // 8):
            for tx in range(o["w"] // 8):
                t = o["tile"] + ty * 32 + tx
                b = d.vram[0x10000 + t * 32:0x10000 + t * 32 + 32]
                for k in ix.get(b, ()):
                    hits[(o["i"], k)] += 1
    by = collections.defaultdict(list)
    for (oi, k), n in hits.items():
        by[k].append(oi)
    for k, ois in sorted(by.items(), key=lambda x: -len(x[1])):
        print(k, "sprites", sorted(ois))


if __name__ == "__main__":
    main()
