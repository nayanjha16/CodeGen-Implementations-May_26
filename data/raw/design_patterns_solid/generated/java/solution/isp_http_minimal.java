// DesignPatternsSolid | kind=solid | label=isp | domain=http | tier=minimal
package org.example.patterns;

// ISP: small role interfaces for http
interface HttpReadable {
    String read();
}
interface HttpWritable {
    void write(String v);
}

class HttpStore implements HttpReadable, HttpWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "http:" + v; }
}

public class HttpIspClient {
    public static String mirror(HttpReadable r) { return r.read(); }
}
