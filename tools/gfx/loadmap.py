"""Turn a gfxload.lua log into resource loads: frame, bank, index, chunk, dest(s).
    python -X utf8 tools/gfx/loadmap.py LOG [--from F] [--to F]
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
import banks  # noqa: E402


def chunk_index(rom):
    dirs = json.load(open(os.path.join(HERE, "dirs.json")))
    m = {}
    for base, recs in dirs.items():
        for i, (o, info) in enumerate(recs):
            off = int(o, 16)
            for c in range((info >> 4) + 1):
                m.setdefault(off, (base, i, c, info))
                _, off = banks.mmcomp.decompress(rom, off, banks.chunk_size(info))
    return m


def main():
    rom = open(os.path.join(ROOT, "work", "orig.gba"), "rb").read()
    ci = chunk_index(rom)
    lo = int(sys.argv[sys.argv.index("--from") + 1]) if "--from" in sys.argv else 0
    hi = int(sys.argv[sys.argv.index("--to") + 1]) if "--to" in sys.argv else 1 << 30
    cur = None
    out = []
    for line in open(sys.argv[1]):
        p = line.split()
        if len(p) < 3 or not p[0][1:].isdigit():
            continue
        f = int(p[0][1:])
        if not lo <= f <= hi:
            continue
        kv = dict(x.split("=") for x in p[2:])
        if p[1] == "DEC":
            src = int(kv["src"], 16) & 0x1FFFFFF
            cur = [f, ci.get(src, ("?", src, 0, 0)), []]
            out.append(cur)
        elif p[1] == "DMA" and cur:
            cur[2].append((kv["dad"], kv["cnt"]))
    seen = set()
    for f, (b, i, c, info), d in out:
        key = (b, i, c, tuple(d))
        if key in seen:
            continue
        seen.add(key)
        dd = " ".join(f"{a}x{n}" for a, n in d[:4]) + (" .." if len(d) > 4 else "")
        print(f"f{f} {b} #{i} c{c} info={info:#x} -> {dd}")


if __name__ == "__main__":
    main()
