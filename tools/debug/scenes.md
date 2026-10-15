# Scene list (debug tool)

All from a cold boot: `tools/routes/mainmenu.txt` reaches the main menu (save `--state-out work/states/mainmenu.mss`).
Debug menu: main menu route, then `--script tools/debug/state.lua --var STATE=0x0001 --var AT=2100` (the game's own
leftover debug menu, state 0 of table 0x08EB0E9C) -> `work/states/debugmenu.mss` after ~3000 frames.
`EMU = python -X utf8 H:/translation/batch/.claude/skills/translate-retro-game/scripts/emu.py <rom>`

| scene | how (from state) |
|---|---|
| title | cold boot, 1300 frames |
| main menu + message bar | mainmenu.mss; left/right rotate the buttons |
| song select / difficulty | mainmenu.mss: `6 a;200 -;6 a;250 -` (down = next song), `6 a` -> difficulty |
| song play + lyrics | as above + `6 a;200 -;6 a` then `--mash 150`; line buffers: work/lines.py on a RAM dump |
| results / post-song menu | song play + mash ~5000 frames |
| name entry | mainmenu.mss: `6 left;90 -;6 a;200 -;6 a;200 -;6 a;200 -` |
| link-cable messages | mainmenu.mss: `6 right;90 -;6 a;150 -;6 a;150 -;6 a` |
| staff roll + song credits | debugmenu.mss: `10 -;6 r;40 -;6 a;6000 -` (debug page 2 "Staff") |
| debug menu | debugmenu.mss |
| song editor ("Your Pitch") | debugmenu.mss: three downs + A |
Graphics screens and routes: docs/re/graphics.md and tools/routes/gfx_*.txt.
