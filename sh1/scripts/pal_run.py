import sys
sys.path.insert(0,r'C:\re\splatterhouse\scripts')
from shrun import *
m=boot()
cnt={}
def h(b,o,v):
    if 0x170<=b<=0x172: cnt[(b,o)]=v
m.hook_wr=h
for i in range(40):
    run(m,500000)
    print(i,len(cnt),hex(m.cpu.PC),[hex(m.win[w]) for w in range(8)])
import pickle
pickle.dump({b:bytes(m.ram[b]) for b in (0x170,0x171,0x172) if b in m.ram},open(r'C:\re\splatterhouse\work\palram.pkl','wb'))
