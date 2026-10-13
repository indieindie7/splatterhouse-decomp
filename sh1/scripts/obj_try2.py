import sys
from PIL import Image
d=open(sys.argv[1],'rb').read()
off=int(sys.argv[3],0)
# 16 wide, rows continuing: 128 rows x 16 -> shows vertical continuity; tile as columns of 64 rows
W=16;H=64;cols=32
im=Image.new('L',(cols*W,H))
for c in range(cols):
    for y in range(H):
        for x in range(W):
            v=d[off+(c*H+y)*W+x]
            im.putpixel((c*W+x,y),v*16 if v<15 else 255)
im.resize((cols*W*2,H*2),0).save(sys.argv[2])
