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


# ---------------------------------------------------------------- title screen logo + copyright (#2, OBJ origin 0,0)
TTF = "C:/Windows/Fonts/ARLRDBD.TTF"   # Arial Rounded MT Bold, binarised at large sizes only


def ttf_mask(text, size, thresh=110):
    from PIL import Image, ImageDraw, ImageFont
    f = ImageFont.truetype(TTF, size)
    b = f.getbbox(text)
    im = Image.new("L", (b[2] + 4, b[3] + 4), 0)
    ImageDraw.Draw(im).text((2, 2), text, font=f, fill=255)
    a = (np.array(im) > thresh).astype(np.uint8)
    ys, xs = np.nonzero(a)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def quantize_into(canvas, cov, rgba, dumpobj, palmap, x0, y0):
    """Write an RGBA target into canvas: alpha 0 -> transparent (0), else nearest colour of the covering palette."""
    H, W = canvas.shape
    for y in range(H):
        for x in range(W):
            if not cov[y, x]:
                continue
            r, g, b, a = rgba[y, x]
            if a == 0:
                canvas[y, x] = 0
                continue
            p = palmap[y + y0, x + x0]
            best = min(range(1, 16), key=lambda i: sum((c1 - c2) ** 2 for c1, c2 in
                                                        zip(dumpobj.color(p, i), (r, g, b))))
            canvas[y, x] = best


def stroke(mask, colors):
    """Layered outlines: colors[0] = fill, then 1 px rings outward. Returns (H, W, 4) uint8 and the pad."""
    pad = len(colors) - 1
    layers = [np.pad(mask, pad)]
    for _ in colors[1:]:
        layers.append(P.dilate(layers[-1], 1, True)[1:-1, 1:-1])
    H, W = layers[0].shape
    out = np.zeros((H, W, 4), np.uint8)
    for lay, col in reversed(list(zip(layers, colors))):
        if col is None:
            continue
        out[lay > 0] = (*col, 255)
    return out


