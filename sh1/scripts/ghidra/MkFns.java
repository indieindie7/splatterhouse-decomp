//@category SH
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
public class MkFns extends GhidraScript {
  public void run() throws Exception {
    for (String s : getScriptArgs()) { Address a = toAddr(Long.decode(s)); disassemble(a); if (getFunctionAt(a)==null) createFunction(a,null); }
  }
}
