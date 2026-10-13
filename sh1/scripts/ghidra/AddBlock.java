//@category SH
// args: name addrHex file [overlay]
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import java.nio.file.*;
public class AddBlock extends GhidraScript {
  public void run() throws Exception {
    String[] a=getScriptArgs();
    byte[] b=Files.readAllBytes(Paths.get(a[2]));
    Address ad=toAddr(Long.decode(a[1]));
    boolean ovl=a.length>3 && a[3].equals("overlay");
    Memory m=currentProgram.getMemory();
    MemoryBlock blk=m.createInitializedBlock(a[0],ad,new java.io.ByteArrayInputStream(b),b.length,monitor,ovl);
    blk.setRead(true); blk.setExecute(true); blk.setWrite(false);
    println("added "+a[0]+" at "+blk.getStart()+" len "+b.length);
  }
}
