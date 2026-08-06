// DesignPatternsSolid | kind=solid | label=isp | domain=logging | tier=minimal
package org.example.patterns;

// ISP: small role interfaces for logging
interface LoggingReadable {
    String read();
}
interface LoggingWritable {
    void write(String v);
}

class LoggingStore implements LoggingReadable, LoggingWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "logging:" + v; }
}

public class LoggingIspClient {
    public static String mirror(LoggingReadable r) { return r.read(); }
}
