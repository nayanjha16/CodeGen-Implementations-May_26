// DesignPatternsSolid | kind=solid | label=isp | domain=notifications | tier=errors
package org.example.patterns;

// ISP: small role interfaces for notifications
interface NotificationsReadable {
    String read();
}
interface NotificationsWritable {
    void write(String v);
}

class NotificationsStore implements NotificationsReadable, NotificationsWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "notifications:" + v; }
}

public class NotificationsIspClient {
    public static String mirror(NotificationsReadable r) { return r.read(); }
}
