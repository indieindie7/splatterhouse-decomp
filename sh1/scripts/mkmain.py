import sys
sys.path.insert(0,r'C:\re\splatterhouse\scripts')
import mkrom
mk=mkrom
img=b''.join(mk.bank(b) for b in (0x230,0x3FA,0x3FD,0x3FE,0x3FF))
open(r'C:\re\splatterhouse\work\main_6000.bin','wb').write(img)
open(r'C:\re\splatterhouse\work\bank_3b4.bin','wb').write(mk.bank(0x3b4))
print(len(img))
