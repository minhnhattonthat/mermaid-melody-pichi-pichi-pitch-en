"""Text bank codec (lyrics, karaoke and UI strings drawn by the 12x12 font engine at 0x08017C50).

Bank: id table at 0xD71AC0 (768 x u24 offsets) relative to text base 0xD723C0; text ends at 0xD739EF (FF).
Byte codes: 00-EF glyph (glyph index = code, font 0xD74FF0, 36 bytes per glyph); F0-F5 xx two-byte glyph
((b-F0)<<8|xx). Control codes (handlers table 0x08FC05F4):
  F6 s       sub-op (case s&31): 2: +1 if s&80; 4: +2 (+1 if s&80 (+1 if s&40)); 5: +2; 7: +1; 10: +2 if s&80; 12: +3
  F7         no args            F8 o24  call text at base+o24     F9 o24  jump to base+o24
  FA f ..    function f (table 0x08FC055C): 0F/10/11 +u8, 0C +u16, 08 +u24 jump table, 05 menu (see ctl_len)
             FB p32 b  print number at p32     FC a [b if not a&C0]  position
  FD b       window style       FE newline                        FF end / return
"""
TABLE, BASE, COUNT = 0xD71AC0, 0xD723C0, 768
TEXT_END = 0xD739EF  # exclusive (last FF at 0xD739EE)


def ctl_len(data, p):
    """Length of the control token at data[p] (p points at the code byte)."""
    b = data[p]
    if b == 0xF6:
        s = data[p + 1]; c = s & 31; n = 2
        if c == 2 and s & 0x80: n += 1
        elif c == 4:
            n += 2
            if s & 0x80:
                n += 1
                if s & 0x40: n += 1
        elif c == 5: n += 2
        elif c == 7: n += 1
        elif c == 10 and s & 0x80: n += 2
        elif c == 12: n += 3
        return n
    if b in (0xF7, 0xFE, 0xFF): return 1
    if b in (0xF8, 0xF9): return 4
    if b == 0xFA:
        f = data[p + 1]
        if f in (0x0F, 0x10, 0x11): return 3            # u8 arg
        if f == 0x0C: return 4                          # u16 arg
        if f == 0x08: return 5                          # jump table u24 x (sel+1); only sel=0 tables occur (debug menu)
        if f == 0x05:                                   # menu: FF end | FE jump table (unused) | spec [+u8 if &80]
            a = data[p + 2]
            if a == 0xFE: raise ValueError("FA 05 FE jump table not supported")
            return 3 if a == 0xFF or not a & 0x80 else 4
        return 2
    if b == 0xFD: return 2
    if b == 0xFB: return 6
    if b == 0xFC: return 2 if data[p + 1] & 0xC0 else 3
    raise ValueError(f"bad control {b:#x} at {p:#x}")


def tokens(data, p):
    """Yield (kind, value, raw) from data[p] up to and including the FF. kind: 'g' glyph code, 'c' control."""
    while True:
        b = data[p]
        if b < 0xF0:
            yield "g", b, data[p:p + 1]; p += 1
        elif b < 0xF6:
            yield "g", ((b - 0xF0) << 8) | data[p + 1], data[p:p + 2]; p += 2
        else:
            n = ctl_len(data, p)
            yield "c", b, data[p:p + n]; p += n
            if b == 0xFF:
                return


def offsets(rom):
    return [rom[TABLE + 3 * i] | rom[TABLE + 3 * i + 1] << 8 | rom[TABLE + 3 * i + 2] << 16 for i in range(COUNT)]
