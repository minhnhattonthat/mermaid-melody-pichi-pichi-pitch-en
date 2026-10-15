"""Run game routines offline with unicorn (ROM + RAM + VRAM + DMA3 emulation) to get BG maps the game builds.
    python -X utf8 tools/gfx/uemu.py MAPIDX OUT.bin     -> 0x800-byte BG map (screen base 0x0600C000) for map MAPIDX
Map MAPIDX is entry MAPIDX of the screen table 0x08D662DC (full-screen cards: card #i uses map i-0x86).
IWRAM (decompressor code, tables) comes from a RAM dump of a running game (work/qa/ram1/ram_002000.bin).
"""
import os, struct, sys
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_MEM_WRITE, UC_HOOK_INTR
from unicorn.arm_const import *

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ROM = os.path.join(ROOT, "rom", "Mermaid Melody - Pichi Pichi Pitch (Japan).gba")
RAMDUMP = os.path.join(ROOT, "work", "qa", "ram1", "ram_002000.bin")
STOP = 0x08FFFF00


def machine(rom_bytes=None):
    rom = rom_bytes or open(ROM, "rb").read()
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    uc.mem_map(0x08000000, 0x2000000)
    uc.mem_write(0x08000000, bytes(rom))
    for base, size in ((0x02000000, 0x40000), (0x03000000, 0x8000), (0x04000000, 0x1000),
                       (0x05000000, 0x1000), (0x06000000, 0x20000), (0x07000000, 0x1000)):
        uc.mem_map(base, size)
    d = open(RAMDUMP, "rb").read()
    uc.mem_write(0x03000000, d[0x40000:0x48000])
    dma = {}

    def on_io(uc_, access, addr, size, value, _):
        if not (0x040000D4 <= addr <= 0x040000DF):
            return
        for k in range(size):
            dma[addr + k] = (value >> (8 * k)) & 0xFF
        cnth = dma.get(0x040000DE, 0) | dma.get(0x040000DF, 0) << 8
        if addr + size - 1 >= 0x040000DE and cnth & 0x8000:
            src = sum(dma.get(0x040000D4 + i, 0) << (8 * i) for i in range(4))
            dst = sum(dma.get(0x040000D8 + i, 0) << (8 * i) for i in range(4))
            cnt = dma.get(0x040000DC, 0) | dma.get(0x040000DD, 0) << 8 or 0x10000
            w = 4 if cnth & 0x400 else 2
            sfix = (cnth >> 7) & 3 == 2
            dfix = (cnth >> 5) & 3 == 2
            for i in range(cnt):
                v = uc_.mem_read(src + (0 if sfix else i * w), w)
                uc_.mem_write(dst + (0 if dfix else i * w), bytes(v))
            dma[0x040000DF] = dma[0x040000DF] & 0x7F
    uc.hook_add(UC_HOOK_MEM_WRITE, on_io, begin=0x04000000, end=0x04000FFF)

    def busy_clear(uc_, addr, size, _):  # the DMA wrapper polls the enable bit: DMA is instant here
        b = uc_.mem_read(0x040000DF, 1)[0]
        if b & 0x80:
            uc_.mem_write(0x040000DF, bytes([b & 0x7F]))
    from unicorn import UC_HOOK_CODE
    uc.hook_add(UC_HOOK_CODE, busy_clear, begin=0x08000500, end=0x08000700)

    def on_intr(uc_, intno, _):
        raise RuntimeError(f"SWI/interrupt {intno} at {uc_.reg_read(UC_ARM_REG_PC):#x}")
    uc.hook_add(UC_HOOK_INTR, on_intr)
    uc.mem_map(STOP & ~0xFFF, 0x1000) if False else None
    return uc


def call(uc, fn, args=(), stack_args=()):
    sp = 0x03007E00
    for i, a in enumerate(stack_args):
        uc.mem_write(sp + 4 * i, struct.pack("<I", a))
    uc.reg_write(UC_ARM_REG_SP, sp)
    for i, a in enumerate(args):
        uc.reg_write(UC_ARM_REG_R0 + i, a)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    uc.emu_start(fn | 1, STOP, count=20_000_000)
    return uc.reg_read(UC_ARM_REG_R0)


def screen_map(mapidx, rom_bytes=None):
    uc = machine(rom_bytes)
    ptr = call(uc, 0x08002150, (0x08D662DC, mapidx))
    call(uc, 0x080020B8, (ptr, 0x0600C000, 0, 0), (0, 0))
    return bytes(uc.mem_read(0x0600C000, 0x800))


def card_palette(card, rom_bytes=None):
    """BG palettes (16 x 16 BGR555) the game loads for full-screen card #card (157..175)."""
    uc = machine(rom_bytes)
    call(uc, 0x080012F4, (0x08D4EBF8, (card - 157) * 14 + 0x228, 0, 0xE))
    return bytes(uc.mem_read(0x030002A0, 0x200))  # palette work buffer (BG palette 0 at 0x030002A0)


if __name__ == "__main__":
    m = screen_map(int(sys.argv[1], 0))
    open(sys.argv[2], "wb").write(m)
    print(m[:64].hex())
