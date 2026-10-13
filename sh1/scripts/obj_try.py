import sys
from PIL import Image
d=open(sys.argv[1],'rb').read()
import collections
print(len(d), collections.Counter(d).most_common(20))
# linear rows of 32: view first 64KB as 256-wide strips
for name,w in (('w32',32),('w256',256)):
    n=0x8000
    im=Image.new('L',(w, n//w))
    im.putdata([ (v*16 if v<16 else 255) for v in d[:n]])
    if w==256: im=im.resize((512,im.height*2))
    im.save(sys.argv[2]+name+'.png')
