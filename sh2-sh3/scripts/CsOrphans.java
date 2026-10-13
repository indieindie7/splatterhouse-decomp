// CsOrphans.java <lo> <hi> [create]: list runs of instructions in [lo,hi) that no function owns ("orphan" code, e.g.
// the real entries behind junk-prefix gaps, or tails left when a false function was deleted). A run starts at an
// orphan instruction that no orphan instruction falls into. Prints "orphan <start> len <bytes> refs <n>" (refs = code
// or data references to the start, with the owning function). With "create", makes a function at every run start
// that is called (bsr/jsr); "createref" also at runs with only data refs (code pointers in lea/move or ROM tables);
// with "fixup", re-flows the body of every function that branches into a run (CreateFunctionCmd.fixupFunctionBody).
//@category Splatterhouse
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.app.cmd.function.CreateFunctionCmd;
import java.util.*;
public class CsOrphans extends GhidraScript {
  public void run() throws Exception {
    String[] a = getScriptArgs();
    long lo = Long.decode(a[0]), hi = Long.decode(a[1]);
    boolean create = a.length > 2 && a[2].equals("create");
    fixup = a.length > 2 && a[2].equals("fixup");
    anyRef = a.length > 2 && a[2].equals("createref");
    if (anyRef) create = true;
    Listing L = currentProgram.getListing();
    int runs = 0, made = 0;
    long start = -1, end = -1;
    for (Instruction ins : L.getInstructions(toAddr(lo), true)) {
      long o = ins.getAddress().getOffset();
      if (o >= hi) break;
      boolean orphan = getFunctionContaining(ins.getAddress()) == null;
      if (orphan && start >= 0 && o == end) { end = o + ins.getLength(); continue; }
      if (start >= 0) { report(start, end, create); runs++; start = -1; }
      if (orphan) { start = o; end = o + ins.getLength(); }
    }
    if (start >= 0) { report(start, end, create); runs++; }
    if (fixup) for (Function f : grow) if (CreateFunctionCmd.fixupFunctionBody(currentProgram, f, monitor)) made2++;
    println("orphans: runs " + runs + ", created/grown " + made2 + " of " + grow.size());
  }
  int made2 = 0;
  boolean fixup, anyRef;
  Set<Function> grow = new LinkedHashSet<>();
  void report(long s, long e, boolean create) throws Exception {
    Address at = toAddr(s);
    int refs = currentProgram.getReferenceManager().getReferenceCountTo(at);
    String from = "";
    boolean called = false;
    for (Reference r : getReferencesTo(at)) {
      Function f = getFunctionContaining(r.getFromAddress());
      from += String.format(" %s:%s", r.getReferenceType().isCall() ? "call" : r.getReferenceType().isFlow() ? "jump" : "data", f == null ? r.getFromAddress().toString() : f.getName());
      if (r.getReferenceType().isCall() || anyRef) called = true;
      else if (f != null && r.getReferenceType().isFlow()) grow.add(f);
    }
    println(String.format("orphan %06x len %d refs %d%s", s, e - s, refs, from));
    if (create && called && getFunctionContaining(at) == null) {
      if (createFunction(at, null) != null) made2++; else println(String.format("create failed %06x", s));
    }
  }
}
