// DesignPatternsSolid | kind=solid | label=isp | domain=calendar | tier=logging
package org.example.patterns;

// ISP: small role interfaces for calendar
interface CalendarReadable {
    String read();
}
interface CalendarWritable {
    void write(String v);
}

class CalendarStore implements CalendarReadable, CalendarWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "calendar:" + v; }
}

public class CalendarIspClient {
    public static String mirror(CalendarReadable r) { return r.read(); }
}
