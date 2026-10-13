import sys, re, collections
# globs.py <decomp.c> <out>: DAT_ refs in RAM/shared/NVRAM ranges, count + users
cnt = collections.Counter(); users = collections.defaultdict(set); fn = None
for l in open(sys.argv[1], encoding='utf-8', errors='replace'):
    m = re.match(r'// ==== (\S+) @', l)
    if m: fn = m.group(1); continue
    for a in re.findall(r'DAT_00([0-9a-f]{6})\b', l):
        v = int(a, 16)
        if 0x100000 <= v < 0x1c0000 or 0x900000 <= v < 0x910000:
            cnt[v] += 1; users[v].add(fn)
with open(sys.argv[2], 'w') as o:
    for v in sorted(cnt):
        u = sorted(users[v])
        o.write('0x%06x refs %d fns %d: %s\n' % (v, cnt[v], len(u), ' '.join(u[:8])))
print(len(cnt), sum(1 for v in cnt if len(users[v]) >= 2))
