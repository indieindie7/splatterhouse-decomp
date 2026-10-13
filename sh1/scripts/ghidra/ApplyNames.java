// Applies names from a tools/omfsig.py result file: lines "<addr> func|data <name> <module> <conf>".
// func: creates the function if needed and names it (register-convention trailing "_" stripped); if the function already
// has a user-defined name (e.g. from the routine table) the new name becomes an extra label.
// data: creates a label (one leading "_" stripped). Names also get a plate comment with the library module + confidence.
//@category Scorcher
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.nio.file.*;

public class ApplyNames extends GhidraScript {
    @Override
    public void run() throws Exception {
        int funcs = 0, created = 0, labels = 0, data = 0;
        for (String line : Files.readAllLines(Paths.get(getScriptArgs()[0]))) {
            String[] t = line.trim().split(" ");
            if (t.length < 5) continue;
            Address a = toAddr(Long.decode(t[0]));
            String name = t[2];
            boolean isFunc = t[1].equals("func");
            if (isFunc && name.endsWith("_") && name.length() > 1) name = name.substring(0, name.length() - 1);
            if (!isFunc && name.startsWith("_") && name.length() > 1) name = name.substring(1);
            boolean hand = t[3].equals("hand");
            SourceType src = hand ? SourceType.USER_DEFINED : SourceType.IMPORTED;
            String note = (hand ? "Hand-named: " : t[3].equals("xalign") ? "Cross-build match " : "Watcom runtime: ") + t[2] + " (" + String.join(" ", java.util.Arrays.copyOfRange(t, 3, t.length)) + ")";
            if (isFunc) {
                Function f = getFunctionAt(a);
                if (f == null && getFunctionContaining(a) == null) {
                    disassemble(a); f = createFunction(a, null);
                    if (f != null) created++;
                }
                if (f == null) { printerr("no function for " + line); continue; }
                try {
                    if (!hand && f.getSymbol().getSource() == SourceType.USER_DEFINED && !f.getName().equals(name)) {
                        createLabel(a, name, false, SourceType.IMPORTED); labels++;
                    } else { f.setName(name, src); funcs++; }
                } catch (Exception e) { f.setName(name + "_" + a, src); funcs++; }
                setPlateComment(a, note);
            } else {
                Symbol s = getSymbolAt(a);
                if (hand || s == null || s.getSource() != SourceType.USER_DEFINED) {
                    try { createLabel(a, name, true, src); } catch (Exception e) { createLabel(a, name + "_" + a, true, src); }
                    data++;
                }
                String old = getEOLComment(a);
                setEOLComment(a, (old == null ? "" : old + " ") + note);
            }
        }
        println("ApplyNames: functions named " + funcs + " (created " + created + "), extra labels " + labels + ", data labels " + data);
    }
}
