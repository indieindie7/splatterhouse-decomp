# v1check.py <prog> <n chunks>: validate round-1 verdict files work/v1_<p>_<k>.txt against chunk headers,
# write ghidra/hand_<p>.txt (func lines, dup names get _<addr>) and ghidra/bogus_<p>.txt
import re, sys, collections
p, n = sys.argv[1], int(sys.argv[2])
want = {}
for k in range(n):
    for l in open('r1_%s_%d.c' % (p, k)):
        m = re.match(r'// ==== (\S+) @ ([0-9a-f]+)', l)
        if m: want[int(m.group(2), 16)] = m.group(1)
got, bad = {}, []
for k in range(n):
    for l in open('v1_%s_%d.txt' % (p, k), encoding='utf-8', errors='replace'):
        l = l.strip()
        if not l: continue
        m = re.match(r'(0x[0-9a-fA-F]+)\s+(func\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:hand\s*)?(.*)|bogus\s*(.*))$', l)
        if not m: bad.append(l); continue
        a = int(m.group(1), 16)
        if a in got: bad.append('dup addr ' + l); continue
        got[a] = ('bogus', m.group(5)) if m.group(2).startswith('bogus') else (m.group(3)[:60], m.group(4))
miss = sorted(set(want) - set(got)); extra = sorted(set(got) - set(want))
keep = {a: v for a, v in want.items() if not v.startswith(('FUN_', 'ptr_'))}  # vector names etc.
cnt = collections.Counter(v[0] for a, v in got.items() if v[0] != 'bogus')
H, B = [], []
for a in sorted(got):
    if a not in want: continue
    nm, ev = got[a]
    if nm == 'bogus':
        if a in keep: continue
        B.append('0x%x' % a); continue
    if a in keep: continue
    if cnt[nm] > 1 or nm in keep.values(): nm = '%s_%x' % (re.sub(r'_[0-9a-f]+$', '', nm), a)
    H.append('0x%x func %s hand %s' % (a, nm, ev.replace('\t', ' ')))
names = collections.Counter(h.split()[2] for h in H)
print(p, 'want', len(want), 'got', len(got), 'missing', len(miss), 'extra', len(extra), 'badlines', len(bad), 'hand', len(H), 'bogus', len(B), 'dupnames left', sum(1 for v in names.values() if v > 1))
for x in miss[:10]: print(' missing %x %s' % (x, want[x]))
for x in bad[:10]: print(' bad', x[:120])
open('../ghidra/hand_%s.txt' % p, 'w', newline='\n').write('\n'.join(H) + '\n')
open('../ghidra/bogus_%s.txt' % p, 'w', newline='\n').write('\n'.join(B) + '\n')
