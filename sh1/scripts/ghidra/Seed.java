//@category SH
// args: addr... ; disassembles + creates functions at each, runs auto-analysis, prints coverage per block
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.*;
public class Seed extends GhidraScript {
  public void run() throws Exception {
    for (String s : getScriptArgs()) { Address a = toAddr(Long.decode(s)); disassemble(a); if (getFunctionAt(a)==null) createFunction(a,null); }
    analyzeAll(currentProgram);
    cover();
  }
  void cover() {
    Listing l=currentProgram.getListing();
    for (MemoryBlock b : currentProgram.getMemory().getBlocks()) {
      long fn=0, code=0, tot=b.getSize();
      for (Function f : l.getFunctions(new AddressSet(b.getStart(),b.getEnd()), true)) fn+=f.getBody().getNumAddresses();
      for (Instruction i : l.getInstructions(new AddressSet(b.getStart(),b.getEnd()), true)) code+=i.getLength();
      int nf=0; for (Function f : l.getFunctions(new AddressSet(b.getStart(),b.getEnd()), true)) nf++;
      println("COVER "+b.getName()+" funcs="+nf+" fnbytes="+fn+" codebytes="+code+" of "+tot);
    }
  }
}
