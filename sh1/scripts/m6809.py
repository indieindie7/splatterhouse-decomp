# Table-driven 6809 disassembler + emulator core (own code). Bus supplied by caller.
UN={0:'NEG',3:'COM',4:'LSR',6:'ROR',7:'ASR',8:'LSL',9:'ROL',0xA:'DEC',0xC:'INC',0xD:'TST',0xE:'JMP',0xF:'CLR'}
BR=['BRA','BRN','BHI','BLS','BCC','BCS','BNE','BEQ','BVC','BVS','BPL','BMI','BGE','BLT','BGT','BLE']
AA=['SUBA','CMPA','SBCA','SUBD','ANDA','BITA','LDA','STA','EORA','ADCA','ORA','ADDA','CMPX','JSR','LDX','STX']
BB=['SUBB','CMPB','SBCB','ADDD','ANDB','BITB','LDB','STB','EORB','ADCB','ORB','ADDB','LDD','STD','LDU','STU']
W16={'SUBD','ADDD','CMPX','LDX','STX','LDD','STD','LDU','STU','CMPD','CMPY','LDY','STY','LDS','STS','CMPU','CMPS'}
def build():
    T={}
    for base,mode in((0x00,'dir'),(0x60,'idx'),(0x70,'ext')):
        for k,n in UN.items(): T[(0,base+k)]=(n,mode)
    for base in(0x40,0x50):
        r='A' if base==0x40 else 'B'
        for k,n in UN.items():
            if k!=0xE: T[(0,base+k)]=(n+r,'reg1')
    for i,n in enumerate(BR):
        T[(0,0x20+i)]=(n,'rel8'); T[(1,0x20+i)]=('L'+n,'rel16')
    T[(0,0x12)]=('NOP','inh');T[(0,0x13)]=('SYNC','inh');T[(0,0x16)]=('LBRA','rel16');T[(0,0x17)]=('LBSR','rel16')
    T[(0,0x19)]=('DAA','inh');T[(0,0x1A)]=('ORCC','imm8');T[(0,0x1C)]=('ANDCC','imm8');T[(0,0x1D)]=('SEX','inh')
    T[(0,0x1E)]=('EXG','reg');T[(0,0x1F)]=('TFR','reg')
    for o,n in((0x30,'LEAX'),(0x31,'LEAY'),(0x32,'LEAS'),(0x33,'LEAU')): T[(0,o)]=(n,'idx')
    T[(0,0x34)]=('PSHS','stk');T[(0,0x35)]=('PULS','stk');T[(0,0x36)]=('PSHU','stk');T[(0,0x37)]=('PULU','stk')
    for o,n in((0x39,'RTS'),(0x3A,'ABX'),(0x3B,'RTI'),(0x3C,'CWAI'),(0x3D,'MUL'),(0x3F,'SWI')): T[(0,o)]=(n,'inh')
    T[(1,0x3F)]=('SWI2','inh');T[(2,0x3F)]=('SWI3','inh')
    for hi,mode in((8,'imm'),(9,'dir'),(0xA,'idx'),(0xB,'ext')):
        for lo in range(16):
            for tab,base in((AA,0),(BB,0x40)):
                op=(hi<<4|lo)+base; n=tab[lo]
                if hi==8 and lo==0xD and base==0:
                    T[(0,op)]=('BSR','rel8'); continue
                if mode=='imm':
                    if n in('STA','STB','STD','STU','STX','JSR'): continue
                    if op in(0x8F,0xCF): continue
                    m='imm16' if n in W16 else 'imm8'
                else: m=mode
                T[(0,op)]=(n,m)
    for hi,mode in((8,'imm16'),(9,'dir'),(0xA,'idx'),(0xB,'ext')):
        for lo,n in {0x3:'CMPD',0xC:'CMPY',0xE:'LDY',0xF:'STY'}.items():
            if n=='STY' and mode=='imm16': continue
            T[(1,hi<<4|lo)]=(n,mode)
        for lo,n in {0x3:'CMPU',0xC:'CMPS'}.items(): T[(2,hi<<4|lo)]=(n,mode)
    for hi,mode in((0xC,'imm16'),(0xD,'dir'),(0xE,'idx'),(0xF,'ext')):
        T[(1,hi<<4|0xE)]=('LDS',mode)
        if mode!='imm16': T[(1,hi<<4|0xF)]=('STS',mode)
    return T