def r_002():
    import screen
    sh = load(B0, 2)
    d = dump("title")
    idx, pal, src = screen.obj_layer(d)
    # logo area y 30-110 (Push Start Button sprites start at y 110 and are left as they are)
    X0, Y0, X1, Y1 = 0, 28, 240, 110
    tgt = np.zeros((Y1 - Y0, X1 - X0, 4), np.uint8)
    # "Mermaid Melody": orange, white ring, pink ring
    m1 = ttf_mask("Mermaid Melody", 17)
    s1 = stroke(m1, [(248, 168, 80), (248, 248, 248), (248, 128, 168)])
    # vertical orange gradient
    for y in range(s1.shape[0]):
        row = s1[y]
        sel = (row[:, 0] == 248) & (row[:, 1] == 168)
        t = y / max(1, s1.shape[0] - 1)
        row[sel] = (248, int(200 - 60 * t), int(104 - 30 * t), 255)
    # "Pichi Pichi Pitch": blue gradient body, white ring x2, pink ring
    m2 = ttf_mask("Pichi Pichi Pitch", 27)
    s2 = stroke(m2, [(80, 160, 230), (248, 248, 248), (248, 248, 248), (248, 128, 168)])
    for y in range(s2.shape[0]):
        t = y / max(1, s2.shape[0] - 1)
        col = (int(160 - 120 * t), int(210 - 70 * t), int(245 - 25 * t), 255)
        row = s2[y]
        sel = (row[:, 0] == 80) & (row[:, 1] == 160)
        row[sel] = col
    # sparkles: copy near-white pixels that sat inside the original big logo body
    def blit(s, x, y):
        h, w = s.shape[:2]
        reg = tgt[y:y + h, x:x + w]
        a = s[:, :, 3] > 0
        reg[a] = s[a]
    # sprite coverage is stepped: "Mermaid" fits x 50-130 from y 37, "Melody" x 138-226 from y 53 (an arc,
    # like the original); the big line fits y 77-109, x 12-220
    ma = stroke(ttf_mask("Mermaid", 17), [(248, 168, 80), (248, 248, 248), (248, 128, 168)])
    me = stroke(ttf_mask("Melody", 17), [(248, 168, 80), (248, 248, 248), (248, 128, 168)])
    for s in (ma, me):
        for y in range(s.shape[0]):
            t = y / max(1, s.shape[0] - 1)
            row = s[y]
            sel = (row[:, 0] == 248) & (row[:, 1] == 168)
            row[sel] = (248, int(200 - 60 * t), int(104 - 30 * t), 255)
    blit(ma, 90 - ma.shape[1] // 2, 40 - Y0)
    blit(me, 90 - me.shape[1] // 2, 57 - Y0)
    blit(s2, 12 + (208 - s2.shape[1]) // 2, 80 - Y0)

    def draw(c, cov):
        palmap = pal
        quantize_into(c, cov, tgt, d, palmap, X0, Y0)
    screen.edit_obj(d, sh, (0, 0), (X0, Y0, X1, Y1), draw)

    # copyright: the Japanese line (y 132-146, grey palette) becomes two lines of the tiny font
    def draw_c(c, cov):
        c[c >= 0] = 0
        for text, y in (("© Kodansha, We've, TV Aichi /", 1), ("Pichi Pichi Pitch Production Committee", 8)):
            m = P.render_tiny(text)
            x = (240 - m.shape[1]) // 2
            P._put(c, x - 1, y - 1, P.dilate(m, 1, True), 1)
            P._put(c, x, y, m, 15)
    screen.edit_obj(d, sh, (0, 0), (0, 132, 240, 147), draw_c)
    save(sh, B0, 2)
    preview("title", sh, (0, 0), "002")


def preview(dumpname, sheet, origin, name):
    """Render the dump's OBJ layer with `sheet` patched in at its origin -> work/gfx_prev/<name>_screen.png"""
    import screen
    from PIL import Image
    d = dump(dumpname)
    v = bytearray(d.vram)
    full = res.to_sheet(bytes(v[0x10000:0x18000]), 0)
    ox, oy = origin[0] * 8, origin[1] * 8
    h, w = sheet.shape
    full[oy:oy + h, ox:ox + w] = sheet[:256 - oy, :256 - ox]
    v[0x10000:0x18000] = res.from_sheet(full, 0, 0x8000)
    d.vram = bytes(v)
    idx, pal, src = screen.obj_layer(d)
    im = screen.rgb(d, np.maximum(idx, 0), pal, bg=(40, 40, 60))
    im.resize((720, 480), Image.NEAREST).save(os.path.join(PREV, f"{name}_screen.png"))


# ---------------------------------------------------------------- song plates (#72 all titles, OBJ origin 0,8)
# (dump, title sprite y, main line, small line in the furigana sprites); sprite widths fix the space:
# Promised Land 160+16 px, 大事な宝箱 72 px (+74 px furigana), 恋はなんだろう 96 px
PLATES = [("songselect", 20, 156, "Paradise of the Sun", "Promised Land"),
          ("songselect3", 128, 70, "Treasure Box", "My Precious"),
          ("songselect6", 20, 94, "What Is Love?", "")]


def title_mask(text, avail):
    """Largest rounded title (cap 10 px like the English plates) that fits avail px; 5x7 fallback."""
    for size in (14, 13, 12):
        m = ttf_mask(text, size, thresh=100)
        if m.shape[1] + 2 <= avail:
            return m
    return P.trim_rows(P.render(text))


def plate_text(c, x, y, m, ink=11, ring=15):
    P._put(c, x - 1, y - 1, P.dilate(m, 1, True), ring)
    P._put(c, x, y, m, ink)


def r_072():
    import screen
    sh = load(B0, 72)
    for dn, ty, avail, main, small in PLATES:
        def draw(c, cov, main=main, small=small):
            c[c >= 0] = 0
            if small == "Promised Land":   # furigana sprites x 41-72 and 76-107: tiny dark text either side of the gap
                P._put(c, 2, 2, P.render_tiny("Promised"), 1)
                P._put(c, 37, 2, P.render_tiny("Land"), 1)
            elif small == "My Precious":   # furigana sprites x 43-74 and 77-117
                P._put(c, 22, 1, P.trim_rows(P.render("My")), 15)
                P._put(c, 37, 1, P.trim_rows(P.render("Precious")), 15)
            m = title_mask(main, avail)
            assert m.shape[1] + 2 <= avail, main
            plate_text(c, 2, 10 if m.shape[0] <= 10 else 9, m)
        screen.edit_obj(dump(dn), sh, (0, 8), (40, ty - 8, 220, ty + 16), draw)
    # Live / Hippo plates: the game block-copies these 128x16 sources (sheet rows 16-17) into a plate slot;
    # the Live slot sprites show 80 px of the block, the Hippo one the original text width (~120 px)
    for x0, text, avail in ((0, "Song with Hippo!!", 118), (128, "Nothing here!", 78)):
        blk = sh[128:144, x0:x0 + 128]
        blk[:] = 0
        m = title_mask(text, avail)
        assert m.shape[1] + 2 <= avail, text
        plate_text(blk, 1, 2 if m.shape[0] <= 10 else 1, m)
    save(sh, B0, 72)


# ---------------------------------------------------------------- play screen score unit (#7 BG tiles 0xD4-0xD5)
def r_007():
    sh = load(B0, 7)
    blk = sh[48:56, 160:176]       # "てん" (points) after each score, 16x8: "pts" (abbreviation, only 2 tiles)
    blk[:] = 9
    m = P.render_tiny("pts")
    P._put(blk, (16 - m.shape[1]) // 2 + 1, 2, m, 10)
    P._put(blk, (16 - m.shape[1]) // 2, 1, m, 14)
    save(sh, B0, 7)


ALL = {"027": r_027, "035": r_035, "209": r_209, "002": r_002, "072": r_072, "007": r_007}
ALL.update({f"{i:03d}": r_bar(i) for i in BARS})

if __name__ == "__main__":
    for k in (sys.argv[1:] or ALL):
        ALL[k]()
        print("redrew", k)
