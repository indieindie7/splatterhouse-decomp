import sys; sys.path.insert(0,'C:/re/splatterhouse/scripts')
from sprlib import *
pal=load_pal(0x330)
W=16
im=Image.new('RGB',(W*68,8*34),(60,0,60))
for p in range(128):
    c=Image.new('RGBA',(64,32),(0,0,0,0))
    c.paste(render_cell(0,pal,p*16),(0,0));c.paste(render_cell(1,pal,p*16),(32,0))
    im.paste(c,((p%W)*68,(p//W)*34),c)
im=im.resize((im.width*1,im.height*1))
im.save(r'C:\goobi\brawler\assets\private\splatterhouse\sheets\palpick_rick.png')
