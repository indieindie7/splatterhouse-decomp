# usage: py -3.13 -I dis2.py [w=bank ...] <start hex> <end hex|count> ; default window map = gameplay (3=3f9 4=3b1 5=3fd 6=3fe 7=3ff); 'x' prefix on 2nd arg = hex dump of bytes
import sys
sys.path.insert(0,r'C:\re\splatterhouse\scripts')
import shmach,m6809
win=[0,0,0,0x3f9,0x3b1,0x3fd,0x3fe,0x3ff]
rest=[]
for x in sys.argv[1:]:
    if '=' in x: w,b=x.split('=');win[int(w)]=int(b,16)
    else: rest.append(x)
def rd(ad):
    ad&=0xffff;b=win[ad>>13]
    return shmach.rombank(b)[ad&0x1fff] if 0x200<=b<0x400 else 0
a=int(rest[0],16);e=rest[1] if len(rest)>1 else '40'
if e[0]=='x':
    end=int(e[1:],16)
    while a<end:
        print('%04x: '%a+' '.join('%02x'%rd(a+i) for i in range(min(16,end-a)))); a+=16
    sys.exit()
end=int(e,16) if len(e)>2 else None;n=0
while True:
    if end is not None and a>=end: break
    if end is None and n>=int(e): break
    t,l=m6809.disasm(rd,a)
    print('%04x  %-26s %s'%(a,t,' '.join('%02x'%rd(a+i) for i in range(l))));a+=l;n+=1
