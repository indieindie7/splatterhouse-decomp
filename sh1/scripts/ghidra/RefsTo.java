//@category SH
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.listing.*;
public class RefsTo extends GhidraScript {
  public void run() throws Exception {
    long lo = Long.decode(getScriptArgs()[0]), hi = Long.decode(getScriptArgs()[1]);
    for (long a = lo; a < hi; a++) {
      for (Reference r : getReferencesTo(toAddr(a))) {
        Function f = getFunctionContaining(r.getFromAddress());
        println("REF " + Long.toHexString(a) + " <- " + r.getFromAddress() + " " + r.getReferenceType() + " in " + (f==null?"-":f.getEntryPoint()+" "+f.getName()));
      }
    }
  }
}
