# Phase 6: main + sub CPU together (own code). Both Mach objects share one RAM dict, so banks 0x180-0x183
# (and video banks) are common. Sub starts at its real reset E00B with window 7 = bank 0x377.
import sys,collections
sys.path.insert(0,r'C:\re\splatterhouse\scripts')
import shmach
from shrun import boot
def dual(irq_every=6000):
    m=boot()
    s=shmach.Mach(); s.ram=m.ram
    s.writes_log=collections.deque(maxlen=64); m.writes_log=collections.deque(maxlen=64)
    s.win[7]=0x377; s.cpu.PC=0xe00b
    m.sub=s; m.irq_every=irq_every; m.frames=0
    return m
def step_frames(m,nf=1,hook=None):
    c=m.cpu;sc=m.sub.cpu
    for _ in range(nf):
        for i in range(m.irq_every):
            c.step(); sc.step()
            if hook and hook(m): return True
        m.frames+=1
        if not c.CC&0x10: c.irq()
        if not sc.CC&0x10: sc.irq()
    return False
REGS=('A','B','DP','X','Y','U','S','PC','CC')
def save(m,path):
    import pickle
    st={'ram':{b:bytes(v) for b,v in m.ram.items()},'frames':m.frames,'n':m.n}
    for tag,x in (('m',m),('s',m.sub)):
        st[tag]={'regs':{r:getattr(x.cpu,r) for r in REGS},'win':list(x.win),'latch':list(x.latch)}
    pickle.dump(st,open(path,'wb'))
def load(path):
    import pickle
    st=pickle.load(open(path,'rb'));m=dual()
    for b,v in st['ram'].items(): m.ram[b]=bytearray(v)
    m.frames=st['frames'];m.n=st['n']
    for tag,x in (('m',m),('s',m.sub)):
        for r,v in st[tag]['regs'].items(): setattr(x.cpu,r,v)
        x.win=st[tag]['win'];x.latch=st[tag]['latch']
    return m
def game_inputs(m):
    """Wire P1 port $3026 and coin port $302A to m.IN; returns dict to set."""
    m.IN={'p1':0,'svc':0x18}
    m.io_read_val[(0x17f,0x1026)]=lambda:m.IN['p1']
    m.io_read_val[(0x17f,0x102a)]=lambda:m.IN['svc']
    return m.IN
