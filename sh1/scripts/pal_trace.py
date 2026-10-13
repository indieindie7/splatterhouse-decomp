import sys,collections
sys.path.insert(0,r'C:\re\splatterhouse\scripts')
from shrun import *
m=boot(); run(m,3000000)
m.ram[0x180][0x2a]=int(sys.argv[1]); m.ram[0x180][0x2b]=0
c=collections.Counter()
for i in range(200000):
    run(m,10)
    c[m.cpu.PC]+=1
print(c.most_common(12)); print([hex(m.ram[0x180][i]) for i in (0x2a,0x2b,0x41,0x43,0x02,0x06)])
