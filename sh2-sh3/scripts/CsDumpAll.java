// CsDumpAll.java <abs out.c> [lo hi]: decompile every function (optionally entry in [lo,hi)) into one C file.
//@category Splatterhouse
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import java.io.*;
public class CsDumpAll extends GhidraScript {
  public void run() throws Exception {
    String[] a = getScriptArgs();
    long lo = a.length > 2 ? Long.decode(a[1]) : 0, hi = a.length > 2 ? Long.decode(a[2]) : Long.MAX_VALUE;
    DecompInterface d = new DecompInterface();
    d.openProgram(currentProgram);
    int n = 0;
    try (PrintWriter w = new PrintWriter(new FileWriter(a[0]))) {
      for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
        long o = f.getEntryPoint().getOffset();
        if (o < lo || o >= hi) continue;
        DecompileResults r = d.decompileFunction(f, 30, monitor);
        w.println("// ==== " + f.getName() + " @ " + f.getEntryPoint() + " size=" + f.getBody().getNumAddresses());
        w.println(r.decompileCompleted() ? r.getDecompiledFunction().getC() : "// decompile failed: " + r.getErrorMessage());
        n++;
      }
    }
    d.dispose();
    println("dumped " + n);
  }
}
