// DesignPatternsSolid | kind=solid | label=isp | domain=scheduling | tier=errors
package org.example.patterns;

// ISP: small role interfaces for scheduling
interface SchedulingReadable {
    String read();
}
interface SchedulingWritable {
    void write(String v);
}

class SchedulingStore implements SchedulingReadable, SchedulingWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "scheduling:" + v; }
}

public class SchedulingIspClient {
    public static String mirror(SchedulingReadable r) { return r.read(); }
}
