import sys
sys.path.insert(0,r'C:\re\splatterhouse\scripts')
import shmach
from PIL import Image, ImageDraw
OBJ=open(r'C:\re\splatterhouse\files\DISK_1\ROMS\OBJ.DAT','rb').read()
def cell_pixels(c):
    """32x32 list of rows of values 0..15 (15 = transparent); quadrant order TL,TR,BL,BR, each 16x16 raster"""
    rows=[[0]*32 for _ in range(32)]
    o=c*1024
    for q in range(4):
        qx=(q&1)*16; qy=(q>>1)*16
        for y in range(16):
            rows[qy+y][qx:qx+16]=list(OBJ[o+q*256+y*16:o+q*256+y*16+16])
    return rows
def palette_set(setbank, bankram=0x170):
    """returns list of 2048 (r,g,b) for sprite palette RAM bank from palette list in PRG5 table (idx 4 style)"""
    pass
def load_pal(srcbank, n=2048):
    """read n colours of R,G,B triples from ROM bank sequence starting srcbank at 0x8000 (3 bytes each); records are 0x300 bytes at 0x8000,0x8300,...0x9500 (8 records)"""
    d=shmach.rombank(srcbank)
    cols=[]
    for rec in range(8):
        for i in range(256):
            o=rec*0x300+i*3
            cols.append((d[o],d[o+1],d[o+2]))
    return cols
def render_cell(c,pal,base=0):
    im=Image.new('RGBA',(32,32),(0,0,0,0))
    px=im.load();rows=cell_pixels(c)
    for y in range(32):
        for x in range(32):
            v=rows[y][x]
            if v!=15: px[x,y]=pal[base+v]+(255,)
    return im
