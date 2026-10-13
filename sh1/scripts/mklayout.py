import sys,json; sys.path.insert(0,'C:/re/splatterhouse/scripts')
from sprbuild import rick,zomb
spec=[('rick','idle',rick,[0,2]),('rick','walk',rick,[8,10,16,18,24,26,32,34]),
('rick','punch',rick,[112,114,176,178,184]),('rick','kick',rick,[104,240]),
('rick','jump',rick,[88,90,96]),('rick','hurt',rick,[64,82]),('rick','down',rick,[128]),
('deadman','walk',zomb,[576,577,578,579]),('deadman','walk_hunched',zomb,[584,585,586,587]),
('deadman','hit',zomb,[592,594,595]),('deadman','die',zomb,[593,600,601])]
fr=[]
for ch,an,fn,bs in spec:
    for n,b in enumerate(bs): fr.append({'char':ch,'anim':an,'n':n,'base':b,'cells':fn(b)})
json.dump({'src':'0x330','pal':0,'note':'cells=[cell,dx,dy]; palette 0 of ROM bank 0x330 is a GUESS','frames':fr},open('C:/re/splatterhouse/scripts/layout.json','w'),indent=0)
