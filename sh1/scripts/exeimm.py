import struct,sys
d=open(r'C:\re\splatterhouse\files\DISK_1\SPLATTER.EXE','rb').read()
# .text raw start: find via PE header quickly
import re
for val in (0x80000,0x7e000,0x5e000,0x2000,0x3ff,0x3b4,0x1ff,0x10000,0x20000,0x70000,0x60000,0x3f):
    offs=[m.start() for m in re.finditer(re.escape(struct.pack('<I',val)),d)]
    print(hex(val),len(offs),[hex(o) for o in offs[:12]])
