"""Full-screen cards (bank 0xC67D94 #157-#175): English logo stickers and speech bubbles.

Cards are 4bpp tiles + a BG map the game builds from screen table 0x08D662DC (card i -> map i-0x86) and 14 BG
palettes from 0x08D4EBF8 (index (i-157)*14+0x228); both are produced offline by uemu.py. Edits are drawn in RGB in
screen space, then every touched tile is requantised to its own palette and written back (only tiles used once).
    python -X utf8 tools/gfx/cards.py [--preview]   -> gfx/en/c67d94_<i>.png (+ work/cards_preview.png)
"""
import os, struct, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import res, uemu, pixfont  # noqa: E402

BANK = "0xc67d94"
FONT = r"C:\Windows\Fonts\comicbd.ttf"
# logo sticker boxes (screen x, y, w, h) covering the Japanese "Mermaid Melody Pichi Pichi Pitch" logo
LOGO = {164: (2, 114, 126, 44), 165: (2, 0, 116, 40), 166: (112, 114, 126, 44), 167: (112, 114, 126, 44), 168: (2, 114, 126, 44),
        169: (2, 114, 126, 44), 170: (110, 114, 128, 44), 171: (2, 114, 128, 46), 172: (2, 0, 126, 44),
        173: (2, 120, 126, 40), 174: (2, 112, 128, 46), 175: (112, 117, 124, 42)}
# speech bubbles: (x, y, w, h) of the text area to clear (bubble white), lines of English
BUBBLE = {157: ((134, 16, 99, 30), ["Your save data", "is damaged!"], (18, 31)),
          158: ((10, 24, 116, 76), ["Your Live data", "is damaged!"], (43, 74))}  # line y avoids shared tiles


