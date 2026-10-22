# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| `tools/font_glyphs.py` | drawn for this project | MIT, same as repo | yes | 12x12 VWF text bank (lyrics, UI, credits) | - |
| `fonts/Nunito.ttf` | https://github.com/google/fonts/blob/main/ofl/nunito/Nunito%5Bwght%5D.ttf (google/fonts 6049366) | OFL 1.1 (`fonts/OFL.txt`) | yes, as rendered glyphs | graphics text: title logo, song plates, "pts", card logo stickers, #176 banners (`tools/gfx/redraw.py`, `tools/gfx/cards.py`) | variable font used at weight 800; binarised |
| Game 12x12 font (ROM 0xD74FF0) | original game | Konami; not in this repo | not redistributed | Japanese text (overwritten by the English glyphs) | - |
