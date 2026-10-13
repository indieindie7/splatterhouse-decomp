# usage: py -3.13 -I dis6000.py <start hex> [<end hex>|count]   disassemble work\game_6000.bin (base 0x6000)
import sys
sys.path.insert(0,r'C:\re\splatterhouse\scripts')
import m6809
img=open(r'C:\re\splatterhouse\work\game_6000.bin','rb').read()
rd=lambda a: img[(a&0xffff)-0x6000] if 0x6000<=(a&0xffff)<0x6000+len(img) else 0
a=int(sys.argv[1],16); e=sys.argv[2] if len(sys.argv)>2 else '40'
end=int(e,16) if len(e)>2 else None
n=0
while True:
    if end is not None and a>=end: break
    if end is None and n>=int(e): break
    t,l=m6809.disasm(rd,a)
    print('%04x  %-26s %s'%(a,t,' '.join('%02x'%rd(a+i) for i in range(l))))
    a+=l;n+=1
