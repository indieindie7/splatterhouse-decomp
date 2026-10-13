//@category SH
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import java.io.*;
public class ListRange extends GhidraScript {
  public void run() throws Exception {
    String[] a=getScriptArgs();
    PrintWriter w=new PrintWriter(new FileWriter(a[0]));
    Address lo=toAddr(Long.decode(a[1])), hi=toAddr(Long.decode(a[2]));
    for (CodeUnit cu : currentProgram.getListing().getCodeUnits(new AddressSet(lo,hi), true))
      w.println(cu.getAddress()+"  "+cu.toString());
    w.close();
  }
}
