"""English font + VWF engine for the text bank (mode-0 renderer 0x080174BC replaced).

Codes: 0x00 = space, 0x01.. = the glyphs of font_glyphs.G in CHARS order. Icons keep their original codes
(D-pad/A button 0x138-0x13F, alt glyph table). Glyph data is written in place over the Japanese font at
0xD74FF0 (36 bytes/glyph, 12 rows x 3 bytes, 2 bits per pixel, pixel 0 in the low bits), the per-code info
table 0xD7ECAC is rewritten (mouth shape bits only), digits in the name/number table 0xD7F384 are repointed.
VWF: vwf.s (Thumb) draws pixel-exact into 8x16 tile columns and returns the advance; the caller at 0x08017D16
adds the returned advance to the pen x ([win+0x2B]).
"""
import os, re, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from font_glyphs import G  # noqa: E402

FONT, INFO, NUMTAB, LUT = 0xD74FF0, 0xD7ECAC, 0xD7F384, 0xD739F0
ICONS = {"{A}": 0x13F, "{L}": 0x13C, "{D}": 0x13A, "{U}": 0x139, "{C}": 0x138}  # A button, D-pad left/down/up/centre
CHARS = [c for c in G if c != " "]
CODE = {" ": 0}
for i, c in enumerate(CHARS):
    CODE[c] = i + 1
assert len(CODE) < 0x138
SPACE_W = 3


def reverse_table():
    r = dict(CODE)
    r.update(ICONS)
    return r


def advance(ch):
    if ch == " ":
        return SPACE_W
    if ch in ICONS:
        return 13
    return len(G[ch][0]) + 1


TOKEN = re.compile(r"\[[0-9A-F]{2}(?: [0-9A-F]{2})*(?: @)?\]|\{@\}|\{[A-Z]\}|\n|.", re.S)


def line_widths(markup):
    """Pixel width of each line (split on newline) of an English markup string; controls count 0."""
    ws, w = [], 0
    for t in TOKEN.findall(markup):
        if t == "\n":
            ws.append(w); w = 0
        elif t.startswith("[") or t == "{@}":
            continue
        else:
            w += advance(t) if (t in CODE or t in ICONS) else 0
    ws.append(w)
    return ws


def marker_text(jp):
    """Marker build: keep controls/newlines, replace text with a fixed English filler."""
    out, n = [], 0
    for t in TOKEN.findall(jp):
        if t == "\n" or t.startswith("[") or t == "{@}" or t in ICONS:
            out.append(t)
        elif n < 1:
            out.append("The quick brown fox"); n += 1
    return "".join(out)


def fix_controls(markup):
    """English uses only the mode-0 VWF renderer: FD xx -> FD (xx & ~3)."""
    return re.sub(r"\[FD ([0-9A-F]{2})\]", lambda m: "[FD %02X]" % (int(m.group(1), 16) & ~3 & 0xFF), markup)


def glyph_bytes(ch):
    rows = G[ch]
    out = bytearray()
    for r in rows:
        bits = 0
        for i, p in enumerate(r[:12]):
            v = {".": 0, "+": 2, "#": 3}[p]
            bits |= v << (2 * i)
        out += bits.to_bytes(3, "little")
    return bytes(out)


VOWEL = {"a": 1, "i": 2, "u": 3, "e": 4, "o": 5, "y": 2}


def install(rom, alloc):
    import vwf
    # glyphs
    for ch, c in CODE.items():
        if c:
            rom[FONT + 36 * c:FONT + 36 * c + 36] = glyph_bytes(ch)
    # info table: keep icon entries, set mouth bits for letters
    for c in range(0x1B5):
        old = struct.unpack_from("<H", rom, INFO + 2 * c)[0]
        if c in ICONS.values():
            continue
        ch = next((k for k, v in CODE.items() if v == c), None)
        val = (VOWEL.get(ch.lower(), 0) << 9) if ch else 0
        struct.pack_into("<H", rom, INFO + 2 * c, val)
    # width table
    widths = bytearray(0x200)
    for ch, c in CODE.items():
        widths[c] = advance(ch)
    for k, c in ICONS.items():
        widths[c] = 13
    wt = alloc.put(bytes(widths))
    # digits for number printing (FB) / name table head
    for d in range(10):
        struct.pack_into("<H", rom, NUMTAB + 2 * d, CODE[str(d)])
    vwf.install(rom, alloc, wt)


def lint(ents):
    """Width + encodability lint for English entries; returns error count."""
    import json
    errs = 0
    budgets = load_budgets()
    for e in ents:
        en = e.get("en") or ""
        if not en:
            continue
        for t in TOKEN.findall(en):
            if not (t == "\n" or t.startswith("[") or t == "{@}" or t in CODE or t in ICONS):
                print(e["id"], "unencodable", repr(t)); errs += 1
        if re.search(r"[぀-ヿ一-鿿]", en):
            print(e["id"], "Japanese left in en"); errs += 1
        if en.count("{@}") != e["jp"].count("{@}") or en.count("@]") != e["jp"].count("@]"):
            print(e["id"], "label/jump count differs from jp"); errs += 1
        box = e.get("box") or "default"
        b = budgets.get(box)
        if b:
            for w in line_widths(en):
                if w > b["px"]:
                    print(e["id"], f"line {w}px > {b['px']}px ({box})"); errs += 1
            if b.get("lines") and en.count("\n") + 1 > b["lines"]:
                print(e["id"], f"{en.count(chr(10)) + 1} lines > {b['lines']} ({box})"); errs += 1
    return errs


def load_budgets():
    import json
    p = os.path.join(os.path.dirname(HERE), "data", "windows.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


if __name__ == "__main__":
    for s in sys.argv[1:]:
        print(line_widths(s.replace("\\n", "\n")), repr(s))
