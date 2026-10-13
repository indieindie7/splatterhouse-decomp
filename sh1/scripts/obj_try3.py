import sys
from PIL import Image
d=open(sys.argv[1],'rb').read()
off=int(sys.argv[3],0); cols=int(sys.argv[4]); rows=int(sys.argv[5])
im=Image.new('L',(cols*17,rows*17),128)
for n in range(cols*rows):
    cx=(n%cols)*17; cy=(n//cols)*17
    for y in range(16):
        for x in range(16):
            v=d[off+n*256+y*16+x]
            im.putpixel((cx+x,cy+y),v*16 if v<15 else 255)
im.resize((im.width*2,im.height*2),0).save(sys.argv[2])
