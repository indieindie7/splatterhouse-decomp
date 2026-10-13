# Splatterhouse 2 + 3 (Sega Genesis) decompile notes

Research only, non-commercial. Never publish ROMs, bins, C dumps or the Ghidra db. No leaked source.
Goal (user 10-13): "lets do a decomp of splatterhouse 1 2 and 3 we have and send those to goobichat"
(Splatterhouse 1 = the PC/arcade 6809 decompile in C:\re\splatterhouse, done 10-10.)

## Layout
- rom/sh2.bin = the US cartridge dump of Splatterhouse 2, 1048576 bytes,
  header "SPLATTER HOUSE 2", GM T-14076 -00, reset 0x200, rom end 0xfffff.
- rom/sh3.bin = the US cartridge dump of Splatterhouse 3, 2097152 bytes,
  header "SPLATTER HOUSE 3", GM T-14086 -00, reset 0x200, rom end 0x1fffff.
  (header checksums do not match a plain word sum from 0x200; not important.)
- ghidra\ = project SplatGen, programs sh2.bin / sh3.bin (68000 BE, base 0).
- ghidra\scripts: GenMap.java (Genesis map + 64 vectors), Cs* copied from CyberSled (CsPtrFuncs scans to the ROM end),
  shrun.sh <abs log> <headless args> = runner. Shared Amok scripts: C:/Users/john/Documents/Amok/ghidra/scripts
  (ApplyNames, ExportFuncInfo, DeleteFunctions). Method = skill cybersled-re.

## Log
- 10-13: set up, ROMs copied, scripts written. Next: import both programs with -preScript GenMap.java.
- 10-13 import: `shrun.sh <log> -import rom/<p>.bin -processor 68000:BE:32:default -loader BinaryLoader -preScript GenMap.java`.
  Vectors: sh2 reset 0x200, VBlank 0x460, HBlank 0x498, other IRQs 0x502; sh3 reset 0x200, VBlank 0x424, HBlank 0x454, other 0x456.
- Code range (abs jsr/jmp targets): sh2 0x200..~0x20000, sh3 0x200..~0x30000, both also call 0x60000/0x60004/0x6000c (a module at 0x60000).
- Discovery: CsCoverage pseudo + CsOrphans create (7 rounds), CsPtrFuncs (targets kept only when a site is < code end;
  work/ptr_<p>.txt, copied to ghidra/ptr_<p>.txt and applied), CsOrphans createref. Result: sh2 422 functions, sh3 840.
- Dumps ghidra/decomp_<p>.c (local only): sh2 12365 lines, sh3 32307 lines. Round 1 naming: 8 Sonnet agents,
  chunks work/r1_<p>_<k>.c, prompt ghidra/scripts/r1_prompt.txt, verdicts work/v1_<p>_<k>.txt.
- 10-13 round 1 applied: v1check.py (hand optional) -> DeleteFunctions bogus_<p>.txt (sh2 10, sh3 22), ApplyNames hand_<p>.txt.
  sh2 412 functions, sh3 818, 0 FUN_ in both. Round 2 (2 Sonnet agents) re-checked the GUESS names: work/v2_<p>.txt,
  merged by scripts/v2merge.py (sh2 3 renames, 29 GUESS left; sh3 4 renames, 13 GUESS left). Dumps regenerated.
- Key entry points: sh3 player_state_update_main 0xb660, script_op_* behaviour-script interpreter (61 ops), sound driver 0x60000.
- Repo: Documents/github/splatterhouse-decomp (sh1/ + sh2-sh3/), funcinfo published without S (string) lines.
