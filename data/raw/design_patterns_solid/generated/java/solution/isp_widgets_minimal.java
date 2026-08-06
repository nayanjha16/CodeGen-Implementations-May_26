// DesignPatternsSolid | kind=solid | label=isp | domain=widgets | tier=minimal
package org.example.patterns;

// ISP: small role interfaces for widgets
interface WidgetsReadable {
    String read();
}
interface WidgetsWritable {
    void write(String v);
}

class WidgetsStore implements WidgetsReadable, WidgetsWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "widgets:" + v; }
}

public class WidgetsIspClient {
    public static String mirror(WidgetsReadable r) { return r.read(); }
}
