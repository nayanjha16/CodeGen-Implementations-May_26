// DesignPatternsSolid | kind=solid | label=isp | domain=sms | tier=errors
package org.example.patterns;

// ISP: small role interfaces for sms
interface SmsReadable {
    String read();
}
interface SmsWritable {
    void write(String v);
}

class SmsStore implements SmsReadable, SmsWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "sms:" + v; }
}

public class SmsIspClient {
    public static String mirror(SmsReadable r) { return r.read(); }
}
