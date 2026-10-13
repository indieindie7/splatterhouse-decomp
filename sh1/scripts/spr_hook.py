import sys,collections
sys.path.insert(0,r'C:\re\splatterhouse\scripts')
from shrun import *
m=boot()
c=collections.Counter();off=collections.Counter()
def h(b,o,v):
    if b==0x173: c[m.cpu.PC]+=1; off[o>>8]+=1
m.hook_wr=h
for st in (None,0,1,2,3,4,5):
    if st is not None: m.ram[0x180][0x2a]=st
    run(m,2000000)
    print(st,hex(m.cpu.PC),dict(m.ram[0x180][0x2a:0x2c] and {'2a':m.ram[0x180][0x2a],'2b':m.ram[0x180][0x2b]}),len(c))
print(c.most_common(10)); print(sorted(off.items()))