def rgb555(v):
    return ((v & 31) * 255 // 31, ((v >> 5) & 31) * 255 // 31, ((v >> 10) & 31) * 255 // 31)


class Card:
    def __init__(self, rom, i):
        self.i = i
        self.data, self.info = res.decode(rom, BANK, i)
        self.data = bytearray(self.data)
        self.map = struct.unpack("<1024H", uemu.screen_map(i - 0x86, rom))
        pal = struct.unpack("<256H", uemu.card_palette(i, rom))
        self.pal = np.array([rgb555(v) for v in pal], np.int32).reshape(16, 16, 3)
        self.uses = {}
        for y in range(20):
            for x in range(30):
                self.uses.setdefault(self.map[y * 32 + x] & 0x3FF, []).append((x, y))

    def tile(self, e):
        t = e & 0x3FF
        a = res.tiles_to_idx(bytes(self.data[t * 32:t * 32 + 32]))
        if e & 0x400: a = a[:, ::-1]
        if e & 0x800: a = a[::-1, :]
        return a

    def rgb(self):
        im = np.zeros((160, 240, 3), np.uint8)
        for y in range(20):
            for x in range(30):
                e = self.map[y * 32 + x]
                im[y * 8:y * 8 + 8, x * 8:x * 8 + 8] = self.pal[e >> 12][self.tile(e)]
        return im

    def put_rgb(self, new, old):
        """Requantise changed tiles of `new` (RGB screen) into their own palettes and store them."""
        diff = (new != old).any(2)
        skipped = 0
        for y in range(20):
            for x in range(30):
                if not diff[y * 8:y * 8 + 8, x * 8:x * 8 + 8].any():
                    continue
                e = self.map[y * 32 + x]
                t = e & 0x3FF
                if len(self.uses[t]) > 1:
                    # shared tile: only safe when every use shows the same new pixels (flip-aware)
                    want = new[y * 8:y * 8 + 8, x * 8:x * 8 + 8]
                    ok = True
                    for ux, uy in self.uses[t]:
                        ue = self.map[uy * 32 + ux]
                        w2 = new[uy * 8:uy * 8 + 8, ux * 8:ux * 8 + 8]
                        if (ue ^ e) & 0x400: w2 = w2[:, ::-1]
                        if (ue ^ e) & 0x800: w2 = w2[::-1, :]
                        if (ue >> 12) != (e >> 12) or not (w2 == want).all():
                            ok = False
                    if not ok:
                        skipped += 1
                        continue
                block = new[y * 8:y * 8 + 8, x * 8:x * 8 + 8].astype(np.int32)
                pal = self.pal[e >> 12]
                d = ((block[:, :, None, :] - pal[None, None, :, :]) ** 2).sum(3)
                d[:, :, 0] += 10 ** 9  # index 0 is the transparent/backdrop colour on this BG
                a = d.argmin(2).astype(np.uint8)
                if e & 0x400: a = a[:, ::-1]
                if e & 0x800: a = a[::-1, :]
                self.data[t * 32:t * 32 + 32] = res.idx_to_tile(a)
        return skipped


def text_mask(text, size):
    f = ImageFont.truetype(FONT, size, layout_engine=ImageFont.Layout.BASIC)
    l, t, r, b = f.getbbox(text)
    im = Image.new("L", (r - l + 2, b - t + 2), 0)
    ImageDraw.Draw(im).text((1 - l, 1 - t), text, fill=255, font=f)
    return np.array(im) > 110


def stamp(img, m, x, y, color):
    h, w = m.shape
    sub = img[y:y + h, x:x + w]
    sub[m[:sub.shape[0], :sub.shape[1]]] = color


def logo(img, box):
    x, y, w, h = box
    # colours taken from the original logo, so every touched tile's palette has a close match
    BLUE, DARK, WHITE, PINK, SKY = (0, 172, 230), (0, 98, 176), (255, 255, 255), (246, 131, 156), (164, 230, 238)
    pil = Image.fromarray(img)
    dr = ImageDraw.Draw(pil)
    dr.rounded_rectangle([x + 1, y + 1, x + w - 2, y + h - 2], radius=6, fill=WHITE, outline=BLUE, width=2)
    img[:] = np.array(pil)
    big = text_mask("Pichi Pichi Pitch", 16)
    if big.shape[1] > w - 8:
        big = text_mask("Pichi Pichi Pitch", 15)
    small = pixfont.render("Mermaid Melody", bold=True) > 0
    bx = x + (w - big.shape[1]) // 2
    by = y + 14 + (h - 14 - big.shape[0]) // 2
    ring = pixfont.dilate(big.astype(np.uint8), 1) > 0
    stamp(img, ring, bx - 1, by - 1, DARK)
    stamp(img, big, bx, by, BLUE)
    sx = x + (w - small.shape[1]) // 2
    sy = y + 3
    stamp(img, small, sx, sy, PINK)


def bubble(img, box, lines, ys):
    x, y, w, h = box
    img[y:y + h, x:x + w] = (255, 255, 255)
    for t, yy in zip(lines, ys):
        m = pixfont.render(t, bold=True) > 0
        stamp(img, m, x + (w - m.shape[1]) // 2, yy, (24, 24, 48))


def banners(rom):
    """#176 OBJ sheet: ゲ/ム/オ/バ cells + bar (blanked: the Game Over card art already reads GAME OVER),
    クリアもくひょう strip -> "Clear Goal", クリア 3 cells -> CL/EA/R!."""
    d, info = res.decode(rom, BANK, 176)
    s = res.to_sheet(d, info)
    s[0:40, 0:128] = 0

    def draw(text, x, y, w, h, size, squeeze=False):
        m = text_mask(text, size)
        if squeeze and m.shape[1] > w - 2:  # condense horizontally to fit the 32-px cell
            im = Image.fromarray((m * 255).astype(np.uint8)).resize((w - 2, m.shape[0]), Image.BILINEAR)
            m = np.array(im) > 100
        m = m[np.nonzero(m.any(1))[0].min():np.nonzero(m.any(1))[0].max() + 1]
        m = m[:, np.nonzero(m.any(0))[0].min():np.nonzero(m.any(0))[0].max() + 1]
        ox, oy = x + (w - m.shape[1]) // 2, y + (h - m.shape[0]) // 2
        shade = np.zeros_like(m)
        shade[1:, 1:] = m[:-1, :-1]
        for yy, xx in zip(*np.nonzero(pixfont.dilate(m.astype(np.uint8), 1))):
            Y, X = oy - 1 + yy, ox - 1 + xx
            if y <= Y < y + h and x <= X < x + w:
                s[Y, X] = 9
        for yy, xx in zip(*np.nonzero(m)):
            s[oy + yy, ox + xx] = 12 if shade[yy, xx] and not (yy and m[yy - 1, xx]) else 15
    # Game Over sprites sit at x 32 (ゲ), 74 (ム), 104 (オ), 152 (バ) plus bars: GAME in ム, OVER in バ
    draw("GAME", 32, 0, 32, 32, 22, squeeze=True)
    draw("OVER", 96, 0, 32, 32, 22, squeeze=True)
    s[40:64, 0:128] = 0
    draw("Clear Goal", 0, 40, 128, 16, 15)  # the strip's sprites are 16 px tall (rows 56-63 are elsewhere)
    s[64:96, 0:128] = 0
    for k, t in enumerate(("CL", "EA", "R!")):
        draw(t, 32 * k, 72, 32, 24, 22)  # rows 64-71 are also the bottom of the 64x32 Clear Goal sprites
    res.save_png(s, os.path.join(ROOT, "gfx", "en", "c67d94_176.png"))
    return s


def patch_040():
    """#40 results sheet: the medley line "65 pts でクリア" kept でクリア (tiles 0xD0-0xD4 over 0xE0-0xE4, shown as a
    40x16 block). Redraw it as "to clear" on top of the graphics workstream's PNG (idempotent)."""
    p = os.path.join(ROOT, "gfx", "en", "c67d94_040.png")
    im = Image.open(p)
    a = np.array(im)
    blk = np.zeros((16, 40), np.uint8)
    m = pixfont.render("to clear") > 0
    ring = pixfont.dilate(m.astype(np.uint8), 1) > 0
    oy, ox = 3, (40 - m.shape[1]) // 2
    for yy, xx in zip(*np.nonzero(ring)):
        if 0 <= oy - 1 + yy < 16 and 0 <= ox - 1 + xx < 40:
            blk[oy - 1 + yy, ox - 1 + xx] = 0x9
    for yy, xx in zip(*np.nonzero(m)):
        blk[oy + yy, ox + xx] = 0xE
    for k in range(5):
        a[48:56, 128 + 8 * k:136 + 8 * k] = blk[0:8, 8 * k:8 * k + 8]
        a[56:64, 8 * k:8 * k + 8] = blk[8:16, 8 * k:8 * k + 8]
    out = Image.fromarray(a, "P")
    out.putpalette(im.getpalette())
    out.save(p)


def main():
    rom = open(os.path.join(ROOT, "rom", "Mermaid Melody - Pichi Pichi Pitch (Japan).gba"), "rb").read()
    previews = []
    for i in sorted(set(LOGO) | set(BUBBLE)):
        c = Card(rom, i)
        old = c.rgb()
        new = old.copy()
        if i in LOGO:
            logo(new, LOGO[i])
        if i in BUBBLE:
            bubble(new, *BUBBLE[i])
        skipped = c.put_rgb(new, old)
        if skipped:
            print(f"#{i}: {skipped} shared tiles not edited")
        res.save_png(res.to_sheet(bytes(c.data), c.info), os.path.join(ROOT, "gfx", "en", f"c67d94_{i:03d}.png"))
        previews.append(c.rgb())
    b = banners(rom)
    patch_040()
    if "--preview" in sys.argv:
        res.save_png(b, os.path.join(ROOT, "work", "banner176.png"), zoom=3)
        W = 3
        H = (len(previews) + W - 1) // W
        m = Image.new("RGB", (240 * W, 160 * H))
        for k, p in enumerate(previews):
            m.paste(Image.fromarray(p), ((k % W) * 240, (k // W) * 160))
        m.save(os.path.join(ROOT, "work", "cards_preview.png"))


if __name__ == "__main__":
    main()
