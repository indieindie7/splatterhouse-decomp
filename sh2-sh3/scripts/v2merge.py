# v2merge.py <prog>: fold work/v2_<prog>.txt (round-2 verdicts) into ghidra/hand_<prog>.txt and bogus_<prog>.txt.
# Run from work/. Prints the renames and refuses duplicate names.
import re, sys
p = sys.argv[1]
hand = '../ghidra/hand_%s.txt' % p
lines = open(hand, encoding='utf-8').read().splitlines()
idx = {int(l.split()[0], 16): i for i, l in enumerate(lines)}
newbogus = []
for l in open('v2_%s.txt' % p, encoding='utf-8').read().splitlines():
    l = l.strip()
    if not l:
        continue
    m = re.match(r'(0x[0-9a-fA-F]+)\s+(?:func\s+([A-Za-z_]\w*)\s*(?:hand\s*)?(.*)|bogus\s*(.*))$', l)
    if not m:
        sys.exit('bad line: ' + l)
    a = int(m.group(1), 16)
    if a not in idx:
        sys.exit('not in hand: ' + l)
    old = lines[idx[a]]
    if m.group(2) is None:
        newbogus.append('0x%x' % a)
        lines[idx[a]] = None
        print('bogus', old)
        continue
    new = '0x%x func %s hand %s' % (a, m.group(2), m.group(3))
    if old.split()[2] != m.group(2):
        print('rename 0x%x %s -> %s' % (a, old.split()[2], m.group(2)))
    lines[idx[a]] = new
lines = [l for l in lines if l is not None]
names = [l.split()[2] for l in lines]
d = {n for n in names if names.count(n) > 1}
if d:
    sys.exit('duplicate names: %s' % sorted(d))
open(hand, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
if newbogus:
    open('../ghidra/bogus_%s.txt' % p, 'a', encoding='utf-8', newline='\n').write('\n'.join(newbogus) + '\n')
print(p, 'hand', len(lines), 'new bogus', len(newbogus), 'GUESS left', sum('GUESS' in l for l in lines))
