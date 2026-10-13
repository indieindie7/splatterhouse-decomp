# Phase 6: try to get from attract into gameplay. Logs DP $2A/$2B/$2C changes.
import sys
sys.path.insert(0,r'C:\re\splatterhouse\scripts')
from shrun import *
m=boot();c=m.cpu
def dp(o): return m.read_logical(((c.DP<<8)|o)&0xffff)
def setdp(o,v): m.wr(((c.DP<<8)|o)&0xffff,v)
last=None;steps=0;credit=False
N=int(sys.argv[1]) if len(sys.argv)>1 else 3_000_000
while steps<N:
    run(m,2000);steps+=2000
    st=(dp(0x2a),dp(0x2b),dp(0x2c))
    if st!=last: print(steps,'DP=%02x'%c.DP,'2A/2B/2C=',st,'PC=%04x'%c.PC);last=st
    if st[0]==1 and st[1]==2 and not credit:
        setdp(0x3e,1);credit=True;print('  credit planted')
    if credit: setdp(0xfa,dp(0xfa)|0x80)
print('end PC=%04x'%c.PC, 'wins',[hex(w) for w in m.win])
