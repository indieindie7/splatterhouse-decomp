# Boot, coin, start, skip intro; save at round 1 gameplay -> work\p6\round1.pkl
import sys
sys.path.insert(0,r'C:\re\splatterhouse\scripts')
from shdual import *
m=dual();IN=game_inputs(m);k=m.ram[0x180]
for f in range(520):
    IN['svc']=0x08 if 110<=f<114 else 0x18
    IN['p1']=0x80 if 140<=f<144 else (0x10 if 300<=f<304 else 0)
    step_frames(m)
print('2A/2B/2C',k[0x2a],k[0x2b],k[0x2c],'65',k[0x65])
save(m,r'C:\re\splatterhouse\work\p6\round1.pkl')
