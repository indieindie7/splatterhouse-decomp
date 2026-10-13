import sys
sys.path.insert(0,r'C:\re\splatterhouse\scripts')
from sprlib import *
out=r'C:\goobi\brawler\assets\private\splatterhouse\sheets'
gray=[(v*17,)*3 for v in range(16)]
for s in range(8):
    im=Image.new('RGB',(16*68,16*68),(255,0,255))
    dr=ImageDraw.Draw(im)
    for n in range(256):
        c=s*256+n
        cx=(n%16)*68;cy=(n//16)*68
        t=render_cell(c,gray,0).resize((64,64),0)
        im.paste((40,40,40),(cx,cy,cx+66,cy+66))
        im.paste(t,(cx+1,cy+1),t)
        dr.text((cx+2,cy+2),str(c),fill=(255,255,0))
    im.save(out+r'\gray_%04d-%04d.png'%(s*256,s*256+255))
