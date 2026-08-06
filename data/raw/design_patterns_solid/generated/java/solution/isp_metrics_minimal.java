// DesignPatternsSolid | kind=solid | label=isp | domain=metrics | tier=minimal
package org.example.patterns;

// ISP: small role interfaces for metrics
interface MetricsReadable {
    String read();
}
interface MetricsWritable {
    void write(String v);
}

class MetricsStore implements MetricsReadable, MetricsWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "metrics:" + v; }
}

public class MetricsIspClient {
    public static String mirror(MetricsReadable r) { return r.read(); }
}
