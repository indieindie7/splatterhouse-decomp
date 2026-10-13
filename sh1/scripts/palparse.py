import sys
sys.path.insert(0,r'C:\re\splatterhouse\scripts')
import shmach
b370=shmach.rombank(0x370)
def w(o): return b370[o]<<8|b370[o+1]
print('first words',[hex(w(i*2)) for i in range(12)])
# palette lists: pointers at 0x6000+2i
for i in range(0,90):
    p=w(i*2)
    if not (0x6000<=p<0x8000): print('idx',i,'ptr',hex(p));break
    o=p-0x6000;recs=[]
    while True:
        bk=w(o)
        if bk==0:break
        recs.append((hex(bk),hex(w(o+2)),hex(w(o+4)),hex(w(o+6))));o+=8
    print(i,hex(p),recs)
