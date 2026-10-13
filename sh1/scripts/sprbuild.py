import sys,json; sys.path.insert(0,'C:/re/splatterhouse/scripts')
from sprlib import *
OUT='C:/goobi/brawler/assets/private/splatterhouse/'
def rick(b): return [[b,0,0],[b+1,32,0],[b+4,0,32],[b+5,32,32]]
def zomb(b): return [[b,0,0],[b+4,0,32]]
def compose(cells,pal,pn):
    w=max(dx for _,dx,_ in cells)+32; h=max(dy for _,_,dy in cells)+32
    f=Image.new('RGBA',(w,h),(0,0,0,0))
    for c,dx,dy in cells: f.alpha_composite(render_cell(c,pal,pn*16),(dx,dy))
    return f
def trim(f):
    bb=f.getbbox()
    if not bb: return f
    return f.crop((0,bb[1],f.width,bb[3]))  # keep width (centre anchor), trim top/bottom -> feet at bottom edge
if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='preview':
        pal=load_pal(0x330)
        items=[('r',b) for b in eval(sys.argv[2])]+[('z',b) for b in eval(sys.argv[3])]
        S=2;im=Image.new('RGB',(10*140,((len(items)+9)//10)*150),(70,0,70));d=ImageDraw.Draw(im)
        for n,(k,b) in enumerate(items):
            f=compose(rick(b) if k=='r' else zomb(b),pal,int(sys.argv[4]) if len(sys.argv)>4 else 0)
            f=f.resize((f.width*S,f.height*S),Image.NEAREST);x=(n%10)*140;y=(n//10)*150
            im.paste(f,(x,y+12),f);d.text((x,y),k+str(b),fill=(255,255,0))
        im.save(OUT+'sheets/preview.png')
    else:  # build from layout json
        L=json.load(open(sys.argv[2]));pal=load_pal(int(L['src'],16))
        import os
        for fr in L['frames']:
            p=OUT+fr['char']+'/';os.makedirs(p,exist_ok=True)
            trim(compose(fr['cells'],pal,fr.get('pal',L['pal']))).save(p+'%s_%02d.png'%(fr['anim'],fr['n']))
