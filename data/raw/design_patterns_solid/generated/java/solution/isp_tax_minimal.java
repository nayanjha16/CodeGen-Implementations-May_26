// DesignPatternsSolid | kind=solid | label=isp | domain=tax | tier=minimal
package org.example.patterns;

// ISP: small role interfaces for tax
interface TaxReadable {
    String read();
}
interface TaxWritable {
    void write(String v);
}

class TaxStore implements TaxReadable, TaxWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "tax:" + v; }
}

public class TaxIspClient {
    public static String mirror(TaxReadable r) { return r.read(); }
}
