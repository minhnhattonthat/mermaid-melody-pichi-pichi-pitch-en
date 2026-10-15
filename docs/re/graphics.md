# Graphics text survey (bank 0xC67D94 unless noted)

Pipeline: tools/gfx/redraw.py (one function per resource) -> gfx/en/<bank>_<idx>.png -> tools/gfx/apply.py
(recompress, repoint 5-byte record). Sheet layout: tools/gfx/res.py. Screen-space edits: tools/gfx/screen.py
(edit_obj on PPU dumps in gfx/dumps/). Find a resource from a screen: tools/gfx/whose.py DUMP --rect.
Loads per screen: tools/lua/gfxload.lua + tools/gfx/loadmap.py. Graphics-only test ROM: tools/gfx/testbuild.py.

| res | content | screen / route | status |
|---|---|---|---|
| #2 | title logo マーメイドメロディー ぴちぴちピッチ + 講談社… copyright | title (gfx_mainmenu.txt first 1600 f) | English |
| #27 | 11 menu buttons (ひとりでピッチ …) + empty message bar | main menu + sub menus (gfx_mainmenu.txt) | English |
| #28-33 | main menu message bars | main menu carousel | English |
| #35 | name entry kana grid (2 pages) | gfx_nameentry.txt | English (Latin grid per controller layout) |
| #209 | name entry header START/SELECTボタン | gfx_nameentry.txt | English |
| #72 | song plates (titles + furigana, Hippo/Nothing-here plates) | gfx_songselect.txt, Live (main menu right x2, A) | English |
| #7 | play screen てん (score unit, 2 tiles) | gfx_solo.txt (song play) | English "pts" (abbrev. forced: 16 px) |
| #58 | difficulty かんたん/ふつう/むずかしい, A/B ボタン けってい もどる, いつもの/きぶん | song select -> A (work/states/gfx_diff2.mss) | TODO |
| #40 | results/score labels (かんたん ふつう むずかしい いつもの きぶん small) + score text | results screen | TODO |
| #41 | big digits + てん / scoring glyphs | results | TODO (digits fine; kana part) |
| #57 | song-maker items ヘッドホン 矢印 あり なし なまえ 絵 やじるし はいけい | Hippo Pitch editor | TODO |
| #119 | post-song buttons もどる みる セーブ | after results | TODO |
| #120 | はい/いいえ/もどる/あそぶ/きいてみる/セーブ, START メニューへ, セーブする?, まえとかわったけどセーブ, SELECT きりかえ | Hippo editor / save prompts | TODO |
| #176 | ゲームオーバー / クリアもくひょう / クリア | play result banners | TODO |
| #157-175, #177 | full-screen title cards with logo text | song intros / mode cards | TODO (survey) |
| #45, #39 | mermaid melody frame | name entry bg | Latin already |
| dd62a0 (lyrics/dancers) | character art, no text | play | no text |
| ef4890/f24461/f5837f/f8854f | movie frames | song intro video | no text |

Debug menu (state 0x0001): font-drawn, text workstream.
