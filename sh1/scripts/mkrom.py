# Build the 1 MB ROM image the PC port builds in FUN_00408750 (PRG7 first, each file twice), and bank files.
import sys,os
R=r'C:\re\splatterhouse\files\DISK_1\ROMS\PRG%d'
buf=bytearray()
for i in range(7,-1,-1):
    d=open(R%i,'rb').read(); assert len(d)==0x10000
    buf+=d+d
assert len(buf)==0x100000
open(r'C:\re\splatterhouse\work\rom1mb.bin','wb').write(buf)
def bank_off(b):
    assert 0x200<=b<0x400
    k=b-0x200; outer=k>>6
    return 0xE0000-0x20000*outer+(k&15)*0x2000
if __name__=='__main__':
    for b in (0x3ff,0x377,0x3b4):
        o=bank_off(b); print(hex(b),hex(o),'PRG%d'%(7-(o>>17)),hex(o&0xffff))
        open(r'C:\re\splatterhouse\work\bank_%x.bin'%b,'wb').write(buf[o:o+0x2000])

def bank(b):
    o=bank_off(b); return bytes(buf[o:o+0x2000])
