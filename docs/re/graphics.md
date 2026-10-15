# Graphics text survey (bank 0xC67D94 unless noted)

Pipeline: tools/gfx/redraw.py (one function per resource) -> gfx/en/<bank>_<idx>.png -> tools/gfx/apply.py
(recompress, repoint 5-byte record). Sheet layout: tools/gfx/res.py. Screen-space edits: tools/gfx/screen.py
(edit_obj / edit_bg on PPU dumps in gfx/dumps/). Find a resource from a screen: tools/gfx/whose.py DUMP --rect.
Loads per screen: tools/lua/gfxload.lua + tools/gfx/loadmap.py. Graphics-only test ROM: tools/gfx/testbuild.py.
Terms: docs/gfx_terms.md.

| res | content | screen / route | status |
|---|---|---|---|
| #2 | title logo + 講談社… copyright | title (gfx_mainmenu.txt, first 1600 f) | English |
| #27 | 11 menu buttons + empty message bar | main menu + sub menus (gfx_mainmenu.txt) | English |
| #28-33 | main menu message bars | main menu carousel | English |
| #35 | kana grid (2 pages) | gfx_nameentry.txt; Hippo lyric editor | English (Latin grid, controller layout) |
| #209 | name entry header START/SELECTボタン | gfx_nameentry.txt | English |
| #72 | song plates (titles, furigana, Hippo/Nothing-here plates) | gfx_songselect.txt; Live (menu right x2, A) | English |
| #7 | play HUD てん (2 tiles) | song play (gfx_solo.txt) | English "pts" (abbreviation, 16 px) |
| #58 | difficulty bubbles, いつもの/きぶん, A/B hint | gfx_difficulty.txt | English (きぶん -> "Free", meaning unverified) |
| #40 | results labels, small てん, best score, badges | results (state work/qa/gfx_solo/s007000.mss +300 f) | English; Easy/Normal/Usual badges checked; Hard/Free badges rebuilt from the tile layout (first+row*16+col), not seen on screen |
| #41 | results big てん | results | English "pts" |
| #119 | post-song みる/セーブ/もどる | results + A | English |
| #120 | Hippo editor menu bubbles, START/SELECT headers | Hippo Pitch (menu left x2, A; START) | English (incl. まえとかわったけどセーブする? panel; edit a line, START, Back) |
| #57 | Style Pitch options plates (ヘッドホン はいけい やじるし あり なし 矢印 絵 なまえ) | menu left, A, right, A | English |
| #157-#175, #177 | full-screen stills (save broken, Game Over, ending cards) | | controller |
| #176 | ゲームオーバー / クリアもくひょう / クリア banners | | controller |
| #45, #39 | mermaid melody frame | | Latin already |
| dd62a0, ef4890, f24461, f5837f, f8854f, eb19e0, fc0830, 0273d0 | art, video frames, arrows, digits | | no Japanese text |

Debug menu: font-drawn (text workstream).
