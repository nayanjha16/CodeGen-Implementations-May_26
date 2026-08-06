// DesignPatternsSolid | kind=solid | label=isp | domain=queue | tier=logging
package org.example.patterns;

// ISP: small role interfaces for queue
interface QueueReadable {
    String read();
}
interface QueueWritable {
    void write(String v);
}

class QueueStore implements QueueReadable, QueueWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "queue:" + v; }
}

public class QueueIspClient {
    public static String mirror(QueueReadable r) { return r.read(); }
}
