package org.example.patterns;
public class NotesBridgeTest {
    public static void main(String[] args) {
        NotesBridge b = new NotesAlertBridge(new NotesFileImpl());
        String out = b.send("x");
        if (!out.equals("file:notes:ALERT-x")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
