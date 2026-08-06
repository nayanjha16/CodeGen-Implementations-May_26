// DesignPatternsSolid | kind=solid | label=isp | domain=notes | tier=errors
package org.example.patterns;

// ISP: small role interfaces for notes
interface NotesReadable {
    String read();
}
interface NotesWritable {
    void write(String v);
}

class NotesStore implements NotesReadable, NotesWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "notes:" + v; }
}

public class NotesIspClient {
    public static String mirror(NotesReadable r) { return r.read(); }
}
