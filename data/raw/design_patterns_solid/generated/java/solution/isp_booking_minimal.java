// DesignPatternsSolid | kind=solid | label=isp | domain=booking | tier=minimal
package org.example.patterns;

// ISP: small role interfaces for booking
interface BookingReadable {
    String read();
}
interface BookingWritable {
    void write(String v);
}

class BookingStore implements BookingReadable, BookingWritable {
    private String data = "";
    public String read() { return data; }
    public void write(String v) { data = "booking:" + v; }
}

public class BookingIspClient {
    public static String mirror(BookingReadable r) { return r.read(); }
}
