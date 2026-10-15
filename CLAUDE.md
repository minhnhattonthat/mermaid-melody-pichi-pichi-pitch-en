# Mermaid Melody Pichi Pichi Pitch (GBA) English translation

Skill: translate-retro-game (H:\translation\batch\.claude\skills\translate-retro-game\SKILL.md). Read it before ROM, text or QA work.
Batch brief: H:\translation\batch\projects\BATCH_BRIEF.md (all rulings pre-approved; never push/publish).

## Commands (run from repo root)
- Build:    `python -X utf8 tools/build.py build` -> build/mmppp_en.gba
- Check:    `python -X utf8 tools/check.py` (pre-commit hook runs this)
- Smoke:    `python -X utf8 H:/translation/batch/.claude/skills/translate-retro-game/scripts/emu.py build/mmppp_en.gba --out work/qa/smoke --route tools/routes/mainmenu.txt --smoke`
- Warp:     see tools/debug/ (scene list) once written
- Release:  `python -X utf8 tools/release.py`

## Paths
- Original ROM: `rom/Mermaid Melody - Pichi Pichi Pitch (Japan).gba` (copy at work/orig.gba). Emulator: tools/mesen/ (MesenCE 2.2.1,
  https://github.com/nesdev-org/MesenCE/releases/download/2.2.1/Mesen_2.2.1_Windows.zip; BIOS via fetch_emu.py gba-bios). Settings copy: tools/emu-config/.
- RE notes: docs/re/README.md. Glossary + rulings: glossary.md. Lua probes: tools/lua/ (execlog.lua = registers at an exec addr, dmalog.lua).

## Rulings
- Edit source only with Edit/Write tools. Honorifics dropped; Western name order; official English anime/manga names (Lucia, Hanon, Rina).
- Credits English. All graphics text in scope. Full words, no abbreviations unless flagged.
- glossary.md must stay reusable by the sequel (Pichi Pichi Party, sibling repo).

## Pipeline
- Text bank (lyrics/UI/credits): tools/textcodec.py (format), tools/textins.py (dump/identity/insert), script/text.json,
  tbl/jp.tbl (glyph table, OCR'd by eye + song-credit research). English: tools/font_glyphs.py + font_en.py + vwf.py
  (VWF hook on 0x080174BC, advance patch 0x08017D16). Batches: tools/batches.py (split/check/merge/pairs), work/tl/.
- Graphics: tools/gfx/apply.py (owned by the graphics workstream), gfx/orig + gfx/en PNGs, docs/re/graphics.md.
- Debug menu: poke state 0x0001 into 0x03001E00 from the main menu (tools/debug/state.lua); states in work/states/.

## Status
- Done: text side complete (304/304 strings English, reviewed, lint 0; VWF; name entry Latin grid; staff roll
  reflowed). Release tooling ready (tools/release.py). Graphics: title, main menu buttons/bars, song plates, name
  grid English. Next: remaining graphics rows (difficulty, results, post-song menu, sub menus, live, song editor,
  title cards #157-175, button hints) -> docs/re/graphics.md; phase 8 QA (save/load on 32 MiB, ending, staff roll,
  t022E/t027B/save-error screens); release. Open bugs: none known.
