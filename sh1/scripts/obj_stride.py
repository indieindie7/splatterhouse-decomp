import sys
d=open(sys.argv[1],'rb').read()[:0x40000]
r=[]
for W in range(4,600):
    s=0;n=0
    for i in range(0,len(d)-W,7):
        a=d[i];b=d[i+W]
        if a!=15 or b!=15:
            n+=1; s+=abs(a-b) if a!=15 and b!=15 else 16
    r.append((s/max(n,1),W))
r.sort();print(r[:12])
