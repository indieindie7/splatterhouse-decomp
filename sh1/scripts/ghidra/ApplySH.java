//@category SH
// args: names.txt. Lines "ADDR func|data name source description..."; ADDR = 0xNNNN (default map) or bank:0xNNNN (overlay block "b<bank>").
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.nio.file.*;
public class ApplySH extends GhidraScript {
  public void run() throws Exception {
    int fn=0, lb=0, skip=0;
    for (String line : Files.readAllLines(Paths.get(getScriptArgs()[0]))) {
      String[] t=line.trim().split(" +",5);
      if (t.length<3) continue;
      Address a;
      if (t[0].contains(":")) {
        String[] p=t[0].split(":");
        AddressSpace sp=currentProgram.getAddressFactory().getAddressSpace("b"+p[0].toLowerCase());
        if (sp==null) { skip++; continue; }
        a=sp.getAddress(Long.decode(p[1]));
      } else a=toAddr(Long.decode(t[0]));
      if (currentProgram.getMemory().getBlock(a)==null) { skip++; continue; }
      String desc=t.length>4? t[4] : "";
      try {
        if (t[1].equals("func")) {
          Function f=getFunctionAt(a);
          if (f==null) { disassemble(a); f=createFunction(a,null); }
          if (f!=null) { f.setName(t[2],SourceType.USER_DEFINED); fn++; }
          else { createLabel(a,t[2],true,SourceType.USER_DEFINED); lb++; }
        } else { Function g=getFunctionAt(a); if (g!=null) removeFunction(g); createLabel(a,t[2],true,SourceType.USER_DEFINED); lb++; }
        if (!desc.isEmpty()) setPlateComment(a,desc);
      } catch (Exception e) { skip++; println("fail "+line+" : "+e.getMessage()); }
    }
    println("ApplySH funcs="+fn+" labels="+lb+" skipped="+skip);
  }
}
