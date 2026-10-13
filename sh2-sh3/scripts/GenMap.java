// GenMap.java: Sega Genesis / Mega Drive memory map for a cartridge ROM imported at base 0 (68000 BE), then the
// 64 68000 vectors as pointers, a function at every vector target inside the ROM, and names for them.
// Map: ROM 0..size, Z80 space 0xa00000, I/O 0xa10000, Z80 bus/reset 0xa11100, TMSS 0xa14000, VDP 0xc00000,
// work RAM 0xff0000 (64 KB, mirrored through 0xe00000 on hardware; only the canonical copy is mapped).
//@category Splatterhouse
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.symbol.SourceType;
import java.util.*;
public class GenMap extends GhidraScript {
  Memory m;
  void io(String n, long a, long len, boolean vol) throws Exception {
    MemoryBlock b = m.createUninitializedBlock(n, toAddr(a), len, false);
    b.setRead(true); b.setWrite(true); b.setVolatile(vol);
  }
  static final String[] NAMES = {"vec_InitSP", "Reset", "BusError", "AddressError", "IllegalInstr", "ZeroDivide",
    "ChkInstr", "TrapV", "Privilege", "Trace", "Line1010", "Line1111"};
  public void run() throws Exception {
    m = currentProgram.getMemory();
    long romEnd = m.getBlocks()[0].getEnd().getOffset() + 1;
    io("z80_space", 0xa00000, 0x10000, true);
    io("io_ports", 0xa10000, 0x20, true);
    io("z80_busreq", 0xa11100, 2, true);
    io("z80_reset", 0xa11200, 2, true);
    io("tmss", 0xa14000, 4, true);
    io("vdp_data", 0xc00000, 4, true);
    io("vdp_ctrl", 0xc00004, 4, true);
    io("vdp_hvcount", 0xc00008, 2, true);
    io("psg", 0xc00011, 1, true);
    io("work_ram", 0xff0000, 0x10000, false);
    for (String[] r : new String[][] {{"a10001", "io_Version"}, {"a10003", "io_Data1"}, {"a10005", "io_Data2"},
        {"a10007", "io_Data3"}, {"a10009", "io_Ctrl1"}, {"a1000b", "io_Ctrl2"}, {"a1000d", "io_Ctrl3"},
        {"a11100", "z80_BusReq"}, {"a11200", "z80_Reset"}, {"a14000", "tmss_Sega"}, {"c00000", "vdp_Data"},
        {"c00004", "vdp_Ctrl"}, {"c00008", "vdp_HVCounter"}, {"c00011", "psg_Port"}})
      createLabel(toAddr(Long.parseLong(r[0], 16)), r[1], true, SourceType.USER_DEFINED);
    // cartridge header
    createLabel(toAddr(0x100), "hdr_Console", true, SourceType.USER_DEFINED);
    for (long a = 0x100; a < 0x200; a += 16) { clearListing(toAddr(a), toAddr(a + 15)); }
    createAsciiString(toAddr(0x100), 16); createAsciiString(toAddr(0x110), 16);
    createAsciiString(toAddr(0x120), 48); createAsciiString(toAddr(0x150), 48); createAsciiString(toAddr(0x180), 14);
    Map<Long, String> made = new LinkedHashMap<>();
    for (int i = 0; i < 64; i++) {
      Address a = toAddr(4L * i);
      clearListing(a, a.add(3));
      createData(a, PointerDataType.dataType);
      if (i == 0) continue;
      long t = getInt(a) & 0xffffffffL;
      if (t == 0 || t >= romEnd || (t & 1) != 0) continue;
      String n;
      if (i < NAMES.length) n = "exc_" + NAMES[i];
      else if (i == 24) n = "exc_Spurious";
      else if (i == 26) n = "irq_External";
      else if (i == 28) n = "irq_HBlank";
      else if (i == 30) n = "irq_VBlank";
      else if (i > 24 && i <= 31) n = "irq_Level" + (i - 24);
      else if (i >= 32 && i <= 47) n = "trap_" + (i - 32);
      else n = "vec_" + i;
      if (made.containsKey(t)) { made.put(t, made.get(t) + "_" + n); continue; }
      made.put(t, n);
    }
    for (Map.Entry<Long, String> e : made.entrySet()) {
      Address t = toAddr(e.getKey());
      disassemble(t);
      createFunction(t, null);
      String n = e.getValue().length() > 60 ? e.getValue().substring(0, 60) : e.getValue();
      createLabel(t, n, true, SourceType.USER_DEFINED);
      println(String.format("%06x %s", e.getKey(), e.getValue()));
    }
    println("map: " + m.getBlocks().length + " blocks, rom end " + Long.toHexString(romEnd) + ", vectors: " + made.size() + " targets");
  }
}
