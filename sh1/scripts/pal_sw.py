import sys
sys.path.insert(0,r'C:\re\splatterhouse\scripts')
from sprlib import *
for name,bk in (('330',0x330),('331',0x331)):
    pal=load_pal(bk)
    im=Image.new('RGB',(16*10+30,128*6),(0,0,0))
    dr=ImageDraw.Draw(im)
    for p in range(128):
        for c in range(16):
            r,g,b=pal[p*16+c]
            im.paste((r,g,b),(30+c*10,p*6,40+c*10,p*6+6))
        if p%4==0: dr.text((0,p*6-1),str(p),fill=(255,255,0))
    im.save(r'C:\goobi\brawler\assets\private\splatterhouse\sheets\palette_%s.png'%name)
