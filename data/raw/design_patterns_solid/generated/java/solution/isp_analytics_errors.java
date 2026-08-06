// DesignPatternsSolid | kind=solid | label=isp | domain=analytics | tier=errors
package org.example.patterns;

// ISP: small role interfaces for analytics
interface AnalyticsReadable {
    String read();
}
interface AnalyticsWritable {
    void write(String v);
}

class AnalyticsStore implements AnalyticsReadable, AnalyticsWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "analytics:" + v; }
}

public class AnalyticsIspClient {
    public static String mirror(AnalyticsReadable r) { return r.read(); }
}
