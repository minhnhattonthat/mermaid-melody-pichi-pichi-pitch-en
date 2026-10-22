# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| `tools/font_glyphs.py` | drawn for this project | MIT, same as repo | yes | 12x12 VWF text bank (lyrics, UI, credits) | - |
| Arial Rounded MT Bold (`C:/Windows/Fonts/ARLRDBD.TTF`, `tools/gfx/redraw.py`) | Windows system font | Monotype/Microsoft EULA | unclear: only binarised rendered pixels ship, never the font file; check before publishing | large graphics text | rendered, binarised |
| Comic Sans MS Bold (`C:/Windows/Fonts/comicbd.ttf`, `tools/gfx/cards.py`) | Windows system font | Microsoft EULA | unclear: only rendered pixels ship, never the font file; check before publishing | logo stickers, cards #157-176 | rendered |
| Game 12x12 font (ROM 0xD74FF0) | original game | Konami; not in this repo | not redistributed | Japanese text (overwritten by the English glyphs) | - |
