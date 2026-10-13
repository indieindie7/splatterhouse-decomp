import sys; sys.path.insert(0,'C:/re/splatterhouse/scripts')
from sprlib import *
def frame(b,pal,pn):
    f=Image.new('RGBA',(64,64),(0,0,0,0))
    for i,(dx,dy,c) in enumerate([(0,0,b),(32,0,b+1),(0,32,b+4),(32,32,b+5)]):
        f.alpha_composite(render_cell(c,pal,pn*16),(dx,dy))
    return f
if __name__=='__main__':
    lo,hi,pn=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]); src=int(sys.argv[4],16) if len(sys.argv)>4 else 0x330
    pal=load_pal(src)
    bs=[8*i+j for i in range(lo//8,hi//8) for j in (0,2)]
    cols=8; S=2
    im=Image.new('RGB',(cols*(64*S+4),((len(bs)+cols-1)//cols)*(64*S+14)),(70,0,70)); d=ImageDraw.Draw(im)
    for n,b in enumerate(bs):
        x=(n%cols)*(64*S+4); y=(n//cols)*(64*S+14)
        f=frame(b,pal,pn).resize((64*S,64*S),Image.NEAREST); im.paste(f,(x,y+12),f); d.text((x,y),str(b),fill=(255,255,0))
    im.save(sys.argv[5] if len(sys.argv)>5 else 'C:/goobi/brawler/assets/private/splatterhouse/sheets/frames_%d_%d_p%d.png'%(lo,hi,pn))
