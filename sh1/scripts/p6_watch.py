# Coin+start, then print P1 struct ($011D, 0x40 bytes) and active enemy slots ($019D x32, stride 0x40) every N frames.
import sys,time
sys.path.insert(0,r'C:\re\splatterhouse\scripts')
from shdual import *
m=dual();k=m.ram[0x180]
IN={'p1':0,'svc':0x18}
m.io_read_val[(0x17f,0x1026)]=lambda:IN['p1']
m.io_read_val[(0x17f,0x102a)]=lambda:IN['svc']
F=int(sys.argv[1]);EV=int(sys.argv[2]);t=time.time()
for f in range(F):
    IN['svc']=0x08 if 110<=f<114 else 0x18
    IN['p1']=0x80 if 140<=f<144 else (0x10 if 300<=f<304 else 0)
    step_frames(m)
    if f%EV==0 and k[0x2a]==3:
        p=k[0x11d:0x15d]
        en=[(i,hex(k[0x19d+i*0x40+9])) for i in range(32) if k[0x19d+i*0x40]]
        print('f',f,'2C',k[0x2c],'P1',p[:0x20].hex(' '),'| en',en)
print('fps %.1f'%(F/(time.time()-t)))
