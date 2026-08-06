// DesignPatternsSolid | kind=solid | label=isp | domain=discount | tier=errors
package org.example.patterns;

// ISP: small role interfaces for discount
interface DiscountReadable {
    String read();
}
interface DiscountWritable {
    void write(String v);
}

class DiscountStore implements DiscountReadable, DiscountWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "discount:" + v; }
}

public class DiscountIspClient {
    public static String mirror(DiscountReadable r) { return r.read(); }
}
