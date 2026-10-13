// CsCoverage.java <lo> <hi> [create]: byte coverage of [lo,hi): in instructions, in defined data, undefined.
// Lists undefined runs of >= 8 bytes. With "create", disassembles at the start of each run whose first word
// decodes and creates a function there when the flow ends in RTS/RTE/JMP (68000 code gaps).
// With "pseudo", any gap start that PseudoDisassembler.isValidSubroutine (must terminate) accepts is created (no nibble filter).
//@category Splatterhouse
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.app.util.PseudoDisassembler;
public class CsCoverage extends GhidraScript {
  public void run() throws Exception {
    String[] a = getScriptArgs();
    long lo = Long.decode(a[0]), hi = Long.decode(a[1]);
    boolean create = a.length > 2 && a[2].equals("create"), pseudo = a.length > 2 && a[2].equals("pseudo");
    PseudoDisassembler pd = new PseudoDisassembler(currentProgram);
    Listing L = currentProgram.getListing();
    long ins = 0, dat = 0, und = 0, runs = 0, made = 0;
    long runStart = -1;
    for (long o = lo; o <= hi; o++) {
      boolean u = o < hi && L.getCodeUnitContaining(toAddr(o)) instanceof Data && !((Data) L.getCodeUnitContaining(toAddr(o))).isDefined();
      if (o < hi) {
        CodeUnit cu = L.getCodeUnitContaining(toAddr(o));
        if (cu instanceof Instruction) ins++; else if (u) und++; else dat++;
      }
      if (u && runStart < 0) runStart = o;
      if (!u && runStart >= 0) {
        long len = o - runStart;
        long s = (runStart + 1) & ~1L;
        if (len >= 8 && getShort(toAddr(s)) != 0 && getShort(toAddr(s)) != -1) {
          runs++;
          if (runs <= 40) println(String.format("gap %06x len %d first %04x", s, len, getShort(toAddr(s)) & 0xffff));
          int hn = (getShort(toAddr(s)) >> 12) & 0xf;
          if (pseudo && pd.isValidSubroutine(toAddr(s), true, true) && disassemble(toAddr(s)) && getFunctionContaining(toAddr(s)) == null && createFunction(toAddr(s), null) != null) made++;
          if (create && hn != 0 && hn != 0xf && hn != 0xa && disassemble(toAddr(s)) && getFunctionContaining(toAddr(s)) == null && createFunction(toAddr(s), null) != null) made++;
        }
        runStart = -1;
      }
    }
    println(String.format("coverage %x..%x: instr %d, data %d, undefined %d, gaps %d, created %d", lo, hi, ins, dat, und, runs, made));
  }
}
