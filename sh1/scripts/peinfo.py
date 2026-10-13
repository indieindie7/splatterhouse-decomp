import sys, struct, re
for p in sys.argv[1:]:
    d = open(p,'rb').read()
    print('==', p, len(d), d[:2])
    if d[:2]!=b'MZ': continue
    e = struct.unpack('<I', d[0x3c:0x40])[0]
    sig = d[e:e+2]; print(' sig', sig)
    if sig==b'PE':
        m,ns,ts,_,_,so,ch = struct.unpack('<HHIIIHH', d[e+4:e+24])
        opt=d[e+24:]; mg=struct.unpack('<H',opt[:2])[0]
        print(' machine',hex(m),'dll' if ch&0x2000 else 'exe','magic',hex(mg),'linker %d.%d'%(opt[2],opt[3]),'subsys',struct.unpack('<H',opt[68:70])[0], 'ts',ts)
        base = 0 if True else 0
        # imports
        nrva = 96 if mg==0x10b else 112
        ddir = opt[nrva:nrva+128]
        secs=[]; so0=e+24+so
        for i in range(ns):
            s=d[so0+i*40:so0+i*40+40]; secs.append((s[:8].rstrip(b'\0').decode('latin1'),)+struct.unpack('<IIII',s[8:24]))
        print(' sections',[(s[0],hex(s[1]),hex(s[2])) for s in secs])
        def r2o(r):
            for n,vs,va,rs,ro in secs:
                if va<=r<va+max(vs,rs): return r-va+ro
        irva,isz=struct.unpack('<II',ddir[8:16])
        names=[]
        if irva:
            o=r2o(irva)
            while True:
                x=struct.unpack('<IIIII',d[o:o+20])
                if not x[3]: break
                n=r2o(x[3]); names.append(d[n:d.index(b'\0',n)].decode()); o+=20
        print(' imports',names)
    else:
        print(' non-PE sig; e_lfanew',e)
    for k in [b'Microsoft',b'Borland',b'Watcom',b'Visual C',b'MSVC',b'Delphi',b'Inno',b'Nullsoft']:
        if k in d: print(' hint',k.decode(), d.count(k))
