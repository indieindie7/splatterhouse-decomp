#!/bin/bash
# headless Ghidra on the SplatGen project (same wrapper call as CyberSled csrun.sh).
# usage: shrun.sh <abs log> [headless args after project name]
log="$1"; shift
cd /c/Users/john/Documents/SplatterhouseGen/ghidra || exit 1
cmd //c "C:\Users\john\Documents\Tools\ghidra-headless.bat C:\Users\john\Documents\SplatterhouseGen\ghidra SplatGen $*" > "$log" 2>&1
tail -3 "$log"
