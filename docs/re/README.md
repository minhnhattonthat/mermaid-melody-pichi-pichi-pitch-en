# RE notes: Mermaid Melody Pichi Pichi Pitch (GBA, Konami 2003, AGB-BMAJ)

Base ROM: `rom/Mermaid Melody - Pichi Pichi Pitch (Japan).gba`, 16 MiB, SHA-1 4a0422acf0f22dd85f35a2e040adcfdf70dcc6ec.
No earlier fan translation found (web search, 2026-10).

## Game
Rhythm game (dance/sing to arrows) with karaoke lyrics. No font-rendered dialogue was found: every Japanese
element seen so far is a pre-rendered compressed image (menus, buttons, message bars, results, lyrics lines).

## Memory map
- 0x000000-0x07FFFF code + data. 0x080000-0xC67D93 audio (PCM). 0xC67D94-0xFC0D96 graphics banks + palettes.
- IWRAM 0x03000000.. is copied from ROM 0xEB0D80-ish region (decompressor at IWRAM 0x03000BA4, ARM).

## Graphics codec (`tools/mmcomp.py`, verified against chunk end offsets)
Chunk = flag byte + commands; decodes to 0x800 (or 0x1000) bytes; resources are N consecutive chunks.
Wrapper: thumb 0x08000AE8(dst, src, size, add) returns end of chunk.

## Banks (`tools/banks.py`)
5-byte records {u32 ptr unaligned, u8 info}, data directly after the directory.
info: high nibble = chunks-1, bit2 = 0x1000-byte chunks, bit3 = dst addressing.
Loader 0x08001084(dst, bank, index, ...) -> 0x08000BF8 (ptr) / 0x08000C20 (info) / 0x08000C84.
Directories found (work/scan_dirs.py brute scan): 0x0273D0(2) 0xC67D94(210, main UI) 0xDD62A0(120, lyrics/anim?)
0xEB19E0(16) 0xEF4890(32) 0xF24461(32) 0xF5837F(32) 0xF8854F(28) 0xFC0830(2).
Gaps not yet explained: 0xD4EBF5-0xDD62A0, 0xE3BFF0-0xEB19E0 (pointer table 0x08E3C000..), 0xEB738B-0xEF4890,
0xFB413F-0xFC0830.

## Screens
- Main menu (state route tools/routes/mainmenu.txt): buttons = OBJ tiles from bank 0xC67D94 idx 0x48 -> 0x06010000;
  message bar = OBJ, image decompressed into IWRAM 0x03006900 then DMA to EWRAM 0x02002C80 then VRAM 0x06017000.
- Play: lyrics line on BG0 tiles 0x6C.., buffer EWRAM 0x020041AC (0xB00 bytes), recoloured for the karaoke wipe
  by 0x0800B3A8 using table 0x08EB7E1C; lyric images come from chunks around 0xDDB534 (bank 0xDD62A0).
