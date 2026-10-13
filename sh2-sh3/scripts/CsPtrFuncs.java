// CsPtrFuncs.java <codeEnd> [create]: scan the ROM (0x400..rom end, even offsets, outside instructions) for big-endian
// 32-bit pointers into [0x400, codeEnd) that land on code no function owns: an existing orphan instruction, or an
// undefined spot that PseudoDisassembler.isValidSubroutine (must terminate) accepts. Lists targets with the pointer
// sites; with "create", disassembles and creates a function at each (pointer / jump tables, junk-prefix gaps).
//@category Splatterhouse
import ghidra.app.script.GhidraScript;
import ghidra.app.util.PseudoDisassembler;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import java.util.*;
public class CsPtrFuncs extends GhidraScript {
  public void run() throws Exception {
    String[] a = getScriptArgs();
    long end = Long.decode(a[0]);
    boolean create = a.length > 1 && a[1].equals("create");
    Listing L = currentProgram.getListing();
    PseudoDisassembler pd = new PseudoDisassembler(currentProgram);
    TreeMap<Long, List<Long>> hits = new TreeMap<>();
    Set<Long> orph = new HashSet<>();
    long romEnd = currentProgram.getMemory().getBlocks()[0].getEnd().getOffset() + 1;
    for (long o = 0x400; o + 4 <= romEnd; o += 2) {
      Address at = toAddr(o);
      if (L.getInstructionContaining(at) != null) continue;
      long v = getInt(at) & 0xffffffffL;
      if (v < 0x400 || v >= end || (v & 1) != 0) continue;
      Address t = toAddr(v);
      if (getFunctionContaining(t) != null) continue;
      boolean orphan = L.getInstructionAt(t) != null;
      boolean undef = L.getCodeUnitContaining(t) instanceof Data && !((Data) L.getCodeUnitContaining(t)).isDefined();
      if (!orphan && !(undef && pd.isValidSubroutine(t, true, true))) continue;
      hits.computeIfAbsent(v, k -> new ArrayList<>()).add(o);
      if (orphan) orph.add(v);
    }
    int made = 0;
    for (Map.Entry<Long, List<Long>> e : hits.entrySet()) {
      StringBuilder sb = new StringBuilder();
      for (long s : e.getValue()) sb.append(String.format(" %x", s));
      println(String.format("target %06x %s sites%s", e.getKey(), orph.contains(e.getKey()) ? "orphan" : "undef", sb));
      if (create) {
        Address t = toAddr(e.getKey());
        if (getFunctionContaining(t) != null) continue;
        disassemble(t);
        if (createFunction(t, null) != null) made++;
      }
    }
    println("ptrfuncs: targets " + hits.size() + ", created " + made);
  }
}
