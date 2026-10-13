# Splatterhouse PC (ISO) recon - 2026-10-10
Source: the CD image of the PC release (bin + cue). Nothing from the image was executed.

## Image
- CUE: one track, TRACK 01 MODE1/2352. 78962 sectors, 186 MB. **0 audio tracks.**
- Volume label SPLATTER_HOUSE. Japanese release (HELP/*.HTM are Shift-JIS, FrontPage 4).
- 7-Zip misreads the .bin as a CAB (embedded DirectX cab) and extracts junk - do NOT use it.
  Used scripts\iso_extract.py (2352->2048 strip + ISO9660 walk). Output: files\ (218 files); listing in scripts\listing.txt.

## Layout
- AUTORUN.INF, CDAUTO~1.EXE (autorun launcher), ICON1.ICO
- DIRECT~1\  DirectX 8-ish redistributable (DXSETUP.EXE, *.CAB, DSETUP*.DLL). Ignore.
- DISK_1\
  - SPLATTER.EXE (196 KB) - the game
  - DLL6809.DLL (90 KB) - 6809 CPU emulator core, imports only KERNEL32
  - SETUP.EXE, INSTMSIA/W.EXE, SPLATTER.MSI (5.2 MB, OLE2 installer) - install only
  - SPLATTER.INI (fullscreen/window/frameskip/attractsound, keys as DirectInput scancodes, 5 buttons), SETUP.INI
  - USERRANK.DAT (64 B, high-score table: 8-byte records, "..." initials)
  - ROMS\ PRG0-PRG7 (8 x 64 KB), CHR.DAT 768 KB, CHR_MASK.BIN 128 KB, OBJ.DAT 2 MB
  - SOUND\ FM01..FM3F.WAV (114 files, ~133 MB total, RIFF PCM 8-bit mono 22050 Hz) + 4 BMPs
  - HELP\ 13 .HTM, 53 .JPG (manual: CHARA, ITEM, GAME, PLAY, CONFIG1-3...)

## Executables
| file | type | linker | imports |
|---|---|---|---|
| SPLATTER.EXE | PE32 GUI x86, ts 2003-09-08 | MSVC 6.0 (link 6.0, VC runtime strings) | KERNEL32 USER32 GDI32 SHELL32 DSOUND WINMM DINPUT IMM32 DLL6809 |
| DLL6809.DLL | PE32 DLL x86, ts 2003-02-05 | MSVC 6.0 | KERNEL32 |
| CDAUTO~1.EXE / SETUP.EXE / INSTMSI*.EXE / DXSETUP.EXE | PE32 installers | MSVC 5/6 | std Win32 |
No NE/LE/DOS4GW. Not Watcom/Borland.
SPLATTER.EXE sections: .text 0x115ce, .rdata, .data 0x561d, .rsrc 0x15d28. Uses GetPrivateProfileInt for INI, DirectSound/DirectInput(old DINPUT.dll)/GDI (software blit).

## What it is (inference)
A Windows emulator-style port of the 1988 Namco System 1 arcade game: x86 shell (SPLATTER.EXE) drives
a 6809 core (DLL6809) over the ROM dumps in ROMS\. Sound is pre-rendered WAVs (FMxx) rather than emulated chips.
Game mechanics therefore live in the arcade program ROMs (6809 code, plus possibly 68000 - arcade original had a 68000 main CPU; check which PRGs hold what), not in the x86 code.

## Data file format guesses (headers/entropy only, not verified)
- PRG0/PRG1: monotonic byte-pair ramps (0000,0001,0002.. / 0100..) - lookup/index tables.
- PRG2: dense non-repeating bytes (starts 44 3E 44 D5..) - likely 6809/68000 code or compressed data.
- PRG3: 16-bit pairs like 01 02 1B EB / 1C 5C - tilemap/scene or script tables.
- PRG4: 3-byte-ish repeating groups, small values - sprite/animation tables or palette.
- PRG5: ascending 16-bit big-endian pointers (60 6E, 61 76, 62 3A..) at stride ~0x62 - pointer table into 0x6xxx address space (6809 map).
- PRG6: 0x10000/n reciprocal table (0000 0000 8000 5555 4000 3333 2AAA..) - fixed-point divide LUT.
- PRG7: rising 60C0,60C8,60D0.. - address/offset table.
- CHR.DAT: one pixel per byte, values 0/1 in 8x8 tile layout (expanded 1bpp-ish/4-colour tiles).
- CHR_MASK.BIN: 8-byte-per-glyph 1bpp 8x8 font (ASCII-like: "0 1 2 3 .." glyphs).
- OBJ.DAT: 2 MB, one pixel per byte (0x0F = transparent/background fill, 4bpp values) - sprite graphics. Assets: we do not ship these.
- WAV: standard RIFF PCM; BMPs are UI art.

## Ghidra
- Installed: C:\Users\john\Documents\Tools\ghidra\ghidra_12.1.4_PUBLIC
  - GUI: ...\ghidraRun.bat ; headless: ...\support\analyzeHeadless.bat
  - wrappers (set bundled JDK 21): C:\Users\john\Documents\Tools\ghidra.bat, ghidra-headless.bat; ghidra-bridge dir alongside.
- Nothing imported yet.

## Suggested next steps
1. Import SPLATTER.EXE + DLL6809.DLL (x86 32 LE) in a new project outside files\.
2. Find how SPLATTER.EXE maps PRG0-7 into 6809 space (look for ReadFile of "ROMS\PRGn" paths and DLL6809 exports).
3. Disassemble PRG code as 6809 (Ghidra has a 6809 processor module) to get player/enemy state machines.
4. Cross-check against MAME namcos1 splatter driver notes (public docs) for memory map.
