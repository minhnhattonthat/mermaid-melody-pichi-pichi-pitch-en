"""Text bank dump / encode helpers.
    python -X utf8 tools/text.py dump [--force]   -> script/text.json (never clobbers without --force)
    python -X utf8 tools/text.py show             -> print every string (id, table ids, jp)
Markup in jp/en: glyph chars; controls as [F6 05 ...] hex groups; [FE] newline; trailing [FF] implicit.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import textcodec as T  # noqa: E402

ROM = os.path.join(ROOT, "rom", "Mermaid Melody - Pichi Pichi Pitch (Japan).gba")
SCRIPT = os.path.join(ROOT, "script", "text.json")


def load_tbl(path=os.path.join(ROOT, "tbl", "jp.tbl")):
    m = {}
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        k, v = line.split("=", 1)
        m[int(k, 16)] = v
    return m


def decode(rom, p, tbl):
    """Return (markup, raw bytes, end) for the string at file offset p."""
    s, start = [], p
    for kind, v, raw in T.tokens(rom, p):
        p += len(raw)
        if kind == "g":
            s.append(tbl.get(v, "{%03X}" % v))
        elif v == 0xFF:
            break
        elif v == 0xFE:
            s.append("\n")
        else:
            s.append("[" + " ".join("%02X" % b for b in raw) + "]")
    return "".join(s), rom[start:p], p


def strings(rom):
    """Sequential walk of the whole bank: list of (offset, raw, end)."""
    offs = T.offsets(rom)
    out, p = [], T.BASE
    while p < T.TEXT_END:
        s = p
        for _, _, raw in T.tokens(rom, p):
            p += len(raw)
        out.append((s - T.BASE, p - T.BASE))
    ids = {}
    for i, o in enumerate(offs):
        ids.setdefault(o, []).append(i)
    return out, ids


def dump(force=False):
    if os.path.exists(SCRIPT) and not force:
        sys.exit("script/text.json exists; use --force (it would clobber English)")
    rom = open(ROM, "rb").read()
    tbl = load_tbl()
    segs, ids = strings(rom)
    entries = []
    for s, e in segs:
        jp, raw, _ = decode(rom, T.BASE + s, tbl)
        entries.append({"id": "t%04X" % s, "ids": ids.get(s, []), "jp": jp, "en": "", "notes": ""})
    os.makedirs(os.path.dirname(SCRIPT), exist_ok=True)
    with open(SCRIPT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(entries, f, ensure_ascii=False, indent=1)
    print(len(entries), "strings ->", SCRIPT)


if __name__ == "__main__":
    if sys.argv[1] == "dump":
        dump("--force" in sys.argv)
    elif sys.argv[1] == "show":
        rom = open(ROM, "rb").read(); tbl = load_tbl()
        segs, ids = strings(rom)
        for s, e in segs:
            jp, _, _ = decode(rom, T.BASE + s, tbl)
            print("t%04X" % s, ids.get(s, []), jp.replace("\n", "/"))
