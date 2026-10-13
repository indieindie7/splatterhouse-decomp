import re,sys
d=open(r'C:\re\splatterhouse\work\rom1mb.bin','rb').read()
for h in sys.argv[1:]:
    p=bytes.fromhex(h)
    print(h,[hex(m.start()) for m in re.finditer(re.escape(p),d)][:30])
