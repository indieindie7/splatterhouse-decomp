# Per-frame trace of P1 from the round-1 save. usage: p6_trace.py "<sched>" frames out.csv
# sched = "start-end:hex,..."  e.g. "0-60:02,5-9:20" (inputs OR-ed on port $3026)
import sys
sys.path.insert(0,r'C:\re\splatterhouse\scripts')
from shdual import *
def s16(v): return v-0x10000 if v&0x8000 else v
sched=[];F=int(sys.argv[2])
for part in sys.argv[1].split(','):
    r,v=part.split(':');a,b=r.split('-');sched.append((int(a),int(b),int(v,16)))
m=load(r'C:\re\splatterhouse\work\p6\round1.pkl');IN=game_inputs(m);k=m.ram[0x180]
out=open(sys.argv[3],'w');out.write('f,in,act,st,anim,vx,vy,x,y,z,hp,inv,e_active\n')
P=0x11d
for f in range(F):
    IN['p1']=0
    for a,b,v in sched:
        if a<=f<b: IN['p1']|=v
    step_frames(m)
    g=lambda o:k[P+o]; w=lambda o:k[P+o]<<8|k[P+o+1]
    ne=sum(1 for i in range(32) if k[0x19d+i*0x40])
    out.write(','.join(map(str,[f,hex(IN['p1']),g(0),hex(g(4)),g(5),s16(w(0x0a))/256,s16(w(0x0e))/256,
        (w(0x13)*256+g(0x15))/256,(w(0x16)*256+g(0x18))/256,(w(0x19)*256+g(0x1b))/256,g(0x1c),g(1),ne]))+'\n')
