# Boot both CPUs, drop a coin on $302A (idle 0x18, pulse 0x08 = coin; other bits active high, e.g. test), press P1 start on $3026 (bit7), log game state.
import sys
sys.path.insert(0,r'C:\re\splatterhouse\scripts')
from shdual import *
m=dual();c=m.cpu;s=m.sub.cpu
dp=lambda o:m.ram[0x180][o]
IN={'p1':0x00,'svc':0x18}
m.io_read_val[(0x17f,0x1026)]=lambda:IN['p1']
m.io_read_val[(0x17f,0x102a)]=lambda:IN['svc']
last=None;F=int(sys.argv[1]);coin_at=110
for f in range(F):
    step_frames(m)
    st=(dp(0x2a),dp(0x2b),dp(0x2c))
    if st!=last: print('f',f,'2A/2B/2C',st,'credits 3E=%d FA=%02x'%(dp(0x3e),dp(0xfa)));last=st
    IN['svc']=0x08 if coin_at<=f<coin_at+4 else 0x18
    IN['p1']=0x80 if coin_at+30<=f<coin_at+34 else 0x00
print('end f',f,'3E',dp(0x3e))
