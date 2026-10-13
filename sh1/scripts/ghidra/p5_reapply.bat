@echo off
rem Re-apply names.txt (overlays already exist) and re-dump decompiled C into decomp\.
set R=C:\re\splatterhouse
call C:\Users\john\Documents\Tools\ghidra-headless.bat %R%\ghidra SH -process game_6000.bin -noanalysis -scriptPath %R%\scripts\ghidra -postScript ApplySH.java %R%\names.txt
call C:\Users\john\Documents\Tools\ghidra-headless.bat %R%\ghidra SH -process game_6000.bin -noanalysis -readOnly -scriptPath %R%\scripts\ghidra -postScript DumpAll.java %R%\decomp
