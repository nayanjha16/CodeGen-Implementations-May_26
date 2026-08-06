// DesignPatternsSolid | kind=solid | label=isp | domain=report | tier=minimal
package org.example.patterns;

// ISP: small role interfaces for report
interface ReportReadable {
    String read();
}
interface ReportWritable {
    void write(String v);
}

class ReportStore implements ReportReadable, ReportWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "report:" + v; }
}

public class ReportIspClient {
    public static String mirror(ReportReadable r) { return r.read(); }
}
