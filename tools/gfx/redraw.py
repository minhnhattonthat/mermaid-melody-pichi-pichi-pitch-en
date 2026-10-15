"""Generate gfx/en/*.png from the original resources: one function per resource, all text from TERMS below.
    python -X utf8 tools/gfx/redraw.py [name ...]     (writes gfx/en/<bank>_<idx>.png and work/gfx_prev/*.png)
"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import res, pixfont as P  # noqa: E402

ROM = os.path.join(ROOT, "rom", "Mermaid Melody - Pichi Pichi Pitch (Japan).gba")
EN = os.path.join(ROOT, "gfx", "en")
PREV = os.path.join(ROOT, "work", "gfx_prev")
B0 = "0xc67d94"


def load(bank, idx):
    rom = open(ROM, "rb").read()
    d, info = res.decode(rom, bank, idx)
    return res.to_sheet(d, info)


def save(sheet, bank, idx):
    os.makedirs(EN, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    name = f"{bank[2:]}_{idx:03d}.png"
    res.save_png(sheet, os.path.join(EN, name))
    res.save_png(sheet, os.path.join(PREV, name), zoom=3)


def center_text(dst, cx, y, text, ink, ring=None, bold=True, diag_ring=None):
    m = P.trim_rows(P.render(text, bold=bold))
    x = cx - m.shape[1] // 2
    if diag_ring is not None:
        P._put(dst, x - 1, y - 1, P.dilate(m, 1, True), diag_ring)
    if ring is not None:
        P._put(dst, x - 1, y - 1, P.dilate(m, 1, False), ring)
    P._put(dst, x, y, m, ink)
    return m.shape[1]


# ---------------------------------------------------------------- main menu buttons (#27, 64x64 OBJ each)
BUTTONS = ["Solo|Pitch", "Group|Pitch", "Your|Pitch", "Nonstop|Pitch", "Live|Pitch", "Hippo|Pitch",
           "Medley|Pitch", "Together|Pitch", "Survival|Pitch", "Name|Pitch", "Style|Pitch"]


def r_027():
    sh = load(B0, 27)
    for k, label in enumerate(BUTTONS):
        cx, cy = (k % 4) * 64, (k // 4) * 64
        r = sh[cy + 20:cy + 46, cx + 12:cx + 52]
        fill = int(np.bincount(r.ravel(), minlength=16).argmax())
        ink = {fill + 1, fill + 2, fill + 3, 15}
        # first JP text row: >= 5 white pixels (row 12+ skips the gloss)
        top = {3: cy + 23}.get(k) or next(y for y in range(cy + 12, cy + 40)
                                           if (sh[y, cx + 13:cx + 53] == 15).sum() >= 5)
        for y in range(top - 1, top + 22):
            for x in range(cx + 13, cx + 53):
                if sh[y, x] in ink:
                    sh[y, x] = fill
        l1, l2 = label.split("|")
        mid = cx + 31
        for text, y in ((l1, top), (l2, top + 11)):
            bold = P.width(text, bold=True) <= 40
            center_text(sh, mid, y, text, 15, ring=fill + 2, bold=bold, diag_ring=fill + 1)
    save(sh, B0, 27)


# ---------------------------------------------------------------- main menu message bars (#28-33, 256x32 OBJ strip)
BARS = {28: "Aim for a high score!", 29: "Play with friends over the Link Cable!",
        30: "Live Start with your saved data!", 31: "Make a song that's all your own!",
        32: "You can change all kinds of settings!", 33: "You can change all kinds of settings!"}


def r_bar(i):
    def f():
        sh = load(B0, i)
        sh[:] = load(B0, 27)[224:256]           # #27 keeps the empty bar
        text = BARS[i]
        bold = P.width(text, bold=True) <= 222
        m = P.render(text, bold=bold)
        x = 9
        P._put(sh, x - 1, 12, P.dilate(m, 1, True), 6)
        P._put(sh, x, 13, m, 15)
        save(sh, B0, i)
    return f


# ---------------------------------------------------------------- name entry grid (#35, 8x16 OBJ cells)
# cells as (tile x, tile y) in screen order per row (OAM dump of the name entry screen); page 2 = ty + 16
NAME_CELLS = [
    [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (15, 0), (0, 2), (1, 2), (2, 2), (3, 2),
     (14, 2), (15, 2), (0, 4), (1, 4), (2, 4), (11, 4), (12, 4), (13, 4), (9, 6), (10, 6)],
    [(5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2),
     (3, 4), (4, 4), (5, 4), (7, 6), (14, 4), (15, 4), (0, 6), (1, 6), (2, 6)],
    [(10, 0), (11, 0), (12, 0), (13, 0), (14, 0), (9, 2), (10, 2), (11, 2), (12, 2), (13, 2),
     (6, 4), (7, 4), (8, 4), (9, 4), (10, 4), (3, 6), (4, 6), (5, 6), (6, 6)],
]
# controller's character layout (text engine maps the codes); "" = blank cell
NAME_ROWS = [list("ABCDEFGHIJKLMNOPQR") + ["", ""], list("STUVWXYZ.,!?-'01234"), list("56789&()/:~+=#*♪♥★%")]


def r_035():
    sh = load(B0, 35)
    for page, lower in ((0, False), (16, True)):
        for cells, chars in zip(NAME_CELLS, NAME_ROWS):
            assert len(cells) == len(chars), (len(cells), len(chars))
            for (tx, ty), ch in zip(cells, chars):
                x0, y0 = tx * 8, (ty + page) * 8
                sh[y0:y0 + 16, x0:x0 + 8] = 0
                if not ch:
                    continue
                if lower:
                    ch = ch.lower()
                m = P.render(ch)
                P._put(sh, x0 + (8 - m.shape[1]) // 2 + 1, y0 + 6, m, 13)   # soft shadow
                P._put(sh, x0 + (8 - m.shape[1]) // 2, y0 + 5, m, 15)
    save(sh, B0, 35)


def dump(name):
    import screen
    return screen.Dump(os.path.join(ROOT, "gfx", "dumps", name))


def text_at(canvas, x, y, text, ink, outline, bold=False, diag=True):
    m = P.trim_rows(P.render(text, bold=bold))
    P._put(canvas, x - 1, y - 1, P.dilate(m, 1, diag), outline)
    P._put(canvas, x, y, m, ink)
    return m.shape[1]


# ---------------------------------------------------------------- name entry header (#209 at OBJ tile 16,16)
def r_209():
    import screen
    sh = load(B0, 209)

    # screen x 48-80 and 168-200 show the same tiles (shared sprite): both hold the same arrow
    def draw(c, cov):
        c[:, 16:118][c[:, 16:118] >= 0] = 0
        c[:, 136:240][c[:, 136:240] >= 0] = 0
        text_at(c, 17, 5, "START", 15, 5)
        for x in (48, 168):
            text_at(c, x + 13, 4, "→", 15, 5)
        text_at(c, 80, 4, "OK", 15, 5, bold=True)
        text_at(c, 137, 5, "Select", 15, 5)
        text_at(c, 201, 4, "A/a", 15, 5, bold=True)
    screen.edit_obj(dump("nameentry"), sh, (16, 16), (0, 0, 240, 20), draw)
    save(sh, B0, 209)


ALL = {"027": r_027, "035": r_035, "209": r_209}
ALL.update({f"{i:03d}": r_bar(i) for i in BARS})

if __name__ == "__main__":
    for k in (sys.argv[1:] or ALL):
        ALL[k]()
        print("redrew", k)