T=build()
REGN=['D','X','Y','U','S','PC','?','?','A','B','CC','DP','?','?','?','?']
class CPU:
    def __init__(s,rd,wr):
        s.rd=rd;s.wr=wr;s.A=s.B=s.DP=0;s.X=s.Y=s.U=s.S=s.PC=0;s.CC=0x50;s.cyc=0
    def rd16(s,a): return s.rd(a&0xffff)<<8|s.rd((a+1)&0xffff)
    def wr16(s,a,v): s.wr(a&0xffff,(v>>8)&0xff);s.wr((a+1)&0xffff,v&0xff)
    @property
    def D(s): return s.A<<8|s.B
    @D.setter
    def D(s,v): s.A=(v>>8)&0xff;s.B=v&0xff
    def f(s,m): return 1 if s.CC&m else 0
    def sf(s,m,c):
        if c: s.CC|=m
        else: s.CC&=~m&0xff
    def fetch(s): v=s.rd(s.PC);s.PC=(s.PC+1)&0xffff;return v
    def fetch16(s): v=s.rd16(s.PC);s.PC=(s.PC+2)&0xffff;return v
    def getreg(s,i):
        return {0:lambda:s.D,1:lambda:s.X,2:lambda:s.Y,3:lambda:s.U,4:lambda:s.S,5:lambda:s.PC,8:lambda:s.A,9:lambda:s.B,10:lambda:s.CC,11:lambda:s.DP}.get(i,lambda:0xff)()
    def setreg(s,i,v):
        if i==0:s.D=v
        elif i==1:s.X=v&0xffff
        elif i==2:s.Y=v&0xffff
        elif i==3:s.U=v&0xffff
        elif i==4:s.S=v&0xffff
        elif i==5:s.PC=v&0xffff
        elif i==8:s.A=v&0xff
        elif i==9:s.B=v&0xff
        elif i==10:s.CC=v&0xff
        elif i==11:s.DP=v&0xff
    def idx(s):
        pb=s.fetch()
        r='XYUS'[(pb>>5)&3]
        if not pb&0x80:
            o=pb&0x1f
            if o&0x10:o-=32
            return (getattr(s,r)+o)&0xffff
        t=pb&0xf;ind=pb&0x10
        b=getattr(s,r)
        if t==0: a=b;setattr(s,r,(b+1)&0xffff)
        elif t==1: a=b;setattr(s,r,(b+2)&0xffff)
        elif t==2: b=(b-1)&0xffff;setattr(s,r,b);a=b
        elif t==3: b=(b-2)&0xffff;setattr(s,r,b);a=b
        elif t==4: a=b
        elif t==5: a=b+(s.B-256 if s.B&0x80 else s.B)
        elif t==6: a=b+(s.A-256 if s.A&0x80 else s.A)
        elif t==8:
            o=s.fetch();a=b+(o-256 if o&0x80 else o)
        elif t==9:
            o=s.fetch16();a=b+(o-65536 if o&0x8000 else o)
        elif t==0xB: a=b+s.D
        elif t==0xC:
            o=s.fetch();a=s.PC+(o-256 if o&0x80 else o)
        elif t==0xD:
            o=s.fetch16();a=s.PC+(o-65536 if o&0x8000 else o)
        elif t==0xF: a=s.fetch16()
        else: raise Exception('bad idx %02x at %04x'%(pb,s.PC))
        a&=0xffff
        if ind: a=s.rd16(a)
        return a
    def push(s,stack,v,n=1):
        sp=getattr(s,stack)
        for i in range(n):
            sp=(sp-1)&0xffff;s.wr(sp,(v>>(8*i))&0xff)
        setattr(s,stack,sp)
    def pop(s,stack,n=1):
        sp=getattr(s,stack);v=0
        for i in range(n):
            v=(v<<8)|s.rd(sp);sp=(sp+1)&0xffff
        setattr(s,stack,sp);return v
    def pshs(s,st,mask):
        o='U' if st=='S' else 'S'
        if mask&0x80:s.push(st,s.PC,2)
        if mask&0x40:s.push(st,getattr(s,o),2)
        if mask&0x20:s.push(st,s.Y,2)
        if mask&0x10:s.push(st,s.X,2)
        if mask&0x08:s.push(st,s.DP)
        if mask&0x04:s.push(st,s.B)
        if mask&0x02:s.push(st,s.A)
        if mask&0x01:s.push(st,s.CC)
    def puls(s,st,mask):
        o='U' if st=='S' else 'S'
        if mask&0x01:s.CC=s.pop(st)
        if mask&0x02:s.A=s.pop(st)
        if mask&0x04:s.B=s.pop(st)
        if mask&0x08:s.DP=s.pop(st)
        if mask&0x10:s.X=s.pop(st,2)
        if mask&0x20:s.Y=s.pop(st,2)
        if mask&0x40:setattr(s,o,s.pop(st,2))
        if mask&0x80:s.PC=s.pop(st,2)
    def irq(s,vec=0xFFF8):
        s.CC|=0x80;s.pshs('S',0xff);s.CC|=0x50;s.PC=s.rd16(vec)
    def nz8(s,r):
        s.sf(8,r&0x80);s.sf(4,(r&0xff)==0)
    def nz16(s,r):
        s.sf(8,r&0x8000);s.sf(4,(r&0xffff)==0)
    def add8(s,a,b,c=0):
        r=a+b+c;s.sf(32,((a&15)+(b&15)+c)>15);s.sf(1,r>0xff)
        s.sf(2,(~(a^b)&(a^r))&0x80);s.nz8(r);return r&0xff
    def sub8(s,a,b,c=0):
        r=a-b-c;s.sf(1,r<0);s.sf(2,((a^b)&(a^r))&0x80);s.nz8(r);return r&0xff
    def add16(s,a,b):
        r=a+b;s.sf(1,r>0xffff);s.sf(2,(~(a^b)&(a^r))&0x8000);s.nz16(r);return r&0xffff
    def sub16(s,a,b):
        r=a-b;s.sf(1,r<0);s.sf(2,((a^b)&(a^r))&0x8000);s.nz16(r);return r&0xffff
    def unary(s,n,v):
        if n=='NEG':
            r=(-v)&0xff;s.sf(1,v!=0);s.sf(2,v==0x80);s.nz8(r);return r
        if n=='COM':
            r=(~v)&0xff;s.sf(1,1);s.sf(2,0);s.nz8(r);return r
        if n=='LSR':
            s.sf(1,v&1);r=v>>1;s.sf(8,0);s.sf(4,r==0);return r
        if n=='ROR':
            c=s.f(1);s.sf(1,v&1);r=(v>>1)|(c<<7);s.nz8(r);return r
        if n=='ASR':
            s.sf(1,v&1);r=(v>>1)|(v&0x80);s.nz8(r);return r
        if n=='LSL':
            s.sf(1,v&0x80);r=(v<<1)&0xff;s.sf(2,(v>>7&1)^(v>>6&1));s.nz8(r);return r
        if n=='ROL':
            c=s.f(1);s.sf(1,v&0x80);r=((v<<1)|c)&0xff;s.sf(2,(v>>7&1)^(v>>6&1));s.nz8(r);return r
        if n=='DEC':
            r=(v-1)&0xff;s.sf(2,v==0x80);s.nz8(r);return r
        if n=='INC':
            r=(v+1)&0xff;s.sf(2,v==0x7f);s.nz8(r);return r
        if n=='TST':
            s.sf(2,0);s.nz8(v);return v
        if n=='CLR':
            s.CC=(s.CC&0xf0)|4;return 0
    def cond(s,i):
        c=s.f(1);z=s.f(4);n=s.f(8);v=s.f(2)
        return [1,0,not(c or z),c or z,not c,c,not z,z,not v,v,not n,n,n==v,n!=v,(not z) and n==v,z or n!=v][i]
    def step(s):
        pc0=s.PC;op=s.fetch();page=0
        if op in(0x10,0x11):
            page=op-0x0f;op=s.fetch()
        e=T.get((page,op))
        if not e: raise Exception('bad opcode %d:%02x at %04x'%(page,op,pc0))
        n,m=e
        s.cyc+=2
        if m=='reg1':
            reg=n[-1];setattr(s,reg,s.unary(n[:-1],getattr(s,reg)));return
        if m=='inh':
            s.inh(n);return
        if m=='rel8':
            o=s.fetch();o=o-256 if o&0x80 else o
            if n=='BSR': s.push('S',s.PC,2);s.PC=(s.PC+o)&0xffff
            elif s.cond(BR.index(n)):s.PC=(s.PC+o)&0xffff
            return
        if m=='rel16':
            o=s.fetch16();o=o-65536 if o&0x8000 else o
            if n=='LBSR': s.push('S',s.PC,2);s.PC=(s.PC+o)&0xffff
            elif n=='LBRA':s.PC=(s.PC+o)&0xffff
            elif s.cond(BR.index(n[1:])):s.PC=(s.PC+o)&0xffff
            return
        if m=='reg':
            pb=s.fetch();a=pb>>4;b=pb&15
            if n=='TFR':
                v=s.getreg(a);s.setreg(b,v)
            else:
                va=s.getreg(a);vb=s.getreg(b);s.setreg(a,vb);s.setreg(b,va)
            return
        if m=='stk':
            mk=s.fetch()
            {'PSHS':lambda:s.pshs('S',mk),'PULS':lambda:s.puls('S',mk),'PSHU':lambda:s.pshs('U',mk),'PULU':lambda:s.puls('U',mk)}[n]();return
        v=None
        if m=='imm8': a=None;v=s.fetch()
        elif m=='imm16': a=None;v=s.fetch16()
        elif m=='dir': a=(s.DP<<8)|s.fetch()
        elif m=='ext': a=s.fetch16()
        elif m=='idx': a=s.idx()
        if n.startswith('LEA'):
            r=n[3];setattr(s,r,a)
            if r in'XY': s.sf(4,a==0)
            return
        if n in('ORCC','ANDCC'):
            s.CC=(s.CC|v) if n=='ORCC' else (s.CC&v);return
        if n in UN.values():
            if n=='JMP': s.PC=a;return
            s.wr(a,s.unary(n,s.rd(a)));return
        if n=='JSR': s.push('S',s.PC,2);s.PC=a;return
        w16=n in W16
        isst=n.startswith('ST')
        if v is None and not isst:
            v=s.rd16(a) if w16 else s.rd(a)
        if n=='STA':s.wr(a,s.A);s.nz8(s.A);s.sf(2,0);return
        if n=='STB':s.wr(a,s.B);s.nz8(s.B);s.sf(2,0);return
        if n=='STD':s.wr16(a,s.D);s.nz16(s.D);s.sf(2,0);return
        if n in('STX','STY','STU','STS'):
            r=getattr(s,n[2]);s.wr16(a,r);s.nz16(r);s.sf(2,0);return
        if n in('LDA','LDB'):
            setattr(s,n[2],v);s.nz8(v);s.sf(2,0);return
        if n=='LDD':s.D=v;s.nz16(v);s.sf(2,0);return
        if n in('LDX','LDY','LDU','LDS'):
            setattr(s,n[2],v);s.nz16(v);s.sf(2,0);return
        if n in('SUBD','ADDD','CMPD','CMPX','CMPY','CMPU','CMPS'):
            if n=='SUBD':s.D=s.sub16(s.D,v)
            elif n=='ADDD':s.D=s.add16(s.D,v)
            else:
                r={'CMPD':s.D,'CMPX':s.X,'CMPY':s.Y,'CMPU':s.U,'CMPS':s.S}[n];s.sub16(r,v)
            return
        reg=n[-1];op2=n[:-1];r=getattr(s,reg)
        if op2=='SUB':setattr(s,reg,s.sub8(r,v))
        elif op2=='CMP':s.sub8(r,v)
        elif op2=='SBC':setattr(s,reg,s.sub8(r,v,s.f(1)))
        elif op2=='ADD':setattr(s,reg,s.add8(r,v))
        elif op2=='ADC':setattr(s,reg,s.add8(r,v,s.f(1)))
        elif op2 in('AND','BIT','EOR','OR'):
            x={'AND':r&v,'BIT':r&v,'EOR':r^v,'OR':r|v}[op2];s.nz8(x);s.sf(2,0)
            if op2!='BIT':setattr(s,reg,x)
        else: raise Exception('unimpl '+n)
    def inh(s,n):
        if n=='NOP':return
        if n=='RTS':s.PC=s.pop('S',2);return
        if n=='RTI':
            s.CC=s.pop('S')
            if s.CC&0x80: s.puls('S',0xFE)
            else: s.PC=s.pop('S',2)
            return
        if n=='ABX':s.X=(s.X+s.B)&0xffff;return
        if n=='SEX':s.A=0xff if s.B&0x80 else 0;s.nz16(s.D);return
        if n=='MUL':
            r=s.A*s.B;s.D=r;s.sf(4,r==0);s.sf(1,r&0x80);return
        if n=='DAA':
            a=s.A;c=0
            lo=a&15;hi=a>>4
            if s.f(32) or lo>9:c|=6
            if s.f(1) or hi>9 or (hi>8 and lo>9):c|=0x60
            r=a+c;s.sf(1,s.f(1) or r>0xff);s.A=r&0xff;s.nz8(s.A);return
        if n in('SWI','SWI2','SWI3'):
            s.CC|=0x80;s.pshs('S',0xff);s.CC|=0x50;s.PC=s.rd16({'SWI':0xfffa,'SWI2':0xfff4,'SWI3':0xfff2}[n]);return
        if n=='SYNC':return
        raise Exception('unimpl inh '+n)

