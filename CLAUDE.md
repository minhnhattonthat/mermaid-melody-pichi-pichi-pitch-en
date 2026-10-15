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

## Status
- Done: Step 0 (emulator, hooks), codec (tools/mmcomp.py), bank scan. Next: catalogue all text graphics (phase 1 survey). Open bugs: none.
