import re,sys
d=open(sys.argv[1],'rb').read()
for m in re.finditer(rb'[\x20-\x7e]{4,}',d):
    print(hex(m.start()),m.group().decode())
