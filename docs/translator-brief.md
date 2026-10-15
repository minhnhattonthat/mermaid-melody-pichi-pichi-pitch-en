# Translator brief - Mermaid Melody Pichi Pichi Pitch (GBA, Konami 2003)

You translate part of the Japanese text of this rhythm/karaoke game into English for a fan patch. Players dance and
sing along with the anime's mermaid idols Lucia, Hanon and Rina; the text is mostly song lyrics shown one line at a
time in a karaoke bar, plus menus, link-cable messages, a profile screen and the staff roll. Audience: young fans;
tone warm and light. Work only on the batch named in your dispatch. Do all translation yourself; no subagents.

## Read first
1. `docs/style-reference.md` - approved example pairs and lyric rules. Match this voice.
2. `build/terms_<batch>.txt` - binding glossary rows for this batch (full table and rulings: `glossary.md`).

## Input: `work/tl/<batch>.tsv`
`id<TAB>box<TAB>limit<TAB>Japanese`. ` / ` separates lines of one entry (keep the same number of lines unless the
limit says otherwise). box: `lyric` = one karaoke line (max 168 px), `fit` = UI text that must not get wider than the
Japanese line (limit gives px per line), `credits` = staff roll (232 px per line). Entries are in game order: lyric
lines of one song follow each other, use neighbours for context.
Width: the English font is proportional, about 5-6 px per character (space 3 px, i/l/!/. 2-3 px, m/w/M/W 6 px).
Check any line with `python -X utf8 tools/font_en.py "your line"` (prints px per line).

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Plain ASCII plus these extras when the Japanese has them:
♪ ♥ ★ … é ×. Use ` / ` between lines exactly where the Japanese has them. No tabs, no Japanese, no fullwidth.

## Control codes - copy every one exactly, in the same order, at the matching place
- `[..]` hex groups (e.g. `[FA 11 01]`, `[FC 82]`, `[FB E0 36 00 03 C2]`, `[F6 01]`), `{@}`, `{A}`.
- `[FB ...]` prints a number; `[F6 01]` prints the player's name. Write "Score: [FB ...]" style, never a suffix glued
  on the number ("1th"), never "a/an" right before the name.
- `[FC xx]` positions the pen; `[FA 11 xx]` moves down; Japanese full-width spaces at a line start are layout
  (centering): replace them with ordinary spaces so the English is roughly centred the same way (the line px budget
  includes them).

## Validate
Run `python -X utf8 tools/batches.py check <batch>` from the repo root and fix every reported id until it prints OK.

## Style
- Faithful: keep the meaning and order of ideas; adapt idiom, not meaning. No added details, no summaries.
- Lyrics: natural, poetic, short English lines; one Japanese line -> one English line (they are timed). Keep the
  English words the original already has ("Dear My Songs", "Super Live", "Splash Dream", "Destiny", "Song for You").
  Rhyme is not required; rhythm and clarity are. Onomatopoeia/la-la lines stay as sounds ("La la la la").
- Names and terms exactly as in the glossary (Lucia, Hanon, Rina, Kaito, Hippo). Honorifics are dropped: ちゃん/くん
  after a name become nothing. Western name order.
- Staff names: romanise in Western order (given name first), modified Hepburn, no macrons ("Asumi Nakata").
- Punctuation: 「」 -> "...", … -> ..., ！ -> !, ？ -> ?, ～Promised Land～ -> ~Promised Land~.
- Never abbreviate to fit. If a line cannot fit without losing meaning, keep the meaning and report `LONG: id`.

## Consistency
Never edit `glossary.md`. For a recurring term not in it, pick a form, use it consistently, and report it.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
