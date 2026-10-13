import sys
sys.path.insert(0,r'C:\re\splatterhouse\scripts')
from shdual import *
m=dual();c=m.cpu;s=m.sub.cpu
dp=lambda o:m.ram[0x180][o]
last=None
for f in range(int(sys.argv[1])):
    step_frames(m)
    st=(dp(0x2a),dp(0x2b),dp(0x2c))
    if st!=last or f%50==0: print('f',f,'2A/2B/2C',st,'main PC %04x sub PC %04x'%(c.PC,s.PC),'sub wins',[hex(w) for w in m.sub.win]);last=st
