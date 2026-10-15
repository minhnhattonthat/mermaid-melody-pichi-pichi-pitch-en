Mermaid Melody Pichi Pichi Pitch (GBA) - English translation patch v{v}
=====================================================================

Unofficial fan translation of Konami's 2003 Game Boy Advance rhythm game
"Mermaid Melody Pichi Pichi Pitch" (マーメイドメロディー ぴちぴちピッチ).
No ROM is included and none will be provided. Use your own dump.

What is translated
- All song lyrics in the karaoke bar (new proportional English font).
- Menus, buttons, message bars, song plates, results and other screens drawn as pictures.
- Link-cable messages, name entry (Latin letters), profile, save messages.
- Staff roll and song credits.
Names follow the official English localisation (Lucia, Hanon, Rina, Kaito, Hippo).

Base ROM (No-Intro: Mermaid Melody - Pichi Pichi Pitch (Japan).gba)
  Size   {o[size]} bytes
  CRC32  {o[crc32]}
  MD5    {o[md5]}
  SHA-1  {o[sha1]}

Patched ROM (32 MiB; the patch expands the ROM to make room)
  CRC32  {p[crc32]}
  SHA-1  {p[sha1]}

How to patch
  Apply {patch} to the base ROM with Floating IPS (Flips), beat, or
  RomPatcher.js (https://www.marcrobledo.com/RomPatcher.js/). Patch SHA-1: {psha}

Notes
- Tested in MesenCE 2.2.1 (headless QA). Start from a cold boot, not from a savestate
  made with the Japanese ROM. Saves made with the Japanese version keep player names
  in Japanese character codes; enter the name again.
- Staff names of the Konami team were romanised from the game's font; a few readings
  may be wrong. Song credits were checked against the series discography.
- Lyrics are translations for meaning, not singable adaptations.
- Known issues:
  * The score unit is shortened to "pts" (only 16-32 px of room in the HUD and results).
  * Hippo's song maker holds one letter per note, so its default song is a short
    English adaptation (8 letters per line); Rina's name did not fit.
  * A few full-screen illustration cards show small tile artifacts around the new
    English logo where the picture shares tiles or colours.
  * One crowd-banner picture (resource #177) is still Japanese: no screen that
    shows it was found.
  * The "save data is damaged" screens and the "CLEAR!" banner were checked
    offline/in the sprite sheet but not seen during play.

Credits
  Translation, engine work and graphics: fan translation made with AI assistance
  (Claude, Anthropic) for the patch author. Original game (c) Konami; Mermaid Melody
  Pichi Pichi Pitch (c) Michiko Yokote, Pink Hanamori, Kodansha, We've, TV Aichi.
