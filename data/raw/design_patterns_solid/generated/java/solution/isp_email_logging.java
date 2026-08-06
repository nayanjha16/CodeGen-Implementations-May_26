// DesignPatternsSolid | kind=solid | label=isp | domain=email | tier=logging
package org.example.patterns;

// ISP: small role interfaces for email
interface EmailReadable {
    String read();
}
interface EmailWritable {
    void write(String v);
}

class EmailStore implements EmailReadable, EmailWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "email:" + v; }
}

public class EmailIspClient {
    public static String mirror(EmailReadable r) { return r.read(); }
}
