// DesignPatternsSolid | kind=solid | label=isp | domain=billing | tier=minimal
package org.example.patterns;

// ISP: small role interfaces for billing
interface BillingReadable {
    String read();
}
interface BillingWritable {
    void write(String v);
}

class BillingStore implements BillingReadable, BillingWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "billing:" + v; }
}

public class BillingIspClient {
    public static String mirror(BillingReadable r) { return r.read(); }
}
