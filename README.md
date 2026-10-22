# Mermaid Melody Pichi Pichi Pitch English translation

Unofficial English fan translation of **Mermaid Melody Pichi Pichi Pitch** (Game Boy Advance, Konami, 2003): the source
text and tools that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block (lyrics, UI, credits): original Japanese and English. Translation fixes go here. |
| `gfx/` | Text drawn as pictures: English redraws (`gfx/en/`) and the screen dumps they were made from. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, font, graphics, lint, release. |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |

## Build your own patched ROM

Needs Python 3.12+ with Pillow, and your own dump of the Japanese game.

```sh
git clone https://github.com/minhnhattonthat/mermaid-melody-pichi-pichi-pitch-en
cd mermaid-melody-pichi-pichi-pitch-en
# copy your dump to: rom/Mermaid Melody - Pichi Pichi Pitch (Japan).gba
#   (16777216 bytes, SHA-1 4a0422acf0f22dd85f35a2e040adcfdf70dcc6ec; the build refuses any other dump, see rom.sha1)
python -X utf8 tools/build.py build                    # -> build/mmppp_en.gba
python -X utf8 tools/check.py                          # identity build + text lint
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Konami's and is included only so the
translation can be checked against it. Mermaid Melody Pichi Pichi Pitch is (c) Konami, Michiko Yokote, Pink Hanamori,
Kodansha; this project is not affiliated with them. Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
