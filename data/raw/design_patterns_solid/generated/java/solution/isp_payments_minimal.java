// DesignPatternsSolid | kind=solid | label=isp | domain=payments | tier=minimal
package org.example.patterns;

// ISP: small role interfaces for payments
interface PaymentsReadable {
    String read();
}
interface PaymentsWritable {
    void write(String v);
}

class PaymentsStore implements PaymentsReadable, PaymentsWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "payments:" + v; }
}

public class PaymentsIspClient {
    public static String mirror(PaymentsReadable r) { return r.read(); }
}
