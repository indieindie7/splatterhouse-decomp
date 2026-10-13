//@category SH
import ghidra.app.script.GhidraScript;
import ghidra.program.model.symbol.*;
public class ListSyms extends GhidraScript {
  public void run() throws Exception {
    String pat = getScriptArgs()[0];
    SymbolIterator it = currentProgram.getSymbolTable().getAllSymbols(true);
    while (it.hasNext()) { Symbol s = it.next();
      String n = s.getName(true);
      if (n.contains(pat)) println(s.getAddress() + " " + s.getSymbolType() + " " + n); }
  }
}
