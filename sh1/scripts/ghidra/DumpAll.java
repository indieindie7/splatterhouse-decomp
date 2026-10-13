//@category SH
// Decompile every function into <outdir>/<block>.c (one file per memory block, address order), with plate comments.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import java.io.*;
import java.util.*;
public class DumpAll extends GhidraScript {
  public void run() throws Exception {
    File dir=new File(getScriptArgs()[0]); dir.mkdirs();
    DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
    Map<String,PrintWriter> out=new TreeMap<>();
    int ok=0, bad=0;
    for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
      String blk=currentProgram.getMemory().getBlock(f.getEntryPoint()).getName();
      PrintWriter w=out.get(blk);
      if (w==null) { w=new PrintWriter(new FileWriter(new File(dir,blk+".c"))); out.put(blk,w); }
      String plate=getPlateComment(f.getEntryPoint());
      w.println("// ---- "+f.getEntryPoint()+" "+f.getName()+(plate!=null?"\n// "+plate.replace("\n"," "):""));
      DecompileResults r=di.decompileFunction(f,60,monitor);
      if (r!=null && r.decompileCompleted()) { w.println(r.getDecompiledFunction().getC()); ok++; }
      else { w.println("// decompile failed: "+(r==null?"null":r.getErrorMessage())); bad++; }
    }
    for (PrintWriter w : out.values()) w.close();
    println("DumpAll ok="+ok+" failed="+bad);
  }
}
