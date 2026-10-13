import re,collections
R=b''.join(open(r'C:\re\splatterhouse\files\DISK_1\ROMS\PRG%d'%i,'rb').read() for i in range(8))
c=collections.Counter()
for m in re.finditer(rb'\xcc(..)\xfd([\xe0-\xef])([\x00-\xff])',R,re.S):
    v=int.from_bytes(m.group(1),'big'); a=m.group(2)[0]<<8|m.group(3)[0]
    if a&0x1ff in(0,): c[(a,v)]+=1
win=collections.defaultdict(set)
for (a,v),n in c.items(): win[(a>>9)&7].add(v)
for w in sorted(win): print(w,sorted(hex(x) for x in win[w]))
print(len(R))
