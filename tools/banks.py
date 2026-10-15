"""Find graphics banks: 5-byte records {u32 ptr (unaligned LE), u8 info} referenced from code literal pools.

info: high nibble = chunks-1; bit2 = 0x1000-byte chunks (else 0x800) and literal add applies; bit3 = dst addressing.
    python -X utf8 tools/banks.py ROM [--json OUT]
"""
import json, struct, sys

sys.path.insert(0, __import__("os").path.dirname(__file__))
import mmcomp  # noqa: E402


def scan_bank(rom, base):
    """Return list of (ptr_off, info) records if `base` looks like a bank, else None."""
    recs, p, lo = [], base, None
    while p + 5 <= len(rom):
        if lo is not None and p >= lo:
            break
        v = struct.unpack_from("<I", rom, p)[0]
        if not (0x08000000 <= v < 0x09000000):
            break
        off = v & 0x1FFFFFF
        if off < base:
            break
        recs.append((off, rom[p + 4]))
        lo = off if lo is None else min(lo, off)
        p += 5
    return recs


def chunk_size(info):
    return 0x1000 if info & 4 else 0x800


def decode_res(rom, off, info):
    n = (info >> 4) + 1
    out = bytearray()
    for _ in range(n):
        d, off = mmcomp.decompress(rom, off, chunk_size(info))
        out += d
    return bytes(out), off


def literal_pointers(rom, code_end=0x80000):
    s = set()
    for p in range(0, code_end, 4):
        v = struct.unpack_from("<I", rom, p)[0]
        if 0x08080000 <= v < 0x09000000:
            s.add(v & 0x1FFFFFF)
    return s


def find_banks(rom):
    banks = {}
    for base in sorted(literal_pointers(rom)):
        recs = scan_bank(rom, base)
        if len(recs) < 1:
            continue
        # validate: data starts right after the directory, and every record decodes
        first = min(o for o, _ in recs)
        if first != base + 5 * len(recs):
            continue
        try:
            for o, i in recs:
                decode_res(rom, o, i)
        except Exception:
            continue
        banks[base] = recs
    return banks


if __name__ == "__main__":
    rom = open(sys.argv[1], "rb").read()
    b = find_banks(rom)
    tot = 0
    for base, recs in b.items():
        tot += len(recs)
        print(f"{base:#08x} {len(recs):4d} recs  infos={sorted(set(i for _, i in recs))}")
    print("banks", len(b), "resources", tot)
    if "--json" in sys.argv:
        json.dump({f"{k:#08x}": [[f"{o:#08x}", i] for o, i in v] for k, v in b.items()},
                  open(sys.argv[sys.argv.index("--json") + 1], "w", newline="\n"), indent=1)
