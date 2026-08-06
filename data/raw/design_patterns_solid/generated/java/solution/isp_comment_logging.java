// DesignPatternsSolid | kind=solid | label=isp | domain=comment | tier=logging
package org.example.patterns;

// ISP: small role interfaces for comment
interface CommentReadable {
    String read();
}
interface CommentWritable {
    void write(String v);
}

class CommentStore implements CommentReadable, CommentWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "comment:" + v; }
}

public class CommentIspClient {
    public static String mirror(CommentReadable r) { return r.read(); }
}
