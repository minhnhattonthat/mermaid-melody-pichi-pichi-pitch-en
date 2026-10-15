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


ALL = {"027": r_027}
ALL.update({f"{i:03d}": r_bar(i) for i in BARS})

if __name__ == "__main__":
    for k in (sys.argv[1:] or ALL):
        ALL[k]()
        print("redrew", k)
