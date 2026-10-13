# Splatterhouse 1, 2 and 3 reverse-engineering notes and symbols

Hand-named function maps, notes and tools for three Namco games:

- **Splatterhouse** (arcade, 1988, Namco System 1, Motorola 6809), studied through the 2003 PC port, which
  runs the arcade 6809 program in an emulator DLL;
- **Splatterhouse 2** (Sega Genesis, 1992, 68000);
- **Splatterhouse 3** (Sega Genesis, 1993, 68000).

Same method as [cybersled-decomp](https://github.com/indieindie7/cybersled-decomp) and
[scorcher-decomp](https://github.com/indieindie7/scorcher-decomp). Non-commercial, done for study and
preservation (and for the combat feel of a fan brawler).

## What is here

| Path | Content |
|---|---|
| `sh1/names.txt` | 1803 named 6809 functions plus 337 data labels (`0x<addr> func|data <name> <source> <comment>`, banked addresses as in NOTES) |
| `sh1/NOTES.md` | ROM layout inside the PC port, banking, frame flow, object table, player state machine, the hit pipeline, measured movement and combat numbers, enemy identities, rounds |
| `sh1/RECON.md` | first look at the PC CD: file list, compilers, how the port is built |
| `sh1/scripts/` | a 6809 disassembler (`m6809.py`), a small 6809 machine used to run the boot and measure values (`shmach.py`, `shrun.py`, `p6_*.py`), layout/sprite-sheet helpers, Ghidra scripts |
| `sh2-sh3/NOTES.md` | Genesis project log: import, discovery pipeline, naming rounds, counts |
| `sh2-sh3/hand_sh2.txt`, `hand_sh3.txt` | hand-named functions (`0x<addr> func <name> hand <comment>`; `GUESS` marks weak names) |
| `sh2-sh3/ptr_<p>.txt` | names for functions found through ROM pointer tables |
| `sh2-sh3/bogus_<p>.txt` | false function starts that were deleted |
| `sh2-sh3/funcinfo_<p>.tsv` | per-function export: address, name, size, callees, string references |
| `sh2-sh3/scripts/` | `GenMap.java` (Genesis memory map + 68000 vectors), coverage / orphan / pointer-table discovery, decompile dump, the naming prompt and the verdict checker |

`ApplyNames.java`, `ExportFuncInfo.java` and `DeleteFunctions.java` are in
[amok-decomp](https://github.com/indieindie7/amok-decomp)'s `ghidra/scripts`.

## What is NOT here

No game files: no ROMs, no program images, no sprites or sounds, no game strings, no decompiled C output and
no Ghidra project database (which embeds the binaries). You need your own copies of the games.

## Reproducing the Genesis projects

1. Ghidra 12.1.4: import the cartridge ROM as `68000:BE:32:default` with the BinaryLoader at base 0 and
   `-preScript GenMap.java`.
2. Run `DeleteFunctions.java` with the `bogus_<p>.txt` addresses, then `ApplyNames.java` with `ptr_<p>.txt`
   and `hand_<p>.txt` in `hand` mode (it creates missing functions).
3. `CsDumpAll.java <out.c>` writes the whole decompile.

Starting points: SH3 `player_state_update_main` (0xb660), the behaviour-script interpreter (`script_op_*`),
the enemy AI groups (`enemy_*`), the sound driver at 0x60000; SH1 player update `B479` and the hit pipeline
in `sh1/NOTES.md` ("Phase 3: combat").

## License

The notes, names and scripts are MIT (see `LICENSE`). Splatterhouse is a trademark of Bandai Namco; this
project has no affiliation with it and contains none of its code or data.
