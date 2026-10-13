# usage: py -3.13 -I dis.py <bank hex> <addr hex> [count]   (disassemble from a ROM bank at its window address; bank in window addr>>13)
import sys
sys.path.insert(0,r'C:\re\splatterhouse\scripts')
import shmach,m6809
def main():
    banks={}
    a=sys.argv[1:]
    # args: pairs window=bank ... then addr count ; e.g.  6=3b4 7=3ff c000 40
    win=[0]*8;win[7]=0x3ff
    rest=[]
    for x in a:
        if '=' in x:
            w,b=x.split('=');win[int(w)]=int(b,16)
        else: rest.append(x)
    addr=int(rest[0],16);n=int(rest[1]) if len(rest)>1 else 30
    def rd(ad):
        ad&=0xffff;b=win[ad>>13]
        return shmach.rombank(b)[ad&0x1fff] if 0x200<=b<0x400 else 0
    for _ in range(n):
        t,l=m6809.disasm(rd,addr)
        print('%04x  %-24s %s'%(addr,t,' '.join('%02x'%rd(addr+i) for i in range(l))))
        addr+=l
main()
