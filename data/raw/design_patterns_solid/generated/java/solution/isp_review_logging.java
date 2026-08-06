// DesignPatternsSolid | kind=solid | label=isp | domain=review | tier=logging
package org.example.patterns;

// ISP: small role interfaces for review
interface ReviewReadable {
    String read();
}
interface ReviewWritable {
    void write(String v);
}

class ReviewStore implements ReviewReadable, ReviewWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "review:" + v; }
}

public class ReviewIspClient {
    public static String mirror(ReviewReadable r) { return r.read(); }
}
