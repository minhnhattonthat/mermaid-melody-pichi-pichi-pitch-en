"""Graphics-only test ROM: original expanded to 32 MiB + gfx.apply -> work/gfx_test.gba (no text changes).
    python -X utf8 tools/gfx/testbuild.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from build import Alloc, load_orig, SIZE  # noqa: E402
import apply  # noqa: E402

rom = bytearray(load_orig()) + b"\xff" * (SIZE - 0x1000000)
alloc = Alloc(rom, 0x1400000, SIZE)
apply.apply(rom, alloc)
out = os.path.join(ROOT, "work", "gfx_test.gba")
open(out, "wb").write(rom)
print(out, "used", hex(alloc.p - 0x1400000))
