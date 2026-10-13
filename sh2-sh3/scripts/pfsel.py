import sys
rows = [l.split() for l in open(sys.argv[1]) if l.startswith('target')]
sites = {int(s, 16) for r in rows for s in r[4:]}
n = 0
for r in rows:
    ss = [int(s, 16) for s in r[4:]]
    run = any((s + 4 in sites) or (s - 4 in sites) for s in ss)
    if len(ss) >= 2 or run:
        print('0x%s func ptr_%s hand pointer-table target (%s) sites %s' % (r[1].lstrip('0'), r[1].lstrip('0'), r[2], ' '.join(r[4:9])))
        n += 1
print(n, file=sys.stderr)
