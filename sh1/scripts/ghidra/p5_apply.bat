@echo off
rem Phase 5: add bank overlays (3fa 3fb 3fc at 8000, 3b4 at C000, 377 at E000) and apply names.txt. Run once (overlays fail if they exist).
set R=C:\re\splatterhouse
call C:\Users\john\Documents\Tools\ghidra-headless.bat %R%\ghidra SH -process game_6000.bin -noanalysis -scriptPath %R%\scripts\ghidra ^
 -postScript AddBlock.java b3fa 0x8000 %R%\work\p5\bank_3fa.bin overlay ^
 -postScript AddBlock.java b3fb 0x8000 %R%\work\p5\bank_3fb.bin overlay ^
 -postScript AddBlock.java b3fc 0x8000 %R%\work\p5\bank_3fc.bin overlay ^
 -postScript AddBlock.java b3b4 0xC000 %R%\work\bank_3b4.bin overlay ^
 -postScript AddBlock.java b377 0xE000 %R%\work\bank_377.bin overlay ^
 -postScript ApplySH.java %R%\names.txt
