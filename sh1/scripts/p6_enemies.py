# Walk right from round1.pkl; log every active enemy slot per frame. usage: p6_enemies.py frames out.csv [hold_hex] [punch_from_frame: stop and punch every 24 f]
import sys
sys.path.insert(0,r'C:\re\splatterhouse\scripts')
from shdual import *
def s16(v): return v-0x10000 if v&0x8000 else v
F=int(sys.argv[1]);hold=int(sys.argv[3],16) if len(sys.argv)>3 else 1
m=load(r'C:\re\splatterhouse\work\p6\round1.pkl');IN=game_inputs(m);k=m.ram[0x180]
out=open(sys.argv[2],'w');out.write('f,slot,act,type,st,tmr,vx,vy,x,y,z,hp,px\n')
for f in range(F):
    IN['p1']=(hold if f<int(sys.argv[4] if len(sys.argv)>4 else 99999) else 0)|(0x10 if len(sys.argv)>4 and f>=int(sys.argv[4]) and f%24<3 else 0); step_frames(m)
    px=(k[0x130]<<8|k[0x131])
    for i in range(32):
        b=0x19d+i*0x40
        if not k[b]: continue
        g=lambda o:k[b+o]; w=lambda o:k[b+o]<<8|k[b+o+1]
        out.write(','.join(map(str,[f,i,g(0),g(9),hex(g(4)),g(5),s16(w(0x0a))/256,s16(w(0x0e))/256,
            (w(0x13)*256+g(0x15))/256,(w(0x16)*256+g(0x18))/256,(w(0x19)*256+g(0x1b))/256,g(0x1c),px]))+'\n')
