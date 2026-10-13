import sys, os, struct
bin_, out = sys.argv[1], sys.argv[2]
f = open(bin_, 'rb')
def sec(n):
    f.seek(n*2352+16)  # mode1 raw: 12 sync+4 header
    return f.read(2048)
pvd = sec(16)
assert pvd[1:6] == b'CD001', pvd[:8]
root = pvd[156:190]
rl = struct.unpack('<I', root[2:6])[0]; rs = struct.unpack('<I', root[10:14])[0]
print('vol', pvd[40:72].decode().strip(), 'sectors', struct.unpack('<I', pvd[80:84])[0])
listing=[]
def walk(lba, size, path):
    data = b''.join(sec(lba+i) for i in range((size+2047)//2048))[:size]
    p = 0
    while p < len(data):
        l = data[p]
        if l == 0:
            p = (p//2048+1)*2048; continue
        r = data[p:p+l]; p += l
        if len(r)<34 or l<34: print("BAD",l,r.hex()); continue
        elo = struct.unpack('<I', r[2:6])[0]; esz = struct.unpack('<I', r[10:14])[0]
        fl = r[25]; nl = r[32]; name = r[33:33+nl]
        if name in (b'\x00', b'\x01'): continue
        name = name.decode('latin1').split(';')[0]
        full = path + '/' + name
        if fl & 2:
            os.makedirs(out + full, exist_ok=True); walk(elo, esz, full)
        else:
            os.makedirs(os.path.dirname(out + full), exist_ok=True)
            with open(out + full, 'wb') as o:
                for i in range((esz+2047)//2048): o.write(sec(elo+i))
                o.truncate(esz)
            listing.append((full, esz))
walk(rl, rs, '')
for n, s in listing: print(s, n)
