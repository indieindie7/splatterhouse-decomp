import sys, capstone
b = open(sys.argv[1], 'rb').read()
a, n = int(sys.argv[2], 16), int(sys.argv[3])
md = capstone.Cs(capstone.CS_ARCH_M68K, capstone.CS_MODE_BIG_ENDIAN | capstone.CS_MODE_M68K_000)
for i in md.disasm(b[a:a + n], a):
    print('%06x  %-8s %s' % (i.address, i.mnemonic, i.op_str))
