import struct,sys
d=open(r'C:\re\splatterhouse\files\DISK_1\SPLATTER.EXE','rb').read()
for name in sys.argv[1:]:
    off=d.find(b'.?AV'+name.encode()+b'@@')
    td=0x400000+off-8
    cols=[0x400000+m for m in range(0,len(d)-20,4) if struct.unpack_from('<I',d,m)[0]==0 and struct.unpack_from('<I',d,m+12)[0]==td]
    for col in cols:
        p=struct.pack('<I',col); i=d.find(p)
        while i>=0:
            n=16
            print(name,'vft',hex(0x400000+i+4),' '.join('%08x'%x for x in struct.unpack_from('<%dI'%n,d,i+4)))
            i=d.find(p,i+1)
