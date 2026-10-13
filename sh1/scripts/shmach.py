# Namco System 1 main-CPU harness for Splatterhouse (own code). Emulates main 6809 only; sub CPU not run.
import sys,collections
sys.path.insert(0,r'C:\re\splatterhouse\scripts')
import m6809
ROM=open(r'C:\re\splatterhouse\work\rom1mb.bin','rb').read()
def bank_off(b):
    k=b-0x200;return 0xE0000-0x20000*(k>>6)+(k&15)*0x2000
def rombank(b): o=bank_off(b);return ROM[o:o+0x2000]
class Mach:
    def __init__(s):
        s.io_read_val={};s.rombanks={};s.win=[0]*8;s.latch=[0]*8
        s.ram=collections.defaultdict(lambda:bytearray(0x2000))
        s.io_log=collections.Counter();s.bank_writes=collections.Counter()
        s.window_hist=collections.defaultdict(collections.Counter)  # window -> bank -> count of writes
        s.cpu=m6809.CPU(s.rd,s.wr)
        s.win[7]=0x3ff
        s.cpu.PC=s.cpu.rd16(0xfffe)
        s.trace_io=True
        s.io_read_val={}      # (bank,off)->value override
        s.writes_log=[]       # control writes F000+
        s.hook_wr=None
        s.rombanks={}
    def bankdata(s,b):
        if 0x200<=b<0x400:
            d=s.rombanks.get(b)
            if d is None: d=s.rombanks[b]=rombank(b)
            return d,False
        return s.ram[b],True
    def rd(s,a):
        w=a>>13;b=s.win[w]
        if b==0x17f or b==0x173 or (b,a&0x1fff) in s.io_read_val:
            s.io_log[('R',b,a&0x1fff)]+=1
            v=s.io_read_val.get((b,a&0x1fff))
            if v is not None:return v() if callable(v) else v
            if b==0x17f and 0x1000<=(a&0x1fff)<0x1040: return 0x00
        d,_=s.bankdata(b)
        return d[a&0x1fff]
    def wr(s,a,v):
        w=a>>13
        if w==7 and a>=0xe000:
            if a<0xf000:
                win=(a>>9)&7
                if a&1: s.win[win]=(v&0xff)|s.latch[win];s.window_hist[win][s.win[win]]+=1
                else: s.latch[win]=(v&3)<<8
                return
            s.writes_log.append((a,v));return
        b=s.win[w]
        if 0x200<=b<0x400: return
        if b==0x17f: s.io_log[('W',b,a&0x1fff)]+=1
        s.ram[b][a&0x1fff]=v
        if s.hook_wr: s.hook_wr(b,a&0x1fff,v)
    def read_logical(s,a):  # peek without logging
        d,_=s.bankdata(s.win[a>>13]);return d[a&0x1fff]
    def dis(s,a,n=1):
        out=[]
        for i in range(n):
            t,l=m6809.disasm(s.read_logical_wrap,a);out.append('%04x  %s'%(a,t));a+=l
        return out
    def read_logical_wrap(s,a): return s.read_logical(a&0xffff)
