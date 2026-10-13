# Recursive descent over the gameplay map (6000-FFFF, work\game_6000.bin) with jump-table expansion.
# usage: reach.py seedhex...   prints function entries (hex) on stdout, stats on stderr
import sys, re
sys.path.insert(0, r'C:\re\splatterhouse\scripts')
import m6809
img = open(r'C:\re\splatterhouse\work\game_6000.bin', 'rb').read()
def rd(a):
    a &= 0xffff
    return img[a - 0x6000] if a >= 0x6000 else 0
seen = set(); fn = set(); code = 0; tabs = {}
def walk(seeds):
    global code
    work = list(seeds); hist = []
    while work:
        a = work.pop()
        while a not in seen and 0x6000 <= a < 0x10000:
            try: t, l = m6809.disasm(rd, a)
            except Exception: break
            if t.startswith('db'): break
            seen.add(a); code += l
            hist.append(t); hist[:] = hist[-8:]
            p = t.split(); mn = p[0]; op = p[1] if len(p) > 1 else ''
            m = re.match(r'\$([0-9a-f]{4})$', op)
            if mn in ('JSR', 'BSR', 'LBSR') and m:
                x = int(m.group(1), 16); fn.add(x); work.append(x)
            elif m and mn[0] == 'B' and mn not in ('BITA', 'BITB') or (m and mn in ('LBRA', 'JMP') or (m and mn.startswith('LB'))):
                work.append(int(m.group(1), 16))
            if mn in ('JSR', 'JMP') and '[' in t:
                for h in hist[:-1]:
                    mm = re.match(r'LDX #\$([0-9a-f]{4})', h)
                    if mm: tabs[int(mm.group(1), 16)] = 1
            if mn in ('RTS', 'RTI', 'JMP', 'BRA', 'LBRA'): break
            a += l
seeds = [int(x, 16) for x in sys.argv[1:]]
fn.update(seeds); walk(seeds)
done = set()
for rnd in range(6):
    new = []
    for ta in sorted(tabs):
        if ta in done: continue
        done.add(ta)
        for i in range(40):
            e = (rd(ta + 2 * i) << 8) | rd(ta + 2 * i + 1)
            if not (0x6000 <= e < 0x10000) or ta <= e < ta + 2 * i + 2: break
            try:
                t, l = m6809.disasm(rd, e)
            except Exception: break
            if t.startswith('db'): break
            if e not in fn: fn.add(e); new.append(e)
    if not new: break
    walk(new)
print('insns', len(seen), 'codebytes', code, 'fns', len(fn), 'tables', sorted(hex(x) for x in tabs), file=sys.stderr)
print(' '.join('0x%x' % f for f in sorted(fn)))
