import sys,pickle
sys.path.insert(0,r'C:\re\splatterhouse\scripts')
from shrun import *
st=int(sys.argv[1])
m=boot()
run(m,3000000)
print('booted',hex(m.cpu.PC),m.ram[0x180][0x2a],m.ram[0x180][0x2b])
cnt={}
def h(b,o,v):
    if 0x170<=b<=0x172 and v: cnt[(b,o)]=v
m.hook_wr=h
m.ram[0x180][0x2a]=st
for i in range(30):
    run(m,300000)
    print(i,len(cnt),hex(m.cpu.PC),m.ram[0x180][0x2a],m.ram[0x180][0x2b],[hex(m.win[w]) for w in (2,3)])
pickle.dump({b:bytes(m.ram[b]) for b in (0x170,0x171,0x172)},open(r'C:\re\splatterhouse\work\palram%d.pkl'%st,'wb'))
