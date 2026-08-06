// DesignPatternsSolid | kind=solid | label=isp | domain=session | tier=minimal
package org.example.patterns;

// ISP: small role interfaces for session
interface SessionReadable {
    String read();
}
interface SessionWritable {
    void write(String v);
}

class SessionStore implements SessionReadable, SessionWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "session:" + v; }
}

public class SessionIspClient {
    public static String mirror(SessionReadable r) { return r.read(); }
}
