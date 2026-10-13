import sys, itertools
d=open(sys.argv[1],'rb').read()
def blk(c,q): # 16x16 block q of cell c as list of rows
    o=c*1024+q*256
    return [d[o+y*16:o+y*16+16] for y in range(16)]
def seam(a,b,horiz):
    s=0;n=0
    for i in range(16):
        if horiz: p,q=a[i][15],b[i][0]
        else: p,q=a[15][i],b[0][i]
        if p!=15 or q!=15:
            n+=1; s+= abs(p-q) if p!=15 and q!=15 else 16
    return s,n
res=[]
for perm in itertools.permutations(range(4)):
    S=0;N=0
    for c in range(0,1500,3):
        B=[blk(c,perm[i]) for i in range(4)]
        for (a,b,h) in ((0,1,1),(2,3,1),(0,2,0),(1,3,0)):
            s,n=seam(B[a],B[b],h);S+=s;N+=n
    res.append((S/max(N,1),perm))
res.sort();print(res[:6])
