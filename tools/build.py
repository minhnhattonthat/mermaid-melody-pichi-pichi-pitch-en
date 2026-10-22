"""One entry point.
    python -X utf8 tools/build.py build [--lang en] [--marker] [--out PATH]   -> build/mmppp_<lang>.gba (32 MiB)
    python -X utf8 tools/build.py check                                       -> identity + text lint (pre-commit)
Free space after expansion to 32 MiB:
  0x1000000-0x13FFFFF  text / font / code   (tools/textins.py, asm/)
  0x1400000-0x1FFFFFF  graphics             (tools/gfx/apply.py: apply(rom, Alloc))
"""
import hashlib, importlib, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
ORIG = os.path.join(ROOT, "rom", "Mermaid Melody - Pichi Pichi Pitch (Japan).gba")
SIZE = 0x2000000


class Alloc:
    """Bump allocator over a free ROM window; raises when it would overflow."""
    def __init__(self, rom, lo, hi, align=4):
        self.rom, self.p, self.hi, self.align = rom, lo, hi, align

    def put(self, data, align=None):
        a = align or self.align
        self.p = (self.p + a - 1) & ~(a - 1)
        if self.p + len(data) > self.hi:
            raise RuntimeError(f"free space overflow at {self.p:#x} (+{len(data):#x} > {self.hi:#x})")
        off = self.p
        self.rom[off:off + len(data)] = data
        self.p += len(data)
        return off


def load_orig():
    import check_rom
    check_rom.check()
    return open(ORIG, "rb").read()


def build(lang="en", marker=False, expand=True):
    rom = bytearray(load_orig())
    if expand:
        rom += b"\xff" * (SIZE - len(rom))
    import textins
    textins.apply(rom, lang=lang, marker=marker, alloc=Alloc(rom, 0x1000000, 0x1400000) if expand else None)
    if expand and os.path.exists(os.path.join(HERE, "gfx", "apply.py")):
        gfx = importlib.import_module("gfx.apply")
        gfx.apply(rom, Alloc(rom, 0x1400000, SIZE))
    return rom


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    lang = sys.argv[sys.argv.index("--lang") + 1] if "--lang" in sys.argv else "en"
    if cmd == "build":
        marker = "--marker" in sys.argv
        out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else \
            os.path.join(ROOT, "build", f"mmppp_{lang}{'_marker' if marker else ''}.gba")
        rom = build(lang, marker)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "wb").write(rom)
        print("built", out, hashlib.sha1(rom).hexdigest())
    elif cmd == "check":
        import textins
        rom = load_orig()
        ident = bytearray(rom)
        textins.apply(ident, lang=None, marker=False, alloc=None)  # re-encode jp in place
        if bytes(ident) != rom:
            diff = next(i for i in range(len(rom)) if ident[i] != rom[i])
            sys.exit(f"identity build differs at {diff:#x}")
        print("identity ok")
        sys.exit(textins.lint(lang))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
