# Boot helper: builds Mach with key-chip stubs, runs frames. Usage: from shrun import *
import sys
sys.path.insert(0,r'C:\re\splatterhouse\scripts')
import shmach
def boot():
    m=shmach.Mach()
    m.io_read_val[(0x17f,0x1000)]=0xa6
    st=[0]
    def tog():
        st[0]=(st[0]+1)&0xff;return st[0] or 1
    m.io_read_val[(0x17f,0x100f)]=tog
    for o in (0x103c,0x102f,0x1030,0x103e,0x103f,0x1040,0x1038): m.io_read_val[(0x17f,o)]=0
    m.n=0
    for o in (0x36,0x3f): m.io_read_val[(0x17c,o)]=0xb5   # sub-CPU 'alive' markers (shared RAM bank 0x17C)
    return m
def run(m,N,irq_every=6000,until=None,stop_pc=None):
    c=m.cpu;n=0
    while n<N:
        m.n+=1;n+=1
        if m.n%irq_every==irq_every-1 and not c.CC&0x10: c.irq()
        if c.PC==0xe054: m.ram[0x180][6]=0   # stand-in for sub CPU handshake
        c.step()
        if stop_pc is not None and c.PC==stop_pc: return True
        if until and until(m): return True
    return False