def disasm(rd,pc):
    """rd(addr)->byte. returns (text,len)"""
    a=pc;op=rd(a);a+=1;page=0
    if op in(0x10,0x11):page=op-0x0f;op=rd(a);a+=1
    e=T.get((page,op))
    if not e:return('db $%02x'%op,a-pc)
    n,m=e
    def r16(x):return rd(x)<<8|rd(x+1)
    if m in('inh','reg1'):return(n,a-pc)
    if m=='imm8':return('%s #$%02x'%(n,rd(a)),a+1-pc)
    if m=='imm16':return('%s #$%04x'%(n,r16(a)),a+2-pc)
    if m=='dir':return('%s <$%02x'%(n,rd(a)),a+1-pc)
    if m=='ext':return('%s $%04x'%(n,r16(a)),a+2-pc)
    if m=='rel8':
        o=rd(a);o=o-256 if o&0x80 else o;return('%s $%04x'%(n,(a+1+o)&0xffff),a+1-pc)
    if m=='rel16':
        o=r16(a);o=o-65536 if o&0x8000 else o;return('%s $%04x'%(n,(a+2+o)&0xffff),a+2-pc)
    if m=='reg':
        pb=rd(a);return('%s %s,%s'%(n,REGN[pb>>4],REGN[pb&15]),a+1-pc)
    if m=='stk':
        mk=rd(a);rs=['CC','A','B','DP','X','Y','U' if n[3]=='S' else 'S','PC']
        return('%s %s'%(n,','.join(x for i,x in enumerate(rs) if mk>>i&1)),a+1-pc)
    if m=='idx':
        pb=rd(a);a+=1;R='XYUS'[(pb>>5)&3]
        if not pb&0x80:
            o=pb&0x1f;o=o-32 if o&0x10 else o;return('%s %d,%s'%(n,o,R),a-pc)
        t=pb&15;ind=pb&0x10
        if t==0:x=',%s+'%R
        elif t==1:x=',%s++'%R
        elif t==2:x=',-%s'%R
        elif t==3:x=',--%s'%R
        elif t==4:x=',%s'%R
        elif t==5:x='B,%s'%R
        elif t==6:x='A,%s'%R
        elif t==8:
            o=rd(a);a+=1;o=o-256 if o&0x80 else o;x='%d,%s'%(o,R)
        elif t==9:
            o=r16(a);a+=2;o=o-65536 if o&0x8000 else o;x='%d,%s'%(o,R)
        elif t==0xB:x='D,%s'%R
        elif t==0xC:
            o=rd(a);a+=1;o=o-256 if o&0x80 else o;x='%d,PC'%o
        elif t==0xD:
            o=r16(a);a+=2;o=o-65536 if o&0x8000 else o;x='%d,PC'%o
        elif t==0xF:
            x='$%04x'%r16(a);a+=2
        else:x='?'
        return('%s %s'%(n,('[%s]'%x) if ind else x),a-pc)
