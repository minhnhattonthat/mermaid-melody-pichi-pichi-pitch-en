# Mermaid Melody Pichi Pichi Pitch (GBA, Konami 2003) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `<SKILL_DIR>/SKILL.md`; `$SKILL` = the directory holding its SKILL.md). Read it before ROM, text or QA work.

## Commands (run from repo root)
- Build:    `python -X utf8 tools/build.py build`        -> build/mmppp_en.gba (checks the dump against `rom.sha1` first; `--marker` = marker build)
- Check:    `python -X utf8 tools/check.py`  (codec selftest, identity build, text lint; the pre-commit hook runs this)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/mmppp_en.gba --out work/qa/smoke --route tools/routes/mainmenu.txt --smoke`
- Warp:     scene list and routes in `tools/debug/scenes.md` (debug menu: poke state 0x0001 into 0x03001E00 from the main menu, `tools/debug/state.lua`); never ask the user to play to a scene
- Release:  `python -X utf8 tools/release.py` (patch + verify; never publish without the user; `$SKILL` env var overrides the plugin path)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original ROM: `rom/Mermaid Melody - Pichi Pichi Pitch (Japan).gba` (gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`; copy at work/orig.gba). Emulator: this repo's own copy in `tools/mesen/` (MesenCE 2.2.1, https://github.com/nesdev-org/MesenCE/releases/download/2.2.1/Mesen_2.2.1_Windows.zip; BIOS via fetch_emu.py gba-bios; gitignored; settings in `tools/emu-config/`). Savestates: `work/states/`.
- Text: `script/text.json` (text bank: lyrics, UI, credits). Tables: `tbl/jp.tbl` (glyph table, OCR'd by eye + song-credit research). Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.
- Text pipeline: tools/textcodec.py (format), tools/textins.py (dump/identity/insert). English font: tools/font_glyphs.py + font_en.py + vwf.py (VWF hook on 0x080174BC, advance patch 0x08017D16). Batches: tools/batches.py (split/check/merge/pairs), work/tl/, brief docs/translator-brief.md.
- Graphics: tools/gfx/apply.py, gfx/orig + gfx/en PNGs, survey docs/re/graphics.md, terms docs/gfx_terms.md. Cards #157-176: tools/gfx/cards.py (offline map/palette via tools/gfx/uemu.py). Lua probes: tools/lua/ (execlog.lua = registers at an exec addr, dmalog.lua).

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- glossary.md must stay reusable by the sequel (Pichi Pichi Party, sibling repo).
- QA states made with the JP ROM keep JP SRAM (Hippo song in Japanese codes): regenerate from cold boot.
- Release README text: `docs/README.template.txt` (filled by tools/release.py).

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
