// Dump decompiled C for the functions containing the given addresses.  args: <out.c> <addr> [<addr> ...]
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import java.io.*;
public class DumpDecomp extends GhidraScript {
    public void run() throws Exception {
        String[] a = getScriptArgs();
        PrintWriter w = new PrintWriter(new FileWriter(a[0]));
        DecompInterface di = new DecompInterface(); di.openProgram(currentProgram);
        for (int i = 1; i < a.length; i++) {
            Address addr = toAddr(Long.parseLong(a[i].replace("0x", ""), 16));
            Function f = getFunctionContaining(addr);
            if (f == null) { w.println("// no function at " + a[i]); continue; }
            DecompileResults r = di.decompileFunction(f, 60, monitor);
            w.println("// ==== " + f.getName() + " @ " + f.getEntryPoint() + " body=" + f.getBody().getNumAddresses() + " ranges=" + f.getBody().getNumAddressRanges());
            if (r.decompileCompleted()) w.println(r.getDecompiledFunction().getC()); else w.println("// failed: " + r.getErrorMessage());
        }
        di.dispose(); w.close(); println("DumpDecomp: done " + (a.length - 1));
    }
}
